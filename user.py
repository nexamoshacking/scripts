#!/usr/bin/env python3
import os
import subprocess
import random
import string
from pathlib import Path

def gerar_senha(tamanho=12):
    chars = string.ascii_letters + string.digits + string.punctuation
    return ''.join(random.choices(chars, k=tamanho))

def criar_arquivo_fake(caminho):
    extensoes = ['.txt', '.log', '.pdf', '.docx', '.sh', '.dat']
    for i in range(10):  # 10 arquivos por usuário
        nome = f"arquivo_{i}{random.choice(extensoes)}"
        conteudo = f"Conteúdo falso de {nome}\nID: {random.randint(1000,9999)}"
        with open(caminho / nome, 'w') as f:
            f.write(conteudo)

def criar_usuario(numero):
    nome = f"usuario{numero:02}"
    senha = gerar_senha()
    home_dir = Path(f"/home/{nome}")

    print(f"[+] Criando usuário: {nome}")
    subprocess.run(["useradd", "-m", "-d", str(home_dir), "-s", "/bin/bash", nome], check=True)

    # Define a senha
    subprocess.run(["chpasswd"], input=f"{nome}:{senha}", text=True, check=True)

    # Popula a home com arquivos falsos
    criar_arquivo_fake(home_dir)

    # Permissões apropriadas
    subprocess.run(["chown", "-R", f"{nome}:{nome}", str(home_dir)], check=True)

    return nome, senha

def main():
    if os.geteuid() != 0:
        print("[ERRO] Este script deve ser executado como root.")
        exit(1)

    usuarios = []
    for i in range(1, 50):  # De 1 a 49
        try:
            nome, senha = criar_usuario(i)
            usuarios.append((nome, senha))
        except subprocess.CalledProcessError as e:
            print(f"[!] Erro ao criar {nome}: {e}")

    # Salvar lista de usuários e senhas
    with open("usuarios_criados.txt", "w") as f:
        for nome, senha in usuarios:
            f.write(f"{nome}:{senha}\n")

    print("[+] Script finalizado. Lista salva em 'usuarios_criados.txt'.")

if __name__ == "__main__":
    main()
