"""
views/boost.py — Boost (Ads Performance) dashboard tab.

Data contract
─────────────
All functions accept a `data` dict whose shape mirrors what the
Meta Marketing API (v19.0) would return.  Pass the placeholder
produced by `empty_boost_data()` until the real API integration
is wired up.

TODO: replace `empty_boost_data()` calls in views/facebook.py with
      a call to api/boost.py → fetch_boost_insights(ad_account_id, since, until)
      once the Marketing API access token is available.
"""

from __future__ import annotations

import pandas as pd
import plotly.graph_objects as go
import streamlit as st

from components.charts import get_chart_layout


# ─── Placeholder data structure ───────────────────────────────────────────────
def empty_boost_data() -> dict:
    """
    Returns a zero-filled data structure that matches the shape expected by
    render_boost_tab().  Replace this with real Meta Marketing API data.

    Shape reference (Meta Marketing API fields):
      campaigns[*].insights → impressions, reach, clicks (link_clicks),
                               spend, cpc, ctr, frequency,
                               actions[action_type=purchase].value,
                               cost_per_action_type[action_type=purchase].value
    """
    return {
        # ── Totals across all active campaigns ──────────────────────────────
        # TODO: aggregate from ad_account/insights?fields=impressions,reach,
        #       clicks,spend,cpc,ctr,frequency&date_preset=...
        "totals": {
            "campaigns_count":  0,
            "link_clicks":      0,
            "reach":            0,
            "impressions":      0,
            "cpc":              0.0,   # €
            "ctr":              0.0,   # %
            "spend":            0.0,   # €
            "frequency":        0.0,
        },

        # ── Conversion-objective campaigns only ──────────────────────────────
        # TODO: filter by effective_status=ACTIVE & objective=CONVERSIONS
        "conversions": {
            "campaigns_count":       0,
            "link_clicks":           0,
            "reach":                 0,
            "impressions":           0,
            "cpc":                   0.0,
            "ctr":                   0.0,
            "spend":                 0.0,
            "frequency":             0.0,
            "cost_per_conversion":   0.0,  # cost_per_action_type[purchase]
            "total_conversions":     0,    # actions[purchase]
        },

        # ── Per-campaign detail (used for Top Campaigns chart) ───────────────
        # TODO: /act_{ad_account_id}/campaigns?fields=name,objective,
        #       insights{impressions,reach,clicks,spend,actions,cpc,ctr}
        "campaigns": [
            # {
            #     "name":        "Nom de la campagne",
            #     "objective":   "CONVERSIONS",
            #     "spend":       0.0,
            #     "conversions": 0,
            #     "cpa":         0.0,
            #     "clicks":      0,
            #     "reach":       0,
            # }
        ],
    }


# ─── Internal helpers ──────────────────────────────────────────────────────────
def _fmt_currency(value: float) -> str:
    return f"€{value:,.2f}"


def _fmt_pct(value: float) -> str:
    return f"{value:.2f}%"


def _fmt_int(value: int) -> str:
    return f"{value:,}"


def _kpi_card(icon: str, label: str, value: str, color: str | None = None,
              delta: float | None = None, lower_is_better: bool = False) -> str:
    _dark = st.session_state.get("theme", "dark") == "dark"
    _bg  = "rgba(255,255,255,0.05)" if _dark else "#ffffff"
    _brd = "none"                    if _dark else "1px solid #e5e7eb"
    _lc  = "rgba(255,255,255,0.45)" if _dark else "#6b7280"
    _vc  = color if color else ("#ffffff" if _dark else "#111827")
    if delta is not None:
        _good = (delta < 0) if lower_is_better else (delta > 0)
        _dc   = "#4ade80" if _good else "#f87171" if delta != 0 else "#a1a1aa"
        _arrow = "↑" if delta > 0 else "↓" if delta < 0 else "→"
        _sign  = "+" if delta > 0 else ""
        _delta_html = (
            f'<div style="font-size:0.65rem;color:{_dc};margin-top:0.15rem;">'
            f'{_arrow} {_sign}{delta:.1f}%</div>'
        )
    else:
        _delta_html = ""
    return (
        f'<div style="background:{_bg};border:{_brd};border-radius:12px;'
        f'padding:0.9rem 1rem;text-align:center;">'
        f'<div style="font-size:0.72rem;color:{_lc};'
        f'margin-bottom:0.25rem;">{icon} {label}</div>'
        f'<div style="font-size:1.3rem;font-weight:800;color:{_vc};'
        f'white-space:nowrap;">{value}</div>'
        f'{_delta_html}'
        f'</div>'
    )


def _no_data_banner(msg: str = "Aucune donnée publicitaire disponible pour cette période."):
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


def _section_header(title: str, big: bool = True):
    _brd = "rgba(255,255,255,0.15)"
    st.markdown(
        f'<div style="font-size:1.35rem;color:#ffffff;font-weight:700;'
        f'letter-spacing:0.05em;'
        f'margin:1.8rem 0 0.8rem;border-bottom:2px solid {_brd};'
        f'padding-bottom:0.5rem;">{title}</div>',
        unsafe_allow_html=True,
    )


