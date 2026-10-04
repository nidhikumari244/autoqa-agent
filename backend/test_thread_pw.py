import asyncio
import threading
from playwright.async_api import async_playwright

def run_in_thread():
    loop = asyncio.ProactorEventLoop()
    asyncio.set_event_loop(loop)
    async def task():
        pw = await async_playwright().start()
        browser = await pw.chromium.launch(headless=True)
        page = await browser.new_page()
        await page.goto("https://example.com")
        title = await page.title()
        print("PAGE TITLE:", title)
        await browser.close()
        await pw.stop()
    loop.run_until_complete(task())
    loop.close()

if __name__ == "__main__":
    t = threading.Thread(target=run_in_thread)
    t.start()
    t.join()
    print("SUCCESS IN THREAD!")
