#! /usr/bin/env python3
# IluminaTOR by Nexamos

import random
from subprocess import CalledProcessError, call, check_call, getoutput
from argparse import ArgumentParser
from atexit import register
from itertools import chain
from json import load
from os import devnull
from os.path import basename, isfile
from sys import exit
from time import sleep, time
from urllib.error import URLError
from urllib.request import urlopen

from stem import Signal
from stem.control import Controller


class TorConfig:
    local_dnsport = "53"
    virtual_net = "10.0.0.0/10"
    local_loopback = "127.0.0.1"
    non_tor_net = ["192.168.0.0/16", "172.16.0.0/12"]
    non_tor = ["127.0.0.0/9", "127.128.0.0/10", "127.0.0.0/8"]
    tor_uid = getoutput("id -ur debian-tor")
    trans_port = "9040"
    tor_config_file = '/etc/tor/torrc'
    torrc = r'''
## Inserted by %s for tor iptables rules set
## Transparently route all traffic thru tor on port %s
VirtualAddrNetwork %s
AutomapHostsOnResolve 1
TransPort %s
DNSPort %s
''' % (basename(__file__), trans_port, virtual_net, trans_port, local_dnsport)


class TorIptables(TorConfig):

    def __init__(self):
        super(TorConfig, self).__init__()

    def show_ip_address(self, my_ip_addr):
        call(["notify-send", f"Seu novo IP via Tor: {my_ip_addr}"])

    def flush_iptables_rules(self):
        call(["iptables", "-F"])
        call(["iptables", "-t", "nat", "-F"])

    def load_iptables_rules(self):
        self.flush_iptables_rules()

        @register
        def restart_tor():
            fnull = open(devnull, 'w')
            try:
                tor_restart = check_call(
                    ["service", "tor", "restart"],
                    stdout=fnull, stderr=fnull)

                if tor_restart == 0:
                    print("[+] IluminaTOR by Nexamos: Anonimato ativado")
                    print("[*] Obtendo IP público via Tor...")
                    retries = 0
                    my_public_ip = None
                    while retries < 12 and not my_public_ip:
                        retries += 1
                        try:
                            my_public_ip = load(urlopen('https://check.torproject.org/api/ip'))['IP']
                        except URLError:
                            sleep(5)
                            print("[?] Ainda tentando obter IP...")
                        except ValueError:
                            break
                    if not my_public_ip:
                        my_public_ip = getoutput('wget -qO - ident.me')
                    if not my_public_ip:
                        exit("[!] Não foi possível obter o IP público!")
                    print(f"[+] Seu IP via Tor: {my_public_ip}")
                    self.show_ip_address(my_public_ip)
            except CalledProcessError as err:
                print(f"[!] Falha ao reiniciar Tor: {' '.join(err.cmd)}")

        non_tor = list(chain(self.non_tor, self.non_tor_net))

        call([
            "iptables", "-I", "OUTPUT", "!", "-o", "lo", "!", "-d",
            self.local_loopback, "!", "-s", self.local_loopback, "-p", "tcp",
            "-m", "tcp", "--tcp-flags", "ACK,FIN", "ACK,FIN", "-j", "DROP"
        ])
        call([
            "iptables", "-I", "OUTPUT", "!", "-o", "lo", "!", "-d",
            self.local_loopback, "!", "-s", self.local_loopback, "-p", "tcp",
            "-m", "tcp", "--tcp-flags", "ACK,RST", "ACK,RST", "-j", "DROP"
        ])

        call([
            "iptables", "-t", "nat", "-A", "OUTPUT", "-m", "owner", "--uid-owner",
            self.tor_uid, "-j", "RETURN"
        ])
        call([
            "iptables", "-t", "nat", "-A", "OUTPUT", "-p", "udp", "--dport",
            self.local_dnsport, "-j", "REDIRECT", "--to-ports", self.local_dnsport
        ])

        for net in non_tor:
            call([
                "iptables", "-t", "nat", "-A", "OUTPUT", "-d", net, "-j", "RETURN"
            ])

        call([
            "iptables", "-t", "nat", "-A", "OUTPUT", "-p", "tcp", "--syn", "-j",
            "REDIRECT", "--to-ports", self.trans_port
        ])
        call([
            "iptables", "-A", "OUTPUT", "-m", "state", "--state",
            "ESTABLISHED,RELATED", "-j", "ACCEPT"
        ])

        for net in non_tor:
            call(["iptables", "-A", "OUTPUT", "-d", net, "-j", "ACCEPT"])

        call([
            "iptables", "-A", "OUTPUT", "-m", "owner", "--uid-owner",
            self.tor_uid, "-j", "ACCEPT"
        ])
        call(["iptables", "-A", "OUTPUT", "-j", "REJECT"])


