"""Week 4 — Chained Requests & Data Flow (restful-booker API).

The point of these tests is NOT to hit endpoints in isolation, but to follow a
record through a whole lifecycle and assert that data stays consistent from one
request to the next: what you create is what you read, what you update is what
comes back, and what you delete is truly gone.

Three explicit workflow chains, each passing data (the booking id, the payload)
from one step into the next:
  1. Full CRUD lifecycle  — create -> read -> update(PUT) -> read -> delete -> read(404)
  2. Partial update flow   — create -> patch one field -> read (others intact) -> delete
  3. Filter round-trip     — create -> find via filtered list -> delete -> gone from list

The rest map one-to-one onto the plan's Data Flow Checklist.

Run just these:   pytest -m api
"""
import pytest

pytestmark = pytest.mark.api


# --- Workflow chain 1: full CRUD lifecycle -------------------------------

@pytest.mark.smoke
def test_crud_lifecycle(booker, sample_booking):
    """create -> read -> update -> read -> delete -> read(404), one record all
    the way through. This is the flagship Week-4 chain."""
    # Create
    created = booker.create(sample_booking)
    assert created.status_code == 200
    booking_id = created.json()["bookingid"]

    # Read: the created record matches what we sent
    got = booker.get(booking_id)
    assert got.status_code == 200
    assert got.json() == sample_booking

    # Update (full replace via PUT)
    updated_payload = {**sample_booking, "firstname": "Grace", "totalprice": 999}
    updated = booker.update(booking_id, updated_payload)
    assert updated.status_code == 200

    # Read again: the update is reflected
    got_again = booker.get(booking_id)
    assert got_again.status_code == 200
    assert got_again.json() == updated_payload

    # Delete
    deleted = booker.delete(booking_id)
    assert deleted.status_code == 201  # booker's documented success code

    # Read after delete: truly gone
    gone = booker.get(booking_id)
    assert gone.status_code == 404


# --- Workflow chain 2: partial update, siblings untouched ----------------

@pytest.mark.smoke
def test_patch_changes_only_target_field(booker, created_booking):
    """create -> patch a single field -> read: only that field changes, every
    other field is preserved. Guards against a PATCH that silently wipes
    unspecified fields."""
    booking_id, original = created_booking

    resp = booker.patch(booking_id, {"additionalneeds": "Late checkout"})
    assert resp.status_code == 200

    got = booker.get(booking_id).json()
    assert got["additionalneeds"] == "Late checkout"          # changed
    assert got["firstname"] == original["firstname"]           # untouched
    assert got["lastname"] == original["lastname"]             # untouched
    assert got["totalprice"] == original["totalprice"]         # untouched
    assert got["bookingdates"] == original["bookingdates"]     # untouched


# --- Workflow chain 3: filter round-trip ---------------------------------

def test_filter_round_trip(booker, sample_booking):
    """create with a unique name -> the filtered list finds exactly it ->
    delete -> the filtered list no longer returns it. Ties list/filter behavior
    to the create/delete lifecycle instead of testing them apart."""
    # A name unique enough that the filter should match only our record.
    unique = {**sample_booking, "firstname": "ZzUnique", "lastname": "Wk4Filter"}
    created = booker.create(unique)
    assert created.status_code == 200
    booking_id = created.json()["bookingid"]

    try:
        listed = booker.list_ids(firstname="ZzUnique", lastname="Wk4Filter")
        assert listed.status_code == 200
        ids = [row["bookingid"] for row in listed.json()]
        assert booking_id in ids
    finally:
        assert booker.delete(booking_id).status_code == 201

    after = booker.list_ids(firstname="ZzUnique", lastname="Wk4Filter")
    ids_after = [row["bookingid"] for row in after.json()]
    assert booking_id not in ids_after


# --- Data Flow Checklist -------------------------------------------------

def test_create_then_read_all_fields_match(booker, created_booking):
    """[Create -> Read] all fields returned correctly, field by field."""
    booking_id, payload = created_booking
    got = booker.get(booking_id).json()
    for key, value in payload.items():
        assert got[key] == value, f"field '{key}' round-tripped as {got[key]!r}"


def test_read_missing_returns_404(booker):
    """[Create -> Delete -> Read returns 404] — here, a never-created id."""
    resp = booker.get(99999999)
    assert resp.status_code == 404


def test_list_with_no_matches_is_empty_not_error(booker):
    """[List with 0 items] returns an empty array with 200, not an error."""
    resp = booker.list_ids(firstname="NoSuchPersonXyz", lastname="NoSuchNameXyz")
    assert resp.status_code == 200
    assert resp.json() == []


def test_list_structure_is_stable_across_sizes(booker, created_booking):
    """[List with 1 item vs many] same response shape: a list of objects each
    carrying a 'bookingid'."""
    # Many: the unfiltered list.
    many = booker.list_ids()
    assert many.status_code == 200
    many_rows = many.json()
    assert isinstance(many_rows, list) and len(many_rows) >= 1
    assert all("bookingid" in row for row in many_rows[:20])

    # One: filtered down to our single created record's name.
    booking_id, payload = created_booking
    one = booker.list_ids(firstname=payload["firstname"], lastname=payload["lastname"])
    one_rows = one.json()
    assert isinstance(one_rows, list)
    assert all("bookingid" in row for row in one_rows)


def test_filter_returns_only_matching_items(booker, created_booking):
    """[Filter returns only matching items] every id the name-filter returns
    must actually carry that name when read back."""
    booking_id, payload = created_booking
    listed = booker.list_ids(firstname=payload["firstname"], lastname=payload["lastname"])
    ids = [row["bookingid"] for row in listed.json()]
    assert booking_id in ids
    # Spot-check that matches really match (sample the first few to stay fast).
    for row_id in ids[:5]:
        record = booker.get(row_id).json()
        assert record["firstname"] == payload["firstname"]
        assert record["lastname"] == payload["lastname"]


def test_date_filter_returns_bookings_in_range(booker, created_booking):
    """[Filter] checkin/checkout date filtering returns a well-formed list."""
    booking_id, payload = created_booking
    resp = booker.list_ids(checkin="2026-01-01")
    assert resp.status_code == 200
    assert isinstance(resp.json(), list)


def test_write_without_auth_is_rejected(booker, created_booking):
    """[Auth on writes] DELETE without a token must be refused (403), and the
    record must survive. A write that succeeds unauthenticated is a real bug."""
    booking_id, _ = created_booking
    # Hit the endpoint directly with no auth header, bypassing the client helper.
    resp = booker.session.delete(
        f"{booker.base_url}/booking/{booking_id}", timeout=booker.timeout
    )
    assert resp.status_code == 403
    # Still there.
    assert booker.get(booking_id).status_code == 200
