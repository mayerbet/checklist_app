import streamlit as st
import pandas as pd
import io

st.set_page_config(page_title="Checklist de Qualidade", layout="wide")
st.markdown("<a name='top'></a>", unsafe_allow_html=True)
# st.image("bet365-logo-0.png", width=300)
# st.markdown("---")
st.title("📋 Análise de QA")
st.markdown("Preencha o checklist abaixo. Comentários serão gerados automaticamente com base nas marcações.")

@st.cache_resource
def carregar_planilha():
    return pd.ExcelFile("checklist_modelo.xlsx")

try:
    if "resetar" not in st.session_state:
        st.session_state["resetar"] = False

    xls = carregar_planilha()
    checklist_df = pd.read_excel(xls, sheet_name="Checklist")
    config_df = pd.read_excel(xls, sheet_name="Config")

    checklist = checklist_df.iloc[1:].reset_index(drop=True)
    checklist.columns = ['Index', 'Topico', 'Marcacao', 'Comentario', 'Observacoes', 'Relatorio']

    config = config_df.iloc[1:].reset_index(drop=True)
    config.columns = ['Index', 'Topico', 'ComentarioPadrao']

    if st.button("🧹 Limpar"):
        for i in range(len(checklist)):
            st.session_state[f"resp_{i}"] = "OK"
            st.session_state[f"coment_{i}"] = ""
        st.session_state["texto_final"] = ""
        st.rerun()

    respostas = []
    st.subheader("🔢 Checklist")
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
                if f"coment_{i}" not in st.session_state:
                    st.session_state[f"coment_{i}"] = comentario_default

                comentario_manual = st.text_area(
                    f"Comentário adicional (opcional)",
                    value=st.session_state[f"coment_{i}"],
                    key=f"coment_{i}_text_area",
                    height=100
                )

        respostas.append({
            "Topico": topico,
            "Marcacao": resposta,
            "ComentarioManual": comentario_manual,
            "Indice": i
        })

    if st.button("Concluído"):
        st.subheader("Relatório")
        comentarios = []

        for r in respostas:
            if r["Marcacao"] in ["X", "N/A"]:
                base = config[config['Topico'] == r['Topico']]
                comentario_padrao = base['ComentarioPadrao'].values[0] if not base.empty else "Comentário não encontrado."
                prefixo = "🟡 N/A:" if r["Marcacao"] == "N/A" else "❌"
                comentario_final = f"{prefixo} {comentario_padrao}"
                if r['ComentarioManual']:
                    comentario_final += f" ({r['ComentarioManual']})"
                comentarios.append((r["Indice"], comentario_final, r["Marcacao"]))

        ultimos_5_idx = set(range(len(respostas) - 5, len(respostas)))
        prioridade = [c for c in comentarios if c[0] in ultimos_5_idx and c[2] == "X"]
        restantes = [c for c in comentarios if c not in prioridade]

        comentarios_final = prioridade + restantes
        comentarios_final = [c[1] for c in comentarios_final]

        if comentarios_final:
            st.session_state["texto_final"] = "\n\n".join(comentarios_final)

    if st.session_state.get("texto_final"):
        if "texto_editado" not in st.session_state:
            st.session_state["texto_editado"] = st.session_state["texto_final"]

        st.session_state["texto_editado"] = st.text_area(
            "📝 Edite, se necessário:",
            value=st.session_state["texto_editado"],
            height=400
        )
    else:
        st.info("Nenhuma marcação relevante foi encontrada.")

    st.markdown("""
        <div style="
        position: fixed;
        bottom: 80px;
        right: 20px;
        z-index: 9999;
        background-color: #005440;
        border-radius: 18px;
        padding: 0.6rem 1rem;
        box-shadow: 0 4px 10px rgba(0,0,0,0.3);
    ">
        <a href='#top' style='text-decoration: none; color: white; font-size: 16px; font-weight: bold;'>
            ToTop
        </a>
    </div>
    """, unsafe_allow_html=True)

except Exception as e:
    st.error(f"Erro ao carregar a planilha: {e}")
