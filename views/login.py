"""
views/login.py — Login page for Footland dashboard.
"""

import streamlit as st
import auth


_LOGIN_CSS = """
<style>
.login-wrapper {
    display: flex;
    flex-direction: column;
    align-items: center;
    justify-content: center;
    min-height: 70vh;
}
.login-box {
    background: #161616;
    border: 1px solid #262626;
    border-radius: 20px;
    padding: 48px 40px;
    width: 100%;
    max-width: 420px;
    box-shadow: 0 8px 40px rgba(0,0,0,0.5);
}
.login-logo {
    font-size: 36px;
    font-weight: 800;
    background: linear-gradient(90deg, #E8420A, #FF6B35, #C1320A);
    -webkit-background-clip: text;
    -webkit-text-fill-color: transparent;
    text-align: center;
    margin-bottom: 4px;
}
.login-sub {
    font-size: 13px;
    color: #71717a !important;
    text-align: center;
    margin-bottom: 32px;
}
</style>
"""


def render_login():
    st.markdown(_LOGIN_CSS, unsafe_allow_html=True)

    _, col, _ = st.columns([1, 2, 1])
    with col:
        st.markdown('<div class="login-logo">⚽ Footland</div>', unsafe_allow_html=True)
        st.markdown('<div class="login-sub">Analytics Dashboard</div>', unsafe_allow_html=True)

        with st.form("login_form", clear_on_submit=False):
            email    = st.text_input("Email", placeholder="votre@email.com")
            password = st.text_input("Mot de passe", type="password", placeholder="••••••••")
            submit   = st.form_submit_button("Se connecter", use_container_width=True)

        if submit:
            if not email or not password:
                st.error("Veuillez remplir tous les champs.")
            else:
                with st.spinner("Connexion..."):
                    try:
                        session = auth.login(email.strip(), password)
                        st.session_state.user = session
                        st.rerun()
                    except ValueError as e:
                        st.error(f"Identifiants incorrects. Veuillez réessayer.")
