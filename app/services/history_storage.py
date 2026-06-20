import csv
import os
from datetime import datetime

from app.config import Config


class HistoryStorage:

    def __init__(self):
        self.file = Config.HISTORY_FILE

    def append_snapshot(self, workers):

        file_exists = os.path.exists(self.file)

        with open(self.file, "a", newline="", encoding="utf-8") as f:

            writer = csv.writer(f)

            if not file_exists:
                writer.writerow([
                    "timestamp",
                    "worker",
                    "state",
                    "hashrate_5m",
                    "hashrate_60m",
                    "hashrate_24h",
                    "last_share"
                ])

            timestamp = datetime.now().isoformat()

            for worker, info in workers.items():

                writer.writerow([
                    timestamp,
                    worker,
                    info.get("state", ""),
                    info.get("hash_rate_5m", 0),
                    info.get("hash_rate_60m", 0),
                    info.get("hash_rate_24h", 0),
                    info.get("last_share", 0)
                ])