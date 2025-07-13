# app.py
import streamlit as st
from components.auth import exibir_login

# Configuração visual da página inicial (login)
st.set_page_config(page_title="Login", layout="centered")

# Inicializa a flag se ainda não estiver presente
if "logado" not in st.session_state:
    st.session_state["logado"] = False

# Verifica se precisa rerodar após login
if not st.session_state["logado"]:
    if st.session_state.get("aguardar_rerun"):
        st.session_state.pop("aguardar_rerun")
        st.rerun()
    else:
        exibir_login()
        st.stop()
