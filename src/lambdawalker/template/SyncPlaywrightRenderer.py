from playwright.sync_api import sync_playwright


class SyncPlaywrightRenderer:
    def __init__(self, log=lambda m: None, report_progress=lambda p: None):
        self.playwright = None
        self.browser = None
        self.context = None
        self.page = None
        self.log = log
        self.report_progress = report_progress

    def start(self, headless=True):
        # Initialize the sync playwright manager
        self.playwright = sync_playwright().start()

        # Launch browser and create context/page
        self.browser = self.playwright.chromium.launch(headless=headless)
        self.context = self.browser.new_context()
        self.page = self.context.new_page()

        self.log(f"Playwright renderer started (Sync) with headless mode: {headless}")
        return self

    def close(self):
        if self.context:
            self.context.close()
        if self.browser:
            self.browser.close()
        if self.playwright:
            self.playwright.stop()