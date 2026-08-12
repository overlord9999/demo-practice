"""A thin service client for the restful-booker API.

This is the API-side analogue of the Page Object: tests talk to booking
endpoints through named methods instead of hand-rolling URLs and headers, so a
Week-4 workflow chain (create -> read -> update -> delete) reads as business
steps, not HTTP plumbing.

restful-booker quirks worth knowing (they make good test targets):
- POST /booking returns 200 (not 201) and wraps the record under "booking".
- Writes (PUT/PATCH/DELETE) require auth: a `Cookie: token=...` header.
- DELETE returns 201 on success and 405 if the record is already gone.
- GET /booking/{missing} returns 404 with a plain-text body, not JSON.
"""
from __future__ import annotations

import requests


class BookerClient:
    def __init__(self, base_url: str, timeout: float = 15.0):
        self.base_url = base_url.rstrip("/")
        self.timeout = timeout
        self.token: str | None = None
        # One session = one TCP connection reused across the chain, and a place
        # to hang the JSON headers every request needs.
        self.session = requests.Session()
        self.session.headers.update(
            {"Content-Type": "application/json", "Accept": "application/json"}
        )

    # --- auth -------------------------------------------------------------
    def authenticate(self, username: str, password: str) -> str:
        """POST /auth -> token. Stored for later writes and returned."""
        r = self.session.post(
            f"{self.base_url}/auth",
            json={"username": username, "password": password},
            timeout=self.timeout,
        )
        r.raise_for_status()
        body = r.json()
        if "token" not in body:
            # Booker answers bad creds with 200 + {"reason": "Bad credentials"}.
            raise AssertionError(f"Auth failed: {body}")
        self.token = body["token"]
        return self.token

    def _auth_headers(self) -> dict:
        if not self.token:
            raise RuntimeError("authenticate() must be called before writes")
        return {"Cookie": f"token={self.token}"}

    # --- reads ------------------------------------------------------------
    def list_ids(self, **filters) -> requests.Response:
        """GET /booking, optionally with firstname/lastname/checkin/checkout."""
        return self.session.get(
            f"{self.base_url}/booking", params=filters or None, timeout=self.timeout
        )

    def get(self, booking_id: int) -> requests.Response:
        return self.session.get(
            f"{self.base_url}/booking/{booking_id}", timeout=self.timeout
        )

    # --- writes -----------------------------------------------------------
    def create(self, payload: dict) -> requests.Response:
        return self.session.post(
            f"{self.base_url}/booking", json=payload, timeout=self.timeout
        )

    def update(self, booking_id: int, payload: dict) -> requests.Response:
        """Full replace (PUT). Requires auth."""
        return self.session.put(
            f"{self.base_url}/booking/{booking_id}",
            json=payload,
            headers=self._auth_headers(),
            timeout=self.timeout,
        )

    def patch(self, booking_id: int, payload: dict) -> requests.Response:
        """Partial update (PATCH). Requires auth."""
        return self.session.patch(
            f"{self.base_url}/booking/{booking_id}",
            json=payload,
            headers=self._auth_headers(),
            timeout=self.timeout,
        )

    def delete(self, booking_id: int) -> requests.Response:
        return self.session.delete(
            f"{self.base_url}/booking/{booking_id}",
            headers=self._auth_headers(),
            timeout=self.timeout,
        )
