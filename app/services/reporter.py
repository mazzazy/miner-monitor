from pathlib import Path
from datetime import datetime
import pandas as pd

from app.config import Config


class Reporter:

    def __init__(self):

        self.history_file = Path(Config.HISTORY_FILE)

        self.history_file.parent.mkdir(
            parents=True,
            exist_ok=True
        )

    # ----------------------------------
    # Save one snapshot
    # ----------------------------------

    def save_snapshot(self, workers):

        rows = []

        timestamp = datetime.now().strftime("%Y-%m-%d %H:%M:%S")

        for worker in workers:

            rows.append({

                "timestamp": timestamp,

                "worker": worker.name,

                "state": worker.state,

                "hashrate_5m_gh": worker.hash_rate_5m,

                "hashrate_60m_gh": worker.hash_rate_60m,

                "hashrate_24h_gh": worker.hash_rate_24h,

                "hashrate_5m_th": round(worker.hash_rate_th, 2),

                "hashrate_5m_ph": round(worker.hash_rate_ph, 6)

            })

        df = pd.DataFrame(rows)

        if self.history_file.exists():

            df.to_csv(

                self.history_file,

                mode="a",

                header=False,

                index=False

            )

        else:

            df.to_csv(

                self.history_file,

                index=False

            )

    # ----------------------------------
    # Generate Summary
    # ----------------------------------

    def generate_summary(self, workers):

        total_workers = len(workers)

        online = 0
        offline = 0
        low = 0

        total_hashrate = 0

        best_worker = None
        worst_worker = None

        best_hash = -1
        worst_hash = 999999999999

        for worker in workers:

            total_hashrate += worker.hash_rate_ph

            state = worker.state.lower()

            if state == "ok":
                online += 1

            elif state == "off":
                offline += 1

            elif state == "low":
                low += 1

            if worker.hash_rate_5m > best_hash:

                best_hash = worker.hash_rate_5m

                best_worker = worker

            if worker.hash_rate_5m < worst_hash:

                worst_hash = worker.hash_rate_5m

                worst_worker = worker

        report = []

        report.append("📊 DAILY HASHRATE REPORT")
        report.append("")

        report.append(f"Total Workers : {total_workers}")

        report.append(f"Online        : {online}")

        report.append(f"Offline       : {offline}")

        report.append(f"Low Hashrate  : {low}")

        report.append("")

        report.append(f"Total Hashrate : {total_hashrate:.2f} PH/s")

        report.append("")

        if best_worker:

            report.append(

                f"🏆 Best Miner : {best_worker.name} ({best_worker.hash_rate_th:.2f} TH/s)"

            )

        if worst_worker:

            report.append(

                f"📉 Lowest Miner : {worst_worker.name} ({worst_worker.hash_rate_th:.2f} TH/s)"

            )

        report.append("")

        report.append("Top Workers")

        report.append("----------------------------")

        sorted_workers = sorted(

            workers,

            key=lambda x: x.hash_rate_5m,

            reverse=True

        )

        for worker in sorted_workers[:10]:

            report.append(

                f"{worker.name:<18} {worker.hash_rate_th:8.2f} TH/s"

            )

        return "\n".join(report)