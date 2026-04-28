import base64
import pathlib
import streamlit as st
from datetime import datetime, timezone, timedelta

from config import PERIOD_DAYS
import api_client as api


@st.cache_data(ttl=900, show_spinner=False)
def _get_health():
    return api.check_api_health()


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

        platform = st.radio("Platform", ["🔵 Facebook", "📸 Instagram"], label_visibility="collapsed")
        platform = "Facebook" if "Facebook" in platform else "Instagram"

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

        st.divider()

        health = _get_health()
        if health.get("status") == "ok":
            st.success(f"✅ API Connected\n\n{health.get('name', '')}")
        else:
            st.error(f"❌ API Error\n\n{health.get('message', 'Unknown error')}")

        st.caption("Cache TTL: 15 min • Graph API v19.0")

    return platform, period_label, days, start_date, end_date
