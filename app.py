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
    <style>
        body { background: #1a1a2e; color: #eee; font-family: monospace; padding: 20px; margin: 0; }
        h1 { color: #00d4ff; text-align: center; margin-bottom: 5px; }
        .subtitle { text-align: center; color: #888; font-size: 12px; margin-bottom: 20px; }
        .grid { display: grid; grid-template-columns: repeat(2, 1fr); gap: 15px; max-width: 900px; margin: auto; }
        .card { background: #16213e; border: 1px solid #00d4ff33; border-radius: 10px; padding: 20px; }
        .card h2 { color: #00d4ff; margin: 0 0 10px 0; font-size: 13px; text-transform: uppercase; }
        .value { font-size: 32px; font-weight: bold; color: #fff; }
        .sub { font-size: 12px; color: #888; margin-top: 5px; }
        .bar { background: #0f3460; border-radius: 5px; height: 8px; margin-top: 10px; }
        .bar-fill { border-radius: 5px; height: 8px; }
        .ok { background: #00d4ff; }
        .warn { background: #ff6b6b; }
        .value-warn { color: #ff6b6b !important; }
        .full { grid-column: span 2; }
        table { width: 100%; border-collapse: collapse; font-size: 12px; }
        th { color: #00d4ff; text-align: left; padding: 5px; border-bottom: 1px solid #00d4ff33; }
        td { padding: 5px; border-bottom: 1px solid #ffffff11; }
        .time { text-align: center; color: #888; font-size: 11px; margin-top: 15px; }
    </style>
</head>
<body>
    <h1>⚡ SYSTEM MONITOR</h1>
    <div class="subtitle">{{ uptime }} uptime | {{ ssh }} SSH konekcija | Temp: {{ temperatura }}°C</div>

    <div class="grid">
        <div class="card">
            <h2>🖥️ CPU</h2>
            <div class="value {{ 'value-warn' if cpu > config.CPU_PRAG else '' }}">{{ cpu }}%</div>
            <div class="bar">
                <div class="bar-fill {{ 'warn' if cpu > config.CPU_PRAG else 'ok' }}" style="width: {{ cpu }}%"></div>
            </div>
        </div>

        <div class="card">
            <h2>🧠 RAM</h2>
            <div class="value {{ 'value-warn' if ram.procenat > config.RAM_PRAG else '' }}">{{ ram.procenat }}%</div>
            <div class="sub">{{ ram.korisceno }} / {{ ram.ukupno }} GB</div>
            <div class="bar">
                <div class="bar-fill {{ 'warn' if ram.procenat > config.RAM_PRAG else 'ok' }}" style="width: {{ ram.procenat }}%"></div>
            </div>
        </div>

        <div class="card">
            <h2>💾 DISK</h2>
            <div class="value {{ 'value-warn' if disk.procenat > config.DISK_PRAG else '' }}">{{ disk.procenat }}%</div>
            <div class="sub">{{ disk.korisceno }} / {{ disk.ukupno }} GB | Slobodno: {{ disk.slobodno }} GB</div>
            <div class="bar">
                <div class="bar-fill {{ 'warn' if disk.procenat > config.DISK_PRAG else 'ok' }}" style="width: {{ disk.procenat }}%"></div>
            </div>
        </div>

        <div class="card">
            <h2>🌐 MREŽA</h2>
            <div class="value">{{ mreza.primljeno }} MB</div>
            <div class="sub">Primljeno | Poslato: {{ mreza.poslato }} MB</div>
        </div>

        <div class="card full">
            <h2>🔥 Top 5 Procesa po CPU</h2>
            <table>
                <tr>
                    <th>PID</th>
                    <th>Naziv</th>
                    <th>CPU %</th>
                    <th>RAM %</th>
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
    </div>

    <div class="time">
        Poslednje osvežavanje: {{ vreme }} | Auto-refresh: {{ config.REFRESH_INTERVAL }}s
    </div>
</body>
</html>
'''

@app.route("/")
def dashboard():
    podaci = monitor.uzmi_sve()
    alerts.proveri_alertove(podaci)

    ram = type("RAM", (), podaci["ram"])()
    disk = type("Disk", (), podaci["disk"])()
    mreza = type("Mreza", (), podaci["mreza"])()

    return render_template_string(
        HTML,
        cpu=podaci["cpu"],
        ram=ram,
        disk=disk,
        mreza=mreza,
        uptime=podaci["uptime"],
        temperatura=podaci["temperatura"],
        ssh=podaci["ssh_konekcije"],
        procesi=podaci["procesi"],
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
