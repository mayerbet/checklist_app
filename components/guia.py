# components/guia.py
import streamlit as st
import pandas as pd
from utils.excel_loader import carregar_guia_qualidade
from collections import defaultdict

def formatar_html_guia(texto):
    """Aplica formatação HTML ao conteúdo vindo do Excel."""
    texto = texto.replace("**", "<strong>")
    texto = texto.replace("    ", "&nbsp;&nbsp;&nbsp;&nbsp;")
    texto = texto.replace("\n", "<br>")

    # Corrige títulos que vêm como ### Título
    texto = texto.replace("###", "<h4>").replace("<br><h4>", "<h4>")  # evita quebrar linha antes de h4
    texto = texto.replace(":", "</h4>:")  # fecha o h4 ao final do título

    return texto

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

        # Controle de expansão única
        area_aberta = st.session_state.get("area_aberta", "")

        for area, topicos in areas_agrupadas.items():
            expanded_area = (area == area_aberta)
            with st.expander(f"📂 {area}", expanded=expanded_area):
                if expanded_area:
                    st.session_state["area_aberta"] = area
                for item in topicos:
                    topico = item["topico"]
                    descricao = item["descricao"]
                    descricao_formatada = formatar_html_guia(descricao)

                    with st.expander(f"🔸 {topico}", expanded=False):
                        st.markdown(descricao_formatada, unsafe_allow_html=True)

    except Exception as e:
        st.error(f"Erro ao carregar o guia: {e}")
