"""
views/analytics.py — Google Analytics 4 dashboard tab.
"""
from __future__ import annotations

import pandas as pd
import plotly.graph_objects as go
import streamlit as st

from components.charts import get_chart_layout


# ─── Helpers ───────────────────────────────────────────────────────────────────
def _fmt_int(v: int) -> str:
    return f"{int(v):,}"

def _fmt_pct(v: float) -> str:
    return f"{v:.2f}%"

def _fmt_dur(seconds: float) -> str:
    m = int(seconds) // 60
    s = int(seconds) % 60
    return f"{m}m {s:02d}s"

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
        f'letter-spacing:0.05em;margin:1.8rem 0 0.8rem;border-bottom:2px solid {_brd};'
        f'padding-bottom:0.5rem;">{title}</div>',
        unsafe_allow_html=True,
    )

def _no_data(msg: str = "Aucune donnée disponible pour cette période."):
    _dark = st.session_state.get("theme", "dark") == "dark"
    _bg  = "rgba(255,165,0,0.08)"  if _dark else "rgba(255,165,0,0.12)"
    _tc  = "rgba(255,165,0,0.9)"   if _dark else "#92400e"
    st.markdown(
        f'<div style="background:{_bg};border:1px solid rgba(255,165,0,0.3);'
        f'border-radius:10px;padding:1rem 1.2rem;color:{_tc};'
        f'font-size:0.85rem;margin:0.5rem 0 1rem;">⚠️ {msg}</div>',
        unsafe_allow_html=True,
    )


# ─── Section renderers ─────────────────────────────────────────────────────────
def _render_overview(ov: dict):
    _section_header("📊 VUE D'ENSEMBLE")
    if not ov:
        _no_data()
        return

    row1 = f"""
<div style="display:grid;grid-template-columns:repeat(4,1fr);gap:0.6rem;margin-bottom:0.6rem;">
  {_kpi_card("👥", "Utilisateurs actifs",    _fmt_int(ov.get("active_users", 0)),     "#7dd3fc")}
  {_kpi_card("🆕", "Nouveaux utilisateurs",  _fmt_int(ov.get("new_users", 0)),         "#a78bfa")}
  {_kpi_card("🔄", "Sessions",               _fmt_int(ov.get("sessions", 0)),          "#4ade80")}
  {_kpi_card("✅", "Sessions engagées",      _fmt_int(ov.get("engaged_sessions", 0)),  "#34d399")}
</div>"""

    row2 = f"""
<div style="display:grid;grid-template-columns:repeat(5,1fr);gap:0.6rem;margin-bottom:1rem;">
  {_kpi_card("💡", "Taux d'engagement",  _fmt_pct(ov.get("engagement_rate", 0.0)),        "#4ade80")}
  {_kpi_card("↩️", "Taux de rebond",     _fmt_pct(ov.get("bounce_rate", 0.0)),             "#f87171")}
  {_kpi_card("⏱️", "Durée moyenne",      _fmt_dur(ov.get("avg_session_duration", 0.0)),    "#facc15")}
  {_kpi_card("📄", "Pages vues",         _fmt_int(ov.get("page_views", 0)),                "#fb923c")}
  {_kpi_card("📑", "Pages / Session",    f"{ov.get('pages_per_session', 0.0):.2f}",        "#e879f9")}
</div>"""

    st.markdown(row1 + row2, unsafe_allow_html=True)


