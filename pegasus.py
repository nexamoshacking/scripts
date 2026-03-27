#!/usr/bin/env python3
import os
import sys
import subprocess
import shutil
import random

USUARIO_ATUAL = os.getenv("SUDO_USER") or os.getenv("LOGNAME") or os.getenv("USER") or "user"
HOME = os.path.expanduser(f"~{USUARIO_ATUAL}")
CONTAINER = os.path.join(HOME, ".container.img")
MAPPER = "cryptcontainer"
PONTO_MONTAGEM = os.path.join(HOME, ".jogos")
SENHA = "hackingnexamos"
SCRIPT_PATH = os.path.realpath(sys.argv[0])
SCRIPT_OCULTO = os.path.join(HOME, ".yugioh.sh")
BASHRC = os.path.join(HOME, ".bashrc")

def run(cmd, check=True, capture_output=False, input_text=None):
    return subprocess.run(cmd, shell=True, check=check,
                          capture_output=capture_output,
                          input=input_text, text=True)

def ensure_sudo():
    if os.geteuid() != 0:
        env = os.environ.copy()
        env["SUDO_USER"] = USUARIO_ATUAL
        print("[INFO] Elevando privilégios com sudo...")
        os.execve("/usr/bin/sudo", ["sudo", sys.executable] + sys.argv, env)

def check_dependencies():
    deps = ["cryptsetup", "mkfs.ext4", "mount", "umount", "lsof", "shred", "fuser"]
    for cmd in deps:
        if shutil.which(cmd) is None:
            print(f"[ERRO] Comando obrigatório '{cmd}' não encontrado. Instale o pacote correspondente.")
            sys.exit(1)

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
    mount_output = subprocess.run(f"mount | grep '{PONTO_MONTAGEM}'", shell=True)
    if mount_output.returncode != 0:
        if not os.path.exists(CONTAINER):
            print("[!] Container não encontrado. Criando...")
            criar_container()
        run(f"echo -n '{SENHA}' | cryptsetup open {CONTAINER} {MAPPER} --key-file=-")
        os.makedirs(PONTO_MONTAGEM, exist_ok=True)
        run(f"mount /dev/mapper/{MAPPER} {PONTO_MONTAGEM}")
        run(f"chown {USUARIO_ATUAL}:{USUARIO_ATUAL} {PONTO_MONTAGEM}")
        print(f"[+] Volume montado em {PONTO_MONTAGEM}")
    else:
        print("[*] Volume já está montado.")

def desmontar_volume():
    ensure_sudo()
    mount_output = subprocess.run(f"mount | grep '{PONTO_MONTAGEM}'", shell=True)
    if mount_output.returncode == 0:
        print(f"[*] Finalizando processos que usam {PONTO_MONTAGEM}...")
        try:
            run(f"fuser -km {PONTO_MONTAGEM}", check=True)
        except subprocess.CalledProcessError:
            pass
        try:
            run(f"umount {PONTO_MONTAGEM}")
            run(f"cryptsetup close {MAPPER}")
            print("[+] Volume desmontado.")
        except subprocess.CalledProcessError:
            print("[!] Falha ao desmontar volume mesmo após finalizar processos.")
    else:
        print("[!] Volume não está montado.")

def limpar_volume():
    mount_output = subprocess.run(f"mount | grep '{PONTO_MONTAGEM}'", shell=True)
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
    run(f"shred -u {SCRIPT_PATH}", check=False)
    print("[!] Container e script apagados com segurança.")
    print("Recomendo fechar o terminal agora.")

def charada():
    hist = os.path.join(HOME, ".bash_history")
    comandos = ["hack_the_planet", "foo", "bar", "ls -l", "curl site.com", "ping 8.8.8.8", "chmod 777 *", "sleep 5", "git clone repo", "ssh root@host"]
    with open(hist, "w") as f:
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
                if "yugioh.sh" not in line and "pegasus" not in line:
                    f.write(line)
            f.write(f"alias magonegro='sudo pegasus --magonegro'\n")
            f.write(f"alias exodia='sudo pegasus --exodia'\n")
            f.write(f"alias pandora='sudo pegasus --pandora'\n")
            f.write(f"alias nexamos='sudo pegasus --nexamos'\n")
            f.write(f"alias charada='sudo pegasus --charada'\n")
        print(f"[+] Aliases criados no {BASHRC}. Reabra o terminal ou rode: source ~/.bashrc")

def instalar_script():
    if os.geteuid() != 0:
        print("[INFO] Elevando privilégios para instalar em /usr/bin ...")
        os.execvp("sudo", ["sudo", sys.executable] + sys.argv + ["--install"])
    else:
        target = "/usr/bin/pegasus"
        shutil.copy2(SCRIPT_PATH, target)
        os.chmod(target, 0o755)
        print(f"[+] Script copiado para {target}. Agora você pode chamar 'pegasus' de qualquer terminal.")
        criar_aliases()
        sys.exit(0)

def agendar_charada_cron():
    crontab = subprocess.run("crontab -l", shell=True, capture_output=True, text=True)
    linhas = [l for l in crontab.stdout.splitlines() if "pegasus" not in l]
    linhas.append(f"*/15 * * * * pegasus --charada")
    cron_text = "\n".join(linhas) + "\n"
    subprocess.run("crontab -", input=cron_text, text=True, shell=True)
    print("[+] Cron para charada agendado.")

def print_usage():
    print("""
Modo de uso:

 - pegasus --magonegro : montar volume
 - pegasus --exodia    : desmontar volume
 - pegasus --pandora   : destruir tudo
 - pegasus --nexamos   : limpar conteúdo do container
 - pegasus --charada   : alterar histórico com comandos falsos

""")

def main():
    if len(sys.argv) > 1 and sys.argv[1] == "--install":
        instalar_script()

    if len(sys.argv) < 2:
        print_usage()
        sys.exit(0)

    cmd = sys.argv[1]

    if cmd == "--magonegro":
        montar_volume()
    elif cmd == "--exodia":
        desmontar_volume()
    elif cmd == "--nexamos":
        limpar_volume()
    elif cmd == "--pandora":
        caixa_pandora()
    elif cmd == "--charada":
        charada()
    else:
        print_usage()

if __name__ == "__main__":
    main()
