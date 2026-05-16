"""
fetcher.py — Fetches all metrics from Meta Graph API and stores them in Supabase.
Run manually or via GitHub Actions cron (every 6 hours).

Covers every date-range preset available in the dashboard sidebar so that
all selections hit Supabase cache instead of making a live API call.

Usage:
    python fetcher.py
"""

import calendar
from datetime import datetime, timezone, date, timedelta
from concurrent.futures import ThreadPoolExecutor, as_completed, TimeoutError
from dotenv import load_dotenv

load_dotenv()

import api
import db
from api.boost import fetch_boost_insights, fetch_adset_ad_insights as fetch_adset_ad_insights_fetcher


# ── Periods to fetch ──────────────────────────────────────────────────────────
def _periods():
    """
    Returns a list of (label, period_start, period_end, days) tuples.
    Covers ALL sidebar presets: rolling windows + every calendar period.
    """
    today = date.today()

    def _quarter(d):
        return (d.month - 1) // 3 + 1

    # ── Rolling windows ───────────────────────────────────────────────────────
    rolling = [
        ("last_7d",  today - timedelta(days=7),  today,  7),
        ("last_14d", today - timedelta(days=14), today, 14),
        ("last_30d", today - timedelta(days=30), today, 30),
        ("last_60d", today - timedelta(days=60), today, 60),
        ("last_90d", today - timedelta(days=90), today, 90),
    ]

    # ── Calendar windows ──────────────────────────────────────────────────────
    yesterday = today - timedelta(days=1)

    # This week (Mon → today)
    tw_start = today - timedelta(days=today.weekday())

    # Last week (Mon → Sun)
    lw_end   = today - timedelta(days=today.weekday() + 1)
    lw_start = lw_end - timedelta(days=6)

    # This month / Last month
    cm_start = today.replace(day=1)
    pm_end   = cm_start - timedelta(days=1)
    pm_start = pm_end.replace(day=1)

    # This quarter
    q        = _quarter(today)
    tq_start = today.replace(month=(q - 1) * 3 + 1, day=1)

    # Last quarter
    lq       = q - 1 if q > 1 else 4
    lq_year  = today.year if q > 1 else today.year - 1
    lq_fm    = (lq - 1) * 3 + 1          # first month of last quarter
    lq_lm    = lq_fm + 2                  # last  month of last quarter
    _, lq_ld = calendar.monthrange(lq_year, lq_lm)
    lq_start = date(lq_year, lq_fm, 1)
    lq_end   = date(lq_year, lq_lm, lq_ld)

    # This year / Last year
    ty_start = today.replace(month=1, day=1)
    ly_start = date(today.year - 1, 1, 1)
    ly_end   = date(today.year - 1, 12, 31)

    calendar_periods = [
        ("today",        today,    today,    1),
        ("yesterday",    yesterday, yesterday, 1),
        ("this_week",    tw_start, today,    (today - tw_start).days + 1),
        ("last_week",    lw_start, lw_end,   7),
        ("this_month",   cm_start, today,    (today - cm_start).days + 1),
        ("last_month",   pm_start, pm_end,   (pm_end - pm_start).days + 1),
        ("this_quarter", tq_start, today,    (today - tq_start).days + 1),
        ("last_quarter", lq_start, lq_end,   (lq_end - lq_start).days + 1),
        ("this_year",    ty_start, today,    (today - ty_start).days + 1),
        ("last_year",    ly_start, ly_end,   365),
    ]

    all_periods = rolling + calendar_periods
    return [
        (label, str(s), str(e), days)
        for label, s, e, days in all_periods
    ]


# ── Metrics to fetch per period ───────────────────────────────────────────────
# fb_demographics is excluded: it uses the Marketing API which is blocked
# for organic-only pages and causes repeated 90-second retry storms.
def _tasks_for_period(p_start, p_end, days):
    return [
        ("ig_profile",      api.fetch_ig_profile,                             p_start, p_end, days),
        ("ig_engagement",   api.fetch_ig_engagement,                          p_start, p_end, days),
        ("ig_posts",        lambda d, s, e: api.fetch_ig_posts(d, s, e, 100), p_start, p_end, days),
        ("ig_post_totals",  api.fetch_ig_post_totals,                         p_start, p_end, days),
        ("fb_audience",     api.fetch_fb_audience,                            p_start, p_end, days),
        ("fb_engagement",   api.fetch_fb_engagement,                          p_start, p_end, days),
        ("fb_visibility",   api.fetch_fb_visibility,                          p_start, p_end, days),
        ("fb_posts",        lambda d, s, e: api.fetch_fb_posts(d, s, e, 100), p_start, p_end, days),
        ("fb_post_totals",  api.fetch_fb_post_totals,                         p_start, p_end, days),
        ("fb_conversations",api.fetch_fb_conversations,                       p_start, p_end, days),
        ("fb_messaging",    api.fetch_fb_messaging_stats,                     p_start, p_end, days),
        ("boost_insights",  fetch_boost_insights,                             p_start, p_end, days),
        ("boost_adset_ad", fetch_adset_ad_insights_fetcher, p_start, p_end, days),
    ]


# ── Fetch + save one metric ───────────────────────────────────────────────────
TASK_TIMEOUT = 60   # seconds: max time for a single API fetch + save

def _fetch_and_save(metric_key, fn, period_start, period_end, days):
    print(f"  → {metric_key} [{period_start} → {period_end}]")
    try:
        data = fn(days, period_start, period_end)
        ok   = db.save(metric_key, period_start, period_end, data)
        status = "OK" if ok else "FAIL(save)"
    except Exception as e:
        status = f"FAIL({type(e).__name__}: {str(e)[:60]})"
    print(f"     {status}  {metric_key}")
    return metric_key, status


# ── Main ──────────────────────────────────────────────────────────────────────
def run():
    started = datetime.now(timezone.utc)
    print(f"\n{'═'*56}")
    print(f"  Footland Fetcher — {started.strftime('%Y-%m-%d %H:%M UTC')}")
    print(f"{'═'*56}\n")

    periods = _periods()

    # Build full task list
    tasks = []
    for label, p_start, p_end, days in periods:
        for task in _tasks_for_period(p_start, p_end, days):
            tasks.append(task)

    n_periods = len(periods)
    n_tasks   = len(tasks)
    print(f"  {n_tasks} tasks across {n_periods} periods\n")
    for label, p_start, p_end, _ in periods:
        print(f"    {label:15s}  {p_start} → {p_end}")
    print()

    results = []
    with ThreadPoolExecutor(max_workers=12) as pool:
        futures = {
            pool.submit(_fetch_and_save, *task): f"{task[0]}[{task[2]}]"
            for task in tasks
        }
        for future in as_completed(futures):
            label = futures[future]
            try:
                key, status = future.result(timeout=TASK_TIMEOUT)
            except TimeoutError:
                status = "FAIL(timeout)"
                print(f"     TIMEOUT  {label}")
            except Exception as e:
                status = f"FAIL({e})"
            results.append(status)

    elapsed = (datetime.now(timezone.utc) - started).total_seconds()
    success = sum(1 for s in results if s == "OK")
    failed  = len(results) - success

    print(f"\n{'═'*56}")
    print(f"  ✅ {success} OK   ❌ {failed} FAILED   ⏱ {elapsed:.0f}s")
    print(f"{'═'*56}\n")


if __name__ == "__main__":
    run()
