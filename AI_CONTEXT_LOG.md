# AI_CONTEXT_LOG.md
## Footland Dashboard — Rolling AI Context & Change Log

> This file is **automatically appended** by `log_refresh()` in `app.py` every time the data refresh logic runs.  
> It serves as a handoff document for AI context continuity across sessions.

---

## Session Log

---

### [2026-04-23 10:36] — Initial Project Scaffold

**Agent:** Antigravity (Full-Stack Data Engineer)  
**Action:** Project initialization  

**Files Created:**
| File | Status | Notes |
|------|--------|-------|
| `PROJECT_OVERSIGHT.md` | ✅ Created | Scope, metrics, constraints |
| `APP_STRUCTURE.md` | ✅ Created | Full UI layout + data-flow spec |
| `AI_CONTEXT_LOG.md` | ✅ Created | This file |
| `config.py` | ✅ Created | Credentials + constants |
| `api_client.py` | ✅ Created | Meta Graph API client |
| `app.py` | ✅ Created | Main Streamlit application |
| `requirements.txt` | ✅ Created | Python dependencies |

**API Endpoints Targeted:**
| Endpoint | Platform | Status |
|----------|----------|--------|
| `/{page-id}/insights` | Facebook | 🟡 Pending first run |
| `/{page-id}/posts` | Facebook | 🟡 Pending first run |
| `/{page-id}/conversations` | Facebook | 🟡 Pending first run |
| `/{ig-user-id}/insights` | Instagram | 🟡 Pending first run |
| `/{ig-user-id}/media` | Instagram | 🟡 Pending first run |

**UI Components Status:**
| Component | Status |
|-----------|--------|
| Sidebar (platform + date selector) | ✅ Built |
| KPI Header Row | ✅ Built |
| Tab: Audience | ✅ Built |
| Tab: Engagement | ✅ Built |
| Tab: Visibility | ✅ Built |
| Tab: Top Content | ✅ Built |
| Tab: Community Management | ✅ Built |

**Known Constraints Applied:**
- Ad Account `act_765947885726761` is blocklisted in `api_client.py`
- All benchmark/paid endpoints are excluded
- `log_refresh()` function wired to auto-append this file on every data refresh

**Next Step for Handoff:**
1. Run `pip install -r requirements.txt`
2. Run `streamlit run app.py`
3. Verify API token returns `200 OK` on the health-check endpoint
4. If any metric returns `403`, check token permissions: `pages_read_engagement`, `instagram_basic`, `instagram_manage_insights`, `pages_show_list`
5. Update this log with first successful API response summary

---
<!-- AUTO-APPENDED ENTRIES BELOW THIS LINE -->

### [2026-04-23 09:46 UTC] — Data Refresh
- **Platform:** Facebook
- **Period:** Last 30 Days
- **Status:** ✅ Data Loaded
---

### [2026-04-23 09:46 UTC] — Data Refresh
- **Platform:** Facebook
- **Period:** Last 30 Days
- **Status:** ✅ Data Loaded
---

### [2026-04-23 09:48 UTC] — Data Refresh
- **Platform:** Facebook
- **Period:** Last 30 Days
- **Status:** ✅ Data Loaded
---

### [2026-04-23 09:50 UTC] — Data Refresh
- **Platform:** Instagram
- **Period:** Last 30 Days
- **Status:** ✅ Data Loaded
---

### [2026-04-23 09:53 UTC] — Data Refresh
- **Platform:** Facebook
- **Period:** Last 30 Days
- **Status:** ✅ Data Loaded
- **Notes:** Followers: 0, Posts: 0, Reach: 20580850
---

### [2026-04-23 09:56 UTC] — Data Refresh
- **Platform:** Instagram
- **Period:** Last 30 Days
- **Status:** ✅ Data Loaded
- **Notes:** Followers: 0, Posts: 0, Reach: 0
---

### [2026-04-23 10:01 UTC] — Data Refresh
- **Platform:** Instagram
- **Period:** Last 30 Days
- **Status:** 🔄 Manual Refresh Triggered
---

### [2026-04-23 10:05 UTC] — Data Refresh
- **Platform:** Instagram
- **Period:** Last 30 Days
- **Status:** ✅ Data Loaded
- **Notes:** Followers: 226393, Posts: 20, Reach: 13036530
---

### [2026-04-23 10:07 UTC] — Data Refresh
- **Platform:** Facebook
- **Period:** Last 30 Days
- **Status:** ✅ Data Loaded
- **Notes:** Followers: 0, Posts: 0, Reach: 20580850
---

### [2026-04-23 10:11 UTC] — Data Refresh
- **Platform:** Facebook
- **Period:** Last 30 Days
- **Status:** ✅ Data Loaded
- **Notes:** Followers: 0, Posts: 0, Reach: 20580850
---

### [2026-04-23 10:12 UTC] — Data Refresh
- **Platform:** Facebook
- **Period:** Last 30 Days
- **Status:** ✅ Data Loaded
- **Notes:** Followers: 0, Posts: 0, Reach: 20580850
---

### [2026-04-23 10:12 UTC] — Data Refresh
- **Platform:** Facebook
- **Period:** Last 30 Days
- **Status:** ✅ Data Loaded
- **Notes:** Followers: 0, Posts: 0, Reach: 20580850
---

### [2026-04-23 10:14 UTC] — Data Refresh
- **Platform:** Facebook
- **Period:** Last 30 Days
- **Status:** ✅ Data Loaded
- **Notes:** Followers: 500072, Posts: 0, Reach: 20580850
---

### [2026-04-23 10:21 UTC] — Data Refresh
- **Platform:** Facebook
- **Period:** Last 30 Days
- **Status:** 🔄 Manual Refresh Triggered
---

### [2026-04-23 10:23 UTC] — Data Refresh
- **Platform:** Facebook
- **Period:** Last 30 Days
- **Status:** ✅ Data Loaded
- **Notes:** Followers: 500073, Posts: 20, Reach: 20580948
---

### [2026-04-23 10:27 UTC] — Data Refresh
- **Platform:** Facebook
- **Period:** Last 30 Days
- **Status:** ✅ Data Loaded
- **Notes:** Followers: 500073, Posts: 20, Reach: 20580948
---

### [2026-04-23 10:28 UTC] — Data Refresh
- **Platform:** Facebook
- **Period:** Last 30 Days
- **Status:** ✅ Data Loaded
- **Notes:** Followers: 500073, Posts: 20, Reach: 20580948
---

### [2026-04-23 10:28 UTC] — Data Refresh
- **Platform:** Facebook
- **Period:** Last 30 Days
- **Status:** 🔄 Manual Refresh Triggered
---

### [2026-04-23 10:28 UTC] — Data Refresh
- **Platform:** Facebook
- **Period:** Last 30 Days
- **Status:** 🔄 Manual Refresh Triggered
---

### [2026-04-23 10:28 UTC] — Data Refresh
- **Platform:** Facebook
- **Period:** Last 30 Days
- **Status:** 🔄 Manual Refresh Triggered
---

### [2026-04-23 10:28 UTC] — Data Refresh
- **Platform:** Facebook
- **Period:** Last 30 Days
- **Status:** ✅ Data Loaded
- **Notes:** Followers: 500074, Posts: 20, Reach: 20580948
---

### [2026-04-23 10:37 UTC] — Data Refresh
- **Platform:** Facebook
- **Period:** Last 30 Days
- **Status:** ✅ Data Loaded
- **Notes:** Followers: 500075, Posts: 20, Reach: 20580948
---

