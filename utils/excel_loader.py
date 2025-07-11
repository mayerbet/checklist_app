import pandas as pd
import streamlit as st

@st.cache_resource
def carregar_planilha():
    try:
        return pd.ExcelFile("checklist_modelo.xlsx")
    except FileNotFoundError:
        st.error("Arquivo checklist_modelo.xlsx não encontrado no diretório raiz do projeto.")
        return None

def carregar_guia_qualidade():
    return pd.read_excel("guia.xlsx") 


