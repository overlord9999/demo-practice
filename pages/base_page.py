"""Shared behaviour for every page object (nav, helpers)."""
from playwright.sync_api import Page


class BasePage:
    def __init__(self, page: Page):
        self.page = page

    def goto(self, url: str):
        self.page.goto(url)
        return self

    def screenshot(self, name: str):
        """Evidence for bug reports — saved under screenshots/."""
        self.page.screenshot(path=f"screenshots/{name}.png", full_page=True)
        return self
