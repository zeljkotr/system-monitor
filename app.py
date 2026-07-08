from flask import Flask, render_template_string
from datetime import datetime
import monitor
import alerts
import config

app = Flask(__name__)

HTML = '''
<!DOCTYPE html>
<html>
<head>
    <title>System Monitor</title>
    <meta charset="utf-8">
    <meta http-equiv="refresh" content="3">
    <script src="https://cdnjs.cloudflare.com/ajax/libs/Chart.js/4.4.0/chart.umd.min.js"></script>
    <style>
        * { box-sizing: border-box; margin: 0; padding: 0; }
        body { background: #0d1117; color: #eee; font-family: monospace; padding: 20px; }
        h1 { color: #00d4ff; text-align: center; margin-bottom: 5px; font-size: 24px; }
        .subtitle { text-align: center; color: #888; font-size: 12px; margin-bottom: 20px; }
        .grid { display: grid; grid-template-columns: repeat(2, 1fr); gap: 15px; max-width: 1100px; margin: auto; }
        .card { background: #161b22; border: 1px solid #30363d; border-radius: 10px; padding: 20px; }
        .card h2 { color: #00d4ff; margin: 0 0 10px 0; font-size: 13px; text-transform: uppercase; letter-spacing: 1px; }
        .value { font-size: 32px; font-weight: bold; color: #fff; }
        .sub { font-size: 12px; color: #888; margin-top: 5px; }
        .bar { background: #21262d; border-radius: 5px; height: 8px; margin-top: 10px; }
        .bar-fill { border-radius: 5px; height: 8px; transition: width 0.3s; }
        .ok { background: #00d4ff; }
        .warn { background: #ff6b6b; }
        .value-warn { color: #ff6b6b !important; }
        .full { grid-column: span 2; }
        table { width: 100%; border-collapse: collapse; font-size: 12px; }
        th { color: #00d4ff; text-align: left; padding: 6px; border-bottom: 1px solid #30363d; }
        td { padding: 6px; border-bottom: 1px solid #21262d; }
        .alert-item { padding: 6px 10px; margin: 4px 0; background: #ff6b6b22; border-left: 3px solid #ff6b6b; border-radius: 3px; font-size: 12px; }
        .no-alerts { color: #888; font-size: 12px; }
        .io-grid { display: grid; grid-template-columns: repeat(2, 1fr); gap: 10px; margin-top: 10px; }
        .io-item { background: #21262d; padding: 10px; border-radius: 5px; text-align: center; }
        .io-value { font-size: 18px; font-weight: bold; color: #00d4ff; }
        .io-label { font-size: 11px; color: #888; margin-top: 3px; }
        .badge { display: inline-block; padding: 2px 8px; border-radius: 10px; font-size: 11px; }
        .badge-green { background: #00ff8822; color: #00ff88; border: 1px solid #00ff8844; }
        .badge-red { background: #ff6b6b22; color: #ff6b6b; border: 1px solid #ff6b6b44; }
        .time { text-align: center; color: #888; font-size: 11px; margin: 15px auto 0; max-width: 1100px; }
    </style>
</head>
<body>
    <h1>⚡ SYSTEM MONITOR</h1>
    <div style="text-align:center; color:#00d4ff44; font-size:11px; margin-bottom:5px;">
    Autor: Zeljko Tripcevski | IT Team Lead @ MTC Nissal
    </div>
    <div class="subtitle">
        🕐 Uptime: {{ uptime }} &nbsp;|&nbsp;
        🌡️ Temp: {{ temperatura }}°C &nbsp;|&nbsp;
        🔐 SSH: {{ ssh_konekcije|length }} aktivnih konekcija
    </div>

    <div class="grid">
        <!-- CPU -->
        <div class="card">
            <h2>🖥️ CPU</h2>
            <div class="value {{ 'value-warn' if cpu > config.CPU_PRAG else '' }}">{{ cpu }}%</div>
            <div class="bar">
                <div class="bar-fill {{ 'warn' if cpu > config.CPU_PRAG else 'ok' }}" style="width: {{ cpu }}%"></div>
            </div>
            <canvas id="cpuChart" height="80" style="margin-top:15px"></canvas>
        </div>

        <!-- RAM -->
        <div class="card">
            <h2>🧠 RAM</h2>
            <div class="value {{ 'value-warn' if ram.procenat > config.RAM_PRAG else '' }}">{{ ram.procenat }}%</div>
            <div class="sub">{{ ram.korisceno }} / {{ ram.ukupno }} GB</div>
            <div class="bar">
                <div class="bar-fill {{ 'warn' if ram.procenat > config.RAM_PRAG else 'ok' }}" style="width: {{ ram.procenat }}%"></div>
            </div>
            <canvas id="ramChart" height="80" style="margin-top:15px"></canvas>
        </div>

        <!-- DISK -->
        <div class="card">
            <h2>💾 DISK</h2>
            <div class="value {{ 'value-warn' if disk.procenat > config.DISK_PRAG else '' }}">{{ disk.procenat }}%</div>
            <div class="sub">{{ disk.korisceno }} / {{ disk.ukupno }} GB | Slobodno: {{ disk.slobodno }} GB</div>
            <div class="bar">
                <div class="bar-fill {{ 'warn' if disk.procenat > config.DISK_PRAG else 'ok' }}" style="width: {{ disk.procenat }}%"></div>
            </div>
            <div class="io-grid">
                <div class="io-item">
                    <div class="io-value">{{ disk_io.citanje }} MB</div>
                    <div class="io-label">Procitano</div>
                </div>
                <div class="io-item">
                    <div class="io-value">{{ disk_io.pisanje }} MB</div>
                    <div class="io-label">Zapisano</div>
                </div>
            </div>
        </div>

        <!-- MREZA -->
        <div class="card">
            <h2>🌐 MREZA</h2>
            <div class="value">{{ mreza.rx_sec }} MB/s</div>
            <div class="sub">⬇ Primanje | ⬆ Slanje: {{ mreza.tx_sec }} MB/s</div>
            <canvas id="mrezaChart" height="80" style="margin-top:15px"></canvas>
            <div class="io-grid" style="margin-top:10px">
                <div class="io-item">
                    <div class="io-value" style="color:#00ff88">{{ mreza.primljeno }} MB</div>
                    <div class="io-label">⬇ Ukupno primljeno</div>
                </div>
                <div class="io-item">
                    <div class="io-value" style="color:#ff9500">{{ mreza.poslato }} MB</div>
                    <div class="io-label">⬆ Ukupno poslato</div>
                </div>
            </div>
        </div>

        <!-- PROCESI -->
        <div class="card full">
            <h2>🔥 Top 5 Procesa po CPU</h2>
            <table>
                <tr>
                    <th>PID</th><th>Naziv</th><th>CPU %</th><th>RAM %</th>
                </tr>
                {% for p in procesi %}
                <tr>
                    <td>{{ p.pid }}</td>
                    <td>{{ p.name }}</td>
                    <td>{{ "%.1f"|format(p.cpu_percent) }}%</td>
                    <td>{{ "%.1f"|format(p.memory_percent) }}%</td>
                </tr>
                {% endfor %}
            </table>
        </div>

        <!-- DOCKER -->
        <div class="card full">
            <h2>🐳 Docker Kontejneri</h2>
            {% if docker_kontejneri %}
            <table>
                <tr>
                    <th>Ime</th><th>Status</th><th>Image</th><th>Portovi</th>
                </tr>
                {% for k in docker_kontejneri %}
                <tr>
                    <td>{{ k.ime }}</td>
                    <td>
                        <span class="badge {{ 'badge-green' if 'Up' in k.status else 'badge-red' }}">
                            {{ k.status }}
                        </span>
                    </td>
                    <td>{{ k.image }}</td>
                    <td>{{ k.portovi }}</td>
                </tr>
                {% endfor %}
            {% else %}
                <div class="no-alerts">Nema aktivnih Docker kontejnera</div>
            {% endif %}
            </table>
        </div>

        <!-- SSH -->
        <div class="card full">
            <h2>🔐 Aktivne SSH Konekcije</h2>
            {% if ssh_konekcije %}
            <table>
                <tr>
                    <th>IP Adresa</th><th>Port</th><th>Status</th>
                </tr>
                {% for k in ssh_konekcije %}
                <tr>
                    <td>{{ k.ip }}</td>
                    <td>{{ k.port }}</td>
                    <td><span class="badge badge-green">{{ k.status }}</span></td>
                </tr>
                {% endfor %}
            {% else %}
                <div class="no-alerts">Nema aktivnih SSH konekcija</div>
            {% endif %}
            </table>
        </div>

        <!-- ALERTS -->
        <div class="card full">
            <h2>🚨 Alerts Log</h2>
            {% if alerts_log %}
                {% for alert in alerts_log %}
                    <div class="alert-item">{{ alert }}</div>
                {% endfor %}
            {% else %}
                <div class="no-alerts">✅ Nema aktivnih upozorenja</div>
            {% endif %}
        </div>
    </div>

    <div class="time">
        Poslednje osvezavanje: {{ vreme }} | Auto-refresh: {{ config.REFRESH_INTERVAL }}s
    </div>

    <script>
        const cpuData = {{ cpu_istorija | tojson }};
        const ramData = {{ ram_istorija | tojson }};
        const mrezaRx = {{ mreza_rx_istorija | tojson }};
        const mrezaTx = {{ mreza_tx_istorija | tojson }};
        const labels = cpuData.map((_, i) => i + 's');

        function napraviGrafikon(id, data1, boja1, data2, boja2, label1, label2) {
            const datasets = [{
                label: label1,
                data: data1,
                borderColor: boja1,
                backgroundColor: boja1 + '22',
                fill: true,
                tension: 0.3,
                pointRadius: 0,
                borderWidth: 2
            }];

            if (data2) {
                datasets.push({
                    label: label2,
                    data: data2,
                    borderColor: boja2,
                    backgroundColor: boja2 + '22',
                    fill: true,
                    tension: 0.3,
                    pointRadius: 0,
                    borderWidth: 2
                });
            }

            new Chart(document.getElementById(id), {
                type: 'line',
                data: { labels: labels, datasets: datasets },
                options: {
                    plugins: { legend: { display: !!data2, labels: { color: '#888', font: { size: 10 } } } },
                    scales: {
                        y: { min: 0, ticks: { color: '#888', font: { size: 10 } }, grid: { color: '#21262d' } },
                        x: { display: false }
                    }
                }
            });
        }

        napraviGrafikon('cpuChart', cpuData, '#00d4ff', null, null, 'CPU', null);
        napraviGrafikon('ramChart', ramData, '#00ff88', null, null, 'RAM', null);
        napraviGrafikon('mrezaChart', mrezaRx, '#00ff88', mrezaTx, '#ff9500', '⬇ RX', '⬆ TX');
    </script>
</body>
</html>
'''

