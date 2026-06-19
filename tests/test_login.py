"""Login flow tests against the public saucedemo.com sandbox.

Run only the fast checks:   pytest -m smoke
Watch the browser:          pytest -m smoke --headed
Run on Firefox:             pytest -m smoke --browser firefox

These mirror the bp-e2e login tests, but every locator here is stable thanks to
saucedemo's data-test attributes — so this suite is a reliable CI target.
"""
import pytest
from playwright.sync_api import Page, expect

from pages.login_page import LoginPage


@pytest.mark.smoke
def test_login_page_loads(page: Page, base_url):
    page.goto(base_url)
    expect(page).to_have_title("Swag Labs")
    login = LoginPage(page)
    expect(login.username).to_be_visible()
    expect(login.submit).to_be_visible()


@pytest.mark.smoke
def test_successful_login(page: Page, base_url, demo_credentials):
    inventory = LoginPage(page).open(base_url).login(**demo_credentials)
    inventory.assert_loaded()


@pytest.mark.smoke
@pytest.mark.parametrize(
    "user,password,expected_error",
    [
        ("", "", "Username is required"),
        ("standard_user", "", "Password is required"),
        ("standard_user", "wrong_password", "Username and password do not match"),
        ("locked_out_user", "secret_sauce", "Sorry, this user has been locked out"),
    ],
)
def test_login_rejects_bad_credentials(page: Page, base_url, user, password, expected_error):
    login = LoginPage(page).open(base_url)
    login.login(user, password)
    # Stays on the login page and shows the inline error banner.
    expect(login.error).to_be_visible()
    expect(login.error).to_contain_text(expected_error)


@pytest.mark.regression
def test_logout_returns_to_login(page: Page, base_url, demo_credentials):
    inventory = LoginPage(page).open(base_url).login(**demo_credentials)
    inventory.assert_loaded()
    inventory.logout()
    expect(page).to_have_url(base_url)
    expect(LoginPage(page).submit).to_be_visible()
