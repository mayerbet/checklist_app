# pages/4_historico.py
import streamlit as st
import pandas as pd
from datetime import datetime
from services.supabase_client import supabase
from components.auth_guard import proteger_pagina, mostrar_sidebar

# ✅ Configuração da página
st.set_page_config(page_title="Histórico de Análises", layout="wide")
st.title("📚 Histórico de Análises")

# ✅ Verificação de autenticação
usuario = proteger_pagina()
mostrar_sidebar(usuario)

# ✅ Lógica da página
st.markdown("Lista das análises realizadas:")

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
        df = df.drop(columns=[col for col in ["id"] if col in df.columns])

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