def renovar_ip_tor():
    try:
        with Controller.from_port(port=9051) as controller:
            controller.authenticate()  # Se tiver senha, passe aqui como controller.authenticate(password='sua_senha')
            controller.signal(Signal.NEWNYM)
            print("[+] Sinal NEWNYM enviado para renovar IP Tor")
    except Exception as e:
        print(f"[!] Erro ao renovar IP Tor: {e}")


def get_ip_tor():
    try:
        ip = load(urlopen('https://check.torproject.org/api/ip'))['IP']
        return ip
    except:
        return None


def baixar_frases():
    try:
        with urlopen("https://pastebin.com/raw/VytbaBNb") as response:
            content = response.read().decode()
            frases = [linha.strip() for linha in content.splitlines() if linha.strip()]
            return frases
    except Exception as e:
        print(f"[!] Erro ao baixar frases: {e}")
        return []


def notificar(mensagem, duracao_ms=10000):
    # Usa notify-send com timeout (segundos)
    segundos = duracao_ms // 1000
    call(["notify-send", "-t", str(duracao_ms), mensagem])


def loop_frases_ip():
    frases = baixar_frases()
    if not frases:
        print("[!] Nenhuma frase encontrada no Pastebin.")
        return

    # Notifica "Nexamos te ama <3" só uma vez no começo
    notificar("Nexamos te ama <3", 5000)
    print("Nexamos te ama <3")

    ultimo_renew = 0
    interval_renew = 300  # 5 minutos em segundos

    while True:
        agora = time()
        if agora - ultimo_renew >= interval_renew:
            renovar_ip_tor()
            sleep(10)  # espera o Tor trocar IP
            ip_novo = get_ip_tor()
            if ip_novo:
                print(f"[+] Novo IP via Tor: {ip_novo}")
                notificar(f"Novo IP via Tor: {ip_novo}", 10000)
            else:
                print("[!] Não foi possível obter o novo IP via Tor")
            ultimo_renew = agora

        frase = random.choice(frases)
        print(f"[+] Frase exibida: \"{frase}\"")
        notificar(frase, 60000)

        sleep(60)  # espera 1 minuto


if __name__ == '__main__':
    parser = ArgumentParser(description='IluminaTOR by Nexamos - Roteamento global via Tor')
    parser.add_argument(
        '--start',
        action='store_true',
        help='Ativa regras de iptables e roteamento via Tor')
    parser.add_argument(
        '--flush',
        action='store_true',
        help='Remove as regras e retorna ao padrão')
    args = parser.parse_args()

    try:
        tor = TorIptables()
        if isfile(tor.tor_config_file):
            if 'VirtualAddrNetwork' not in open(tor.tor_config_file).read():
                with open(tor.tor_config_file, 'a+') as torrconf:
                    torrconf.write(tor.torrc)

        if args.start:
            tor.load_iptables_rules()
            loop_frases_ip()
        elif args.flush:
            tor.flush_iptables_rules()
            print("[!] IluminaTOR by Nexamos: Anonimato desativado")
            try:
                try:
                    my_real_ip = load(urlopen('https://check.torproject.org/api/ip'))['IP']
                except (URLError, ValueError):
                    my_real_ip = getoutput('wget -qO - ident.me')
                tor.show_ip_address(my_real_ip)
            except:
                pass
        else:
            parser.print_help()
    except Exception as e:
        print(f"[!] Execute como superusuário! Erro: {e}")
