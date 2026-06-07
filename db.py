"""
db.py — Supabase REST API layer for Skechers dashboard.
Stores and retrieves metric results as JSON blobs keyed by (metric_key, period_start, period_end).
"""

import os
from datetime import datetime, timezone

import requests
from dotenv import load_dotenv

load_dotenv()

# ── In-memory invalidation registry ───────────────────────────────────────────
# Maps "metric_key:period_start:period_end" → invalidation timestamp.
# db.load() skips Supabase data fetched before the invalidation time,
# forcing a fresh API call — without needing DELETE or PATCH on Supabase.
_INVALIDATED: dict = {}

# Metric keys grouped by platform
_PLATFORM_METRICS = {
    "Facebook":  ["fb_audience", "fb_engagement", "fb_visibility", "fb_demographics",
                  "fb_posts", "fb_post_totals", "fb_conversations", "fb_messaging"],
    "Instagram": ["ig_profile", "ig_engagement", "ig_posts", "ig_post_totals"],
    "Boost":     ["boost_insights", "fb_demographics", "boost_adset_ad"],
}


def invalidate(platform: str, period_start: str, period_end: str):
    """Invalidate only the current platform + period. Called by the Refresh button."""
    ts = datetime.now(timezone.utc).isoformat()
    for mk in _PLATFORM_METRICS.get(platform, []):
        _INVALIDATED[f"{mk}:{period_start}:{period_end}"] = ts


SUPABASE_URL = os.environ["SUPABASE_URL"]
SUPABASE_KEY = os.environ["SUPABASE_KEY"]
TABLE        = "metric_cache"
ENDPOINT     = f"{SUPABASE_URL}/rest/v1/{TABLE}"

HEADERS = {
    "apikey":        SUPABASE_KEY,
    "Authorization": f"Bearer {SUPABASE_KEY}",
    "Content-Type":  "application/json",
    "Prefer":        "resolution=merge-duplicates,return=minimal",
}


def _get_headers():
    return HEADERS


# ── Write ──────────────────────────────────────────────────────────────────────
def save(metric_key: str, period_start: str, period_end: str, data) -> bool:
    """
    Upsert a metric result into Supabase.
    Uses UNIQUE index on (metric_key, period_start, period_end) to update in place.
    """
    payload = {
        "metric_key":   metric_key,
        "period_start": period_start,
        "period_end":   period_end,
        "data":         data,
        "fetched_at":   datetime.now(timezone.utc).isoformat(),
    }
    try:
        # Try insert first
        resp = requests.post(ENDPOINT, headers=_get_headers(), json=payload, timeout=15)
        if resp.status_code == 409:
            # Row exists — update it via PATCH
            patch_headers = {
                **_get_headers(),
                "Prefer": "return=minimal",
            }
            params = {
                "metric_key":   f"eq.{metric_key}",
                "period_start": f"eq.{period_start}",
                "period_end":   f"eq.{period_end}",
            }
            patch_payload = {
                "data":       data,
                "fetched_at": datetime.now(timezone.utc).isoformat(),
            }
            resp = requests.patch(ENDPOINT, headers=patch_headers, params=params, json=patch_payload, timeout=15)
        resp.raise_for_status()
        return True
    except Exception as e:
        print(f"DEBUG db.save error [{metric_key}]: {e}")
        return False


# ── Read ───────────────────────────────────────────────────────────────────────
def load(metric_key: str, period_start: str, period_end: str):
    """
    Fetch the latest cached result for a given metric + period.
    Returns the data (dict or list) or None if not found.
    """
    params = {
        "metric_key":   f"eq.{metric_key}",
        "period_start": f"eq.{period_start}",
        "period_end":   f"eq.{period_end}",
        "order":        "fetched_at.desc",
        "limit":        "1",
        "select":       "data,fetched_at",
    }
    headers = {**_get_headers(), "Prefer": ""}
    try:
        resp = requests.get(ENDPOINT, headers=headers, params=params, timeout=15)
        resp.raise_for_status()
        rows = resp.json()
        if rows and rows[0]["data"] is not None:
            inv_key = f"{metric_key}:{period_start}:{period_end}"
            inv_ts  = _INVALIDATED.get(inv_key, "")
            if inv_ts and rows[0].get("fetched_at", "") < inv_ts:
                return None
            return rows[0]["data"]
        return None
    except Exception as e:
        print(f"DEBUG db.load error [{metric_key}]: {e}")
        return None


