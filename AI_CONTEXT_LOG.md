# AI_CONTEXT_LOG.md
## Skechers Dashboard — Rolling AI Context & Change Log

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

<!-- Older auto-appended entries (2026-04-23 to 2026-05-06, ~350 entries) trimmed to keep file size manageable. -->

---

### [2026-05-06 09:53 UTC] — Data Refresh
- **Platform:** Facebook
- **Period:** Last 30 Days
- **Status:** ✅ Data Loaded
- **Notes:** Followers: 501264, Posts: 30, Reach: 6029395
---

### [2026-06-03 12:18 UTC] — Data Refresh
- **Platform:** Facebook
- **Period:** Last 30 Days
- **Status:** ✅ Data Loaded
- **Notes:** Followers: 0, Posts: 0, Reach: 0
---

### [2026-06-03 13:17 UTC] — Data Refresh
- **Platform:** Facebook
- **Period:** Last 30 Days
- **Status:** ✅ Data Loaded
- **Notes:** Followers: 9043177, Posts: 16, Reach: 3512467
---

### [2026-06-03 13:22 UTC] — Data Refresh
- **Platform:** Instagram
- **Period:** Last 30 Days
- **Status:** ✅ Data Loaded
- **Notes:** Followers: 127580, Posts: 16, Reach: 1960957
---

### [2026-06-03 13:22 UTC] — Data Refresh
- **Platform:** Facebook
- **Period:** Last 30 Days
- **Status:** ✅ Data Loaded
- **Notes:** Followers: 9043177, Posts: 16, Reach: 3512467
---

### [2026-06-03 13:22 UTC] — Data Refresh
- **Platform:** Instagram
- **Period:** Last 30 Days
- **Status:** ✅ Data Loaded
- **Notes:** Followers: 127580, Posts: 16, Reach: 1960957
---

### [2026-06-03 13:46 UTC] — Data Refresh
- **Platform:** Boost
- **Period:** Last 30 Days
- **Status:** 🔄 Manual Refresh Triggered
---

### [2026-06-03 13:48 UTC] — Data Refresh
- **Platform:** Facebook
- **Period:** Last 30 Days
- **Status:** ✅ Data Loaded
- **Notes:** Followers: 9042992, Posts: 16, Reach: 3512467
---

### [2026-06-03 14:07 UTC] — Data Refresh
- **Platform:** Facebook
- **Period:** Last 30 Days
- **Status:** ✅ Data Loaded
- **Notes:** Followers: 9043146, Posts: 16, Reach: 3512467
---

### [2026-06-03 14:18 UTC] — Data Refresh
- **Platform:** Facebook
- **Period:** Last 30 Days
- **Status:** ✅ Data Loaded
- **Notes:** Followers: 9043146, Posts: 16, Reach: 3512467
---

### [2026-06-03 14:25 UTC] — Data Refresh
- **Platform:** Facebook
- **Period:** Last 30 Days
- **Status:** ✅ Data Loaded
- **Notes:** Followers: 9043146, Posts: 16, Reach: 3512467
---

### [2026-06-03 14:28 UTC] — Data Refresh
- **Platform:** Facebook
- **Period:** Last 30 Days
- **Status:** ✅ Data Loaded
- **Notes:** Followers: 9042135, Posts: 16, Reach: 3512467
---

### [2026-06-03 14:32 UTC] — Data Refresh
- **Platform:** Facebook
- **Period:** Last 30 Days
- **Status:** ✅ Data Loaded
- **Notes:** Followers: 9042135, Posts: 16, Reach: 3512467
---

### [2026-06-03 14:36 UTC] — Data Refresh
- **Platform:** Facebook
- **Period:** Last 30 Days
- **Status:** ✅ Data Loaded
- **Notes:** Followers: 9042135, Posts: 16, Reach: 3512467
---

### [2026-06-03 14:41 UTC] — Data Refresh
- **Platform:** Facebook
- **Period:** Last 30 Days
- **Status:** ✅ Data Loaded
- **Notes:** Followers: 9042135, Posts: 16, Reach: 3512467
---

### [2026-06-03 14:46 UTC] — Data Refresh
- **Platform:** Facebook
- **Period:** Last 30 Days
- **Status:** ✅ Data Loaded
- **Notes:** Followers: 9042135, Posts: 16, Reach: 3512467
---

### [2026-06-03 14:51 UTC] — Data Refresh
- **Platform:** Instagram
- **Period:** Last 30 Days
- **Status:** ✅ Data Loaded
- **Notes:** Followers: 127582, Posts: 16, Reach: 1960957
---

### [2026-06-03 14:52 UTC] — Data Refresh
- **Platform:** Facebook
- **Period:** Last 30 Days
- **Status:** ✅ Data Loaded
- **Notes:** Followers: 9042135, Posts: 16, Reach: 3512467
---
