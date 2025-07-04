import streamlit as st
import pandas as pd
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
    try:
        data = {
            "data": data_analise,
            "atendente": nome_atendente,
            "contato_id": contato_id,
            "resultado": texto_editado
        }
        res = supabase.table("history").insert(data).execute()
        return bool(res and res.data)
    except Exception as e:
        st.error(f"Exceção ao salvar no Supabase: {e}")
        return False

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
        supabase.table("comentarios_padrao").upsert(
            registros,
            on_conflict="topico,usuario"  # <- Corrigido aqui
        ).execute()
        return True
    except Exception as e:
        st.error(f"Erro ao salvar comentários no Supabase: {e}")
        return False

def carregar_comentarios_padrao(usuario):
    try:
        res = supabase.table("comentarios_padrao").select("topico, comentario").eq("usuario", usuario).execute()
        return {item["topico"]: item["comentario"] for item in res.data} if res.data else {}
    except Exception as e:
        st.error(f"Erro ao carregar comentários do Supabase: {e}")
        return {}

# Entrada de usuário compartilhada entre abas
st.sidebar.subheader("👤 Usuário")
usuario = st.sidebar.text_input("Digite seu nome", key="usuario", value=st.session_state.get("usuario", ""))
st.session_state["usuario"] = usuario.strip()

def exibir_configuracoes():
    st.subheader("🛠️ Configurar Comentários Padrão")

    if not usuario:
        st.info("Insira seu nome no menu lateral para editar seus comentários padrão.")
        return

    xls = carregar_planilha()
    try:
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
                height=100
            )
            comentarios_atualizados[topico] = novo_comentario

        if st.button("💾 Salvar Comentários Padrão no Supabase"):
            sucesso = salvar_comentarios_padrao(usuario, comentarios_atualizados)
            if sucesso:
                st.success("Comentários padrão salvos com sucesso no Supabase!")

    except Exception as e:
        st.error(f"Erro ao carregar a aba 'Config': {e}")

def exibir_checklist():
    st.subheader("🔢 Checklist")

    if not usuario:
        st.info("Informe o nome de usuário no menu lateral para continuar.")
        return

    try:
        xls = carregar_planilha()
        checklist_df = pd.read_excel(xls, sheet_name="Checklist")
        checklist = checklist_df.iloc[1:].reset_index(drop=True)
        checklist.columns = ['Index', 'Topico', 'Marcacao', 'Comentario', 'Observacoes', 'Relatorio']

        comentarios_usuario = carregar_comentarios_padrao(usuario)
        respostas = []

        for i, row in checklist.iterrows():
            topico = row['Topico']
            st.markdown(f"### {topico}")
            col1, col2 = st.columns([1, 3])

            with col1:
                resposta = st.radio(
                    f"Selecione para o tópico {i+1}",
                    options=['OK', 'X', 'N/A'],
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
                        comentario_final += f" ({r['ComentarioManual']})"
                    comentarios.append((r["Indice"], comentario_final, r["Marcacao"]))

            ultimos_5_idx = set(range(len(respostas) - 5, len(respostas)))
            prioridade = [c for c in comentarios if c[0] in ultimos_5_idx and c[2] == "X"]
            restantes = [c for c in comentarios if c not in prioridade]
            comentarios_final = prioridade + restantes
            texto_gerado = "\n\n".join([c[1] for c in comentarios_final])

            st.session_state["texto_editado"] = st.text_area(
                "📝 Edite o texto gerado, se necessário:",
                value=texto_gerado,
                height=400,
                key="texto_editado_area"
            )

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
                else:
                    st.warning("⚠️ Preencha todos os campos para salvar.")

    except Exception as e:
        st.error(f"Erro ao carregar checklist: {e}")

def exibir_historico():
    st.subheader("📚 Histórico de Análises")
    try:
        data = supabase.table("history").select("*").order("data", desc=True).limit(50).execute()
        registros = data.data
        if registros:
            df = pd.DataFrame(registros)
            st.dataframe(df)
            if st.button("🗑️ Limpar Histórico"):
                supabase.table("history").delete().neq("id", "").execute()
                st.success("Histórico limpo com sucesso.")
        else:
            st.info("Nenhum histórico encontrado.")
    except Exception as e:
        st.error(f"Erro ao carregar histórico: {e}")

# Navegação
aba = st.sidebar.radio("Navegação", ["Checklist", "Comentários Padrão", "Histórico"])
if aba == "Checklist":
    exibir_checklist()
elif aba == "Comentários Padrão":
    exibir_configuracoes()
elif aba == "Histórico":
    exibir_historico()

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
