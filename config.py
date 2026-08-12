"""Central config — reads from environment (.env locally, secrets in CI).

The saucedemo.com credentials are PUBLIC (documented on the site's login page),
so they're safe defaults here. We still route them through env vars to practice
the exact same secrets pattern you'd use for a real, private app in CI.
"""
import os
from dotenv import load_dotenv

load_dotenv()  # loads .env if present; no-op in CI where vars come from secrets

BASE_URL = os.getenv("DEMO_BASE_URL", "https://www.saucedemo.com/")
# Public demo creds — fine as defaults; override via .env / CI secrets to practice the pattern.
USER = os.getenv("DEMO_USER", "standard_user")
PASSWORD = os.getenv("DEMO_PASSWORD", "secret_sauce")

# --- API practice (Week 4: Chained Requests & Data Flow) ---
# restful-booker is a PUBLIC API sandbox built for testing (NDA-safe). It persists
# real records, needs a token for writes, and has documented quirks — ideal for
# exercising CRUD chains and data-flow assertions.
API_BASE_URL = os.getenv("BOOKER_BASE_URL", "https://restful-booker.herokuapp.com")
# Public credentials, documented at https://restful-booker.herokuapp.com/apidoc/
API_USER = os.getenv("BOOKER_USER", "admin")
API_PASSWORD = os.getenv("BOOKER_PASSWORD", "password123")
