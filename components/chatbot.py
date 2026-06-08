"""
components/chatbot.py — Gemini-powered floating chatbot for the Skechers dashboard.
Answers only dashboard-related questions.
"""

import os
import streamlit as st
from dotenv import load_dotenv

load_dotenv()


SYSTEM_PROMPT = """
You are a helpful assistant for the Skechers Algeria social media analytics dashboard.
You ONLY answer questions related to this dashboard — its metrics, KPIs, data sources,
and how to interpret the numbers. If a user asks about anything unrelated to the dashboard,
politely decline and redirect them to dashboard topics.

You respond in the same language the user writes in (French or English or Arabic).

--- DASHBOARD CONTEXT ---

PLATFORMS:
- Facebook: Audience, Engagement, Visibility, Top Content, Community tabs
- Instagram: Visibility, Engagement tabs
- Boost: Paid campaigns (Meta Ads)
- Google Analytics 4: Website traffic and e-commerce

INSTAGRAM KPIs (all from Meta Graph API v22+):
- 👥 Followers: total follower count (profile field)
- 📢 Vues: total views across all content (posts+stories+reels) — from account-level insights metric=views, metric_type=total_value
- 🎯 Couverture: unique accounts reached — metric=reach, metric_type=total_value (only works for ≤30 day windows)
- 🔥 Total interactions: likes+comments+shares+saves — metric=total_interactions, metric_type=total_value
- ❤️ Réactions: total likes (NOT privacy-filtered at account level) — metric=likes, metric_type=total_value
- 💬 Commentaires: total comments — metric=comments, metric_type=total_value
- ↗️ Partages: total shares — metric=shares, metric_type=total_value
- 🔖 Enregistrements: total saves — metric=saves, metric_type=total_value
- 📊 Taux d'engagement: Total interactions ÷ Reach × 100

IMPORTANT INSTAGRAM LIMITATIONS:
- Per-post like_count is privacy-filtered by Meta (e.g. API returns 88 but real count is 2,500). Nothing can be done.
- impressions metric was deprecated by Meta in v22+ for all post types — replaced by views
- views metric_type=time_series is NOT supported — no daily breakdown available for views
- Couverture shows "—" for periods >30 days (API limitation)
- Per-post data fetched via field expansion: fields=insights.metric(views,reach,saved,shares,likes,comments,total_interactions)

FACEBOOK KPIs:
- Followers, Net follows, Unfollows from page_fans, page_fan_adds, page_fan_removes
- Reach from page_impressions_unique
- Impressions from page_impressions
- Engagement from page_post_engagements
- Top Content: podium of top 3 posts by reach and by engagement

BOOST (Paid):
- Campaigns data from Meta Marketing API
- KPIs: spend, reach, impressions, clicks, CTR, CPC, CPM, frequency, conversions
- Only Skechers campaigns (filtered by keywords: SKX, Skechers, page ID)
- Ad account act_765947885726761 is the source

GOOGLE ANALYTICS 4:
- Active users, new users, sessions, engagement rate, bounce rate
- E-commerce funnel: view_item → add_to_cart → begin_checkout → purchase
- Traffic sources, geography, device breakdown

CACHE & REFRESH:
- Data is cached in Supabase permanently
- "Refresh Data" button deletes the cache for the current period and re-fetches from Meta API
- If numbers seem stale, click Refresh Data

DATA SOURCES:
- Facebook & Instagram: Meta Graph API v22+
- Boost: Meta Marketing API
- Google Analytics: GA4 Data API v1beta
- Storage: Supabase (PostgreSQL)

--- END CONTEXT ---

Be concise, helpful, and accurate. If you're not sure about something, say so.
"""


def _get_api_key() -> str:
    """Read Groq API key from st.secrets or environment."""
    try:
        key = st.secrets["GROQ_API_KEY"]
        if key:
            return key.strip()
    except Exception:
        pass
    return os.environ.get("GROQ_API_KEY", "").strip()


