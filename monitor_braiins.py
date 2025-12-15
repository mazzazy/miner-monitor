import os
import time
import requests
from datetime import datetime

# ==============================
# Configuration
# ==============================

POOL_NAME = "Braiins Pool"

API_URL = "https://pool.braiins.com/accounts/workers/json/btc"
API_TOKEN = "EpkK4c1HNnTCjsKo"

BOT_TOKEN = "8317223306:AAElNK873qmWkEXmUmQIASmLt2aTUgmG-aw"
CHAT_ID = "589954993"



OFFLINE_THRESHOLD = 600      # 10 minutes
DEAD_THRESHOLD = 3600        # 1 hour
LOW_HASHRATE_RATIO = 0.5


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




def detect_problem_workers(data):
    workers = data.get("btc", {}).get("workers", {})
    print(f"DEBUG: found {len(workers)} workers")

    offline = []
    low = []

    for name, info in workers.items():
        state = info.get("state", "").lower()

        if state == "off":
            offline.append(name)
        elif state == "low":
            low.append(name)

    print(f"DEBUG offline={len(offline)}, low={len(low)}")
    return offline, low




# ==============================
# Main
# ==============================

def main():
     
    try:
        from datetime import datetime, timedelta, timezone
        data = fetch_workers()
        offline, low = detect_problem_workers(data)

        print(f"DEBUG offline={len(offline)}, low={len(low)}")
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

if __name__ == "__main__":
    print("DEBUG: script started")
    main()

