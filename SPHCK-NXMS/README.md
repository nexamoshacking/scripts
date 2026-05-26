![](.extras/assets/sl-hack-ware.jpg)

# Sl (hack) ware

### a Slackware GNU/Linux Pentesting Suite

The aim of this project is to bring a curated collection of programs, tools, libraries and various utilities, ~~packaged~~ (some packages are way too big, sorry) and ready to be installed on Slackware.

### Why Slackware

Because it's the best distro ever.

### We have Kali and/or Parrot

Yes, but I prefer Slackware.

## Packages List

This list is ever growing, if you want to ask for a package to be prioritized, just open an issue

| Package Name         | SlackBuilds.org available | Upstream                                                     | Version    |
| -------------------- | ------------------------- | ------------------------------------------------------------ | ---------- |
| SecLists             | ✅                         | [danielmiessler/SecLists](https://github.com/danielmiessler/SecLists) | 2026.1 |
| ffuf                 | ✅                         | [ffuf/ffuf](https://github.com/ffuf/ffuf)                    | 2.1.0      |
| gobuster             | ✅                         | [OJ/gobuster](https://github.com/OJ/gobuster)                | 3.8.2      |
| hashcat              | ✅                         | [hashcat.net](https://hashcat.net/hashcat/)                  | 7.1.2      |
| john                 | ✅                         | [openwall.com](https://www.openwall.com/john/)               | 1.9.0      |
| exploitdb            | ✅                         | [exploit-db.com](https://www.exploit-db.com/)                | 2026-04-30 |
| cadaver              | ✅                         | [notroj/cadaver](https://notroj.github.io/cadaver/)          | 0.28       |
| nuclei               | ✅                         | [projectdiscovery/nuclei](https://github.com/projectdiscovery/nuclei) | 3.8.0      |
| windows binaries     | ❎                         | [kali.org](https://www.kali.org/tools/windows-binaries/)     | 0.6.10     |
| webshells            | ❎                         | [kali.org](https://www.kali.org/tools/webshells/)            | 1.1        |
| metasploit framework | ❎                         | [metasploit.com](https://www.metasploit.com/)                | 6.4.133   |

> [!IMPORTANT]
>
> The exploitdb package pulls also the binsploits which consists of 1.1Gb of exploits.

> [!NOTE]
>
> There's a metasploit package on slackbuilds.org but is an older version (last updated in 2022). I'll contact the mantainer and ask to transfer it to me and I'll update it.
>
> The cadaver package is available on slackbuilds.org but it's for an older version. I've reported here the script and built the newest version. The slackbuild includes now a pull from the [notroj/neon](https://github.com/notroj/neon) repository which is usually not allowed for SlackBuilds that are uploaded to slackbuilds.org
>
> The Powershell package is available on slackbuilds.org without modifications necessary so I removed it.
