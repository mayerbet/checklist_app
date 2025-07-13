# components/auth.py
import hashlib
from services.supabase_client import supabase

def hash_senha(senha):
    return hashlib.sha256(senha.encode()).hexdigest()

def registrar_usuario(nome, senha):
    senha_hash = hash_senha(senha)
    try:
        supabase.table("usuarios").insert({
            "nome": nome,
            "senha": senha_hash
        }).execute()
        return True, "✅ Conta criada com sucesso!"
    except Exception as e:
        return False, f"Erro ao registrar: {e}"

def autenticar_usuario(nome, senha):
    senha_hash = hash_senha(senha)
    try:
        res = supabase.table("usuarios").select("*").eq("nome", nome).eq("senha", senha_hash).execute()
        return bool(res.data)
    except Exception:
        return False
