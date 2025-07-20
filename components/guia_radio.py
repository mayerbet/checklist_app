# components/guia.py
import streamlit as st
import pandas as pd
from utils.excel_loader import carregar_guia_qualidade
from collections import defaultdict
from utils.html_formatter import formatar_html_guia
from services.supabase_client import supabase


def exibir_guia(usuario):
    st.subheader("📘 Guia de Qualidade")

    try:
       # df = carregar_guia_qualidade()
        df = carregar_guia_qualidade().fillna("").astype(str)
        # Botão para salvar no Supabase
        if st.button("💾 Salvar Guia no Supabase"):
            try:
                registros = []
                for _, row in df.iterrows():
                    registros.append({
                        "area": row["AREA"],
                        "topico": row["TÓPICOS"],
                        "descricao": row["DESCRIÇÃO"]
                    })
                                
                resposta = supabase.table("guide").upsert(registros).execute()
                st.success("✅ Guia salvo no Supabase com sucesso!")
            except Exception as e:
                st.error(f"❌ Erro ao salvar no Supabase: {e}")

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
