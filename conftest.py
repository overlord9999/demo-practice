"""Shared fixtures, auto-discovered by pytest (no imports needed in tests)."""
import os
import pytest

import config


@pytest.fixture(scope="session", autouse=True)
def _use_data_test_attribute(playwright):
    """saucedemo.com tags controls with `data-test`, but Playwright's
    get_by_test_id() defaults to `data-testid`. Point it at the real attribute
    so get_by_test_id("username") resolves to [data-test="username"]."""
    playwright.selectors.set_test_id_attribute("data-test")


@pytest.fixture(scope="session")
def base_url():
    return config.BASE_URL


@pytest.fixture(scope="session")
def demo_credentials():
    return {"user": config.USER, "password": config.PASSWORD}


@pytest.fixture(autouse=True)
def _ensure_screenshot_dir():
    os.makedirs("screenshots", exist_ok=True)
