import os
import sys
import time
import base64
import asyncio
import traceback
from datetime import datetime, timezone
from pathlib import Path
from typing import Optional, List, Dict, Any

from sqlalchemy import select
from app.core.database import AsyncSessionLocal
from app.core.config import settings
from app.models.test_run import TestRun, TestRunStep
from app.models.project import TestScenario, Project
from app.schemas.actions import ActionType
from app.engine.browser_controller import BrowserController
from app.engine.dom_grounding import DOMGroundingEngine
from app.engine.vision_agent import VisionAgent
from app.engine.code_synthesizer import CodeSynthesizer
from app.engine.reporter import PDFReportGenerator
from app.api.v1.websockets import ws_manager

class MasterTestRunner:
    def __init__(self, run_id: str):
        self.run_id = run_id
        self.browser: Optional[BrowserController] = None
        self.synthesizer: Optional[CodeSynthesizer] = None

    async def execute(self):
        # On Windows, Playwright requires ProactorEventLoop to spawn browser subprocesses.
        # If running under SelectorEventLoop (e.g. uvicorn --reload), delegate to a dedicated thread with ProactorEventLoop.
        if sys.platform == "win32" and not isinstance(asyncio.get_running_loop(), getattr(asyncio, "ProactorEventLoop", object)):
            loop = asyncio.get_running_loop()
            await loop.run_in_executor(None, self._run_in_proactor_thread)
            return
        await self._execute_internal()

    def _run_in_proactor_thread(self):
        worker_loop = asyncio.ProactorEventLoop()
        asyncio.set_event_loop(worker_loop)
        try:
            worker_loop.run_until_complete(self._execute_internal())
        finally:
            try:
                pending = asyncio.all_tasks(worker_loop)
                for t in pending:
                    t.cancel()
                if pending:
                    worker_loop.run_until_complete(asyncio.gather(*pending, return_exceptions=True))
            except Exception:
                pass
            worker_loop.close()

    async def _execute_internal(self):
        start_time = time.time()
        
        async with AsyncSessionLocal() as db:
            result = await db.execute(
                select(TestRun, TestScenario, Project)
                .join(TestScenario, TestRun.scenario_id == TestScenario.id)
                .join(Project, TestScenario.project_id == Project.id)
                .where(TestRun.id == self.run_id)
            )
            row = result.first()
            if not row:
                return
            test_run, scenario, project = row

            test_run.status = "RUNNING"
            await db.commit()

        run_artifacts_dir = settings.ARTIFACTS_PATH / self.run_id
        run_artifacts_dir.mkdir(parents=True, exist_ok=True)

        self.synthesizer = CodeSynthesizer(
            scenario_title=scenario.title,
            base_url=project.base_url
        )

        agent = VisionAgent()
        self.browser = BrowserController(headless=settings.HEADLESS)
        history: List[Dict[str, Any]] = []
        final_status = "PASSED"
        error_summary = None

        await ws_manager.broadcast(self.run_id, {
            "type": "RUN_STARTED",
            "run_id": self.run_id,
            "scenario": scenario.title,
            "base_url": project.base_url,
            "goal": scenario.goal_prompt
        })

        try:
            await self.browser.start()
            
            # Initial navigation to target base URL
            await ws_manager.broadcast(self.run_id, {
                "type": "LOG",
                "message": f"Navigating to initial base URL: {project.base_url}"
            })
            await self.browser.navigate(project.base_url)
            self.synthesizer.record_step(
                action=type("Act", (), {"action_type": ActionType.NAVIGATE, "url": project.base_url})(),
                resolved_selector=project.base_url,
                reasoning=f"Initial navigation to target URL"
            )

            max_steps = scenario.max_steps or settings.MAX_STEPS_PER_RUN

            for step_num in range(1, max_steps + 1):
                step_start = time.time()

                # 1. Clean previous badges & extract interactive elements
                await DOMGroundingEngine.clean_visual_markers(self.browser.page)
                dom_obs, element_lookup = await DOMGroundingEngine.extract_interactive_map(self.browser.page)

                # 2. Take visual screenshot with marked Set-of-Marks badges
                shot_path = run_artifacts_dir / f"step_{step_num}.jpg"
                shot_bytes = await self.browser.capture_screenshot(str(shot_path))
                b64_screen = base64.b64encode(shot_bytes).decode("utf-8")

                # Stream current screen to frontend
                await ws_manager.broadcast(self.run_id, {
                    "type": "SCREENSHOT_UPDATE",
                    "step": step_num,
                    "screenshot_b64": b64_screen,
                    "url": dom_obs.url,
                    "interactive_elements_count": len(dom_obs.interactive_elements)
                })

                # 3. Consult Multi-Modal Vision Agent
                await ws_manager.broadcast(self.run_id, {
                    "type": "AGENT_THINKING",
                    "step": step_num,
                    "message": "Analyzing visual state and evaluating goal progress..."
                })

                decision = await agent.decide_next_step(
                    goal=scenario.goal_prompt,
                    dom_obs=dom_obs,
                    screenshot_bytes=shot_bytes,
                    history=history
                )

                # Clean badges before user interaction
                await DOMGroundingEngine.clean_visual_markers(self.browser.page)

                await ws_manager.broadcast(self.run_id, {
                    "type": "STEP_DECISION",
                    "step": step_num,
                    "thought": decision.thought,
                    "action_type": decision.action.action_type.value,
                    "target_id": decision.action.target_id,
                    "text": decision.action.text
                })

                # Check for termination
                if decision.action.action_type == ActionType.FINISH:
                    final_status = decision.action.status or "PASSED"
                    error_summary = decision.action.summary
                    break

                # 4. Execute atomic action
                success, resolved_selector, details = await self.browser.execute_action(
                    action=decision.action,
                    element_lookup=element_lookup
                )

                step_duration_ms = int((time.time() - step_start) * 1000)

                # Record in synthesizer
                self.synthesizer.record_step(
                    action=decision.action,
                    resolved_selector=resolved_selector,
                    reasoning=decision.thought
                )

                # Record step history for agent context
                history.append({
                    "step": step_num,
                    "action_type": decision.action.action_type.value,
                    "target": resolved_selector,
                    "thought": decision.thought,
                    "details": details,
                    "success": success
                })

                # Persist step in DB
                async with AsyncSessionLocal() as db:
                    step_record = TestRunStep(
                        run_id=self.run_id,
                        step_number=step_num,
                        action_type=decision.action.action_type.value,
                        thought=decision.thought,
                        action_payload=decision.action.model_dump(),
                        screenshot_path=f"/artifacts/{self.run_id}/step_{step_num}.jpg",
                        execution_time_ms=step_duration_ms,
                        status="SUCCESS" if success else "FAILED"
                    )
                    db.add(step_record)
                    await db.commit()

                await ws_manager.broadcast(self.run_id, {
                    "type": "STEP_COMPLETED",
                    "step": step_num,
                    "status": "SUCCESS" if success else "FAILED",
                    "details": details,
                    "duration_ms": step_duration_ms
                })

                if not success:
                    # Give one retry or let next iteration assess
                    await asyncio.sleep(1.0)

            else:
                # Loop completed without finish
                final_status = "TIMED_OUT"
                error_summary = f"Reached maximum allowed steps ({max_steps}) before goal was verified."

        except Exception as e:
            final_status = "FAILED"
            error_summary = f"{type(e).__name__}: {str(e)} | Trace: {traceback.format_exc()}"
            await ws_manager.broadcast(self.run_id, {
                "type": "RUN_ERROR",
                "error": error_summary
            })

        finally:
            total_duration_ms = int((time.time() - start_time) * 1000)
            if self.browser:
                await self.browser.close()

            # Compile test scripts
            python_code = self.synthesizer.generate_python() if self.synthesizer else ""
            ts_code = self.synthesizer.generate_typescript() if self.synthesizer else ""

            # Generate PDF Audit Report
            pdf_path = run_artifacts_dir / "audit_report.pdf"
            try:
                PDFReportGenerator.generate(
                    run_data={
                        "run_id": self.run_id,
                        "scenario_title": scenario.title,
                        "base_url": project.base_url,
                        "goal_prompt": scenario.goal_prompt,
                        "status": final_status,
                        "duration_ms": total_duration_ms,
                        "steps": history
                    },
                    output_pdf_path=str(pdf_path)
                )
                pdf_rel_path = f"/artifacts/{self.run_id}/audit_report.pdf"
            except Exception:
                pdf_rel_path = None

            # Update DB with final results
            async with AsyncSessionLocal() as db:
                result = await db.execute(select(TestRun).where(TestRun.id == self.run_id))
                run_obj = result.scalar_one_or_none()
                if run_obj:
                    run_obj.status = final_status
                    run_obj.duration_ms = total_duration_ms
                    run_obj.generated_code_python = python_code
                    run_obj.generated_code_ts = ts_code
                    run_obj.error_summary = error_summary
                    run_obj.report_pdf_path = pdf_rel_path
                    run_obj.finished_at = datetime.now(timezone.utc)
                    await db.commit()

            await ws_manager.broadcast(self.run_id, {
                "type": "RUN_FINISHED",
                "status": final_status,
                "duration_ms": total_duration_ms,
                "generated_code_python": python_code,
                "generated_code_ts": ts_code,
                "report_pdf_path": pdf_rel_path
            })
