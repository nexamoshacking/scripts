#!/usr/bin/env python3

import re
import os
import time
import requests
from bs4 import BeautifulSoup
from datetime import datetime

from selenium import webdriver
from selenium.webdriver.chrome.options import Options
from selenium.webdriver.chrome.service import Service


"""
========================================
        DARKNET OSINT SCANNER
              by Nexamos
========================================

Descrição:
-----------
Darknet OSINT Scanner é uma ferramenta de investigação que automatiza
a coleta de informações de serviços .onion na rede Tor.

O script recebe uma lista de possíveis domínios .onion, testa a
disponibilidade dos serviços através do proxy Tor e coleta informações
básicas das páginas encontradas.

Funcionalidades:
----------------
• Extração automática de endereços .onion a partir de arquivos .txt
• Verificação de disponibilidade de serviços na rede Tor
• Coleta do título da página HTML
• Registro de status HTTP e tempo de resposta
• Captura automática de screenshots usando Chromium headless
• Geração de relatório com todos os serviços ativos encontrados

Fluxo de funcionamento:
-----------------------
1. O usuário fornece um arquivo contendo possíveis domínios .onion
2. O script extrai automaticamente os endereços válidos
3. Cada domínio é testado através do proxy Tor (127.0.0.1:9050)
4. Sites ativos têm informações coletadas
5. Um screenshot da página é gerado automaticamente
6. Um relatório final é salvo com os resultados do scan

Arquivos gerados:
-----------------
onions_vivos.txt  -> relatório dos sites ativos encontrados
prints/           -> screenshots das páginas acessadas

Requisitos:
-----------
• Tor rodando localmente
• Python 3
• requests
• bs4 (BeautifulSoup)
• selenium
• chromedriver

Uso educacional (ou n, problema e de quem for usar kkkkk fds:
----------------
Ferramenta desenvolvida para fins educacionais, OSINT e pesquisa
em infraestrutura da rede Tor.

Autor:
------
Nexamos
"""


# ==========================
# BANNER
# ==========================

def banner():
    print(r"""
========================================
        DARKNET OSINT SCANNER
              by Nexamos
========================================
""")

# ==========================
# EXTRAIR .ONION
# ==========================

def extrair_onions(arquivo):

    with open(arquivo, "r", encoding="utf-8", errors="ignore") as f:
        conteudo = f.read()

    onions = set(re.findall(r"[a-z2-7]{56}\.onion", conteudo))
    return list(onions)

# ==========================
# TESTAR SITE
# ==========================

def testar_onion(site):

    proxies = {
        "http": "socks5h://127.0.0.1:9050",
        "https": "socks5h://127.0.0.1:9050"
    }

    try:
        inicio = time.time()

        r = requests.get(
            "http://" + site,
            proxies=proxies,
            timeout=60
        )

        tempo_resposta = round(time.time() - inicio, 2)

        soup = BeautifulSoup(r.text, "html.parser")

        if soup.title and soup.title.string:
            titulo = soup.title.string.strip()
        else:
            titulo = "Sem titulo"

        return True, titulo, r.status_code, tempo_resposta

    except:
        return False, None, None, None

# ==========================
# SCREENSHOT COM CHROMIUM
# ==========================

def screenshot(site):

    try:
        os.makedirs("prints", exist_ok=True)

        options = Options()
        options.add_argument("--headless=new")
        options.add_argument("--no-sandbox")
        options.add_argument("--disable-dev-shm-usage")
        options.add_argument("--proxy-server=socks5://127.0.0.1:9050")

        service = Service("/usr/bin/chromedriver")

        driver = webdriver.Chrome(service=service, options=options)

        driver.set_page_load_timeout(120)

        print(f"[+] Abrindo {site}...")

        driver.get("http://" + site)

        time.sleep(20)

        nome = site.replace(".", "_")
        caminho = f"prints/{nome}.png"

        driver.save_screenshot(caminho)
        driver.quit()

        print(f"[PRINT OK] {site}")

    except Exception as e:
        print(f"[ERRO PRINT] {site}")
        print(e)

# ==========================
# SCAN
# ==========================

def scan(onions):

    vivos = []

    print("\n[+] Testando sites .onion...\n")

    for site in onions:

        status, titulo, status_code, tempo = testar_onion(site)

        if status:
            print(f"[ON]  {site} | {titulo} | {status_code} | {tempo}s")
            vivos.append((site, titulo, status_code, tempo))
            screenshot(site)
        else:
            print(f"[OFF] {site}")

    return vivos

# ==========================
# MAIN
# ==========================

def main():

    banner()

    arquivo = input("Lista de sites (.txt): ")

    if not os.path.exists(arquivo):
        print("Arquivo não encontrado")
        return

    onions = extrair_onions(arquivo)

    print(f"\n[+] {len(onions)} sites encontrados\n")

    vivos = scan(onions)

    data_scan = datetime.now().strftime("%d/%m/%Y %H:%M:%S")

    with open("onions_vivos.txt", "w", encoding="utf-8") as f:
        f.write(f"Scan realizado em: {data_scan}\n")
        f.write("="*60 + "\n\n")

        for site, titulo, status_code, tempo in vivos:
            f.write(f"http://{site}\n")
            f.write(f"Título: {titulo}\n")
            f.write(f"Status Code: {status_code}\n")
            f.write(f"Tempo de resposta: {tempo}s\n")
            f.write("-"*60 + "\n")

    print(f"\n[+] {len(vivos)} sites vivos encontrados")
    print("[+] Lista salva em onions_vivos.txt")
    print("[+] Prints salvos na pasta /prints")

if __name__ == "__main__":
    main()