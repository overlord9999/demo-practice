"""Shared fixtures, auto-discovered by pytest (no imports needed in tests)."""
import os
import pytest

import config
from api.booker_client import BookerClient


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


# --- API fixtures (Week 4) ----------------------------------------------

@pytest.fixture(scope="session")
def booker():
    """An authenticated BookerClient, shared across the API test session."""
    client = BookerClient(config.API_BASE_URL)
    client.authenticate(config.API_USER, config.API_PASSWORD)
    return client


@pytest.fixture
def sample_booking():
    """A fresh, valid booking payload for each test that needs one."""
    return {
        "firstname": "Ada",
        "lastname": "Lovelace",
        "totalprice": 240,
        "depositpaid": True,
        "bookingdates": {"checkin": "2026-02-01", "checkout": "2026-02-07"},
        "additionalneeds": "Breakfast",
    }


@pytest.fixture
def created_booking(booker, sample_booking):
    """Create a booking, yield (id, payload), then delete it — so tests never
    leak records and each starts from a known state."""
    resp = booker.create(sample_booking)
    assert resp.status_code == 200, f"setup create failed: {resp.status_code}"
    booking_id = resp.json()["bookingid"]
    yield booking_id, sample_booking
    # Teardown: best-effort cleanup; the record may already be gone if the test
    # deleted it, and that's fine.
    booker.delete(booking_id)
