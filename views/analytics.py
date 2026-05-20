"""
views/analytics.py — Google Analytics 4 dashboard tab.
"""
from __future__ import annotations

import streamlit as st


# ─── Shared helpers (mirrored from boost.py) ──────────────────────────────────
def _kpi_card(icon: str, label: str, value: str, color: str | None = None) -> str:
    _dark = st.session_state.get("theme", "dark") == "dark"
    _bg  = "rgba(255,255,255,0.05)" if _dark else "#ffffff"
    _brd = "none"                    if _dark else "1px solid #e5e7eb"
    _lc  = "rgba(255,255,255,0.45)" if _dark else "#6b7280"
    _vc  = color if color else ("#ffffff" if _dark else "#111827")
    return (
        f'<div style="background:{_bg};border:{_brd};border-radius:12px;'
        f'padding:0.9rem 1rem;text-align:center;">'
        f'<div style="font-size:0.72rem;color:{_lc};margin-bottom:0.25rem;">{icon} {label}</div>'
        f'<div style="font-size:1.3rem;font-weight:800;color:{_vc};white-space:nowrap;">{value}</div>'
        f'</div>'
    )


def _section_header(title: str):
    _brd = "rgba(255,255,255,0.15)"
    st.markdown(
        f'<div style="font-size:1.35rem;color:#ffffff;font-weight:700;'
        f'letter-spacing:0.05em;'
        f'margin:1.8rem 0 0.8rem;border-bottom:2px solid {_brd};'
        f'padding-bottom:0.5rem;">{title}</div>',
        unsafe_allow_html=True,
    )


def _no_data_banner(msg: str):
    _dark = st.session_state.get("theme", "dark") == "dark"
    _bg  = "rgba(255,165,0,0.08)"  if _dark else "rgba(255,165,0,0.12)"
    _tc  = "rgba(255,165,0,0.9)"   if _dark else "#92400e"
    st.markdown(
        f'<div style="background:{_bg};border:1px solid rgba(255,165,0,0.3);'
        f'border-radius:10px;padding:1rem 1.2rem;color:{_tc};'
        f'font-size:0.85rem;margin:0.5rem 0 1rem;">'
        f'⚠️ {msg}</div>',
        unsafe_allow_html=True,
    )


def _fmt_int(v: int) -> str:
    return f"{v:,}"


def _fmt_pct(v: float) -> str:
    return f"{v:.2f}%"


# ─── Section renderers ─────────────────────────────────────────────────────────
def _render_overview_kpis(ga4: dict):
    _section_header("📊 VUE D'ENSEMBLE")

    sessions  = ga4.get("sessions", 0)
    pageviews = ga4.get("page_views", 0)
    bounce    = ga4.get("bounce_rate", 0.0)
    duration  = ga4.get("avg_session_duration", 0.0)

    mins = int(duration) // 60
    secs = int(duration) % 60
    duration_str = f"{mins}m {secs:02d}s"

    row = f"""
<div style="display:grid;grid-template-columns:repeat(4,1fr);gap:0.6rem;margin-bottom:1rem;">
  {_kpi_card("👥", "Sessions", _fmt_int(sessions), "#7dd3fc")}
  {_kpi_card("📄", "Pages vues", _fmt_int(pageviews), "#a78bfa")}
  {_kpi_card("↩️", "Taux de rebond", _fmt_pct(bounce), "#f87171")}
  {_kpi_card("⏱️", "Durée moyenne", duration_str, "#4ade80")}
</div>"""
    st.markdown(row, unsafe_allow_html=True)