### [2026-04-23 10:44 UTC] — Data Refresh
- **Platform:** Facebook
- **Period:** Last 30 Days
- **Status:** ✅ Data Loaded
- **Notes:** Followers: 500075, Posts: 20, Reach: 20580948
---

### [2026-04-23 10:48 UTC] — Data Refresh
- **Platform:** Facebook
- **Period:** Last 30 Days
- **Status:** ✅ Data Loaded
- **Notes:** Followers: 500075, Posts: 20, Reach: 20580948
---

### [2026-04-23 10:58 UTC] — Data Refresh
- **Platform:** Facebook
- **Period:** Last 30 Days
- **Status:** ✅ Data Loaded
- **Notes:** Followers: 500075, Posts: 20, Reach: 20580948
---

### [2026-04-23 10:59 UTC] — Data Refresh
- **Platform:** Facebook
- **Period:** Custom Range
- **Status:** ✅ Data Loaded
- **Notes:** Followers: 500075, Posts: 20, Reach: 20308090
---

### [2026-04-23 11:20 UTC] — Data Refresh
- **Platform:** Facebook
- **Period:** Last 30 Days
- **Status:** ✅ Data Loaded
- **Notes:** Followers: 500077, Posts: 43, Reach: 20581934
---

### [2026-04-23 11:20 UTC] — Data Refresh
- **Platform:** Facebook
- **Period:** Custom Range
- **Status:** 🔄 Manual Refresh Triggered
---

### [2026-04-23 11:21 UTC] — Data Refresh
- **Platform:** Facebook
- **Period:** Custom Range
- **Status:** ✅ Data Loaded
- **Notes:** Followers: 500077, Posts: 29, Reach: 20308090
---

### [2026-04-23 11:27 UTC] — Data Refresh
- **Platform:** Facebook
- **Period:** Last 30 Days
- **Status:** ✅ Data Loaded
- **Notes:** Followers: 500078, Posts: 43, Reach: 20581934
---

### [2026-04-23 11:28 UTC] — Data Refresh
- **Platform:** Facebook
- **Period:** Custom Range
- **Status:** ✅ Data Loaded
- **Notes:** Followers: 500077, Posts: 29, Reach: 20308090
---

### [2026-04-23 11:33 UTC] — Data Refresh
- **Platform:** Facebook
- **Period:** Custom Range
- **Status:** 🔄 Manual Refresh Triggered
---

### [2026-04-23 11:35 UTC] — Data Refresh
- **Platform:** Facebook
- **Period:** Custom Range
- **Status:** ✅ Data Loaded
- **Notes:** Followers: 500079, Posts: 29, Reach: 20308090
---

### [2026-04-23 11:38 UTC] — Data Refresh
- **Platform:** Facebook
- **Period:** Custom Range
- **Status:** 🔄 Manual Refresh Triggered
---

### [2026-04-23 11:39 UTC] — Data Refresh
- **Platform:** Facebook
- **Period:** Custom Range
- **Status:** ✅ Data Loaded
- **Notes:** Followers: 500079, Posts: 29, Reach: 20308090
---

### [2026-04-23 11:44 UTC] — Data Refresh
- **Platform:** Facebook
- **Period:** Custom Range
- **Status:** 🔄 Manual Refresh Triggered
---

### [2026-04-23 11:45 UTC] — Data Refresh
- **Platform:** Facebook
- **Period:** Custom Range
- **Status:** ✅ Data Loaded
- **Notes:** Followers: 500080, Posts: 29, Reach: 20308090
---

### [2026-04-23 11:58 UTC] — Data Refresh
- **Platform:** Facebook
- **Period:** Custom Range
- **Status:** 🔄 Manual Refresh Triggered
---

### [2026-04-23 11:59 UTC] — Data Refresh
- **Platform:** Facebook
- **Period:** Custom Range
- **Status:** ✅ Data Loaded
- **Notes:** Followers: 500080, Posts: 29, Reach: 20308090
---

### [2026-04-23 12:43 UTC] — Data Refresh
- **Platform:** Facebook
- **Period:** Custom Range
- **Status:** 🔄 Manual Refresh Triggered
---

### [2026-04-23 12:44 UTC] — Data Refresh
- **Platform:** Facebook
- **Period:** Custom Range
- **Status:** ✅ Data Loaded
- **Notes:** Followers: 500085, Posts: 29, Reach: 20308090
---

### [2026-04-23 13:08 UTC] — Data Refresh
- **Platform:** Facebook
- **Period:** Custom Range
- **Status:** 🔄 Manual Refresh Triggered
---

### [2026-04-23 13:09 UTC] — Data Refresh
- **Platform:** Facebook
- **Period:** Custom Range
- **Status:** ✅ Data Loaded
- **Notes:** Followers: 500086, Posts: 29, Reach: 20308090
---

### [2026-04-23 13:11 UTC] — Data Refresh
- **Platform:** Facebook
- **Period:** Custom Range
- **Status:** 🔄 Manual Refresh Triggered
---

### [2026-04-23 13:12 UTC] — Data Refresh
- **Platform:** Facebook
- **Period:** Custom Range
- **Status:** ✅ Data Loaded
- **Notes:** Followers: 500086, Posts: 29, Reach: 20308090
---

### [2026-04-23 13:13 UTC] — Data Refresh
- **Platform:** Facebook
- **Period:** Custom Range
- **Status:** 🔄 Manual Refresh Triggered
---

### [2026-04-23 13:15 UTC] — Data Refresh
- **Platform:** Facebook
- **Period:** Custom Range
- **Status:** ✅ Data Loaded
- **Notes:** Followers: 500086, Posts: 29, Reach: 20308090
---

### [2026-04-23 13:26 UTC] — Data Refresh
- **Platform:** Facebook
- **Period:** Custom Range
- **Status:** ✅ Data Loaded
- **Notes:** Followers: 500086, Posts: 29, Reach: 20308090
---

### [2026-04-23 13:30 UTC] — Data Refresh
- **Platform:** Facebook
- **Period:** Custom Range
- **Status:** 🔄 Manual Refresh Triggered
---

### [2026-04-23 13:31 UTC] — Data Refresh
- **Platform:** Facebook
- **Period:** Custom Range
- **Status:** ✅ Data Loaded
- **Notes:** Followers: 500087, Posts: 29, Reach: 20308090
---

### [2026-04-23 13:39 UTC] — Data Refresh
- **Platform:** Facebook
- **Period:** Custom Range
- **Status:** ✅ Data Loaded
- **Notes:** Followers: 500087, Posts: 29, Reach: 20308090
---

### [2026-04-23 13:43 UTC] — Data Refresh
- **Platform:** Facebook
- **Period:** Custom Range
- **Status:** ✅ Data Loaded
- **Notes:** Followers: 500089, Posts: 47, Reach: 26536681
---

### [2026-04-23 13:44 UTC] — Data Refresh
- **Platform:** Facebook
- **Period:** Custom Range
- **Status:** ✅ Data Loaded
- **Notes:** Followers: 500087, Posts: 29, Reach: 20308090
---

### [2026-04-23 13:59 UTC] — Data Refresh
- **Platform:** Facebook
- **Period:** Last 30 Days
- **Status:** ✅ Data Loaded
- **Notes:** Followers: 500089, Posts: 43, Reach: 20585796
---

### [2026-04-23 14:01 UTC] — Data Refresh
- **Platform:** Facebook
- **Period:** Custom Range
- **Status:** ✅ Data Loaded
- **Notes:** Followers: 500089, Posts: 29, Reach: 20308090
---

