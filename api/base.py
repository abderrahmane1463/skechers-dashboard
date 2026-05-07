"""
api/base.py — Shared HTTP helpers, date utilities, and health check.
"""

import time
import requests
from datetime import datetime, timedelta, timezone

from config import (
    GRAPH_BASE_URL,
    ACCESS_TOKEN,
    BLOCKED_AD_ACCOUNTS,
    REQUEST_TIMEOUT,
    MAX_RETRIES,
    RETRY_BACKOFF,
)


def _assert_not_blocked(endpoint: str):
    """Raise if any blocked ad account ID appears in the endpoint."""
    for blocked in BLOCKED_AD_ACCOUNTS:
        if blocked in endpoint:
            raise ValueError(
                f"🚫 Blocked endpoint — ad account data is prohibited: {blocked}"
            )


def _get(endpoint: str, params: dict) -> dict:
    """
    Perform a GET request against the Meta Graph API with retry + backoff.
    Returns the parsed JSON response or raises on unrecoverable error.
    """
    _assert_not_blocked(endpoint)
    url = f"{GRAPH_BASE_URL}/{endpoint.lstrip('/')}"
    params["access_token"] = ACCESS_TOKEN

    for attempt in range(1, MAX_RETRIES + 1):
        try:
            resp = requests.get(url, params=params, timeout=REQUEST_TIMEOUT)
            if resp.status_code != 200:
                print(f"DEBUG: API Error {resp.status_code} on {endpoint}: {resp.text}")
            if resp.status_code == 429:
                wait = RETRY_BACKOFF ** attempt
                time.sleep(wait)
                continue
            resp.raise_for_status()
            return resp.json()
        except requests.exceptions.RequestException as exc:
            print(f"DEBUG: Request failed: {exc}")
            if attempt == MAX_RETRIES:
                raise exc
            time.sleep(RETRY_BACKOFF ** attempt)

    return {}


def _date_range(days: int, start: str = None, end: str = None) -> tuple[str, str]:
    """Return (since, until) ISO date strings — always computed from today for API calls."""
    if start and end:
        return start, end
    until = datetime.now(timezone.utc).date()
    since = until - timedelta(days=days)
    return str(since), str(until)


def _cache_key_range(days: int, start: str = None, end: str = None) -> tuple[str, str]:
    """
    Return a STABLE Supabase cache key.
    - Rolling periods (Last 7/14/30/60/90 Days): key never changes → "rolling" / "last_Xd"
    - Fixed ranges (custom dates, calendar periods): use actual dates as key
    Only a manual Refresh wipes the entry.
    """
    if start and end:
        return start, end          # fixed range — key is the actual dates
    return "rolling", f"last_{days}d"   # rolling — always the same key


def _prev_date_range(days: int) -> tuple[str, str]:
    """Return the equivalent previous period for delta comparisons."""
    until = datetime.now(timezone.utc).date() - timedelta(days=days)
    since = until - timedelta(days=days)
    return str(since), str(until)


def _get_insights_chunked(endpoint: str, params: dict, since: str, until: str, chunk_days: int = 88) -> dict:
    """
    Fetch Facebook Insights for wide date ranges by splitting into ≤88-day chunks.
    The Insights API silently returns nothing (or errors) for requests > ~92 days.
    Returns a merged response shaped like a normal _get() Insights response:
        {"data": [{"name": "metric_name", "values": [...]}]}
    """
    from datetime import date as _d, timedelta as _td

    s = _d.fromisoformat(since)
    u = _d.fromisoformat(until)
    accumulated: dict = {}   # metric_name → [value dicts]

    chunk_start = s
    while chunk_start <= u:
        chunk_end = min(chunk_start + _td(days=chunk_days - 1), u)
        chunk_params = {**params, "since": str(chunk_start), "until": str(chunk_end)}
        try:
            data = _get(endpoint, chunk_params)
            for metric in data.get("data", []):
                name = metric.get("name", "")
                accumulated.setdefault(name, []).extend(metric.get("values", []))
        except Exception as e:
            print(f"DEBUG: insights chunk {chunk_start}→{chunk_end}: {e}")
        chunk_start = chunk_end + _td(days=1)

    return {"data": [{"name": n, "values": v} for n, v in accumulated.items()]}


def check_api_health() -> dict:
    """
    Returns API connectivity status and token info.
    Never hits any blocked ad account endpoint.
    """
    try:
        data = _get("me", {"fields": "id,name"})
        return {
            "status": "ok",
            "user_id": data.get("id"),
            "name": data.get("name", "Unknown"),
        }
    except Exception as e:
        return {"status": "error", "message": str(e)}