def _build_data_context() -> str:
    """Build context from ALL platforms loaded so far in this session."""
    lines = ["\n--- DASHBOARD DATA (ALL PLATFORMS) ---\n"]
    any_data = False

    # ── Instagram ─────────────────────────────────────────────────────────────
    ig = st.session_state.get("ctx_instagram")
    if ig:
        any_data = True
        lines.append(f"=== 📸 INSTAGRAM — {ig.get('period','?')} ===")
        lines += [
            f"Followers: {ig['followers']:,} (prev: {ig.get('prev_followers',0):,})",
            f"Vues: {ig['total_views']:,} (prev: {ig.get('prev_views',0):,})",
            f"Reach: {ig['total_reach']:,} (prev: {ig.get('prev_reach',0):,})",
            f"Total Interactions: {ig['total_interactions']:,} (prev: {ig.get('prev_interactions',0):,})",
            f"Likes: {ig['total_likes']:,} (prev: {ig.get('prev_likes',0):,})",
            f"Commentaires: {ig['total_comments']:,} (prev: {ig.get('prev_comments',0):,})",
            f"Partages: {ig['total_shares']:,} (prev: {ig.get('prev_shares',0):,})",
            f"Enregistrements: {ig['total_saves']:,} (prev: {ig.get('prev_saves',0):,})",
            f"Taux engagement: {ig['engagement_rate']}%",
            f"Publications: {ig['total_posts']}",
        ]
        rs = ig.get("reach_series", [])
        if rs:
            lines.append("Daily Reach (last 7 days):")
            for pt in rs[-7:]:
                lines.append(f"  {pt.get('date','?')}: {pt.get('value',0):,}")
        for label, key in [("Top 3 by Views", "top3_by_views"), ("Top 3 by Engagement", "top3_by_engagement")]:
            posts = ig.get(key, [])
            if posts:
                lines.append(f"{label}:")
                for i, p in enumerate(posts, 1):
                    lines.append(f"  #{i} [{p['date']}] {p['text'][:40]} | Views:{p['views']:,} Reach:{p['reach']:,} Likes:{p['likes']:,} Comments:{p['comments']:,} Shares:{p['shares']:,} Total:{p['total_interactions']:,}")
        lines.append("")

    # ── Facebook ──────────────────────────────────────────────────────────────
    fb = st.session_state.get("ctx_facebook")
    if fb:
        any_data = True
        lines.append(f"=== 🔵 FACEBOOK — {fb.get('period','?')} ===")
        lines += [
            f"Followers: {fb['followers']:,} (prev: {fb.get('prev_followers',0):,})",
            f"Reach: {fb['total_reach']:,} (prev: {fb.get('prev_reach',0):,})",
            f"Impressions: {fb['total_impressions']:,} (prev: {fb.get('prev_impressions',0):,})",
            f"Total Interactions: {fb['total_interactions']:,} (prev: {fb.get('prev_interactions',0):,})",
            f"Reactions: {fb['total_reactions']:,} (prev: {fb.get('prev_reactions',0):,})",
            f"Commentaires: {fb['total_comments']:,} (prev: {fb.get('prev_comments',0):,})",
            f"Partages: {fb['total_shares']:,} (prev: {fb.get('prev_shares',0):,})",
            f"Publications: {fb['total_posts']}",
        ]
        rs = fb.get("reach_series", [])
        if rs:
            lines.append("Daily Reach (last 7 days):")
            for pt in rs[-7:]:
                lines.append(f"  {pt.get('date','?')}: {pt.get('value',0):,}")
        for label, key in [("Top 3 by Reach", "top3_by_reach"), ("Top 3 by Engagement", "top3_by_engagement")]:
            posts = fb.get(key, [])
            if posts:
                lines.append(f"{label}:")
                for i, p in enumerate(posts, 1):
                    lines.append(f"  #{i} [{p['date']}] {p['text'][:40]} | Reach:{p['reach']:,} Reactions:{p['reactions']:,} Comments:{p['comments']:,} Shares:{p['shares']:,} Total:{p['total_interactions']:,}")
        lines.append("")

    # ── Boost ─────────────────────────────────────────────────────────────────
    bo = st.session_state.get("ctx_boost")
    if bo:
        any_data = True
        lines.append(f"=== 🚀 BOOST — {bo.get('period','?')} ===")
        lines += [
            f"Spend: €{bo['total_spend']:,.2f} (prev: €{bo.get('prev_spend',0):,.2f})",
            f"Reach: {bo['total_reach']:,} (prev: {bo.get('prev_reach',0):,})",
            f"Impressions: {bo['total_impressions']:,} (prev: {bo.get('prev_impressions',0):,})",
            f"Clicks: {bo['total_clicks']:,} (prev: {bo.get('prev_clicks',0):,})",
            f"CTR: {bo['ctr']}%  CPC: €{bo['cpc']:,.2f}  Freq: {bo['frequency']}",
            f"Conversions: {bo['total_conversions']}  Campaigns: {bo['total_campaigns']}",
        ]
        top3 = bo.get("top3_campaigns", [])
        if top3:
            lines.append("Top 3 campaigns by spend:")
            for i, c in enumerate(top3, 1):
                lines.append(f"  #{i} {c['name'][:50]} | Spend:€{c['spend']:,.2f} Reach:{c['reach']:,} Clicks:{c['clicks']:,} CTR:{c['ctr']}% Conv:{c['conversions']}")
        lines.append("")

    # ── Google Analytics ──────────────────────────────────────────────────────
    ga = st.session_state.get("ctx_ga4")
    if ga:
        any_data = True
        lines.append(f"=== 📊 GOOGLE ANALYTICS 4 — {ga.get('period','?')} ===")
        lines += [
            f"Active Users: {ga['active_users']:,}  New Users: {ga['new_users']:,}",
            f"Sessions: {ga['sessions']:,}  Engaged: {ga['engaged_sessions']:,}",
            f"Engagement Rate: {ga['engagement_rate']}%  Bounce Rate: {ga['bounce_rate']}%",
            f"Avg Session Duration: {ga['avg_session_duration']:.0f}s",
            f"Page Views: {ga['page_views']:,}  Pages/Session: {ga['pages_per_session']:.2f}",
        ]
        src = ga.get("traffic_sources", [])
        if src:
            lines.append("Traffic Sources:")
            for s in src[:5]:
                lines.append(f"  {s.get('channel','?')}: {s.get('sessions',0):,} sessions ({s.get('pct',0):.1f}%)")
        funnel = ga.get("funnel", [])
        if funnel:
            lines.append("Purchase Funnel:")
            for step in funnel:
                lines.append(f"  {step.get('step','?')}: {step.get('users',0):,} users")
        items = ga.get("top_items", [])
        if items:
            lines.append("Top Products:")
            for item in items[:5]:
                lines.append(f"  {item.get('name','?')} | Viewed:{item.get('viewed',0):,} Cart:{item.get('added_to_cart',0):,} Purchased:{item.get('purchased',0):,}")
        countries = ga.get("top_countries", [])
        if countries:
            lines.append("Top Countries:")
            for c in countries:
                lines.append(f"  {c.get('country','?')}: {c.get('users',0):,} users")
        lines.append("")

    if not any_data:
        lines.append("No data loaded yet. User has not visited any platform tab.")

    lines.append("--- END DASHBOARD DATA ---\n")
    return "\n".join(lines)


