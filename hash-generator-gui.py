import hashlib
import tkinter as tk
from tkinter import filedialog, messagebox, ttk
import threading
import time

# -------- CORES -------- #
BG = "#0d1117"
FG = "#00ff9c"
BTN_BG = "#161b22"
ACTIVE = "#238636"
ENTRY_BG = "#010409"

# -------- FUNÇÕES -------- #

def log(msg):
    log_box.insert(tk.END, f"> {msg}\n")
    log_box.see(tk.END)

def animar_progresso():
    barra["value"] = 0
    for i in range(101):
        barra["value"] = i
        root.update_idletasks()
        time.sleep(0.01)

def gerar_hash_texto():
    def task():
        log("Gerando hash de texto...")
        animar_progresso()
        
        texto = entrada_texto.get("1.0", tk.END).strip().encode()
        if not texto:
            messagebox.showwarning("Erro", "Digite algo")
            return
        
        h = hashlib.new(algoritmo.get())
        h.update(texto)
        resultado.set(h.hexdigest())
        
        log("Hash gerado com sucesso ✔️")
    
    threading.Thread(target=task).start()

def hash_arquivo():
    caminho = filedialog.askopenfilename()
    if not caminho:
        return
    
    def task():
        log(f"Lendo arquivo: {caminho}")
        animar_progresso()
        
        h = hashlib.new(algoritmo.get())
        
        try:
            with open(caminho, "rb") as f:
                for bloco in iter(lambda: f.read(4096), b""):
                    h.update(bloco)
            
            resultado.set(h.hexdigest())
            log("Hash de arquivo gerado ✔️")
        
        except:
            messagebox.showerror("Erro", "Falha ao ler arquivo")
    
    threading.Thread(target=task).start()

def comparar_hash():
    if entrada_hash1.get() == entrada_hash2.get():
        log("MATCH ✔️")
        messagebox.showinfo("Resultado", "Hashes iguais")
    else:
        log("NO MATCH ❌")
        messagebox.showerror("Resultado", "Hashes diferentes")

# -------- UI -------- #

root = tk.Tk()
root.title("HASH TOOL // DARK")
root.geometry("700x650")
root.configure(bg=BG)

algoritmo = tk.StringVar(value="sha256")
resultado = tk.StringVar()

# ---- ESTILO DA BARRA ---- #
style = ttk.Style()
style.theme_use('default')
style.configure("TProgressbar",
                troughcolor=BG,
                background="#00ff9c",
                thickness=10)

# ---- TÍTULO ---- #
tk.Label(root, text="HASH TOOL", fg=FG, bg=BG,
         font=("Consolas", 20, "bold")).pack(pady=10)

# ---- TEXTO ---- #
tk.Label(root, text="INPUT TEXT", fg=FG, bg=BG).pack()
entrada_texto = tk.Text(root, height=4, bg=ENTRY_BG, fg=FG,
                        insertbackground=FG, relief="flat")
entrada_texto.pack(pady=5, fill="x", padx=20)

tk.Button(root, text="GENERATE HASH",
          command=gerar_hash_texto,
          bg=BTN_BG, fg=FG, relief="flat").pack(pady=5)

# ---- ARQUIVO ---- #
tk.Button(root, text="SELECT FILE",
          command=hash_arquivo,
          bg=BTN_BG, fg=FG, relief="flat").pack(pady=5)

# ---- ALGORITMOS BONITOS ---- #
tk.Label(root, text="ALGORITHM", fg=FG, bg=BG).pack()

frame_alg = tk.Frame(root, bg=BG)
frame_alg.pack(pady=5)

botoes_alg = {}

def set_alg(valor):
    algoritmo.set(valor)
    for nome, botao in botoes_alg.items():
        if nome == valor:
            botao.config(bg=ACTIVE)
        else:
            botao.config(bg=BTN_BG)

for alg in ["md5", "sha1", "sha256", "sha512"]:
    btn = tk.Button(frame_alg,
                    text=alg.upper(),
                    command=lambda a=alg: set_alg(a),
                    bg=BTN_BG,
                    fg=FG,
                    relief="flat",
                    width=10)
    btn.pack(side="left", padx=5)
    botoes_alg[alg] = btn

set_alg("sha256")

# ---- RESULTADO ---- #
tk.Label(root, text="OUTPUT HASH", fg=FG, bg=BG).pack()

tk.Entry(root, textvariable=resultado,
         bg=ENTRY_BG, fg=FG,
         insertbackground=FG,
         width=80, relief="flat").pack(pady=5, padx=20)

# ---- PROGRESSO ---- #
barra = ttk.Progressbar(root, length=400, mode='determinate')
barra.pack(pady=10)

# ---- COMPARAÇÃO ---- #
tk.Label(root, text="COMPARE HASHES", fg=FG, bg=BG).pack(pady=10)

entrada_hash1 = tk.Entry(root, width=70, bg=ENTRY_BG, fg=FG,
                         insertbackground=FG, relief="flat")
entrada_hash1.pack(pady=2)

entrada_hash2 = tk.Entry(root, width=70, bg=ENTRY_BG, fg=FG,
                         insertbackground=FG, relief="flat")
entrada_hash2.pack(pady=2)
#Bons sonhos beijao NXMS
tk.Button(root, text="COMPARE",
          command=comparar_hash,
          bg=BTN_BG, fg=FG, relief="flat").pack(pady=5)

# ---- LOGS (EFEITO TERMINAL) ---- #
tk.Label(root, text="LOG OUTPUT", fg=FG, bg=BG).pack(pady=5)

log_box = tk.Text(root, height=8, bg="#010409", fg="#58a6ff",
                  insertbackground=FG, relief="flat")
log_box.pack(fill="both", padx=20, pady=5)

# ---- RODAPÉ ---- #
tk.Label(root, text="> cyber tool // hashing module",
         fg="#6e7681", bg=BG).pack(side="bottom", pady=10)

root.mainloop()