# ─── Section renderers ─────────────────────────────────────────────────────────
def _render_global_kpis(totals: dict, prev_totals: dict | None = None):
    """Top-level ad account KPI row."""
    _section_header("📊 STATISTIQUES DU BOOST", big=True)

    no_data = totals.get("campaigns_count", 0) == 0
    pt = prev_totals or {}

    def _d(curr, prev):
        try:
            return round((curr - prev) / abs(prev) * 100, 1) if prev else None
        except Exception:
            return None

    row1 = f"""
<div style="display:grid;grid-template-columns:repeat(4,1fr);gap:0.6rem;margin-bottom:0.5rem;">
  {_kpi_card("📁", "Total des campagnes", _fmt_int(totals.get("campaigns_count", 0)),
             delta=_d(totals.get("campaigns_count",0), pt.get("campaigns_count",0)))}
  {_kpi_card("🖱️", "Clics sur le lien",  _fmt_int(totals.get("link_clicks", 0)),
             delta=_d(totals.get("link_clicks",0), pt.get("link_clicks",0)))}
  {_kpi_card("👁️", "Comptes touchés",    _fmt_int(totals.get("reach", 0)),
             delta=_d(totals.get("reach",0), pt.get("reach",0)))}
  {_kpi_card("📢", "Impressions",         _fmt_int(totals.get("impressions", 0)),
             delta=_d(totals.get("impressions",0), pt.get("impressions",0)))}
</div>"""

    row2 = f"""
<div style="display:grid;grid-template-columns:repeat(4,1fr);gap:0.6rem;margin-bottom:1rem;">
  {_kpi_card("💸", "Coût par clic",   _fmt_currency(totals.get("cpc", 0.0)),   "#facc15",
             delta=_d(totals.get("cpc",0.0), pt.get("cpc",0.0)),   lower_is_better=True)}
  {_kpi_card("📈", "CTR",             _fmt_pct(totals.get("ctr", 0.0)),         "#4ade80",
             delta=_d(totals.get("ctr",0.0), pt.get("ctr",0.0)))}
  {_kpi_card("💰", "Montant dépensé", _fmt_currency(totals.get("spend", 0.0)), "#f97316",
             delta=_d(totals.get("spend",0.0), pt.get("spend",0.0)), lower_is_better=True)}
  {_kpi_card("🔁", "Répétition",      f"{totals.get('frequency', 0.0):.2f}x",
             delta=_d(totals.get("frequency",0.0), pt.get("frequency",0.0)), lower_is_better=True)}
</div>"""

    st.markdown(row1 + row2, unsafe_allow_html=True)

    if no_data:
        _no_data_banner(
            "Données Marketing API non connectées. "
            "Connectez votre compte publicitaire pour afficher vos KPIs."
        )


def _render_conversion_campaigns(conv: dict, prev_conv: dict | None = None):
    """Conversion-objective campaigns subsection."""
    _section_header("🎯 AVEC L'OBJECTIF CONVERSION", big=True)

    no_data = conv.get("campaigns_count", 0) == 0
    pc = prev_conv or {}

    def _d(curr, prev):
        try:
            return round((curr - prev) / abs(prev) * 100, 1) if prev else None
        except Exception:
            return None

    row1 = f"""
<div style="display:grid;grid-template-columns:repeat(4,1fr);gap:0.6rem;margin-bottom:0.5rem;">
  {_kpi_card("📁", "Campagnes",         _fmt_int(conv.get("campaigns_count", 0)),
             delta=_d(conv.get("campaigns_count",0), pc.get("campaigns_count",0)))}
  {_kpi_card("🖱️", "Clics sur le lien", _fmt_int(conv.get("link_clicks", 0)),
             delta=_d(conv.get("link_clicks",0), pc.get("link_clicks",0)))}
  {_kpi_card("👁️", "Comptes touchés",   _fmt_int(conv.get("reach", 0)),
             delta=_d(conv.get("reach",0), pc.get("reach",0)))}
  {_kpi_card("📢", "Impressions",        _fmt_int(conv.get("impressions", 0)),
             delta=_d(conv.get("impressions",0), pc.get("impressions",0)))}
</div>"""

    row2 = f"""
<div style="display:grid;grid-template-columns:repeat(5,1fr);gap:0.6rem;margin-bottom:0.5rem;">
  {_kpi_card("💸", "Coût par clic",    _fmt_currency(conv.get("cpc", 0.0)),                "#facc15",
             delta=_d(conv.get("cpc",0.0), pc.get("cpc",0.0)),                   lower_is_better=True)}
  {_kpi_card("📈", "CTR",              _fmt_pct(conv.get("ctr", 0.0)),                     "#4ade80",
             delta=_d(conv.get("ctr",0.0), pc.get("ctr",0.0)))}
  {_kpi_card("💰", "Montant dépensé",  _fmt_currency(conv.get("spend", 0.0)),              "#f97316",
             delta=_d(conv.get("spend",0.0), pc.get("spend",0.0)),               lower_is_better=True)}
  {_kpi_card("🎁", "Coût par vente",   _fmt_currency(conv.get("cost_per_conversion",0.0)),"#fb7185",
             delta=_d(conv.get("cost_per_conversion",0.0), pc.get("cost_per_conversion",0.0)), lower_is_better=True)}
  {_kpi_card("✅", "Commandes (conv.)", _fmt_int(conv.get("total_conversions", 0)),         "#a78bfa",
             delta=_d(conv.get("total_conversions",0), pc.get("total_conversions",0)))}
</div>"""

    st.markdown(row1 + row2, unsafe_allow_html=True)

    if no_data:
        _no_data_banner("Aucune campagne de conversion détectée pour la période sélectionnée.")