def _get_groq_response(history: list) -> str:
    """Call Groq API with conversation history using LLaMA 3.3 70B."""
    try:
        from groq import Groq

        api_key = _get_api_key()
        if not api_key:
            return "⚠️ Clé API Groq manquante. Veuillez configurer GROQ_API_KEY dans les secrets Streamlit."

        client = Groq(api_key=api_key)

        # Build messages with system prompt + dynamic data context
        messages = [
            {"role": "system", "content": SYSTEM_PROMPT + _build_data_context()}
        ]
        for msg in history:
            messages.append({
                "role": "user" if msg["role"] == "user" else "assistant",
                "content": msg["content"],
            })

        for model in ["llama-3.3-70b-versatile", "llama-3.1-8b-instant"]:
            try:
                response = client.chat.completions.create(
                    model=model,
                    messages=messages,
                    temperature=0.7,
                    max_tokens=1024,
                )
                return response.choices[0].message.content
            except Exception as e:
                if "429" in str(e) or "rate_limit" in str(e).lower():
                    continue  # try next model
                return f"⚠️ Erreur : {str(e)}"
        return "⚠️ Les deux modèles ont atteint leur limite quotidienne. Réessayez dans quelques heures."
    except Exception as e:
        return f"⚠️ Erreur : {str(e)}"


