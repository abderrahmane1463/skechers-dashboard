"""
api/boost.py — Meta Marketing API fetch functions (paid campaigns).

The _assert_not_blocked() guard from api/base.py is intentionally NOT used
here. The ad account in BLOCKED_AD_ACCOUNTS is "blocked" only for organic
endpoints (fetch_fb_*, fetch_ig_*) to enforce the organic-only constraint.
This module is the single authorised place to query it.

Required token permissions: ads_read (the long-lived page token in config.py
must have been generated with this scope, or a User token with ads_read must
replace it for this endpoint).
"""

import time
import requests

from config import (
    ACCESS_TOKEN,
    GRAPH_BASE_URL,
    BLOCKED_AD_ACCOUNTS,
    REQUEST_TIMEOUT,
    MAX_RETRIES,
    RETRY_BACKOFF,
)
from api.base import _date_range

# The page's ad account — intentionally queried here (Boost tab only)
AD_ACCOUNT_ID = BLOCKED_AD_ACCOUNTS[0]   # "act_765947885726761"

# Meta action types that represent a purchase / conversion
_PURCHASE_TYPES = {"purchase", "offsite_conversion.fb_pixel_purchase"}

# Campaign objectives that count as "conversion" campaigns
_CONV_OBJECTIVES = {"CONVERSIONS", "OUTCOME_SALES", "OUTCOME_LEADS"}


# ─── Internal HTTP layer (no block-guard) ─────────────────────────────────────
def _get_ads(endpoint: str, params: dict) -> dict:
    """
    GET against the Meta Marketing API with retry + backoff.
    Bypasses _assert_not_blocked() — this is intentional (see module docstring).
    """
    url = f"{GRAPH_BASE_URL}/{endpoint.lstrip('/')}"
    full_params = {**params, "access_token": ACCESS_TOKEN}

    for attempt in range(1, MAX_RETRIES + 1):
        try:
            resp = requests.get(url, params=full_params, timeout=REQUEST_TIMEOUT)
            if resp.status_code not in (200, 400):
                print(f"DEBUG ads: HTTP {resp.status_code} on {endpoint}: {resp.text[:200]}")
            if resp.status_code == 429:
                time.sleep(RETRY_BACKOFF ** attempt)
                continue
            resp.raise_for_status()
            return resp.json()
        except requests.exceptions.RequestException as exc:
            print(f"DEBUG ads: request failed (attempt {attempt}): {exc}")
            if attempt == MAX_RETRIES:
                raise
            time.sleep(RETRY_BACKOFF ** attempt)

    return {}


# ─── Helpers ──────────────────────────────────────────────────────────────────
def _purchases(actions: list) -> int:
    return sum(
        int(float(a.get("value", 0)))
        for a in (actions or [])
        if a.get("action_type") in _PURCHASE_TYPES
    )


def _cpa(cost_per_action: list) -> float:
    for item in (cost_per_action or []):
        if item.get("action_type") in _PURCHASE_TYPES:
            return float(item.get("value", 0.0))
    return 0.0


def _safe_float(val, default=0.0) -> float:
    try:
        return float(val)
    except (TypeError, ValueError):
        return default


def _safe_int(val, default=0) -> int:
    try:
        return int(float(val))
    except (TypeError, ValueError):
        return default


