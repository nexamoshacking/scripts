import os
import requests
from bs4 import BeautifulSoup
import concurrent.futures
import time
import socket
from fake_useragent import UserAgent
import random
import sys

# ================= CONFIG =================
FONTES_PROXY = [
    'https://www.socks-proxy.net/',
    'https://free-proxy-list.net/',
    'https://www.proxy-list.download/SOCKS4',
    'https://www.proxy-list.download/SOCKS5',
    'https://spys.one/en/socks-proxy-list/',
]

URL_TESTE = 'http://example.com'
TIMEOUT_REQ = 30
MAX_PROXIES = 50
ARQ_PROXYCHAINS = '/etc/proxychains.conf'

UA = {'User-Agent': UserAgent().random}

# ================= UI =================
CORES = {
    "verde": "\033[92m",
    "roxo": "\033[95m",
    "azul": "\033[94m",
    "reset": "\033[0m"
}

SPINNER = ["⣾","⣷","⣯","⣟","⡿","⡱","⡇","⡧"]

def banner():
    print(f"""{CORES['roxo']}
███╗   ██╗███████╗██╗  ██╗ █████╗ ███╗   ███╗ ██████╗ ███████╗
████╗  ██║██╔════╝╚██╗██╔╝██╔══██╗████╗ ████║██╔═══██╗██╔════╝
██╔██╗ ██║█████╗   ╚███╔╝ ███████║██╔████╔██║██║   ██║███████╗
██║╚██╗██║██╔══╝   ██╔██╗ ██╔══██║██║╚██╔╝██║██║   ██║╚════██║
██║ ╚████║███████╗██╔╝ ██╗██║  ██║██║ ╚═╝ ██║╚██████╔╝███████║
╚═╝  ╚═══╝╚══════╝╚═╝  ╚═╝╚═╝  ╚═╝╚═╝     ╚═╝ ╚═════╝ ╚══════╝

        Proxy Hunt3r • SOCKS4/5 • Auto Cleaner
                Author: Nexamos (a Gh0st)
{CORES['reset']}""")

def loading():
    for i in range(1, 101):
        spin = random.choice(SPINNER)
        barra = "#" * (i // 2)
        sys.stdout.write(f"\r{CORES['verde']}[{spin}] Carregando {barra} {i}%{CORES['reset']}")
        sys.stdout.flush()
        time.sleep(0.01)
    print()

# ================= CORE =================
def coletar_proxies():
    lista = []
    for url in FONTES_PROXY:
        try:
            r = requests.get(url, headers=UA, timeout=TIMEOUT_REQ)
            soup = BeautifulSoup(r.text, 'html.parser')

            for tabela in soup.find_all('table'):
                for linha in tabela.find_all('tr'):
                    cols = linha.find_all(['td', 'th'])
                    if len(cols) >= 2:
                        ip = cols[0].text.strip().split()[0]
                        porta = cols[1].text.strip().split()[0]

                        proto = cols[4].text.lower() if len(cols) > 4 else ''

                        if 'socks4' in proto:
                            lista.append((f"{ip}:{porta}", 'socks4'))
                        elif 'socks5' in proto:
                            lista.append((f"{ip}:{porta}", 'socks5'))

        except Exception:
            print(f"{CORES['azul']}[!] Falha em {url}{CORES['reset']}")

    return list(set(lista))


def testar_proxy(proxy):
    addr, tipo = proxy
    try:
        ip, porta = addr.split(':')
        sock = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        sock.settimeout(TIMEOUT_REQ)

        inicio = time.time()

        if sock.connect_ex((ip, int(porta))) != 0:
            return None

        if tipo == 'socks4':
            sock.sendall(b'\x04\x01' + int(porta).to_bytes(2, 'big') + socket.inet_aton(ip) + b'\x00')
            resp = sock.recv(8)
            if len(resp) != 8 or resp[1] != 0x5a:
                return None

        elif tipo == 'socks5':
            sock.sendall(b'\x05\x01\x00')
            resp = sock.recv(2)
            if resp[1] != 0x00:
                return None

            sock.sendall(b'\x05\x01\x00\x01' + socket.inet_aton(ip) + int(porta).to_bytes(2, 'big'))
            resp = sock.recv(10)
            if resp[1] != 0x00:
                return None

        proxy_cfg = {
            'http': f'{tipo}://{addr}',
            'https': f'{tipo}://{addr}'
        }

        r = requests.get(URL_TESTE, proxies=proxy_cfg, timeout=TIMEOUT_REQ, headers=UA)

        if r.status_code == 200:
            return (addr, tipo, time.time() - inicio)

    except:
        return None
    finally:
        sock.close()


def ler_proxychains():
    ativos = []
    try:
        with open(ARQ_PROXYCHAINS, 'r') as f:
            linhas = f.readlines()

        for l in linhas:
            l = l.strip()
            if l.startswith('socks'):
                p = l.split()
                ativos.append((f"{p[1]}:{p[2]}", p[0]))

    except:
        pass

    return ativos


def atualizar_proxychains(lista):
    try:
        if not os.access(ARQ_PROXYCHAINS, os.W_OK):
            print(f"{CORES['azul']}[!] Use sudo para atualizar{CORES['reset']}")
            return

        with open(ARQ_PROXYCHAINS, 'r') as f:
            cfg = f.read()

        header = cfg.split('[ProxyList]')[0]

        novo = f"{header}\n[ProxyList]\n"

        for proxy in lista[:MAX_PROXIES]:
            addr, tipo = proxy
            ip, porta = addr.split(':')
            novo += f"{tipo} {ip} {porta}\n"

        with open(ARQ_PROXYCHAINS, 'w') as f:
            f.write(novo)

        print(f"{CORES['verde']}[✓] Proxychains atualizado!{CORES['reset']}")

    except Exception as e:
        print(f"[ERRO] {e}")


# ================= MAIN =================
def main():
    banner()
    loading()

    print(f"{CORES['azul']}[*] Limpando proxies antigos...{CORES['reset']}")
    antigos = ler_proxychains()

    validos = []

    with concurrent.futures.ThreadPoolExecutor(max_workers=20) as exe:
        resultados = exe.map(testar_proxy, antigos)

        for r in resultados:
            if r:
                print(f"{CORES['verde']}[OK]{CORES['reset']} {r[1]}://{r[0]}")
                validos.append((r[0], r[1]))

    print(f"\n{CORES['azul']}[*] Coletando novos proxies...{CORES['reset']}")
    novos = coletar_proxies()

    with concurrent.futures.ThreadPoolExecutor(max_workers=20) as exe:
        resultados = exe.map(testar_proxy, novos)

        for r in resultados:
            if r:
                print(f"{CORES['verde']}[OK]{CORES['reset']} {r[1]}://{r[0]}")
                validos.append((r[0], r[1]))

    validos = list(set(validos))

    if validos:
        print(f"\n{CORES['roxo']}[🔥] PROXIES FINAIS:{CORES['reset']}")
        for p in validos[:MAX_PROXIES]:
            print(f"- {p[1]}://{p[0]}")

        atualizar_proxychains(validos)
    else:
        print("[X] Nenhum proxy funcional")


if __name__ == "__main__":
    main()