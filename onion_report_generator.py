import os
from datetime import datetime

# ========= CONFIG =========
PASTA_PRINTS = "prints"
NOME_HTML = "report.html"
TITULO = "Nexamos Onion Search"
# ==========================
"""
========================================
        NEXAMOS ONION REPORT
            by Nexamos
========================================

Descrição
---------
Este script gera automaticamente um relatório HTML a partir
das screenshots coletadas durante o scan de serviços .onion.

Ele percorre a pasta "prints", onde ficam armazenadas as
capturas de tela dos sites encontrados na rede Tor, e cria
uma interface visual em HTML para facilitar a análise dos
resultados.

Funcionalidades
---------------
• Detecta automaticamente imagens PNG na pasta /prints
• Converte o nome das imagens em endereços .onion
• Cria um dashboard HTML com preview dos sites
• Permite abrir os serviços diretamente pelo navegador Tor
• Exibe data do scan e total de serviços encontrados

Saída gerada
------------
report.html  -> painel visual com todos os serviços encontrados

Uso
---
1. Execute o scanner que gera os prints dos sites .onion vulgo tor-sites-check-live.py
2. Execute este script após
3. O arquivo report.html será criado automaticamente

Autor
-----
Nexamos
"""

def gerar_html():
    if not os.path.exists(PASTA_PRINTS):
        print("[ERRO] Pasta 'prints' não encontrada.")
        return

    arquivos = [f for f in os.listdir(PASTA_PRINTS) if f.endswith(".png")]

    if not arquivos:
        print("[ERRO] Nenhum PNG encontrado na pasta prints.")
        return

    html_inicio = f"""
<!DOCTYPE html>
<html>
<head>
<meta charset="UTF-8">
<title>{TITULO}</title>
<style>
body {{
    background-color: #000;
    font-family: Arial, sans-serif;
    color: #fff;
    margin: 0;
}}

h1 {{
    text-align: center;
    color: #ff0033;
    text-shadow: 0 0 20px #ff0033;
    margin: 30px 0 10px 0;
    font-size: 40px;
}}

.info {{
    text-align: center;
    color: #aaa;
    margin-bottom: 30px;
}}

.grid {{
    display: grid;
    grid-template-columns: repeat(4, 1fr);
    gap: 25px;
    padding: 30px;
}}

.card {{
    background-color: #111;
    border: 1px solid #ff0033;
    box-shadow: 0 0 20px #ff0033;
    padding: 15px;
    text-align: center;
    border-radius: 12px;
    transition: 0.3s;
}}

.card:hover {{
    transform: scale(1.03);
    box-shadow: 0 0 35px #ff0033;
}}

.card img {{
    width: 100%;
    height: 220px;
    object-fit: cover;
    border-radius: 8px;
}}

.card h3 {{
    font-size: 13px;
    margin: 15px 0 10px 0;
    word-break: break-all;
}}

.card a {{
    display: inline-block;
    padding: 8px 18px;
    background-color: #ff0033;
    color: white;
    text-decoration: none;
    border-radius: 6px;
    box-shadow: 0 0 15px #ff0033;
    transition: 0.3s;
    font-weight: bold;
}}

.card a:hover {{
    background-color: #ff3366;
    box-shadow: 0 0 30px #ff3366;
}}

@media (max-width: 1200px) {{
    .grid {{
        grid-template-columns: repeat(2, 1fr);
    }}
}}

@media (max-width: 700px) {{
    .grid {{
        grid-template-columns: 1fr;
    }}
}}
</style>
</head>
<body>

<h1>{TITULO}</h1>
<div class="info">
Scan realizado em: {datetime.now().strftime("%d/%m/%Y %H:%M:%S")} <br>
Total de sites encontrados: {len(arquivos)}
</div>

<div class="grid">
"""

    cards = ""

    for arquivo in arquivos:
        # converte nome do arquivo para .onion
        url = arquivo.replace("_onion.png", ".onion")

        cards += f"""
        <div class="card">
            <img src="{PASTA_PRINTS}/{arquivo}">
            <h3>{url}</h3>
            <a href="http://{url}" target="_blank">Acessar Site</a>
        </div>
        """

    html_fim = """
</div>
</body>
</html>
"""

    with open(NOME_HTML, "w", encoding="utf-8") as f:
        f.write(html_inicio + cards + html_fim)

    print(f"[✔] HTML gerado com sucesso: {NOME_HTML}")
    print(f"[✔] {len(arquivos)} sites adicionados.")


if __name__ == "__main__":
    gerar_html()