"""Cart page object — /cart.html, reached via the cart icon in the header.

Each cart row shows the item name ([data-test="inventory-item-name"]) and a
"Remove" button. The page title reads "Your Cart".
"""
import re

from playwright.sync_api import Page, expect
from pages.base_page import BasePage


class CartPage(BasePage):
    def __init__(self, page: Page):
        super().__init__(page)
        self.title = page.locator(".title")                 # "Your Cart"
        self.item_names = page.get_by_test_id("inventory-item-name")

    def assert_loaded(self):
        expect(self.page).to_have_url(re.compile(r"/cart\.html"))
        expect(self.title).to_have_text("Your Cart")
        return self
