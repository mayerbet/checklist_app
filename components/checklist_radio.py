import streamlit as st
import pandas as pd
from datetime import datetime
from services.historico_service import salvar_historico_supabase
from services.comentarios_service import carregar_comentarios_padrao
from utils.excel_loader import carregar_planilha


def exibir_checklist(usuario):
    st.subheader("✅ Checklist de Análise de Qualidade")

    if not usuario:
        st.warning("Usuário não identificado.")
        return

    try:
        xls = carregar_planilha()
        checklist_df = pd.read_excel(xls, sheet_name="Checklist")
        checklist = checklist_df.iloc[1:].reset_index(drop=True)
        checklist.columns = ['Index', 'Topico', 'Marcacao', 'Comentario', 'Observacoes', 'Relatorio']

        # Botão de limpar
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
                        "Comentário adicional (opcional)",
                        key=f"coment_{i}_text_area",
                        height=100
                    )
            respostas.append({
                "Topico": topico,
                "Marcacao": resposta,
                "ComentarioManual": comentario_manual,
                "Indice": i
            })

        # Botão gerar relatório
        if st.button("✅ Gerar Relatório"):
            comentarios = []
            for r in respostas:
                if r["Marcacao"] in ["X", "N/A"]:
                    comentario_padrao = comentarios_usuario.get(r["Topico"], "Comentário não encontrado.")
                    prefixo = "🟡 N/A:" if r["Marcacao"] == "N/A" else "❌"

                    # Inserir comentário manual dentro do corpo do comentário padrão (após marcador '>')
                    if r["ComentarioManual"] and '>' in comentario_padrao:
                        comentario_formatado = comentario_padrao.replace(
                            '>',
                            f'> (Obs: {r["ComentarioManual"]})',
                            1  # só substitui o primeiro
                        )

                    else:
                        comentario_formatado = comentario_padrao
                        if r["ComentarioManual"]:
                            comentario_formatado += f"\n(Obs: {r['ComentarioManual']})"

                    comentario_final = f"{prefixo} {comentario_formatado}"
                    comentarios.append((r["Indice"], comentario_final, r["Marcacao"]))

            ultimos_5_idx = set(range(len(respostas) - 5, len(respostas)))
            prioridade = [c for c in comentarios if c[0] in ultimos_5_idx and c[2] == "X"]
            restantes = [c for c in comentarios if c not in prioridade]
            comentarios_final = prioridade + restantes
            texto_gerado = "\n\n".join([c[1] for c in comentarios_final])

            st.session_state["texto_editado"] = texto_gerado
            st.session_state["relatorio_gerado"] = True

        # Exibição do relatório + salvamento
        if st.session_state.get("relatorio_gerado"):
            st.text_area(
                "📝 Edite o texto, se necessário:",
                value=st.session_state.get("texto_editado", ""),
                height=400,
                key="texto_editado_area"
            )
            nome_atendente = st.text_input("Nome do GC:", key="nome_atendente")
            contato_id = st.text_input("ID do chat:", key="contato_id")

            if st.button("📅 Salvar Histórico", key="salvar_historico"):
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
                        st.success("✔️ Salvo com sucesso!")
                        st.session_state["relatorio_gerado"] = False
                    else:
                        st.error("❌ Erro ao salvar no histórico.")
                else:
                    st.warning("⚠️ Preencha todos os campos para salvar.")

    except Exception as e:
        st.error(f"Erro ao carregar checklist: {e}")
