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
            lines.append("Daily Reach:")
            for pt in rs:
                lines.append(f"  {pt.get('date','?')}: {pt.get('value',0):,}")
        for label, key in [("Top 3 by Views", "top3_by_views"), ("Top 3 by Engagement", "top3_by_engagement")]:
            posts = ig.get(key, [])
            if posts:
                lines.append(f"{label}:")
                for i, p in enumerate(posts, 1):
                    lines.append(f"  #{i} [{p['date']}] {p['text'][:50]} | Views:{p['views']:,} Reach:{p['reach']:,} Likes:{p['likes']:,} Comments:{p['comments']:,} Shares:{p['shares']:,} Saves:{p['saves']:,} Total:{p['total_interactions']:,}")
        all_p = ig.get("all_posts", [])
        if all_p:
            lines.append(f"All {len(all_p)} posts:")
            for p in all_p:
                lines.append(f"  [{p['date']}] {p['media_type']} | {p['text'][:40]} | Views:{p['views']:,} Reach:{p['reach']:,} Likes:{p['likes']:,} Total:{p['total_interactions']:,}")
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
            lines.append("Daily Reach:")
            for pt in rs:
                lines.append(f"  {pt.get('date','?')}: {pt.get('value',0):,}")
        for label, key in [("Top 3 by Reach", "top3_by_reach"), ("Top 3 by Engagement", "top3_by_engagement")]:
            posts = fb.get(key, [])
            if posts:
                lines.append(f"{label}:")
                for i, p in enumerate(posts, 1):
                    lines.append(f"  #{i} [{p['date']}] {p['text'][:50]} | Reach:{p['reach']:,} Reactions:{p['reactions']:,} Comments:{p['comments']:,} Shares:{p['shares']:,} Total:{p['total_interactions']:,}")
        all_p = fb.get("all_posts", [])
        if all_p:
            lines.append(f"All {len(all_p)} posts:")
            for p in all_p:
                lines.append(f"  [{p['date']}] {p['text'][:40]} | Reach:{p['reach']:,} Reactions:{p['reactions']:,} Total:{p['total_interactions']:,}")
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
                lines.append(f"  #{i} {c['name']} | Spend:€{c['spend']:,.2f} Reach:{c['reach']:,} Clicks:{c['clicks']:,} CTR:{c['ctr']}% Conv:{c['conversions']}")
        all_c = bo.get("all_campaigns", [])
        if all_c:
            lines.append(f"All {len(all_c)} campaigns:")
            for c in all_c:
                lines.append(f"  [{c['objective']}] {c['name'][:50]} | Spend:€{c['spend']:,.2f} Reach:{c['reach']:,} CTR:{c['ctr']}% Conv:{c['conversions']}")
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

        response = client.chat.completions.create(
            model="llama-3.3-70b-versatile",
            messages=messages,
            temperature=0.7,
            max_tokens=1024,
        )
        return response.choices[0].message.content
    except Exception as e:
        return f"⚠️ Erreur : {str(e)}"


