"""
components/skeleton.py — Shimmer skeleton loading cards.

Usage:
    _skel = st.empty()
    with _skel.container():
        render_skeleton_dashboard()   # or render_skeleton_boost()

    data = fetch_all(...)             # blocking fetch

    _skel.empty()                     # wipe skeleton
    render_real_content(data)         # draw real UI
"""

import streamlit as st

# ── Shared shimmer CSS (injected once per page load) ─────────────────────────
_SHIMMER_CSS = """
<style>
@keyframes _skel_shimmer {
  0%   { background-position: -700px 0; }
  100% { background-position:  700px 0; }
}
.skel-block {
  background: linear-gradient(90deg,
    rgba(255,255,255,0.06) 25%,
    rgba(255,255,255,0.13) 50%,
    rgba(255,255,255,0.06) 75%
  );
  background-size: 700px 100%;
  animation: _skel_shimmer 1.4s infinite linear;
  border-radius: 10px;
}
.skel-kpi {
  height: 88px;
  margin-bottom: 4px;
}
.skel-chart {
  height: 220px;
  margin: 8px 0 16px;
}
.skel-card {
  height: 260px;
  margin-bottom: 8px;
}
.skel-row {
  display: flex;
  gap: 12px;
  margin-bottom: 12px;
}
.skel-row .skel-block {
  flex: 1;
}
</style>
"""


def _inject_css():
    st.markdown(_SHIMMER_CSS, unsafe_allow_html=True)


def _kpi_row(n: int = 4):
    """Render a row of n shimmer KPI tiles."""
    cols = "".join(
        '<div class="skel-block skel-kpi" style="flex:1;min-width:0;"></div>'
        for _ in range(n)
    )
    st.markdown(
        f'<div class="skel-row">{cols}</div>',
        unsafe_allow_html=True,
    )


def _chart_block():
    st.markdown('<div class="skel-block skel-chart"></div>', unsafe_allow_html=True)


def _card_row(n: int = 3):
    cols = "".join(
        '<div class="skel-block skel-card" style="flex:1;min-width:0;"></div>'
        for _ in range(n)
    )
    st.markdown(
        f'<div class="skel-row">{cols}</div>',
        unsafe_allow_html=True,
    )


# ── Public helpers ─────────────────────────────────────────────────────────────

def render_skeleton_dashboard(n_kpis: int = 5):
    """
    Generic dashboard skeleton: a KPI row, a chart block, and a card row.
    Works for both Facebook and Instagram dashboards.
    """
    _inject_css()
    _kpi_row(n_kpis)
    _chart_block()
    _kpi_row(4)
    _chart_block()
    _card_row(3)


def render_skeleton_boost():
    """Skeleton for the Boost tab (two KPI rows + chart)."""
    _inject_css()
    _kpi_row(4)
    _kpi_row(4)
    _chart_block()
    _card_row(3)
