import streamlit as st
import pandas as pd
import io

st.set_page_config(page_title="Checklist de Qualidade", layout="wide")
# Estilo global
st.markdown("""
    <style>
    /* Fonte padrão e tamanho base */
    html, body, [class*="css"] {
        font-family: 'Segoe UI', sans-serif;
        font-size: 16px;
        color: #333333;
    }

    /* Títulos */
    h1, h2, h3 {
        color: #0E5C86;
        margin-bottom: 0.3rem;
    }

    /* Caixa do checklist */
    .checklist-box {
        background-color: #f9f9f9;
        border-radius: 10px;
        padding: 1.2rem;
        box-shadow: 0 2px 6px rgba(0,0,0,0.08);
        margin-bottom: 1.5rem;
    }

    /* Botões Streamlit */
    button[kind="primary"] {
        background-color: #0E5C86;
        color: white;
        border-radius: 10px;
    }

    /* Alinhamento dos inputs */
    input, textarea {
        border-radius: 6px !important;
    }
    </style>
""", unsafe_allow_html=True)
#fim do estilo global
st.markdown("<a name='top'></a>", unsafe_allow_html=True)
st.title("📋 Análise de QA?")
st.markdown("Preencha o checklist abaixo. Comentários serão gerados automaticamente com base nas marcações.")

# Carrega a planilha fixa do repositório
@st.cache_resource
def carregar_planilha():
    return pd.ExcelFile("checklist_modelo.xlsx")

try:
    if "resetar" not in st.session_state:
        st.session_state["resetar"] = False

    if "texto_final" not in st.session_state:
        st.session_state["texto_final"] = ""

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
        st.session_state["texto_final"] = ""
        st.rerun()

    respostas = []
    st.subheader("🔢 Checklist")

    for i, row in checklist.iterrows():
        topico = row['Topico']

        with st.container():
            st.markdown(f"""<div class="checklist-box">""", unsafe_allow_html=True)
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
                    comentario_manual = st.text_input(
                        f"Comentário adicional (opcional)", 
                        key=f"coment_{i}", 
                        value=comentario_default
                    )

            respostas.append({
                "Topico": topico,
                "Marcacao": resposta,
                "ComentarioManual": comentario_manual,
                "Indice": i
            })

            st.markdown("</div>", unsafe_allow_html=True)

    # Geração dos comentários finais
    if st.button("✅ Gerar Relatório"):
        st.subheader("📃 Resultado Final")
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

        # Corrigir ordenação: priorizar somente os X dos últimos 5 tópicos
        ultimos_5_idx = set(range(len(respostas) - 5, len(respostas)))
        comentarios_prioritarios = [c for c in comentarios if c[0] in ultimos_5_idx and c[2] == "X"]
        comentarios_restantes = [c for c in comentarios if c not in comentarios_prioritarios]

        comentarios_ordenados = comentarios_prioritarios + comentarios_restantes
        comentarios_final = [c[1] for c in comentarios_ordenados]

        if comentarios_final:
            st.session_state["texto_final"] = "\n\n".join(comentarios_final)

    # Mostrar texto final se existir
    if st.session_state["texto_final"]:
        texto_editado = st.text_area("📝 Edite o texto gerado, se necessário:", value=st.session_state["texto_final"], height=400)

    # Botão fixo para voltar ao topo
    st.markdown("""
        <div style="
        position: fixed;
        bottom: 100px;
        right: 20px;
        z-index: 9999;
        background-color: #0E1117;
        border-radius: 12px;
        padding: 0.6rem 1rem;
        box-shadow: 0 4px 10px rgba(0,0,0,0.3);
    ">
        <a href='#top' style='text-decoration: none; color: white; font-size: 16px; font-weight: bold;'>
            🔝 Voltar ao Topo
        </a>
    </div>
    """, unsafe_allow_html=True)

except Exception as e:
    st.error(f"Erro ao carregar a planilha: {e}")