def render_chatbot():
    """Render floating chat bubble — fixed-position panel, toggle in sidebar."""
    _dark = st.session_state.get("theme", "dark") == "dark"

    if "chat_history" not in st.session_state:
        st.session_state.chat_history = []

    if not st.session_state.get("chat_open", False):
        return

    # ── Theme tokens ──────────────────────────────────────────────────────────
    _panel_bg  = "#111111" if _dark else "#ffffff"
    _border    = "#2a2a2a" if _dark else "#e5e7eb"
    _msg_bg    = "#1c1c1c" if _dark else "#f3f4f6"
    _msg_tc    = "#ffffff" if _dark else "#111827"
    _ts_c      = "rgba(255,255,255,0.35)" if _dark else "#9ca3af"

    # ── Build messages HTML ───────────────────────────────────────────────────
    if not st.session_state.chat_history:
        msgs_html = f"""
<div style="display:flex;gap:10px;align-items:flex-start;">
  <div style="width:32px;height:32px;border-radius:50%;background:linear-gradient(135deg,#003594,#0050D0);
              display:flex;align-items:center;justify-content:center;font-size:16px;flex-shrink:0;">🤖</div>
  <div style="background:{_msg_bg};color:{_msg_tc};padding:10px 14px;border-radius:4px 16px 16px 16px;
              font-size:0.83rem;line-height:1.6;max-width:85%;">
    👋 <b>Bonjour !</b> Je suis l'assistant du dashboard Skechers.<br><br>
    Posez-moi vos questions sur les KPIs, les données ou comment interpréter les chiffres.
  </div>
</div>"""
    else:
        msgs_html = ""
        for m in st.session_state.chat_history:
            content = m["content"].replace("\n", "<br>").replace("<br><br>", "<br>")
            if m["role"] == "user":
                msgs_html += f"""
<div style="display:flex;gap:10px;align-items:flex-start;justify-content:flex-end;">
  <div style="background:linear-gradient(135deg,#003594,#0050D0);color:white;padding:10px 14px;
              border-radius:16px 4px 16px 16px;font-size:0.83rem;line-height:1.6;max-width:85%;">
    {content}
  </div>
  <div style="width:32px;height:32px;border-radius:50%;background:#333;
              display:flex;align-items:center;justify-content:center;font-size:16px;flex-shrink:0;">👤</div>
</div>"""
            else:
                msgs_html += f"""
<div style="display:flex;gap:10px;align-items:flex-start;">
  <div style="width:32px;height:32px;border-radius:50%;background:linear-gradient(135deg,#003594,#0050D0);
              display:flex;align-items:center;justify-content:center;font-size:16px;flex-shrink:0;">🤖</div>
  <div style="background:{_msg_bg};color:{_msg_tc};padding:10px 14px;border-radius:4px 16px 16px 16px;
              font-size:0.83rem;line-height:1.6;max-width:85%;">
    {content}
  </div>
</div>"""

    # ── Floating panel (fixed position) ───────────────────────────────────────
    st.markdown(f"""
<style>
#chat-float-panel {{
    position: fixed;
    bottom: 80px;
    right: 24px;
    width: 360px;
    height: 500px;
    background: {_panel_bg};
    border: 1px solid {_border};
    border-radius: 20px;
    box-shadow: 0 12px 48px rgba(0,0,0,0.4);
    z-index: 9999;
    display: flex;
    flex-direction: column;
    overflow: hidden;
    animation: chatSlideUp 0.25s ease;
}}
@keyframes chatSlideUp {{
    from {{ opacity:0; transform:translateY(16px); }}
    to   {{ opacity:1; transform:translateY(0); }}
}}
#chat-hdr {{
    background: linear-gradient(90deg,#003594,#0050D0);
    padding: 12px 16px;
    flex-shrink: 0;
}}
#chat-msgs {{
    flex: 1;
    overflow-y: auto;
    padding: 14px 12px;
    display: flex;
    flex-direction: column;
    gap: 12px;
    scrollbar-width: thin;
    scrollbar-color: #333 transparent;
}}
#chat-msgs::-webkit-scrollbar {{ width:4px; }}
#chat-msgs::-webkit-scrollbar-thumb {{ background:#444; border-radius:4px; }}
#chat-footer-note {{
    text-align: center;
    padding: 6px 0 8px;
    font-size: 0.68rem;
    color: {_ts_c};
    flex-shrink: 0;
    border-top: 1px solid {_border};
}}
</style>

<div id="chat-float-panel">
  <div id="chat-hdr">
    <div style="color:white;font-weight:700;font-size:0.92rem;display:flex;align-items:center;gap:8px;">
      🤖 Assistant Dashboard
      <span style="background:rgba(255,255,255,0.15);border-radius:20px;padding:2px 8px;
                   font-size:0.65rem;font-weight:400;">Groq · LLaMA 3.3</span>
    </div>
    <div style="color:rgba(255,255,255,0.6);font-size:0.68rem;margin-top:2px;">
      Posez vos questions sur le dashboard
    </div>
  </div>
  <div id="chat-msgs">
    {msgs_html}
  </div>
  <div id="chat-footer-note">
    Tapez votre question ci-dessous ↓ &nbsp;·&nbsp;
    Données du dashboard chargées automatiquement
  </div>
</div>
""", unsafe_allow_html=True)

    # ── Native chat input (anchors to page bottom) ────────────────────────────
    if prompt := st.chat_input("Posez votre question..."):
        if prompt.strip():
            st.session_state.chat_history.append({"role": "user", "content": prompt.strip()})
            with st.spinner(""):
                reply = _get_groq_response(st.session_state.chat_history)
            st.session_state.chat_history.append({"role": "assistant", "content": reply})
            st.rerun()

    # ── Clear button (small, unobtrusive) ─────────────────────────────────────
    if st.session_state.chat_history:
        _cc1, _cc2, _cc3 = st.columns([3, 1, 3])
        with _cc2:
            if st.button("🗑️", key="clear_chat", help="Effacer la conversation"):
                st.session_state.chat_history = []
                st.rerun()