def load_fetched_at(metric_key: str, period_start: str, period_end: str):
    """Returns the fetched_at timestamp string for a metric, or None."""
    params = {
        "metric_key":   f"eq.{metric_key}",
        "period_start": f"eq.{period_start}",
        "period_end":   f"eq.{period_end}",
        "order":        "fetched_at.desc",
        "limit":        "1",
        "select":       "fetched_at",
    }
    headers = {**_get_headers(), "Prefer": ""}
    try:
        resp = requests.get(ENDPOINT, headers=headers, params=params, timeout=15)
        resp.raise_for_status()
        rows = resp.json()
        if rows:
            return rows[0]["fetched_at"]
        return None
    except Exception as e:
        print(f"DEBUG db.load_fetched_at error [{metric_key}]: {e}")
        return None


# ── Delete ─────────────────────────────────────────────────────────────────────
def delete_period(period_start: str, period_end: str) -> bool:
    """
    Delete all cached rows for a given (period_start, period_end).
    The next db._get() call will treat the missing rows as a cache miss
    and re-fetch fresh data from the API.
    """
    try:
        params = {
            "period_start": f"eq.{period_start}",
            "period_end":   f"eq.{period_end}",
        }
        resp = requests.delete(ENDPOINT, headers=_get_headers(), params=params, timeout=15)
        resp.raise_for_status()
        print(f"DEBUG db.delete_period: deleted [{period_start} → {period_end}]")
        return True
    except Exception as e:
        print(f"DEBUG db.delete_period error: {e}")
        return False


# ── High-level getters (cache → API fallback) ──────────────────────────────────
import api
from api.base import _cache_key_range


def _get(metric_key: str, api_fn, days: int, start: str, end: str, default):
    """
    Load from Supabase using a STABLE cache key; fall back to live API if not cached.
    Rolling periods (Last X Days) always use the same key so data is saved forever
    and only re-fetched when the user clicks Refresh.
    Fixed ranges (custom / calendar) use the actual dates as the key.
    """
    ck_start, ck_end = _cache_key_range(days, start, end)
    data = load(metric_key, ck_start, ck_end)
    if data is not None:
        return data
    # Cache miss → call Meta API with real dates, then save under stable key
    data = api_fn(days, start, end)
    save(metric_key, ck_start, ck_end, data)
    return data


def get_ig_profile(days, start=None, end=None):
    return _get("ig_profile", api.fetch_ig_profile, days, start, end, {})

def get_ig_engagement(days, start=None, end=None):
    return _get("ig_engagement", api.fetch_ig_engagement, days, start, end, {})

def get_ig_posts(days, start=None, end=None):
    return _get("ig_posts", lambda d, s, e: api.fetch_ig_posts(d, s, e, 100), days, start, end, [])

def get_ig_post_totals(days, start=None, end=None):
    return _get("ig_post_totals", api.fetch_ig_post_totals, days, start, end, {})

def get_fb_audience(days, start=None, end=None):
    return _get("fb_audience", api.fetch_fb_audience, days, start, end, {})

def get_fb_engagement(days, start=None, end=None):
    return _get("fb_engagement", api.fetch_fb_engagement, days, start, end, {})

def get_fb_visibility(days, start=None, end=None):
    return _get("fb_visibility", api.fetch_fb_visibility, days, start, end, {})

def get_fb_demographics(days, start=None, end=None):
    return _get("fb_demographics", api.fetch_fb_demographics, days, start, end, {})

def get_fb_posts(days, start=None, end=None):
    return _get("fb_posts", lambda d, s, e: api.fetch_fb_posts(d, s, e, 100), days, start, end, [])

def get_fb_post_totals(days, start=None, end=None):
    return _get("fb_post_totals", api.fetch_fb_post_totals, days, start, end, {})

def get_fb_conversations(days, start=None, end=None):
    return _get("fb_conversations", api.fetch_fb_conversations, days, start, end, {})

def get_fb_messaging_stats(days, start=None, end=None):
    return _get("fb_messaging", api.fetch_fb_messaging_stats, days, start, end, {})

def get_boost_insights(days, start=None, end=None):
    from api.boost import fetch_boost_insights
    return _get("boost_insights", fetch_boost_insights, days, start, end, {})

def get_adset_ad_insights(days, start=None, end=None):
    from api.boost import fetch_adset_ad_insights
    return _get("boost_adset_ad", fetch_adset_ad_insights, days, start, end, {"adsets": [], "ads": []})
