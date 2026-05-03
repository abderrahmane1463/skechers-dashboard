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

import json
import time
import requests

from config import (
    ADS_ACCESS_TOKEN,
    FACEBOOK_PAGE_ID,
    FOOTLAND_CAMPAIGN_KEYWORDS,
    GRAPH_BASE_URL,
    BLOCKED_AD_ACCOUNTS,
    REQUEST_TIMEOUT,
    MAX_RETRIES,
    RETRY_BACKOFF,
)
from api.base import _date_range

# The page's ad account — intentionally queried here (Boost tab only)
AD_ACCOUNT_ID = BLOCKED_AD_ACCOUNTS[0]   # "act_765947885726761"

# Meta action types that represent a purchase / conversion.
# Use only "purchase" (the unified de-duplicated count Meta exposes).
# "offsite_conversion.fb_pixel_purchase" is the same event and would double-count.
_PURCHASE_TYPES = {"purchase"}

# Campaign objectives that count as "conversion" campaigns
_CONV_OBJECTIVES = {"CONVERSIONS", "OUTCOME_SALES", "OUTCOME_LEADS"}


# ─── Internal HTTP layer (no block-guard) ─────────────────────────────────────
def _get_ads(endpoint: str, params: dict) -> dict:
    """
    GET against the Meta Marketing API with retry + backoff.
    Bypasses _assert_not_blocked() — this is intentional (see module docstring).
    """
    url = f"{GRAPH_BASE_URL}/{endpoint.lstrip('/')}"
    full_params = {**params, "access_token": ADS_ACCESS_TOKEN}

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
    # inline_link_clicks = clicks that go to the destination URL (true "link clicks")
    # unique_inline_link_clicks = deduplicated version
    # clicks/unique_clicks = ALL clicks (reactions, comments, profile, link) — too broad
    _FIELDS = (
        "campaign_id,campaign_name,objective,"
        "impressions,reach,inline_link_clicks,unique_inline_link_clicks,"
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

    # ── 1. Resolve Footland campaign IDs ─────────────────────────────────────
    # The ad account manages multiple clients (Footland, Skechers standalone,
    # Air Algérie, Algérie Télécom, Caarama…).
    # Footland campaigns are identified by either:
    #   (a) page ID "144124252311741" in the name  → post-boost campaigns
    #   (b) "FL" code in the name (- FL -, ON- FL, FL -)  → brand campaigns
    #       e.g. "ClarksON- FL - HF -Week08", "SkechersON- FL - HF -Week08"
    # "Footland" keyword alone also catches branded posts.
    def _is_footland(name: str) -> bool:
        """Returns True if the campaign name matches any Footland keyword."""
        return any(kw in name for kw in FOOTLAND_CAMPAIGN_KEYWORDS)

    footland_ids = []
    try:
        resp = _get_ads(f"{AD_ACCOUNT_ID}/campaigns", {
            "fields": "id,name",
            "limit":  500,
        })
        all_camps = resp.get("data", [])
        footland_ids = [c["id"] for c in all_camps if _is_footland(c.get("name", ""))]
        print(f"DEBUG boost: {len(footland_ids)} Footland campaigns found")
    except Exception as e:
        print(f"DEBUG boost: campaign list error: {e}")

    if not footland_ids:
        return out

    _FILTERING = json.dumps([{
        "field":    "campaign.id",
        "operator": "IN",
        "value":    footland_ids,
    }])

    # ── 2. Account-level deduplicated reach (Footland only) ───────────────────
    try:
        # Use a more explicit time_range parameter for account insights
        resp = _get_ads(f"{AD_ACCOUNT_ID}/insights", {
            "level":         "account",
            "fields":        "reach",
            "filtering":     _FILTERING,
            "time_range":    time_range,
        })
        rows_acc = resp.get("data", [])
        if rows_acc:
            out["totals"]["reach"] = _safe_int(rows_acc[0].get("reach"))
    except Exception as e:
        print(f"DEBUG boost: account-level reach error: {e}")

    # ── 3. Campaign-level insights (Footland only) ────────────────────────────
    try:
        # Ensure the time_range is strictly passed to prevent lifetime defaults
        resp = _get_ads(f"{AD_ACCOUNT_ID}/insights", {
            "level":      "campaign",
            "fields":     _FIELDS,
            "filtering":  _FILTERING,
            "time_range": time_range,
            "limit":      500,
        })
        rows = resp.get("data", [])

        campaigns  = []
        conv_ids:  list[str]   = []   # campaign IDs with conversion objective
        # Accumulators — reach excluded (comes from dedup account-level call)
        t_clicks = t_imp = 0
        t_spend  = 0.0
        t_cpcs:  list[float] = []
        t_ctrs:  list[float] = []
        t_freqs: list[float] = []
        # Conversion-objective accumulators
        cv_clicks = cv_imp = cv_purchases = 0
        cv_spend  = 0.0
        cv_cpcs:  list[float] = []
        cv_ctrs:  list[float] = []
        cv_freqs: list[float] = []

        for r in rows:
            objective  = r.get("objective", "")
            purchases  = _purchases(r.get("actions"))
            cpa_val    = _cpa(r.get("cost_per_action_type"))
            spend_val  = _safe_float(r.get("spend"))
            cpc_val    = _safe_float(r.get("cpc"))
            ctr_val    = _safe_float(r.get("ctr"))
            freq_val   = _safe_float(r.get("frequency"))
            clicks_val = _safe_int(r.get("unique_inline_link_clicks") or r.get("inline_link_clicks"))
            reach_val  = _safe_int(r.get("reach"))
            imp_val    = _safe_int(r.get("impressions"))
            camp_id    = r.get("campaign_id", "")

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

            t_clicks += clicks_val
            t_imp    += imp_val
            t_spend  += spend_val
            if cpc_val:  t_cpcs.append(cpc_val)
            if ctr_val:  t_ctrs.append(ctr_val)
            if freq_val: t_freqs.append(freq_val)

            if objective in _CONV_OBJECTIVES:
                cv_clicks    += clicks_val
                cv_imp       += imp_val
                cv_spend     += spend_val
                cv_purchases += purchases
                if camp_id:  conv_ids.append(camp_id)
                if cpc_val:  cv_cpcs.append(cpc_val)
                if ctr_val:  cv_ctrs.append(ctr_val)
                if freq_val: cv_freqs.append(freq_val)

        # Deduplicated reach for conversion campaigns only
        cv_reach = 0
        if conv_ids:
            try:
                resp_cv = _get_ads(f"{AD_ACCOUNT_ID}/insights", {
                    "level":      "account",
                    "fields":     "reach",
                    "filtering":  json.dumps([{
                        "field": "campaign.id", "operator": "IN", "value": conv_ids
                    }]),
                    "time_range": time_range,
                })
                rows_cv = resp_cv.get("data", [])
                if rows_cv:
                    cv_reach = _safe_int(rows_cv[0].get("reach"))
            except Exception as e:
                print(f"DEBUG boost: conv dedup reach error: {e}")

        out["campaigns"] = campaigns
        active_count = sum(1 for c in campaigns if c["spend"] > 0 or c["impressions"] > 0)

        # Frequency = total_impressions / deduplicated_reach
        # Per-campaign frequency values must NOT be averaged (that ignores campaign size).
        # The account-level deduplicated reach was already fetched above.
        dedup_reach = out["totals"].get("reach", 0)
        total_freq  = round(t_imp / dedup_reach, 2) if dedup_reach else 0.0
        cv_freq     = round(cv_imp / cv_reach,   2) if cv_reach    else 0.0

        # CPC: weighted by clicks (not a simple average)
        # CTR: weighted by impressions
        total_cpc = round(t_spend  / t_clicks,  2) if t_clicks else 0.0
        total_ctr = round(t_clicks / t_imp * 100, 2) if t_imp  else 0.0
        cv_cpc    = round(cv_spend  / cv_clicks,  2) if cv_clicks else 0.0
        cv_ctr    = round(cv_clicks / cv_imp * 100, 2) if cv_imp  else 0.0

        out["totals"].update({
            "campaigns_count": active_count,
            "link_clicks":     t_clicks,
            # reach already set by account-level dedup call above — preserved
            "impressions":     t_imp,
            "spend":           t_spend,
            "cpc":             total_cpc,
            "ctr":             total_ctr,
            "frequency":       total_freq,
        })

        cv_count = sum(1 for c in campaigns if c["objective"] in _CONV_OBJECTIVES)
        out["conversions"].update({
            "campaigns_count":     cv_count,
            "link_clicks":         cv_clicks,
            "reach":               cv_reach,   # deduplicated
            "impressions":         cv_imp,
            "spend":               cv_spend,
            "cpc":                 cv_cpc,
            "ctr":                 cv_ctr,
            "frequency":           cv_freq,
            "total_conversions":   cv_purchases,
            "cost_per_conversion": cv_spend / cv_purchases if cv_purchases else 0.0,
        })

    except Exception as e:
        print(f"DEBUG boost: campaign insights error: {e}")

    return out
