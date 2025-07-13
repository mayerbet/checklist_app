# components/auth_guard.py
import streamlit as st

def proteger_pagina():
    if "logado" not in st.session_state or not st.session_state["logado"]:
        st.warning("Você precisa estar logado para acessar esta página.")
        st.stop()
    return st.session_state.get("usuario_logado", "")

def mostrar_sidebar(usuario):
    st.sidebar.markdown(f"👤 `{usuario}`")
    if st.sidebar.button("🚪 Logout"):
        for key in ["logado", "usuario_logado"]:
            st.session_state.pop(key, None)
        st.switch_page("app.py")

