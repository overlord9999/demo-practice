"""Inventory ("Products") page object — the post-login landing page.

After a successful login saucedemo.com redirects to /inventory.html and shows a
"Products" header plus the product grid. Logout lives behind the burger menu.
"""
import re

from playwright.sync_api import Page, expect
from pages.base_page import BasePage


class InventoryPage(BasePage):
    def __init__(self, page: Page):
        super().__init__(page)
        self.title = page.locator(".title")                 # "Products"
        self.inventory_list = page.locator(".inventory_list")
        self.menu_button = page.locator("#react-burger-menu-btn")
        self.logout_link = page.get_by_test_id("logout-sidebar-link")

    def assert_loaded(self):
        expect(self.page).to_have_url(re.compile(r"/inventory\.html"))
        expect(self.title).to_have_text("Products")
        expect(self.inventory_list).to_be_visible()
        return self

    def logout(self):
        self.menu_button.click()
        self.logout_link.click()
        return self