@app.route("/")
def dashboard():
    podaci = monitor.uzmi_sve()
    alerts.proveri_alertove(podaci)

    ram = type("RAM", (), podaci["ram"])()
    disk = type("Disk", (), podaci["disk"])()
    disk_io = type("DiskIO", (), podaci["disk_io"])()
    mreza = type("Mreza", (), podaci["mreza"])()

    return render_template_string(
        HTML,
        cpu=podaci["cpu"],
        ram=ram,
        disk=disk,
        disk_io=disk_io,
        mreza=mreza,
        uptime=podaci["uptime"],
        temperatura=podaci["temperatura"],
        ssh_konekcije=podaci["ssh_konekcije"],
        docker_kontejneri=podaci["docker_kontejneri"],
        procesi=podaci["procesi"],
        cpu_istorija=podaci["cpu_istorija"],
        ram_istorija=podaci["ram_istorija"],
        mreza_rx_istorija=podaci["mreza_rx_istorija"],
        mreza_tx_istorija=podaci["mreza_tx_istorija"],
        alerts_log=podaci["alerts_log"],
        vreme=datetime.now().strftime("%Y-%m-%d %H:%M:%S"),
        config=config
    )

if __name__ == "__main__":
    app.run(host="0.0.0.0", port=config.PORT, debug=False)