### [2026-04-23 14:08 UTC] — Data Refresh
- **Platform:** Facebook
- **Period:** Last 30 Days
- **Status:** ✅ Data Loaded
- **Notes:** Followers: 500089, Posts: 43, Reach: 20585796
---

### [2026-04-23 14:09 UTC] — Data Refresh
- **Platform:** Facebook
- **Period:** Custom Range
- **Status:** ✅ Data Loaded
- **Notes:** Followers: 500089, Posts: 43, Reach: 20585796
---

### [2026-04-23 14:09 UTC] — Data Refresh
- **Platform:** Facebook
- **Period:** Custom Range
- **Status:** ✅ Data Loaded
- **Notes:** Followers: 500089, Posts: 60, Reach: 36146067
---

### [2026-04-23 14:09 UTC] — Data Refresh
- **Platform:** Facebook
- **Period:** Custom Range
- **Status:** ✅ Data Loaded
- **Notes:** Followers: 500089, Posts: 29, Reach: 20308090
---

### [2026-04-23 14:09 UTC] — Data Refresh
- **Platform:** Facebook
- **Period:** Custom Range
- **Status:** 🔄 Manual Refresh Triggered
---

### [2026-04-23 14:14 UTC] — Data Refresh
- **Platform:** Facebook
- **Period:** Custom Range
- **Status:** ✅ Data Loaded
- **Notes:** Followers: 500090, Posts: 29, Reach: 20308090
---

### [2026-04-23 14:18 UTC] — Data Refresh
- **Platform:** Facebook
- **Period:** Custom Range
- **Status:** ✅ Data Loaded
- **Notes:** Followers: 500090, Posts: 29, Reach: 20308090
---

### [2026-04-23 14:26 UTC] — Data Refresh
- **Platform:** Facebook
- **Period:** Last 30 Days
- **Status:** ✅ Data Loaded
- **Notes:** Followers: 500090, Posts: 43, Reach: 20585796
---

### [2026-04-23 14:26 UTC] — Data Refresh
- **Platform:** Facebook
- **Period:** Custom Range
- **Status:** ✅ Data Loaded
- **Notes:** Followers: 500090, Posts: 43, Reach: 20585796
---

### [2026-04-23 14:26 UTC] — Data Refresh
- **Platform:** Facebook
- **Period:** Custom Range
- **Status:** ✅ Data Loaded
- **Notes:** Followers: 500090, Posts: 60, Reach: 36146067
---

### [2026-04-23 14:27 UTC] — Data Refresh
- **Platform:** Facebook
- **Period:** Custom Range
- **Status:** ✅ Data Loaded
- **Notes:** Followers: 500091, Posts: 29, Reach: 20308090
---

### [2026-04-23 14:32 UTC] — Data Refresh
- **Platform:** Facebook
- **Period:** Custom Range
- **Status:** ✅ Data Loaded
- **Notes:** Followers: 500092, Posts: 29, Reach: 20308090
---

### [2026-04-23 14:41 UTC] — Data Refresh
- **Platform:** Facebook
- **Period:** Custom Range
- **Status:** ✅ Data Loaded
- **Notes:** Followers: 500092, Posts: 29, Reach: 20308090
---

### [2026-04-23 14:57 UTC] — Data Refresh
- **Platform:** Instagram
- **Period:** Custom Range
- **Status:** ✅ Data Loaded
- **Notes:** Followers: 226394, Posts: 29, Reach: 10307545
---

### [2026-04-23 14:57 UTC] — Data Refresh
- **Platform:** Instagram
- **Period:** Custom Range
- **Status:** ✅ Data Loaded
- **Notes:** Followers: 226394, Posts: 29, Reach: 10307545
---

### [2026-04-23 15:06 UTC] — Data Refresh
- **Platform:** Facebook
- **Period:** Last 30 Days
- **Status:** ✅ Data Loaded
- **Notes:** Followers: 500095, Posts: 43, Reach: 20586990
---

### [2026-04-23 15:06 UTC] — Data Refresh
- **Platform:** Instagram
- **Period:** Last 30 Days
- **Status:** ✅ Data Loaded
- **Notes:** Followers: 226394, Posts: 43, Reach: 13037507
---

### [2026-04-23 15:06 UTC] — Data Refresh
- **Platform:** Instagram
- **Period:** Custom Range
- **Status:** ✅ Data Loaded
- **Notes:** Followers: 226394, Posts: 43, Reach: 13037507
---

### [2026-04-23 15:06 UTC] — Data Refresh
- **Platform:** Instagram
- **Period:** Custom Range
- **Status:** ✅ Data Loaded
- **Notes:** Followers: 226394, Posts: 29, Reach: 10307545
---

### [2026-04-23 15:12 UTC] — Data Refresh
- **Platform:** Instagram
- **Period:** Custom Range
- **Status:** 🔄 Manual Refresh Triggered
---

### [2026-04-23 15:17 UTC] — Data Refresh
- **Platform:** Instagram
- **Period:** Custom Range
- **Status:** 🔄 Manual Refresh Triggered
---

### [2026-04-23 15:21 UTC] — Data Refresh
- **Platform:** Facebook
- **Period:** Custom Range
- **Status:** ✅ Data Loaded
- **Notes:** Followers: 500098, Posts: 29, Reach: 20308090
---

### [2026-04-23 15:24 UTC] — Data Refresh
- **Platform:** Instagram
- **Period:** Custom Range
- **Status:** ✅ Data Loaded
- **Notes:** Followers: 226394, Posts: 29, Reach: 10307545
---

### [2026-04-23 15:25 UTC] — Data Refresh
- **Platform:** Facebook
- **Period:** Custom Range
- **Status:** ✅ Data Loaded
- **Notes:** Followers: 500098, Posts: 29, Reach: 20308090
---

### [2026-04-23 15:25 UTC] — Data Refresh
- **Platform:** Instagram
- **Period:** Custom Range
- **Status:** ✅ Data Loaded
- **Notes:** Followers: 226394, Posts: 29, Reach: 10307545
---

### [2026-04-23 15:30 UTC] — Data Refresh
- **Platform:** Facebook
- **Period:** Last 30 Days
- **Status:** ✅ Data Loaded
- **Notes:** Followers: 500098, Posts: 43, Reach: 20586990
---

### [2026-04-23 15:31 UTC] — Data Refresh
- **Platform:** Facebook
- **Period:** Custom Range
- **Status:** ✅ Data Loaded
- **Notes:** Followers: 500098, Posts: 43, Reach: 20586990
---

### [2026-04-23 15:31 UTC] — Data Refresh
- **Platform:** Facebook
- **Period:** Custom Range
- **Status:** ✅ Data Loaded
- **Notes:** Followers: 500098, Posts: 60, Reach: 36147261
---

### [2026-04-23 15:31 UTC] — Data Refresh
- **Platform:** Facebook
- **Period:** Custom Range
- **Status:** ✅ Data Loaded
- **Notes:** Followers: 500098, Posts: 29, Reach: 20308090
---

### [2026-04-23 15:31 UTC] — Data Refresh
- **Platform:** Facebook
- **Period:** Custom Range
- **Status:** 🔄 Manual Refresh Triggered
---

### [2026-04-23 15:32 UTC] — Data Refresh
- **Platform:** Facebook
- **Period:** Custom Range
- **Status:** ✅ Data Loaded
- **Notes:** Followers: 500099, Posts: 29, Reach: 20308090
---