def _render_by_objective(campaigns: list[dict], obj_reach: dict | None = None):
    """Single KPI block aggregated from selected objectives (multiselect filter).
    Uses inline_link_clicks and deduplicated reach — same methodology as conversion section."""
    _section_header("🗂️ PAR OBJECTIF")

    obj_reach = obj_reach or {}

    # Keep only campaigns with activity
    active = [c for c in campaigns if c.get("spend", 0) > 0 or c.get("impressions", 0) > 0]
    if not active:
        _no_data_banner("Aucune campagne active pour afficher la répartition par objectif.")
        return

    # Friendly labels
    _OBJ_LABELS = {
        "OUTCOME_SALES":         "🛒 Ventes",
        "OUTCOME_TRAFFIC":       "🚦 Trafic",
        "OUTCOME_AWARENESS":     "📣 Notoriété",
        "OUTCOME_ENGAGEMENT":    "💬 Engagement",
        "OUTCOME_LEADS":         "🎯 Leads",
        "OUTCOME_APP_PROMOTION": "📱 App",
        "CONVERSIONS":           "🛒 Conversions",
        "LINK_CLICKS":           "🚦 Clics sur le lien",
        "REACH":                 "📣 Portée",
        "BRAND_AWARENESS":       "📣 Notoriété de la marque",
        "VIDEO_VIEWS":           "▶️ Vues de vidéo",
        "LEAD_GENERATION":       "🎯 Génération de leads",
        "MESSAGES":              "💬 Messages",
        "APP_INSTALLS":          "📱 Installations d'app",
        "PAGE_LIKES":            "👍 Mentions J'aime",
        "EVENT_RESPONSES":       "📅 Réponses événements",
        "POST_ENGAGEMENT":       "💬 Engagement posts",
        "STORE_VISITS":          "🏪 Visites en magasin",
        "PRODUCT_CATALOG_SALES": "🛒 Ventes catalogue",
    }

    # Unique objectives in data sorted by spend
    seen = {}
    for c in sorted(active, key=lambda x: x.get("spend", 0), reverse=True):
        obj = c.get("objective", "—")
        if obj not in seen:
            seen[obj] = _OBJ_LABELS.get(obj, obj)
    all_objectives = list(seen.keys())
    all_labels     = [seen[o] for o in all_objectives]

    selected_labels = st.multiselect(
        "Filtrer par objectif",
        options=all_labels,
        default=all_labels,
        label_visibility="collapsed",
        placeholder="Sélectionner les objectifs à afficher…",
    )

    selected_objectives = [o for o, l in zip(all_objectives, all_labels) if l in selected_labels]

    if not selected_objectives:
        st.caption("Aucun objectif sélectionné.")
        return

    # Aggregate across all selected objectives
    group        = [c for c in active if c.get("objective") in selected_objectives]
    total_spend  = sum(c.get("spend", 0.0)       for c in group)
    total_clicks = sum(c.get("link_clicks", 0)    for c in group)   # inline_link_clicks
    total_imp    = sum(c.get("impressions", 0)    for c in group)
    total_conv   = sum(c.get("conversions", 0)    for c in group)
    n_camps      = len(group)
    # Deduplicated reach: sum pre-computed per-objective reach from API
    total_reach  = sum(obj_reach.get(obj, 0) for obj in selected_objectives)

    w_ctr = round(total_clicks / total_imp * 100, 2) if total_imp   > 0 else 0.0
    w_cpc = round(total_spend  / total_clicks,    2) if total_clicks > 0 else 0.0
    w_cpa = round(total_spend  / total_conv,      2) if total_conv   > 0 else 0.0

    row1 = f"""
<div style="display:grid;grid-template-columns:repeat(4,1fr);gap:0.6rem;margin-bottom:0.5rem;">
  {_kpi_card("📁", "Campagnes",         _fmt_int(n_camps))}
  {_kpi_card("🖱️", "Clics sur le lien", _fmt_int(total_clicks))}
  {_kpi_card("👁️", "Comptes touchés",   _fmt_int(total_reach))}
  {_kpi_card("📢", "Impressions",        _fmt_int(total_imp))}
</div>"""

    row2 = f"""
<div style="display:grid;grid-template-columns:repeat(5,1fr);gap:0.6rem;margin-bottom:1rem;">
  {_kpi_card("💸", "Coût par clic",   _fmt_currency(w_cpc),       "#facc15", lower_is_better=True)}
  {_kpi_card("📈", "CTR",             _fmt_pct(w_ctr),             "#4ade80")}
  {_kpi_card("💰", "Montant dépensé", _fmt_currency(total_spend),  "#f97316", lower_is_better=True)}
  {_kpi_card("🎁", "Coût par vente",  _fmt_currency(w_cpa),        "#fb7185", lower_is_better=True)}
  {_kpi_card("✅", "Commandes",       _fmt_int(total_conv),         "#a78bfa")}
</div>"""

    st.markdown(row1 + row2, unsafe_allow_html=True)


