"""
check_boost.py
--------------
Diagnoses why the Boost tab shows "non connectées".

Run:
    python scratch/check_boost.py
"""

import sys, os
sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

import requests
from config import ADS_ACCESS_TOKEN, FOOTLAND_CAMPAIGN_KEYWORDS, GRAPH_BASE_URL, BLOCKED_AD_ACCOUNTS

AD_ACCOUNT = BLOCKED_AD_ACCOUNTS[0]

print(f"\nAd account : {AD_ACCOUNT}")
print(f"Token      : {ADS_ACCESS_TOKEN[:20]}...")
print(f"Keywords   : {FOOTLAND_CAMPAIGN_KEYWORDS}\n")

# ── Step 1: Verify token has ads_read ────────────────────────────────────────
print("── Step 1: Token permissions ────────────────────────────────")
r = requests.get(
    f"{GRAPH_BASE_URL}/me/permissions",
    params={"access_token": ADS_ACCESS_TOKEN},
    timeout=15,
)
perms = r.json()
if "error" in perms:
    print(f"  ERROR: {perms['error'].get('message')}")
else:
    granted = [p["permission"] for p in perms.get("data", []) if p.get("status") == "granted"]
    has_ads = "ads_read" in granted
    print(f"  ads_read granted : {'✅ YES' if has_ads else '❌ NO  ← this is the problem'}")
    print(f"  all permissions  : {granted}")

# ── Step 2: Can we access the ad account at all? ──────────────────────────────
print("\n── Step 2: Ad account access ────────────────────────────────")
r2 = requests.get(
    f"{GRAPH_BASE_URL}/{AD_ACCOUNT}",
    params={"fields": "name,account_status", "access_token": ADS_ACCESS_TOKEN},
    timeout=15,
)
acc = r2.json()
if "error" in acc:
    print(f"  ERROR: {acc['error'].get('message')}")
else:
    print(f"  Account name   : {acc.get('name')}")
    print(f"  Account status : {acc.get('account_status')}  (1=active)")

# ── Step 3: List ALL campaigns and check keyword matches ─────────────────────
print("\n── Step 3: Campaigns in ad account ─────────────────────────")
r3 = requests.get(
    f"{GRAPH_BASE_URL}/{AD_ACCOUNT}/campaigns",
    params={"fields": "id,name", "limit": 500, "access_token": ADS_ACCESS_TOKEN},
    timeout=20,
)
camps = r3.json()
if "error" in camps:
    print(f"  ERROR: {camps['error'].get('message')}")
else:
    all_camps = camps.get("data", [])
    print(f"  Total campaigns : {len(all_camps)}")

    footland = [c for c in all_camps if any(kw in c.get("name","") for kw in FOOTLAND_CAMPAIGN_KEYWORDS)]
    other    = [c for c in all_camps if c not in footland]

    print(f"  Footland matches: {len(footland)}")
    for c in footland[:20]:
        print(f"    ✅  {c['id']}  {c['name']}")

    print(f"\n  Non-Footland (first 10):")
    for c in other[:10]:
        print(f"    ·   {c['id']}  {c['name']}")

    if not footland and all_camps:
        print("\n  ⚠️  No campaigns matched. Campaign names above — do any of these")
        print("  contain one of your keywords? If not, update FOOTLAND_CAMPAIGN_KEYWORDS in config.py.")

print()
