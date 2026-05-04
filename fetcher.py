"""
fetcher.py — Fetches all metrics from Meta Graph API and stores them in Supabase.
Run manually or via GitHub Actions cron.

Usage:
    python fetcher.py
"""

import os
from datetime import datetime, timezone, date, timedelta
from concurrent.futures import ThreadPoolExecutor, as_completed
from dotenv import load_dotenv

load_dotenv()

import api
import db
from api.boost import fetch_boost_insights


# ── Periods to fetch ──────────────────────────────────────────────────────────
def _periods():
    """
    Returns a list of (label, period_start, period_end, days) tuples to fetch.
    Covers: last 7d, last 30d, last 90d, current month, previous month.
    """
    today = date.today()

    # Current month
    cm_start = today.replace(day=1)
    cm_end   = today

    # Previous month
    pm_end   = cm_start - timedelta(days=1)
    pm_start = pm_end.replace(day=1)

    return [
        ("last_7d",   str(today - timedelta(days=7)),  str(today), 7),
        ("last_30d",  str(today - timedelta(days=30)), str(today), 30),
        ("last_90d",  str(today - timedelta(days=90)), str(today), 90),
        ("cur_month", str(cm_start),                   str(cm_end), (cm_end - cm_start).days + 1),
        ("prev_month",str(pm_start),                   str(pm_end), (pm_end - pm_start).days + 1),
    ]


# ── Fetch + save one metric ───────────────────────────────────────────────────
def _fetch_and_save(metric_key: str, fn, period_start: str, period_end: str, days: int):
    print(f"  fetching {metric_key} [{period_start} to {period_end}]")
    try:
        data = fn(days, period_start, period_end)
        ok   = db.save(metric_key, period_start, period_end, data)
        status = "OK" if ok else "FAIL save"
    except Exception as e:
        status = f"FAIL {e}"
    print(f"     {status} {metric_key}")
    return metric_key, status


# ── Main ──────────────────────────────────────────────────────────────────────
def run():
    started = datetime.now(timezone.utc)
    print(f"\nFetcher started at {started.strftime('%Y-%m-%d %H:%M UTC')}\n")

    periods = _periods()

    # Build task list: (metric_key, fn, period_start, period_end, days)
    tasks = []
    for label, p_start, p_end, days in periods:
        tasks += [
            ("ig_profile",     api.fetch_ig_profile,        p_start, p_end, days),
            ("ig_engagement",  api.fetch_ig_engagement,     p_start, p_end, days),
            ("ig_posts",       lambda d,s,e: api.fetch_ig_posts(d, s, e, 100), p_start, p_end, days),
            ("ig_post_totals", api.fetch_ig_post_totals,    p_start, p_end, days),
            ("fb_audience",    api.fetch_fb_audience,       p_start, p_end, days),
            ("fb_engagement",  api.fetch_fb_engagement,     p_start, p_end, days),
            ("fb_visibility",  api.fetch_fb_visibility,     p_start, p_end, days),
            ("fb_demographics",api.fetch_fb_demographics,   p_start, p_end, days),
            ("fb_posts",       lambda d,s,e: api.fetch_fb_posts(d, s, e, 100), p_start, p_end, days),
            ("fb_post_totals", api.fetch_fb_post_totals,    p_start, p_end, days),
            ("fb_conversations",api.fetch_fb_conversations, p_start, p_end, days),
            ("fb_messaging",   api.fetch_fb_messaging_stats,p_start, p_end, days),
            ("boost_insights", fetch_boost_insights,        p_start, p_end, days),
        ]

    print(f"{len(tasks)} tasks across {len(periods)} periods\n")

    results = []
    with ThreadPoolExecutor(max_workers=6) as pool:
        futures = {
            pool.submit(_fetch_and_save, *task): task[0]
            for task in tasks
        }
        for future in as_completed(futures):
            key, status = future.result()
            results.append(status)

    elapsed = (datetime.now(timezone.utc) - started).total_seconds()
    success = sum(1 for s in results if s == "OK")
    failed  = len(results) - success

    print(f"\n{'─'*50}")
    print(f"OK: {success} succeeded  FAIL: {failed} failed  TIME: {elapsed:.1f}s")
    print(f"{'─'*50}\n")


if __name__ == "__main__":
    run()