def _render_top_campaigns(campaigns: list[dict]):
    """Top-3 campaigns podium cards — mirrors the report's slide 39 layout."""
    _section_header("🏆 TOP #3 CAMPAGNES PAR VENTES")

    if not campaigns:
        _no_data_banner("Aucune campagne à afficher.")
        return

    # Sort by commandes (conversions) desc, take top 3
    top = sorted(campaigns, key=lambda c: c.get("conversions", 0), reverse=True)[:3]

    # Fall back to spend ranking when no conversions are recorded
    use_commandes = any(c.get("conversions", 0) > 0 for c in top)
    if not use_commandes:
        top = sorted(campaigns, key=lambda c: c.get("spend", 0.0), reverse=True)[:3]

    # Pad to always have 3 slots
    while len(top) < 3:
        top.append({"name": "—", "conversions": 0, "spend": 0.0, "cpa": 0.0})

    # Podium style: #1 gold, #2 silver, #3 bronze
    _ranks = [
        ("#1", "#FFD700", "rgba(255,215,0,0.12)",  "rgba(255,215,0,0.35)"),   # gold
        ("#2", "#C0C0C0", "rgba(192,192,192,0.10)", "rgba(192,192,192,0.30)"), # silver
        ("#3", "#CD7F32", "rgba(205,127,50,0.10)",  "rgba(205,127,50,0.30)"),  # bronze
    ]

    _dark = st.session_state.get("theme", "dark") == "dark"
    _name_c  = "rgba(255,255,255,0.75)" if _dark else "#1f2937"
    _meta_c  = "rgba(255,255,255,0.4)"  if _dark else "#9ca3af"
    _div_brd = "rgba(255,255,255,0.08)" if _dark else "#e5e7eb"
    _sub_lc  = "rgba(255,255,255,0.35)" if _dark else "#9ca3af"
    _sub_vc  = "rgba(255,255,255,0.7)"  if _dark else "#374151"

    cards_html = '<div style="display:grid;grid-template-columns:repeat(3,1fr);gap:1rem;margin:0.5rem 0 1rem;">'

    for i, c in enumerate(top):
        rank_label, rank_color, bg_color, border_color = _ranks[i]
        name = c["name"]
        # Truncate long names to two lines visually
        display_name = name if len(name) <= 40 else name[:38] + "…"

        if use_commandes:
            metric_value = f"{c.get('conversions', 0):,}"
            metric_label = "commandes"
        else:
            metric_value = _fmt_currency(c.get("spend", 0.0))
            metric_label = "dépensé"

        spend_str = _fmt_currency(c.get("spend", 0.0))
        cpa_str   = _fmt_currency(c.get("cpa", 0.0))

        cards_html += f"""
<div style="background:{bg_color};border:1px solid {border_color};border-radius:14px;
            padding:1.2rem 1rem;text-align:center;position:relative;display:flex;
            flex-direction:column;align-items:center;gap:0.4rem;">
  <div style="font-size:1.6rem;font-weight:900;color:{rank_color};
              line-height:1;margin-bottom:0.2rem;">{rank_label}</div>
  <div style="font-size:0.78rem;color:{_name_c};font-weight:600;
              line-height:1.35;min-height:2.7rem;display:flex;align-items:center;
              justify-content:center;">{display_name}</div>
  <div style="font-size:2rem;font-weight:900;color:{rank_color};
              line-height:1.1;margin:0.3rem 0 0.1rem;">{metric_value}</div>
  <div style="font-size:0.7rem;color:{_meta_c};
              text-transform:uppercase;letter-spacing:0.06em;">{metric_label}</div>
  <div style="margin-top:0.5rem;width:100%;border-top:1px solid {_div_brd};
              padding-top:0.5rem;display:flex;justify-content:space-around;">
    <div style="text-align:center;">
      <div style="font-size:0.68rem;color:{_sub_lc};">Dépensé</div>
      <div style="font-size:0.82rem;font-weight:700;color:{_sub_vc};">{spend_str}</div>
    </div>
    <div style="text-align:center;">
      <div style="font-size:0.68rem;color:{_sub_lc};">Coût / vente</div>
      <div style="font-size:0.82rem;font-weight:700;color:{_sub_vc};">{cpa_str}</div>
    </div>
  </div>
</div>"""

    cards_html += "</div>"
    st.markdown(cards_html, unsafe_allow_html=True)


