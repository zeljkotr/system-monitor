import smtplib
from email.mime.text import MIMEText
from datetime import datetime
import config

# Pamti sta je vec alerirano da ne spamuje
vec_alerirano = set()

def posalji_email(naslov, poruka):
    try:
        msg = MIMEText(poruka)
        msg["Subject"] = naslov
        msg["From"] = config.EMAIL_POSILJALAC
        msg["To"] = config.EMAIL_PRIMALAC

        smtp = smtplib.SMTP(config.SMTP_SERVER, config.SMTP_PORT)
        smtp.starttls()
        smtp.login(config.EMAIL_POSILJALAC, config.EMAIL_LOZINKA)
        smtp.send_message(msg)
        smtp.quit()
        print(f"Alert poslat: {naslov}")
    except Exception as e:
        print(f"Greska pri slanju emaila: {e}")

def proveri_alertove(podaci):
    vreme = datetime.now().strftime("%Y-%m-%d %H:%M:%S")

    # CPU alert
    if podaci["cpu"] > config.CPU_PRAG:
        if "cpu" not in vec_alerirano:
            posalji_email(
                f"[ALERT] CPU visok na serveru!",
                f"Vreme: {vreme}\nCPU: {podaci['cpu']}%\nPrag: {config.CPU_PRAG}%"
            )
            vec_alerirano.add("cpu")
    else:
        vec_alerirano.discard("cpu")

    # RAM alert
    if podaci["ram"]["procenat"] > config.RAM_PRAG:
        if "ram" not in vec_alerirano:
            posalji_email(
                f"[ALERT] RAM visok na serveru!",
                f"Vreme: {vreme}\nRAM: {podaci['ram']['procenat']}%\nPrag: {config.RAM_PRAG}%"
            )
            vec_alerirano.add("ram")
    else:
        vec_alerirano.discard("ram")

    # Disk alert
    if podaci["disk"]["procenat"] > config.DISK_PRAG:
        if "disk" not in vec_alerirano:
            posalji_email(
                f"[ALERT] Disk skoro pun na serveru!",
                f"Vreme: {vreme}\nDisk: {podaci['disk']['procenat']}%\nPrag: {config.DISK_PRAG}%"
            )
            vec_alerirano.add("disk")
    else:
        vec_alerirano.discard("disk")
