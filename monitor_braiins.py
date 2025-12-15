import os
import time
import requests
from datetime import datetime

# ==============================
# Configuration
# ==============================

POOL_NAME = "Braiins Pool"

API_URL = os.getenv("BRAIINS_API_URL")
API_TOKEN = os.getenv("BRAIINS_API_TOKEN")

BOT_TOKEN = os.getenv("BOT_TOKEN")
CHAT_ID = os.getenv("CHAT_ID")

OFFLINE_THRESHOLD = 10 * 60      # 10 minutes
DEAD_THRESHOLD = 24 * 60 * 60    # 24 hours


# ==============================
# Telegram Notification
# ==============================

def send_telegram_message(message):
    url = f"https://api.telegram.org/bot{BOT_TOKEN}/sendMessage"
    payload = {
        "chat_id": CHAT_ID,
        "text": message
    }

    response = requests.post(url, data=payload, timeout=15)
    response.raise_for_status()


# ==============================
# Fetch Workers
# ==============================

def fetch_workers():
    headers = {
        "Pool-Auth-Token": API_TOKEN
    }

    response = requests.get(API_URL, headers=headers, timeout=30)
    response.raise_for_status()
    return response.json()


# ==============================
# Detect Offline Miners
# ==============================

def detect_offline_miners(data):
    workers = data["btc"]["workers"]
    now = int(time.time())

    offline = []
    dead = []

    for worker_name, info in workers.items():
        hash_5m = info.get("hash_rate_5m", 0)
        last_share = info.get("last_share", 0)
        last_seen = now - last_share

        if hash_5m == 0 and last_seen > DEAD_THRESHOLD:
            dead.append(worker_name)

        elif hash_5m == 0 or last_seen > OFFLINE_THRESHOLD:
            offline.append(worker_name)

    return offline, dead


# ==============================
# Main
# ==============================

def main():
    from datetime import datetime, timedelta, timezone
    try:
        data = fetch_workers()
        offline, dead = detect_offline_miners(data)

        if offline:
            message = (
                f"⚠️ [{POOL_NAME}] Offline miners detected\n\n"
                + "\n".join(offline)
                +f"\n\nChecked at {datetime.now(timezone(timedelta(hours=4))).strftime('%d/%m/%Y %H:%M:%S (UTC+4)')}"
            )
            send_telegram_message(message)
            print("Telegram alert sent.")

        else:
            print("All miners online.")

    except Exception as e:
        send_telegram_message(
            f"❌ [{POOL_NAME}] Monitor error:\n{str(e)}"
        )


if __name__ == "__main__":
    main()