def _render_traffic_sources(sources: list):
    _section_header("🚦 SOURCES DE TRAFIC")
    if not sources:
        _no_data()
        return

    _dark   = st.session_state.get("theme", "dark") == "dark"
    _bg     = "rgba(255,255,255,0.03)" if _dark else "#f9fafb"
    _brd    = "rgba(255,255,255,0.08)" if _dark else "#e5e7eb"
    _txt_c  = "#ffffff"                 if _dark else "#111827"
    _sub_c  = "rgba(255,255,255,0.45)" if _dark else "#6b7280"

    _CHANNEL_ICONS = {
        "Organic Search":  "🔍",
        "Direct":          "🔗",
        "Organic Social":  "📱",
        "Paid Search":     "💰",
        "Paid Social":     "📢",
        "Referral":        "🔄",
        "Email":           "📧",
        "Unassigned":      "❓",
        "Organic Video":   "▶️",
        "Affiliates":      "🤝",
    }

    max_sessions = max(s["sessions"] for s in sources) or 1
    rows_html = ""
    for s in sources:
        bar_w = round(s["sessions"] / max_sessions * 100, 1)
        icon  = _CHANNEL_ICONS.get(s["channel"], "📊")
        rows_html += (
            f'<div style="margin-bottom:0.75rem;">'
            f'<div style="display:flex;justify-content:space-between;align-items:center;margin-bottom:4px;">'
            f'<span style="font-size:0.8rem;color:{_txt_c};font-weight:600;">{icon} {s["channel"]}</span>'
            f'<span style="font-size:0.72rem;color:{_sub_c};">'
            f'{_fmt_int(s["sessions"])} sessions · {s["pct"]}% · '
            f'eng. {_fmt_pct(s["engagement_rate"])}'
            f'</span></div>'
            f'<div style="background:{_brd};border-radius:6px;height:8px;">'
            f'<div style="background:#E8420A;width:{bar_w}%;height:8px;border-radius:6px;"></div>'
            f'</div></div>'
        )

    st.markdown(
        f'<div style="background:{_bg};border:1px solid {_brd};border-radius:12px;padding:1.2rem 1.4rem;">'
        f'{rows_html}</div>',
        unsafe_allow_html=True,
    )


def _render_top_pages(pages: list):
    _section_header("📄 TOP PAGES")
    if not pages:
        _no_data()
        return

    df = pd.DataFrame([
        {
            "Page":           p["path"],
            "Titre":          (p["title"][:45] + "…") if len(p.get("title", "")) > 45 else p.get("title", "—"),
            "Vues":           p["views"],
            "Utilisateurs":   p["users"],
            "Durée moy.":     _fmt_dur(p["avg_duration"]),
            "Taux de rebond": f'{p["bounce_rate"]:.1f}%',
        }
        for p in pages
    ])
    st.dataframe(
        df,
        use_container_width=True,
        hide_index=True,
        column_config={
            "Page":           st.column_config.TextColumn("Page",           width="large"),
            "Titre":          st.column_config.TextColumn("Titre",          width="medium"),
            "Vues":           st.column_config.NumberColumn("Vues",         format="%d"),
            "Utilisateurs":   st.column_config.NumberColumn("Utilisateurs", format="%d"),
            "Durée moy.":     st.column_config.TextColumn("Durée moy.",     width="small"),
            "Taux de rebond": st.column_config.TextColumn("Rebond",         width="small"),
        },
    )


def _render_geography(geo: dict):
    _section_header("🌍 GÉOGRAPHIE")
    countries = geo.get("countries", [])
    cities    = geo.get("cities", [])
    if not countries and not cities:
        _no_data()
        return

    _dark   = st.session_state.get("theme", "dark") == "dark"
    _bg     = "rgba(255,255,255,0.03)" if _dark else "#f9fafb"
    _brd    = "rgba(255,255,255,0.08)" if _dark else "#e5e7eb"
    _txt_c  = "#ffffff"                 if _dark else "#111827"
    _sub_c  = "rgba(255,255,255,0.45)" if _dark else "#6b7280"
    _rank_c = ["#FFD700", "#C0C0C0", "#CD7F32"] + ["rgba(255,255,255,0.3)"] * 20

    def _geo_block(items: list, icon: str, title: str) -> str:
        if not items:
            return (
                f'<div style="background:{_bg};border:1px solid {_brd};border-radius:12px;padding:1.2rem;">'
                f'<p style="font-size:0.9rem;font-weight:700;color:{_txt_c};margin:0 0 8px;">{icon} {title}</p>'
                f'<p style="font-size:0.8rem;color:{_sub_c};margin:0;">Aucune donnée</p></div>'
            )
        max_u = max(i["users"] for i in items) or 1
        rows  = ""
        for i, item in enumerate(items[:10]):
            bar_w = round(item["users"] / max_u * 90, 1)
            rows += (
                f'<div style="display:flex;align-items:center;gap:8px;margin-bottom:7px;">'
                f'<span style="font-size:0.72rem;font-weight:700;color:{_rank_c[i]};'
                f'width:18px;text-align:right;">#{i+1}</span>'
                f'<div style="flex:1;">'
                f'<div style="display:flex;justify-content:space-between;margin-bottom:2px;">'
                f'<span style="font-size:0.78rem;color:{_txt_c};">{item["name"]}</span>'
                f'<span style="font-size:0.72rem;color:{_sub_c};">'
                f'{_fmt_int(item["users"])} · {item["pct"]}%</span>'
                f'</div>'
                f'<div style="background:{_brd};border-radius:4px;height:5px;">'
                f'<div style="background:#E8420A;width:{bar_w}%;height:5px;border-radius:4px;"></div>'
                f'</div></div></div>'
            )
        return (
            f'<div style="background:{_bg};border:1px solid {_brd};border-radius:12px;padding:1.2rem;">'
            f'<p style="font-size:0.9rem;font-weight:700;color:{_txt_c};margin:0 0 12px;">{icon} {title}</p>'
            f'{rows}</div>'
        )

    col1, col2 = st.columns(2)
    with col1:
        st.markdown(_geo_block(countries, "🌐", "Top Pays"), unsafe_allow_html=True)
    with col2:
        st.markdown(_geo_block(cities, "🏙️", "Top Villes"), unsafe_allow_html=True)


