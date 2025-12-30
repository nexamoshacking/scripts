#!/usr/bin/env python3
# -*- coding: utf-8 -*-

import os
import tarfile
import argparse
import hashlib
import shutil
from getpass import getpass
from base64 import urlsafe_b64encode
from concurrent.futures import ThreadPoolExecutor
from cryptography.hazmat.primitives.kdf.pbkdf2 import PBKDF2HMAC
from cryptography.hazmat.primitives import hashes
from cryptography.fernet import Fernet
from send2trash import send2trash

# ================= CONFIG =================

SCRIPT_DIR = os.path.dirname(os.path.abspath(__file__))
TEMP_TAR = os.path.join(SCRIPT_DIR, ".__vault_tmp.tar")

SALT = b'\x91\x02\xfa\x88\x10\xef\xaa\x13'
ITERATIONS = 15_000_000
CHUNK_SIZE = 10 * 1024 * 1024  # 2MB

# ================= BANNER =================

def banner():
    print("""
\033[34m══════════════════════════════════════\033[0m
\033[91m   CRYPTUM\033[0m
   Cofre de arquivos
\033[34m══════════════════════════════════════\033[36m
› Dados selados por criptografia forte.
› Nada é restaurado sem verificação.
› Seus arquivos. Suas regras.
> N.X.M.S shh
""")

# ================= CRYPTO =================

def gerar_chave(senha: str) -> bytes:
    kdf = PBKDF2HMAC(
        algorithm=hashes.SHA256(),
        length=32,
        salt=SALT,
        iterations=ITERATIONS,
    )
    return urlsafe_b64encode(kdf.derive(senha.encode()))

# ================= HASH =================

def calcular_hash(path):
    h = hashlib.sha256()
    with open(path, "rb") as f:
        for chunk in iter(lambda: f.read(8192), b""):
            h.update(chunk)
    return h.digest()

# ================= TAR =================

def listar_arquivos(pasta):
    arquivos = []
    for root, _, files in os.walk(pasta):
        for f in files:
            arquivos.append(os.path.join(root, f))
    return arquivos

def criar_tar_multithread(pasta, tar_path):
    arquivos = listar_arquivos(pasta)
    base = os.path.dirname(pasta)

    with tarfile.open(tar_path, "w") as tar:
        with ThreadPoolExecutor(max_workers=os.cpu_count()) as executor:
            for arquivo in arquivos:
                executor.submit(
                    tar.add,
                    arquivo,
                    arcname=os.path.relpath(arquivo, base)
                )

# ================= CHUNK ENCRYPT =================

def encrypt_chunks(input_path, fout, fernet):
    with open(input_path, "rb") as fin:
        while True:
            chunk = fin.read(CHUNK_SIZE)
            if not chunk:
                break
            encrypted = fernet.encrypt(chunk)
            fout.write(len(encrypted).to_bytes(4, "big"))
            fout.write(encrypted)

def decrypt_chunks(fin, output_path, fernet):
    with open(output_path, "wb") as fout:
        while True:
            size_bytes = fin.read(4)
            if not size_bytes:
                break
            size = int.from_bytes(size_bytes, "big")
            encrypted = fin.read(size)
            fout.write(fernet.decrypt(encrypted))

# ================= LOCK =================

def remover_pasta_segura(pasta):
    try:
        send2trash(pasta)
        print("[*] Pasta enviada para a lixeira")
    except Exception:
        print("[!] Lixeira falhou, removendo definitivamente")
        shutil.rmtree(pasta, ignore_errors=True)

def criptografar_pasta(pasta):
    if not os.path.isdir(pasta):
        print("[!] Pasta inválida")
        return

    senha = getpass("🔐 Senha: ")
    if not senha:
        print("[!] Senha vazia não permitida")
        return

    vault_path = os.path.join(
        SCRIPT_DIR,
        f"{os.path.basename(pasta)}.vault"
    )

    chave = gerar_chave(senha)
    fernet = Fernet(chave)

    print("[*] Compactando arquivos...")
    criar_tar_multithread(pasta, TEMP_TAR)

    print("[*] Calculando hash...")
    hash_original = calcular_hash(TEMP_TAR)

    print("[*] Criptografando...")
    with open(vault_path, "wb") as fout:
        fout.write(hash_original)
        encrypt_chunks(TEMP_TAR, fout, fernet)

    os.remove(TEMP_TAR)

    print("[*] Removendo pasta original...")
    remover_pasta_segura(pasta)

    print(f"[✔] Vault criado → {vault_path}")

