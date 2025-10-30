import os
import requests
import smtplib
import ssl
from email.message import EmailMessage
from datetime import datetime
from dotenv import load_dotenv
from pathlib import Path

# Load environment variables from .env
env_path = Path(__file__).parent / ".env"
if env_path.exists():
    load_dotenv(env_path)

# === Configuration ===
API_URL = os.getenv("API_URL", "")
EMAIL_SENDER = os.getenv("EMAIL_SENDER", "")
EMAIL_RECEIVER = os.getenv("EMAIL_RECEIVER", "")
SMTP_HOST = os.getenv("SMTP_HOST", "smtp.gmail.com")
SMTP_PORT = int(os.getenv("SMTP_PORT", "587"))
SMTP_USER = os.getenv("SMTP_USER", EMAIL_SENDER)
SMTP_PASS = os.getenv("SMTP_PASS", "")

def fetch_workers():
    response = requests.get(API_URL, timeout=15)
    response.raise_for_status()
    return response.json()

def find_offline_workers(data):
    workers = data.get("workers", {})
    offline = []

    for name, info in workers.items():
        status = info.get("status", "").upper()
        hashrate = str(info.get("hashrate", ""))
        avg_diff = str(info.get("hashRateAvgDiff", ""))
        online = info.get("online", True)

        # Condition 1: explicitly offline
        if not online:
            offline.append(f"{name} (offline)")
            continue

        # Condition 2: status is DEAD
        if status == "DEAD":
            offline.append(f"{name} (status=DEAD)")
            continue

        # Condition 3: zero hashrate or avg diff
        if hashrate == "0" or avg_diff == "0":
            offline.append(f"{name} (zero hashrate)")
            continue

    return offline


def send_email(subject, body):
    msg = EmailMessage()
    msg["From"] = EMAIL_SENDER
    msg["To"] = EMAIL_RECEIVER
    msg["Subject"] = subject
    msg.set_content(body)

    context = ssl.create_default_context()
    with smtplib.SMTP(SMTP_HOST, SMTP_PORT) as smtp:
        smtp.starttls(context=context)
        smtp.login(SMTP_USER, SMTP_PASS)
        smtp.send_message(msg)

# -----------------------------
# 🔔 Telegram Notification Setup
# -----------------------------
import requests

BOT_TOKEN = "8317223306:AAElNK873qmWkEXmUmQIASmLt2aTUgmG-aw"  # ← Replace with your BotFather token
CHAT_ID = "589954993"  # ← Replace with your chat ID (from @userinfobot)

def send_telegram_message(message):
    """
    Sends a message to your Telegram chat or group using the Bot API.
    """
    url = f"https://api.telegram.org/bot{BOT_TOKEN}/sendMessage"
    payload = {
        "chat_id": CHAT_ID,
        "text": message,
        "parse_mode": "HTML"
    }

    try:
        response = requests.post(url, data=payload)
        if response.status_code == 200:
            print("✅ Telegram message sent successfully.")
        else:
            print(f"⚠️ Telegram message failed: {response.status_code} - {response.text}")
    except Exception as e:
        print("❌ Telegram send error:", e)


def main():
    from datetime import datetime, timedelta, timezone
    try:
        
        data = fetch_workers()
        offline = find_offline_workers(data)
        if offline:
            subject = f"[ALERT] Offline miners detected ({len(offline)})"
            body = (
                f"The following miners are offline:\n"
                + "\n".join(offline)
                # + f"\n\nChecked at {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}"
                +f"\n\nChecked at {datetime.now(timezone(timedelta(hours=4))).strftime('%d/%m/%Y %H:%M:%S (UTC+4)')}"

            )

            # Send both Email and Telegram alerts
            # send_email(subject, body)
            # print("📧 Alert email sent.")

            send_telegram_message(body)
            print("📱 Telegram alert sent.")
        else:
            print("✅ All miners online.")
    except Exception as e:
        print(f"❌ Error: {e}")


if __name__ == "__main__":
    main()
