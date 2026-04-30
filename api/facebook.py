"""
api/facebook.py — Facebook Graph API fetch functions (organic only).
"""

import calendar
from datetime import timedelta, datetime
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
    Returns daily post engagements, reaction breakdowns, and
    follower vs non-follower daily impression series.
    """
    since, until = _date_range(days, start, end)
    result = {
        "engagements": [], "reactions": [],
        "fan_daily": [],        # daily impressions to followers
        "nonfan_daily": [],     # daily impressions to non-followers
        "prev_fan_total": 0,
        "prev_nonfan_total": 0,
    }

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

    # Follower vs Non-follower daily breakdown
    # page_impressions_fan  = content seen by people who follow the page
    # page_impressions_nonviral = content seen by non-followers via direct page posts
    try:
        fan_data = _get(f"{FACEBOOK_PAGE_ID}/insights", {
            "metric": "page_impressions_fan,page_impressions_nonviral",
            "period": "day",
            "since": since,
            "until": until,
        })
        for m in fan_data.get("data", []):
            series = [
                {"date": v["end_time"][:10], "value": v["value"]}
                for v in m.get("values", [])
            ]
            if m["name"] == "page_impressions_fan":
                result["fan_daily"] = series
            elif m["name"] == "page_impressions_nonviral":
                result["nonfan_daily"] = series
    except Exception as e:
        print(f"DEBUG: fan/nonfan engagement error: {e}")

    # Previous-period totals for % change indicators
    try:
        prev_since, prev_until = _prev_date_range(days)
        prev_data = _get(f"{FACEBOOK_PAGE_ID}/insights", {
            "metric": "page_impressions_fan,page_impressions_nonviral",
            "period": "day",
            "since": prev_since,
            "until": prev_until,
        })
        for m in prev_data.get("data", []):
            vals = m.get("values", [])
            total = sum(v["value"] for v in vals if isinstance(v.get("value"), (int, float)))
            if m["name"] == "page_impressions_fan":
                result["prev_fan_total"] = total
            elif m["name"] == "page_impressions_nonviral":
                result["prev_nonfan_total"] = total
    except Exception as e:
        print(f"DEBUG: prev fan/nonfan error: {e}")

    return result


# ─── Facebook — Visibility / Reach ────────────────────────────────────────────
def fetch_fb_visibility(days: int, start: str = None, end: str = None) -> dict:
    """
    Returns daily reach (unique), impressions, and page views,
    plus a deduplicated total reach for the period.
    """
    since, until = _date_range(days, start, end)
    result = {
        "reach": [], "impressions": [], "page_views": [],
        "page_impressions_daily": [],          # total impressions (all sources) daily series
        "page_views_organic": [],              # organic impressions daily series
        "page_views_paid": [],                 # paid impressions daily series
        "period_reach": 0, "period_impressions": 0,
        "prev_total_views": 0, "prev_organic_views": 0, "prev_paid_views": 0,
    }

    # 1. Fetch daily metrics (for charts)
    # page_impressions_unique + page_views_total batch well together.
    # page_impressions is fetched separately in section 1c (with organic/paid breakdown)
    # to avoid batch-contamination, then aliased to result["impressions"] below.
    mapping = {
        "page_impressions_unique": "reach",
        "page_views_total":        "page_views",
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

    # 1c. page_impressions daily series — try page_impressions (all placements),
    #     fall back to page_posts_impressions if the API rejects it.
    for _imp_metric in ("page_impressions", "page_posts_impressions"):
        try:
            pv_data = _get(f"{FACEBOOK_PAGE_ID}/insights", {
                "metric": _imp_metric,
                "period": "day",
                "since": since,
                "until": until,
            })
            _raw_names = [m.get("name") for m in pv_data.get("data", [])]
            print(f"DEBUG: {_imp_metric} response names={_raw_names} data_len={len(pv_data.get('data', []))}")
            for m in pv_data.get("data", []):
                if m["name"] == _imp_metric:
                    series = [
                        {"date": v["end_time"][:10], "value": v["value"]}
                        for v in m.get("values", [])
                    ]
                    result["page_impressions_daily"] = series
                    result["impressions"] = series
            if result["impressions"]:
                print(f"DEBUG: impressions daily set via {_imp_metric}, rows={len(result['impressions'])}")
                break   # got data — no need for fallback
            else:
                print(f"DEBUG: {_imp_metric} returned empty series, trying fallback")
        except Exception as e:
            print(f"DEBUG: {_imp_metric} daily error: {e}")

    # 1c-b. Organic + Paid breakdown — optional, needs ads_read permission.
    #       Failure here must NOT affect the main impressions series.
    try:
        op_data = _get(f"{FACEBOOK_PAGE_ID}/insights", {
            "metric": "page_impressions_organic,page_impressions_paid",
            "period": "day",
            "since": since,
            "until": until,
        })
        for m in op_data.get("data", []):
            series = [
                {"date": v["end_time"][:10], "value": v["value"]}
                for v in m.get("values", [])
            ]
            if m["name"] == "page_impressions_organic":
                result["page_views_organic"] = series
            elif m["name"] == "page_impressions_paid":
                result["page_views_paid"] = series
    except Exception as e:
        print(f"DEBUG: organic/paid impressions breakdown error: {e}")

    # 1d. Previous-period totals for growth indicators (period-over-period %)
    try:
        prev_since, prev_until = _prev_date_range(days)
        prev_data = _get(f"{FACEBOOK_PAGE_ID}/insights", {
            "metric": "page_impressions,page_impressions_organic,page_impressions_paid",
            "period": "day",
            "since": prev_since,
            "until": prev_until,
        })
        for m in prev_data.get("data", []):
            vals = m.get("values", [])
            total_val = sum(v["value"] for v in vals if isinstance(v.get("value"), (int, float)))
            if m["name"] == "page_impressions":
                result["prev_total_views"] = total_val
            elif m["name"] == "page_impressions_organic":
                result["prev_organic_views"] = total_val
            elif m["name"] == "page_impressions_paid":
                result["prev_paid_views"] = total_val
    except Exception as e:
        print(f"DEBUG: prev period impressions error: {e}")

    # Calendar month boundaries used by both 1b and section 2 below.
    # We align to the calendar month that contains the START of the selected period
    # so that the KPI values match what Meta Business Suite / PDF reports show.
    _since_dt  = datetime.strptime(since, "%Y-%m-%d").date()
    _, _last_d = calendar.monthrange(_since_dt.year, _since_dt.month)
    _month_since = f"{_since_dt.year}-{_since_dt.month:02d}-01"
    _month_until = f"{_since_dt.year}-{_since_dt.month:02d}-{_last_d:02d}"

    # 1b. Monthly-level impressions total (page_impressions all sources, period=month)
    # Aligned to the same calendar month as the period_reach call (month of period start).
    # This matches how Meta Business Suite / PDF reports display impressions.
    try:
        data_mi = _get(f"{FACEBOOK_PAGE_ID}/insights", {
            "metric": "page_impressions",
            "period": "month",
            "since": _month_since,
            "until": _month_until,
        })
        _mi_names = [m.get("name") for m in data_mi.get("data", [])]
        print(f"DEBUG: period_impressions response names={_mi_names} since={_month_since} until={_month_until}")
        for m in data_mi.get("data", []):
            if m["name"] == "page_impressions":
                vals = m.get("values", [])
                print(f"DEBUG: period_impressions raw values = {vals}")
                if vals:
                    result["period_impressions"] = max(v["value"] for v in vals)
        print(f"DEBUG: period_impressions = {result['period_impressions']}")
    except Exception as e:
        print(f"DEBUG: visibility monthly impressions error: {e}")

    # 2. Fetch deduplicated reach (Period Total) — monthly aggregate
    # page_impressions_unique with period=month gives true deduplicated reach.
    # Uses the same calendar-month boundaries computed above for impressions.
    try:
        data_p = _get(f"{FACEBOOK_PAGE_ID}/insights", {
            "metric": "page_impressions_unique",
            "period": "month",
            "since": _month_since,
            "until": _month_until,
        })

        for m in data_p.get("data", []):
            if m["name"] == "page_impressions_unique":
                vals = m.get("values", [])
                if vals:
                    # Take the highest bucket — the most complete calendar month
                    result["period_reach"] = max(v["value"] for v in vals)

        print(f"DEBUG: period_reach = {result['period_reach']} (month: {_month_since} → {_month_until})")
    except Exception as e:
        print(f"DEBUG: visibility period reach (month) error: {e}")

    # Fallback: days_28 then week
    if not result["period_reach"]:
        best_period = "days_28" if days > 7 else "week"
        try:
            data_p = _get(f"{FACEBOOK_PAGE_ID}/insights", {
                "metric": "page_impressions_unique",
                "period": best_period,
                "since": since,
                "until": until,
            })
            for m in data_p.get("data", []):
                if m["name"] == "page_impressions_unique":
                    vals = m.get("values", [])
                    if vals:
                        result["period_reach"] = vals[-1]["value"]
        except Exception as e:
            print(f"DEBUG: visibility period reach ({best_period}) error: {e}")

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
        _DICT_METRIC = "post_reactions_by_type_total,post_activity_by_action_type"  # dict-value metrics

        def _process_fb_post(p):
            # ── 0. Public snapshot (always available — no extra API call) ─────
            reacs_public = p.get("reactions", {}).get("summary", {}).get("total_count", 0)
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

            # Use the sum of the breakdown as the canonical reactions count —
            # post_reactions_by_type_total includes paid/boosted reactions and
            # matches what Facebook shows publicly on the post.
            # Fall back to the public snapshot if insights returned nothing.
            reacs = sum(reactions_by_type.values()) if reactions_by_type else reacs_public

            # post_activity_by_action_type gives a more complete share count
            # (includes reposts, Reels shares, etc.) vs the public shares.count.
            activity = metrics.get("post_activity_by_action_type", {})
            if isinstance(activity, dict) and activity.get("share", 0) > shar:
                shar = activity.get("share", 0)

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
def fetch_fb_conversations(limit: int = 25, days: int = 30, start: str = None, end: str = None) -> dict:
    """
    Returns message thread metadata for community management stats.
    """
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
            "fields": "id,updated_time,messages{created_time,from,message}",
            "limit": limit,
        })
        threads = data.get("data", [])
        result["total_threads"] = len(threads)

        for thread in threads:
            msgs = thread.get("messages", {}).get("data", [])

            # Count threads whose first message falls within the selected period
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
