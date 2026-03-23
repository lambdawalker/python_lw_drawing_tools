from playwright.async_api import async_playwright


class AsyncPlaywrightRenderer:
    def __init__(self, log=lambda m: None, report_progress=lambda p: None):
        self.playwright = None
        self.browser = None
        self.context = None
        self.page = None
        self.log = log
        self.report_progress = report_progress

    async def start(self, headless=True):
        self.playwright = await async_playwright().start()
        self.browser = await self.playwright.chromium.launch(headless=headless)
        self.context = await self.browser.new_context()
        self.page = await self.context.new_page()
        self.log(f"Playwright renderer started with headless mode: {headless}")
        return self

    async def close(self):
        if self.context:
            await self.context.close()
        if self.browser:
            await self.browser.close()
        if self.playwright:
            await self.playwright.stop()
