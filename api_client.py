"""
api_client.py — Footland Meta Graph API Client
Fetches ONLY organic page/profile data. Ad account endpoints are blocked.
"""

import time
import requests
import pandas as pd
from datetime import datetime, timedelta, timezone
from dateutil import parser as dateparser

from config import (
    GRAPH_BASE_URL,
    ACCESS_TOKEN,
    FACEBOOK_PAGE_ID,
    INSTAGRAM_USER_ID,
    BLOCKED_AD_ACCOUNTS,
    REQUEST_TIMEOUT,
    MAX_RETRIES,
    RETRY_BACKOFF,
    FB_POST_FIELDS,
    IG_MEDIA_FIELDS,
    IG_PROFILE_METRICS,
    IG_ENGAGEMENT_METRICS,
)


# ─── Safety Guard ─────────────────────────────────────────────────────────────
def _assert_not_blocked(endpoint: str):
    """Raise if any blocked ad account ID appears in the endpoint."""
    for blocked in BLOCKED_AD_ACCOUNTS:
        if blocked in endpoint:
            raise ValueError(
                f"🚫 Blocked endpoint — ad account data is prohibited: {blocked}"
            )


# ─── HTTP Helper ──────────────────────────────────────────────────────────────
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


# ─── Date Utilities ───────────────────────────────────────────────────────────
def _date_range(days: int, start: str = None, end: str = None) -> tuple[str, str]:
    """Return (since, until) ISO date strings."""
    if start and end:
        return start, end
    until = datetime.now(timezone.utc).date()
    since = until - timedelta(days=days)
    return str(since), str(until)


def _prev_date_range(days: int) -> tuple[str, str]:
    """Return the equivalent previous period for delta comparisons."""
    until = datetime.now(timezone.utc).date() - timedelta(days=days)
    since = until - timedelta(days=days)
    return str(since), str(until)


# ─── Facebook — Audience ──────────────────────────────────────────────────────
def fetch_fb_audience(days: int, start: str = None, end: str = None) -> dict:
    """
    Returns daily follower adds, removes, and cumulative fans
    for the selected period.
    """
    since, until = _date_range(days, start, end)
    result = {"fans_adds": [], "fans_removes": [], "fans_total": None}

    # Total fans (Lifetime metric)
    try:
        data = _get(f"{FACEBOOK_PAGE_ID}/insights/page_fans", {
            "period": "lifetime",
        })
        values = data.get("data", [{}])[0].get("values", [])
        if values:
            result["fans_total"] = values[-1].get("value", 0)
        
        # Fallback if insights are empty/forbidden: query fan_count directly
        if not result["fans_total"]:
            p_data = _get(f"{FACEBOOK_PAGE_ID}", {"fields": "fan_count"})
            result["fans_total"] = p_data.get("fan_count")
    except Exception as e:
        print(f"DEBUG: page_fans error: {e}")
        # Try direct fallback
        try:
            p_data = _get(f"{FACEBOOK_PAGE_ID}", {"fields": "fan_count"})
            result["fans_total"] = p_data.get("fan_count")
        except:
            pass

    # Adds (Try individual calls to avoid API rejection)
    for m_name in ["page_daily_follows", "page_fan_adds"]:
        try:
            data = _get(f"{FACEBOOK_PAGE_ID}/insights", {
                "metric": m_name,
                "period": "day",
                "since": since,
                "until": until,
            })
            for m in data.get("data", []):
                result["fans_adds"].extend([
                    {"date": v["end_time"][:10], "value": v["value"]}
                    for v in m["values"]
                ])
            if result["fans_adds"]: break # Stop if we got data
        except Exception:
            pass

    # Removes
    for m_name in ["page_daily_unfollows", "page_fan_removes"]:
        try:
            data = _get(f"{FACEBOOK_PAGE_ID}/insights", {
                "metric": m_name,
                "period": "day",
                "since": since,
                "until": until,
            })
            for m in data.get("data", []):
                result["fans_removes"].extend([
                    {"date": v["end_time"][:10], "value": v["value"]}
                    for v in m["values"]
                ])
            if result["fans_removes"]: break # Stop if we got data
        except Exception:
            pass

    return result