### [2026-04-23 20:41 UTC] — Data Refresh
- **Platform:** Facebook
- **Period:** Last 30 Days
- **Status:** ✅ Data Loaded
- **Notes:** Followers: 500127, Posts: 43, Reach: 20587775
---

### [2026-04-23 20:43 UTC] — Data Refresh
- **Platform:** Facebook
- **Period:** Custom Range
- **Status:** ✅ Data Loaded
- **Notes:** Followers: 500122, Posts: 29, Reach: 20308090
---

### [2026-04-23 20:45 UTC] — Data Refresh
- **Platform:** Instagram
- **Period:** Custom Range
- **Status:** ✅ Data Loaded
- **Notes:** Followers: 226392, Posts: 29, Reach: 10307545
---

### [2026-04-26 08:01 UTC] — Data Refresh
- **Platform:** Facebook
- **Period:** Custom Range
- **Status:** ✅ Data Loaded
- **Notes:** Followers: 500222, Posts: 29, Reach: 20308090
---

### [2026-04-26 08:05 UTC] — Data Refresh
- **Platform:** Facebook
- **Period:** Custom Range
- **Status:** ✅ Data Loaded
- **Notes:** Followers: 500222, Posts: 29, Reach: 20308090
---

### [2026-04-26 08:24 UTC] — Data Refresh
- **Platform:** Facebook
- **Period:** Custom Range
- **Status:** 🔄 Manual Refresh Triggered
---

### [2026-04-26 08:25 UTC] — Data Refresh
- **Platform:** Facebook
- **Period:** Custom Range
- **Status:** ✅ Data Loaded
- **Notes:** Followers: 500222, Posts: 29, Reach: 6291846
---

### [2026-04-26 08:32 UTC] — Data Refresh
- **Platform:** Facebook
- **Period:** Custom Range
- **Status:** 🔄 Manual Refresh Triggered
---

### [2026-04-26 08:33 UTC] — Data Refresh
- **Platform:** Facebook
- **Period:** Custom Range
- **Status:** ✅ Data Loaded
- **Notes:** Followers: 500223, Posts: 29, Reach: 6291846
---

### [2026-04-26 08:40 UTC] — Data Refresh
- **Platform:** Facebook
- **Period:** Custom Range
- **Status:** ✅ Data Loaded
- **Notes:** Followers: 500223, Posts: 29, Reach: 6291846
---

### [2026-04-26 08:40 UTC] — Data Refresh
- **Platform:** Facebook
- **Period:** Custom Range
- **Status:** 🔄 Manual Refresh Triggered
---

### [2026-04-26 08:41 UTC] — Data Refresh
- **Platform:** Facebook
- **Period:** Custom Range
- **Status:** ✅ Data Loaded
- **Notes:** Followers: 500223, Posts: 31, Reach: 6291846
---

### [2026-04-26 08:53 UTC] — Data Refresh
- **Platform:** Facebook
- **Period:** Custom Range
- **Status:** 🔄 Manual Refresh Triggered
---

### [2026-04-26 08:54 UTC] — Data Refresh
- **Platform:** Facebook
- **Period:** Custom Range
- **Status:** ✅ Data Loaded
- **Notes:** Followers: 500221, Posts: 31, Reach: 6291846
---

### [2026-04-26 09:01 UTC] — Data Refresh
- **Platform:** Facebook
- **Period:** Custom Range
- **Status:** 🔄 Manual Refresh Triggered
---

### [2026-04-26 09:02 UTC] — Data Refresh
- **Platform:** Facebook
- **Period:** Custom Range
- **Status:** ✅ Data Loaded
- **Notes:** Followers: 500222, Posts: 31, Reach: 6291846
---

### [2026-04-26 09:05 UTC] — Data Refresh
- **Platform:** Facebook
- **Period:** Custom Range
- **Status:** 🔄 Manual Refresh Triggered
---

### [2026-04-26 09:06 UTC] — Data Refresh
- **Platform:** Facebook
- **Period:** Custom Range
- **Status:** ✅ Data Loaded
- **Notes:** Followers: 500222, Posts: 31, Reach: 6291846
---

### [2026-04-26 09:10 UTC] — Data Refresh
- **Platform:** Facebook
- **Period:** Custom Range
- **Status:** ✅ Data Loaded
- **Notes:** Followers: 500222, Posts: 31, Reach: 6291846
---

### [2026-04-26 09:10 UTC] — Data Refresh
- **Platform:** Facebook
- **Period:** Custom Range
- **Status:** 🔄 Manual Refresh Triggered
---

### [2026-04-26 09:15 UTC] — Data Refresh
- **Platform:** Facebook
- **Period:** Custom Range
- **Status:** 🔄 Manual Refresh Triggered
---

### [2026-04-26 09:20 UTC] — Data Refresh
- **Platform:** Facebook
- **Period:** Custom Range
- **Status:** ✅ Data Loaded
- **Notes:** Followers: 500223, Posts: 31, Reach: 6291846
---

### [2026-04-26 09:24 UTC] — Data Refresh
- **Platform:** Facebook
- **Period:** Last 30 Days
- **Status:** ✅ Data Loaded
- **Notes:** Followers: 500224, Posts: 41, Reach: 5673004
---

### [2026-04-26 09:25 UTC] — Data Refresh
- **Platform:** Facebook
- **Period:** Custom Range
- **Status:** ✅ Data Loaded
- **Notes:** Followers: 500223, Posts: 31, Reach: 6291846
---

### [2026-04-26 09:27 UTC] — Data Refresh
- **Platform:** Facebook
- **Period:** Custom Range
- **Status:** 🔄 Manual Refresh Triggered
---

### [2026-04-26 09:28 UTC] — Data Refresh
- **Platform:** Facebook
- **Period:** Custom Range
- **Status:** ✅ Data Loaded
- **Notes:** Followers: 500224, Posts: 29, Reach: 6291846
---

### [2026-04-26 09:33 UTC] — Data Refresh
- **Platform:** Facebook
- **Period:** Custom Range
- **Status:** ✅ Data Loaded
- **Notes:** Followers: 500224, Posts: 29, Reach: 6291846
---

### [2026-04-26 09:33 UTC] — Data Refresh
- **Platform:** Facebook
- **Period:** Custom Range
- **Status:** 🔄 Manual Refresh Triggered
---

### [2026-04-26 09:34 UTC] — Data Refresh
- **Platform:** Facebook
- **Period:** Custom Range
- **Status:** ✅ Data Loaded
- **Notes:** Followers: 500224, Posts: 31, Reach: 6291846
---

### [2026-04-26 09:36 UTC] — Data Refresh
- **Platform:** Facebook
- **Period:** Custom Range
- **Status:** ✅ Data Loaded
- **Notes:** Followers: 500224, Posts: 31, Reach: 6291846
---

### [2026-04-26 09:37 UTC] — Data Refresh
- **Platform:** Facebook
- **Period:** Custom Range
- **Status:** ✅ Data Loaded
- **Notes:** Followers: 500224, Posts: 27, Reach: 5507025
---

### [2026-04-26 09:38 UTC] — Data Refresh
- **Platform:** Facebook
- **Period:** Custom Range
- **Status:** ✅ Data Loaded
- **Notes:** Followers: 500224, Posts: 27, Reach: 5507025
---

### [2026-04-26 09:38 UTC] — Data Refresh
- **Platform:** Facebook
- **Period:** Custom Range
- **Status:** ✅ Data Loaded
- **Notes:** Followers: 500224, Posts: 31, Reach: 6291846
---

### [2026-04-26 09:45 UTC] — Data Refresh
- **Platform:** Facebook
- **Period:** Custom Range
- **Status:** 🔄 Manual Refresh Triggered
---

