import tkinter as tk
from tkinter import messagebox
import json, os, random, hashlib, time

# ================= CONFIG =================
USERS_FILE = "users.json"
CHAT_FILE = "chat.log"

SALDO_INICIAL = 1000
PRECO_CARTELA = 50

QTD_NUM = 6
RANGE_NUM = 20   # 🔥 balanceado

PREMIO_MIN = 500
PREMIO_MAX = 55000

# ================= UTIL =================
def hash_senha(s):
    return hashlib.sha256(s.encode()).hexdigest()

def load_users():
    if not os.path.exists(USERS_FILE):
        return {}
    return json.load(open(USERS_FILE))

def save_users(u):
    json.dump(u, open(USERS_FILE, "w"), indent=4)

def log_chat(msg):
    with open(CHAT_FILE, "a", encoding="utf-8") as f:
        f.write(msg + "\n")

def read_chat():
    if not os.path.exists(CHAT_FILE):
        return ""
    return open(CHAT_FILE, encoding="utf-8").read()

# ================= LOGIN =================
class Login(tk.Tk):
    def __init__(self):
        super().__init__()
        self.title("Login")
        self.geometry("300x200")

        tk.Label(self, text="Usuário").pack()
        self.user = tk.Entry(self)
        self.user.pack()

        tk.Label(self, text="Senha").pack()
        self.pw = tk.Entry(self, show="*")
        self.pw.pack()

        tk.Button(self, text="Login", command=self.login).pack(pady=5)
        tk.Button(self, text="Registrar", command=self.registrar).pack()

    def login(self):
        users = load_users()
        u = self.user.get()
        p = self.pw.get()

        if u in users and users[u]["password"] == hash_senha(p):
            self.destroy()
            Lobby(u)
        else:
            messagebox.showerror("Erro", "Login inválido")

    def registrar(self):
        users = load_users()
        u = self.user.get()
        p = self.pw.get()

        if u in users:
            messagebox.showerror("Erro", "Usuário já existe")
            return

        users[u] = {
            "password": hash_senha(p),
            "saldo": SALDO_INICIAL
        }
        save_users(users)
        messagebox.showinfo("OK", "Usuário registrado")

# ================= LOBBY =================
class Lobby(tk.Tk):
    def __init__(self, usuario):
        super().__init__()
        self.usuario = usuario
        self.users = load_users()
        self.cartelas = []
        self.jackpot = 0

        self.title(f"Lobby - {usuario}")
        self.geometry("750x550")

        self.lbl_saldo = tk.Label(self, text="")
        self.lbl_saldo.pack()

        # -------- Cartelas --------
        tk.Label(self, text="🎟️ Suas Cartelas").pack()
        self.lista_cartelas = tk.Listbox(self, height=6)
        self.lista_cartelas.pack(fill="x")

        # -------- Chat --------
        self.chat = tk.Text(self, state="disabled", height=10)
        self.chat.pack(fill="x", pady=5)

        self.msg = tk.Entry(self)
        self.msg.pack(fill="x")
        self.msg.bind("<Return>", self.send_msg)

        # -------- Botões --------
        frame = tk.Frame(self)
        frame.pack(pady=10)

        tk.Button(frame, text="🎲 Cartela Aleatória", command=self.cartela_random).pack(side="left", padx=5)
        tk.Button(frame, text="✍️ Cartela Personalizada", command=self.cartela_custom).pack(side="left", padx=5)
        tk.Button(frame, text="🎰 Sortear", command=self.sortear).pack(side="left", padx=5)

        self.after(1000, self.update_chat)
        self.update_saldo()
        self.mainloop()

    def update_saldo(self):
        self.users = load_users()
        self.lbl_saldo.config(
            text=f"💰 Saldo: {self.users[self.usuario]['saldo']} | 🎰 Jackpot: {self.jackpot}"
        )

    def send_msg(self, e=None):
        if self.msg.get().strip():
            log_chat(f"[{time.strftime('%H:%M:%S')}] {self.usuario}: {self.msg.get()}")
            self.msg.delete(0, tk.END)

    def update_chat(self):
        self.chat.config(state="normal")
        self.chat.delete("1.0", tk.END)
        self.chat.insert(tk.END, read_chat())
        self.chat.config(state="disabled")
        self.after(1000, self.update_chat)

    def comprar(self, numeros, tipo):
        if self.users[self.usuario]["saldo"] < PRECO_CARTELA:
            messagebox.showerror("Erro", "Saldo insuficiente")
            return

        self.users[self.usuario]["saldo"] -= PRECO_CARTELA
        save_users(self.users)

        self.cartelas.append({
            "jogador": self.usuario,
            "numeros": numeros
        })

        self.jackpot += int(PRECO_CARTELA * 0.2)

        emoji = "🎲" if tipo == "random" else "✍️"
        self.lista_cartelas.insert(tk.END, f"{emoji} {' '.join(map(str, numeros))}")

        self.update_saldo()

    def cartela_random(self):
        nums = sorted(random.sample(range(1, RANGE_NUM+1), QTD_NUM))
        self.comprar(nums, "random")

    def cartela_custom(self):
        win = tk.Toplevel(self)
        win.title("Cartela Personalizada")

        tk.Label(win, text=f"Digite {QTD_NUM} números (1 a {RANGE_NUM})").pack()
        entry = tk.Entry(win)
        entry.pack()

        def ok():
            try:
                nums = sorted(set(map(int, entry.get().split())))
                if len(nums) == QTD_NUM and all(1 <= n <= RANGE_NUM for n in nums):
                    win.destroy()
                    self.comprar(nums, "custom")
                else:
                    raise ValueError
            except:
                messagebox.showerror("Erro", "Números inválidos")

        tk.Button(win, text="Confirmar", command=ok).pack()

    def sortear(self):
        if not self.cartelas:
            messagebox.showerror("Erro", "Sem cartelas")
            return

        # 🎯 Sorteio levemente favorecido
        numeros_jogados = []
        for c in self.cartelas:
            numeros_jogados.extend(c["numeros"])

        fixo = random.choice(numeros_jogados)
        resto = random.sample(
            [n for n in range(1, RANGE_NUM+1) if n != fixo],
            QTD_NUM - 1
        )
        sorteio = set([fixo] + resto)

        premio = random.randint(PREMIO_MIN, PREMIO_MAX)

        vencedores = {6: [], 5: [], 4: []}

        for c in self.cartelas:
            acertos = len(sorteio & set(c["numeros"]))
            if acertos in vencedores:
                vencedores[acertos].append(c["jogador"])

        msg = f"Sorteio: {sorted(sorteio)}\n"

        if vencedores[6]:
            ganho = self.jackpot // len(vencedores[6])
            for v in vencedores[6]:
                self.users[v]["saldo"] += ganho
            self.jackpot = 0
            msg += f"🎰 JACKPOT! {vencedores[6]} ganharam {ganho}"
        elif vencedores[5] or vencedores[4]:
            faixa = 5 if vencedores[5] else 4
            ganhadores = vencedores[faixa]
            ganho = premio // len(ganhadores)
            for v in ganhadores:
                self.users[v]["saldo"] += ganho
            msg += f"🏆 {faixa} acertos: {ganhadores} (+{ganho})"
        else:
            msg += "❌ Ninguém ganhou"

        save_users(self.users)
        self.cartelas.clear()
        self.lista_cartelas.delete(0, tk.END)
        self.update_saldo()

        messagebox.showinfo("Resultado", msg)

# ================= START =================
Login().mainloop()
