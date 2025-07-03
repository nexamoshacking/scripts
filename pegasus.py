#!/usr/bin/env python3
import os
import sys
import subprocess

HOME = os.path.expanduser("~")
USUARIO_ATUAL = os.getenv("LOGNAME") or os.getenv("USER")
CONTAINER = os.path.join(HOME, "container.img")
MAPPER = "cryptcontainer"
PONTO_MONTAGEM = os.path.join(HOME, "jogos")
SENHA = "hackingnexamos"
SCRIPT_OCULTO = os.path.join(HOME, ".yugioh.sh")
BASHRC = os.path.join(HOME, ".bashrc")

def run(cmd, check=True, capture_output=False, input_text=None):
    return subprocess.run(cmd, shell=True, check=check,
                          capture_output=capture_output,
                          input=input_text, text=True)

def check_dependencies():
    deps = ["cryptsetup", "mkfs.ext4", "mount", "umount", "lsof", "shred"]
    for cmd in deps:
        if not shutil.which(cmd):
            print(f"[ERRO] Comando obrigatório '{cmd}' não encontrado. Instale o pacote correspondente.")
            sys.exit(1)

def ensure_sudo():
    if os.geteuid() != 0:
        print("[INFO] Elevando privilégios com sudo...")
        os.execvp("sudo", ["sudo", sys.executable] + sys.argv)

def criar_container():
    check_dependencies()
    try:
        run(f"cryptsetup isLuks {CONTAINER}", check=True)
        print("[*] Container já existe.")
    except subprocess.CalledProcessError:
        print(f"[*] Criando container em {CONTAINER} (1GB)...")
        run(f"dd if=/dev/zero of={CONTAINER} bs=1M count=1024 status=none")
        run(f"echo -n '{SENHA}' | cryptsetup luksFormat {CONTAINER} -q --type luks1 --key-file=-")
        run(f"echo -n '{SENHA}' | cryptsetup open {CONTAINER} {MAPPER} --key-file=-")
        run(f"mkfs.ext4 /dev/mapper/{MAPPER} > /dev/null")
        os.makedirs(PONTO_MONTAGEM, exist_ok=True)
        run(f"mount /dev/mapper/{MAPPER} {PONTO_MONTAGEM}")
        run(f"chown -R {USUARIO_ATUAL}:{USUARIO_ATUAL} {PONTO_MONTAGEM}")
        run(f"umount {PONTO_MONTAGEM}")
        run(f"cryptsetup close {MAPPER}")
        print("[+] Container criado e formatado.")

def montar_volume():
    ensure_sudo()
    mount_output = subprocess.run(f"mount | grep {PONTO_MONTAGEM}", shell=True)
    if mount_output.returncode != 0:
        run(f"echo -n '{SENHA}' | cryptsetup open {CONTAINER} {MAPPER} --key-file=-")
        os.makedirs(PONTO_MONTAGEM, exist_ok=True)
        run(f"mount /dev/mapper/{MAPPER} {PONTO_MONTAGEM}")
        run(f"chown {USUARIO_ATUAL}:{USUARIO_ATUAL} {PONTO_MONTAGEM}")
        print(f"[+] Volume montado em {PONTO_MONTAGEM}")
    else:
        print("[*] Volume já está montado.")

def desmontar_volume():
    ensure_sudo()
    mount_output = subprocess.run(f"mount | grep {PONTO_MONTAGEM}", shell=True)
    if mount_output.returncode == 0:
        print(f"[*] Verificando processos que usam {PONTO_MONTAGEM}...")
        lsof_output = subprocess.run(f"lsof +D {PONTO_MONTAGEM}", shell=True, capture_output=True)
        if lsof_output.stdout:
            print("[!] Existem processos usando o volume. Finalize-os antes de desmontar.")
            print(lsof_output.stdout.decode().splitlines()[:10])
            return
        try:
            run(f"umount {PONTO_MONTAGEM}")
            run(f"cryptsetup close {MAPPER}")
            print("[+] Volume desmontado.")
        except subprocess.CalledProcessError:
            print("[!] Falha ao desmontar volume.")
    else:
        print("[!] Volume não está montado.")

def limpar_volume():
    mount_output = subprocess.run(f"mount | grep {PONTO_MONTAGEM}", shell=True)
    if mount_output.returncode == 0:
        run(f"find {PONTO_MONTAGEM} -mindepth 1 -exec rm -rf {{}} +")
        print("[+] Conteúdo limpo.")
    else:
        print("[!] Volume não está montado. Nada a limpar.")

def caixa_pandora():
    ensure_sudo()
    print("[!] Executando destruição completa...")
    run(f"fuser -km {PONTO_MONTAGEM}", check=False)
    run(f"umount {PONTO_MONTAGEM}", check=False)
    run(f"cryptsetup close {MAPPER}", check=False)
    run(f"shred -u {CONTAINER}", check=False)
    run(f"shred -u {SCRIPT_OCULTO}", check=False)
    print("[!] Container e script apagados com segurança.")
    print("Recomendo fechar o terminal agora.")

def charada():
    hist = os.path.join(HOME, ".bash_history")
    comandos = ["hack_the_planet", "foo", "bar", "ls -l", "curl site.com", "ping 8.8.8.8", "chmod 777 *", "sleep 5", "git clone repo", "ssh root@host"]
    with open(hist, "w") as f:
        import random
        for _ in range(100):
            f.write(random.choice(comandos) + "\n")
    run(f"chown {USUARIO_ATUAL}:{USUARIO_ATUAL} {hist}")
    print("[*] Histórico preparado. Reabra o terminal para ver os comandos falsos.")

