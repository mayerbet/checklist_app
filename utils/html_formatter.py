import re
import streamlit.components.v1 as components

def formatar_html_guia(texto):
    """Mantém sua função original para formatação básica"""
    texto = re.sub(r"\*\*(.*?)\*\*", r"<strong>\1</strong>", texto)
    texto = re.sub(r"###(.*?)\n?", r"<h4>\1</h4>", texto)
    texto = texto.replace("\t", "&nbsp;&nbsp;&nbsp;&nbsp;")
    texto = texto.replace("    ", "&nbsp;&nbsp;&nbsp;&nbsp;")
    return texto.replace("\n", "<br>")

# NOVA FUNÇÃO: Gerador de popups
def gerar_popup_guia(titulo: str, conteudo_formatado: str) -> None:
    """Renderiza um popup com o guia formatado"""
    popup_html = f"""
    <script>
    function showGuide{hash(titulo)}() {{
        const modal = document.createElement('div');
        modal.style = `
            position: fixed;
            top: 50%;
            left: 50%;
            transform: translate(-50%, -50%);
            width: 70%;
            max-height: 80vh;
            background: white;
            padding: 25px;
            border-radius: 12px;
            box-shadow: 0 5px 25px rgba(0,0,0,0.3);
            z-index: 1000;
            overflow-y: auto;
            font-family: Arial, sans-serif;
        `;
        
        modal.innerHTML = `
            <div style="display:flex; justify-content:space-between; align-items:center">
                <h3 style="margin:0; color:#1e3a8a">{titulo}</h3>
                <button onclick="this.parentElement.parentElement.remove(); document.getElementById('overlay').remove()" 
                        style="background:none; border:none; font-size:1.8rem; cursor:pointer; color:#555">
                    ×
                </button>
            </div>
            <hr style="border-top:1px solid #eee; margin:15px 0">
            <div style="color:#333; line-height:1.6">{conteudo_formatado}</div>
        `;
        
        const overlay = document.createElement('div');
        overlay.id = 'overlay';
        overlay.style = `
            position: fixed;
            top: 0;
            left: 0;
            width: 100vw;
            height: 100vh;
            background: rgba(0,0,0,0.65);
            z-index: 999;
        `;
        
        document.body.appendChild(overlay);
        document.body.appendChild(modal);
    }}
    </script>
    
    <button onclick="showGuide{hash(titulo)}()"
            style="
                background: #f0f2f6;
                border: 1px solid #ddd;
                border-radius: 50%;
                width: 28px;
                height: 28px;
                font-size: 16px;
                font-weight: bold;
                margin-left: 12px;
                cursor: pointer;
                vertical-align: middle;
                transition: all 0.3s;
                display: inline-flex;
                justify-content: center;
                align-items: center;"
            onmouseover="this.style.background='#e2e8f0'"
            onmouseout="this.style.background='#f0f2f6'">
        ?
    </button>
    """
    components.html(popup_html, height=0)
