"""
api/facebook.py — Facebook Graph API fetch functions (organic only).
"""

from datetime import timedelta, datetime
from concurrent.futures import ThreadPoolExecutor

from dateutil import parser as dateparser

from config import FACEBOOK_PAGE_ID, FB_POST_FIELDS
from api.base import _get, _get_insights_chunked, _date_range, _prev_date_range


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

    # Adds — chunked to support date ranges > 92 days (This Year, Last Year, etc.)
    for m_name in ["page_daily_follows", "page_fan_adds"]:
        try:
            data = _get_insights_chunked(
                f"{FACEBOOK_PAGE_ID}/insights",
                {"metric": m_name, "period": "day"},
                since, until,
            )
            for m in data.get("data", []):
                result["fans_adds"].extend([
                    {"date": v["end_time"][:10], "value": v["value"]}
                    for v in m.get("values", [])
                ])
            if result["fans_adds"]: break
        except Exception:
            pass

    # Removes — chunked
    for m_name in ["page_daily_unfollows", "page_fan_removes"]:
        try:
            data = _get_insights_chunked(
                f"{FACEBOOK_PAGE_ID}/insights",
                {"metric": m_name, "period": "day"},
                since, until,
            )
            for m in data.get("data", []):
                result["fans_removes"].extend([
                    {"date": v["end_time"][:10], "value": v["value"]}
                    for v in m.get("values", [])
                ])
            if result["fans_removes"]: break
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
        data = _get_insights_chunked(
            f"{FACEBOOK_PAGE_ID}/insights",
            {"metric": "page_post_engagements", "period": "day"},
            since, until,
        )
        values = []
        for m in data.get("data", []):
            if m.get("name") == "page_post_engagements":
                values = m.get("values", [])
                break
        result["engagements"] = [
            {"date": v["end_time"][:10], "value": v["value"]}
            for v in values
        ]
        result["period_content_interactions"] = sum(v["value"] for v in values)
        print(f"DEBUG: period_content_interactions = {result['period_content_interactions']}")
    except Exception as e:
        print(f"DEBUG: page_post_engagements error: {e}")

    try:
        data = _get_insights_chunked(
            f"{FACEBOOK_PAGE_ID}/insights",
            {"metric": "page_actions_post_reactions_total", "period": "day"},
            since, until,
        )
        values = []
        for m in data.get("data", []):
            if m.get("name") == "page_actions_post_reactions_total":
                values = m.get("values", [])
                break
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
        fan_data = _get_insights_chunked(
            f"{FACEBOOK_PAGE_ID}/insights",
            {"metric": "page_impressions_fan,page_impressions_nonviral", "period": "day"},
            since, until,
        )
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
        # None = exact value; "7j" / "28j" = rolling window used (shown in UI)
        "reach_window_label": None,
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
        data = _get_insights_chunked(
            f"{FACEBOOK_PAGE_ID}/insights",
            {"metric": metrics_str, "period": "day"},
            since, until,
        )
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
        pv_data = _get_insights_chunked(
            f"{FACEBOOK_PAGE_ID}/insights",
            {"metric": "page_posts_impressions", "period": "day"},
            since, until,
        )
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
        op_data = _get_insights_chunked(
            f"{FACEBOOK_PAGE_ID}/insights",
            {"metric": "page_impressions_organic,page_impressions_paid", "period": "day"},
            since, until,
        )
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

    # ── period_reach — exact deduplicated unique reach ────────────────────────
    #
    # Only computed for windows that map EXACTLY to a Meta Graph API period.
    # For all other windows, reach_window_label="N/A" signals the UI to show "—"
    # instead of a misleading approximation.
    #
    # Exact windows:
    #   1 day        → period=day   (Today, Yesterday, custom 1-day)
    #   2–7 days     → period=week  (This Week, Last Week, Last 7 Days)
    #   28–31 days   → period=month (Last 30 Days, This Month, Last Month)
    #
    # Everything else (Last 14d, Last 60d, Last 90d, quarters, years…) → "—"
    from datetime import datetime as _dt2
    _since_dt = _dt2.strptime(since, "%Y-%m-%d").date()
    _until_dt = _dt2.strptime(until, "%Y-%m-%d").date()
    _window   = (_until_dt - _since_dt).days + 1

    if _window == 1:
        _reach_api_period = "day"
    elif _window <= 7:
        _reach_api_period = "week"
    elif 28 <= _window <= 31:
        _reach_api_period = "month"
    else:
        _reach_api_period = None   # no valid exact window → show "—" in UI

    if _reach_api_period:
        def _try_reach(period: str) -> int:
            try:
                d = _get(f"{FACEBOOK_PAGE_ID}/insights", {
                    "metric": "page_impressions_unique",
                    "period": period,
                    "since": since,
                    "until": until,
                })
                for m in d.get("data", []):
                    if m["name"] == "page_impressions_unique":
                        vals = m.get("values", [])
                        if vals:
                            v = vals[-1].get("value", 0)
                            print(f"DEBUG: period_reach ({period}, {_window}d) = {v}")
                            return v
            except Exception as e:
                print(f"DEBUG: period_reach ({period}) failed: {e}")
            return 0

        reach_val = _try_reach(_reach_api_period)
        # For month, also try days_28 if month returned 0
        if reach_val == 0 and _reach_api_period == "month":
            reach_val = _try_reach("days_28")
        # Last resort: daily sum (still exact-ish for short windows)
        if reach_val == 0:
            reach_val = sum(v["value"] for v in result.get("reach", []))
            print(f"DEBUG: period_reach (daily sum fallback, {_window}d) = {reach_val}")

        result["period_reach"]      = reach_val
        result["reach_window_label"] = None   # exact — UI shows the number
    else:
        result["period_reach"]      = 0
        result["reach_window_label"] = "N/A"  # UI shows "—"
        print(f"DEBUG: period_reach N/A — window {_window}d has no exact Meta API mapping")

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

    # Values Meta returns that carry no useful geographic information
    _SKIP = {"unknown", "?", "", "other", "n/a"}

    # ── Countries ─────────────────────────────────────────────────────────────
    try:
        c_rows = _fetch_breakdown("country")
        c_totals: dict[str, int] = {}
        for row in c_rows:
            c = row.get("country", "").strip()
            if c.lower() in _SKIP:
                continue
            c_totals[c] = c_totals.get(c, 0) + int(row.get("reach", 0) or 0)
        total_c = sum(c_totals.values()) or 1
        result["top_countries"] = sorted(
            [{"name": k, "reach": v, "pct": round(v / total_c * 100, 1)}
             for k, v in c_totals.items()],
            key=lambda x: x["reach"], reverse=True,
        )[:10]
        print(f"DEBUG demographics countries: {len(result['top_countries'])} entries")
    except Exception as e:
        print(f"DEBUG demographics countries error: {e}")

    # ── Cities / Regions ──────────────────────────────────────────────────────
    try:
        r_rows = _fetch_breakdown("region")
        r_totals: dict[str, int] = {}
        for row in r_rows:
            r = row.get("region", "").strip()
            if r.lower() in _SKIP:
                continue
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
def fetch_fb_posts(days: int = None, start: str = None, end: str = None, limit: int = 20) -> list[dict]:
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

            # ── 5. Post type from attachments ─────────────────────────────────
            _att_items = p.get("attachments", {}).get("data", [])
            _att_type  = _att_items[0].get("type", "") if _att_items else ""
            _att_media = _att_items[0].get("media_type", "") if _att_items else ""
            # Normalize to human-readable label
            if _att_type in ("video_inline", "video_autoplay") or _att_media == "video":
                _post_type = "Vidéo / Reel"
            elif _att_type == "album" or _att_media == "album":
                _post_type = "Carrousel"
            elif _att_type in ("photo", "sticker") or _att_media == "photo":
                _post_type = "Photo"
            elif _att_type == "share":
                _post_type = "Lien"
            elif video_views > 0:
                _post_type = "Vidéo / Reel"   # fallback: has video views → video
            else:
                _post_type = "Photo"           # default fallback

            return {
                "id":                   p.get("id", ""),
                "text":                 p.get("message", p.get("story", ""))[:120],
                "created_time":         p.get("created_time", "")[:10],
                "thumbnail":            p.get("full_picture", ""),
                "media_type":           _post_type,
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
        with ThreadPoolExecutor(max_workers=20) as executor:
            parsed = list(executor.map(_process_fb_post, posts))

        return parsed
    except Exception as e:
        print(f"DEBUG: FB posts error: {e}")
        return []


# ─── Facebook — Post interaction totals (all posts in period) ────────────────
def fetch_fb_post_totals(days: int = None, start: str = None, end: str = None) -> dict:
    """
    Paginates through ALL posts published in the period and sums reactions,
    comments and shares from the public post snapshot (no per-post insights
    call — very fast).

    Used exclusively for the KPI row so totals are not capped at 20 posts.
    The Top Content display still uses fetch_fb_posts (20 posts + full insights).
    """
    since, until = _date_range(days or 30, start, end)
    try:
        until_incl = str((dateparser.parse(until) + timedelta(days=1)).date())
    except Exception:
        until_incl = until

    _FIELDS = "id,reactions.summary(true).filter(stream),comments.summary(true).filter(stream),shares"
    params = {
        "fields": _FIELDS,
        "limit":  100,
        "since":  since,
        "until":  until_incl,
    }

    total_reactions = 0
    total_comments  = 0
    total_shares    = 0
    total_posts     = 0

    for _ in range(10):          # max 10 pages = 1 000 posts safety cap
        try:
            data = _get(f"{FACEBOOK_PAGE_ID}/posts", params)
        except Exception as e:
            print(f"DEBUG fetch_fb_post_totals page error: {e}")
            break

        posts = data.get("data", [])
        if not posts:
            break

        for p in posts:
            total_reactions += p.get("reactions", {}).get("summary", {}).get("total_count", 0)
            total_comments  += p.get("comments",  {}).get("summary", {}).get("total_count", 0)
            total_shares    += p.get("shares",     {}).get("count", 0)
            total_posts     += 1

        next_cursor = data.get("paging", {}).get("cursors", {}).get("after")
        next_url    = data.get("paging", {}).get("next")
        if not next_url or not next_cursor:
            break
        params = {**params, "after": next_cursor}

    print(f"DEBUG fetch_fb_post_totals: {total_posts} posts, "
          f"{total_reactions} reactions, {total_comments} comments, {total_shares} shares")

    return {
        "total_posts":     total_posts,
        "total_reactions": total_reactions,
        "total_comments":  total_comments,
        "total_shares":    total_shares,
        "total_interactions": total_reactions + total_comments + total_shares,
    }


# ─── Facebook — Messaging insights ───────────────────────────────────────────
def fetch_fb_messaging_stats(days: int, start: str = None, end: str = None) -> dict:
    """
    Returns messaging KPIs sourced from Page Insights.

    page_messages_new_conversations_unique (period=day, summed) — the only
    confirmed working metric for period-scoped contact volume on this page.
    page_messages_total_messaging_connections is not supported (empty data).
    """
    since, until = _date_range(days, start, end)
    result = {"new_conversations": 0}
    try:
        data = _get_insights_chunked(
            f"{FACEBOOK_PAGE_ID}/insights",
            {"metric": "page_messages_new_conversations_unique", "period": "day"},
            since, until,
        )
        for m in data.get("data", []):
            if m.get("name") == "page_messages_new_conversations_unique":
                vals = m.get("values", [])
                result["new_conversations"] = sum(
                    v.get("value", 0) for v in vals if isinstance(v.get("value"), int)
                )
    except Exception as e:
        print(f"DEBUG messaging stats error: {e}")
    return result


# ─── Facebook — Conversations ─────────────────────────────────────────────────
def fetch_fb_conversations(limit: int = 25, days: int = 30, start: str = None, end: str = None) -> dict:
    """
    Returns thread-level community stats: response rate, response time,
    unanswered threads. Fetched from /conversations with cursor pagination.

    The /conversations endpoint ignores since/until — it always returns threads
    sorted newest-first. We filter client-side by updated_time date prefix.
    Each API call is individually wrapped so a timeout on one page doesn't
    zero out the whole result.
    """
    since, until = _date_range(days, start, end)

    result = {
        "total_threads": 0,
        "replied_threads": 0,
        "response_times_minutes": [],
        "recent_unanswered": [],
    }

    all_threads = []
    cursor = None

    # Up to 3 pages of 25 threads each (75 max).
    # limit=25 with full message fields is reliably fast; limit=50+ can timeout.
    for _ in range(3):
        try:
            params = {
                "fields": "id,updated_time,messages{created_time,from,message}",
                "limit": 25,
            }
            if cursor:
                params["after"] = cursor

            data = _get(f"{FACEBOOK_PAGE_ID}/conversations", params)
        except Exception as e:
            print(f"DEBUG conversations fetch error (page): {e}")
            break

        page_threads = data.get("data", [])
        if not page_threads:
            break

        stop_paginating = False
        for t in page_threads:
            upd_date = t.get("updated_time", "")[:10]
            if not upd_date:
                continue
            # Threads are newest-first; stop once we're past our window
            if upd_date < since:
                stop_paginating = True
                break
            if since <= upd_date <= until:
                all_threads.append(t)

        if stop_paginating:
            break

        cursor = data.get("paging", {}).get("cursors", {}).get("after")
        if not cursor:
            break

    # Fallback: if nothing matched the date range, show the raw first page
    # so the tab never renders all-zeros when the API is alive
    if not all_threads:
        try:
            fallback = _get(f"{FACEBOOK_PAGE_ID}/conversations", {
                "fields": "id,updated_time,messages{created_time,from,message}",
                "limit": 25,
            })
            all_threads = fallback.get("data", [])
        except Exception as e:
            print(f"DEBUG conversations fallback error: {e}")

    result["total_threads"] = len(all_threads)

    for thread in all_threads:
        try:
            msgs = thread.get("messages", {}).get("data", [])
            if not msgs:
                continue

            last_msg       = msgs[0]   # newest
            last_sender_id = str(last_msg.get("from", {}).get("id", ""))

            page_replied = any(
                str(m.get("from", {}).get("id", "")) == str(FACEBOOK_PAGE_ID)
                for m in msgs
            )

            if page_replied:
                result["replied_threads"] += 1
                user_msgs = [m for m in msgs
                             if str(m.get("from", {}).get("id", "")) != str(FACEBOOK_PAGE_ID)]
                page_msgs = [m for m in msgs
                             if str(m.get("from", {}).get("id", "")) == str(FACEBOOK_PAGE_ID)]
                if user_msgs and page_msgs:
                    first_user_time = dateparser.parse(user_msgs[-1]["created_time"])
                    # Oldest page reply that came after the first user message
                    first_reply = next(
                        (m for m in reversed(page_msgs)
                         if dateparser.parse(m["created_time"]) >= first_user_time),
                        page_msgs[-1],
                    )
                    delta = (dateparser.parse(first_reply["created_time"]) - first_user_time
                             ).total_seconds() / 60
                    if delta >= 0:
                        result["response_times_minutes"].append(delta)
            else:
                snippet = last_msg.get("message", "").strip()
                result["recent_unanswered"].append({
                    "text": snippet[:80] if snippet else "(media / attachment)",
                    "time": thread.get("updated_time", "")[:16],
                    "sender": last_msg.get("from", {}).get("name", ""),
                })
        except Exception as e:
            print(f"DEBUG thread processing error: {e}")
            continue

    return result
