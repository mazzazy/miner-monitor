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
    low = []
    dead = []

    for worker_name, info in workers.items():
        state = info.get("state", "").lower()
        hash_5m = info.get("hash_rate_5m", 0) or 0
        hash_24h = info.get("hash_rate_24h", 0) or 0
        last_share = info.get("last_share", 0)

        last_seen = now - last_share

        # DEAD (ignore)
        if hash_5m == 0 and last_seen > DEAD_THRESHOLD:
            dead.append(worker_name)
            continue

        # OFFLINE (alert)
        if hash_5m == 0 or last_seen > OFFLINE_THRESHOLD:
            offline.append(worker_name)
            continue

        # LOW HASHRATE (alert)
        if state == "low":
            low.append(
                f"{worker_name} (state=low)"
            )
            continue

        if hash_24h > 0 and (hash_5m / hash_24h) < LOW_HASHRATE_RATIO:
            low.append(
                f"{worker_name} ({hash_5m:.0f} < {int(LOW_HASHRATE_RATIO*100)}% avg)"
            )

    return offline, low, dead



# ==============================
# Main
# ==============================

def main():
     
    try:
        from datetime import datetime, timedelta, timezone
        data = fetch_workers()
        offline, low, dead = detect_offline_miners(data)

        if offline or low:
            message = f"⚠️ [{POOL_NAME}] Miner issues detected\n\n"

            if offline:
                message += "🚨 OFFLINE:\n" + "\n".join(offline) + "\n\n"

            if low:
                message += "⚠️ LOW HASHRATE:\n" + "\n".join(low) + "\n\n"

            message += f"Checked at: {datetime.now(timezone(timedelta(hours=4))).strftime('%d/%m/%Y %H:%M:%S (UTC+4)')}"

            send_telegram_message(message)
            print("Telegram alert sent.")
        else:
            print("All miners operating normally.")

    except Exception as e:
        error_message = (
            f"❌ [{POOL_NAME}] Monitor error\n\n"
            f"{str(e)}\n\n"
            f"Checked at: {datetime.now(timezone(timedelta(hours=4))).strftime('%d/%m/%Y %H:%M:%S (UTC+4)')}"
        )
        send_telegram_message(error_message)
        print("Error alert sent.")

