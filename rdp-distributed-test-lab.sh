#!/bin/bash

INTERFACE="enp0s3"
RDP_TARGET="192.168.0.6"
USUARIO="nexamos"
SENHA="senhaerrada"

BRIDGE="br-rdp"
SUBNET="10.50.0"
NAMESPACES=("ns1" "ns2" "ns3")


#!/bin/bash

############################################################
# ███╗   ██╗███████╗██╗  ██╗ █████╗ ███╗   ███╗ ██████╗ ███████╗
# ████╗  ██║██╔════╝╚██╗██╔╝██╔══██╗████╗ ████║██╔═══██╗██╔════╝
# ██╔██╗ ██║█████╗   ╚███╔╝ ███████║██╔████╔██║██║   ██║███████╗
# ██║╚██╗██║██╔══╝   ██╔██╗ ██╔══██║██║╚██╔╝██║██║   ██║╚════██║
# ██║ ╚████║███████╗██╔╝ ██╗██║  ██║██║ ╚═╝ ██║╚██████╔╝███████║
# ╚═╝  ╚═══╝╚══════╝╚═╝  ╚═╝╚═╝  ╚═╝╚═╝     ╚═╝ ╚═════╝ ╚══════╝
#
#              RDP DISTRIBUTED TEST LAB
#                     by Nexamos
#
# ----------------------------------------------------------
# Script de laboratório para simulação de tentativas de
# autenticação RDP distribuídas usando Linux namespaces.
#
# O objetivo é gerar múltiplas conexões RDP a partir de
# diferentes IPs simulados para testar:
#
# • IDS / IPS
# • Fail2Ban
# • Firewall
# • Sistemas de detecção de brute force
#
# Funcionamento:
#
# 1. Cria uma bridge virtual no Linux
# 2. Cria múltiplos network namespaces
# 3. Cada namespace recebe um IP diferente
# 4. NAT é configurado para saída
# 5. Cada namespace executa tentativas RDP via xfreerdp
#
# Isso simula um ataque distribuído controlado para
# ambientes de teste e laboratório.
#
# Requisitos:
# • Linux
# • iproute2
# • iptables
# • xfreerdp
# • Permissão root
#
# Uso:
# Execute apenas em ambientes controlados de laboratório.
#
############################################################
cleanup() {
    echo "[*] Limpando ambiente..."

    for ns in "${NAMESPACES[@]}"; do
        sudo ip netns del $ns 2>/dev/null
    done

    sudo ip link set $BRIDGE down 2>/dev/null
    sudo ip link del $BRIDGE 2>/dev/null

    sudo iptables -t nat -D POSTROUTING -s ${SUBNET}.0/24 -o $INTERFACE -j MASQUERADE 2>/dev/null

    echo "[✓] Ambiente limpo."
}

trap cleanup EXIT

echo "[+] Criando bridge..."
sudo ip link add name $BRIDGE type bridge
sudo ip addr add ${SUBNET}.1/24 dev $BRIDGE
sudo ip link set $BRIDGE up

echo "[+] Habilitando NAT..."
sudo sysctl -w net.ipv4.ip_forward=1 >/dev/null
sudo iptables -t nat -A POSTROUTING -s ${SUBNET}.0/24 -o $INTERFACE -j MASQUERADE

COUNT=2

for ns in "${NAMESPACES[@]}"; do
    echo "[+] Criando namespace $ns"

    sudo ip netns add $ns

    sudo ip link add veth-$ns type veth peer name veth-br-$ns
    sudo ip link set veth-$ns netns $ns

    sudo ip link set veth-br-$ns master $BRIDGE
    sudo ip link set veth-br-$ns up

    sudo ip netns exec $ns ip addr add ${SUBNET}.$COUNT/24 dev veth-$ns
    sudo ip netns exec $ns ip link set veth-$ns up
    sudo ip netns exec $ns ip link set lo up
    sudo ip netns exec $ns ip route add default via ${SUBNET}.1

    COUNT=$((COUNT+1))
done

echo "[*] Iniciando tentativas RDP distribuídas..."

for ns in "${NAMESPACES[@]}"; do
    echo "[*] Namespace $ns"
    for i in {1..3}; do
        echo "   Tentativa $i"
        sudo ip netns exec $ns xfreerdp /v:$RDP_TARGET /u:$USUARIO /p:$SENHA /cert-ignore 2>/dev/null
    done
done

echo "[✓] Teste concluído."