# pages/3_guia.py
import streamlit as st
import pandas as pd
from datetime import datetime
from services.historico_service import salvar_historico_supabase
from services.comentarios_service import carregar_comentarios_padrao
from utils.excel_loader import carregar_planilha

# ✅ Verificação de autenticação
if "logado" not in st.session_state or not st.session_state["logado"]:
    st.warning("Você precisa estar logado para acessar esta página.")
    st.stop()

usuario = st.session_state["usuario_logado"]

# ✅ Título da página
st.set_page_config(page_title="Guia", layout="wide")
st.title("Guia de Qualidade")

st.markdown("Diretrizes de Qualidade")

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
