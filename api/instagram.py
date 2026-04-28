"""
api/instagram.py — Instagram Graph API fetch functions (organic only).
"""

from datetime import timedelta
from concurrent.futures import ThreadPoolExecutor

from dateutil import parser as dateparser

from config import INSTAGRAM_USER_ID, IG_MEDIA_FIELDS
from api.base import _get, _date_range


# ─── Instagram — Profile & Insights ──────────────────────────────────────────
def fetch_ig_profile(days: int, start: str = None, end: str = None) -> dict:
    """
    Returns Instagram follower count and daily profile insights,
    applying the same robust 'Retry & Fallback' logic as the Facebook section.
    """
    since, until = _date_range(days, start, end)

    # Use timestamps for better API compatibility (from diagnostic)
    try:
        since_ts = int(dateparser.parse(since).timestamp())
        until_ts = int(dateparser.parse(until).timestamp())
    except:
        since_ts, until_ts = since, until

    result = {
        "followers_count": 0,
        "reach": [],
        "impressions": [],
        "profile_views": [],
        "follower_series": [],
        "follower_additions": [],
        "period_reach": 0,
        "username": "footland"
    }

    # 1. Total Followers (Fallback logic like FB page_fans)
    try:
        data = _get(INSTAGRAM_USER_ID, {"fields": "followers_count,username"})
        result["followers_count"] = data.get("followers_count", 0)
        result["username"] = data.get("username", "footland")
    except Exception as e:
        print(f"DEBUG: IG followers snapshot error: {e}")

    # 2. Daily Visibility and Interaction Metrics
    metrics_to_fetch = {
        "reach": "reach",
        "views": "impressions",           # Account-level total views
        "profile_views": "profile_views",
        "total_interactions": "total_interactions_series", # Account-level total engagement
    }
    for metric, key in metrics_to_fetch.items():
        try:
            params = {
                "metric": metric,
                "period": "day",
                "since": since_ts,
                "until": until_ts,
            }
            # Special params for newer API versions
            if metric == "profile_views":
                params["metric_type"] = "total_value"

            data = _get(f"{INSTAGRAM_USER_ID}/insights", params)
            for m in data.get("data", []):
                if m["name"] == metric:
                    result[key] = [
                        {"date": v["end_time"][:10], "value": v["value"]}
                        for v in m["values"]
                    ]
        except Exception as e:
            print(f"DEBUG: IG {metric} fetch error: {e}")
            # Final fallback: try 'impressions' if 'views' failed
            if metric == "views" and not result["impressions"]:
                try:
                    data = _get(f"{INSTAGRAM_USER_ID}/insights", {
                        "metric": "impressions",
                        "period": "day", "since": since_ts, "until": until_ts
                    })
                    for m in data.get("data", []):
                        result["impressions"] = [{"date": v["end_time"][:10], "value": v["value"]} for v in m["values"]]
                except: pass

    # 3. Deduplicated Period Reach (FB page_impressions_unique logic)
    # Mirroring the 'week'/'days_28' selection logic from FB
    best_period = "days_28" if days > 7 else "week"
    try:
        data_p = _get(f"{INSTAGRAM_USER_ID}/insights", {
            "metric": "reach",
            "period": best_period,
            "since": since_ts,
            "until": until_ts,
        })
        for m in data_p.get("data", []):
            if m["name"] == "reach":
                vals = m.get("values", [])
                if vals:
                    # Like FB, we take the most recent period total
                    result["period_reach"] = vals[-1]["value"]
    except Exception:
        pass

    # 4. New Followers (Retry Pattern like FB fans_adds)
    for m_name in ["follower_count"]:
        try:
            data = _get(f"{INSTAGRAM_USER_ID}/insights", {
                "metric": m_name,
                "period": "day",
                "since": since_ts,
                "until": until_ts,
            })
            for m in data.get("data", []):
                if m["name"] == m_name:
                    result["follower_additions"] = [
                        {"date": v["end_time"][:10], "value": v["value"]}
                        for v in m["values"]
                    ]
            if result["follower_additions"]: break
        except Exception:
            pass

    result["follower_series"] = result["follower_additions"]
    return result


# ─── Instagram — Engagement ───────────────────────────────────────────────────
def fetch_ig_engagement(days: int, start: str = None, end: str = None) -> dict:
    """
    Returns aggregated Instagram engagement metrics, mirroring
    the Facebook interaction breakdown pattern.
    """
    since, until = _date_range(days, start, end)

    try:
        since_ts = int(dateparser.parse(since).timestamp())
        until_ts = int(dateparser.parse(until).timestamp())
    except:
        since_ts, until_ts = since, until

    result = {"likes": 0, "comments": 0, "shares": 0, "saves": 0, "daily": []}

    # Mirroring FB: Try individual insights for the period
    metric_map = {
        "likes": "likes",
        "comments": "comments",
        "shares": "shares",
        "saves": "saves"
    }

    for metric, key in metric_map.items():
        try:
            data = _get(f"{INSTAGRAM_USER_ID}/insights", {
                "metric": metric,
                "period": "day",
                "since": since_ts,
                "until": until_ts,
            })
            for m in data.get("data", []):
                if m["name"] == metric:
                    vals = m.get("values", [])
                    result[key] = sum(v["value"] for v in vals)
                    result["daily"].extend([
                        {"date": v["end_time"][:10], "metric": key, "value": v["value"]}
                        for v in vals
                    ])
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
        # Make end date inclusive for media list
        try:
            params["until"] = str((dateparser.parse(until) + timedelta(days=1)).date())
        except:
            params["until"] = until

    try:
        data = _get(f"{INSTAGRAM_USER_ID}/media", params)
        posts = data.get("data", [])

        def _process_ig_post(p):
            # 1. Start with Public Snapshot (Fallback)
            likes, comments = p.get("like_count", 0), p.get("comments_count", 0)

            # 2. Fetch Deep Insights (Bulletproof Node-Fields Syntax)
            impressions, reach, saves = 0, 0, 0
            try:
                # This syntax is robust: it only returns what the post supports
                m_list = "total_likes,total_comments,total_views,reach,saved,plays,views,impressions"
                data = _get(p["id"], {"fields": f"insights.metric({m_list})"})

                ins_list = data.get("insights", {}).get("data", [])
                for item in ins_list:
                    name = item["name"]
                    val = item["values"][0]["value"] if item.get("values") else 0

                    if name == "total_likes":
                        likes = val
                    elif name == "total_comments":
                        comments = val
                    elif name in ["total_views", "impressions", "views", "plays"]:
                        impressions = max(impressions, val)
                    elif name == "reach":
                        reach = val
                    elif name == "saved":
                        saves = val
            except:
                pass

            return {
                "id":               p.get("id", ""),
                "text":             p.get("caption", "")[:120] if p.get("caption") else "",
                "created_time":     p.get("timestamp", "")[:10],
                "media_type":       p.get("media_type", ""),
                "thumbnail":        p.get("thumbnail_url") or p.get("media_url", ""),
                "permalink":        p.get("permalink", ""),
                "reach":            reach,
                "impressions":      impressions,
                "reactions":        likes,
                "comments":         comments,
                "saves":            saves,
                "total_interactions": likes + comments + saves,
            }

        # Parallelize the insight fetching (Restored for speed)
        with ThreadPoolExecutor(max_workers=10) as executor:
            parsed = list(executor.map(_process_ig_post, posts))

        return parsed
    except Exception as e:
        print(f"DEBUG: IG posts error: {e}")
        return []