### [2026-04-26 09:46 UTC] — Data Refresh
- **Platform:** Facebook
- **Period:** Custom Range
- **Status:** ✅ Data Loaded
- **Notes:** Followers: 500224, Posts: 31, Reach: 6291846
---

### [2026-04-26 09:48 UTC] — Data Refresh
- **Platform:** Instagram
- **Period:** Custom Range
- **Status:** ✅ Data Loaded
- **Notes:** Followers: 226427, Posts: 31, Reach: 3039846
---

### [2026-04-26 09:48 UTC] — Data Refresh
- **Platform:** Facebook
- **Period:** Custom Range
- **Status:** ✅ Data Loaded
- **Notes:** Followers: 500224, Posts: 31, Reach: 6291846
---

### [2026-04-26 09:48 UTC] — Data Refresh
- **Platform:** Instagram
- **Period:** Custom Range
- **Status:** ✅ Data Loaded
- **Notes:** Followers: 226427, Posts: 31, Reach: 3039846
---

### [2026-04-26 09:54 UTC] — Data Refresh
- **Platform:** Instagram
- **Period:** Custom Range
- **Status:** 🔄 Manual Refresh Triggered
---

### [2026-04-26 09:56 UTC] — Data Refresh
- **Platform:** Instagram
- **Period:** Custom Range
- **Status:** ✅ Data Loaded
- **Notes:** Followers: 226426, Posts: 31, Reach: 3039846
---

### [2026-04-26 09:57 UTC] — Data Refresh
- **Platform:** Facebook
- **Period:** Custom Range
- **Status:** ✅ Data Loaded
- **Notes:** Followers: 500226, Posts: 31, Reach: 6291846
---

### [2026-04-26 09:57 UTC] — Data Refresh
- **Platform:** Instagram
- **Period:** Custom Range
- **Status:** ✅ Data Loaded
- **Notes:** Followers: 226426, Posts: 31, Reach: 3039846
---

### [2026-04-26 10:00 UTC] — Data Refresh
- **Platform:** Instagram
- **Period:** Custom Range
- **Status:** 🔄 Manual Refresh Triggered
---

### [2026-04-26 10:02 UTC] — Data Refresh
- **Platform:** Instagram
- **Period:** Custom Range
- **Status:** ✅ Data Loaded
- **Notes:** Followers: 226426, Posts: 31, Reach: 3039846
---

### [2026-04-26 10:03 UTC] — Data Refresh
- **Platform:** Facebook
- **Period:** Custom Range
- **Status:** ✅ Data Loaded
- **Notes:** Followers: 500226, Posts: 31, Reach: 6291846
---

### [2026-04-26 10:03 UTC] — Data Refresh
- **Platform:** Instagram
- **Period:** Custom Range
- **Status:** ✅ Data Loaded
- **Notes:** Followers: 226426, Posts: 31, Reach: 3039846
---

### [2026-04-26 10:10 UTC] — Data Refresh
- **Platform:** Instagram
- **Period:** Custom Range
- **Status:** 🔄 Manual Refresh Triggered
---

### [2026-04-26 10:13 UTC] — Data Refresh
- **Platform:** Instagram
- **Period:** Custom Range
- **Status:** ✅ Data Loaded
- **Notes:** Followers: 226427, Posts: 31, Reach: 3039846
---

### [2026-04-26 10:22 UTC] — Data Refresh
- **Platform:** Instagram
- **Period:** Custom Range
- **Status:** 🔄 Manual Refresh Triggered
---

### [2026-04-26 10:24 UTC] — Data Refresh
- **Platform:** Instagram
- **Period:** Custom Range
- **Status:** ✅ Data Loaded
- **Notes:** Followers: 226428, Posts: 29, Reach: 3019512
---

### [2026-04-26 10:29 UTC] — Data Refresh
- **Platform:** Instagram
- **Period:** Custom Range
- **Status:** 🔄 Manual Refresh Triggered
---

### [2026-04-26 10:31 UTC] — Data Refresh
- **Platform:** Instagram
- **Period:** Custom Range
- **Status:** ✅ Data Loaded
- **Notes:** Followers: 226428, Posts: 27, Reach: 2391146
---

### [2026-04-26 10:34 UTC] — Data Refresh
- **Platform:** Instagram
- **Period:** Custom Range
- **Status:** ✅ Data Loaded
- **Notes:** Followers: 226427, Posts: 31, Reach: 3039846
---

### [2026-04-26 10:36 UTC] — Data Refresh
- **Platform:** Instagram
- **Period:** Custom Range
- **Status:** 🔄 Manual Refresh Triggered
---

### [2026-04-26 10:40 UTC] — Data Refresh
- **Platform:** Instagram
- **Period:** Custom Range
- **Status:** ✅ Data Loaded
- **Notes:** Followers: 226427, Posts: 31, Reach: 3039846
---

### [2026-04-26 10:57 UTC] — Data Refresh
- **Platform:** Instagram
- **Period:** Custom Range
- **Status:** 🔄 Manual Refresh Triggered
---

### [2026-04-26 11:01 UTC] — Data Refresh
- **Platform:** Instagram
- **Period:** Custom Range
- **Status:** ✅ Data Loaded
- **Notes:** Followers: 226424, Posts: 31, Reach: 3039846
---

### [2026-04-26 11:01 UTC] — Data Refresh
- **Platform:** Instagram
- **Period:** Custom Range
- **Status:** 🔄 Manual Refresh Triggered
---

### [2026-04-26 11:04 UTC] — Data Refresh
- **Platform:** Instagram
- **Period:** Custom Range
- **Status:** ✅ Data Loaded
- **Notes:** Followers: 226425, Posts: 31, Reach: 3039846
---

### [2026-04-26 11:13 UTC] — Data Refresh
- **Platform:** Instagram
- **Period:** Custom Range
- **Status:** 🔄 Manual Refresh Triggered
---

### [2026-04-26 11:16 UTC] — Data Refresh
- **Platform:** Instagram
- **Period:** Custom Range
- **Status:** ✅ Data Loaded
- **Notes:** Followers: 226425, Posts: 31, Reach: 3039846
---

### [2026-04-26 11:26 UTC] — Data Refresh
- **Platform:** Instagram
- **Period:** Custom Range
- **Status:** 🔄 Manual Refresh Triggered
---

### [2026-04-26 11:30 UTC] — Data Refresh
- **Platform:** Instagram
- **Period:** Custom Range
- **Status:** ✅ Data Loaded
- **Notes:** Followers: 226425, Posts: 31, Reach: 3039846
---

### [2026-04-26 11:47 UTC] — Data Refresh
- **Platform:** Instagram
- **Period:** Custom Range
- **Status:** 🔄 Manual Refresh Triggered
---

### [2026-04-26 11:51 UTC] — Data Refresh
- **Platform:** Instagram
- **Period:** Custom Range
- **Status:** ✅ Data Loaded
- **Notes:** Followers: 226425, Posts: 31, Reach: 3039846
---

### [2026-04-26 11:51 UTC] — Data Refresh
- **Platform:** Facebook
- **Period:** Custom Range
- **Status:** ✅ Data Loaded
- **Notes:** Followers: 500231, Posts: 31, Reach: 6291846
---

### [2026-04-26 12:01 UTC] — Data Refresh
- **Platform:** Instagram
- **Period:** Custom Range
- **Status:** ✅ Data Loaded
- **Notes:** Followers: 226425, Posts: 31, Reach: 3039846
---

