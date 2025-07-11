# components/guia.py
import streamlit as st
import pandas as pd
from utils.excel_loader import carregar_guia_qualidade
from collections import defaultdict

def exibir_guia(usuario):
    st.subheader("📘 Guia de Qualidade")

    try:
        df = carregar_guia_qualidade()
        
        # Agrupa os tópicos por área
        areas_agrupadas = defaultdict(list)
        for _, row in df.iterrows():
            area = row["AREA"]
            topico = row["TÓPICOS"]
            descricao = row["DESCRIÇÃO"]
            areas_agrupadas[area].append({"topico": topico, "descricao": descricao})

        # Variável para controle de expansão exclusiva
        area_aberta = st.session_state.get("area_aberta", "")

        for area, topicos in areas_agrupadas.items():
            with st.expander(f"📂 {area}", expanded=(area == area_aberta)):
                for i, item in enumerate(topicos):
                    topico = item["topico"]
                    descricao = item["descricao"]

                    # Simples parser para negrito e recuos
                    descricao_formatada = (
                        descricao
                        .replace("**", "<b>").replace("__", "</b>")  # opcional para palavras-chave
                        .replace("    ", "&nbsp;&nbsp;&nbsp;&nbsp;")
                        .replace("\n", "<br>")
                    )

                    with st.expander(f"🔸 {topico}", expanded=False):
                        st.markdown(descricao_formatada, unsafe_allow_html=True)

    except Exception as e:
        st.error(f"Erro ao carregar o guia: {e}")
