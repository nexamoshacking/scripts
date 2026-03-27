import sys
import asyncio
import time
import random
import webbrowser
import websockets
from cryptography.fernet import Fernet

from PySide6.QtWidgets import (
    QApplication, QWidget, QVBoxLayout, QHBoxLayout,
    QTextEdit, QLineEdit, QLabel, QPushButton, QCheckBox
)
from PySide6.QtCore import QThread, Signal

# ================= CONFIG =================
SERVER = "ws://ip-aqui:8765"
KEY = b'3o7V9y1FZ0N5uFJm7c9qY2m0Qn8kZBzQbJ6XkZPZ0eI='
cipher = Fernet(KEY)

GREEN = "#22c55e"

NICKS = [
    # clássicos / hacker
    "root","ghost","void","entropy","chaos","nmap","xor","kernel",
    "shadow","null","daemon","exploit","phantom","overflow",
    "segfault","hex","matrix","cipher","zero","glitch",

    # técnicos / baixo nível
    "syscall","stack","heap","ptr","malloc","free","opcode",
    "payload","shell","reverse","bind","packet","socket",
    "buffer","leak","panic","core","thread","fork",

    # cyber / dark
    "blackout","nightfall","umbra","noctis","oblivion",
    "reaper","wraith","specter","shade","veil","echo",
    "pulse","frost","ember","secretario","smoke","static",

    # latim / oculto
    "nexus","aether","arcana","infernum","lux","umbra",
    "ordo","chaosx","nihil","vita","mors","ignis","terra",

    # aleatórios estilizados
    "xeno","kryp","z3r0","v0id","sh4d0w","d4rk","phx",
    "qx","rx","zx","vx","nx","kx","mx",

    # nonsense bons
    "blip","zap","flux","warp","drift","fract","pulse",
    "noise","spark","ion","neon","plasma","quantum",

    # nomes únicos
    "nex","nexis","nexamos","nexx","nyx","nyxel","nyxor",
    "axion","axiom","exodus","anomaly","singularity"
]


# ================= WS THREAD =================
class WSClient(QThread):
    received = Signal(str)
    status = Signal(str)

    def __init__(self):
        super().__init__()
        self.loop = asyncio.new_event_loop()
        self.ws = None

    def run(self):
        asyncio.set_event_loop(self.loop)
        self.loop.run_until_complete(self.main())

    async def main(self):
        try:
            async with websockets.connect(SERVER) as ws:
                self.ws = ws
                self.status.emit("🟢 Conectado")
                async for msg in ws:
                    try:
                        text = cipher.decrypt(msg.encode()).decode()
                        self.received.emit(text)
                    except:
                        pass
        except:
            self.status.emit("🔴 Desconectado")

    def send(self, text):
        if not self.ws:
            return
        asyncio.run_coroutine_threadsafe(
            self.ws.send(cipher.encrypt(text.encode()).decode()),
            self.loop
        )

# ================= UI =================
class Chat(QWidget):
    def __init__(self):
        super().__init__()
        self.setWindowTitle("👽⃤ Birutinha 🍁🥴")
        self.resize(560, 640)

        self.nick = self.random_nick()

        main = QVBoxLayout(self)

        # ===== TOP =====
        top = QHBoxLayout()
        self.nick_input = QLineEdit(self.nick)
        self.nick_btn = QPushButton("🎲")
        self.nick_btn.clicked.connect(self.set_random_nick)

        self.allow_exec = QCheckBox("Louvar a Nexamos")
        self.allow_exec.setChecked(True)
        self.status_lbl = QLabel("🔴 Conectando...")

        top.addWidget(QLabel("Nick:"))
        top.addWidget(self.nick_input)
        top.addWidget(self.nick_btn)
        top.addStretch()
        top.addWidget(self.allow_exec)
        top.addWidget(self.status_lbl)

        # ===== CHAT =====
        self.chat = QTextEdit()
        self.chat.setReadOnly(True)

        # ===== INPUT =====
        bottom = QHBoxLayout()
        self.input = QLineEdit()
        self.input.setPlaceholderText("Digite a mensagem...")
        self.input.returnPressed.connect(self.send_msg)

        self.send_btn = QPushButton("ENVIAR")
        self.send_btn.clicked.connect(self.send_msg)

        bottom.addWidget(self.input)
        bottom.addWidget(self.send_btn)

        main.addLayout(top)
        main.addWidget(self.chat)
        main.addLayout(bottom)

        # ===== STYLE =====
        self.setStyleSheet(f"""
        QWidget {{
            background:#020617;
            color:{GREEN};
            font-family: Consolas;
        }}
        QTextEdit {{
            background:#020617;
            border:1px solid {GREEN};
            border-radius:10px;
            padding:10px;
        }}
        QLineEdit {{
            background:#020617;
            border:1px solid {GREEN};
            border-radius:8px;
            padding:8px;
            color:{GREEN};
        }}
        QPushButton {{
            background:#020617;
            border:1px solid {GREEN};
            border-radius:8px;
            padding:8px 12px;
            color:{GREEN};
        }}
        QPushButton:hover {{
            background:{GREEN};
            color:#020617;
        }}
        QLabel, QCheckBox {{
            color:{GREEN};
        }}
        """)

        # ===== WS =====
        self.ws = WSClient()
        self.ws.received.connect(self.add_msg)
        self.ws.status.connect(self.status_lbl.setText)
        self.ws.start()

    # ================= LOGIC =================
    def random_nick(self):
        return random.choice(NICKS) + str(random.randint(10, 99))

    def set_random_nick(self):
        self.nick = self.random_nick()
        self.nick_input.setText(self.nick)

    def add_msg(self, msg):
        self.chat.append(msg)
        self.chat.verticalScrollBar().setValue(
            self.chat.verticalScrollBar().maximum()
        )

        # ===== /nexamos COMMAND =====
        if not self.allow_exec.isChecked():
            return

        if ">" not in msg:
            return

        content = msg.split(">", 1)[1].strip().lower()

        if content.startswith("/nexamos"):
            parts = content.split(" ", 1)
            url = "https://www.xvideos.com"

            if len(parts) == 2:
                url = parts[1].strip()
                if not url.startswith("http"):
                    url = "https://" + url

            webbrowser.open(url)

    def send_msg(self):
        text = self.input.text().strip()
        if not text:
            return

        self.nick = self.nick_input.text().strip() or self.nick
        ts = time.strftime("%H:%M:%S")
        payload = f"[{ts}] <{self.nick}> {text}"

        self.ws.send(payload)
        self.input.clear()

# ================= START =================
app = QApplication(sys.argv)
w = Chat()
w.show()
sys.exit(app.exec())
