import psutil
import datetime
import subprocess
from collections import deque

# Istorija poslednjih 60 merenja
cpu_istorija = deque(maxlen=60)
ram_istorija = deque(maxlen=60)
mreza_rx_istorija = deque(maxlen=60)
mreza_tx_istorija = deque(maxlen=60)
alerts_log = deque(maxlen=20)

# Za racunanje mreze po sekundi
_prethodna_mreza = None

def uzmi_cpu():
    cpu = psutil.cpu_percent(interval=1)
    cpu_istorija.append(cpu)
    return cpu

def uzmi_ram():
    ram = psutil.virtual_memory()
    ram_istorija.append(ram.percent)
    return {
        "ukupno": round(ram.total / (1024**3), 2),
        "korisceno": round(ram.used / (1024**3), 2),
        "procenat": ram.percent
    }

def uzmi_disk():
    disk = psutil.disk_usage("/")
    return {
        "ukupno": round(disk.total / (1024**3), 2),
        "korisceno": round(disk.used / (1024**3), 2),
        "slobodno": round(disk.free / (1024**3), 2),
        "procenat": disk.percent
    }

def uzmi_disk_io():
    io = psutil.disk_io_counters()
    return {
        "citanje": round(io.read_bytes / (1024**2), 2),
        "pisanje": round(io.write_bytes / (1024**2), 2),
        "citanja_ops": io.read_count,
        "pisanja_ops": io.write_count
    }

def uzmi_mrezu():
    global _prethodna_mreza
    
    mreza = psutil.net_io_counters()
    
    if _prethodna_mreza is None:
        rx_sec = 0
        tx_sec = 0
    else:
        rx_sec = round((mreza.bytes_recv - _prethodna_mreza.bytes_recv) / (1024**2), 2)
        tx_sec = round((mreza.bytes_sent - _prethodna_mreza.bytes_sent) / (1024**2), 2)
    
    _prethodna_mreza = mreza
    
    mreza_rx_istorija.append(max(0, rx_sec))
    mreza_tx_istorija.append(max(0, tx_sec))
    
    return {
        "poslato": round(mreza.bytes_sent / (1024**2), 2),
        "primljeno": round(mreza.bytes_recv / (1024**2), 2),
        "rx_sec": max(0, rx_sec),
        "tx_sec": max(0, tx_sec)
    }

def uzmi_uptime():
    boot = psutil.boot_time()
    uptime = datetime.datetime.now() - datetime.datetime.fromtimestamp(boot)
    sati = int(uptime.total_seconds() // 3600)
    minuti = int((uptime.total_seconds() % 3600) // 60)
    return f"{sati}h {minuti}m"

def uzmi_temperaturu():
    try:
        temps = psutil.sensors_temperatures()
        if "coretemp" in temps:
            return round(temps["coretemp"][0].current, 1)
        elif "cpu_thermal" in temps:
            return round(temps["cpu_thermal"][0].current, 1)
        else:
            return "N/A"
    except:
        return "N/A"

def uzmi_procese():
    procesi = []
    for proc in psutil.process_iter(["pid", "name", "cpu_percent", "memory_percent"]):
        try:
            procesi.append(proc.info)
        except:
            pass
    sortirani = sorted(procesi, key=lambda x: x["cpu_percent"], reverse=True)
    return sortirani[:5]

def uzmi_ssh_konekcije():
    try:
        konekcije = []
        for k in psutil.net_connections():
            if k.laddr.port == 22 and k.status == "ESTABLISHED":
                konekcije.append({
                    "ip": k.raddr.ip if k.raddr else "N/A",
                    "port": k.raddr.port if k.raddr else "N/A",
                    "status": k.status
                })
        return konekcije
    except:
        return []

def uzmi_docker_kontejnere():
    try:
        rezultat = subprocess.run(
            ["docker", "ps", "--format",
             "{{.Names}}|{{.Status}}|{{.Image}}|{{.Ports}}"],
            capture_output=True, text=True, timeout=3
        )
        kontejneri = []
        for linija in rezultat.stdout.strip().split("\n"):
            if linija:
                delovi = linija.split("|")
                if len(delovi) >= 3:
                    kontejneri.append({
                        "ime": delovi[0],
                        "status": delovi[1],
                        "image": delovi[2],
                        "portovi": delovi[3] if len(delovi) > 3 else ""
                    })
        return kontejneri
    except:
        return []

def dodaj_alert(poruka):
    vreme = datetime.datetime.now().strftime("%H:%M:%S")
    alerts_log.appendleft(f"{vreme} — {poruka}")

def uzmi_sve():
    return {
        "cpu": uzmi_cpu(),
        "ram": uzmi_ram(),
        "disk": uzmi_disk(),
        "disk_io": uzmi_disk_io(),
        "mreza": uzmi_mrezu(),
        "uptime": uzmi_uptime(),
        "temperatura": uzmi_temperaturu(),
        "procesi": uzmi_procese(),
        "ssh_konekcije": uzmi_ssh_konekcije(),
        "docker_kontejneri": uzmi_docker_kontejnere(),
        "cpu_istorija": list(cpu_istorija),
        "ram_istorija": list(ram_istorija),
        "mreza_rx_istorija": list(mreza_rx_istorija),
        "mreza_tx_istorija": list(mreza_tx_istorija),
        "alerts_log": list(alerts_log)
    }
