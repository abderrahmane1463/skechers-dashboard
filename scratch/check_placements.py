import sys, os
sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

import requests
from config import ACCESS_TOKEN, FACEBOOK_PAGE_ID, GRAPH_BASE_URL

metrics_to_test = [
    "page_impressions",
    "page_impressions_unique",
    "page_posts_impressions",
    "page_posts_impressions_unique",
    "page_impressions_organic",
    "page_impressions_organic_unique",
    "page_impressions_paid",
    "page_impressions_paid_unique",
    "page_impressions_viral",
    "page_impressions_viral_unique",
    "page_impressions_nonviral",
    "page_impressions_nonviral_unique",
    "page_video_views",
    "page_video_views_unique",
    "page_video_complete_views_30s",
    "page_video_views_organic",
    "page_video_views_paid",
    "page_daily_story_views",
    "page_impressions_by_story_type",
    "page_impressions_by_story_type_unique",
]

since = "2025-03-01"
until = "2025-03-31"

print(f"\n{'METRIC':<45} {'VALUE':>15}")
print("-" * 62)

for metric in metrics_to_test:
    try:
        r = requests.get(
            f"{GRAPH_BASE_URL}/{FACEBOOK_PAGE_ID}/insights",
            params={
                "metric": metric,
                "period": "month",
                "since": since,
                "until": until,
                "access_token": ACCESS_TOKEN,
            },
            timeout=15,
        )
        data = r.json()
        if "error" in data:
            msg = data["error"].get("message", "")[:40]
            print(f"{metric:<45} ERROR: {msg}")
            continue
        for m in data.get("data", []):
            vals = m.get("values", [])
            if not vals:
                print(f"{metric:<45} {'(no values)':>15}")
                continue
            val = max(v["value"] for v in vals)
            if isinstance(val, dict):
                val = sum(val.values())
            print(f"{metric:<45} {val:>15,}")
    except Exception as e:
        print(f"{metric:<45} EXCEPTION: {e}")

print()
