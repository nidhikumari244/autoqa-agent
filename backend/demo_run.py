import os
import sys
import asyncio
from pathlib import Path

# Add backend to sys.path
sys.path.insert(0, str(Path(__file__).resolve().parent))

from app.core.database import init_db, AsyncSessionLocal
from app.models.project import Project, TestScenario
from app.models.test_run import TestRun
from app.engine.runner import MasterTestRunner
from sqlalchemy import select

async def run_standalone_demo():
    print("=============================================================")
    print("   AUTOQA: AUTONOMOUS MULTI-MODAL E2E VERIFICATION DEMO      ")
    print("=============================================================\n")

    await init_db()

    async with AsyncSessionLocal() as db:
        # Check or create demo project
        result = await db.execute(select(Project).where(Project.name == "Wikipedia Knowledge Portal"))
        project = result.scalar_one_or_none()
        if not project:
            project = Project(
                name="Wikipedia Knowledge Portal",
                base_url="https://en.wikipedia.org",
                description="Autonomous navigation, search queries, and content verification"
            )
            db.add(project)
            await db.commit()
            await db.refresh(project)
            print(f"[+] Initialized Project: {project.name} ({project.base_url})")
        else:
            print(f"[i] Using existing Project: {project.name}")

        # Check or create demo scenario
        result = await db.execute(select(TestScenario).where(TestScenario.project_id == project.id))
        scenario = result.first()
        if not scenario:
            scenario = TestScenario(
                project_id=project.id,
                title="Search Artificial Intelligence & Verify Headline",
                goal_prompt="Find search input, query 'Artificial intelligence', and verify the page heading displays 'Artificial intelligence'.",
                expected_outcome="Heading element with text 'Artificial intelligence' is visible",
                max_steps=5
            )
            db.add(scenario)
            await db.commit()
            await db.refresh(scenario)
            print(f"[+] Created Test Scenario: {scenario.title}")
        else:
            scenario = scenario[0]
            print(f"[i] Using Test Scenario: {scenario.title}")

        # Create a new TestRun
        test_run = TestRun(scenario_id=scenario.id, status="PENDING")
        db.add(test_run)
        await db.commit()
        await db.refresh(test_run)
        run_id = test_run.id
        print(f"[+] Created Test Run Session: {run_id}\n")

    print("[*] Launching Master Runner with Headless Chromium & Set-of-Marks Grounding...")
    runner = MasterTestRunner(run_id=run_id)
    await runner.execute()

    # Fetch final run details
    async with AsyncSessionLocal() as db:
        result = await db.execute(select(TestRun).where(TestRun.id == run_id))
        finished_run = result.scalar_one()

    print("\n=============================================================")
    print(f"  RUN COMPLETED WITH STATUS: {finished_run.status}")
    print(f"  Execution Time: {finished_run.duration_ms / 1000:.2f}s")
    print(f"  Audit PDF Report: {finished_run.report_pdf_path}")
    print("=============================================================\n")

    print("--- SYNTHESIZED PLAYWRIGHT PYTHON SPEC ---")
    print(finished_run.generated_code_python or "No code generated.")
    print("\n--- SYNTHESIZED PLAYWRIGHT TYPESCRIPT SPEC ---")
    print(finished_run.generated_code_ts or "No code generated.")
    print("=============================================================")

if __name__ == "__main__":
    asyncio.run(run_standalone_demo())
