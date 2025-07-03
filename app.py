import streamlit as st
import pandas as pd
import io
import os
from datetime import datetime
from supabase import create_client

# Lê as credenciais do secrets.toml
SUPABASE_URL = st.secrets["supabase"]["url"]
SUPABASE_KEY = st.secrets["supabase"]["key"]

supabase = create_client(SUPABASE_URL, SUPABASE_KEY)

st.set_page_config(page_title="Checklist de Qualidade", layout="wide")
st.markdown("<a name='top'></a>", unsafe_allow_html=True)
st.title("📋 Análise de QA")
st.markdown("Preencha o checklist abaixo. Comentários serão gerados automaticamente com base nas marcações.")

@st.cache_resource
def carregar_planilha():
    return pd.ExcelFile("checklist_modelo.xlsx")

def salvar_historico_supabase(data_analise, nome_atendente, contato_id, texto_editado):
    data = {
        "data": data_analise,
        "atendente": nome_atendente,
        "contato_id": contato_id,
        "resultado": texto_editado
    }
    res = supabase.table("historico").insert(data).execute()
    return res.status_code == 201

def exibir_configuracoes():
    st.subheader("🛠️ Configurar Comentários Padrão")
    xls = carregar_planilha()
    try:
        df_config = pd.read_excel(xls, sheet_name="Config", skiprows=1)
        df_config.columns = ["Index", "Topico", "ComentarioPadrao"]
        for i, row in df_config.iterrows():
            novo_comentario = st.text_area(
                f"✏️ {row['Topico']}",
                value=row['ComentarioPadrao'],
                key=f"coment_config_{i}",
                height=100
            )
            df_config.at[i, 'ComentarioPadrao'] = novo_comentario

        if st.button("📏 Salvar Comentários Padrão"):
            df_config.to_excel("checklist_modelo.xlsx", sheet_name="Config", index=False)
            st.success("Comentários padrão atualizados com sucesso!")
    except Exception as e:
        st.error(f"Erro ao carregar a aba 'Config': {e}")

def exibir_checklist():
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

        if st.button("🩹 Limpar"):
            for i in range(len(checklist)):
                st.session_state[f"resp_{i}"] = "OK"
                st.session_state[f"coment_{i}"] = ""
            st.session_state["texto_final"] = ""
            st.session_state["texto_editado"] = ""
            st.session_state["relatorio_gerado"] = False
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

        if st.button("✅ Gerar Relatório"):
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
                texto_gerado = "\n\n".join(comentarios_final)
                st.session_state["texto_final"] = texto_gerado
                st.session_state["texto_editado"] = texto_gerado
                st.session_state["relatorio_gerado"] = True

        if st.session_state.get("relatorio_gerado", False):
            st.session_state["texto_editado"] = st.text_area(
                "📝 Edite o texto gerado, se necessário:",
                value=st.session_state.get("texto_editado", ""),
                height=400,
                key="texto_editado_area"
            )

            st.markdown("### 📏 Preencha para salvar no histórico")
            nome_atendente = st.text_input("Nome do atendente:", key="nome_atendente")
            contato_id = st.text_input("ID do atendimento:", key="contato_id")
            if st.button("📅 Salvar Histórico"):
                if nome_atendente and contato_id:
                    sucesso = salvar_historico_supabase(
                        datetime.now().isoformat(),
                        nome_atendente,
                        contato_id,
                        st.session_state["texto_editado"]
                    )
                    if sucesso:
                        st.success("✔️ Análise salva com sucesso no Supabase!")
                        st.session_state["relatorio_gerado"] = False
                    else:
                        st.error("❌ Erro ao salvar no Supabase.")
                else:
                    st.warning("⚠️ Preencha todos os campos para salvar.")

    except Exception as e:
        st.error(f"Erro ao carregar a planilha: {e}")

aba = st.sidebar.radio("Navegação", ["Checklist", "Comentários Padrão"])
if aba == "Checklist":
    exibir_checklist()
elif aba == "Comentários Padrão":
    exibir_configuracoes()

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
