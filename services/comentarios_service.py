from datetime import datetime
from supabase import create_client
import streamlit as st
# Cliente Supabase
from services.supabase_client import supabase


def salvar_comentarios_padrao(usuario, comentarios):
    try:
        registros = [
            {
                "topico": topico,
                "comentario": comentario,
                "usuario": usuario,
                "atualizado_em": datetime.now().isoformat()
            }
            for topico, comentario in comentarios.items()
        ]
        supabase.table("comentarios_padrao").upsert(registros, on_conflict="topico,usuario").execute()
        return True
    except Exception as e:
        st.error(f"Erro ao salvar comentários: {e}")
        return False

def carregar_comentarios_padrao(usuario):
    try:
        res = supabase.table("comentarios_padrao").select("topico, comentario").eq("usuario", usuario).execute()
        return {item["topico"]: item["comentario"] for item in res.data} if res.data else {}
    except Exception as e:
        st.error(f"Erro ao carregar comentários: {e}")
        return {}

