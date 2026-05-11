"""
components/skeleton.py — Shimmer skeleton loading cards.

Usage:
    _skel = st.empty()
    _skel.markdown(skeleton_dashboard_html(), unsafe_allow_html=True)

    data = fetch_all(...)   # blocking fetch

    _skel.empty()           # wipe skeleton — single element, clears reliably
    render_real_content(data)
"""

import streamlit as st

_CSS = """
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
</style>
"""

def _kpi_row_html(n: int) -> str:
    tiles = "".join(
        f'<div class="skel-block" style="flex:1;min-width:0;height:88px;border-radius:10px;"></div>'
        for _ in range(n)
    )
    return f'<div style="display:flex;gap:12px;margin-bottom:12px;">{tiles}</div>'

def _chart_html() -> str:
    return '<div class="skel-block" style="height:220px;border-radius:10px;margin:8px 0 16px;"></div>'

def _card_row_html(n: int) -> str:
    cards = "".join(
        f'<div class="skel-block" style="flex:1;min-width:0;height:260px;border-radius:10px;"></div>'
        for _ in range(n)
    )
    return f'<div style="display:flex;gap:12px;margin-bottom:12px;">{cards}</div>'

def _tab_bar_html() -> str:
    return '<div class="skel-block" style="height:36px;border-radius:8px;max-width:420px;margin-bottom:16px;"></div>'


# ── Public HTML builders (single string → single st.empty().markdown()) ───────

def skeleton_dashboard_html(n_kpis: int = 5) -> str:
    return (
        _CSS
        + _kpi_row_html(n_kpis)
        + _chart_html()
        + _kpi_row_html(4)
        + _chart_html()
        + _card_row_html(3)
    )

def skeleton_boost_html() -> str:
    return (
        _CSS
        + _kpi_row_html(4)
        + _kpi_row_html(4)
        + _chart_html()
        + _card_row_html(3)
    )

def skeleton_charts_html(n_charts: int = 2, n_cards: int = 3) -> str:
    charts = "".join(_chart_html() for _ in range(n_charts))
    return _CSS + _tab_bar_html() + charts + _card_row_html(n_cards)


# ── Convenience wrappers (for Boost tab in app.py) ────────────────────────────

def render_skeleton_boost():
    _skel = st.empty()
    _skel.markdown(skeleton_boost_html(), unsafe_allow_html=True)
    return _skel
