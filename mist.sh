#!/bin/bash

USUARIO_ATUAL="$(logname)"
HOME_DIR="$HOME"
CONTAINER="$HOME_DIR/container.img"
MAPPER="cryptcontainer"
PONTO_MONTAGEM="$HOME_DIR/jogos"
SENHA="hackingnexamos"
SCRIPT_OCULTO="$HOME_DIR/.yugioh.sh"
BASHRC="$HOME_DIR/.bashrc"

check_dependencies() {
  local deps=("cryptsetup" "mkfs.ext4" "mount" "umount" "lsof" "shred")
  for cmd in "${deps[@]}"; do
    if ! command -v "$cmd" >/dev/null 2>&1; then
      echo "[ERRO] Comando obrigatório '$cmd' não encontrado. Instale o pacote correspondente."
      exit 1
    fi
  done
}

ensure_sudo() {
  if [ "$EUID" -ne 0 ]; then
    echo "[INFO] Elevando privilégios com sudo..."
    exec sudo bash "$0" "$@"
    exit 0
  fi
}

criar_container() {
  check_dependencies
  if ! sudo cryptsetup isLuks "$CONTAINER" 2>/dev/null; then
    echo "[*] Criando container em $CONTAINER (1GB)..."
    dd if=/dev/zero of="$CONTAINER" bs=1M count=1024 status=none
    echo -n "$SENHA" | sudo cryptsetup luksFormat "$CONTAINER" -q --type luks1 --key-file=-
    echo -n "$SENHA" | sudo cryptsetup open "$CONTAINER" "$MAPPER" --key-file=-
    sudo mkfs.ext4 "/dev/mapper/$MAPPER" > /dev/null
    mkdir -p "$PONTO_MONTAGEM"
    sudo mount "/dev/mapper/$MAPPER" "$PONTO_MONTAGEM"
    sudo chown -R "$USUARIO_ATUAL:$USUARIO_ATUAL" "$PONTO_MONTAGEM"
    sudo umount "$PONTO_MONTAGEM"
    sudo cryptsetup close "$MAPPER"
    echo "[+] Container criado e formatado."
  else
    echo "[*] Container já existe."
  fi
}

montar_volume() {
  check_dependencies
  ensure_sudo "$@"
  if ! mount | grep -q "$PONTO_MONTAGEM"; then
    echo -n "$SENHA" | sudo cryptsetup open "$CONTAINER" "$MAPPER" --key-file=-
    mkdir -p "$PONTO_MONTAGEM"
    sudo mount "/dev/mapper/$MAPPER" "$PONTO_MONTAGEM"
    sudo chown "$USUARIO_ATUAL:$USUARIO_ATUAL" "$PONTO_MONTAGEM"
    echo "[+] Volume montado em $PONTO_MONTAGEM"
  else
    echo "[*] Volume já está montado."
  fi
}

desmontar_volume() {
  check_dependencies
  ensure_sudo "$@"
  if mount | grep -q "$PONTO_MONTAGEM"; then
    echo "[*] Verificando processos que usam $PONTO_MONTAGEM..."
    if lsof +D "$PONTO_MONTAGEM" &>/dev/null; then
      echo "[!] Existem processos usando o volume. Finalize-os antes de desmontar."
      lsof +D "$PONTO_MONTAGEM" 2>/dev/null | head -n 10
      return 1
    fi
    sudo umount "$PONTO_MONTAGEM" && sudo cryptsetup close "$MAPPER" && echo "[+] Volume desmontado." || echo "[!] Falha ao desmontar volume."
  else
    echo "[!] Volume não está montado."
  fi
}

limpar_volume() {
  if mount | grep -q "$PONTO_MONTAGEM"; then
    find "$PONTO_MONTAGEM" -mindepth 1 -exec rm -rf {} +
    echo "[+] Conteúdo limpo."
  else
    echo "[!] Volume não está montado. Nada a limpar."
  fi
}

caixa_pandora() {
  echo "[!] Executando destruição completa..."
  fuser -km "$PONTO_MONTAGEM" 2>/dev/null
  sudo umount "$PONTO_MONTAGEM" 2>/dev/null
  sudo cryptsetup close "$MAPPER" 2>/dev/null
  shred -u "$CONTAINER" 2>/dev/null
  shred -u "$SCRIPT_OCULTO" 2>/dev/null
  echo "[!] Container e script apagados com segurança."
  echo "Recomendo fechar o terminal agora."
}

charada() {
  local hist="$HOME_DIR/.bash_history"
  cat /dev/null > "$hist"
  local comandos=("hack_the_planet" "foo" "bar" "ls -l" "curl site.com" "ping 8.8.8.8" "chmod 777 *" "sleep 5" "git clone repo" "ssh root@host")
  for i in $(seq 1 100); do
    echo "${comandos[$RANDOM % ${#comandos[@]}]}" >> "$hist"
  done
  chown "$USUARIO_ATUAL:$USUARIO_ATUAL" "$hist"
  echo "[*] Histórico preparado. Reabra o terminal para ver os comandos falsos."
}

criar_aliases() {
  sed -i '/yugioh.sh/d' "$BASHRC"
  {
    echo "alias magonegro='sudo bash $SCRIPT_OCULTO --montar'"
    echo "alias exodia='sudo bash $SCRIPT_OCULTO --desmontar'"
    echo "alias pandora='sudo bash $SCRIPT_OCULTO --pandora'"
    echo "alias nexamos='bash $SCRIPT_OCULTO --limpar'"
    echo "alias charada='bash $SCRIPT_OCULTO --charada'"
  } >> "$BASHRC"
  echo "[+] Aliases criados no $BASHRC. Reabra o terminal ou rode: source ~/.bashrc"
}

copiar_script() {
  if [ "$(realpath "$0")" != "$SCRIPT_OCULTO" ]; then
    cp "$0" "$SCRIPT_OCULTO"
    chmod 755 "$SCRIPT_OCULTO"
    criar_aliases
    exec bash "$SCRIPT_OCULTO" "$@"
    exit 0
  fi
}

agendar_charada_cron() {
  (crontab -l 2>/dev/null | grep -v yugioh.sh; echo "*/15 * * * * bash $SCRIPT_OCULTO --charada") | crontab -
  echo "[+] Cron para charada agendado."
}

case "$1" in
  --montar) montar_volume ;;
  --desmontar) desmontar_volume ;;
  --limpar) limpar_volume ;;
  --pandora) caixa_pandora ;;
  --charada) charada ;;
  *) copiar_script "$@"; criar_container; agendar_charada_cron ;;
esac

echo -e "\nModo de uso:

 - magonegro : montar volume
 - exodia    : desmontar volume
 - pandora   : destruir tudo
 - nexamos   : limpar conteúdo do container
 - charada   : alterar histórico com comandos falsos
"

echo """
  Criado por Nexamos em homenagem a Mist - 2025
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

"""
echo "Criado por Nexamos em homenagem ao Sr. Pegasus - 2025"
echo "Ilusões Industriais"
