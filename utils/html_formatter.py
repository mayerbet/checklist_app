import re

def formatar_html_guia(texto):
    """Aplica formatação HTML ao conteúdo vindo do Excel preservando indentação e destaques."""
    # Negrito apenas entre **texto**
    texto = re.sub(r"\*\*(.*?)\*\*", r"<strong>\1</strong>", texto)

    # Títulos com ### se transformam em cabeçalhos
    texto = re.sub(r"###(.*?)\n?", r"<h4>\1</h4>", texto)

    # Recuo com tab (\t) ou 4 espaços
    texto = texto.replace("\t", "&nbsp;&nbsp;&nbsp;&nbsp;")
    texto = texto.replace("    ", "&nbsp;&nbsp;&nbsp;&nbsp;")

    # Quebras de linha
    texto = texto.replace("\n", "<br>")

    return texto