### [2026-04-26 12:01 UTC] — Data Refresh
- **Platform:** Instagram
- **Period:** Custom Range
- **Status:** 🔄 Manual Refresh Triggered
---

### [2026-04-26 12:04 UTC] — Data Refresh
- **Platform:** Instagram
- **Period:** Custom Range
- **Status:** ✅ Data Loaded
- **Notes:** Followers: 226425, Posts: 31, Reach: 3039846
---

### [2026-04-26 12:31 UTC] — Data Refresh
- **Platform:** Instagram
- **Period:** Custom Range
- **Status:** 🔄 Manual Refresh Triggered
---

### [2026-04-26 12:33 UTC] — Data Refresh
- **Platform:** Instagram
- **Period:** Custom Range
- **Status:** ✅ Data Loaded
- **Notes:** Followers: 226426, Posts: 31, Reach: 3039846
---

### [2026-04-26 12:35 UTC] — Data Refresh
- **Platform:** Instagram
- **Period:** Custom Range
- **Status:** 🔄 Manual Refresh Triggered
---

### [2026-04-26 12:37 UTC] — Data Refresh
- **Platform:** Instagram
- **Period:** Custom Range
- **Status:** ✅ Data Loaded
- **Notes:** Followers: 226426, Posts: 31, Reach: 3039846
---

### [2026-04-26 12:40 UTC] — Data Refresh
- **Platform:** Instagram
- **Period:** Custom Range
- **Status:** 🔄 Manual Refresh Triggered
---

### [2026-04-26 12:42 UTC] — Data Refresh
- **Platform:** Instagram
- **Period:** Custom Range
- **Status:** ✅ Data Loaded
- **Notes:** Followers: 226428, Posts: 31, Reach: 3039846
---

### [2026-04-26 12:47 UTC] — Data Refresh
- **Platform:** Facebook
- **Period:** Custom Range
- **Status:** ✅ Data Loaded
- **Notes:** Followers: 500240, Posts: 31, Reach: 6291846
---

### [2026-04-26 12:48 UTC] — Data Refresh
- **Platform:** Instagram
- **Period:** Custom Range
- **Status:** ✅ Data Loaded
- **Notes:** Followers: 226428, Posts: 31, Reach: 3039846
---

### [2026-04-26 12:48 UTC] — Data Refresh
- **Platform:** Instagram
- **Period:** Custom Range
- **Status:** 🔄 Manual Refresh Triggered
---

### [2026-04-26 12:50 UTC] — Data Refresh
- **Platform:** Instagram
- **Period:** Custom Range
- **Status:** ✅ Data Loaded
- **Notes:** Followers: 226428, Posts: 31, Reach: 3039846
---

### [2026-04-26 12:54 UTC] — Data Refresh
- **Platform:** Instagram
- **Period:** Custom Range
- **Status:** 🔄 Manual Refresh Triggered
---

### [2026-04-26 12:56 UTC] — Data Refresh
- **Platform:** Instagram
- **Period:** Custom Range
- **Status:** ✅ Data Loaded
- **Notes:** Followers: 226427, Posts: 31, Reach: 3039846
---

### [2026-04-26 12:58 UTC] — Data Refresh
- **Platform:** Instagram
- **Period:** Custom Range
- **Status:** 🔄 Manual Refresh Triggered
---

### [2026-04-26 12:59 UTC] — Data Refresh
- **Platform:** Instagram
- **Period:** Custom Range
- **Status:** ✅ Data Loaded
- **Notes:** Followers: 226427, Posts: 31, Reach: 3039846
---

### [2026-04-26 13:10 UTC] — Data Refresh
- **Platform:** Facebook
- **Period:** Custom Range
- **Status:** ✅ Data Loaded
- **Notes:** Followers: 500243, Posts: 31, Reach: 6291846
---

### [2026-04-26 13:11 UTC] — Data Refresh
- **Platform:** Instagram
- **Period:** Custom Range
- **Status:** ✅ Data Loaded
- **Notes:** Followers: 226427, Posts: 31, Reach: 3039846
---

### [2026-04-26 13:14 UTC] — Data Refresh
- **Platform:** Instagram
- **Period:** Custom Range
- **Status:** 🔄 Manual Refresh Triggered
---

### [2026-04-26 13:16 UTC] — Data Refresh
- **Platform:** Instagram
- **Period:** Custom Range
- **Status:** ✅ Data Loaded
- **Notes:** Followers: 226426, Posts: 31, Reach: 3039846
---

### [2026-04-26 13:16 UTC] — Data Refresh
- **Platform:** Facebook
- **Period:** Custom Range
- **Status:** ✅ Data Loaded
- **Notes:** Followers: 500243, Posts: 31, Reach: 6291846
---

### [2026-04-26 13:18 UTC] — Data Refresh
- **Platform:** Facebook
- **Period:** Custom Range
- **Status:** 🔄 Manual Refresh Triggered
---

### [2026-04-26 13:19 UTC] — Data Refresh
- **Platform:** Facebook
- **Period:** Custom Range
- **Status:** ✅ Data Loaded
- **Notes:** Followers: 500243, Posts: 31, Reach: 6291846
---

### [2026-04-26 13:19 UTC] — Data Refresh
- **Platform:** Facebook
- **Period:** Custom Range
- **Status:** 🔄 Manual Refresh Triggered
---

### [2026-04-26 13:20 UTC] — Data Refresh
- **Platform:** Facebook
- **Period:** Custom Range
- **Status:** ✅ Data Loaded
- **Notes:** Followers: 500243, Posts: 31, Reach: 6291846
---

### [2026-04-26 13:21 UTC] — Data Refresh
- **Platform:** Instagram
- **Period:** Custom Range
- **Status:** ✅ Data Loaded
- **Notes:** Followers: 226425, Posts: 31, Reach: 3039846
---

### [2026-04-26 13:30 UTC] — Data Refresh
- **Platform:** Instagram
- **Period:** Custom Range
- **Status:** 🔄 Manual Refresh Triggered
---

### [2026-04-26 13:31 UTC] — Data Refresh
- **Platform:** Instagram
- **Period:** Custom Range
- **Status:** ✅ Data Loaded
- **Notes:** Followers: 226427, Posts: 31, Reach: 3039846
---

### [2026-04-26 13:33 UTC] — Data Refresh
- **Platform:** Facebook
- **Period:** Custom Range
- **Status:** ✅ Data Loaded
- **Notes:** Followers: 500244, Posts: 31, Reach: 6291846
---

### [2026-04-26 13:45 UTC] — Data Refresh
- **Platform:** Facebook
- **Period:** Custom Range
- **Status:** 🔄 Manual Refresh Triggered
---

### [2026-04-26 13:46 UTC] — Data Refresh
- **Platform:** Facebook
- **Period:** Custom Range
- **Status:** ✅ Data Loaded
- **Notes:** Followers: 500244, Posts: 31, Reach: 6291846
---

### [2026-04-26 13:57 UTC] — Data Refresh
- **Platform:** Facebook
- **Period:** Custom Range
- **Status:** ✅ Data Loaded
- **Notes:** Followers: 500244, Posts: 64, Reach: 5675279
---

### [2026-04-26 13:58 UTC] — Data Refresh
- **Platform:** Facebook
- **Period:** Custom Range
- **Status:** ✅ Data Loaded
- **Notes:** Followers: 500244, Posts: 31, Reach: 6291846
---

