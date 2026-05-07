import smtplib
import os
import logging
import time
from email.mime.multipart import MIMEMultipart
from email.mime.text import MIMEText
from pathlib import Path
from datetime import datetime
from dotenv import load_dotenv

load_dotenv()

BASE_DIR = Path(__file__).parent.parent
HTML_FILE = BASE_DIR / ".tmp" / "newsletter.html"
LOG_FILE = BASE_DIR / "logs" / "nyhedsbrev.log"
LOG_FILE.parent.mkdir(exist_ok=True)

logging.basicConfig(
    filename=LOG_FILE,
    level=logging.INFO,
    format="%(asctime)s %(levelname)s %(message)s",
)

GMAIL_USER = os.getenv("GMAIL_USER")
GMAIL_APP_PASSWORD = os.getenv("GMAIL_APP_PASSWORD")
NEWSLETTER_TO = os.getenv("NEWSLETTER_TO", "thoresbensenmagnusesbensen@gmail.com")


def send():
    if not HTML_FILE.exists():
        raise FileNotFoundError(f"Mangler {HTML_FILE} — kør generate_newsletter.py først")

    html = HTML_FILE.read_text(encoding='utf-8')
    dato = datetime.now().strftime('%d-%m-%Y')

    msg = MIMEMultipart('alternative')
    msg['Subject'] = f'Nyhedsbrev · {dato}'
    msg['From'] = GMAIL_USER
    msg['To'] = NEWSLETTER_TO
    msg.attach(MIMEText(html, 'html', 'utf-8'))

    with smtplib.SMTP_SSL('smtp.gmail.com', 465) as server:
        server.login(GMAIL_USER, GMAIL_APP_PASSWORD)
        server.sendmail(GMAIL_USER, NEWSLETTER_TO, msg.as_string())


def main():
    if not GMAIL_USER or not GMAIL_APP_PASSWORD:
        raise EnvironmentError("GMAIL_USER eller GMAIL_APP_PASSWORD mangler i .env")

    for attempt in range(1, 3):
        try:
            send()
            logging.info(f"Sendt til {NEWSLETTER_TO}")
            print(f"OK: Sendt til {NEWSLETTER_TO}")
            return
        except Exception as e:
            logging.warning(f"Forsøg {attempt} fejlede: {e}")
            if attempt < 2:
                print(f"  Forsøg {attempt} fejlede — prøver igen om 60s...")
                time.sleep(60)
            else:
                logging.error(f"Afsendelse mislykkedes efter 2 forsøg: {e}")
                raise


if __name__ == '__main__':
    main()
