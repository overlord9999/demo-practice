"""Login page object for saucedemo.com.

Locators are STABLE: saucedemo.com ships `data-test` attributes on every control
(a model example of what we ask the BP devs to add). We use them by preference,
which makes these tests resilient to text/CSS changes.

Gotcha: Playwright's get_by_test_id() defaults to the `data-testid` attribute,
but this site uses `data-test`. conftest.py remaps it once per session via
playwright.selectors.set_test_id_attribute("data-test").

  username field : input[data-test="username"]   (#user-name)
  password field : input[data-test="password"]   (#password)
  login button   : input[data-test="login-button"] (#login-button, value="Login")
  error banner   : [data-test="error"]            (shown on bad credentials)
"""
from playwright.sync_api import Page
from pages.base_page import BasePage
from pages.inventory_page import InventoryPage


class LoginPage(BasePage):
    def __init__(self, page: Page):
        super().__init__(page)
        self.username = page.get_by_test_id("username")
        self.password = page.get_by_test_id("password")
        self.submit = page.get_by_test_id("login-button")
        self.error = page.get_by_test_id("error")

    def open(self, base_url: str):
        self.goto(base_url)
        return self

    def login(self, user: str, password: str) -> InventoryPage:
        self.username.fill(user)
        self.password.fill(password)
        self.submit.click()
        return InventoryPage(self.page)
