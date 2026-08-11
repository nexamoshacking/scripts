import socket
import concurrent.futures
import ipaddress
import json
import time
import re
from http.server import HTTPServer, BaseHTTPRequestHandler
from urllib.parse import parse_qs, urlparse
import threading
import webbrowser

# Portas e serviços conhecidos
COMMON_PORTS = {
    21: "FTP", 22: "SSH", 23: "Telnet", 25: "SMTP", 53: "DNS",
    80: "HTTP", 110: "POP3", 135: "RPC", 139: "NetBIOS", 143: "IMAP",
    443: "HTTPS", 445: "SMB", 1433: "MSSQL", 1521: "Oracle", 3306: "MySQL",
    3389: "RDP", 5432: "PostgreSQL", 5900: "VNC", 6379: "Redis", 8080: "HTTP-Alt",
    8443: "HTTPS-Alt", 27017: "MongoDB"
}

TOP_20_PORTS = [21, 22, 23, 25, 53, 80, 110, 135, 139, 143, 443, 445, 1433, 3306, 3389, 5432, 5900, 8080, 8443, 27017]

class ScannerEngine:
    @staticmethod
    def parse_targets(target_str):
        targets = []
        target_str = target_str.strip()
        
        # Intervalo de IPs Ex: 192.168.1.1-10
        if "-" in target_str and not target_str.endswith("-"):
            parts = target_str.split("-")
            base_ip = parts[0].strip()
            end_num = int(parts[1].strip())
            start_num = int(base_ip.split(".")[-1])
            prefix = ".".join(base_ip.split(".")[:-1])
            for i in range(start_num, end_num + 1):
                targets.append(f"{prefix}.{i}")
            return targets

        # CIDR Ex: 192.168.1.0/28
        try:
            net = ipaddress.ip_network(target_str, strict=False)
            return [str(ip) for ip in net.hosts()]
        except ValueError:
            pass

        # IP único ou Domínio
        try:
            ip = socket.gethostbyname(target_str)
            targets.append(ip)
        except socket.gaierror:
            pass
            
        return targets

    @staticmethod
    def scan_port(ip, port, timeout=1.0):
        result = {"ip": ip, "port": port, "status": "closed", "service": COMMON_PORTS.get(port, "Unknown"), "banner": ""}
        try:
            with socket.socket(socket.AF_INET, socket.SOCK_STREAM) as s:
                s.settimeout(timeout)
                res = s.connect_ex((ip, port))
                if res == 0:
                    result["status"] = "open"
                    # Banner grabbing simples
                    try:
                        s.sendall(b"HEAD / HTTP/1.0\r\n\r\n")
                        banner = s.recv(256).decode('utf-8', errors='ignore').strip()
                        result["banner"] = banner.split('\n')[0][:50] if banner else ""
                    except:
                        pass
        except Exception:
            pass
        return result

