import streamlit as st

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
st.sidebar.subheader("👤 Usuário")
if "usuario" not in st.session_state:
    st.session_state["usuario"] = ""

usuario = st.sidebar.text_input("Digite seu nome", value=st.session_state["usuario"], key="usuario_input")
st.session_state["usuario"] = usuario.strip()

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

