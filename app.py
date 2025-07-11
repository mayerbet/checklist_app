import streamlit as st

# Configurações iniciais
st.set_page_config(page_title="Checklist de Qualidade", layout="wide")
st.markdown("<a name='top'></a>", unsafe_allow_html=True)
st.title("📋 Análise de QA")

# Importações dos módulos
from components.checklist import exibir_checklist
from components.comentarios import exibir_configuracoes
from components.historico import exibir_historico
from pages.guia import exibir_guia  # ✅ novo!

# Sidebar - seleção de usuário
st.sidebar.subheader("👤 Usuário")
if "usuario" not in st.session_state:
    st.session_state["usuario"] = ""

usuario = st.sidebar.text_input("Digite seu nome", value=st.session_state["usuario"], key="usuario_input")
st.session_state["usuario"] = usuario.strip()

# Navegação principal
aba = st.sidebar.radio("Navegação", [
    "Checklist",
    "Comentários Padrão",
    "Histórico de análises",
    "Guia de Qualidade"  # ✅ novo item
])

# Exibição conforme aba
if aba == "Checklist":
    exibir_checklist()
elif aba == "Comentários Padrão":
    exibir_configuracoes()
elif aba == "Histórico de análises":
    exibir_historico()
elif aba == "Guia de Qualidade":
    exibir_guia()  # ✅ chamada direta do guia
