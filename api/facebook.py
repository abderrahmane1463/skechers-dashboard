"""
api/facebook.py — Facebook Graph API fetch functions (organic only).
"""

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
        "period_content_interactions": 0,
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
        result["period_content_interactions"] = sum(v["value"] for v in values)
        print(f"DEBUG: period_content_interactions = {result['period_content_interactions']}")
    except Exception as e:
        print(f"DEBUG: page_post_engagements error: {e}")

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
    # page_impressions_unique + page_views_total — both confirmed working.
    # page_impressions_unique is used for the daily Reach chart only;
    # the KPI (period_reach) uses a separate period=month call below.
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

    # 1c. page_posts_impressions daily series.
    # Diagnostic confirmed: page_impressions is blocked for this page type (#100 error).
    # page_posts_impressions returns 35,030,491 which matches the report exactly.
    try:
        pv_data = _get(f"{FACEBOOK_PAGE_ID}/insights", {
            "metric": "page_posts_impressions",
            "period": "day",
            "since": since,
            "until": until,
        })
        for m in pv_data.get("data", []):
            if m["name"] == "page_posts_impressions":
                series = [
                    {"date": v["end_time"][:10], "value": v["value"]}
                    for v in m.get("values", [])
                ]
                result["page_impressions_daily"] = series
                result["impressions"] = series
        print(f"DEBUG: impressions daily rows={len(result['impressions'])}")
    except Exception as e:
        print(f"DEBUG: page_posts_impressions daily error: {e}")

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

    # period_impressions — sum the already-fetched daily series.
    # Responds to any date range change. Slightly lower than period=month
    # aggregate (~1-2%) due to Meta's internal aggregation difference.
    result["period_impressions"] = sum(v["value"] for v in result.get("impressions", []))
    print(f"DEBUG: period_impressions (daily sum) = {result['period_impressions']}")

    # period_reach — deduplicated monthly unique reach via period=month.
    # Always shows the full calendar month value (deduplicated across all days).
    import calendar as _cal
    _since_dt  = datetime.strptime(since, "%Y-%m-%d").date()
    _, _last_d = _cal.monthrange(_since_dt.year, _since_dt.month)
    _month_since = f"{_since_dt.year}-{_since_dt.month:02d}-01"
    _month_until = f"{_since_dt.year}-{_since_dt.month:02d}-{_last_d:02d}"
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
                    result["period_reach"] = max(v["value"] for v in vals)
        print(f"DEBUG: period_reach (month) = {result['period_reach']}")
    except Exception as e:
        print(f"DEBUG: period_reach month error: {e}")

    if not result["period_reach"]:
        result["period_reach"] = sum(v["value"] for v in result.get("reach", []))
        print(f"DEBUG: period_reach (fallback daily sum) = {result['period_reach']}")

    return result


