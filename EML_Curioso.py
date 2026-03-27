import os
import re
import hashlib
from email import policy
from email.parser import BytesParser
from urllib.parse import urlparse
from colorama import Fore, Style, init

init(autoreset=True)

# =========================
# REGEX
# =========================
IP_REGEX = r'\b(?:[0-9]{1,3}\.){3}[0-9]{1,3}\b'
EMAIL_REGEX = r'[a-zA-Z0-9_.+-]+@[a-zA-Z0-9-]+\.[a-zA-Z0-9-.]+'
URL_REGEX = r'https?://[^\s"<>()]+'

FREE_MAIL = [
    "gmail.com","hotmail.com","outlook.com",
    "yahoo.com","icloud.com","live.com"
]

# =========================
# UTILS
# =========================
def sanitize_filename(name):
    return re.sub(r'[<>:"/\\|?*]', '_', name)

def sha256_bytes(data):
    return hashlib.sha256(data).hexdigest()

def extract_domain_from_email(addr):
    try:
        return addr.split("@")[1].lower()
    except:
        return ""

def extract_domain(url):
    try:
        return urlparse(url).netloc
    except:
        return ""

# =========================
# AUTH PARSE
# =========================
def parse_auth(msg):
    auth = msg.get("Authentication-Results", "").lower()

    dkim = "pass" if "dkim=pass" in auth else "fail" if "dkim=fail" in auth else "unknown"
    spf = "pass" if "spf=pass" in auth else "fail" if "spf=fail" in auth else "unknown"
    dmarc = "pass" if "dmarc=pass" in auth else "fail" if "dmarc=fail" in auth else "unknown"

    return dkim, spf, dmarc

# =========================
# SCORE
# =========================
def calc_score(spf, dkim, dmarc, urls, ips):
    score = 0
    if spf == "fail": score += 20
    if dkim == "fail": score += 20
    if dmarc == "fail": score += 25
    score += len(urls) * 3
    score += len(ips) * 2
    return min(score, 100)

# =========================
# ANALISE
# =========================
def analyze_eml(path):

    print(Fore.GREEN + "="*60)
    print(Fore.GREEN + f"ANALISANDO: {os.path.basename(path)}")
    print(Fore.GREEN + "="*60)

    with open(path, "rb") as f:
        msg = BytesParser(policy=policy.default).parse(f)

    raw = msg.as_string()

    ips = set(re.findall(IP_REGEX, raw))
    emails = set(re.findall(EMAIL_REGEX, raw))
    urls = set(re.findall(URL_REGEX, raw))
    domains = set(extract_domain(u) for u in urls if extract_domain(u))

    dkim, spf, dmarc = parse_auth(msg)

    # ================= EMAIL INFO =================
    subject = msg.get("Subject", "N/A")
    from_addr = msg.get("From", "N/A")
    to_addr = msg.get("To", "N/A")
    reply_to = msg.get("Reply-To", "N/A")
    date = msg.get("Date", "N/A")

    print(Fore.CYAN + "\nEMAIL INFO")
    print(Fore.WHITE + f"Subject: {subject}")
    print(Fore.WHITE + f"From: {from_addr}")
    print(Fore.WHITE + f"To: {to_addr}")
    print(Fore.WHITE + f"Reply-To: {reply_to}")
    print(Fore.WHITE + f"Date: {date}")

    # ================= SPOOF CHECK =================
    from_domain = extract_domain_from_email(from_addr)
    reply_domain = extract_domain_from_email(reply_to)

    if reply_domain and from_domain and reply_domain != from_domain:
        print(Fore.RED + "[ALERTA] Possível Spoofing (From != Reply-To)")

    if from_domain in FREE_MAIL:
        print(Fore.YELLOW + "[INFO] Remetente usando Free Mail")

    # ================= ANEXOS =================
    attach_hashes = []
    base_dir = os.path.dirname(path)
    base_name = sanitize_filename(os.path.splitext(os.path.basename(path))[0])
    attach_dir = os.path.join(base_dir, base_name + "_ATTACHMENTS")
    os.makedirs(attach_dir, exist_ok=True)

    for part in msg.iter_attachments():
        filename = part.get_filename()
        if not filename:
            continue

        filename = sanitize_filename(filename)
        data = part.get_payload(decode=True)
        save_path = os.path.join(attach_dir, filename)

        try:
            with open(save_path, "wb") as f:
                f.write(data)

            attach_hashes.append((filename, sha256_bytes(data)))

        except Exception as e:
            print(Fore.RED + f"[ERRO ANEXO] {filename} -> {e}")

    if attach_hashes:
        with open(os.path.join(attach_dir, "hashes.txt"), "w") as f:
            for n, h in attach_hashes:
                f.write(f"{n} | SHA256 | {h}\n")

    # ================= SCORE =================
    score = calc_score(spf, dkim, dmarc, urls, ips)

    if score < 40:
        risk = "LOW"
        color = Fore.GREEN
    elif score < 70:
        risk = "MEDIUM"
        color = Fore.YELLOW
    else:
        risk = "HIGH"
        color = Fore.RED

    # ================= OUTPUT =================
    print(Fore.CYAN + "\nRESUMO EXECUTIVO")
    print(color + f"Risk Score: {score}/100 -> {risk}")
    print(Fore.CYAN + f"SPF: {spf} | DKIM: {dkim} | DMARC: {dmarc}")

    print(Fore.MAGENTA + "\nIOC Counts:")
    print(Fore.WHITE + f"IPs: {len(ips)}")
    print(Fore.WHITE + f"URLs: {len(urls)}")
    print(Fore.WHITE + f"Emails: {len(emails)}")
    print(Fore.WHITE + f"Domínios URL: {len(domains)}")
    print(Fore.WHITE + f"Anexos: {len(attach_hashes)}")

# =========================
# MAIN
# =========================
if __name__ == "__main__":

    print(Fore.GREEN + "=== EML Threat Analyzer ===")
    target = input(Fore.CYAN + "Arquivo ou pasta EML: ").strip('"')

    if os.path.isfile(target):
        analyze_eml(target)

    elif os.path.isdir(target):
        for root, _, files in os.walk(target):
            for file in files:
                if file.lower().endswith(".eml"):
                    analyze_eml(os.path.join(root, file))
    else:
        print(Fore.RED + "Caminho inválido")
