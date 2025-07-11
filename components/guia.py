import streamlit as st
import pandas as pd
from utils.excel_loader import carregar_guia_qualidade

st.set_page_config(page_title="Guia de Qualidade", layout="wide")
st.title("📘 Guia de Qualidade")

# Carrega a planilha do guia (uma aba com Tópico e Descrição)
try:
    df_guia = carregar_guia_qualidade()

    # Menu de seleção de tópico
    topicos = df_guia["Tópico"].dropna().tolist()
    topico_selecionado = st.selectbox("🔍 Selecione um tópico:", topicos)

    # Mostra a descrição correspondente
    descricao = df_guia.loc[df_guia["Tópico"] == topico_selecionado, "Descrição"].values[0]
    st.markdown(f"### 📝 Descrição do tópico:\n\n{descricao}")

except Exception as e:
    st.error(f"Erro ao carregar o guia: {e}")

