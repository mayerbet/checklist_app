import streamlit as st
from components.auth import exibir_login

if "logado" not in st.session_state or not st.session_state["logado"]:
    exibir_login()
    st.stop()  # Impede que o app continue se não estiver logado

# Configuração inicial do app
st.set_page_config(page_title="Checklist de Qualidade", layout="wide")
st.markdown("<a name='top'></a>", unsafe_allow_html=True)
st.title("📋 Análise de QA")

# Importações dos módulos locais conforme a nova estrutura
from components.checklist import exibir_checklist
from components.historico import exibir_historico
from components.comentarios import exibir_configuracoes
from components.guia import exibir_guia

# Sidebar - Seleção de usuário
if st.session_state.get("autenticado"):
    st.sidebar.markdown(f"👤 **Usuário logado:** `{st.session_state['usuario_logado']}`")

# Navegação por abas
aba = st.sidebar.radio("Navegação", [
    "Checklist",
    "Comentários Padrão",
    "Histórico de análises",
    "Guia de Qualidade"
])

# Direcionamento das páginas
if aba == "Checklist":
    exibir_checklist(usuario)
elif aba == "Comentários Padrão":
    exibir_configuracoes(usuario)
elif aba == "Histórico de análises":
    exibir_historico(usuario)
elif aba == "Guia de Qualidade":
    exibir_guia(usuario)
    
if st.session_state.get("autenticado"):
    if st.sidebar.button("🚪 Logout"):
        for key in ["autenticado", "usuario_logado"]:
            st.session_state.pop(key, None)
        st.rerun()

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

