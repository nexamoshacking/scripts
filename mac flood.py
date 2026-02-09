from scapy.all import *
import random
import time

# ===== SUA INTERFACE WIFI =====
IFACE = r"\Device\NPF_{EF36A7A0-89B7-433C-B9EA-9C8EC0F122AA}"

# ===== CONFIG =====
NUM_DEVICES = 999
GATEWAY = "192.168.0.1"
NETWORK_BASE = "192.168.0."

# ===== GERAR DISPOSITIVOS =====
devices = []

for i in range(2, 2 + NUM_DEVICES):
    device = {
        "ip": NETWORK_BASE + str(i),
        "mac": str(RandMAC())
    }
    devices.append(device)

print(f"{len(devices)} dispositivos criados")

# ===== GERADORES DE TRÁFEGO =====

def send_ping(device):
    pkt = Ether(src=device["mac"]) / IP(
        src=device["ip"],
        dst=GATEWAY
    ) / ICMP()

    sendp(pkt, iface=IFACE, verbose=False)


def send_web(device):
    pkt = Ether(src=device["mac"]) / IP(
        src=device["ip"],
        dst=GATEWAY
    ) / TCP(
        sport=random.randint(1024, 65535),
        dport=80
    )

    sendp(pkt, iface=IFACE, verbose=False)


def send_dns(device):
    pkt = Ether(src=device["mac"]) / IP(
        src=device["ip"],
        dst=GATEWAY
    ) / UDP(
        sport=random.randint(1024, 65535),
        dport=53
    )

    sendp(pkt, iface=IFACE, verbose=False)

# ===== LOOP PRINCIPAL =====

print("Simulando rede fake... CTRL+C para parar")

try:
    while True:

        device = random.choice(devices)
        traffic_type = random.choice(["ping", "web", "dns"])

        if traffic_type == "ping":
            send_ping(device)

        elif traffic_type == "web":
            send_web(device)

        elif traffic_type == "dns":
            send_dns(device)

        time.sleep(random.uniform(0.05, 0.3))

except KeyboardInterrupt:
    print("Parado.")
