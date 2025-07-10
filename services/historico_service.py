from datetime import datetime
from supabase import create_client
import streamlit as st

# Cliente Supabase
from services.supabase_client import supabase


def salvar_historico_supabase(data_analise, nome_atendente, contato_id, texto_editado, usuario):
    try:
        data = {
            "data": data_analise,
            "atendente": nome_atendente,
            "contato_id": contato_id,
            "resultado": texto_editado,
            "usuario": usuario
        }
        res = supabase.table("history").insert(data).execute()
        return bool(res and res.data)
    except Exception as e:
        st.error(f"Exceção ao salvar no Supabase: {e}")
        return False

