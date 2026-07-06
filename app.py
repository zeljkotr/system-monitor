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
        .grid { display: grid; grid-template-columns: repeat(2, 1fr); gap: 15px; max-width: 1000px; margin: auto; }
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
        .io-value { font-size: 20px; font-weight: bold; color: #00d4ff; }
        .io-label { font-size: 11px; color: #888; margin-top: 3px; }
        .time { text-align: center; color: #888; font-size: 11px; margin-top: 15px; max-width: 1000px; margin: 15px auto 0; }
    </style>
</head>
<body>
    <h1>⚡ SYSTEM MONITOR</h1>
    <div class="subtitle">
        🕐 Uptime: {{ uptime }} &nbsp;|&nbsp; 
        🌡️ Temp: {{ temperatura }}°C &nbsp;|&nbsp; 
        🔐 SSH: {{ ssh }} konekcija
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
                    <div class="io-label">Ukupno pročitano</div>
                </div>
                <div class="io-item">
                    <div class="io-value">{{ disk_io.pisanje }} MB</div>
                    <div class="io-label">Ukupno zapisano</div>
                </div>
                <div class="io-item">
                    <div class="io-value">{{ disk_io.citanja_ops }}</div>
                    <div class="io-label">Read operacije</div>
                </div>
                <div class="io-item">
                    <div class="io-value">{{ disk_io.pisanja_ops }}</div>
                    <div class="io-label">Write operacije</div>
                </div>
            </div>
        </div>

        <!-- MREZA -->
        <div class="card">
            <h2>🌐 MREŽA</h2>
            <div class="value">{{ mreza.primljeno }} MB</div>
            <div class="sub">Primljeno | Poslato: {{ mreza.poslato }} MB</div>
            <div class="io-grid" style="margin-top:15px">
                <div class="io-item">
                    <div class="io-value" style="color:#00ff88">{{ mreza.primljeno }} MB</div>
                    <div class="io-label">⬇ Primljeno</div>
                </div>
                <div class="io-item">
                    <div class="io-value" style="color:#ff9500">{{ mreza.poslato }} MB</div>
                    <div class="io-label">⬆ Poslato</div>
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

        <!-- ALERTS LOG -->
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
        Poslednje osvežavanje: {{ vreme }} | Auto-refresh: {{ config.REFRESH_INTERVAL }}s
    </div>

    <script>
        const cpuData = {{ cpu_istorija | tojson }};
        const ramData = {{ ram_istorija | tojson }};
        const labels = cpuData.map((_, i) => i + 's');

        new Chart(document.getElementById('cpuChart'), {
            type: 'line',
            data: {
                labels: labels,
                datasets: [{
                    data: cpuData,
                    borderColor: '#00d4ff',
                    backgroundColor: '#00d4ff22',
                    fill: true,
                    tension: 0.3,
                    pointRadius: 0,
                    borderWidth: 2
                }]
            },
            options: {
                plugins: { legend: { display: false } },
                scales: {
                    y: { min: 0, max: 100, ticks: { color: '#888', font: { size: 10 } }, grid: { color: '#21262d' } },
                    x: { display: false }
                }
            }
        });

        new Chart(document.getElementById('ramChart'), {
            type: 'line',
            data: {
                labels: labels,
                datasets: [{
                    data: ramData,
                    borderColor: '#00ff88',
                    backgroundColor: '#00ff8822',
                    fill: true,
                    tension: 0.3,
                    pointRadius: 0,
                    borderWidth: 2
                }]
            },
            options: {
                plugins: { legend: { display: false } },
                scales: {
                    y: { min: 0, max: 100, ticks: { color: '#888', font: { size: 10 } }, grid: { color: '#21262d' } },
                    x: { display: false }
                }
            }
        });
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
        ssh=podaci["ssh_konekcije"],
        procesi=podaci["procesi"],
        cpu_istorija=podaci["cpu_istorija"],
        ram_istorija=podaci["ram_istorija"],
        alerts_log=podaci["alerts_log"],
        vreme=datetime.now().strftime("%Y-%m-%d %H:%M:%S"),
        config=config
    )

if __name__ == "__main__":
    import threading
    import webbrowser

    def otvori_browser():
        import time
        time.sleep(1.5)
        webbrowser.open("http://localhost:5000")

    threading.Thread(target=otvori_browser).start()
    app.run(host="0.0.0.0", port=config.PORT, debug=False)