# ─── Public fetch function ────────────────────────────────────────────────────
def fetch_boost_insights(
    days: int = 30,
    start: str = None,
    end: str = None,
) -> dict:
    """
    Fetch paid campaign performance from the Meta Marketing API.

    Returns a dict with the same shape as views/boost.py:empty_boost_data()
    so the UI can be called identically whether data is real or placeholder.

    Parameters
    ----------
    days  : fallback window if start/end are not provided
    start : ISO date string "YYYY-MM-DD"
    end   : ISO date string "YYYY-MM-DD"
    """
    since, until = _date_range(days, start, end)
    time_range   = f'{{"since":"{since}","until":"{until}"}}'

    # Fields requested from every campaign row
    _FIELDS = (
        "campaign_name,objective,"
        "impressions,reach,clicks,unique_clicks,"
        "spend,cpc,ctr,frequency,"
        "actions,cost_per_action_type"
    )

    # ── Initialise output with zero defaults ──────────────────────────────────
    out = {
        "totals": {
            "campaigns_count": 0,
            "link_clicks":     0,
            "reach":           0,
            "impressions":     0,
            "cpc":             0.0,
            "ctr":             0.0,
            "spend":           0.0,
            "frequency":       0.0,
        },
        "conversions": {
            "campaigns_count":     0,
            "link_clicks":         0,
            "reach":               0,
            "impressions":         0,
            "cpc":                 0.0,
            "ctr":                 0.0,
            "spend":               0.0,
            "frequency":           0.0,
            "cost_per_conversion": 0.0,
            "total_conversions":   0,
        },
        "campaigns": [],
    }

    # ── 1. Account-level totals (single aggregated row) ───────────────────────
    try:
        resp = _get_ads(f"{AD_ACCOUNT_ID}/insights", {
            "level":      "account",
            "fields":     "impressions,reach,unique_clicks,spend,cpc,ctr,frequency",
            "time_range": time_range,
        })
        rows = resp.get("data", [])
        if rows:
            r = rows[0]
            out["totals"]["impressions"]  = _safe_int(r.get("impressions"))
            out["totals"]["reach"]        = _safe_int(r.get("reach"))
            out["totals"]["link_clicks"]  = _safe_int(r.get("unique_clicks") or r.get("clicks"))
            out["totals"]["spend"]        = _safe_float(r.get("spend"))
            out["totals"]["cpc"]          = _safe_float(r.get("cpc"))
            out["totals"]["ctr"]          = _safe_float(r.get("ctr"))
            out["totals"]["frequency"]    = _safe_float(r.get("frequency"))
    except Exception as e:
        print(f"DEBUG boost: account-level totals error: {e}")

    # ── 2. Campaign-level breakdown ───────────────────────────────────────────
    try:
        resp = _get_ads(f"{AD_ACCOUNT_ID}/insights", {
            "level":      "campaign",
            "fields":     _FIELDS,
            "time_range": time_range,
            "limit":      100,
        })
        rows = resp.get("data", [])
        out["totals"]["campaigns_count"] = len(rows)

        campaigns = []
        # Accumulators for conversion-objective campaigns only
        cv_clicks = cv_reach = cv_imp = cv_purchases = 0
        cv_spend  = 0.0
        cv_cpcs:  list[float] = []
        cv_ctrs:  list[float] = []
        cv_freqs: list[float] = []

        for r in rows:
            objective = r.get("objective", "")
            purchases = _purchases(r.get("actions"))
            cpa_val   = _cpa(r.get("cost_per_action_type"))
            spend_val = _safe_float(r.get("spend"))
            cpc_val   = _safe_float(r.get("cpc"))
            ctr_val   = _safe_float(r.get("ctr"))
            freq_val  = _safe_float(r.get("frequency"))
            clicks_val= _safe_int(r.get("unique_clicks") or r.get("clicks"))
            reach_val = _safe_int(r.get("reach"))
            imp_val   = _safe_int(r.get("impressions"))

            campaigns.append({
                "name":        r.get("campaign_name", "—"),
                "objective":   objective,
                "spend":       spend_val,
                "conversions": purchases,
                "cpa":         cpa_val if cpa_val else (spend_val / purchases if purchases else 0.0),
                "clicks":      clicks_val,
                "reach":       reach_val,
                "impressions": imp_val,
                "cpc":         cpc_val,
                "ctr":         ctr_val,
                "frequency":   freq_val,
            })

            # Aggregate conversion campaigns
            if objective in _CONV_OBJECTIVES:
                cv_clicks    += clicks_val
                cv_reach     += reach_val
                cv_imp       += imp_val
                cv_spend     += spend_val
                cv_purchases += purchases
                if cpc_val:  cv_cpcs.append(cpc_val)
                if ctr_val:  cv_ctrs.append(ctr_val)
                if freq_val: cv_freqs.append(freq_val)

        out["campaigns"] = campaigns

        cv_count = sum(1 for c in campaigns if c["objective"] in _CONV_OBJECTIVES)
        out["conversions"].update({
            "campaigns_count":     cv_count,
            "link_clicks":         cv_clicks,
            "reach":               cv_reach,
            "impressions":         cv_imp,
            "spend":               cv_spend,
            "cpc":                 sum(cv_cpcs)  / len(cv_cpcs)  if cv_cpcs  else 0.0,
            "ctr":                 sum(cv_ctrs)  / len(cv_ctrs)  if cv_ctrs  else 0.0,
            "frequency":           sum(cv_freqs) / len(cv_freqs) if cv_freqs else 0.0,
            "total_conversions":   cv_purchases,
            "cost_per_conversion": cv_spend / cv_purchases if cv_purchases else 0.0,
        })

    except Exception as e:
        print(f"DEBUG boost: campaign-level breakdown error: {e}")

    return out