def criar_aliases():
    if os.path.exists(BASHRC):
        with open(BASHRC, "r") as f:
            lines = f.readlines()
        with open(BASHRC, "w") as f:
            for line in lines:
                if "yugioh.sh" not in line:
                    f.write(line)
            f.write(f"alias magonegro='sudo python3 {SCRIPT_OCULTO} --montar'\n")
            f.write(f"alias exodia='sudo python3 {SCRIPT_OCULTO} --desmontar'\n")
            f.write(f"alias pandora='sudo python3 {SCRIPT_OCULTO} --pandora'\n")
            f.write(f"alias nexamos='python3 {SCRIPT_OCULTO} --limpar'\n")
            f.write(f"alias charada='python3 {SCRIPT_OCULTO} --charada'\n")
        print(f"[+] Aliases criados no {BASHRC}. Reabra o terminal ou rode: source ~/.bashrc")

def copiar_script():
    if os.path.realpath(sys.argv[0]) != SCRIPT_OCULTO:
        import shutil
        shutil.copy2(sys.argv[0], SCRIPT_OCULTO)
        os.chmod(SCRIPT_OCULTO, 0o755)
        criar_aliases()
        os.execv(sys.executable, [sys.executable, SCRIPT_OCULTO] + sys.argv[1:])

def agendar_charada_cron():
    from subprocess import PIPE
    crontab = subprocess.run("crontab -l", shell=True, stdout=PIPE, stderr=PIPE, text=True)
    linhas = [l for l in crontab.stdout.splitlines() if "yugioh.sh" not in l]
    linhas.append(f"*/15 * * * * python3 {SCRIPT_OCULTO} --charada")
    cron_text = "\n".join(linhas) + "\n"
    subprocess.run("crontab -", input=cron_text, text=True, shell=True)
    print("[+] Cron para charada agendado.")

def main():
    if len(sys.argv) < 2:
        copiar_script()
        criar_container()
        agendar_charada_cron()
        print_usage()
        return

    cmd = sys.argv[1]
    if cmd == "--montar":
        montar_volume()
    elif cmd == "--desmontar":
        desmontar_volume()
    elif cmd == "--limpar":
        limpar_volume()
    elif cmd == "--pandora":
        caixa_pandora()
    elif cmd == "--charada":
        charada()
    else:
        copiar_script()
        criar_container()
        agendar_charada_cron()
        print_usage()

def print_usage():
    print("""
Modo de uso:

 - magonegro : montar volume
 - exodia    : desmontar volume
 - pandora   : destruir tudo
 - nexamos   : limpar conteúdo do container
 - charada   : alterar histórico com comandos falsos
""")
    print("""
Criado por Nexamos em homenagem ao Corvo - 2025
⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⣀⣀⣀⣀⠀⠀⠀⠀⠀⠀⠀⠀
⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⢀⣴⣿⣿⡟⠋⢻⣷⣄⡀⠀⠀⠀⠀⠀
⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⣤⣾⣿⣷⣿⣿⣿⣿⣿⣶⣾⣿⣿⠿⠿⠿⠶⠄⠀
⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⣾⣿⣿⣿⣿⣿⣿⣿⣿⣿⣿⡿⠉⠀⠀⠀⠀⠀⠀⠀
⠀⠀⠀⠀⠀⠀⠀⠀⠀⢸⣿⣿⣿⣿⣿⣿⣿⣿⣿⣿⣿⡇⠀⠀⠀⠀⠀⠀⠀⠀
⠀⠀⠀⠀⠀⠀⠀⠀⠀⣿⣿⣿⣿⣿⣿⣿⣿⣿⣿⣿⣿⡟⠀⠀⠀⠀⠀⠀⠀⠀
⠀⠀⠀⠀⠀⠀⠀⠀⠀⣿⣿⣿⣿⣿⣿⣿⣿⣿⣿⣿⣿⠃⠀⠀⠀⠀⠀⠀⠀⠀
⠀⠀⠀⠀⠀⠀⠀⠀⠀⣿⣿⣿⣿⣿⣿⣿⣿⣿⣿⣿⠃⠀⠀⠀⠀⠀⠀⠀⠀⠀
⠀⠀⠀⠀⠀⠀⠀⠀⠀⢸⣿⣿⣿⣿⣿⣿⣿⣿⡟⠁⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀
⠀⠀⠀⠀⠀⠀⠀⠀⠀⠈⣿⣿⣿⣿⣿⣿⠟⠻⣧⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀
⠀⠀⠀⠀⠀⠀⠀⠀⠀⣼⣿⣿⣿⣿⣿⣿⣆⣤⠿⢶⣦⡀⠀⠀⠀⠀⠀⠀⠀⠀
⠀⠀⠀⠀⠀⠀⠀⠀⢰⣿⣿⣿⣿⣿⣿⣿⣿⡀⠀⠀⠀⠑⠀⠀⠀⠀⠀⠀⠀⠀
⠀⠀⠀⠀⠀⠀⠀⠀⣿⣿⣿⣿⣿⣿⣿⣿⣿⣇⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀
⠀⠀⠀⠀⠀⠀⠀⠸⢿⣿⣿⣿⣿⣿⣿⣿⣿⣿⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀
⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠉⠉⠙⠛⠋⠉⠉⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀
""")
    print("Criado por Nexamos em homenagem ao Sr. Pegasus - 2025")
    print("Ilusões Industriais")

if __name__ == "__main__":
    import shutil
    main()