def _render_insights_panel(totals: dict, conv: dict):
    """Automated interpretation: CTR, CPC efficiency, conversion rate."""
    _section_header("🧠 Analyse automatique")

    ctr   = totals.get("ctr", 0.0)
    cpc   = totals.get("cpc", 0.0)
    cpa   = conv.get("cost_per_conversion", 0.0)
    clicks = totals.get("link_clicks", 0)
    total_conv = conv.get("total_conversions", 0)
    cvr   = round(total_conv / clicks * 100, 2) if clicks else 0.0

    insights: list[tuple[str, str, str]] = []

    # CTR benchmark (Meta average: 0.9–1.5 % for feed ads)
    if ctr == 0:
        insights.append(("⚪", "CTR", "Données non disponibles."))
    elif ctr >= 2.0:
        insights.append(("🟢", "CTR excellent",  f"{_fmt_pct(ctr)} — bien au-dessus de la moyenne (>2 %)."))
    elif ctr >= 1.0:
        insights.append(("🟡", "CTR correct",    f"{_fmt_pct(ctr)} — dans la norme (1–2 %). Optimisation possible."))
    else:
        insights.append(("🔴", "CTR faible",     f"{_fmt_pct(ctr)} — en dessous de 1 %. Revoir les visuels / ciblage."))

    # CPC benchmark
    if cpc == 0:
        insights.append(("⚪", "Coût par clic", "Données non disponibles."))
    elif cpc <= 0.50:
        insights.append(("🟢", "Coût par clic très efficace", f"{_fmt_currency(cpc)} — coût par clic très bas."))
    elif cpc <= 1.50:
        insights.append(("🟡", "Coût par clic modéré",        f"{_fmt_currency(cpc)} — acceptable selon le secteur."))
    else:
        insights.append(("🔴", "Coût par clic élevé",          f"{_fmt_currency(cpc)} — envisager d'affiner le ciblage."))

    # CPA
    if cpa > 0:
        insights.append(("💡", "Coût par vente", f"{_fmt_currency(cpa)} — comparez à la valeur moyenne d'une commande."))

    _dark  = st.session_state.get("theme", "dark") == "dark"
    _row_bg = "rgba(255,255,255,0.03)" if _dark else "#f8fafc"
    _lbl_c  = "rgba(255,255,255,0.75)" if _dark else "#111827"
    _txt_c  = "rgba(255,255,255,0.45)" if _dark else "#6b7280"

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


