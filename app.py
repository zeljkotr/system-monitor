from flask import Flask, render_template_string
import psutil
from datetime import datetime

app = Flask(__name__)

HTML = '''
<!DOCTYPE html>
<html>
<head>
    <title>System Monitor</title>
    <meta charset="utf-8">
    <meta http-equiv="refresh" content="3">
    <style>
        body { background: #1a1a2e; color: #eee; font-family: monospace; padding: 20px; }
        h1 { color: #00d4ff; text-align: center; }
        .grid { display: grid; grid-template-columns: repeat(2, 1fr); gap: 20px; max-width: 800px; margin: auto; }
        .card { background: #16213e; border: 1px solid #00d4ff33; border-radius: 10px; padding: 20px; }
        .card h2 { color: #00d4ff; margin: 0 0 10px 0; font-size: 14px; text-transform: uppercase; }
        .value { font-size: 36px; font-weight: bold; color: #fff; }
        .sub { font-size: 12px; color: #888; margin-top: 5px; }
        .bar { background: #0f3460; border-radius: 5px; height: 8px; margin-top: 10px; }
        .bar-fill { background: #00d4ff; border-radius: 5px; height: 8px; }
        .warn { color: #ff6b6b !important; }
        .time { text-align: center; color: #888; font-size: 12px; margin-top: 20px; }
    </style>
</head>
<body>
    <h1>⚡ SYSTEM MONITOR</h1>
    <div class="grid">
        <div class="card">
            <h2>🖥️ CPU</h2>
            <div class="value {{ 'warn' if cpu > 80 else '' }}">{{ cpu }}%</div>
            <div class="bar"><div class="bar-fill" style="width: {{ cpu }}%"></div></div>
        </div>
        <div class="card">
            <h2>🧠 RAM</h2>
            <div class="value {{ 'warn' if ram.procenat > 80 else '' }}">{{ ram.procenat }}%</div>
            <div class="sub">{{ ram.korisceno }} / {{ ram.ukupno }} GB</div>
            <div class="bar"><div class="bar-fill" style="width: {{ ram.procenat }}%"></div></div>
        </div>
        <div class="card">
            <h2>💾 DISK</h2>
            <div class="value {{ 'warn' if disk.procenat > 90 else '' }}">{{ disk.procenat }}%</div>
            <div class="sub">{{ disk.korisceno }} / {{ disk.ukupno }} GB | Slobodno: {{ disk.slobodno }} GB</div>
            <div class="bar"><div class="bar-fill" style="width: {{ disk.procenat }}%"></div></div>
        </div>
        <div class="card">
            <h2>🌐 MREŽA</h2>
            <div class="value">{{ mreza.primljeno }} MB</div>
            <div class="sub">Primljeno | Poslato: {{ mreza.poslato }} MB</div>
        </div>
    </div>
    <div class="time">Poslednje osvežavanje: {{ vreme }} | Auto-refresh: 3s</div>
</body>
</html>
'''

@app.route("/")
def dashboard():
    cpu = psutil.cpu_percent(interval=1)
    
    ram_raw = psutil.virtual_memory()
    ram = type("RAM", (), {
        "ukupno": round(ram_raw.total / (1024**3), 2),
        "korisceno": round(ram_raw.used / (1024**3), 2),
        "procenat": ram_raw.percent
    })()
    
    disk_raw = psutil.disk_usage("/")
    disk = type("Disk", (), {
        "ukupno": round(disk_raw.total / (1024**3), 2),
        "korisceno": round(disk_raw.used / (1024**3), 2),
        "slobodno": round(disk_raw.free / (1024**3), 2),
        "procenat": disk_raw.percent
    })()
    
    mreza_raw = psutil.net_io_counters()
    mreza = type("Mreza", (), {
        "poslato": round(mreza_raw.bytes_sent / (1024**2), 2),
        "primljeno": round(mreza_raw.bytes_recv / (1024**2), 2)
    })()
    
    vreme = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
    
    return render_template_string(HTML, cpu=cpu, ram=ram, disk=disk, mreza=mreza, vreme=vreme)

if __name__ == "__main__":
    app.run(host="0.0.0.0", port=5000, debug=False)