def render_chatbot():
    """Render a floating chatbot button and panel."""
    _dark = st.session_state.get("theme", "dark") == "dark"

    # ── Initialize session state ──────────────────────────────────────────────
    if "chat_open" not in st.session_state:
        st.session_state.chat_open = False
    if "chat_history" not in st.session_state:
        st.session_state.chat_history = []

    # ── CSS for floating button + panel ──────────────────────────────────────
    _bg       = "#1a1a1a"   if _dark else "#ffffff"
    _border   = "#333333"   if _dark else "#e5e7eb"
    _msg_user = "#003594"
    _msg_bot  = "#262626"   if _dark else "#f3f4f6"
    _text     = "#ffffff"   if _dark else "#111827"
    _subtext  = "#a1a1aa"   if _dark else "#6b7280"

    st.markdown(f"""
<style>
/* Floating button */
#chat-fab {{
    position: fixed;
    bottom: 28px;
    right: 28px;
    width: 56px;
    height: 56px;
    border-radius: 50%;
    background: linear-gradient(135deg, #003594, #0050D0);
    color: white;
    font-size: 24px;
    display: flex;
    align-items: center;
    justify-content: center;
    cursor: pointer;
    z-index: 9999;
    box-shadow: 0 4px 20px rgba(0,53,148,0.5);
    border: none;
    transition: transform 0.2s ease, box-shadow 0.2s ease;
}}
#chat-fab:hover {{
    transform: scale(1.1);
    box-shadow: 0 6px 28px rgba(0,53,148,0.7);
}}

/* Chat panel */
#chat-panel {{
    position: fixed;
    bottom: 96px;
    right: 28px;
    width: 360px;
    max-height: 520px;
    background: {_bg};
    border: 1px solid {_border};
    border-radius: 20px;
    box-shadow: 0 8px 40px rgba(0,0,0,0.35);
    z-index: 9998;
    display: flex;
    flex-direction: column;
    overflow: hidden;
}}
#chat-header {{
    background: linear-gradient(90deg, #003594, #0050D0);
    padding: 14px 18px;
    color: white;
    font-weight: 700;
    font-size: 0.95rem;
    display: flex;
    align-items: center;
    gap: 8px;
}}
#chat-messages {{
    flex: 1;
    overflow-y: auto;
    padding: 14px;
    display: flex;
    flex-direction: column;
    gap: 10px;
    max-height: 340px;
}}
.chat-msg-user {{
    background: {_msg_user};
    color: white;
    padding: 10px 14px;
    border-radius: 16px 16px 4px 16px;
    font-size: 0.85rem;
    align-self: flex-end;
    max-width: 85%;
    line-height: 1.5;
}}
.chat-msg-bot {{
    background: {_msg_bot};
    color: {_text};
    padding: 10px 14px;
    border-radius: 16px 16px 16px 4px;
    font-size: 0.85rem;
    align-self: flex-start;
    max-width: 85%;
    line-height: 1.5;
}}
.chat-msg-sub {{
    font-size: 0.7rem;
    color: {_subtext};
    margin-top: 2px;
}}
@media (max-width: 480px) {{
    #chat-panel {{ width: calc(100vw - 32px); right: 16px; }}
}}
</style>
""", unsafe_allow_html=True)

    # ── Toggle button ─────────────────────────────────────────────────────────
    col_spacer, col_btn = st.columns([10, 1])
    with col_btn:
        btn_icon = "✕" if st.session_state.chat_open else "💬"
        if st.button(btn_icon, key="chat_fab_btn", help="Assistant Dashboard"):
            st.session_state.chat_open = not st.session_state.chat_open
            st.rerun()

    # ── Chat panel ────────────────────────────────────────────────────────────
    if st.session_state.chat_open:
        with st.container():
            st.markdown(f"""
<div id="chat-panel">
  <div id="chat-header">🤖 Assistant Dashboard &nbsp;<span style="font-size:0.75rem;opacity:0.8;">Powered by Groq</span></div>
  <div id="chat-messages">
    {"".join([
        f'<div class="chat-msg-{"user" if m["role"]=="user" else "bot"}">{m["content"]}</div>'
        for m in (st.session_state.chat_history if st.session_state.chat_history
                  else [{"role": "bot", "content": "👋 Bonjour ! Je suis l'assistant du dashboard Skechers. Posez-moi vos questions sur les KPIs, les données ou comment interpréter les chiffres."}])
    ])}
  </div>
</div>
""", unsafe_allow_html=True)

            # Input form
            with st.form(key="chat_form", clear_on_submit=True):
                cols = st.columns([8, 1])
                user_input = cols[0].text_input(
                    "Message",
                    placeholder="Posez votre question...",
                    label_visibility="collapsed",
                )
                submitted = cols[1].form_submit_button("➤")

            if submitted and user_input.strip():
                # Add user message
                st.session_state.chat_history.append({
                    "role": "user",
                    "content": user_input.strip(),
                })
                # Get Gemini response
                with st.spinner("..."):
                    reply = _get_groq_response(st.session_state.chat_history)
                st.session_state.chat_history.append({
                    "role": "assistant",
                    "content": reply,
                })
                st.rerun()

            # Clear chat button
            if st.session_state.chat_history:
                if st.button("🗑️ Effacer la conversation", key="clear_chat"):
                    st.session_state.chat_history = []
                    st.rerun()
