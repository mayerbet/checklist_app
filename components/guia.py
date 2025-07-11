# components/guia.py

import streamlit as st
import pandas as pd
from utils.excel_loader import carregar_guia_qualidade

def exibir_guia(usuario):
    st.subheader("📘 Guia de Qualidade")

    try:
        df_guia = carregar_guia_qualidade()

        # Menu de seleção de tópico
        topicos = df_guia["TÓPICOS"].dropna().tolist()
        topico_selecionado = st.selectbox("🔍 Selecione um tópico:", topicos)

        # Mostra a DESCRIÇÃO correspondente
        descricao = df_guia.loc[df_guia["TÓPICOS"] == topico_selecionado, "DESCRIÇÃO"].values[0]
        st.markdown(f"### 📝 DESCRIÇÃO do tópico:\n\n{descricao}")

    except Exception as e:
        st.error(f"Erro ao carregar o guia: {e}")
