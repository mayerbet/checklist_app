# pages/2_Comentarios.py
import streamlit as st
import pandas as pd
from services.comentarios_service import carregar_comentarios_padrao, salvar_comentarios_padrao
from utils.excel_loader import carregar_planilha
from components.auth_guard import proteger_pagina, mostrar_sidebar

# ✅ Configuração da página
st.set_page_config(page_title="Comentários Padrão", layout="wide")
st.title("🗒️ Comentários Padrão")

# ✅ Verificação de autenticação
usuario = proteger_pagina()
mostrar_sidebar(usuario)

st.markdown("Registre ou personalize seus comentários para cada tópico:")

try:
    xls = carregar_planilha()
    df_config = pd.read_excel(xls, sheet_name="Config", skiprows=1)
    df_config.columns = ["Index", "Topico", "ComentarioPadrao"]

    comentarios_existentes = carregar_comentarios_padrao(usuario)
    comentarios_atualizados = {}

    for i, row in df_config.iterrows():
        topico = row['Topico']
        comentario_padrao = comentarios_existentes.get(topico, row['ComentarioPadrao'])
        novo_comentario = st.text_area(
            f"✏️ {topico}",
            value=comentario_padrao,
            key=f"coment_config_{i}",
            height=200
        )
        comentarios_atualizados[topico] = novo_comentario

    if st.button("💾 Salvar Comentários"):
        sucesso = salvar_comentarios_padrao(usuario, comentarios_atualizados)
        if sucesso:
            st.success("💾 Comentários salvos com sucesso!")

except Exception as e:
    st.error(f"Erro ao carregar comentários: {e}")
