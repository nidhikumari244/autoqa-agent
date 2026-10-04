import os
import sys
from pathlib import Path

# Ensure backend root is in sys.path
sys.path.insert(0, str(Path(__file__).resolve().parent.parent))

import asyncio
from app.engine.dom_grounding import DOMGroundingEngine
from app.engine.code_synthesizer import CodeSynthesizer
from app.engine.reporter import PDFReportGenerator
from app.engine.browser_controller import BrowserController
from app.schemas.actions import BrowserAction, ActionType

async def test_full_pipeline():
    print(">>> 1. Testing CodeSynthesizer...")
    synth = CodeSynthesizer("User Login and Verification", "https://example.com")
    synth.record_step(
        action=BrowserAction(action_type=ActionType.NAVIGATE, url="https://example.com"),
        resolved_selector="https://example.com",
        reasoning="Open target website"
    )
    synth.record_step(
        action=BrowserAction(action_type=ActionType.CLICK, target_id=1),
        resolved_selector="a:has-text('More information...')",
        reasoning="Click on learn more link"
    )
    synth.record_step(
        action=BrowserAction(action_type=ActionType.ASSERT_VISIBLE, assertion_text="Example Domains"),
        resolved_selector="text='Example Domains'",
        reasoning="Verify landing text"
    )
    py_code = synth.generate_python()
    ts_code = synth.generate_typescript()
    assert "def test_user_login_and_verification" in py_code
    assert "test('User Login and Verification'" in ts_code
    print("[OK] CodeSynthesizer passed (Python and TypeScript code generated)")

    print("\n>>> 2. Testing PDFReportGenerator...")
    test_pdf_path = Path("artifacts/test_report.pdf")
    PDFReportGenerator.generate(
        run_data={
            "scenario_title": "Automated Smoke Test",
            "base_url": "https://example.com",
            "goal_prompt": "Verify home page title and links",
            "status": "PASSED",
            "duration_ms": 3200,
            "steps": [
                {"step_number": 1, "action_type": "navigate", "resolved_selector": "https://example.com", "thought": "Navigated to home", "status": "SUCCESS"},
                {"step_number": 2, "action_type": "assert_visible", "resolved_selector": "Example Domain", "thought": "Confirmed title", "status": "SUCCESS"}
            ]
        },
        output_pdf_path=str(test_pdf_path)
    )
    assert test_pdf_path.exists()
    print(f"[OK] PDFReportGenerator passed (PDF created at {test_pdf_path})")

    print("\n>>> 3. Testing BrowserController & DOMGroundingEngine...")
    browser = BrowserController(headless=True)
    await browser.start()
    try:
        await browser.navigate("https://example.com")
        obs, lookup = await DOMGroundingEngine.extract_interactive_map(browser.page)
        print(f"[OK] Extracted {len(obs.interactive_elements)} interactive elements from {obs.url}")
        assert len(obs.interactive_elements) > 0, "Expected at least 1 interactive element on example.com"
        
        # Test screenshot
        shot = await browser.capture_screenshot("artifacts/test_screen.jpg")
        assert len(shot) > 1000
        print(f"[OK] Captured screenshot ({len(shot)} bytes)")
        
        # Test DOM marker cleaning
        await DOMGroundingEngine.clean_visual_markers(browser.page)
        print("[OK] Cleaned visual marker badges")
    finally:
        await browser.close()
        print("[OK] Browser closed cleanly")

    print("\n==============================")
    print("ALL CORE ENGINE TESTS PASSED!")
    print("==============================")

if __name__ == "__main__":
    asyncio.run(test_full_pipeline())
