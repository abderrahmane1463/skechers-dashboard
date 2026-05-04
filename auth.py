"""
auth.py — Supabase Auth helpers for Footland dashboard.
"""

import os
import requests
from dotenv import load_dotenv

load_dotenv()

SUPABASE_URL = os.environ["SUPABASE_URL"]
SUPABASE_KEY = os.environ["SUPABASE_KEY"]

_AUTH_HEADERS = {
    "apikey":       SUPABASE_KEY,
    "Content-Type": "application/json",
}

_REST_HEADERS = {
    "apikey":        SUPABASE_KEY,
    "Authorization": f"Bearer {SUPABASE_KEY}",
    "Content-Type":  "application/json",
}


def login(email: str, password: str) -> dict:
    """
    Authenticate with Supabase.
    Returns {"user": {...}, "access_token": "...", "role": "admin"|"viewer", "display_name": "..."}
    Raises ValueError with a user-facing message on failure.
    """
    resp = requests.post(
        f"{SUPABASE_URL}/auth/v1/token?grant_type=password",
        headers=_AUTH_HEADERS,
        json={"email": email, "password": password},
        timeout=10,
    )
    if resp.status_code != 200:
        body = resp.json()
        msg = body.get("error_description") or body.get("msg") or "Login failed"
        raise ValueError(msg)

    data        = resp.json()
    user        = data["user"]
    user_id     = user["id"]

    profile = _get_profile(user_id)
    return {
        "user_id":      user_id,
        "email":        user.get("email", ""),
        "access_token": data["access_token"],
        "role":         profile.get("role", "viewer"),
        "display_name": profile.get("display_name", user.get("email", "")),
    }


def _get_profile(user_id: str) -> dict:
    """Fetch role + display_name from the profiles table."""
    resp = requests.get(
        f"{SUPABASE_URL}/rest/v1/profiles",
        headers={**_REST_HEADERS, "Prefer": ""},
        params={
            "user_id": f"eq.{user_id}",
            "select":  "role,display_name",
            "limit":   "1",
        },
        timeout=10,
    )
    rows = resp.json() if resp.ok else []
    return rows[0] if rows else {}
