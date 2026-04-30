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
        "period_impressions": 0,
        "story_impressions": 0,
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

    # 3. Deduplicated Period Reach — try multiple approaches to get the closest
    # value to what Meta Business Suite reports.

    # Attempt A: metric_type=total_value (newer IG API — returns full-period aggregate)
    try:
        data_p = _get(f"{INSTAGRAM_USER_ID}/insights", {
            "metric": "reach",
            "period": "day",
            "metric_type": "total_value",
            "since": since_ts,
            "until": until_ts,
        })
        for m in data_p.get("data", []):
            if m["name"] == "reach":
                tv = m.get("total_value", {})
                if isinstance(tv, dict):
                    val = tv.get("value", 0)
                elif isinstance(tv, (int, float)):
                    val = int(tv)
                else:
                    val = 0
                if val:
                    result["period_reach"] = val
                    print(f"DEBUG IG reach total_value = {val}")
    except Exception as e:
        print(f"DEBUG: IG reach total_value error: {e}")

    # Attempt B: period=month
    if not result["period_reach"]:
        try:
            data_p = _get(f"{INSTAGRAM_USER_ID}/insights", {
                "metric": "reach",
                "period": "month",
                "since": since_ts,
                "until": until_ts,
            })
            for m in data_p.get("data", []):
                if m["name"] == "reach":
                    vals = m.get("values", [])
                    if vals:
                        result["period_reach"] = vals[-1]["value"]
        except Exception:
            pass

    # Attempt C: days_28 / week fallback
    if not result["period_reach"]:
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
                        result["period_reach"] = vals[-1]["value"]
        except Exception:
            pass

    # 4. Daily Follower Series — try multiple metric names across API versions
    for m_name in ["follower_count", "profile_follows", "total_followers_count"]:
        try:
            data = _get(f"{INSTAGRAM_USER_ID}/insights", {
                "metric": m_name,
                "period": "day",
                "since": since_ts,
                "until": until_ts,
            })
            for m in data.get("data", []):
                if m["name"] == m_name:
                    vals = m.get("values", [])
                    if vals:
                        result["follower_additions"] = [
                            {"date": v["end_time"][:10], "value": v["value"]}
                            for v in vals
                        ]
                        print(f"DEBUG IG follower series via '{m_name}': {len(vals)} points")
            if result["follower_additions"]:
                break
        except Exception as e:
            print(f"DEBUG: IG {m_name} error: {e}")

    # Fallback: try metric_type=total_value for follower_count
    if not result["follower_additions"]:
        try:
            data = _get(f"{INSTAGRAM_USER_ID}/insights", {
                "metric": "follower_count",
                "period": "day",
                "metric_type": "total_value",
                "since": since_ts,
                "until": until_ts,
            })
            for m in data.get("data", []):
                if m["name"] == "follower_count":
                    vals = m.get("values", [])
                    if vals:
                        result["follower_additions"] = [
                            {"date": v["end_time"][:10], "value": v["value"]}
                            for v in vals
                        ]
                        print(f"DEBUG IG follower_count total_value: {len(vals)} points")
        except Exception as e:
            print(f"DEBUG: IG follower_count total_value error: {e}")

    # 5. Total Impressions (metric_type=total_value — includes Feed + Reels aggregate)
    try:
        data_imp = _get(f"{INSTAGRAM_USER_ID}/insights", {
            "metric": "impressions",
            "period": "day",
            "metric_type": "total_value",
            "since": since_ts,
            "until": until_ts,
        })
        for m in data_imp.get("data", []):
            if m["name"] == "impressions":
                tv = m.get("total_value", {})
                if isinstance(tv, dict):
                    val = tv.get("value", 0)
                elif isinstance(tv, (int, float)):
                    val = int(tv)
                else:
                    val = 0
                if val:
                    result["period_impressions"] = val
                    print(f"DEBUG IG impressions total_value = {val}")
    except Exception as e:
        print(f"DEBUG: IG impressions total_value error: {e}")

    # 6. Stories Impressions — Stories are NOT included in the account-level
    #    impressions metric. Fetch active stories and sum their view counts.
    try:
        stories_data = _get(f"{INSTAGRAM_USER_ID}/stories", {
            "fields": "id,insights.metric(impressions,reach)",
            "limit": 100,
        })
        story_imp_total = 0
        for story in stories_data.get("data", []):
            ins_list = story.get("insights", {}).get("data", [])
            for item in ins_list:
                if item["name"] == "impressions":
                    val = item.get("values", [{}])[0].get("value", 0) if item.get("values") else 0
                    story_imp_total += val
        if story_imp_total:
            result["story_impressions"] = story_imp_total
            print(f"DEBUG IG story impressions = {story_imp_total}")
    except Exception as e:
        print(f"DEBUG: IG stories impressions error: {e}")

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
def fetch_ig_posts(days: int = None, start: str = None, end: str = None, limit: int = 20) -> list[dict]:
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
            impressions, reach, saves, shares = 0, 0, 0, 0
            try:
                # This syntax is robust: it only returns what the post supports
                m_list = "total_likes,total_comments,total_views,reach,saved,shares,plays,views,impressions"
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
                    elif name == "shares":
                        shares = val
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
                "shares":           shares,
                "total_interactions": likes + comments + saves + shares,
            }

        # Parallelize the insight fetching (Restored for speed)
        with ThreadPoolExecutor(max_workers=20) as executor:
            parsed = list(executor.map(_process_ig_post, posts))

        return parsed
    except Exception as e:
        print(f"DEBUG: IG posts error: {e}")
        return []


# ─── Instagram — Conversations (Community Management) ─────────────────────────
def fetch_ig_conversations(days: int = 30, start: str = None, end: str = None, limit: int = 25) -> dict:
    """
    Returns Instagram DM thread metadata for community management stats.
    Uses the same /conversations endpoint as Facebook with platform=instagram.
    Requires instagram_manage_messages permission on the connected page.
    """
    from config import FACEBOOK_PAGE_ID

    since, until = _date_range(days, start, end)

    result = {
        "total_threads": 0,
        "new_threads": 0,
        "replied_threads": 0,
        "response_times_minutes": [],
        "recent_unanswered": [],
    }

    try:
        data = _get(f"{FACEBOOK_PAGE_ID}/conversations", {
            "platform": "instagram",
            "fields": "id,updated_time,messages{created_time,from,message}",
            "limit": limit,
        })
        threads = data.get("data", [])
        result["total_threads"] = len(threads)

        for thread in threads:
            msgs = thread.get("messages", {}).get("data", [])

            # Count threads whose first message falls within the date range
            if msgs:
                first_msg_date = msgs[-1].get("created_time", "")[:10]
                if since <= first_msg_date <= until:
                    result["new_threads"] += 1

            if len(msgs) < 2:
                result["recent_unanswered"].append({
                    "text": msgs[0].get("message", "")[:80] if msgs else "",
                    "time": thread.get("updated_time", "")[:16],
                })
                continue

            # Check if page replied (sender id matches page)
            page_replied = any(
                str(m.get("from", {}).get("id", "")) == str(FACEBOOK_PAGE_ID)
                for m in msgs
            )
            if page_replied:
                result["replied_threads"] += 1
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

    except Exception as e:
        print(f"DEBUG: IG conversations error: {e}")

    return result
