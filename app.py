import streamlit as st
from components.auth import exibir_login

# Impede acesso se não estiver logado
if "logado" not in st.session_state or not st.session_state["logado"]:
    exibir_login()
    st.stop()

# Configuração do app
st.set_page_config(page_title="Checklist de Qualidade", layout="wide")
st.markdown("<a name='top'></a>", unsafe_allow_html=True)
st.title("📋 Análise de QA")

# Imports dos módulos
from components.checklist import exibir_checklist
from components.historico import exibir_historico
from components.comentarios import exibir_configuracoes
from components.guia import exibir_guia

# Define usuário logado
usuario = st.session_state.get("usuario_logado", "")

# Sidebar
st.sidebar.markdown(f"👤 **Usuário logado:** `{usuario}`")
if st.sidebar.button("🚪 Logout"):
    for key in ["logado", "usuario_logado"]:
        st.session_state.pop(key, None)
    st.rerun()

# Navegação
aba = st.sidebar.radio("Navegação", [
    "Checklist",
    "Comentários Padrão",
    "Histórico de análises",
    "Guia de Qualidade"
])

# Direcionamento
if aba == "Checklist":
    exibir_checklist(usuario)
elif aba == "Comentários Padrão":
    exibir_configuracoes(usuario)
elif aba == "Histórico de análises":
    exibir_historico(usuario)
elif aba == "Guia de Qualidade":
    exibir_guia(usuario)

# Fixar botão "topo"
st.markdown("""
    <div style="
        position: fixed;
        bottom: 80px;
        right: 20px;
        z-index: 9999;
        background-color: #005440;
        border-radius: 18px;
        padding: 0.6rem 1rem;
        box-shadow: 0 4px 10px rgba(0,0,0,0.3);
    ">
    <a href='#top' style='text-decoration: none; color: white; font-size: 16px; font-weight: bold;'>
        ToTop
    </a>
    </div>
""", unsafe_allow_html=True)