# Template HTML/CSS/JS da Interface Dark/Red
HTML_INTERFACE = """
<!DOCTYPE html>
<html lang="pt-BR">
<head>
    <meta charset="UTF-8">
    <title>RED VIPER - Port Scanner</title>
    <style>
        :root {
            --bg-dark: #0a0a0c;
            --card-bg: #121216;
            --accent-red: #ff2a4b;
            --red-glow: rgba(255, 42, 75, 0.4);
            --text-main: #f0f0f5;
            --text-muted: #8a8a9e;
            --border-color: #242430;
        }

        * { box-sizing: border-box; margin: 0; padding: 0; font-family: 'Segoe UI', monospace, sans-serif; }
        body { background-color: var(--bg-dark); color: var(--text-main); padding: 25px; min-height: 100vh; }

        .header { display: flex; align-items: center; justify-content: space-between; padding-bottom: 20px; border-bottom: 2px solid var(--accent-red); margin-bottom: 25px; }
        .logo { font-size: 24px; font-weight: bold; color: var(--accent-red); text-shadow: 0 0 10px var(--red-glow); letter-spacing: 2px; }

        .grid { display: grid; grid-template-columns: 340px 1fr; gap: 20px; }
        .panel { background: var(--card-bg); border: 1px solid var(--border-color); border-radius: 8px; padding: 20px; }
        
        .form-group { margin-bottom: 15px; }
        label { display: block; font-size: 12px; text-transform: uppercase; color: var(--text-muted); margin-bottom: 6px; letter-spacing: 1px; }
        input, select { width: 100%; padding: 10px; background: #070709; border: 1px solid var(--border-color); color: #fff; border-radius: 4px; outline: none; }
        input:focus { border-color: var(--accent-red); box-shadow: 0 0 8px var(--red-glow); }

        .btn { width: 100%; padding: 12px; background: var(--accent-red); color: white; border: none; border-radius: 4px; font-weight: bold; cursor: pointer; text-transform: uppercase; letter-spacing: 1px; transition: 0.2s; }
        .btn:hover { background: #e01f3d; box-shadow: 0 0 15px var(--red-glow); }

        .stats-bar { display: flex; gap: 15px; margin-bottom: 20px; }
        .stat-card { flex: 1; background: var(--card-bg); padding: 15px; border-radius: 6px; border-left: 3px solid var(--accent-red); }
        .stat-val { font-size: 22px; font-weight: bold; color: var(--accent-red); }

        .progress-box { height: 6px; background: #1a1a24; border-radius: 3px; overflow: hidden; margin-bottom: 20px; }
        .progress-bar { height: 100%; width: 0%; background: var(--accent-red); box-shadow: 0 0 10px var(--red-glow); transition: width 0.3s; }

        table { width: 100%; border-collapse: collapse; text-align: left; }
        th { background: #181820; color: var(--text-muted); padding: 12px; font-size: 12px; text-transform: uppercase; border-bottom: 1px solid var(--border-color); }
        td { padding: 12px; border-bottom: 1px solid var(--border-color); font-size: 14px; }
        tr:hover { background: rgba(255, 42, 75, 0.05); }

        .badge-open { color: #00ff88; font-weight: bold; text-shadow: 0 0 5px rgba(0,255,136,0.3); }
        .log-box { background: #050507; border: 1px solid var(--border-color); padding: 10px; height: 120px; border-radius: 4px; overflow-y: auto; font-size: 12px; color: #aaa; margin-top: 15px; }
    </style>
</head>
<body>

    <div class="header">
        <div class="logo">⚡ DRAGÃO DE OLHOS VERMELHOS // PORT SCANNER by NXMS</div>
        <button class="btn" style="width: auto; padding: 8px 16px;" onclick="exportJSON()">Exportar JSON</button>
    </div>

    <div class="grid">
        <div class="panel">
            <div class="form-group">
                <label>Alvo (IP, CIDR, Faixa ou Host)</label>
                <input type="text" id="target" value="scanme.nmap.org" placeholder="Ex: 192.168.1.1 ou 10.0.0.1-20">
            </div>

            <div class="form-group">
                <label>Modo de Portas</label>
                <select id="portMode" onchange="toggleCustomPorts()">
                    <option value="top20">Top 20 Portas Principais</option>
                    <option value="common">Top 100 Portas Comuns</option>
                    <option value="full">Varredura Completa (1-65535)</option>
                    <option value="custom">Faixa Customizada</option>
                </select>
            </div>

            <div class="form-group" id="customPortsGroup" style="display:none;">
                <label>Intervalo Customizado (Ex: 20-8080)</label>
                <input type="text" id="customPorts" value="20-100">
            </div>

            <div class="form-group">
                <label>Threads Paralelas (Velocidade)</label>
                <input type="number" id="threads" value="100" min="10" max="500">
            </div>

            <div class="form-group">
                <label>Timeout (Segundos)</label>
                <input type="number" id="timeout" value="0.8" step="0.1">
            </div>

            <button class="btn" onclick="startScan()" id="btnScan">Iniciar Varredura</button>
        </div>

        <div>
            <div class="stats-bar">
                <div class="stat-card">
                    <div style="font-size: 12px; color: var(--text-muted)">ALVOS ENCONTRADOS</div>
                    <div class="stat-val" id="statTargets">0</div>
                </div>
                <div class="stat-card">
                    <div style="font-size: 12px; color: var(--text-muted)">PORTAS ABERTAS</div>
                    <div class="stat-val" id="statOpen">0</div>
                </div>
                <div class="stat-card">
                    <div style="font-size: 12px; color: var(--text-muted)">TEMPO DE EXECUÇÃO</div>
                    <div class="stat-val" id="statTime">0.0s</div>
                </div>
            </div>

            <div class="progress-box">
                <div class="progress-bar" id="progressBar"></div>
            </div>

            <div class="panel">
                <table>
                    <thead>
                        <tr>
                            <th>Endereço IP</th>
                            <th>Porta</th>
                            <th>Status</th>
                            <th>Serviço</th>
                            <th>Banner / Informação</th>
                        </tr>
                    </thead>
                    <tbody id="resultsBody">
                        <tr><td colspan="5" style="text-align:center; color: var(--text-muted);">Aguardando início do scan...</td></tr>
                    </tbody>
                </table>
            </div>

            <div class="log-box" id="logBox">> Sistema pronto. Insira o alvo para começar.</div>
        </div>
    </div>

    <script>
        let resultsData = [];

        function toggleCustomPorts() {
            const mode = document.getElementById('portMode').value;
            document.getElementById('customPortsGroup').style.display = mode === 'custom' ? 'block' : 'none';
        }

        function log(msg) {
            const box = document.getElementById('logBox');
            box.innerHTML += `<br>> ${msg}`;
            box.scrollTop = box.scrollHeight;
        }

        async function startScan() {
            const btn = document.getElementById('btnScan');
            btn.disabled = true;
            btn.style.opacity = "0.5";
            
            document.getElementById('resultsBody').innerHTML = '';
            document.getElementById('statOpen').innerText = '0';
            document.getElementById('progressBar').style.width = '0%';
            resultsData = [];

            const payload = {
                target: document.getElementById('target').value,
                mode: document.getElementById('portMode').value,
                customPorts: document.getElementById('customPorts').value,
                threads: parseInt(document.getElementById('threads').value),
                timeout: parseFloat(document.getElementById('timeout').value)
            };

            log(`Iniciando varredura em: ${payload.target}...`);
            const startTime = performance.now();

            try {
                const res = await fetch('/api/scan', {
                    method: 'POST',
                    headers: {'Content-Type': 'application/json'},
                    body: JSON.stringify(payload)
                });
                
                const data = await res.json();
                document.getElementById('statTargets').innerText = data.targets_count;
                document.getElementById('progressBar').style.width = '100%';
                
                resultsData = data.results;
                let openCount = 0;

                if (data.results.length === 0) {
                    document.getElementById('resultsBody').innerHTML = '<tr><td colspan="5" style="text-align:center; color: var(--text-muted);">Nenhuma porta aberta encontrada.</td></tr>';
                } else {
                    data.results.forEach(row => {
                        openCount++;
                        const tr = document.createElement('tr');
                        tr.innerHTML = `
                            <td>${row.ip}</td>
                            <td><strong>${row.port}</strong></td>
                            <td><span class="badge-open">ABERTA</span></td>
                            <td>${row.service}</td>
                            <td style="font-family: monospace; font-size:11px; color:#aaa">${row.banner || '-'}</td>
                        `;
                        document.getElementById('resultsBody').appendChild(tr);
                    });
                }

                document.getElementById('statOpen').innerText = openCount;
                const elapsed = ((performance.now() - startTime) / 1000).toFixed(2);
                document.getElementById('statTime').innerText = `${elapsed}s`;
                log(`Varredura concluída! ${openCount} portas abertas detectadas em ${elapsed}s.`);

            } catch (err) {
                log(`Erro ao executar varredura: ${err.message}`);
            }

            btn.disabled = false;
            btn.style.opacity = "1";
        }

        function exportJSON() {
            if (!resultsData.length) return alert('Nenhum resultado para exportar!');
            const dataStr = "data:text/json;charset=utf-8," + encodeURIComponent(JSON.stringify(resultsData, null, 2));
            const anchor = document.createElement('a');
            anchor.setAttribute("href", dataStr);
            anchor.setAttribute("download", `scan_results_${Date.now()}.json`);
            document.body.appendChild(anchor);
            anchor.click();
            anchor.remove();
        }
    </script>
</body>
</html>
"""