# ─── Facebook — Engagement ────────────────────────────────────────────────────
def fetch_fb_engagement(days: int, start: str = None, end: str = None) -> dict:
    """
    Returns daily post engagements and reaction breakdowns.
    """
    since, until = _date_range(days, start, end)
    result = {"engagements": [], "reactions": []}

    try:
        data = _get(f"{FACEBOOK_PAGE_ID}/insights/page_post_engagements", {
            "period": "day",
            "since": since,
            "until": until,
        })
        values = data.get("data", [{}])[0].get("values", [])
        result["engagements"] = [
            {"date": v["end_time"][:10], "value": v["value"]}
            for v in values
        ]
    except Exception:
        pass

    try:
        data = _get(
            f"{FACEBOOK_PAGE_ID}/insights/page_actions_post_reactions_total",
            {"period": "day", "since": since, "until": until},
        )
        values = data.get("data", [{}])[0].get("values", [])
        result["reactions"] = [
            {"date": v["end_time"][:10], **v.get("value", {})}
            for v in values
        ]
    except Exception:
        pass

    return result


# ─── Facebook — Visibility / Reach ────────────────────────────────────────────
def fetch_fb_visibility(days: int, start: str = None, end: str = None) -> dict:
    """
    Returns daily reach (unique), impressions, and page views.
    """
    since, until = _date_range(days, start, end)
    result = {"reach": [], "impressions": [], "page_views": []}
    # New Page Experience metrics mapping
    mapping = {
        "page_impressions_unique": "reach",
        "page_posts_impressions": "impressions",
        "page_views_total": "page_views",
    }

    # Fetch metrics using the preferred /insights?metric=... format
    metrics_str = ",".join(mapping.keys())
    try:
        data = _get(f"{FACEBOOK_PAGE_ID}/insights", {
            "metric": metrics_str,
            "period": "day",
            "since": since,
            "until": until,
        })
        for m in data.get("data", []):
            target_key = mapping.get(m["name"])
            if target_key:
                result[target_key] = [
                    {"date": v["end_time"][:10], "value": v["value"]}
                    for v in m["values"]
                ]
    except Exception as e:
        print(f"DEBUG: visibility insights error: {e}")

    return result


# ─── Facebook — Demographics ──────────────────────────────────────────────────
def fetch_fb_demographics() -> dict:
    """
    Returns lifetime page fans broken down by gender and age bracket.
    Uses the page_fans_gender_age lifetime insight metric.
    Returns {
        "age_brackets": ["18-24","25-34",...],
        "men":   [pct, pct, ...],
        "women": [pct, pct, ...],
        "total_men_pct":   float,
        "total_women_pct": float,
    }
    """
    age_order = ["18-24", "25-34", "35-44", "45-54", "55-64", "65+"]
    result = {
        "age_brackets": age_order,
        "men":   [0] * len(age_order),
        "women": [0] * len(age_order),
        "total_men_pct":   0.0,
        "total_women_pct": 0.0,
    }
    try:
        data = _get(f"{FACEBOOK_PAGE_ID}/insights", {
            "metric": "page_fans_gender_age",
            "period": "lifetime",
        })
        entries = data.get("data", [])
        if not entries:
            return result

        raw = entries[0].get("values", [{}])[-1].get("value", {})
        if not raw:
            return result

        # Aggregate totals
        totals = {bracket: {"M": 0, "F": 0} for bracket in age_order}
        grand_total = 0
        for key, count in raw.items():
            parts = key.split(".")
            if len(parts) != 2:
                continue
            gender, age = parts[0], parts[1]
            # Normalise 65+ key variants
            if age.startswith("65"):
                age = "65+"
            if age in totals and gender in ("M", "F"):
                totals[age][gender] += count
                grand_total += count

        if grand_total == 0:
            return result

        men_total   = sum(v["M"] for v in totals.values())
        women_total = sum(v["F"] for v in totals.values())

        result["men"]   = [round(totals[b]["M"] / grand_total * 100, 1) for b in age_order]
        result["women"] = [round(totals[b]["F"] / grand_total * 100, 1) for b in age_order]
        result["total_men_pct"]   = round(men_total   / grand_total * 100, 1)
        result["total_women_pct"] = round(women_total / grand_total * 100, 1)
    except Exception as e:
        print(f"DEBUG demographics error: {e}")
    return result


