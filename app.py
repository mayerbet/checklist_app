# app.py
import streamlit as st
from components.auth import exibir_login

# Login obrigatório
if "logado" not in st.session_state:
    st.session_state["logado"] = False

if not st.session_state["logado"]:
    if st.session_state.get("aguardar_rerun"):
        st.session_state.pop("aguardar_rerun")
        st.rerun()
    else:
        exibir_login()
        st.stop()

# ✅ Usuário logado
usuario = st.session_state.get("usuario_logado", "")

# ✅ Config inicial
st.set_page_config(page_title="Checklist de Qualidade", layout="wide")
st.markdown("<a name='top'></a>", unsafe_allow_html=True)
st.title("📋 Análise de QA")

# ✅ Navegação horizontal no topo
pagina = st.radio("Selecione uma seção:", ["Checklist", "Comentários Padrão", "Histórico", "Guia"], horizontal=True)

# ✅ Redirecionamento
from components import checklist_radio, comentarios_radio, historico_radio, guia_radio

if pagina == "Checklist":
    checklist.exibir_checklist(usuario)
elif pagina == "Comentários Padrão":
    comentarios.exibir_configuracoes(usuario)
elif pagina == "Histórico":
    historico.exibir_historico(usuario)
elif pagina == "Guia":
    guia.exibir_guia(usuario)

# ✅ Logout opcional (se quiser deixar fora do sidebar)
st.markdown(f"👤 Usuário: **{usuario}**")
if st.button("⏻ Logout"):
    for key in ["logado", "usuario_logado"]:
        st.session_state.pop(key, None)
    st.rerun()
