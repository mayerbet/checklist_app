# components/auth.py
import streamlit as st
import hashlib
from services.supabase_client import supabase

# 🔐 Função utilitária para proteger a senha
def hash_senha(senha):
    return hashlib.sha256(senha.encode()).hexdigest()

# ✅ Função para criar usuário
def registrar_usuario(nome, senha):
    senha_hash = hash_senha(senha)
    try:
        supabase.table("usuarios").insert({"nome": nome, "senha": senha_hash}).execute()
        return True, "✅ Conta criada com sucesso!"
    except Exception as e:
        return False, f"Erro ao registrar: {e}"

# ✅ Função para autenticar login
def autenticar_usuario(nome, senha):
    senha_hash = hash_senha(senha)
    try:
        res = supabase.table("usuarios").select("*").eq("nome", nome).eq("senha", senha_hash).execute()
        return bool(res.data)
    except Exception:
        return False

# ✅ Tela de login e registro
def exibir_login():
    st.title("🔐 Login - Análise QA")
    aba = st.radio("Acesso", ["Entrar", "Criar Conta"])

    nome = st.text_input("Usuário")
    senha = st.text_input("Senha", type="password")

    # 🔄 Segunda execução após login (controle de ciclo)
    if st.session_state.get("aguardar_rerun"):
        st.session_state.pop("aguardar_rerun")
        st.rerun()
        return

    # 🔓 Aba de login
    if aba == "Entrar":
        if st.button("Entrar"):
            if autenticar_usuario(nome, senha):
                st.session_state["usuario_logado"] = nome
                st.session_state["logado"] = True
                st.session_state["aguardar_rerun"] = True
                st.stop()  # para o fluxo até próximo rerun
            else:
                st.error("❌ Usuário ou senha inválidos.")

    # 🆕 Aba de registro
    elif aba == "Criar Conta":
        if st.button("Criar Conta"):
            sucesso, msg = registrar_usuario(nome, senha)
            if sucesso:
                st.success(msg)
            else:
                st.error(msg)