### [2026-04-26 14:00 UTC] — Data Refresh
- **Platform:** Instagram
- **Period:** Custom Range
- **Status:** ✅ Data Loaded
- **Notes:** Followers: 226430, Posts: 31, Reach: 3039846
---

### [2026-04-26 14:07 UTC] — Data Refresh
- **Platform:** Facebook
- **Period:** Custom Range
- **Status:** ✅ Data Loaded
- **Notes:** Followers: 500244, Posts: 31, Reach: 6291846
---

### [2026-04-26 15:53 UTC] — Data Refresh
- **Platform:** Facebook
- **Period:** Last 30 Days
- **Status:** ✅ Data Loaded
- **Notes:** Followers: 500248, Posts: 41, Reach: 5675279
---

### [2026-04-26 15:53 UTC] — Data Refresh
- **Platform:** Facebook
- **Period:** Custom Range
- **Status:** ✅ Data Loaded
- **Notes:** Followers: 500248, Posts: 31, Reach: 6291846
---

### [2026-04-26 16:02 UTC] — Data Refresh
- **Platform:** Facebook
- **Period:** Last 30 Days
- **Status:** ✅ Data Loaded
- **Notes:** Followers: 500248, Posts: 41, Reach: 5675279
---

### [2026-04-26 16:02 UTC] — Data Refresh
- **Platform:** Facebook
- **Period:** Custom Range
- **Status:** ✅ Data Loaded
- **Notes:** Followers: 500248, Posts: 41, Reach: 5675279
---

### [2026-04-26 16:02 UTC] — Data Refresh
- **Platform:** Facebook
- **Period:** Custom Range
- **Status:** ✅ Data Loaded
- **Notes:** Followers: 500248, Posts: 64, Reach: 5675279
---

### [2026-04-26 16:02 UTC] — Data Refresh
- **Platform:** Facebook
- **Period:** Custom Range
- **Status:** ✅ Data Loaded
- **Notes:** Followers: 500248, Posts: 31, Reach: 6291846
---

### [2026-04-26 16:05 UTC] — Data Refresh
- **Platform:** Facebook
- **Period:** Custom Range
- **Status:** 🔄 Manual Refresh Triggered
---

### [2026-04-26 16:06 UTC] — Data Refresh
- **Platform:** Facebook
- **Period:** Custom Range
- **Status:** ✅ Data Loaded
- **Notes:** Followers: 500249, Posts: 31, Reach: 6291846
---

### [2026-04-26 16:09 UTC] — Data Refresh
- **Platform:** Facebook
- **Period:** Custom Range
- **Status:** 🔄 Manual Refresh Triggered
---

### [2026-04-26 16:10 UTC] — Data Refresh
- **Platform:** Facebook
- **Period:** Custom Range
- **Status:** ✅ Data Loaded
- **Notes:** Followers: 500249, Posts: 31, Reach: 6291846
---

### [2026-04-27 22:58 UTC] — Data Refresh
- **Platform:** Facebook
- **Period:** Custom Range
- **Status:** 🔄 Manual Refresh Triggered
---

### [2026-04-27 23:02 UTC] — Data Refresh
- **Platform:** Facebook
- **Period:** Custom Range
- **Status:** ✅ Data Loaded
- **Notes:** Followers: 500719, Posts: 31, Reach: 6291846
---

### [2026-04-27 23:13 UTC] — Data Refresh
- **Platform:** Facebook
- **Period:** Custom Range
- **Status:** ✅ Data Loaded
- **Notes:** Followers: 500719, Posts: 31, Reach: 6291846
---

### [2026-04-27 23:13 UTC] — Data Refresh
- **Platform:** Facebook
- **Period:** Custom Range
- **Status:** ✅ Data Loaded
- **Notes:** Followers: 500729, Posts: 41, Reach: 5841400
---

### [2026-04-27 23:14 UTC] — Data Refresh
- **Platform:** Facebook
- **Period:** Custom Range
- **Status:** ✅ Data Loaded
- **Notes:** Followers: 500729, Posts: 66, Reach: 5841400
---

### [2026-04-27 23:14 UTC] — Data Refresh
- **Platform:** Facebook
- **Period:** Custom Range
- **Status:** ✅ Data Loaded
- **Notes:** Followers: 500719, Posts: 31, Reach: 6291846
---

### [2026-04-27 23:14 UTC] — Data Refresh
- **Platform:** Facebook
- **Period:** Custom Range
- **Status:** 🔄 Manual Refresh Triggered
---

### [2026-04-27 23:14 UTC] — Data Refresh
- **Platform:** Facebook
- **Period:** Custom Range
- **Status:** 🔄 Manual Refresh Triggered
---

### [2026-04-27 23:15 UTC] — Data Refresh
- **Platform:** Facebook
- **Period:** Custom Range
- **Status:** ✅ Data Loaded
- **Notes:** Followers: 500729, Posts: 31, Reach: 6291846
---

### [2026-04-27 23:23 UTC] — Data Refresh
- **Platform:** Facebook
- **Period:** Custom Range
- **Status:** ✅ Data Loaded
- **Notes:** Followers: 500729, Posts: 31, Reach: 6291846
---

### [2026-04-27 23:24 UTC] — Data Refresh
- **Platform:** Facebook
- **Period:** Custom Range
- **Status:** 🔄 Manual Refresh Triggered
---

### [2026-04-27 23:31 UTC] — Data Refresh
- **Platform:** Facebook
- **Period:** Last 30 Days
- **Status:** ✅ Data Loaded
- **Notes:** Followers: 0, Posts: 41, Reach: 5841400
---

### [2026-04-27 23:31 UTC] — Data Refresh
- **Platform:** Facebook
- **Period:** Last 30 Days
- **Status:** ✅ Data Loaded
- **Notes:** Followers: 0, Posts: 41, Reach: 5841400
---

### [2026-04-27 23:32 UTC] — Data Refresh
- **Platform:** Facebook
- **Period:** Custom Range
- **Status:** ✅ Data Loaded
- **Notes:** Followers: 500731, Posts: 31, Reach: 6291846
---

### [2026-04-27 23:44 UTC] — Data Refresh
- **Platform:** Facebook
- **Period:** Custom Range
- **Status:** ✅ Data Loaded
- **Notes:** Followers: 500738, Posts: 31, Reach: 6291846
---

### [2026-04-27 23:44 UTC] — Data Refresh
- **Platform:** Facebook
- **Period:** Last 30 Days
- **Status:** ✅ Data Loaded
- **Notes:** Followers: 500738, Posts: 41, Reach: 5841400
---

### [2026-04-28 07:40 UTC] — Data Refresh
- **Platform:** Facebook
- **Period:** Custom Range
- **Status:** 🔄 Manual Refresh Triggered
---

### [2026-04-28 07:40 UTC] — Data Refresh
- **Platform:** Facebook
- **Period:** Custom Range
- **Status:** 🔄 Manual Refresh Triggered
---

### [2026-04-28 07:41 UTC] — Data Refresh
- **Platform:** Facebook
- **Period:** Custom Range
- **Status:** ✅ Data Loaded
- **Notes:** Followers: 500771, Posts: 31, Reach: 6291846
---

### [2026-04-28 07:47 UTC] — Data Refresh
- **Platform:** Facebook
- **Period:** Custom Range
- **Status:** 🔄 Manual Refresh Triggered
---

### [2026-04-28 07:48 UTC] — Data Refresh
- **Platform:** Facebook
- **Period:** Custom Range
- **Status:** ✅ Data Loaded
- **Notes:** Followers: 500771, Posts: 31, Reach: 6291846
---

