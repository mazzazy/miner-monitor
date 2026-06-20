import csv
import os
from datetime import datetime
from app.config import Config


class HistoryStorage:

    def __init__(self):
        os.makedirs("data", exist_ok=True)

    def append_snapshot(self, workers):

        file_exists = os.path.exists(Config.HISTORY_FILE)

        with open(
            Config.HISTORY_FILE,
            "a",
            newline="",
            encoding="utf-8"
        ) as f:

            writer = csv.writer(f)

            if not file_exists:
                writer.writerow([
                    "timestamp",
                    "worker",
                    "state",
                    "hashrate_th",
                    "last_share"
                ])

            timestamp = datetime.now().strftime("%Y-%m-%d %H:%M:%S")

            for name, info in workers.items():

                writer.writerow([
                    timestamp,
                    name,
                    info.get("state"),
                    round(info.get("hash_rate_5m", 0) / 1000, 2),
                    info.get("last_share")
                ])