# ─── Facebook — Demographics (Marketing API) ─────────────────────────────────
def fetch_fb_demographics(days: int = 30, start: str = None, end: str = None) -> dict:
    """
    Returns reach demographics from the Marketing API broken down by:
      - age + gender  → age/gender bar chart
      - country       → top countries table
      - region        → top cities/regions table

    Filters to Footland campaigns only via FOOTLAND_CAMPAIGN_KEYWORDS.
    page_fans_gender_age is blocked for New Page Experience pages; this
    uses paid reach demographics as a proxy (matches the report which is
    also driven primarily by paid campaigns).

    Returns {
        "age_brackets": [...],
        "men":   [pct, ...],
        "women": [pct, ...],
        "total_men_pct":   float,
        "total_women_pct": float,
        "top_countries": [{"name": str, "reach": int, "pct": float}, ...],
        "top_cities":    [{"name": str, "reach": int, "pct": float}, ...],
        "source": "marketing_api",
    }
    """
    import requests as _requests
    from api.boost import _get_ads
    from config import BLOCKED_AD_ACCOUNTS, FOOTLAND_CAMPAIGN_KEYWORDS, GRAPH_BASE_URL

    AD_ACCOUNT = BLOCKED_AD_ACCOUNTS[0]
    since, until = _date_range(days, start, end)
    time_range = f'{{"since":"{since}","until":"{until}"}}'

    age_order = ["18-24", "25-34", "35-44", "45-54", "55-64", "65+"]
    result = {
        "age_brackets": age_order,
        "men":   [0.0] * len(age_order),
        "women": [0.0] * len(age_order),
        "total_men_pct":   0.0,
        "total_women_pct": 0.0,
        "top_countries": [],
        "top_cities":    [],
        "source": "marketing_api",
    }

    def _is_footland(name: str) -> bool:
        n = (name or "").lower()
        return any(kw.lower() in n for kw in FOOTLAND_CAMPAIGN_KEYWORDS)

    def _fetch_breakdown(breakdown: str) -> list:
        """Fetch campaign-level insights for a breakdown, return Footland rows only."""
        rows = []
        params = {
            "level": "campaign",
            "fields": "campaign_name,reach",
            "breakdowns": breakdown,
            "time_range": time_range,
            "limit": 500,
        }
        try:
            page = _get_ads(f"{AD_ACCOUNT}/insights", params)
            while True:
                for row in page.get("data", []):
                    if _is_footland(row.get("campaign_name", "")):
                        rows.append(row)
                next_url = page.get("paging", {}).get("next")
                if not next_url:
                    break
                try:
                    page = _requests.get(next_url, timeout=30).json()
                except Exception:
                    break
        except Exception as e:
            print(f"DEBUG demographics [{breakdown}] fetch error: {e}")
        return rows

    # ── Age + Gender ──────────────────────────────────────────────────────────
    try:
        ag_rows = _fetch_breakdown("age,gender")
        totals = {b: {"male": 0, "female": 0} for b in age_order}
        for row in ag_rows:
            age    = row.get("age", "")
            gender = row.get("gender", "")
            reach  = int(row.get("reach", 0) or 0)
            if age in totals and gender in ("male", "female"):
                totals[age][gender] += reach
        grand = sum(v["male"] + v["female"] for v in totals.values())
        if grand > 0:
            result["men"]   = [round(totals[b]["male"]   / grand * 100, 1) for b in age_order]
            result["women"] = [round(totals[b]["female"] / grand * 100, 1) for b in age_order]
            result["total_men_pct"]   = round(sum(totals[b]["male"]   for b in age_order) / grand * 100, 1)
            result["total_women_pct"] = round(sum(totals[b]["female"] for b in age_order) / grand * 100, 1)
        print(f"DEBUG demographics age/gender: {len(ag_rows)} rows, grand={grand}")
    except Exception as e:
        print(f"DEBUG demographics age/gender error: {e}")

    # ── Countries ─────────────────────────────────────────────────────────────
    try:
        c_rows = _fetch_breakdown("country")
        c_totals: dict[str, int] = {}
        for row in c_rows:
            c = row.get("country", "?")
            c_totals[c] = c_totals.get(c, 0) + int(row.get("reach", 0) or 0)
        total_c = sum(c_totals.values()) or 1
        result["top_countries"] = sorted(
            [{"name": k, "reach": v, "pct": round(v / total_c * 100, 1)}
             for k, v in c_totals.items()],
            key=lambda x: x["reach"], reverse=True
        )[:10]
        print(f"DEBUG demographics countries: {len(result['top_countries'])} entries")
    except Exception as e:
        print(f"DEBUG demographics countries error: {e}")

    # ── Cities / Regions ──────────────────────────────────────────────────────
    try:
        r_rows = _fetch_breakdown("region")
        r_totals: dict[str, int] = {}
        for row in r_rows:
            r = row.get("region", "?")
            r_totals[r] = r_totals.get(r, 0) + int(row.get("reach", 0) or 0)
        total_r = sum(r_totals.values()) or 1
        result["top_cities"] = sorted(
            [{"name": k, "reach": v, "pct": round(v / total_r * 100, 1)}
             for k, v in r_totals.items()],
            key=lambda x: x["reach"], reverse=True
        )[:10]
        print(f"DEBUG demographics cities: {len(result['top_cities'])} entries")
    except Exception as e:
        print(f"DEBUG demographics cities error: {e}")

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

            # Use the public snapshot as the canonical reactions count —
            # reactions.summary(true).total_count is exactly what Facebook
            # displays on the post when you open it. post_reactions_by_type_total
            # from Insights can differ (delayed reporting, paid vs organic split).
            reacs = reacs_public

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