def _render_devices(devices: list):
    _section_header("📱 APPAREILS")
    if not devices:
        _no_data()
        return

    _dark   = st.session_state.get("theme", "dark") == "dark"
    _COLORS = ["#E8420A", "#7dd3fc", "#4ade80", "#a78bfa"]
    _ICONS  = {"mobile": "📱", "desktop": "🖥️", "tablet": "📲"}

    labels = [d["device"].capitalize() for d in devices]
    values = [d["users"] for d in devices]

    fig = go.Figure(go.Pie(
        labels=labels,
        values=values,
        hole=0.55,
        marker_colors=_COLORS[:len(labels)],
        textfont=dict(size=12),
        hovertemplate="%{label}<br>%{value:,} utilisateurs<br>%{percent}<extra></extra>",
    ))
    fig.update_layout(**{
        **get_chart_layout(),
        "showlegend": True,
        "legend": dict(orientation="h", y=-0.1),
        "height": 280,
        "margin": dict(l=0, r=0, t=10, b=40),
    })
    st.plotly_chart(fig, use_container_width=True)

    _bg  = "rgba(255,255,255,0.05)" if _dark else "#ffffff"
    _brd = "none"                    if _dark else "1px solid #e5e7eb"
    _lc  = "rgba(255,255,255,0.45)" if _dark else "#6b7280"
    _vc  = "#ffffff"                 if _dark else "#111827"

    cards = ""
    for d in devices:
        icon = _ICONS.get(d["device"].lower(), "💻")
        cards += (
            f'<div style="background:{_bg};border:{_brd};border-radius:12px;padding:0.8rem;text-align:center;">'
            f'<div style="font-size:0.72rem;color:{_lc};">{icon} {d["device"].capitalize()}</div>'
            f'<div style="font-size:1.2rem;font-weight:800;color:{_vc};">{d["pct"]}%</div>'
            f'<div style="font-size:0.68rem;color:{_lc};">{_fmt_int(d["sessions"])} sessions</div>'
            f'<div style="font-size:0.68rem;color:{_lc};">Eng. {_fmt_pct(d["engagement_rate"])}</div>'
            f'</div>'
        )
    st.markdown(
        f'<div style="display:grid;grid-template-columns:repeat({len(devices)},1fr);'
        f'gap:0.6rem;margin-top:0.5rem;">{cards}</div>',
        unsafe_allow_html=True,
    )


