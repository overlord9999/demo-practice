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
