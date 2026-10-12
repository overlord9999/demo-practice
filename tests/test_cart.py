"""Cart tests against saucedemo.com: add/remove items and the header badge.

Run only these:   pytest tests/test_cart.py
"""
import pytest
from playwright.sync_api import Page, expect

from pages.login_page import LoginPage

BACKPACK = "sauce-labs-backpack"
BIKE_LIGHT = "sauce-labs-bike-light"


@pytest.fixture
def inventory(page: Page, base_url, demo_credentials):
    """Logged-in inventory page with an empty cart (fresh browser context)."""
    inv = LoginPage(page).open(base_url).login(**demo_credentials)
    inv.assert_loaded()
    expect(inv.cart_badge).to_have_count(0)
    return inv


@pytest.mark.smoke
def test_add_item_to_cart(inventory):
    inventory.add_to_cart(BACKPACK)
    expect(inventory.cart_badge).to_have_text("1")

    cart = inventory.open_cart().assert_loaded()
    expect(cart.item_names).to_have_text(["Sauce Labs Backpack"])


@pytest.mark.regression
def test_remove_item_updates_badge(inventory):
    inventory.add_to_cart(BACKPACK).add_to_cart(BIKE_LIGHT)
    expect(inventory.cart_badge).to_have_text("2")

    inventory.remove_from_cart(BACKPACK)
    expect(inventory.cart_badge).to_have_text("1")

    inventory.remove_from_cart(BIKE_LIGHT)
    expect(inventory.cart_badge).to_have_count(0)