# ─── Facebook — Posts ─────────────────────────────────────────────────────────
def fetch_fb_posts(days: int = None, start: str = None, end: str = None, limit: int = 100) -> list[dict]:
    """
    Returns Facebook posts within the selected date range.
    """
    params = {"fields": FB_POST_FIELDS, "limit": limit}
    if days or (start and end):
        since, until = _date_range(days or 30, start, end)
        params["since"] = since
        params["until"] = until

    try:
        data = _get(f"{FACEBOOK_PAGE_ID}/posts", params)
        posts = data.get("data", [])
        parsed = []
        for p in posts:
            reacs = p.get("reactions", {}).get("summary", {}).get("total_count", 0)
            comm  = p.get("comments",  {}).get("summary", {}).get("total_count", 0)
            shar  = p.get("shares",    {}).get("count", 0)

            # Fetch per-post reach (organic unique impressions)
            reach = 0
            try:
                ins = _get(f"{p['id']}/insights", {"metric": "post_impressions_unique"})
                for item in ins.get("data", []):
                    if item["name"] == "post_impressions_unique":
                        reach = item["values"][0]["value"] if item.get("values") else 0
            except Exception:
                pass

            parsed.append({
                "id":               p.get("id", ""),
                "text":             p.get("message", p.get("story", ""))[:120],
                "created_time":     p.get("created_time", "")[:10],
                "thumbnail":        p.get("full_picture", ""),
                "reach":            reach,
                "reactions":        reacs,
                "comments":         comm,
                "shares":           shar,
                "total_interactions": reacs + comm + shar,
            })
        return parsed
    except Exception:
        return []


# ─── Facebook — Conversations ─────────────────────────────────────────────────
def fetch_fb_conversations(limit: int = 25) -> dict:
    """
    Returns message thread metadata for community management stats.
    """
    result = {
        "total_threads": 0,
        "replied_threads": 0,
        "response_times_minutes": [],
        "recent_unanswered": [],
    }
    try:
        data = _get(f"{FACEBOOK_PAGE_ID}/conversations", {
            "fields": "id,updated_time,messages{created_time,from,message}",
            "limit": limit,
        })
        threads = data.get("data", [])
        result["total_threads"] = len(threads)

        for thread in threads:
            msgs = thread.get("messages", {}).get("data", [])
            if len(msgs) < 2:
                result["recent_unanswered"].append({
                    "text": msgs[0].get("message", "")[:80] if msgs else "",
                    "time": thread.get("updated_time", "")[:16],
                })
                continue

            # Check if page replied (sender is page)
            page_replied = any(
                str(m.get("from", {}).get("id", "")) == str(FACEBOOK_PAGE_ID)
                for m in msgs
            )
            if page_replied:
                result["replied_threads"] += 1
                # Calculate response time
                first_msg_time = dateparser.parse(msgs[-1]["created_time"])
                page_reply = next(
                    (m for m in reversed(msgs)
                     if str(m.get("from", {}).get("id", "")) == str(FACEBOOK_PAGE_ID)),
                    None,
                )
                if page_reply:
                    reply_time = dateparser.parse(page_reply["created_time"])
                    delta_minutes = (reply_time - first_msg_time).total_seconds() / 60
                    if delta_minutes >= 0:
                        result["response_times_minutes"].append(delta_minutes)
            else:
                result["recent_unanswered"].append({
                    "text": msgs[0].get("message", "")[:80] if msgs else "",
                    "time": thread.get("updated_time", "")[:16],
                })

    except Exception:
        pass

    return result