def _render_campaigns_table(campaigns: list[dict]):
    """Full sortable table of all campaigns for the selected period."""
    _section_header("📋 TOUTES LES CAMPAGNES")

    if not campaigns:
        _no_data_banner("Aucune campagne à afficher pour cette période.")
        return

    # Mirror the KPI logic: only campaigns with actual activity in the period
    total_all    = len(campaigns)
    campaigns    = [c for c in campaigns if c.get("spend", 0) > 0 or c.get("impressions", 0) > 0]
    total_active = len(campaigns)
    inactive     = total_all - total_active

    if not campaigns:
        _no_data_banner("Aucune campagne active pour cette période.")
        return

    rows = []
    for c in campaigns:
        rows.append({
            "Campagne":        c.get("name", "—"),
            "Objectif":        c.get("objective", "—"),
            "Dépensé (€)":     round(c.get("spend", 0.0), 2),
            "Impressions":     c.get("impressions", 0),
            "Portée":          c.get("reach", 0),
            "Clics":           c.get("clicks", 0),
            "CTR (%)":         round(c.get("ctr", 0.0), 2),
            "CPC (€)":         round(c.get("cpc", 0.0), 2),
            "Répétition":      round(c.get("frequency", 0.0), 2),
            "Commandes":       c.get("conversions", 0),
            "Coût/vente (€)":  round(c.get("cpa", 0.0), 2),
        })

    df = pd.DataFrame(rows).sort_values("Dépensé (€)", ascending=False).reset_index(drop=True)

    # Summary totals row
    totals_row = {
        "Campagne":       f"TOTAL ({len(campaigns)} campagnes)",
        "Objectif":       "—",
        "Dépensé (€)":    round(df["Dépensé (€)"].sum(), 2),
        "Impressions":    int(df["Impressions"].sum()),
        "Portée":         int(df["Portée"].sum()),
        "Clics":          int(df["Clics"].sum()),
        "CTR (%)":        round(df["CTR (%)"].mean(), 2) if len(df) else 0.0,
        "CPC (€)":        round(df[df["CPC (€)"] > 0]["CPC (€)"].mean(), 2) if (df["CPC (€)"] > 0).any() else 0.0,
        "Répétition":     round(df[df["Répétition"] > 0]["Répétition"].mean(), 2) if (df["Répétition"] > 0).any() else 0.0,
        "Commandes":      int(df["Commandes"].sum()),
        "Coût/vente (€)": round(df[df["Coût/vente (€)"] > 0]["Coût/vente (€)"].mean(), 2) if (df["Coût/vente (€)"] > 0).any() else 0.0,
    }

    st.dataframe(
        df,
        use_container_width=True,
        hide_index=True,
        column_config={
            "Campagne":       st.column_config.TextColumn("Campagne", width="large"),
            "Objectif":       st.column_config.TextColumn("Objectif", width="small"),
            "Dépensé (€)":    st.column_config.NumberColumn("Dépensé (€)",    format="€%.2f"),
            "Impressions":    st.column_config.NumberColumn("Impressions",     format="%d"),
            "Portée":         st.column_config.NumberColumn("Portée",          format="%d"),
            "Clics":          st.column_config.NumberColumn("Clics",           format="%d"),
            "CTR (%)":        st.column_config.NumberColumn("CTR (%)",         format="%.2f%%"),
            "CPC (€)":        st.column_config.NumberColumn("CPC (€)",         format="€%.2f"),
            "Répétition":     st.column_config.NumberColumn("Répétition",      format="%.2fx"),
            "Commandes":      st.column_config.NumberColumn("Commandes",       format="%d"),
            "Coût/vente (€)": st.column_config.NumberColumn("Coût/vente (€)", format="€%.2f"),
        },
    )

    # Totals summary below the table
    _dark   = st.session_state.get("theme", "dark") == "dark"
    _sum_bg  = "rgba(255,255,255,0.04)" if _dark else "#f9fafb"
    _sum_brd = "rgba(255,255,255,0.1)"  if _dark else "#e5e7eb"
    _sum_tc  = "rgba(255,255,255,0.6)"  if _dark else "#4b5563"
    _sum_vc  = "#ffffff"                 if _dark else "#111827"
    _note_c  = "rgba(255,255,255,0.3)"  if _dark else "#9ca3af"
    inactive_note = f' <span style="color:{_note_c};">· {inactive} sans activité masquées</span>' if inactive else ""
    st.markdown(
        f'<div style="background:{_sum_bg};border:1px solid {_sum_brd};'
        f'border-radius:8px;padding:0.6rem 1rem;margin-top:0.4rem;font-size:0.8rem;'
        f'color:{_sum_tc};display:flex;gap:2rem;flex-wrap:wrap;align-items:center;">'
        f'<span>📁 <b style="color:{_sum_vc};">{total_active}</b> campagnes actives{inactive_note}</span>'
        f'<span>💰 Total dépensé : <b style="color:#f97316;">€{totals_row["Dépensé (€)"]:,.2f}</b></span>'
        f'<span>📢 Impressions : <b style="color:{_sum_vc};">{totals_row["Impressions"]:,}</b></span>'
        f'<span>🖱️ Clics : <b style="color:{_sum_vc};">{totals_row["Clics"]:,}</b></span>'
        f'<span>✅ Commandes (toutes campagnes) : <b style="color:#a78bfa;">{totals_row["Commandes"]:,}</b></span>'
        f'</div>',
        unsafe_allow_html=True,
    )


def _render_demographics(demo: dict):
    """Age / gender bar chart from Marketing API paid reach."""
    _section_header("👥 DONNÉES DÉMOGRAPHIQUES")

    age_brackets    = demo.get("age_brackets", [])
    men_pcts        = demo.get("men", [])
    women_pcts      = demo.get("women", [])
    total_men_pct   = demo.get("total_men_pct", 0)
    total_women_pct = demo.get("total_women_pct", 0)

    if not age_brackets or not any(v > 0 for v in men_pcts + women_pcts):
        _no_data_banner("Données démographiques non disponibles pour cette période.")
        return

    fig = go.Figure()
    fig.add_trace(go.Bar(
        name="Hommes",
        x=age_brackets,
        y=men_pcts,
        marker_color="#7EC8E3",
        text=[f"{v}%" for v in men_pcts],
        textposition="outside",
        textfont=dict(size=11, color="rgba(255,255,255,0.6)"),
    ))
    fig.add_trace(go.Bar(
        name="Femmes",
        x=age_brackets,
        y=women_pcts,
        marker_color="#1C4E80",
        text=[f"{v}%" for v in women_pcts],
        textposition="outside",
        textfont=dict(size=11, color="rgba(255,255,255,0.6)"),
    ))
    _ymax = max(max(men_pcts + women_pcts, default=0) * 1.25, 10)
    fig.update_layout(**{
        **get_chart_layout(),
        "barmode": "group",
        "yaxis": dict(
            gridcolor="rgba(255,255,255,0.06)", showline=False,
            ticksuffix="%", range=[0, _ymax],
        ),
        "xaxis": dict(gridcolor="rgba(255,255,255,0.06)", showline=False),
        "showlegend": False,
        "margin": dict(l=0, r=0, t=20, b=40),
        "height": 320,
    })
    st.plotly_chart(fig, use_container_width=True)

    _dark   = st.session_state.get("theme", "dark") == "dark"
    _leg_c  = "rgba(255,255,255,0.7)" if _dark else "#374151"
    _note_c = "rgba(255,255,255,0.3)" if _dark else "#9ca3af"

    st.markdown(
        f'<div style="display:flex;justify-content:center;align-items:center;gap:2rem;margin-top:-8px;">'
        f'<div style="display:flex;align-items:center;gap:6px;">'
        f'<div style="width:24px;height:12px;background:#7EC8E3;border-radius:3px;"></div>'
        f'<span style="font-size:0.8rem;color:{_leg_c};">Hommes — <strong>{total_men_pct}%</strong></span>'
        f'</div>'
        f'<div style="display:flex;align-items:center;gap:6px;">'
        f'<div style="width:24px;height:12px;background:#1C4E80;border-radius:3px;"></div>'
        f'<span style="font-size:0.8rem;color:{_leg_c};">Femmes — <strong>{total_women_pct}%</strong></span>'
        f'</div>'
        f'</div>',
        unsafe_allow_html=True,
    )
    st.markdown(
        f'<p style="font-size:0.7rem;color:{_note_c};text-align:center;margin-top:4px;">'
        f'* Basé sur la portée des campagnes payantes Footland (Marketing API)</p>',
        unsafe_allow_html=True,
    )


