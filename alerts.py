import smtplib
from email.mime.text import MIMEText
from datetime import datetime
import config
import monitor

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
            poruka = f"CPU visok: {podaci['cpu']}% (prag: {config.CPU_PRAG}%)"
            posalji_email(f"[ALERT] CPU visok na serveru!", f"Vreme: {vreme}\n{poruka}")
            monitor.dodaj_alert(poruka)
            vec_alerirano.add("cpu")
    else:
        vec_alerirano.discard("cpu")

    # RAM alert
    if podaci["ram"]["procenat"] > config.RAM_PRAG:
        if "ram" not in vec_alerirano:
            poruka = f"RAM visok: {podaci['ram']['procenat']}% (prag: {config.RAM_PRAG}%)"
            posalji_email(f"[ALERT] RAM visok na serveru!", f"Vreme: {vreme}\n{poruka}")
