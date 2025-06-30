import streamlit as st
import pandas as pd
import io

st.set_page_config(page_title="Checklist de Qualidade", layout="wide")

st.title("📊QA análise - Checklist")
st.markdown("Preencha o checklist abaixo. Comentários serão gerados automaticamente com base nas marcações.")

# Carrega a planilha fixa do repositório
@st.cache_resource
def carregar_planilha():
    return pd.ExcelFile("checklist_modelo.xlsx")

try:
    if "resetar" not in st.session_state:
        st.session_state["resetar"] = False

    xls = carregar_planilha()
    checklist_df = pd.read_excel(xls, sheet_name="Checklist")
    config_df = pd.read_excel(xls, sheet_name="Config")

    # Limpeza: pulando o cabeçalho extra
    checklist = checklist_df.iloc[1:].reset_index(drop=True)
    checklist.columns = ['Index', 'Topico', 'Marcacao', 'Comentario', 'Observacoes', 'Relatorio']

    config = config_df.iloc[1:].reset_index(drop=True)
    config.columns = ['Index', 'Topico', 'ComentarioPadrao']

    # Botão de reset
    if st.button("🧹 Limpar"):
        for i in range(len(checklist)):
            st.session_state[f"resp_{i}"] = "OK"
            st.session_state[f"coment_{i}"] = ""
        st.rerun()

    # Interface do checklist
    respostas = []
    st.subheader("🔢 Checklist Interativo")
    for i, row in checklist.iterrows():
        topico = row['Topico']
        st.markdown(f"### {topico}")

        col1, col2 = st.columns([1, 3])

        resposta_default = st.session_state.get(f"resp_{i}", "OK")
        comentario_default = st.session_state.get(f"coment_{i}", "")

        with col1:
            resposta = st.radio(
                label=f"Selecione para o tópico {i+1}",
                options=['OK', 'X', 'N/A'],
                index=['OK', 'X', 'N/A'].index(resposta_default),
                key=f"resp_{i}"
            )
        with col2:
            comentario_manual = ""
            if resposta != 'OK':
                comentario_manual = st.text_input(f"Comentário adicional (opcional)", key=f"coment_{i}", value=comentario_default)

        respostas.append({
            "Topico": topico,
            "Marcacao": resposta,
            "ComentarioManual": comentario_manual,
            "Indice": i  # salvar o índice para controle de prioridade
        })

    # Geração dos comentários finais
    if st.button("✅ Gerar Comentários"):
        st.subheader("📃 Resultado Final")
        comentarios_x = []
        comentarios_na = []

        for r in respostas:
            if r["Marcacao"] in ["X", "N/A"]:
                base = config[config['Topico'] == r['Topico']]
                comentario_padrao = base['ComentarioPadrao'].values[0] if not base.empty else "Comentário não encontrado."
                prefixo = "🟢 N/A:" if r["Marcacao"] == "N/A" else "❌"
                comentario_final = f"{prefixo} {comentario_padrao}"
                if r['ComentarioManual']:
                    comentario_final += f" ({r['ComentarioManual']})"

                if r["Marcacao"] == "X":
                    comentarios_x.append((r["Indice"], comentario_final))
                else:
                    comentarios_na.append((r["Indice"], comentario_final))

        # Ordenação: prioriza os últimos 5 tópicos se marcados com X
        comentarios_x.sort(key=lambda x: (x[0] < len(respostas) - 5, x[0]))
        comentarios_final = [c[1] for c in comentarios_x + comentarios_na]

        if comentarios_final:
            texto_final = "\n\n".join(comentarios_final)  # separação entre cada item

            texto_editado = st.text_area("📝 Edite o texto gerado, se necessário:", value=texto_final, height=400)

            # Apenas para ter o botão de copiar como no st.code (funciona mesmo sem mostrar texto duplicado)
            with st.expander("📋 Clique aqui para copiar o texto gerado"):
                st.code(texto_editado, language="markdown")

            st.download_button("💾 Baixar Comentários", data=texto_editado, file_name="comentarios.txt")

        else:
            st.info("Nenhuma marcação relevante foi encontrada.")

except Exception as e:
    st.error(f"Erro ao carregar a planilha: {e}")
