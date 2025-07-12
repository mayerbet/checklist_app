import streamlit as st
import hashlib

# Conexão Supabase
from services.supabase_client import supabase


def hash_senha(senha):
    return hashlib.sha256(senha.encode()).hexdigest()

def registrar_usuario(nome, senha):
    senha_hash = hash_senha(senha)
    try:
        res = supabase.table("usuarios").insert({"nome": nome, "senha": senha_hash}).execute()
        return True, "✅ Conta criada com sucesso!"
    except Exception as e:
        return False, f"Erro ao registrar: {e}"

def autenticar_usuario(nome, senha):
    senha_hash = hash_senha(senha)
    try:
        res = supabase.table("usuarios").select("*").eq("nome", nome).eq("senha", senha_hash).execute()
        if res.data:
            return True
        else:
            return False
    except Exception:
        return False

def exibir_login():
    st.title("🔐 Login - Checklist de Qualidade")

    aba = st.radio("Acesso", ["Entrar", "Criar Conta"])

    nome = st.text_input("Usuário")
    senha = st.text_input("Senha", type="password")

    if aba == "Entrar":
        if st.button("Entrar"):
            if autenticar_usuario(nome, senha):
                st.session_state["logado"] = True
                st.session_state["usuario"] = nome
                st.experimental_rerun()
            else:
                st.error("Usuário ou senha inválidos.")
    else:
        if st.button("Criar Conta"):
            sucesso, msg = registrar_usuario(nome, senha)
            if sucesso:
                st.success(msg)
            else:
                st.error(msg)

