import json
from pathlib import Path
import pandas as pd
from collections import defaultdict
from datetime import datetime


class UptimeDashboardService:

    def __init__(self):

        project_root = Path(__file__).resolve().parents[3]
        self.file = project_root / "data" / "uptime.json"

    def load(self):

        if not self.file.exists():
            return {}

        with open(self.file, "r", encoding="utf-8") as f:
            return json.load(f)

    def _extract_worker_stats(self, data, days):

        cutoff = datetime.now().timestamp() - (days * 86400)

        result = defaultdict(lambda: {"ok": 0, "low": 0, "off": 0})

        for worker, hours in data.items():

            if worker == "_meta":
                continue

            for hour_key, states in hours.items():

                try:
                    hour_ts = datetime.strptime(hour_key, "%Y-%m-%d %H:%M").timestamp()
                except:
                    continue

                if hour_ts < cutoff:
                    continue

                for state, value in states.items():
                    result[worker][state] += value

        return result

    def get_uptime_table(self):

        data = self.load()

        workers = []

        for worker, stats in self._extract_worker_stats(data, 30).items():

            total = sum(stats.values())

            available = stats["ok"] + stats["low"]

            uptime = (available / total * 100) if total else 0

            workers.append({
                "Worker": worker,
                "Uptime %": round(uptime, 2),
                "OK": stats["ok"],
                "Low": stats["low"],
                "Offline": stats["off"]
            })

        return pd.DataFrame(workers).sort_values(
            "Uptime %",
            ascending=False
        )
    
    def get_worker_ranking(self):

        df = self.get_uptime_table()

        if df.empty:
            return df

        df["Uptime %"] = df["Uptime %"].astype(float)

        def score(row):
            return row["Uptime %"] * 0.8 + row["OK"] * 0.2

        df["Score"] = df.apply(score, axis=1)

        df = df.sort_values("Score", ascending=False).reset_index(drop=True)

        df["Rank"] = df.index + 1

        # --------------------------------------------------
        # VISUAL ENHANCEMENT (ICON + TEXT COLOR READY)
        # --------------------------------------------------

        def rank_icon(rank):
            if rank == 1:
                return "🥇"
            elif rank == 2:
                return "🥈"
            elif rank == 3:
                return "🥉"
            return "•"

        def status_color(uptime):
            if uptime >= 99:
                return "🟢"
            elif uptime >= 97:
                return "🟡"
            return "🔴"

        df["Rank"] = df["Rank"].apply(rank_icon)
        df["Health"] = df["Uptime %"].apply(status_color)

        return df