import streamlit as st
import pandas as pd
from services.historico_service import supabase

def exibir_historico(usuario: str):
    st.subheader("📚 Histórico de Análises")

    if not usuario:
        st.info("Informe o nome de usuário no menu lateral para visualizar seu histórico.")
        return

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

