"""
check_community.py
------------------
Tests every known Facebook messaging / community metric and the
/conversations endpoint for a given date range.

Run:
    python scratch/check_community.py
    python scratch/check_community.py 2025-03-01 2025-03-31   # custom range
    python scratch/check_community.py > scratch/community_results.txt
"""

import sys, os
sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

import requests
from config import ACCESS_TOKEN, FACEBOOK_PAGE_ID, GRAPH_BASE_URL

SINCE = sys.argv[1] if len(sys.argv) > 1 else "2025-03-01"
UNTIL = sys.argv[2] if len(sys.argv) > 2 else "2025-03-31"

print(f"\nPage ID : {FACEBOOK_PAGE_ID}")
print(f"Period  : {SINCE} → {UNTIL}\n")


def _get(path, params=None):
    p = dict(params or {})
    p["access_token"] = ACCESS_TOKEN
    r = requests.get(f"{GRAPH_BASE_URL}/{path}", params=p, timeout=20)
    return r.json()

def _fmt(val):
    if isinstance(val, dict):
        return f"DICT:{dict(list(val.items())[:4])}"
    try:
        return f"{int(val):>15,}"
    except Exception:
        return f"{str(val):>15}"

def _row(label, value, note=""):
    note_str = f"  ← {note}" if note else ""
    print(f"  {label:<65} {_fmt(value)}{note_str}")

def _section(title):
    print()
    print("═" * 90)
    print(f"  {title}")
    print("═" * 90)

def test_insight(metric, periods=("day", "month")):
    for period in periods:
        try:
            data = _get(f"{FACEBOOK_PAGE_ID}/insights", {
                "metric": metric, "period": period,
                "since": SINCE, "until": UNTIL,
            })
            if "error" in data:
                code = data["error"].get("code", "?")
                msg  = data["error"].get("message", "")[:70]
                _row(f"{metric} [{period}]", f"ERROR #{code}: {msg}")
                continue
            for m in data.get("data", []):
                vals = m.get("values", [])
                if not vals:
                    _row(f"{metric} [{period}]", "(no values)")
                    continue
                if period == "month":
                    agg = max(
                        (v["value"] if not isinstance(v["value"], dict) else sum(v["value"].values()))
                        for v in vals
                    )
                    _row(f"{metric} [{period}]", agg, "max bucket")
                else:
                    agg = sum(
                        (v["value"] if not isinstance(v["value"], dict) else sum(v["value"].values()))
                        for v in vals
                    )
                    _row(f"{metric} [{period}]", agg, f"{len(vals)} days summed")
        except Exception as e:
            _row(f"{metric} [{period}]", f"EXCEPTION: {e}")


# ══════════════════════════════════════════════════════════════════════════════
_section("1 — PAGE MESSAGING INSIGHTS (all known messaging metrics)")
# ══════════════════════════════════════════════════════════════════════════════

MESSAGING_METRICS = [
    # New / active conversations
    "page_messages_new_conversations_unique",
    "page_messages_active_threads_unique",

    # Total messaging connections (all people who can DM)
    "page_messages_total_messaging_connections",

    # Blocked / reported
    "page_messages_blocked_conversations_unique",
    "page_messages_reported_conversations_unique",
    "page_messages_reported_conversations_by_report_type_unique",

    # Response performance
    "page_messages_response_rate",
    "page_messages_average_response_time",

    # Feedback
    "page_messages_feedback_by_action_unique",

    # Conversational ads (may 403 without ads perms)
    "page_messages_paid_threads_unique",
    "page_messages_organic_threads_unique",
]

for m in MESSAGING_METRICS:
    test_insight(m, periods=("day", "month"))


# ══════════════════════════════════════════════════════════════════════════════
_section("2 — /conversations ENDPOINT — raw shape")
# ══════════════════════════════════════════════════════════════════════════════

print("\n  [A] First 5 threads — basic fields")
data = _get(f"{FACEBOOK_PAGE_ID}/conversations", {
    "fields": "id,updated_time,message_count,unread_count,participants",
    "limit": 5,
})
if "error" in data:
    print(f"  ERROR: {data['error'].get('message')}")
