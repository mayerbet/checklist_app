import streamlit as st
import pandas as pd
from datetime import datetime
from supabase import create_client
import pytz

# Lê as credenciais do secrets.toml
SUPABASE_URL = st.secrets["supabase"]["url"]
SUPABASE_KEY = st.secrets["supabase"]["key"]
supabase = create_client(SUPABASE_URL, SUPABASE_KEY)

st.set_page_config(page_title="Checklist de Qualidade", layout="wide")
st.markdown("<a name='top'></a>", unsafe_allow_html=True)
st.title("📋 Análise de QA")

@st.cache_resource
def carregar_planilha():
    return pd.ExcelFile("checklist_modelo.xlsx")

def salvar_historico_supabase(data_analise, nome_atendente, contato_id, texto_editado, usuario):
    try:
        data = {
            "data": data_analise,
            "atendente": nome_atendente,
            "contato_id": contato_id,
            "resultado": texto_editado,
            "usuario": usuario
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
            on_conflict="topico,usuario"
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

# Persistência do usuário via menu lateral
st.sidebar.subheader("👤 Usuário")
if "usuario" not in st.session_state:
    st.session_state["usuario"] = ""
usuario = st.sidebar.text_input("Digite seu nome", value=st.session_state["usuario"], key="usuario_input")
st.session_state["usuario"] = usuario.strip()

def exibir_configuracoes():
    st.subheader("🛠️ Configurar Comentários")
    if not usuario:
        st.info("Insira seu nome no menu lateral para editar seus comentários.")
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

        if st.button("💾 Salvar Comentários"):
            sucesso = salvar_comentarios_padrao(usuario, comentarios_atualizados)
            if sucesso:
                st.success("Comentários salvos com sucesso!")

    except Exception as e:
        st.error(f"Erro ao carregar a aba 'Config': {e}")

def exibir_checklist():
    st.subheader("🔢 Checklist")
    st.markdown("Preencha o checklist. Comentários serão gerados automaticamente com base nas marcações.")
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
                        comentario_final += f" ({r['ComentarioManual']})"
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
                # ✅ Sincroniza o texto realmente editado pelo usuário
                    st.session_state["texto_editado"] = st.session_state.get("texto_editado_area", "")

                    sucesso = salvar_historico_supabase(
                        datetime.now().isoformat(),
                        nome_atendente,
                        contato_id,
                        st.session_state["texto_editado"],
                        st.session_state.get("usuario", "").strip()
                    )

        if sucesso:
            st.success("✔️ Salvo com sucesso no histórico!")
            st.session_state["relatorio_gerado"] = False
    else:
        st.warning("⚠️ Preencha todos os campos para salvar.")


        if st.button("🧹 Limpar"):
            for i in range(len(checklist)):
                st.session_state.pop(f"resp_{i}", None)
                st.session_state.pop(f"coment_{i}_text_area", None)
            st.session_state["texto_editado"] = ""
            st.session_state["relatorio_gerado"] = False
            st.rerun()


    except Exception as e:
        st.error(f"Erro ao carregar checklist: {e}")

def exibir_historico():
    st.subheader("📚 Histórico de Análises")

    usuario = st.session_state.get("usuario", "").strip()
    #st.write("🔍 Usuário ativo para busca:", repr(usuario))

    if not usuario:
        st.info("Informe o nome de usuário no menu lateral para visualizar seu histórico.")
        return

    try:
        resultado = (
            supabase
            .table("history")
            .select("*")
            .eq("usuario", usuario)
            .order("data", desc=True)
            .limit(50)
            .execute()
        )

        registros = resultado.data if resultado and resultado.data else []

        if registros:
            df = pd.DataFrame(registros)
            
            # Oculta colunas irrelevantes
            colunas_ocultar = ["id"]
            df = df.drop(columns=[col for col in colunas_ocultar if col in df.columns])
    
    # Ajusta fuso horário e mostra só a data
            if "data" in df.columns:
                df["data"] = pd.to_datetime(df["data"]).dt.tz_convert("America/Sao_Paulo").dt.date
            st.dataframe(df)
            if st.button("🗑️ Limpar Seu Histórico"):
                try:
                    supabase.table("history").delete().eq("usuario", usuario).execute()
                    st.success("Seu histórico foi limpo com sucesso.")
                    st.rerun()
                except Exception as e:
                    st.error(f"Erro ao apagar histórico: {e}")
        else:
            st.warning("Nenhum histórico encontrado para este usuário.")

    except Exception as e:
        st.error(f"Erro ao carregar histórico: {e}")

# Navegação
aba = st.sidebar.radio("Navegação", ["Checklist", "Comentários Padrão", "Histórico de análises"])
if aba == "Checklist":
    exibir_checklist()
elif aba == "Comentários Padrão":
    exibir_configuracoes()
elif aba == "Histórico de análises":
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
