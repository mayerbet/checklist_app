from datetime import datetime
from supabase import create_client
import streamlit as st

# Cliente Supabase
SUPABASE_URL = st.secrets["supabase"]["url"]
SUPABASE_KEY = st.secrets["supabase"]["key"]
supabase = create_client(SUPABASE_URL, SUPABASE_KEY)

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

