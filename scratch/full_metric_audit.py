"""
full_metric_audit.py
--------------------
Tests every known Facebook Page Insights and Instagram metric for
2025-03-01 → 2025-03-31 across all relevant periods.

Output: a readable table you can compare line-by-line against your report.

Run:
    python scratch/full_metric_audit.py           # both FB + IG
    python scratch/full_metric_audit.py ig        # Instagram only (faster)
    python scratch/full_metric_audit.py fb        # Facebook only
    python scratch/full_metric_audit.py > scratch/audit_results.txt
"""

import sys, os
sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

# Which platforms to run — pass "ig" or "fb" as first arg to limit scope
_arg = sys.argv[1].lower() if len(sys.argv) > 1 else "all"
RUN_FB = _arg in ("all", "fb")
RUN_IG = _arg in ("all", "ig")

import requests
from config import ACCESS_TOKEN, FACEBOOK_PAGE_ID, INSTAGRAM_USER_ID, GRAPH_BASE_URL

SINCE = "2025-03-01"
UNTIL = "2025-03-31"          # inclusive end for the API
UNTIL_MONTH = "2025-03-31"    # same — calendar month end

# ─────────────────────────────────────────────────────────────────────────────
# Helpers
# ─────────────────────────────────────────────────────────────────────────────

def _get(url, params):
    params["access_token"] = ACCESS_TOKEN
    r = requests.get(url, params=params, timeout=20)
    return r.json()

def _fmt(val):
    if isinstance(val, dict):
        return f"DICT: {dict(list(val.items())[:3])}"
    try:
        return f"{int(val):>20,}"
    except Exception:
        return f"{str(val):>20}"

def _print_row(metric, period, value, note=""):
    note_str = f"  ← {note}" if note else ""
    print(f"  {metric:<55} [{period:<9}]  {_fmt(value)}{note_str}")

def _section(title):
    print()
    print("═" * 90)
    print(f"  {title}")
    print("═" * 90)


def test_fb_metric(metric, periods=("day", "week", "days_28", "month"),
                   since=SINCE, until=UNTIL, note=""):
    """Try one FB metric across all requested periods, print result rows."""
    for period in periods:
        try:
            data = _get(f"{GRAPH_BASE_URL}/{FACEBOOK_PAGE_ID}/insights", {
                "metric": metric,
                "period": period,
                "since": since,
                "until": until,
            })
            if "error" in data:
                code = data["error"].get("code", "?")
                msg  = data["error"].get("message", "")[:60]
                _print_row(metric, period, f"ERROR #{code}: {msg}", note)
                continue
            for m in data.get("data", []):
                vals = m.get("values", [])
                if not vals:
                    _print_row(metric, period, "(no values)", note)
                    continue
                # For day/week/days_28: sum all buckets → period total
                # For month: take the max bucket (most complete month)
                if period == "month":
                    agg = max(
                        (v["value"] if not isinstance(v["value"], dict)
                         else sum(v["value"].values()))
                        for v in vals
                    )
                    _print_row(metric, period, agg, note + " [max bucket]")
                else:
                    agg = sum(
                        (v["value"] if not isinstance(v["value"], dict)
                         else sum(v["value"].values()))
                        for v in vals
                    )
                    _print_row(metric, period, agg, note + f" [{len(vals)} days]")
        except Exception as e:
            _print_row(metric, period, f"EXCEPTION: {e}", note)


def test_ig_metric(metric, periods=("day", "week", "days_28", "month"),
                   since=SINCE, until=UNTIL, note=""):
    for period in periods:
        try:
            data = _get(f"{GRAPH_BASE_URL}/{INSTAGRAM_USER_ID}/insights", {
                "metric": metric,
                "period": period,
                "since": since,
                "until": until,
            })
            if "error" in data:
                code = data["error"].get("code", "?")
                msg  = data["error"].get("message", "")[:60]
                _print_row(metric, period, f"ERROR #{code}: {msg}", note)
                continue
            for m in data.get("data", []):
                vals = m.get("values", [])
                if not vals:
                    _print_row(metric, period, "(no values)", note)
                    continue
                if period == "month":
                    agg = max(
                        (v["value"] if not isinstance(v["value"], dict)
                         else sum(v["value"].values()))
                        for v in vals
                    )
                    _print_row(metric, period, agg, note + " [max bucket]")
                else:
                    agg = sum(
                        (v["value"] if not isinstance(v["value"], dict)
                         else sum(v["value"].values()))
                        for v in vals
                    )
                    _print_row(metric, period, agg, note + f" [{len(vals)} days]")
        except Exception as e:
            _print_row(metric, period, f"EXCEPTION: {e}", note)


def test_ig_total_value(metric, since=SINCE, until=UNTIL, note=""):
    """
    Instagram metrics that use metric_type=total_value.
    Meta requires BOTH metric_type=total_value AND period=day together.
    Also tries period=week and period=days_28 to find which returns data.
    """
    for period in ("day", "week", "days_28"):
        label = f"tv+{period}"
        try:
            data = _get(f"{GRAPH_BASE_URL}/{INSTAGRAM_USER_ID}/insights", {
                "metric": metric,
                "metric_type": "total_value",
                "period": period,
                "since": since,
                "until": until,
            })
            if "error" in data:
                code = data["error"].get("code", "?")
                msg  = data["error"].get("message", "")[:60]
                _print_row(metric, label, f"ERROR #{code}: {msg}", note)
                continue
            # total_value responses have a different shape:
            # {"data": [{"name": "...", "total_value": {"value": 123}, "period": "day"}]}
            for item in data.get("data", []):
                tv = item.get("total_value", {})
                if isinstance(tv, dict):
                    val = tv.get("value", "(no value key)")
                    # Some metrics return breakdowns dict under total_value
                    if isinstance(val, dict):
                        val = sum(val.values())
                else:
                    val = tv
                _print_row(metric, label, val, note)
        except Exception as e:
            _print_row(metric, label, f"EXCEPTION: {e}", note)