### [2026-04-28 07:49 UTC] — Data Refresh
- **Platform:** Facebook
- **Period:** Custom Range
- **Status:** 🔄 Manual Refresh Triggered
---

### [2026-04-28 07:49 UTC] — Data Refresh
- **Platform:** Facebook
- **Period:** Custom Range
- **Status:** 🔄 Manual Refresh Triggered
---

### [2026-04-28 07:51 UTC] — Data Refresh
- **Platform:** Facebook
- **Period:** Custom Range
- **Status:** ✅ Data Loaded
- **Notes:** Followers: 500771, Posts: 31, Reach: 6291846
---

### [2026-04-28 07:53 UTC] — Data Refresh
- **Platform:** Facebook
- **Period:** Custom Range
- **Status:** ✅ Data Loaded
- **Notes:** Followers: 500771, Posts: 31, Reach: 6291846
---

### [2026-04-28 07:53 UTC] — Data Refresh
- **Platform:** Facebook
- **Period:** Custom Range
- **Status:** ✅ Data Loaded
- **Notes:** Followers: 500771, Posts: 31, Reach: 6291846
---

### [2026-04-28 07:53 UTC] — Data Refresh
- **Platform:** Facebook
- **Period:** Custom Range
- **Status:** ✅ Data Loaded
- **Notes:** Followers: 500771, Posts: 31, Reach: 6291846
---

### [2026-04-28 07:54 UTC] — Data Refresh
- **Platform:** Instagram
- **Period:** Custom Range
- **Status:** ✅ Data Loaded
- **Notes:** Followers: 226513, Posts: 31, Reach: 3039846
---

### [2026-04-28 08:02 UTC] — Data Refresh
- **Platform:** Facebook
- **Period:** Custom Range
- **Status:** ✅ Data Loaded
- **Notes:** Followers: 500771, Posts: 31, Reach: 6291846
---

### [2026-04-28 08:08 UTC] — Data Refresh
- **Platform:** Facebook
- **Period:** Custom Range
- **Status:** 🔄 Manual Refresh Triggered
---

### [2026-04-28 08:09 UTC] — Data Refresh
- **Platform:** Facebook
- **Period:** Custom Range
- **Status:** ✅ Data Loaded
- **Notes:** Followers: 500772, Posts: 31, Reach: 6291846
---

### [2026-04-28 08:15 UTC] — Data Refresh
- **Platform:** Facebook
- **Period:** Custom Range
- **Status:** 🔄 Manual Refresh Triggered
---

### [2026-04-28 08:17 UTC] — Data Refresh
- **Platform:** Facebook
- **Period:** Custom Range
- **Status:** ✅ Data Loaded
- **Notes:** Followers: 500771, Posts: 31, Reach: 6291846
---

### [2026-04-28 08:18 UTC] — Data Refresh
- **Platform:** Facebook
- **Period:** Custom Range
- **Status:** ✅ Data Loaded
- **Notes:** Followers: 500771, Posts: 31, Reach: 6291846
---

### [2026-04-28 08:18 UTC] — Data Refresh
- **Platform:** Facebook
- **Period:** Custom Range
- **Status:** 🔄 Manual Refresh Triggered
---

### [2026-04-28 08:21 UTC] — Data Refresh
- **Platform:** Facebook
- **Period:** Custom Range
- **Status:** ✅ Data Loaded
- **Notes:** Followers: 500771, Posts: 31, Reach: 6291846
---

### [2026-04-28 08:24 UTC] — Data Refresh
- **Platform:** Instagram
- **Period:** Custom Range
- **Status:** ✅ Data Loaded
- **Notes:** Followers: 226512, Posts: 31, Reach: 3039846
---

### [2026-04-28 08:25 UTC] — Data Refresh
- **Platform:** Instagram
- **Period:** Custom Range
- **Status:** ✅ Data Loaded
- **Notes:** Followers: 226512, Posts: 31, Reach: 3039846
---

### [2026-04-28 08:25 UTC] — Data Refresh
- **Platform:** Instagram
- **Period:** Custom Range
- **Status:** 🔄 Manual Refresh Triggered
---

### [2026-04-28 08:27 UTC] — Data Refresh
- **Platform:** Instagram
- **Period:** Custom Range
- **Status:** ✅ Data Loaded
- **Notes:** Followers: 226512, Posts: 31, Reach: 3039846
---

### [2026-04-28 08:30 UTC] — Data Refresh
- **Platform:** Facebook
- **Period:** Custom Range
- **Status:** ✅ Data Loaded
- **Notes:** Followers: 500771, Posts: 31, Reach: 6291846
---

### [2026-04-28 08:46 UTC] — Data Refresh
- **Platform:** Facebook
- **Period:** Custom Range
- **Status:** 🔄 Manual Refresh Triggered
---

### [2026-04-28 08:49 UTC] — Data Refresh
- **Platform:** Facebook
- **Period:** Custom Range
- **Status:** ✅ Data Loaded
- **Notes:** Followers: 500771, Posts: 31, Reach: 6291846
---

### [2026-04-28 09:03 UTC] — Data Refresh
- **Platform:** Facebook
- **Period:** Custom Range
- **Status:** 🔄 Manual Refresh Triggered
---

### [2026-04-28 09:07 UTC] — Data Refresh
- **Platform:** Facebook
- **Period:** Custom Range
- **Status:** ✅ Data Loaded
- **Notes:** Followers: 500772, Posts: 31, Reach: 6291846
---

### [2026-04-28 09:11 UTC] — Data Refresh
- **Platform:** Facebook
- **Period:** Custom Range
- **Status:** 🔄 Manual Refresh Triggered
---

### [2026-04-28 09:13 UTC] — Data Refresh
- **Platform:** Facebook
- **Period:** Custom Range
- **Status:** ✅ Data Loaded
- **Notes:** Followers: 500772, Posts: 31, Reach: 6291846
---

### [2026-04-28 09:27 UTC] — Data Refresh
- **Platform:** Facebook
- **Period:** Custom Range
- **Status:** 🔄 Manual Refresh Triggered
---

### [2026-04-28 09:29 UTC] — Data Refresh
- **Platform:** Facebook
- **Period:** Custom Range
- **Status:** ✅ Data Loaded
- **Notes:** Followers: 500772, Posts: 31, Reach: 6291846
---

### [2026-04-28 09:34 UTC] — Data Refresh
- **Platform:** Facebook
- **Period:** Custom Range
- **Status:** 🔄 Manual Refresh Triggered
---

### [2026-04-28 09:35 UTC] — Data Refresh
- **Platform:** Facebook
- **Period:** Custom Range
- **Status:** ✅ Data Loaded
- **Notes:** Followers: 500772, Posts: 0, Reach: 6291846
---

### [2026-04-28 09:42 UTC] — Data Refresh
- **Platform:** Facebook
- **Period:** Custom Range
- **Status:** 🔄 Manual Refresh Triggered
---

### [2026-04-28 09:43 UTC] — Data Refresh
- **Platform:** Facebook
- **Period:** Custom Range
- **Status:** ✅ Data Loaded
- **Notes:** Followers: 500772, Posts: 31, Reach: 6291846
---

### [2026-04-28 09:49 UTC] — Data Refresh
- **Platform:** Facebook
- **Period:** Custom Range
- **Status:** 🔄 Manual Refresh Triggered
---

### [2026-04-28 09:50 UTC] — Data Refresh
- **Platform:** Facebook
- **Period:** Custom Range
- **Status:** ✅ Data Loaded
- **Notes:** Followers: 500773, Posts: 31, Reach: 6291846
---