def _render_geographic(demo: dict):
    """Top cities and top countries from Marketing API paid reach."""
    _section_header("🌍 DONNÉES GÉOGRAPHIQUES")

    top_cities = demo.get("top_cities", [])

    if not top_cities:
        _no_data_banner("Données géographiques non disponibles pour cette période.")
        return

    _dark     = st.session_state.get("theme", "dark") == "dark"
    _geo_bg   = "rgba(255,255,255,0.04)" if _dark else "#f9fafb"
    _geo_brd  = "none"                    if _dark else "1px solid #e5e7eb"
    _title_c  = "#ffffff"                 if _dark else "#111827"
    _empty_c  = "rgba(255,255,255,0.35)" if _dark else "#9ca3af"
    _name_c   = "rgba(255,255,255,0.8)"  if _dark else "#111827"
    _stat_c   = "rgba(255,255,255,0.5)"  if _dark else "#6b7280"
    _bar_bg   = "rgba(255,255,255,0.08)" if _dark else "#e5e7eb"
    _rank_low = "rgba(255,255,255,0.3)"  if _dark else "#d1d5db"

    def _geo_table(items: list, icon: str, title: str) -> str:
        if not items:
            return (
                f'<div style="background:{_geo_bg};border:{_geo_brd};border-radius:14px;padding:1.2rem;">'
                f'<p style="font-size:0.95rem;font-weight:700;color:{_title_c};margin:0 0 12px;">{icon} {title}</p>'
                f'<p style="font-size:0.8rem;color:{_empty_c};margin:0;">Aucune donnée disponible</p>'
                f'</div>'
            )
        rank_colors = ["#FFD700", "#C0C0C0", "#CD7F32"] + [_rank_low] * 7
        rows_html = ""
        for i, item in enumerate(items):
            bar_w = round(item["pct"] * 0.9, 1)
            rows_html += (
                f'<div style="display:flex;align-items:center;gap:8px;margin-bottom:8px;">'
                f'<span style="font-size:0.72rem;font-weight:700;color:{rank_colors[i]};width:16px;text-align:right;">#{i+1}</span>'
                f'<div style="flex:1;">'
                f'<div style="display:flex;justify-content:space-between;margin-bottom:2px;">'
                f'<span style="font-size:0.78rem;color:{_name_c};">{item["name"]}</span>'
                f'<span style="font-size:0.78rem;color:{_stat_c};">{item["reach"]:,} impr. · {item["pct"]}%</span>'
                f'</div>'
                f'<div style="background:{_bar_bg};border-radius:4px;height:5px;">'
                f'<div style="background:#E8420A;width:{bar_w}%;height:5px;border-radius:4px;"></div>'
                f'</div></div></div>'
            )
        return (
            f'<div style="background:{_geo_bg};border:{_geo_brd};border-radius:14px;padding:1.2rem;">'
            f'<p style="font-size:0.95rem;font-weight:700;color:{_title_c};margin:0 0 14px;">{icon} {title}</p>'
            f'{rows_html}'
            f'</div>'
        )

    st.markdown(_geo_table(top_cities, "🏙️", "Top Villes / Régions"), unsafe_allow_html=True)


