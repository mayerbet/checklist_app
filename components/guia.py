import streamlit as st
import pandas as pd
from utils.excel_loader import carregar_guia_qualidade

def exibir_guia(usuario):
    st.subheader("📘 Guia de Qualidade")

    try:
        df_guia = carregar_guia_qualidade()

        for _, row in df_guia.iterrows():
            topico = row["TÓPICOS"]
            descricao = row["DESCRIÇÃO"]

            # Substitui quebras de linha por <br> e permite HTML
            descricao_formatada = descricao.replace("\n", "<br>")

            with st.expander(f"🔹 {topico}"):
                st.markdown(descricao_formatada, unsafe_allow_html=True)

    except Exception as e:
        st.error(f"Erro ao carregar o guia: {e}")
