# pages/3_guia.py
import streamlit as st
import pandas as pd
from collections import defaultdict
from utils.excel_loader import carregar_guia_qualidade
from utils.html_formatter import formatar_html_guia
from components.auth_guard import proteger_pagina, mostrar_sidebar

# ✅ Configuração da página
st.set_page_config(page_title="Guia", layout="wide")
st.title("📘 Guia de Qualidade")

# ✅ Verificação de autenticação
usuario = proteger_pagina()
mostrar_sidebar(usuario)

st.markdown("Diretrizes de Qualidade")

# ✅ Carregamento e exibição do guia
try:
    df = carregar_guia_qualidade()
    
    # Agrupamento por área
    areas_agrupadas = defaultdict(list)
    for _, row in df.iterrows():
        area = row["AREA"]
        topico = row["TÓPICOS"]
        descricao = row["DESCRIÇÃO"]
        areas_agrupadas[area].append({"topico": topico, "descricao": descricao})

    area_aberta = st.session_state.get("area_aberta", "")

    for area, topicos in areas_agrupadas.items():
        expanded_area = (area == area_aberta)
        with st.expander(f"🟢 {area}", expanded=expanded_area):
            if expanded_area:
                st.session_state["area_aberta"] = area
            for item in topicos:
                topico = item["topico"]
                descricao = item["descricao"]
                descricao_formatada = formatar_html_guia(descricao)

                with st.expander(f"🔹 {topico}", expanded=False):
                    st.markdown(descricao_formatada, unsafe_allow_html=True)

except Exception as e:
    st.error(f"Erro ao carregar o guia: {e}")
