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
        self.cart_link = page.get_by_test_id("shopping-cart-link")
        self.cart_badge = page.get_by_test_id("shopping-cart-badge")

    def assert_loaded(self):
        expect(self.page).to_have_url(re.compile(r"/inventory\.html"))
        expect(self.title).to_have_text("Products")
        expect(self.inventory_list).to_be_visible()
        return self

    # Item buttons use a slug of the product name, e.g. "sauce-labs-backpack":
    #   add-to-cart-sauce-labs-backpack  ->  remove-sauce-labs-backpack
    def add_to_cart(self, slug: str):
        self.page.get_by_test_id(f"add-to-cart-{slug}").click()
        return self

    def remove_from_cart(self, slug: str):
        self.page.get_by_test_id(f"remove-{slug}").click()
        return self

    def open_cart(self):
        from pages.cart_page import CartPage
        self.cart_link.click()
        return CartPage(self.page)

    def logout(self):
        self.menu_button.click()
        self.logout_link.click()
        return self