class WebServerHandler(BaseHTTPRequestHandler):
    def log_message(self, format, *args):
        return  # Desabilita logs de requisição no terminal

    def do_GET(self):
        self.send_response(200)
        self.send_header("Content-type", "text/html; charset=utf-8")
        self.end_headers()
        self.wfile.write(HTML_INTERFACE.encode('utf-8'))

    def do_POST(self):
        if self.path == '/api/scan':
            content_length = int(self.headers['Content-Length'])
            body = self.rfile.read(content_length)
            data = json.loads(body)

            targets = ScannerEngine.parse_targets(data['target'])
            
            # Definir lista de portas
            ports = []
            mode = data.get('mode')
            if mode == 'top20':
                ports = TOP_20_PORTS
            elif mode == 'common':
                ports = list(COMMON_PORTS.keys())
            elif mode == 'full':
                ports = list(range(1, 65536))
            elif mode == 'custom':
                try:
                    p_range = data.get('customPorts', '20-100').split('-')
                    ports = list(range(int(p_range[0]), int(p_range[1]) + 1))
                except:
                    ports = TOP_20_PORTS

            threads = data.get('threads', 100)
            timeout = data.get('timeout', 0.8)

            open_results = []

            # Mapeamento paralelo de tarefas (IP x Porta)
            tasks = [(ip, port) for ip in targets for port in ports]

            with concurrent.futures.ThreadPoolExecutor(max_workers=threads) as executor:
                futures = [executor.submit(ScannerEngine.scan_port, ip, port, timeout) for ip, port in tasks]
                for future in concurrent.futures.as_completed(futures):
                    res = future.result()
                    if res and res["status"] == "open":
                        open_results.append(res)

            response = {
                "targets_count": len(targets),
                "total_scanned": len(tasks),
                "results": open_results
            }

            self.send_response(200)
            self.send_header("Content-type", "application/json")
            self.end_headers()
            self.wfile.write(json.dumps(response).encode('utf-8'))

def run_server():
    port = 8585
    server = HTTPServer(('127.0.0.1', port), WebServerHandler)
    url = f"http://127.0.0.1:{port}"
    print(f"\n[+] RED VIPER iniciado com sucesso!")
    print(f"[+] Acesse a interface em: {url}\n")
    webbrowser.open(url)
    server.serve_forever()

if __name__ == "__main__":
    run_server()