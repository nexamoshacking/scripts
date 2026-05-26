#!/bin/bash

set -e

clear

echo "=========================================="
echo "        Sl (hack) ware Installer"
echo "=========================================="
echo
echo " Created by the father Nexamos"
echo " Dedicated to Mist, MY ORGULHO"
echo
echo " Slackware supremacy by NEXAMOS and YOUR SON MIST RAVEN. FUCK SCRIPT KIDDIES _)_  <---- PIKA PRA VOCES  ."
echo "=========================================="
echo

for dir in */ ; do

    [ -d "$dir" ] || continue

    cd "$dir"

    BUILD_SCRIPT=$(find . -maxdepth 1 -name "*.SlackBuild" | head -n 1)

    if [ -n "$BUILD_SCRIPT" ]; then

        PKG=$(basename "$BUILD_SCRIPT" .SlackBuild)

        echo "[+] Building $PKG"

        chmod +x "$BUILD_SCRIPT"

        sudo ./"$BUILD_SCRIPT"

        PACKAGE=$(find /tmp -name "${PKG}-*.txz" | tail -n 1)

        if [ -n "$PACKAGE" ]; then
            echo "[+] Installing $PKG"
            sudo upgradepkg --install-new "$PACKAGE"

            echo "[+] $PKG installed successfully"
        else
            echo "[-] Compiled package not found for $PKG"
        fi

    else
        echo "[-] No SlackBuild found inside $dir"
    fi

    cd ..

    echo

done
#TA VENDO SE TEM TROJAN? VA TOMAR NO SEU CU
echo "=========================================="
echo " All packages processed."
echo
echo " Glory to Mist."
echo " Long live Nexamos."
echo "=========================================="