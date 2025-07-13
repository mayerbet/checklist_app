# pages/4_historico.py
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
st.set_page_config(page_title="Historico", layout="wide")
st.title("Historico")

st.markdown("Lista das análises realizadas")

    try:
        resultado = (
            supabase
            .table("history")
            .select("*")
            .eq("usuario", usuario)
            .order("data", desc=True)
            .limit(50)
            .execute()
        )

        registros = resultado.data if resultado and resultado.data else []

        if registros:
            df = pd.DataFrame(registros)

            # Oculta colunas irrelevantes
            colunas_ocultar = ["id"]
            df = df.drop(columns=[col for col in colunas_ocultar if col in df.columns])

            # Ajusta fuso horário e mostra só a data
            if "data" in df.columns:
                df["data"] = pd.to_datetime(df["data"]).dt.tz_convert("America/Sao_Paulo").dt.date

            st.dataframe(df)

            if st.button("🗑️ Limpar Seu Histórico"):
                try:
                    supabase.table("history").delete().eq("usuario", usuario).execute()
                    st.success("Seu histórico foi limpo com sucesso.")
                    st.rerun()
                except Exception as e:
                    st.error(f"Erro ao apagar histórico: {e}")
        else:
            st.warning("Nenhum histórico encontrado para este usuário.")

    except Exception as e:
        st.error(f"Erro ao carregar histórico: {e}")

