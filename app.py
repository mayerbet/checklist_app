import streamlit as st
import pandas as pd

st.set_page_config(page_title="Checklist de Qualidade", layout="wide")

st.title("📊 Análise de Qualidade de Atendimentos - Checklist")
st.markdown("Preencha o checklist abaixo. Comentários serão gerados automaticamente com base nas marcações.")

# Inicialização do estado da sessão
if 'reset' not in st.session_state:
    st.session_state.reset = False

# Carrega a planilha fixa do repositório
@st.cache_resource
def carregar_planilha():
    return pd.ExcelFile("checklist_modelo.xlsx")

try:
    xls = carregar_planilha()
    checklist_df = pd.read_excel(xls, sheet_name="Checklist")
    config_df = pd.read_excel(xls, sheet_name="Config")

    # Limpeza: pulando o cabeçalho extra
    checklist = checklist_df.iloc[1:].reset_index(drop=True)
    checklist.columns = ['Index', 'Topico', 'Marcacao', 'Comentario', 'Observacoes', 'Relatorio']

    config = config_df.iloc[1:].reset_index(drop=True)
    config.columns = ['Index', 'Topico', 'ComentarioPadrao']

    # Botão para limpar a interface - deve vir antes da criação dos widgets
    if st.button("🧹 Limpar e Recomeçar"):
        st.session_state.reset = True
        st.experimental_rerun()

    # Resetar todos os widgets se necessário
    if st.session_state.reset:
        for key in list(st.session_state.keys()):
            if key.startswith("resp_") or key.startswith("coment_"):
                del st.session_state[key]
        st.session_state.reset = False
        st.experimental_rerun()

    # Interface do checklist
    respostas = []
    st.subheader("🔢 Checklist Interativo")
    for i, row in checklist.iterrows():
        topico = row['Topico']
        st.markdown(f"### {topico}")

        col1, col2 = st.columns([1, 3])
        with col1:
            # Usamos um valor padrão se a chave não existir no session_state
            default_index = 0
            if f"resp_{i}" in st.session_state:
                default_index = ['OK', 'X', 'N/A'].index(st.session_state[f"resp_{i}"])
            
            resposta = st.radio(
                label=f"Selecione para o tópico {i+1}",
                options=['OK', 'X', 'N/A'],
                index=default_index,
                key=f"resp_{i}"
            )
        with col2:
            comentario_manual = ""
            if resposta != 'OK':
                # Usamos valor vazio se a chave não existir
                default_value = st.session_state.get(f"coment_{i}", "")
                comentario_manual = st.text_input(
                    f"Comentário adicional (opcional)", 
                    key=f"coment_{i}",
                    value=default_value
                )

        respostas.append({
            "Topico": topico,
            "Marcacao": resposta,
            "ComentarioManual": comentario_manual,
            "Indice": i
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
                prefixo = "🟢 N/A:" if r["Marcacao"] == "N/A" else "🔴"
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
            texto_final = "\n\n".join(comentarios_final)
            texto_editado = st.text_area("📝 Edite o texto gerado, se necessário:", value=texto_final, height=400)
            st.download_button("💾 Baixar Comentários", data=texto_editado, file_name="comentarios.txt")
        else:
            st.info("Nenhuma marcação relevante foi encontrada.")
            
except Exception as e:
    st.error(f"Erro ao carregar a planilha: {e}")
