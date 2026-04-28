"""
api/facebook.py — Facebook Graph API fetch functions (organic only).
"""

from datetime import timedelta
from concurrent.futures import ThreadPoolExecutor

from dateutil import parser as dateparser

from config import FACEBOOK_PAGE_ID, FB_POST_FIELDS
from api.base import _get, _date_range, _prev_date_range


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
    Returns daily reach (unique), impressions, and page views,
    plus a deduplicated total reach for the period.
    """
    since, until = _date_range(days, start, end)
    result = {"reach": [], "impressions": [], "page_views": [], "period_reach": 0}

    # 1. Fetch daily metrics (for charts)
    mapping = {
        "page_impressions_unique": "reach",
        "page_posts_impressions": "impressions",
        "page_views_total": "page_views",
    }
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
        print(f"DEBUG: visibility daily insights error: {e}")

    # 2. Fetch deduplicated reach (Period Total)
    # Meta provides 'week' (7 days) or 'days_28' (28 days) deduplicated reach.
    # We choose the best fit based on the requested range.
    best_period = "days_28" if days > 7 else "week"
    try:
        data_p = _get(f"{FACEBOOK_PAGE_ID}/insights", {
            "metric": "page_impressions_unique",
            "period": best_period,
            "since": since,
            "until": until,
        })
        # The latest value in the range represents the deduplicated reach for that window
        for m in data_p.get("data", []):
            if m["name"] == "page_impressions_unique":
                vals = m.get("values", [])
                if vals:
                    result["period_reach"] = vals[-1]["value"]
    except Exception as e:
        print(f"DEBUG: visibility period reach error: {e}")

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
        # Make end date inclusive for post list
        try:
            params["until"] = str((dateparser.parse(until) + timedelta(days=1)).date())
        except:
            params["until"] = until

    try:
        data = _get(f"{FACEBOOK_PAGE_ID}/posts", params)
        posts = data.get("data", [])

        # ── Confirmed-valid metrics for New Page Experience pages ────────────
        #
        # Diagnosed via live API probe: this page type only supports the _unique
        # (reach) variants of impression metrics. The aggregate counterparts
        # (post_impressions, post_impressions_organic, …) return
        # "(#100) The value must be a valid insights metric" and, critically,
        # ONE bad metric in a batch silently kills all others in the same call.
        #
        # Rule: request ONLY metrics confirmed to work, one batch per call.
        # If Meta ever re-enables the aggregate metrics, they appear in the
        # response automatically (metrics dict is keyed by name).
        _REACH_METRICS = (                        # all return integers
            "post_impressions_unique,"            # total reach (canonical)
            "post_impressions_organic_unique,"    # organic reach
            "post_impressions_paid_unique,"       # paid reach
            "post_impressions_viral_unique,"      # viral reach (via shares)
            "post_impressions_nonviral_unique,"   # non-viral reach
            "post_clicks,"                        # total link clicks
            "post_video_views,"                   # video views ≥3 s
            "post_video_views_unique"             # unique video viewers
        )
        _DICT_METRIC = "post_reactions_by_type_total"   # separate call (dict value)

        def _process_fb_post(p):
            # ── 0. Public snapshot (always available — no extra API call) ─────
            reacs = p.get("reactions", {}).get("summary", {}).get("total_count", 0)
            comm  = p.get("comments",  {}).get("summary", {}).get("total_count", 0)
            shar  = p.get("shares",    {}).get("count", 0)

            metrics = {}

            def _parse_items(items):
                for item in items:
                    raw = item.get("values", [{}])[0].get("value", 0) if item.get("values") else 0
                    metrics[item["name"]] = raw

            # ── 1. Reach metrics (confirmed-valid batch) ──────────────────────
            try:
                ins = _get(f"{p['id']}/insights", {"metric": _REACH_METRICS})
                _parse_items(ins.get("data", []))
            except Exception as e:
                print(f"DEBUG post {p.get('id')} reach metrics error: {e}")

            # ── 2. Reactions breakdown (dict metric — isolated call) ───────────
            try:
                ins2 = _get(f"{p['id']}/insights", {"metric": _DICT_METRIC})
                _parse_items(ins2.get("data", []))
            except Exception as e:
                print(f"DEBUG post {p.get('id')} reactions error: {e}")

            # ── 3. Normalization ───────────────────────────────────────────────
            # For New Page Experience pages only _unique variants are returned.
            # "reach" = post_impressions_unique (total unique accounts that saw post)
            # "total_views" = same (no non-unique aggregate available)
            # organic / paid / viral are also unique-reach breakdowns.
            reach        = metrics.get("post_impressions_unique", 0)
            org_imp      = metrics.get("post_impressions_organic_unique", 0)
            impressions_paid = metrics.get("post_impressions_paid_unique", 0)
            viral_imp    = metrics.get("post_impressions_viral_unique", 0)
            video_views  = metrics.get("post_video_views", 0)

            # total_views: use reach (only total available); for video posts
            # prefer video_views when it is higher (Reels counted differently).
            total_views  = max(reach, video_views)

            # impressions: same as total_views on this page type
            impressions  = total_views

            # ── 4. Remaining metrics ──────────────────────────────────────────
            clicks           = metrics.get("post_clicks", 0)
            clicks_unique    = 0   # not valid for this page type
            negative         = 0   # not valid for this page type
            video_views_uniq = metrics.get("post_video_views_unique", 0)
            video_complete   = 0   # not valid for this page type
            video_avg_watch  = 0   # not valid for this page type

            reactions_by_type = metrics.get("post_reactions_by_type_total", {})
            if not isinstance(reactions_by_type, dict):
                reactions_by_type = {}

            return {
                "id":                   p.get("id", ""),
                "text":                 p.get("message", p.get("story", ""))[:120],
                "created_time":         p.get("created_time", "")[:10],
                "thumbnail":            p.get("full_picture", ""),
                # Reach / impressions (normalized)
                "reach":                reach,
                "total_views":          total_views,
                "impressions":          impressions,
                "impressions_organic":  org_imp,
                "impressions_paid":     impressions_paid,
                "impressions_viral":    viral_imp,
                # Engagement
                "reactions":            reacs,
                "reactions_by_type":    reactions_by_type,
                "comments":             comm,
                "shares":               shar,
                "clicks":               clicks,
                "clicks_unique":        clicks_unique,
                "engaged_users":        0,   # not valid for this page type
                "negative_feedback":    negative,
                # Video
                "video_views":          video_views,
                "video_views_unique":   video_views_uniq,
                "video_complete_views": video_complete,
                "video_avg_watch_sec":  round(video_avg_watch, 1) if video_avg_watch else 0,
                # Computed
                "total_interactions":   reacs + comm + shar,
            }

        # Parallelize
        with ThreadPoolExecutor(max_workers=10) as executor:
            parsed = list(executor.map(_process_fb_post, posts))

        return parsed
    except Exception as e:
        print(f"DEBUG: FB posts error: {e}")
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