# ─────────────────────────────────────────────────────────────────────────────
# FACEBOOK
# ─────────────────────────────────────────────────────────────────────────────

# ─────────────────────────────────────────────────────────────────────────────
# FACEBOOK
# ─────────────────────────────────────────────────────────────────────────────

if RUN_FB:
    _section("FACEBOOK — REACH / IMPRESSIONS  (map to 📢 Impressions + 👁️ Spectateurs)")
    for m in [
        "page_impressions", "page_impressions_unique",
        "page_posts_impressions", "page_posts_impressions_unique",
        "page_impressions_organic", "page_impressions_organic_unique",
        "page_impressions_paid", "page_impressions_paid_unique",
        "page_impressions_viral", "page_impressions_viral_unique",
        "page_impressions_nonviral", "page_impressions_nonviral_unique",
        "page_impressions_by_story_type", "page_impressions_by_story_type_unique",
    ]:
        test_fb_metric(m, periods=("day", "month"))

    _section("FACEBOOK — PAGE VIEWS  (map to 👀 Vues de la page)")
    for m in [
        "page_views_total", "page_views_logged_in_total",
        "page_views_by_profile_tab_total",
        "page_views_by_profile_tab_logged_in_unique",
        "page_views_by_referers_logged_in_unique",
    ]:
        test_fb_metric(m, periods=("day", "month"))

    _section("FACEBOOK — ENGAGEMENT  (map to 💬 Interactions + ❤️ Réactions)")
    for m in [
        "page_post_engagements", "page_actions_post_reactions_total",
        "page_positive_feedback_by_type",
        "page_negative_feedback", "page_negative_feedback_unique",
        "page_fan_adds", "page_fan_removes", "page_fans",
    ]:
        test_fb_metric(m, periods=("day", "month"))

    _section("FACEBOOK — VIDEO  (map to 🎬 Vues vidéo)")
    for m in [
        "page_video_views", "page_video_views_unique",
        "page_video_views_paid", "page_video_views_organic",
        "page_video_views_autoplayed", "page_video_views_click_to_play",
        "page_video_complete_views_30s",
        "page_video_complete_views_30s_paid",
        "page_video_complete_views_30s_organic",
        "page_video_complete_views_30s_autoplayed",
        "page_video_complete_views_30s_click_to_play",
        "page_video_avg_time_based_watch_time",
    ]:
        test_fb_metric(m, periods=("day", "month"))

    _section("FACEBOOK — STORIES  (map to 📖 Stories)")
    for m in ["page_daily_story_views", "page_story_impressions", "page_story_reach"]:
        test_fb_metric(m, periods=("day", "month"))

    _section("FACEBOOK — AUDIENCE / FANS  (map to 👥 Abonnés)")
    for m in [
        "page_fans", "page_fan_adds", "page_fan_adds_unique",
        "page_fan_removes", "page_fans_by_like_source",
        "page_fans_gender_age", "page_fans_country",
        "page_fans_city", "page_fans_locale",
        "page_fans_online", "page_fans_online_per_day",
    ]:
        test_fb_metric(m, periods=("day", "month"))


# ─────────────────────────────────────────────────────────────────────────────
# INSTAGRAM
# Note: most IG metrics need metric_type=total_value + period together.
#       test_ig_total_value() now tries period=day, week, days_28 with total_value.
#       test_ig_metric() tries the plain period-only form (for "reach" which works).
# ─────────────────────────────────────────────────────────────────────────────

if RUN_IG:
    _section("INSTAGRAM — REACH / IMPRESSIONS  (map to 📢 Impressions + 👁️ Portée)")
    for m in ["impressions", "reach", "accounts_engaged", "total_interactions"]:
        test_ig_metric(m, periods=("day", "week", "days_28"))
        test_ig_total_value(m)

    _section("INSTAGRAM — ENGAGEMENT  (map to ❤️ + 💬 + 🔖 + ↗️)")
    for m in ["likes", "comments", "shares", "saves", "replies",
              "total_interactions", "accounts_engaged"]:
        test_ig_metric(m, periods=("day", "days_28"))
        test_ig_total_value(m)

    _section("INSTAGRAM — PROFILE VIEWS  (map to 👀 Vues du profil)")
    for m in ["profile_views", "profile_links_taps", "website_clicks",
              "email_contacts", "get_directions_clicks",
              "call_phone_number_clicks", "text_message_clicks"]:
        test_ig_metric(m, periods=("day", "days_28"))
        test_ig_total_value(m)

    _section("INSTAGRAM — FOLLOWERS  (map to 👥 Abonnés)")
    for m in ["follower_count", "online_followers"]:
        test_ig_metric(m, periods=("day", "week", "days_28"))
        test_ig_total_value(m)

    _section("INSTAGRAM — VIDEO / REELS  (map to 🎬 Vues vidéo)")
    for m in [
        "video_views", "clips_replays_count",
        "ig_reels_aggregated_all_plays_count",
        "ig_reels_video_view_total_time",
        "ig_reels_avg_watch_time",
    ]:
        test_ig_metric(m, periods=("day", "days_28"))
        test_ig_total_value(m)


print()
print("═" * 90)
print("  DONE — compare values above to your Meta Business Suite report for March 2025")
print("═" * 90)
print()
