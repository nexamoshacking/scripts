#!/bin/bash

############################################################
# ███╗   ██╗███████╗██╗  ██╗ █████╗ ███╗   ███╗ ██████╗ ███████╗
# ████╗  ██║██╔════╝╚██╗██╔╝██╔══██╗████╗ ████║██╔═══██╗██╔════╝
# ██╔██╗ ██║█████╗   ╚███╔╝ ███████║██╔████╔██║██║   ██║███████╗
# ██║╚██╗██║██╔══╝   ██╔██╗ ██╔══██║██║╚██╔╝██║██║   ██║╚════██║
# ██║ ╚████║███████╗██╔╝ ██╗██║  ██║██║ ╚═╝ ██║╚██████╔╝███████║
# ╚═╝  ╚═══╝╚══════╝╚═╝  ╚═╝╚═╝  ╚═╝╚═╝     ╚═╝ ╚═════╝ ╚══════╝
#
#                RDP DEFENSE MONITOR
#                   by Nexamos
#
# ----------------------------------------------------------
# Script de monitoramento de tentativas de login no XRDP.
#
# O sistema monitora em tempo real os logs do serviço XRDP
# e detecta falhas de autenticação vindas de IPs externos.
#
# Quando um IP excede o limite de tentativas definido,
# ele é automaticamente bloqueado via iptables.
#
# Funcionalidades:
# • Monitoramento em tempo real de ataques RDP
# • Detecção automática de brute force
# • Contador de tentativas por IP
# • Bloqueio automático de atacantes
#
# Requisitos:
# • Linux
# • XRDP instalado
# • Permissão root
# • iptables ativo
#
############################################################


MAX_ATTEMPTS=3
declare -A ATTEMPTS
LAST_IP=""

echo "================================="
echo "        NEXAMOS RDP GUARD"
echo "     Monitoring XRDP Attacks"
echo "================================="

# Redirecionando stderr para evitar logs truncados
journalctl -f -u xrdp 2>/dev/null | while read line; do

    # Captura IP da conexão
    if echo "$line" | grep -q "connection accepted from"; then
        LAST_IP=$(echo "$line" | grep -oE '([0-9]{1,3}\.){3}[0-9]{1,3}')
    fi

    # Detecta falha de autenticação
    if echo "$line" | grep -q "could not be authenticated"; then
        
        if [ ! -z "$LAST_IP" ]; then

            ((ATTEMPTS[$LAST_IP]++))

            echo "[ATTACK] IP: $LAST_IP | Attempts: ${ATTEMPTS[$LAST_IP]}"

            if [ ${ATTEMPTS[$LAST_IP]} -ge $MAX_ATTEMPTS ]; then
                echo "[BLOCKED] $LAST_IP added to firewall"

                iptables -A INPUT -s $LAST_IP -j DROP

                unset ATTEMPTS[$LAST_IP]
            fi
        fi
    fi

done