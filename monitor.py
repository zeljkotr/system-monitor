import psutil
import datetime

def uzmi_cpu():
    return psutil.cpu_percent(interval=1)

def uzmi_ram():
    ram = psutil.virtual_memory()
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

def uzmi_mrezu():
    mreza = psutil.net_io_counters()
    return {
        "poslato": round(mreza.bytes_sent / (1024**2), 2),
        "primljeno": round(mreza.bytes_recv / (1024**2), 2)
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
        konekcije = psutil.net_connections()
        ssh = [k for k in konekcije if k.laddr.port == 22 and k.status == "ESTABLISHED"]
        return len(ssh)
    except:
        return 0

def uzmi_sve():
    return {
        "cpu": uzmi_cpu(),
        "ram": uzmi_ram(),
        "disk": uzmi_disk(),
        "mreza": uzmi_mrezu(),
        "uptime": uzmi_uptime(),
        "temperatura": uzmi_temperaturu(),
        "procesi": uzmi_procese(),
        "ssh_konekcije": uzmi_ssh_konekcije()
    }