# ─── Instagram — Profile & Insights ──────────────────────────────────────────
def fetch_ig_profile(days: int, start: str = None, end: str = None) -> dict:
    """
    Returns Instagram follower count and daily profile insights.
    """
    since, until = _date_range(days, start, end)
    result = {
        "followers_count": None,
        "reach": [],
        "impressions": [],
        "profile_views": [],
        "follower_series": [],
        "follower_additions": [],
    }

    # Followers count (current snapshot)
    try:
        data = _get(INSTAGRAM_USER_ID, {
            "fields": "followers_count,media_count,username",
        })
        result["followers_count"] = data.get("followers_count")
        result["username"] = data.get("username", "footland")
    except Exception:
        pass

    # Daily insights
    metric_map = {
        "reach": "reach",
        "profile_views": "profile_views",
    }
    for metric, key in metric_map.items():
        try:
            data = _get(f"{INSTAGRAM_USER_ID}/insights", {
                "metric": metric,
                "period": "day",
                "since": since,
                "until": until,
            })
            values = data.get("data", [{}])[0].get("values", [])
            result[key] = [
                {"date": v["end_time"][:10], "value": v["value"]}
                for v in values
            ]
        except Exception:
            pass

    # follower_count daily = daily additions (not cumulative)
    try:
        data = _get(f"{INSTAGRAM_USER_ID}/insights", {
            "metric": "follower_count",
            "period": "day",
            "since": since,
            "until": until,
        })
        values = data.get("data", [{}])[0].get("values", [])
        result["follower_additions"] = [
            {"date": v["end_time"][:10], "value": v["value"]}
            for v in values
        ]
        result["follower_series"] = result["follower_additions"]
    except Exception:
        pass

    return result


# ─── Instagram — Engagement ───────────────────────────────────────────────────
def fetch_ig_engagement(days: int, start: str = None, end: str = None) -> dict:
    """
    Returns aggregated Instagram engagement metrics from recent media.
    """
    since, until = _date_range(days, start, end)
    result = {"likes": 0, "comments": 0, "shares": 0, "saves": 0, "daily": []}

    # Try account-level daily engagement
    for metric in ["likes", "comments", "shares", "saves"]:
        try:
            data = _get(f"{INSTAGRAM_USER_ID}/insights", {
                "metric": metric,
                "period": "day",
                "since": since,
                "until": until,
            })
            values = data.get("data", [{}])[0].get("values", [])
            series = [
                {"date": v["end_time"][:10], "metric": metric, "value": v["value"]}
                for v in values
            ]
            result["daily"].extend(series)
            result[metric] = sum(v["value"] for v in values)
        except Exception:
            pass

    return result


# ─── Instagram — Media / Top Posts ───────────────────────────────────────────
def fetch_ig_posts(days: int = None, start: str = None, end: str = None, limit: int = 100) -> list[dict]:
    """
    Returns Instagram media within the selected date range.
    """
    params = {"fields": IG_MEDIA_FIELDS, "limit": limit}
    if days or (start and end):
        since, until = _date_range(days or 30, start, end)
        params["since"] = since
        params["until"] = until

    try:
        data = _get(f"{INSTAGRAM_USER_ID}/media", params)
        posts = data.get("data", [])
        parsed = []
        for p in posts:
            # Fetch per-media insights separately
            impressions, reach = 0, 0
            try:
                ins = _get(f"{p['id']}/insights", {
                    "metric": "impressions,reach,saved",
                })
                for item in ins.get("data", []):
                    n = item["name"]
                    v = item["values"][0]["value"] if item.get("values") else 0
                    if n == "impressions":
                        impressions = v
                    elif n == "reach":
                        reach = v
            except Exception:
                pass

            likes    = p.get("like_count", 0)
            comments = p.get("comments_count", 0)
            saves    = 0
            try:
                ins2 = _get(f"{p['id']}/insights", {"metric": "saved"})
                for item in ins2.get("data", []):
                    if item["name"] == "saved":
                        saves = item["values"][0]["value"] if item.get("values") else 0
            except Exception:
                pass
            parsed.append({
                "id": p.get("id", ""),
                "text": p.get("caption", "")[:120] if p.get("caption") else "",
                "created_time": p.get("timestamp", "")[:10],
                "media_type": p.get("media_type", ""),
                "thumbnail": p.get("thumbnail_url") or p.get("media_url", ""),
                "reach": reach,
                "impressions": impressions,
                "reactions": likes,
                "comments": comments,
                "saves": saves,
                "shares": 0,
                "total_interactions": likes + comments + saves,
            })
        return parsed
    except Exception:
        return []


# ─── API Health Check ─────────────────────────────────────────────────────────
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
