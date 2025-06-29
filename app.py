import streamlit as st
import pandas as pd
import io

st.set_page_config(page_title="Checklist de Qualidade", layout="wide")

st.title("📊 Análise de Qualidade de Atendimentos - Checklist")
st.markdown("Preencha o checklist abaixo. Comentários serão gerados automaticamente com base nas marcações.")

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

    # Interface do checklist
    respostas = []
    st.subheader("🔢 Checklist Interativo")
    for i, row in checklist.iterrows():
        topico = row['Topico']
        st.markdown(f"### {topico}")

        col1, col2 = st.columns([1, 3])
        with col1:
            resposta = st.radio(
                label=f"Selecione para o tópico {i+1}",
                options=['OK', 'X', 'N/A'],
                index=0,
                key=f"resp_{i}"
            )
        with col2:
            comentario_manual = ""
            if resposta != 'OK':
                comentario_manual = st.text_input(f"Comentário adicional (opcional)", key=f"coment_{i}")

        respostas.append({
            "Topico": topico,
            "Marcacao": resposta,
            "ComentarioManual": comentario_manual,
            "Indice": i  # salvar o índice para controle de prioridade
        })

    # Botão para limpar a interface
    if st.button("🧹 Limpar e Recomeçar"):
        st.rerun()

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

        # ... (código anterior mantido)

        if comentarios_final:
            texto_final = "\n\n".join(comentarios_final)  # separação entre cada item

            texto_editado = st.text_area("📝 Edite o texto gerado, se necessário:", value=texto_final, height=400)

            # Container para os botões
            col1, col2, col3 = st.columns([1, 1, 3])
            
            with col1:
                st.download_button("💾 Baixar Comentários", data=texto_editado, file_name="comentarios.txt")
            
            with col2:
                # Botão de cópia com JS seguro e oculto
                st.markdown(f"""
                <div style="position:relative;">
                    <textarea id="comentarios" style="position:absolute;left:-9999px;">{texto_editado.replace('"', '&quot;')}</textarea>
                    <button onclick="copiarTexto()" style="
                        background-color: #4CAF50;
                        color: white;
                        padding: 8px 16px;
                        border: none;
                        border-radius: 4px;
                        cursor: pointer;
                        display: flex;
                        align-items: center;
                        gap: 8px;
                        font-weight: bold;
                    ">
                        📋 Copiar
                    </button>
                </div>
                
                <script>
                    function copiarTexto() {{
                        var copyText = document.getElementById('comentarios');
                        copyText.select();
                        document.execCommand('copy');
                        
                        // Feedback visual
                        var btn = event.currentTarget;
                        btn.innerHTML = '✓ Copiado!';
                        btn.style.backgroundColor = '#2E7D32';
                        setTimeout(function() {{
                            btn.innerHTML = '📋 Copiar';
                            btn.style.backgroundColor = '#4CAF50';
                        }}, 2000);
                    }}
                </script>
                """, unsafe_allow_html=True)

        else:
            st.info("Nenhuma marcação relevante foi encontrada.")

# ... (restante do código mantido)
except Exception as e:
    st.error(f"Erro ao carregar a planilha: {e}")
