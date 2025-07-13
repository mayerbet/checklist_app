# pages/1_Checklist.py
import streamlit as st
import pandas as pd
from datetime import datetime
from services.historico_service import salvar_historico_supabase
from services.comentarios_service import carregar_comentarios_padrao
from utils.excel_loader import carregar_planilha
from components.auth_guard import proteger_pagina, mostrar_sidebar

# ✅ Título da página
st.markdown("<a name='top'></a>", unsafe_allow_html=True)
st.set_page_config(page_title="Checklist", layout="wide")
st.title("📋 Checklist de Qualidade")

# ✅ Verificação de autenticação
usuario = proteger_pagina()
mostrar_sidebar(usuario)

st.markdown("Preencha o checklist. Comentários serão gerados automaticamente com base nas marcações.")

try:
    xls = carregar_planilha()
    checklist_df = pd.read_excel(xls, sheet_name="Checklist")
    checklist = checklist_df.iloc[1:].reset_index(drop=True)
    checklist.columns = ['Index', 'Topico', 'Marcacao', 'Comentario', 'Observacoes', 'Relatorio']

    # ✅ Botão de limpar antes dos widgets
    if st.button("🧹 Limpar"):
        for i in range(len(checklist)):
            st.session_state.pop(f"resp_{i}", None)
            st.session_state.pop(f"coment_{i}_text_area", None)
        st.session_state["texto_editado"] = ""
        st.session_state["relatorio_gerado"] = False
        st.rerun()

    comentarios_usuario = carregar_comentarios_padrao(usuario)
    respostas = []

    for i, row in checklist.iterrows():
        topico = row['Topico']
        st.markdown(f"### {topico}")
        col1, col2 = st.columns([1, 3])

        with col1:
            resposta_default = st.session_state.get(f"resp_{i}", "OK")
            resposta = st.radio(
                f"Selecione para o tópico {i+1}",
                options=['OK', 'X', 'N/A'],
                index=['OK', 'X', 'N/A'].index(resposta_default),
                key=f"resp_{i}"
            )

        with col2:
            comentario_manual = ""
            if resposta != 'OK':
                comentario_manual = st.text_area(
                    f"Comentário adicional (opcional)",
                    key=f"coment_{i}_text_area",
                    height=100
                )
        respostas.append({
            "Topico": topico,
            "Marcacao": resposta,
            "ComentarioManual": comentario_manual,
            "Indice": i
        })

    if st.button("✅ Gerar Relatório"):
        comentarios = []
        for r in respostas:
            if r["Marcacao"] in ["X", "N/A"]:
                comentario_padrao = comentarios_usuario.get(r["Topico"], "Comentário não encontrado.")
                prefixo = "🟡 N/A:" if r["Marcacao"] == "N/A" else "❌"
                comentario_final = f"{prefixo} {comentario_padrao}"
                if r["ComentarioManual"]:
                    comentario_final += f"\n(Obs: {r['ComentarioManual']})"
                comentarios.append((r["Indice"], comentario_final, r["Marcacao"]))

        ultimos_5_idx = set(range(len(respostas) - 5, len(respostas)))
        prioridade = [c for c in comentarios if c[0] in ultimos_5_idx and c[2] == "X"]
        restantes = [c for c in comentarios if c not in prioridade]
        comentarios_final = prioridade + restantes
        texto_gerado = "\n\n".join([c[1] for c in comentarios_final])

        st.session_state["texto_editado"] = texto_gerado
        st.session_state["relatorio_gerado"] = True

    if st.session_state.get("relatorio_gerado"):
        st.text_area(
            "📝 Edite o texto, se necessário:",
            value=st.session_state.get("texto_editado", ""),
            height=400,
            key="texto_editado_area"
        )
        nome_atendente = st.text_input("Nome do atendente:", key="nome_atendente")
        contato_id = st.text_input("ID do atendimento:", key="contato_id")

        if st.button("📅 Salvar Histórico"):
            if nome_atendente and contato_id:
                st.session_state["texto_editado"] = st.session_state.get("texto_editado_area", "")
                sucesso = salvar_historico_supabase(
                    datetime.now().isoformat(),
                    nome_atendente,
                    contato_id,
                    st.session_state["texto_editado"],
                    usuario
                )
                if sucesso:
                    st.success("✔️ Salvo com sucesso no histórico!")
                    st.session_state["relatorio_gerado"] = False
                else:
                    st.error("❌ Erro ao salvar no histórico.")
            else:
                st.warning("⚠️ Preencha todos os campos para salvar.")

except Exception as e:
    st.error(f"Erro ao carregar checklist: {e}")

