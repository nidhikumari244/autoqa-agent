import os
import asyncio
from typing import Optional, Dict, Tuple, Any
from pathlib import Path
from playwright.async_api import async_playwright, Browser, BrowserContext, Page
from app.schemas.actions import BrowserAction, ActionType
from app.schemas.agent import InteractiveElement
from app.core.config import settings

class BrowserController:
    def __init__(self, headless: bool = True):
        self.headless = headless
        self._playwright = None
        self._browser: Optional[Browser] = None
        self._context: Optional[BrowserContext] = None
        self.page: Optional[Page] = None

    async def start(self):
        self._playwright = await async_playwright().start()
        self._browser = await self._playwright.chromium.launch(
            headless=self.headless,
            args=[
                "--disable-blink-features=AutomationControlled",
                "--no-sandbox",
                "--disable-setuid-sandbox"
            ]
        )
        self._context = await self._browser.new_context(
            viewport={
                "width": settings.BROWSER_VIEWPORT_WIDTH,
                "height": settings.BROWSER_VIEWPORT_HEIGHT
            },
            user_agent="Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/124.0.0.0 Safari/537.36"
        )
        self.page = await self._context.new_page()
        self.page.set_default_timeout(settings.ACTION_TIMEOUT_MS)

    async def navigate(self, url: str):
        if not self.page:
            raise RuntimeError("Browser not started. Call start() first.")
        if not url.startswith("http://") and not url.startswith("https://"):
            url = "https://" + url
        await self.page.goto(url, wait_until="domcontentloaded")
        # Give short buffer for JS frameworks (React/Vue/Next) to hydrate
        await asyncio.sleep(1.0)

    async def capture_screenshot(self, save_path: Optional[str] = None) -> bytes:
        if not self.page:
            raise RuntimeError("Browser not started.")
        screenshot_bytes = await self.page.screenshot(type="jpeg", quality=85)
        if save_path:
            Path(save_path).parent.mkdir(parents=True, exist_ok=True)
            with open(save_path, "wb") as f:
                f.write(screenshot_bytes)
        return screenshot_bytes

    async def execute_action(
        self,
        action: BrowserAction,
        element_lookup: Dict[int, InteractiveElement]
    ) -> Tuple[bool, str, str]:
        """
        Executes the atomic action on the browser.
        Returns: (success: bool, resolved_selector: str, details_or_error: str)
        """
        if not self.page:
            return False, "", "Browser is not active."

        # 1. Resolve selector
        resolved_selector = ""
        if action.target_id is not None and action.target_id in element_lookup:
            elem = element_lookup[action.target_id]
            resolved_selector = f'[data-autoqa-id="{action.target_id}"]'
        elif action.selector:
            resolved_selector = action.selector

        try:
            if action.action_type == ActionType.NAVIGATE:
                if not action.url:
                    return False, "", "No URL provided for navigate action."
                await self.navigate(action.url)
                return True, action.url, f"Navigated to {action.url}"

            elif action.action_type == ActionType.CLICK:
                if not resolved_selector:
                    return False, "", f"Could not resolve target selector for ID {action.target_id}"
                locator = self.page.locator(resolved_selector).first
                await locator.scroll_into_view_if_needed(timeout=5000)
                await locator.click(timeout=8000)
                await asyncio.sleep(0.8)  # Let UI settle
                return True, resolved_selector, f"Clicked on {resolved_selector}"

            elif action.action_type == ActionType.FILL:
                if not resolved_selector:
                    return False, "", f"Could not resolve target selector for ID {action.target_id}"
                locator = self.page.locator(resolved_selector).first
                await locator.scroll_into_view_if_needed(timeout=5000)
                await locator.click()
                await locator.fill(action.text or "")
                await asyncio.sleep(0.3)
                return True, resolved_selector, f"Filled '{action.text}' into {resolved_selector}"

            elif action.action_type == ActionType.HOVER:
                if not resolved_selector:
                    return False, "", f"Target ID {action.target_id} not found."
                locator = self.page.locator(resolved_selector).first
                await locator.hover(timeout=5000)
                return True, resolved_selector, f"Hovered over {resolved_selector}"

            elif action.action_type == ActionType.KEY_PRESS:
                key = action.text or "Enter"
                await self.page.keyboard.press(key)
                return True, "keyboard", f"Pressed key '{key}'"

            elif action.action_type == ActionType.SCROLL:
                amount = action.amount or 500
                delta_y = amount if action.direction == "down" else -amount
                await self.page.mouse.wheel(0, delta_y)
                await asyncio.sleep(0.5)
                return True, "viewport", f"Scrolled {action.direction} by {amount}px"

            elif action.action_type == ActionType.WAIT:
                await asyncio.sleep(2.0)
                return True, "timer", "Waited 2.0s for page state"

            elif action.action_type == ActionType.ASSERT_VISIBLE:
                target_text = action.assertion_text or ""
                locator = self.page.get_by_text(target_text, exact=False)
                is_visible = await locator.first.is_visible()
                if is_visible:
                    return True, f'text="{target_text}"', f"Assertion passed: text '{target_text}' is visible."
                else:
                    return False, f'text="{target_text}"', f"Assertion failed: text '{target_text}' not visible on page."

            elif action.action_type == ActionType.FINISH:
                return True, "finish", f"Finished scenario: {action.summary or action.status}"

            else:
                return False, "", f"Unknown action type {action.action_type}"

        except Exception as e:
            return False, resolved_selector, f"Execution failed: {str(e)}"

    async def close(self):
        try:
            if self.page:
                await self.page.close()
            if self._context:
                await self._context.close()
            if self._browser:
                await self._browser.close()
            if self._playwright:
                await self._playwright.stop()
        except Exception:
            pass
