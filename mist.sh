#!/bin/bash

USUARIO_ATUAL="$(logname)"
DIR_OCULTO="/var/lib/.xsession"
SCRIPT_OCULTO="$DIR_OCULTO/yugioh.sh"
BASHRC="/home/$USUARIO_ATUAL/.bashrc"
CONTAINER="/crypt_jean.img"
MAPPER="cryptjean"
PONTO_MONTAGEM="/home/jean"
SENHA="hackingnexamos"


criar_container() {
  if ! cryptsetup isLuks "$CONTAINER" 2>/dev/null; then
    dd if=/dev/zero of="$CONTAINER" bs=1M count=1024 status=none
    echo -n "$SENHA" | cryptsetup luksFormat "$CONTAINER" -q --type luks1 --key-file=-
    echo -n "$SENHA" | cryptsetup open "$CONTAINER" "$MAPPER" --key-file=-
    mkfs.ext4 "/dev/mapper/$MAPPER" > /dev/null
    mkdir -p "$PONTO_MONTAGEM"
    mount "/dev/mapper/$MAPPER" "$PONTO_MONTAGEM"
    chown -R "$USUARIO_ATUAL:$USUARIO_ATUAL" "$PONTO_MONTAGEM"
    umount "$PONTO_MONTAGEM"
    cryptsetup close "$MAPPER"
  fi
}

criar_aliases() {
  sed -i '/yugioh.sh/d' "$BASHRC"
  {
    echo "alias magonegro='sudo bash $SCRIPT_OCULTO --montar'"
    echo "alias exodia='sudo bash $SCRIPT_OCULTO --desmontar'"
    echo "alias pandora='sudo bash $SCRIPT_OCULTO --pandora'"
    echo "alias nexamos='sudo bash $SCRIPT_OCULTO --limpar'"
    echo "alias charada='bash $SCRIPT_OCULTO --charada'"
  } >> "$BASHRC"
  chown "$USUARIO_ATUAL:$USUARIO_ATUAL" "$BASHRC"
}

copiar_script() {
  if [ "$(realpath "$0")" != "$SCRIPT_OCULTO" ]; then
    mkdir -p "$DIR_OCULTO"
    cp "$0" "$SCRIPT_OCULTO"
    chmod 755 "$SCRIPT_OCULTO"
    criar_aliases
    exec sudo bash "$SCRIPT_OCULTO"
    exit 0
  fi
}

montar_volume() {
  echo -n "$SENHA" | cryptsetup open "$CONTAINER" "$MAPPER" --key-file=- 2>/dev/null
  mkdir -p "$PONTO_MONTAGEM"
  mount "/dev/mapper/$MAPPER" "$PONTO_MONTAGEM" 2>/dev/null
  chown "$USUARIO_ATUAL:$USUARIO_ATUAL" "$PONTO_MONTAGEM"
  echo "[+] Volume montado em $PONTO_MONTAGEM"
}

desmontar_volume() {
  if mount | grep -q "$PONTO_MONTAGEM"; then
    echo "[*] Verificando processos que usam $PONTO_MONTAGEM..."
    if lsof +D "$PONTO_MONTAGEM" &>/dev/null; then
      echo "[!] Existem processos usando o volume. Finalize-os antes de desmontar."
      lsof +D "$PONTO_MONTAGEM" 2>/dev/null | head -n 10
      return 1
    fi

    umount "$PONTO_MONTAGEM" 2>/dev/null && \
    cryptsetup close "$MAPPER" 2>/dev/null && \
    echo "[+] Volume desmontado." || echo "[!] Falha ao desmontar volume."
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
  fuser -km "$PONTO_MONTAGEM" 2>/dev/null
  umount "$PONTO_MONTAGEM" 2>/dev/null
  cryptsetup close "$MAPPER" 2>/dev/null
  shred -u "$CONTAINER" 2>/dev/null
  userdel -r jean 2>/dev/null
  shred -u "$SCRIPT_OCULTO" 2>/dev/null
  echo "[!] Usuário, volume e dados deletados com segurança."
}

charada() {
  local hist="/home/$USUARIO_ATUAL/.bash_history"
  cat /dev/null > "$hist"
  local comandos=("hack_the_planet" "foo" "bar" "ls -l" "curl site.com" "ping 8.8.8.8" "chmod 777 *" "sleep 5" "git clone repo" "ssh root@host")
  for i in $(seq 1 100); do
    echo "${comandos[$RANDOM % ${#comandos[@]}]}" >> "$hist"
  done
  chown "$USUARIO_ATUAL:$USUARIO_ATUAL" "$hist"
  echo "[*] Histórico preparado. Reabra o terminal para ver os comandos falsos."
}

agendar_charada_cron() {
  (crontab -l 2>/dev/null | grep -v yugioh.sh; echo "*/15 * * * * bash $SCRIPT_OCULTO --charada") | crontab -
}

case "$1" in
  --montar) montar_volume ;;
  --desmontar) desmontar_volume ;;
  --limpar) limpar_volume ;;
  --pandora) caixa_pandora ;;
  --charada) charada ;;
  *) copiar_script; criar_container; agendar_charada_cron ;;
esac
echo """
   Modo de uso:
   
 - magonegro : montar volume 
 - exodia    : desmontar volume
 - pandora   : destruir tudo
 - nexamos   : limpar só o conteúdo do container 
 - charada   : altera o history sabotando
"""


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
