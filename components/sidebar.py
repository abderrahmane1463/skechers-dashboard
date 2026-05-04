import base64
import pathlib
import streamlit as st
from datetime import datetime, timezone, timedelta

from config import PERIOD_DAYS
import db


@st.cache_data(ttl=900, show_spinner=False)
def _get_health():
    try:
        result = db.load_fetched_at("ig_profile", "2026-01-01", "2026-12-31")
        # Just check if Supabase responds — any response means connection is OK
        import requests, os
        from dotenv import load_dotenv
        load_dotenv()
        resp = requests.get(
            f"{os.environ['SUPABASE_URL']}/rest/v1/metric_cache",
            headers={"apikey": os.environ["SUPABASE_KEY"], "Authorization": f"Bearer {os.environ['SUPABASE_KEY']}"},
            params={"limit": "1", "select": "id"},
            timeout=5,
        )
        if resp.status_code == 200:
            return {"status": "ok", "name": "Supabase connecte"}
        return {"status": "error", "message": f"Supabase HTTP {resp.status_code}"}
    except Exception as e:
        return {"status": "error", "message": str(e)}


def render_sidebar(log_refresh_fn):
    """
    Renders the sidebar and returns (platform, days, start_date, end_date).
    log_refresh_fn is called when the user clicks Refresh.
    """
    with st.sidebar:
        _logo_path = pathlib.Path("assets/footland_logo.png")
        if _logo_path.exists():
            _logo_b64 = base64.b64encode(_logo_path.read_bytes()).decode()
            st.markdown(
                f'<div style="background:#fff;border-radius:12px;padding:12px 16px;'
                f'margin-bottom:8px;text-align:center;">'
                f'<img src="data:image/png;base64,{_logo_b64}" style="max-width:160px;width:100%;"/>'
                f'</div>',
                unsafe_allow_html=True
            )
        else:
            st.markdown('<div class="brand-header">⚽ Footland</div>', unsafe_allow_html=True)
        st.markdown('<div class="brand-sub">Organic Analytics Dashboard</div>', unsafe_allow_html=True)

        platform = st.radio("Platform", ["🔵 Facebook", "📸 Instagram", "🚀 Boost", "📖 Documentation"], label_visibility="collapsed")
        if "Facebook" in platform:
            platform = "Facebook"
        elif "Instagram" in platform:
            platform = "Instagram"
        elif "Boost" in platform:
            platform = "Boost"
        else:
            platform = "Documentation"

        period_options = list(PERIOD_DAYS.keys()) + ["Custom Range"]
        period_label = st.selectbox("Date Range", period_options, index=1)

        start_date, end_date = None, None
        if period_label == "Custom Range":
            today = datetime.now(timezone.utc).date()
            c1, c2 = st.columns(2)
            start_val = c1.date_input("Start", today - timedelta(days=30))
            end_val = c2.date_input("End", today)
            start_date, end_date = str(start_val), str(end_val)
            days = (end_val - start_val).days
        else:
            days = PERIOD_DAYS[period_label]

        if st.button("🔄 Refresh Data", width="stretch"):
            st.cache_data.clear()
            log_refresh_fn(platform, period_label, "🔄 Manual Refresh Triggered")
            st.rerun()

        # ── Theme toggle ──────────────────────────────────────────────────────
        if "theme" not in st.session_state:
            st.session_state.theme = "dark"

        _is_dark = st.session_state.theme == "dark"
        _toggle_label = "☀️ Mode Clair" if _is_dark else "🌙 Mode Sombre"
        if st.button(_toggle_label, width="stretch"):
            st.session_state.theme = "light" if _is_dark else "dark"
            st.rerun()

        st.divider()

        health = _get_health()
        if health.get("status") == "ok":
            st.success(f"✅ Base de donnees connectee")
        else:
            st.error(f"❌ Erreur\n\n{health.get('message', 'Unknown error')}")

        st.caption("Cache TTL: 15 min • Supabase")

        st.divider()

        user = st.session_state.get("user", {})
        st.caption(f"Connecté : {user.get('display_name') or user.get('email', '')}")
        if st.button("🚪 Se déconnecter", width="stretch"):
            del st.session_state["user"]
            st.rerun()

    return platform, period_label, days, start_date, end_date