def _render_campaign_lookup(campaigns: list[dict]):
    """Search box — type a campaign name fragment to see its full detail card."""
    _section_header("🔍 RECHERCHE DE CAMPAGNE")

    if not campaigns:
        _no_data_banner("Aucune campagne disponible.")
        return

    query = st.text_input(
        "Nom de la campagne",
        placeholder="ex: Footland, Week08, Clarks…",
        label_visibility="collapsed",
    )

    if not query:
        st.caption("Tapez tout ou partie du nom d'une campagne pour afficher ses détails.")
        return

    matches = [c for c in campaigns if query.lower() in c.get("name", "").lower()]

    if not matches:
        st.warning(f"Aucune campagne ne contient « {query} ».")
        return

    _dark    = st.session_state.get("theme", "dark") == "dark"
    _crd_bg  = "rgba(255,255,255,0.05)" if _dark else "#ffffff"
    _crd_brd = "rgba(255,255,255,0.12)" if _dark else "#e5e7eb"
    _nm_c    = "#ffffff"                 if _dark else "#111827"
    _bdg_bg  = "rgba(255,255,255,0.08)" if _dark else "#f1f5f9"
    _bdg_c   = "rgba(255,255,255,0.5)"  if _dark else "#6b7280"

    for c in matches:
        name      = c.get("name", "—")
        objective = c.get("objective", "—")
        spend     = c.get("spend", 0.0)
        imp       = c.get("impressions", 0)
        reach     = c.get("reach", 0)
        clicks    = c.get("clicks", 0)
        ctr       = c.get("ctr", 0.0)
        cpc       = c.get("cpc", 0.0)
        freq      = c.get("frequency", 0.0)
        conv      = c.get("conversions", 0)
        cpa       = c.get("cpa", 0.0)

        freq_label = round(freq, 2) if freq else "—"

        st.markdown(
            f'<div style="background:{_crd_bg};border:1px solid {_crd_brd};'
            f'border-radius:14px;padding:1.2rem 1.4rem;margin-bottom:1rem;">'

            # Campaign name + objective badge
            f'<div style="display:flex;justify-content:space-between;align-items:flex-start;'
            f'margin-bottom:1rem;gap:1rem;">'
            f'<div style="font-size:0.9rem;font-weight:700;color:{_nm_c};line-height:1.4;">{name}</div>'
            f'<div style="background:{_bdg_bg};border-radius:6px;padding:0.2rem 0.6rem;'
            f'font-size:0.68rem;color:{_bdg_c};white-space:nowrap;">{objective}</div>'
            f'</div>'

            # Row 1 — reach / impressions / frequency / clicks
            f'<div style="display:grid;grid-template-columns:repeat(4,1fr);gap:0.5rem;margin-bottom:0.5rem;">'
            f'{_kpi_card("👁️", "Portée",        f"{reach:,}")}'
            f'{_kpi_card("📢", "Impressions",   f"{imp:,}")}'
            f'{_kpi_card("🔁", "Répétition",    f"{freq_label}x")}'
            f'{_kpi_card("🖱️", "Clics",          f"{clicks:,}")}'
            f'</div>'

            # Row 2 — spend / CPC / CTR / conversions / CPA
            f'<div style="display:grid;grid-template-columns:repeat(5,1fr);gap:0.5rem;">'
            f'{_kpi_card("💰", "Dépensé",       _fmt_currency(spend),  "#f97316")}'
            f'{_kpi_card("💸", "CPC",            _fmt_currency(cpc),    "#facc15")}'
            f'{_kpi_card("📈", "CTR",            _fmt_pct(ctr),         "#4ade80")}'
            f'{_kpi_card("✅", "Commandes",      f"{conv:,}",           "#a78bfa")}'
            f'{_kpi_card("🎁", "Coût / vente",  _fmt_currency(cpa),    "#fb7185")}'
            f'</div>'

            f'</div>',
            unsafe_allow_html=True,
        )


# ─── Public entry point ────────────────────────────────────────────────────────
def render_boost_tab(data: dict | None = None, demo: dict | None = None,
                     prev_data: dict | None = None):
    """
    Render the full Boost (Ads Performance) tab.

    Parameters
    ----------
    data      : dict  — output of fetch_boost_insights()
    demo      : dict  — output of fetch_fb_demographics() (age/gender + geo)
    prev_data : dict  — same shape as data but for the previous equivalent period
    """
    if data is None:
        data = empty_boost_data()
    if demo is None:
        demo = {}

    totals    = data.get("totals",      {})
    conv      = data.get("conversions", {})
    campaigns   = data.get("campaigns",      [])
    obj_reach   = data.get("objective_reach", {})

    prev_totals = (prev_data or {}).get("totals",      {})
    prev_conv   = (prev_data or {}).get("conversions", {})

    # Header
    _dark   = st.session_state.get("theme", "dark") == "dark"
    _hdr_c  = "#ffffff"                 if _dark else "#111827"
    _sub_c  = "rgba(255,255,255,0.35)" if _dark else "#9ca3af"
    st.markdown(
        f'<p style="font-size:1.4rem;font-weight:800;letter-spacing:0.08em;'
        f'color:{_hdr_c};margin:0 0 0.2rem;">BOOST — ADS PERFORMANCE</p>'
        f'<p style="font-size:0.8rem;color:{_sub_c};margin:0 0 1rem;">'
        f'Performances publicitaires payantes · Meta Marketing API</p>',
        unsafe_allow_html=True,
    )

    _render_global_kpis(totals, prev_totals)
    st.divider()
    _render_conversion_campaigns(conv, prev_conv)
    st.divider()
    _render_by_objective(campaigns, obj_reach)
    st.divider()
    _render_top_campaigns(campaigns)
    st.divider()
    _render_campaigns_table(campaigns)
    st.divider()
    _render_campaign_lookup(campaigns)
    st.divider()
    _render_demographics(demo)
    st.divider()
    _render_geographic(demo)
    st.divider()
    _render_insights_panel(totals, conv)