def _render_analysis(ov: dict):
    _section_header("🧠 ANALYSE AUTOMATIQUE")
    if not ov:
        _no_data()
        return

    _dark   = st.session_state.get("theme", "dark") == "dark"
    _row_bg = "rgba(255,255,255,0.03)" if _dark else "#f8fafc"
    _lbl_c  = "rgba(255,255,255,0.75)" if _dark else "#111827"
    _txt_c  = "rgba(255,255,255,0.45)" if _dark else "#6b7280"

    bounce   = ov.get("bounce_rate", 0.0)
    duration = ov.get("avg_session_duration", 0.0)
    eng_rate = ov.get("engagement_rate", 0.0)
    pps      = ov.get("pages_per_session", 0.0)
    new_u    = ov.get("new_users", 0)
    total_u  = ov.get("active_users", 1) or 1
    new_pct  = round(new_u / total_u * 100, 1)

    insights: list[tuple[str, str, str]] = []

    if eng_rate >= 60:
        insights.append(("🟢", "Taux d'engagement excellent",   f"{_fmt_pct(eng_rate)} — visiteurs très engagés."))
    elif eng_rate >= 40:
        insights.append(("🟡", "Taux d'engagement correct",     f"{_fmt_pct(eng_rate)} — marge d'amélioration."))
    else:
        insights.append(("🔴", "Taux d'engagement faible",      f"{_fmt_pct(eng_rate)} — revoir l'expérience d'arrivée."))

    if bounce < 40:
        insights.append(("🟢", "Taux de rebond excellent",      f"{_fmt_pct(bounce)} — visiteurs qui explorent."))
    elif bounce < 60:
        insights.append(("🟡", "Taux de rebond correct",        f"{_fmt_pct(bounce)} — dans la norme (40–60 %)."))
    else:
        insights.append(("🔴", "Taux de rebond élevé",          f"{_fmt_pct(bounce)} — beaucoup repartent sans interagir."))

    if duration >= 120:
        insights.append(("🟢", "Bonne durée de session",        f"{_fmt_dur(duration)} — les visiteurs lisent le contenu."))
    elif duration >= 30:
        insights.append(("🟡", "Durée de session courte",       f"{_fmt_dur(duration)} — améliorer le contenu."))
    else:
        insights.append(("🔴", "Durée très courte",             f"{_fmt_dur(duration)} — les visiteurs ne restent pas."))

    if pps >= 3:
        insights.append(("🟢", "Navigation active",             f"{pps:.1f} pages/session — bonne exploration."))
    elif pps >= 1.5:
        insights.append(("🟡", "Navigation limitée",            f"{pps:.1f} pages/session — inciter à explorer davantage."))
    else:
        insights.append(("🔴", "Peu de pages visitées",         f"{pps:.1f} pages/session — améliorer les liens internes."))

    if new_pct > 80:
        insights.append(("💡", "Audience principalement nouvelle", f"{new_pct}% nouveaux — travailler la rétention."))
    elif new_pct > 50:
        insights.append(("💡", "Bon mix acquisition/fidélisation", f"{new_pct}% nouveaux / {100-new_pct:.0f}% récurrents."))
    else:
        insights.append(("💡", "Forte fidélisation",             f"{100-new_pct:.0f}% de visiteurs récurrents — audience fidèle."))

    rows_html = "".join(
        f'<div style="display:flex;align-items:flex-start;gap:0.6rem;background:{_row_bg};'
        f'border-radius:8px;padding:0.55rem 0.8rem;margin-bottom:0.35rem;">'
        f'<span style="font-size:1rem;line-height:1.4;">{dot}</span>'
        f'<div><span style="font-size:0.78rem;font-weight:700;color:{_lbl_c};">{label}</span>'
        f'<span style="font-size:0.78rem;color:{_txt_c};"> — {text}</span></div>'
        f'</div>'
        for dot, label, text in insights
    )
    st.markdown(rows_html, unsafe_allow_html=True)


# ─── Public entry point ────────────────────────────────────────────────────────
def render_analytics_tab(ga4_data: dict, since: str = "", until: str = ""):
    _dark  = st.session_state.get("theme", "dark") == "dark"
    _hdr_c = "#ffffff"                 if _dark else "#111827"
    _sub_c = "rgba(255,255,255,0.35)" if _dark else "#9ca3af"

    st.markdown(
        f'<p style="font-size:1.4rem;font-weight:800;letter-spacing:0.08em;'
        f'color:{_hdr_c};margin:0 0 0.2rem;">GOOGLE ANALYTICS 4</p>'
        f'<p style="font-size:0.8rem;color:{_sub_c};margin:0 0 1rem;">'
        f'Comportement des visiteurs · footland.dz</p>',
        unsafe_allow_html=True,
    )

    if not ga4_data or not ga4_data.get("overview"):
        _no_data("Données Google Analytics non disponibles. Vérifiez que le token GA4 est configuré.")
        return

    _render_overview(ga4_data.get("overview", {}))
    st.divider()
    _render_traffic_sources(ga4_data.get("traffic_sources", []))
    st.divider()
    _render_top_pages(ga4_data.get("top_pages", []))
    st.divider()
    _render_geography(ga4_data.get("geography", {}))
    st.divider()
    _render_devices(ga4_data.get("devices", []))
    st.divider()
    _render_analysis(ga4_data.get("overview", {}))
