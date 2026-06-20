import os
import time
import requests
from datetime import datetime
from app.services.history import save_snapshot
import json
from pathlib import Path

# ==============================
# Configuration
# ==============================

STATE_FILE = Path("last_state.json")
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


def load_state():
    if STATE_FILE.exists():
        with open(STATE_FILE, "r") as f:
            return json.load(f)
    return {}

def save_state(state):
    with open(STATE_FILE, "w") as f:
        json.dump(state, f, indent=2)

def get_worker_state(info):
    state = info.get("state", "").lower()
    last_share = int(info.get("last_share", 0))
    hash_5m = float(info.get("hash_rate_5m", 0) or 0)

    now = int(time.time())
    last_seen = now - last_share

    if state == "off" or hash_5m == 0:
        return "off"

    if state == "low":
        return "low"

    return "ok"

# ==============================
# Main
# ==============================

def main():
    try:
        print("DEBUG: script started")

        data = fetch_workers()
        workers = data.get("btc", {}).get("workers", {})

        previous_state = load_state()
        current_state = {}

        changes = []

        for name, info in workers.items():
            new_state = get_worker_state(info)
            current_state[name] = new_state

            old_state = previous_state.get(name)

            # Trigger alert ONLY on change
            if old_state != new_state:
                changes.append((name, old_state, new_state))

        if changes:
            message = f"⚠️ [{POOL_NAME}] State Change Detected\n\n"

            for name, old, new in changes:
                message += f"{name}: {old} → {new}\n"

            message += f"\nChecked at: {datetime.now()}"

            send_telegram_message(message)
            print("Telegram alert sent.")
        else:
            print("No state changes.")

        # Save snapshot for next run
        save_state(current_state)

    except Exception as e:
        error_message = f"❌ Monitor error:\n{str(e)}"
        send_telegram_message(error_message)
        print("Error alert sent.")

if __name__ == "__main__":
    print("DEBUG: script started")
    main()