def _render_engagement_analysis(ga4: dict):
    _section_header("🧠 ANALYSE D'ENGAGEMENT")

    _dark  = st.session_state.get("theme", "dark") == "dark"
    _row_bg = "rgba(255,255,255,0.03)" if _dark else "#f8fafc"
    _lbl_c  = "rgba(255,255,255,0.75)" if _dark else "#111827"
    _txt_c  = "rgba(255,255,255,0.45)" if _dark else "#6b7280"

    bounce   = ga4.get("bounce_rate", 0.0)
    duration = ga4.get("avg_session_duration", 0.0)
    sessions = ga4.get("sessions", 0)
    pages    = ga4.get("page_views", 0)
    pps      = round(pages / sessions, 2) if sessions else 0.0

    insights: list[tuple[str, str, str]] = []

    # Bounce rate
    if bounce == 0:
        insights.append(("⚪", "Taux de rebond", "Données non disponibles."))
    elif bounce < 40:
        insights.append(("🟢", "Taux de rebond excellent", f"{_fmt_pct(bounce)} — visiteurs très engagés."))
    elif bounce < 60:
        insights.append(("🟡", "Taux de rebond correct", f"{_fmt_pct(bounce)} — dans la norme (40–60 %)."))
    else:
        insights.append(("🔴", "Taux de rebond élevé", f"{_fmt_pct(bounce)} — revoir l'expérience d'arrivée."))

    # Session duration
    if duration < 30:
        insights.append(("🔴", "Durée de session très courte", f"{int(duration)}s — les visiteurs repartent vite."))
    elif duration < 120:
        insights.append(("🟡", "Durée de session courte", f"{int(duration)}s — améliorer le contenu."))
    else:
        mins = int(duration) // 60
        secs = int(duration) % 60
        insights.append(("🟢", "Bonne durée de session", f"{mins}m {secs:02d}s — les visiteurs lisent le contenu."))

    # Pages per session
    if pps > 0:
        if pps >= 3:
            insights.append(("🟢", "Pages par session", f"{pps:.1f} — exploration active du site."))
        elif pps >= 1.5:
            insights.append(("🟡", "Pages par session", f"{pps:.1f} — navigation limitée."))
        else:
            insights.append(("🔴", "Pages par session", f"{pps:.1f} — peu de pages visitées par session."))

    rows_html = "".join(
        f'<div style="display:flex;align-items:flex-start;gap:0.6rem;'
        f'background:{_row_bg};border-radius:8px;'
        f'padding:0.55rem 0.8rem;margin-bottom:0.35rem;">'
        f'<span style="font-size:1rem;line-height:1.4;">{dot}</span>'
        f'<div><span style="font-size:0.78rem;font-weight:700;color:{_lbl_c};">{label}</span>'
        f'<span style="font-size:0.78rem;color:{_txt_c};"> — {text}</span></div>'
        f'</div>'
        for dot, label, text in insights
    )
    st.markdown(rows_html, unsafe_allow_html=True)


def _render_pages_per_session(ga4: dict):
    _section_header("📑 MÉTRIQUES CALCULÉES")

    sessions  = ga4.get("sessions", 0)
    pageviews = ga4.get("page_views", 0)
    bounce    = ga4.get("bounce_rate", 0.0)
    duration  = ga4.get("avg_session_duration", 0.0)

    pps          = round(pageviews / sessions, 2) if sessions else 0.0
    engaged_rate = round((1 - bounce / 100) * 100, 2)
    engaged_sess = int(sessions * (1 - bounce / 100))

    row = f"""
<div style="display:grid;grid-template-columns:repeat(3,1fr);gap:0.6rem;margin-bottom:1rem;">
  {_kpi_card("📑", "Pages / Session", f"{pps:.2f}", "#facc15")}
  {_kpi_card("✅", "Sessions engagées", _fmt_int(engaged_sess), "#4ade80")}
  {_kpi_card("💡", "Taux d'engagement", _fmt_pct(engaged_rate), "#7dd3fc")}
</div>"""
    st.markdown(row, unsafe_allow_html=True)


# ─── Public entry point ────────────────────────────────────────────────────────
def render_analytics_tab(ga4_data: dict, since: str = "", until: str = ""):
    """Render the full Google Analytics dashboard tab."""

    _dark  = st.session_state.get("theme", "dark") == "dark"
    _hdr_c = "#ffffff"                 if _dark else "#111827"
    _sub_c = "rgba(255,255,255,0.35)" if _dark else "#9ca3af"

    st.markdown(
        f'<p style="font-size:1.4rem;font-weight:800;letter-spacing:0.08em;'
        f'color:{_hdr_c};margin:0 0 0.2rem;">GOOGLE ANALYTICS 4</p>'
        f'<p style="font-size:0.8rem;color:{_sub_c};margin:0 0 1rem;">'
        f'Comportement des visiteurs sur le site · GA4</p>',
        unsafe_allow_html=True,
    )

    if not ga4_data:
        _no_data_banner(
            "Données Google Analytics non disponibles. "
            "Vérifiez que le token GA4 est configuré dans les secrets Streamlit."
        )
        return

    _render_overview_kpis(ga4_data)
    st.divider()
    _render_pages_per_session(ga4_data)
    st.divider()
    _render_engagement_analysis(ga4_data)
