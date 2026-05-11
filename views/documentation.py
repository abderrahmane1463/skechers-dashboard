"""
views/documentation.py — Guide du dashboard Footland.
"""

import streamlit as st


_DOC_CSS = """
<style>
.doc-hero {
    background: linear-gradient(135deg, #161616 0%, #1a0f0a 100%);
    border: 1px solid #262626;
    border-radius: 20px;
    padding: 40px 48px;
    margin-bottom: 32px;
}
.doc-hero h1 {
    font-size: 32px;
    font-weight: 800;
    background: linear-gradient(90deg, #E8420A, #FF6B35);
    -webkit-background-clip: text;
    -webkit-text-fill-color: transparent;
    margin-bottom: 8px;
}
.doc-hero p { color: #a1a1aa !important; font-size: 15px; }
.doc-section-title {
    font-size: 20px;
    font-weight: 700;
    color: #E8420A !important;
    margin-bottom: 16px;
    padding-bottom: 10px;
    border-bottom: 1px solid #262626;
}
.kpi-table { width: 100%; border-collapse: collapse; }
.kpi-table th {
    text-align: left;
    padding: 10px 14px;
    font-size: 12px;
    font-weight: 600;
    color: #71717a !important;
    text-transform: uppercase;
    letter-spacing: 0.05em;
    border-bottom: 1px solid #262626;
}
.kpi-table td {
    padding: 10px 14px;
    font-size: 14px;
    color: #e4e4e7 !important;
    border-bottom: 1px solid #1a1a1a;
    vertical-align: top;
}
.kpi-table tr:last-child td { border-bottom: none; }
.kpi-table tr:hover td { background: #1a1a1a; }
.kpi-name { font-weight: 600; white-space: nowrap; }
.kpi-desc { color: #a1a1aa !important; }
.endpoint {
    font-family: monospace;
    font-size: 12px;
    background: #1e1e1e;
    color: #E8420A !important;
    padding: 2px 6px;
    border-radius: 4px;
    white-space: nowrap;
}
</style>
"""


