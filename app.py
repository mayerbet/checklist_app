import streamlit as st
import pandas as pd
import io

st.set_page_config(page_title="Checklist de Qualidade", layout="wide")

st.title("📊 Análise de Qualidade de Atendimentos - Checklist")
st.markdown("Preencha o checklist abaixo. Comentários serão gerados automaticamente com base nas marcações.")

# Upload do arquivo Excel
uploaded_file = st.file_uploader("📂 Envie sua planilha base (.xlsx)", type="xlsx")

if uploaded_file:
    # Lendo as abas necessárias
    xls = pd.ExcelFile(uploaded_file)
    checklist_df = pd.read_excel(xls, sheet_name="Checklist")
    config_df = pd.read_excel(xls, sheet_name="Config")

    # Limpeza: pulando o cabeçalho extra
    checklist = checklist_df.iloc[1:].reset_index(drop=True)
    checklist.columns = ['Index', 'Topico', 'Marcacao', 'Comentario', 'Observacoes', 'Relatorio']

    config = config_df.iloc[1:].reset_index(drop=True)
    config.columns = ['Index', 'Topico', 'ComentarioPadrao']

    # Interface do checklist
    respostas = []
    st.subheader("🔢 Checklist Interativo")
    for i, row in checklist.iterrows():
        topico = row['Topico']
        st.markdown(f"### {topico}")

        col1, col2 = st.columns([1, 3])
        with col1:
            resposta = st.radio(
                label=f"Selecione para o tópico {i+1}",
                options=['OK', 'X', 'N/A'],
                index=0,
                key=f"resp_{i}"
            )
        with col2:
            comentario_manual = ""
            if resposta != 'OK':
                comentario_manual = st.text_input(f"Comentário adicional (opcional)", key=f"coment_{i}")

        respostas.append({
            "Topico": topico,
            "Marcacao": resposta,
            "ComentarioManual": comentario_manual
        })

    # Geração dos comentários finais
    if st.button("✅ Gerar Comentários"):
        st.subheader("📃 Resultado Final")
        texto_final = ""
        for r in respostas:
            if r["Marcacao"] == "X":
                base = config[config['Topico'] == r['Topico']]
                comentario_padrao = base['ComentarioPadrao'].values[0] if not base.empty else "Comentário não encontrado."
                comentario_final = f"- {comentario_padrao}"
                if r['ComentarioManual']:
                    comentario_final += f" ({r['ComentarioManual']})"
                texto_final += comentario_final + "\n"
        if texto_final:
            st.code(texto_final, language="markdown")
            st.download_button("💾 Baixar Comentários", data=texto_final, file_name="comentarios.txt")
        else:
            st.info("Nenhuma marcação com 'X' foi encontrada.")
else:
    st.warning("Envie a planilha base para iniciar o checklist.")