# ================= UNLOCK =================

def descriptografar_pasta(vault):
    if not os.path.isfile(vault):
        print("[!] Vault inválido")
        return

    senha = getpass("🔑 Senha: ")
    chave = gerar_chave(senha)
    fernet = Fernet(chave)

    try:
        with open(vault, "rb") as fin:
            hash_original = fin.read(32)
            decrypt_chunks(fin, TEMP_TAR, fernet)
    except Exception:
        print("[!] Senha incorreta ou vault corrompido")
        return

    if calcular_hash(TEMP_TAR) != hash_original:
        os.remove(TEMP_TAR)
        print("[✖] ERRO CRÍTICO: integridade comprometida")
        return

    with tarfile.open(TEMP_TAR, "r") as tar:
        tar.extractall(SCRIPT_DIR)

    os.remove(TEMP_TAR)
    print("[✔] Arquivos restaurados")

# ================= GUI =================

def iniciar_gui():
    import tkinter as tk
    from tkinter import filedialog, messagebox

    def escolher_pasta():
        p = filedialog.askdirectory()
        if p:
            entrada_path.delete(0, tk.END)
            entrada_path.insert(0, p)

    def escolher_vault():
        v = filedialog.askopenfilename(filetypes=[("Vault", "*.vault")])
        if v:
            entrada_path.delete(0, tk.END)
            entrada_path.insert(0, v)

    def criptografar():
        global getpass
        getpass = lambda _: entrada_senha.get()
        criptografar_pasta(entrada_path.get())
        messagebox.showinfo("CRYPTUM", "Criptografia concluída")

    def descriptografar():
        global getpass
        getpass = lambda _: entrada_senha.get()
        descriptografar_pasta(entrada_path.get())
        messagebox.showinfo("CRYPTUM", "Descriptografia concluída")

    root = tk.Tk()
    root.title("CRYPTUM VAULT")
    root.geometry("920x360")
    root.configure(bg="#0a0f1f")
    root.resizable(False, False)

    tk.Label(root, text="CRYPTUM", fg="#00ffe1", bg="#0a0f1f",
             font=("Consolas", 22, "bold")).pack(pady=10)
    tk.Label(root, text="Apenas um cofre para guardar suas coisas", fg="#00ffe1", bg="#0a0f1f",
             font=("Consolas", 10, "bold")).pack(pady=10)
    entrada_path = tk.Entry(root, width=60, bg="#11162a",
                            fg="#00ffcc", insertbackground="white")
    entrada_path.pack(pady=5)

    frame = tk.Frame(root, bg="#0a0f1f")
    frame.pack()

    tk.Button(frame, text="📂 Pasta", command=escolher_pasta,
              bg="#1b2b52", fg="#00ffe1", width=24).grid(row=0, column=0, padx=8)

    tk.Button(frame, text="🗄 Vault", command=escolher_vault,
              bg="#1b2b52", fg="#ff00aa", width=24).grid(row=0, column=1, padx=8)

    entrada_senha = tk.Entry(root, width=60, show="*",
                             bg="#11162a", fg="#00ffcc",
                             insertbackground="white")
    entrada_senha.pack(pady=15)

    tk.Button(root, text="🔒 CRIPTOGRAFAR", command=criptografar,
              bg="#00ffe1", fg="#000", font=("Consolas", 15, "bold"),
              width=25).pack(pady=5)

    tk.Button(root, text="🔓 DESCRIPTOGRAFAR", command=descriptografar,
              bg="#ff00aa", fg="#fff", font=("Consolas", 15, "bold"),
              width=25).pack()

    root.mainloop()

# ================= CLI =================

def uso():
    print("""
USO:
  python cryptum.py --lock <pasta>
  python cryptum.py --unlock <arquivo.vault>
  python cryptum.py --gui
""")

if __name__ == "__main__":
    banner()

    parser = argparse.ArgumentParser(add_help=False)
    parser.add_argument("--lock")
    parser.add_argument("--unlock")
    parser.add_argument("--gui", action="store_true")
    parser.add_argument("--help", action="store_true")
    args = parser.parse_args()

    if args.gui:
        iniciar_gui()
    elif args.help or (not args.lock and not args.unlock):
        uso()
    elif args.lock:
        criptografar_pasta(args.lock)
    elif args.unlock:
        descriptografar_pasta(args.unlock)