else:
    threads = data.get("data", [])
    print(f"  Total threads returned: {len(threads)}")
    for t in threads[:5]:
        parts = [p.get("name","?") for p in t.get("participants",{}).get("data",[])]
        print(f"    id={t.get('id')}  updated={t.get('updated_time','')[:10]}"
              f"  msgs={t.get('message_count')}  unread={t.get('unread_count')}"
              f"  participants={parts}")

print("\n  [B] First thread — full message list")
data2 = _get(f"{FACEBOOK_PAGE_ID}/conversations", {
    "fields": "id,updated_time,messages{id,created_time,from,message,attachments}",
    "limit": 1,
})
if "error" in data2:
    print(f"  ERROR: {data2['error'].get('message')}")
else:
    threads2 = data2.get("data", [])
    if threads2:
        t = threads2[0]
        msgs = t.get("messages", {}).get("data", [])
        print(f"  Thread id: {t.get('id')}  updated: {t.get('updated_time')}")
        print(f"  Messages loaded: {len(msgs)}")
        for m in msgs[:10]:
            sender = m.get("from", {})
            text   = m.get("message", "(no text)")[:60]
            has_att = bool(m.get("attachments", {}).get("data"))
            print(f"    [{m['created_time'][:16]}] from={sender.get('id')} ({sender.get('name','?')})"
                  f"  text={repr(text)}  att={has_att}")

print("\n  [C] Paging info — cursors available?")
data3 = _get(f"{FACEBOOK_PAGE_ID}/conversations", {"fields": "id,updated_time", "limit": 5})
paging = data3.get("paging", {})
print(f"  paging keys      : {list(paging.keys())}")
print(f"  cursors          : {paging.get('cursors', {})}")
print(f"  next (URL)       : {paging.get('next', '(none)')[:80] if paging.get('next') else '(none)'}")
print(f"  previous (URL)   : {paging.get('previous', '(none)')[:80] if paging.get('previous') else '(none)'}")


# ══════════════════════════════════════════════════════════════════════════════
_section("3 — /conversations with since/until — does date filtering work?")
# ══════════════════════════════════════════════════════════════════════════════

data4 = _get(f"{FACEBOOK_PAGE_ID}/conversations", {
    "fields": "id,updated_time",
    "limit": 25,
    "since": SINCE,
    "until": UNTIL,
})
if "error" in data4:
    print(f"  ERROR: {data4['error'].get('message')}")
else:
    threads4 = data4.get("data", [])
    print(f"  Threads returned with since={SINCE} until={UNTIL}: {len(threads4)}")
    for t in threads4[:5]:
        print(f"    id={t.get('id')}  updated={t.get('updated_time','')[:10]}")
    if threads4:
        oldest = threads4[-1].get("updated_time","")[:10]
        newest = threads4[0].get("updated_time","")[:10]
        print(f"  Date range of returned threads: {oldest} → {newest}")
        in_range = sum(1 for t in threads4 if SINCE <= t.get("updated_time","")[:10] <= UNTIL)
        print(f"  Threads actually within {SINCE}→{UNTIL}: {in_range}/{len(threads4)}")


# ══════════════════════════════════════════════════════════════════════════════
_section("4 — PAGE FIELDS: messaging_feature_status + response rate")
# ══════════════════════════════════════════════════════════════════════════════

fields_to_check = [
    "id,name",
    "messaging_feature_status",
    "overall_star_rating,rating_count",
    "response_time,response_rate",
]
for f in fields_to_check:
    d = _get(f"{FACEBOOK_PAGE_ID}", {"fields": f})
    if "error" in d:
        print(f"  fields={f}  →  ERROR: {d['error'].get('message','?')[:60]}")
    else:
        vals = {k: v for k, v in d.items() if k != "id"}
        print(f"  fields={f}")
        for k, v in vals.items():
            print(f"    {k}: {v}")


# ══════════════════════════════════════════════════════════════════════════════
_section("5 — COMMENT METRICS (posts engagement, moderation)")
# ══════════════════════════════════════════════════════════════════════════════

COMMENT_METRICS = [
    "page_positive_feedback_by_type",
    "page_negative_feedback",
    "page_negative_feedback_by_type",
    "page_negative_feedback_unique",
]
for m in COMMENT_METRICS:
    test_insight(m, periods=("day", "month"))

print()
print("═" * 90)
print("  DONE")
print("═" * 90)
print()