def render_documentation():
    _is_admin = st.session_state.get("user", {}).get("role") == "admin"

    # Hide Endpoint column for viewers via CSS
    if not _is_admin:
        st.markdown("""
<style>
.kpi-table th:nth-child(3),
.kpi-table td:nth-child(3) { display: none !important; }
</style>
""", unsafe_allow_html=True)

    st.markdown(_DOC_CSS, unsafe_allow_html=True)

    st.markdown("""
<div class="doc-hero">
  <h1>📖 Guide du Dashboard</h1>
  <p>Ce guide explique chaque indicateur (KPI) affiché dans le dashboard Footland — ce qu'il mesure, comment il est calculé, et l'endpoint Meta API utilisé pour le récupérer.</p>
</div>
""", unsafe_allow_html=True)

    col1, col2, col3 = st.columns(3)
    with col1:
        st.info("🔵 **Facebook** — Audience, Engagement, Visibilité, Publications, Communauté")
    with col2:
        st.info("📸 **Instagram** — Visibilité, Engagement, Publications")
    with col3:
        st.info("🚀 **Boost** — Campagnes payantes, Conversions, Démographie, Géographie")

    st.markdown("<br>", unsafe_allow_html=True)

    # ── Facebook ──────────────────────────────────────────────────────────────
    st.markdown('<div class="doc-section-title">🔵 Facebook</div>', unsafe_allow_html=True)

    t1, t2, t3, t4, t5, t6 = st.tabs(["Vue d'ensemble", "👥 Audience", "📡 Visibilité", "💬 Engagement", "🏆 Top Contenu", "🤝 Communauté"])

    with t1:
        st.markdown("""
<table class="kpi-table">
  <tr><th>Indicateur</th><th>Description</th><th>Endpoint</th></tr>
  <tr><td class="kpi-name">👥 Followers</td><td class="kpi-desc">Nombre total d'abonnés à la fin de la période.</td><td><span class="endpoint">/{page_id}?fields=fan_count</span></td></tr>
  <tr><td class="kpi-name">➕ Nouveaux followers</td><td class="kpi-desc">Nouveaux abonnements pendant la période.</td><td><span class="endpoint">/{page_id}/insights?metric=page_daily_follows</span></td></tr>
  <tr><td class="kpi-name">➖ Désabonnements</td><td class="kpi-desc">Personnes ayant arrêté de suivre la page.</td><td><span class="endpoint">/{page_id}/insights?metric=page_daily_unfollows</span></td></tr>
  <tr><td class="kpi-name">📊 Taux d'engagement</td><td class="kpi-desc">Interactions totales ÷ portée × 100.</td><td><span class="endpoint">Calculé</span></td></tr>
  <tr><td class="kpi-name">👁️ Spectateurs (Reach)</td><td class="kpi-desc">Comptes uniques ayant vu un contenu de la page.</td><td><span class="endpoint">/{page_id}/insights?metric=page_impressions_unique</span></td></tr>
  <tr><td class="kpi-name">📢 Impressions</td><td class="kpi-desc">Nombre total d'affichages (doublons inclus).</td><td><span class="endpoint">/{page_id}/insights?metric=page_impressions</span></td></tr>
  <tr><td class="kpi-name">🤝 Content Interactions</td><td class="kpi-desc">Réactions, commentaires, partages, clics sur les publications.</td><td><span class="endpoint">/{page_id}/insights?metric=page_post_engagements</span></td></tr>
  <tr><td class="kpi-name">📝 Publications</td><td class="kpi-desc">Nombre de posts publiés sur la période.</td><td><span class="endpoint">/{page_id}/posts?fields=id,…</span></td></tr>
  <tr><td class="kpi-name">🔥 Total interactions (posts)</td><td class="kpi-desc">Somme réactions + commentaires + partages de tous les posts.</td><td><span class="endpoint">/{page_id}/posts?fields=reactions,comments,shares</span></td></tr>
  <tr><td class="kpi-name">❤️ Réactions</td><td class="kpi-desc">Total des réactions sur les posts.</td><td><span class="endpoint">/{page_id}/posts?fields=reactions.summary(true)</span></td></tr>
  <tr><td class="kpi-name">💬 Commentaires</td><td class="kpi-desc">Total des commentaires sur les posts.</td><td><span class="endpoint">/{page_id}/posts?fields=comments.summary(true)</span></td></tr>
  <tr><td class="kpi-name">🔁 Partages</td><td class="kpi-desc">Total des partages sur les posts.</td><td><span class="endpoint">/{page_id}/posts?fields=shares</span></td></tr>
</table>""", unsafe_allow_html=True)

    with t2:
        st.markdown("""
<table class="kpi-table">
  <tr><th>Indicateur</th><th>Description</th><th>Endpoint</th></tr>
  <tr><td class="kpi-name">➡️ Net follows</td><td class="kpi-desc">Nouveaux abonnements moins désabonnements.</td><td><span class="endpoint">/{page_id}/insights?metric=page_fan_adds,page_fan_removes</span></td></tr>
  <tr><td class="kpi-name">↗️ Unfollows</td><td class="kpi-desc">Total des désabonnements sur la période.</td><td><span class="endpoint">/{page_id}/insights?metric=page_daily_unfollows</span></td></tr>
  <tr><td class="kpi-name">👤 Followers (Lifetime)</td><td class="kpi-desc">Évolution du total abonnés jour par jour.</td><td><span class="endpoint">/{page_id}/insights/page_fans?period=lifetime</span></td></tr>
</table>""", unsafe_allow_html=True)

    with t3:
        st.markdown("""
<table class="kpi-table">
  <tr><th>Indicateur</th><th>Description</th><th>Endpoint</th></tr>
  <tr><td class="kpi-name">🔥 Total interactions</td><td class="kpi-desc">Somme des interactions de tous les posts sur la période (réactions + commentaires + partages).</td><td><span class="endpoint">/{page_id}/posts?fields=reactions,comments,shares</span></td></tr>
  <tr><td class="kpi-name">❤️ Réactions</td><td class="kpi-desc">Total des réactions sur tous les posts.</td><td><span class="endpoint">/{page_id}/posts?fields=reactions.summary(true)</span></td></tr>
  <tr><td class="kpi-name">💬 Commentaires</td><td class="kpi-desc">Total des commentaires sur tous les posts.</td><td><span class="endpoint">/{page_id}/posts?fields=comments.summary(true)</span></td></tr>
  <tr><td class="kpi-name">🔁 Partages</td><td class="kpi-desc">Total des partages sur tous les posts.</td><td><span class="endpoint">/{page_id}/posts?fields=shares</span></td></tr>
</table>""", unsafe_allow_html=True)

    with t4:
        st.markdown("""
<table class="kpi-table">
  <tr><th>Indicateur</th><th>Description</th><th>Endpoint</th></tr>
  <tr><td class="kpi-name">📏 Avg Daily Reach</td><td class="kpi-desc">Moyenne de comptes uniques touchés par jour.</td><td><span class="endpoint">/{page_id}/insights?metric=page_impressions_unique&period=day</span></td></tr>
  <tr><td class="kpi-name">🏔️ Peak Reach Day</td><td class="kpi-desc">Meilleure journée en portée sur la période.</td><td><span class="endpoint">Calculé depuis la série journalière</span></td></tr>
  <tr><td class="kpi-name">📊 Total Impressions</td><td class="kpi-desc">Nombre total d'affichages sur la période.</td><td><span class="endpoint">/{page_id}/insights?metric=page_impressions&period=day</span></td></tr>
  <tr><td class="kpi-name">🎯 Pic Impressions</td><td class="kpi-desc">Meilleure journée en impressions.</td><td><span class="endpoint">Calculé depuis la série journalière</span></td></tr>
  <tr><td class="kpi-name">📈 Moy. journalière</td><td class="kpi-desc">Moyenne d'impressions par jour.</td><td><span class="endpoint">Calculé depuis la série journalière</span></td></tr>
</table>""", unsafe_allow_html=True)

    with t5:
        st.markdown("""
<p style="color:#a1a1aa;font-size:14px;">Podium Top #3 par portée et Top #3 par engagement. Chaque carte affiche :</p><br>
<table class="kpi-table">
  <tr><th>Métrique carte</th><th>Description</th><th>Endpoint</th></tr>
  <tr><td class="kpi-name">👁️ Reach</td><td class="kpi-desc">Comptes uniques ayant vu ce post (seule métrique d'impression disponible pour New Page Experience).</td><td><span class="endpoint">/{post_id}/insights?metric=post_impressions_unique</span></td></tr>
  <tr><td class="kpi-name">❤️ Réactions</td><td class="kpi-desc">Total des réactions sur le post.</td><td><span class="endpoint">/{post_id}?fields=reactions.summary(true)</span></td></tr>
  <tr><td class="kpi-name">💬 Commentaires</td><td class="kpi-desc">Total des commentaires.</td><td><span class="endpoint">/{post_id}?fields=comments.summary(true)</span></td></tr>
  <tr><td class="kpi-name">🔁 Partages</td><td class="kpi-desc">Total des partages (inclut reposts via post_activity_by_action_type).</td><td><span class="endpoint">/{post_id}/insights?metric=post_activity_by_action_type</span></td></tr>
  <tr><td class="kpi-name">🖱️ Clics</td><td class="kpi-desc">Total des clics sur le post (liens, photo, nom de page).</td><td><span class="endpoint">/{post_id}/insights?metric=post_clicks</span></td></tr>
  <tr><td class="kpi-name">⚡ Total interactions</td><td class="kpi-desc">Réactions + Commentaires + Partages.</td><td><span class="endpoint">Calculé</span></td></tr>
</table>""", unsafe_allow_html=True)

    with t6:
        st.markdown("""
<table class="kpi-table">
  <tr><th>Indicateur</th><th>Description</th><th>Endpoint</th></tr>
  <tr><td class="kpi-name">🆕 Nouveaux contacts</td><td class="kpi-desc">Nouvelles conversations initiées en DM.</td><td><span class="endpoint">/{page_id}/insights?metric=page_messages_new_conversations_unique</span></td></tr>
</table>""", unsafe_allow_html=True)

    st.markdown("<br>", unsafe_allow_html=True)

    # ── Instagram ─────────────────────────────────────────────────────────────
    st.markdown('<div class="doc-section-title">📸 Instagram</div>', unsafe_allow_html=True)

    i1, i2, i3, i4 = st.tabs(["Vue d'ensemble", "📡 Visibilité", "💬 Engagement", "🏆 Top Contenu"])

    with i1:
        st.markdown("""
<table class="kpi-table">
  <tr><th>Indicateur</th><th>Description</th><th>Endpoint</th></tr>
  <tr><td class="kpi-name">👥 Followers</td><td class="kpi-desc">Total abonnés au compte Instagram.</td><td><span class="endpoint">/{ig_user_id}?fields=followers_count</span></td></tr>
  <tr><td class="kpi-name">📝 Publications</td><td class="kpi-desc">Nombre de posts publiés.</td><td><span class="endpoint">/{ig_user_id}/media?fields=id,timestamp,…</span></td></tr>
  <tr><td class="kpi-name">📊 Taux d'engagement</td><td class="kpi-desc">Total interactions ÷ portée × 100.</td><td><span class="endpoint">Calculé</span></td></tr>
  <tr><td class="kpi-name">👁️ Couvertures (Reach)</td><td class="kpi-desc">Comptes uniques ayant vu au moins un post.</td><td><span class="endpoint">/{ig_user_id}/insights?metric=reach&period=day</span></td></tr>
  <tr><td class="kpi-name">📢 Impressions (Posts)</td><td class="kpi-desc">Total affichages calculé depuis chaque post individuellement.</td><td><span class="endpoint">/{media_id}?fields=insights.metric(impressions)</span></td></tr>
  <tr><td class="kpi-name">🔖 Enregistrements</td><td class="kpi-desc">Posts sauvegardés par des utilisateurs.</td><td><span class="endpoint">/{media_id}?fields=insights.metric(saved)</span></td></tr>
  <tr><td class="kpi-name">🔥 Total interactions</td><td class="kpi-desc">Likes + commentaires + partages + enregistrements.</td><td><span class="endpoint">Calculé depuis les métriques de chaque post</span></td></tr>
  <tr><td class="kpi-name">❤️ Réactions</td><td class="kpi-desc">Total des J'aime sur les posts.</td><td><span class="endpoint">/{media_id}?fields=insights.metric(total_likes)</span></td></tr>
  <tr><td class="kpi-name">💬 Commentaires</td><td class="kpi-desc">Total des commentaires sur les posts.</td><td><span class="endpoint">/{media_id}?fields=insights.metric(total_comments)</span></td></tr>
  <tr><td class="kpi-name">↗️ Partages</td><td class="kpi-desc">Posts partagés (Stories, DMs, etc.).</td><td><span class="endpoint">/{media_id}?fields=insights.metric(shares)</span></td></tr>
</table>""", unsafe_allow_html=True)

    with i2:
        st.markdown("""
<table class="kpi-table">
  <tr><th>Indicateur</th><th>Description</th><th>Endpoint</th></tr>
  <tr><td class="kpi-name">👁️ Total Reach</td><td class="kpi-desc">Comptes uniques touchés par les posts.</td><td><span class="endpoint">/{ig_user_id}/insights?metric=reach&period=day</span></td></tr>
  <tr><td class="kpi-name">🎯 Pic</td><td class="kpi-desc">Meilleure journée en portée ou impressions.</td><td><span class="endpoint">Calculé depuis la série journalière</span></td></tr>
  <tr><td class="kpi-name">📏 Moy. journalière</td><td class="kpi-desc">Moyenne par jour sur la période.</td><td><span class="endpoint">Calculé depuis la série journalière</span></td></tr>
  <tr><td class="kpi-name">📊 Total Impressions</td><td class="kpi-desc">Somme affichages depuis les métriques de chaque post.</td><td><span class="endpoint">/{media_id}?fields=insights.metric(impressions,views,plays)</span></td></tr>
</table>""", unsafe_allow_html=True)

    with i3:
        st.markdown("""
<table class="kpi-table">
  <tr><th>Indicateur</th><th>Description</th><th>Endpoint</th></tr>
  <tr><td class="kpi-name">🔥 Total interactions</td><td class="kpi-desc">Likes + commentaires + enregistrements.</td><td><span class="endpoint">/{ig_user_id}/insights?metric=likes,comments,shares,saves</span></td></tr>
  <tr><td class="kpi-name">❤️ Réactions</td><td class="kpi-desc">Total des likes sur tous les posts.</td><td><span class="endpoint">/{ig_user_id}/insights?metric=likes&period=day</span></td></tr>
  <tr><td class="kpi-name">💬 Commentaires</td><td class="kpi-desc">Total des commentaires sur tous les posts.</td><td><span class="endpoint">/{ig_user_id}/insights?metric=comments&period=day</span></td></tr>
  <tr><td class="kpi-name">🔖 Enregistrements</td><td class="kpi-desc">Total des sauvegardes.</td><td><span class="endpoint">/{ig_user_id}/insights?metric=saves&period=day</span></td></tr>
</table>""", unsafe_allow_html=True)

    with i4:
        st.markdown("""
<p style="color:#a1a1aa;font-size:14px;">Podium Top #3 par vues et Top #3 par engagement. Chaque carte affiche :</p><br>
<table class="kpi-table">
  <tr><th>Métrique carte</th><th>Description</th><th>Endpoint</th></tr>
  <tr><td class="kpi-name">👁️ Vues</td><td class="kpi-desc">Total affichages du post (impressions).</td><td><span class="endpoint">/{media_id}?fields=insights.metric(impressions,views,plays)</span></td></tr>
  <tr><td class="kpi-name">❤️ Réactions</td><td class="kpi-desc">Total des likes sur le post.</td><td><span class="endpoint">/{media_id}?fields=insights.metric(total_likes)</span></td></tr>
  <tr><td class="kpi-name">💬 Commentaires</td><td class="kpi-desc">Total des commentaires.</td><td><span class="endpoint">/{media_id}?fields=insights.metric(total_comments)</span></td></tr>
  <tr><td class="kpi-name">🔖 Enregistrements</td><td class="kpi-desc">Nombre de fois que le post a été sauvegardé.</td><td><span class="endpoint">/{media_id}?fields=insights.metric(saved)</span></td></tr>
  <tr><td class="kpi-name">↗️ Partages</td><td class="kpi-desc">Partages (Stories, DMs, etc.).</td><td><span class="endpoint">/{media_id}?fields=insights.metric(shares)</span></td></tr>
</table>""", unsafe_allow_html=True)

    st.markdown("<br>", unsafe_allow_html=True)

    # ── Boost ─────────────────────────────────────────────────────────────────
    st.markdown('<div class="doc-section-title">🚀 Boost (Campagnes Payantes)</div>', unsafe_allow_html=True)

    b1, b2, b3, b4 = st.tabs(["📊 Global", "🎯 Conversion", "📋 Toutes les campagnes", "👥 Démographie & Géo"])

    with b1:
        st.markdown("""
<table class="kpi-table">
  <tr><th>Indicateur</th><th>Description</th><th>Endpoint</th></tr>
  <tr><td class="kpi-name">📁 Total campagnes</td><td class="kpi-desc">Nombre de campagnes actives sur la période.</td><td><span class="endpoint">/{ad_account}/campaigns?fields=id,name</span></td></tr>
  <tr><td class="kpi-name">🖱️ Clics sur le lien</td><td class="kpi-desc">Clics sur les liens dans les publicités.</td><td><span class="endpoint">/{ad_account}/insights?fields=inline_link_clicks&level=campaign</span></td></tr>
  <tr><td class="kpi-name">👁️ Comptes touchés</td><td class="kpi-desc">Personnes uniques ayant vu au moins une pub.</td><td><span class="endpoint">/{ad_account}/insights?fields=reach&level=account</span></td></tr>
  <tr><td class="kpi-name">📢 Impressions</td><td class="kpi-desc">Total d'affichages des publicités.</td><td><span class="endpoint">/{ad_account}/insights?fields=impressions&level=campaign</span></td></tr>
  <tr><td class="kpi-name">💸 Coût par clic (CPC)</td><td class="kpi-desc">Budget ÷ nombre de clics.</td><td><span class="endpoint">/{ad_account}/insights?fields=cpc&level=campaign</span></td></tr>
  <tr><td class="kpi-name">📈 CTR</td><td class="kpi-desc">Clics ÷ impressions × 100.</td><td><span class="endpoint">/{ad_account}/insights?fields=ctr&level=campaign</span></td></tr>
  <tr><td class="kpi-name">💰 Montant dépensé</td><td class="kpi-desc">Budget total consommé sur la période.</td><td><span class="endpoint">/{ad_account}/insights?fields=spend&level=campaign</span></td></tr>
  <tr><td class="kpi-name">🔁 Répétition</td><td class="kpi-desc">Impressions ÷ Reach. Fréquence moyenne d'exposition.</td><td><span class="endpoint">/{ad_account}/insights?fields=frequency&level=campaign</span></td></tr>
</table>""", unsafe_allow_html=True)

    with b2:
        st.markdown("""
<p style="color:#a1a1aa;font-size:14px;">Filtre uniquement les campagnes avec un objectif de <strong>conversion</strong>.</p><br>
<table class="kpi-table">
  <tr><th>Indicateur</th><th>Description</th><th>Endpoint</th></tr>
  <tr><td class="kpi-name">🎁 Coût par vente</td><td class="kpi-desc">Budget ÷ nombre de conversions.</td><td><span class="endpoint">/{ad_account}/insights?fields=cost_per_action_type&level=campaign</span></td></tr>
  <tr><td class="kpi-name">✅ Commandes (conv.)</td><td class="kpi-desc">Total des conversions attribuées aux publicités.</td><td><span class="endpoint">/{ad_account}/insights?fields=actions&level=campaign</span></td></tr>
</table>""", unsafe_allow_html=True)

    with b3:
        st.markdown("""
<p style="color:#a1a1aa;font-size:14px;">Tableau de toutes les campagnes. Toutes les métriques viennent du même appel.</p><br>
<table class="kpi-table">
  <tr><th>Champ</th><th>Description</th><th>Endpoint</th></tr>
  <tr><td class="kpi-name">Toutes les colonnes</td><td class="kpi-desc">campaign_name, objective, impressions, reach, inline_link_clicks, spend, cpc, ctr, frequency, actions, cost_per_action_type</td><td><span class="endpoint">/{ad_account}/insights?fields=campaign_name,objective,impressions,reach,…&level=campaign&limit=500</span></td></tr>
</table>""", unsafe_allow_html=True)

    with b4:
        st.markdown("""
<table class="kpi-table">
  <tr><th>Section</th><th>Description</th><th>Endpoint</th></tr>
  <tr><td class="kpi-name">👥 Démographie</td><td class="kpi-desc">Répartition Hommes/Femmes par tranche d'âge.</td><td><span class="endpoint">/{ad_account}/insights?breakdowns=age,gender&fields=reach&level=campaign</span></td></tr>
  <tr><td class="kpi-name">🌍 Géographie</td><td class="kpi-desc">Top villes/régions par portée.</td><td><span class="endpoint">/{ad_account}/insights?breakdowns=region&fields=reach&level=campaign</span></td></tr>
  <tr><td class="kpi-name">🧠 Analyse automatique</td><td class="kpi-desc">CTR, CPC vs benchmarks secteur.</td><td><span class="endpoint">Calculé depuis les données campagnes</span></td></tr>
</table>""", unsafe_allow_html=True)

    st.markdown("<br>", unsafe_allow_html=True)

    # ── Limitations ───────────────────────────────────────────────────────────
    with st.expander("⚠️ Limitations & Données Indisponibles", expanded=False):
        st.markdown("""
<div style="margin-bottom:0.8rem;font-size:0.9rem;color:#a1a1aa;">
Certains indicateurs affichent <strong style="color:#E8420A;">—</strong> ou peuvent différer de Meta Business Suite.
Ce n'est pas une erreur du dashboard — ce sont des contraintes imposées par l'API Meta.
</div>
""", unsafe_allow_html=True)

        st.markdown("#### 📊 KPIs avec restrictions de période")
        st.markdown("""
| KPI | Comportement | Raison API |
|---|---|---|
| 👁️ **Couvertures** (Instagram) | Affiche **—** si période > 30 jours | `metric_type=total_value` non supporté au-delà de 30 jours |
| 👁️ **Spectateurs** (Facebook) | Affiche **—** sur certaines périodes | Disponible uniquement pour 1j, 2–7j ou 28–31j exactement |
| 📊 **Taux d'engagement** | Affiche **—** quand la portée est indisponible | Formule = Interactions ÷ Portée — impossible sans portée |
""")

        st.markdown("#### 📢 Impressions & Enregistrements")
        st.markdown("""
| KPI | Limitation | Détail |
|---|---|---|
| 📢 **Impressions** (Instagram) | **Stories non incluses** | L'API Meta supprime les données Stories après 24h — seuls le feed et les Reels sont comptabilisés |
| 🔖 **Enregistrements** | Peut différer de Meta Business Suite | Business Suite inclut les Stories enregistrées ; le dashboard comptabilise uniquement les posts du feed & Reels |
| 📢 **Impressions** (Facebook) | Basé sur `post_impressions_unique` | Pour les pages New Page Experience, Meta n'expose que la portée unique par post, pas les impressions brutes |
""")

        st.markdown("#### 💾 Cache & Actualisation")
        st.markdown("""
| Situation | Explication |
|---|---|
| Une publication récente n'apparaît pas | Les données sont mises en cache — cliquez **🔄 Refresh Data** pour forcer le rechargement |
| Les chiffres diffèrent de Business Suite | Business Suite peut utiliser un fuseau horaire ou une fenêtre glissante différente |
| Les données d'hier semblent incomplètes | Meta finalise certaines métriques avec un délai de 24–48h |
""")

        st.info("💡 En cas de doute sur un chiffre, consultez directement **Meta Business Suite** pour le comparer — le dashboard suit la même source de données (Meta Graph API).")

    st.markdown("<br>", unsafe_allow_html=True)

    # ── Glossaire & Fréquence ─────────────────────────────────────────────────
    with st.expander("📚 Glossaire — Termes clés"):
        st.markdown("""
| Terme | Définition |
|---|---|
| **Reach (Portée)** | Comptes **uniques** ayant vu un contenu. Chaque personne comptée une seule fois. |
| **Impressions** | Nombre total d'**affichages**. Une même personne peut générer plusieurs impressions. |
| **Engagement** | Toute interaction active : like, commentaire, partage, clic, enregistrement. |
| **Taux d'engagement** | Engagement ÷ Reach × 100. |
| **CTR** | Click-Through Rate. Clics ÷ Impressions × 100. |
| **CPC** | Coût Par Clic. Budget ÷ Clics. |
| **CPA** | Coût Par Acquisition. Budget ÷ Conversions. |
| **Répétition** | Impressions ÷ Reach. Fois moyenne qu'une personne voit une pub. |
| **Conversion** | Action réalisée après avoir vu une pub (achat, inscription, etc.). |
| **Organique** | Contenu diffusé sans budget, via l'algorithme. |
| **Payant (Boost)** | Contenu promu via un budget Meta Ads. |
""")

    if _is_admin:
        with st.expander("🔄 Fréquence de mise à jour"):
            st.markdown("""
| Source | Fréquence |
|---|---|
| **Toutes les périodes** | Chargées au premier accès, puis sauvegardées en base indéfiniment |
| **Bouton Refresh Data** | Rechargement immédiat depuis Meta API — écrase les données en cache |
| **Nouvelle session** | Données servies depuis la base (Supabase) — aucun appel API si déjà en cache |

> Facebook et Instagram : **Meta Graph API v19.0** — Boost : **Meta Marketing API**
""")
