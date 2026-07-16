import json
from pathlib import Path
from collections import defaultdict
from datetime import datetime, timedelta


class UptimeChartService:

    def __init__(self):

        project_root = Path(__file__).resolve().parents[3]
        self.file = project_root / "data" / "uptime.json"

    def load(self):

        if not self.file.exists():
            return {}

        with open(self.file, "r", encoding="utf-8") as f:
            return json.load(f)

    def get_farm_trend(self, days=7):

        data = self.load()

        cutoff = datetime.now() - timedelta(days=days)

        trend = defaultdict(int)

        for worker, hours in data.items():

            if worker == "_meta":
                continue

            for hour_key, states in hours.items():

                try:
                    ts = datetime.strptime(hour_key, "%Y-%m-%d %H:%M")
                except:
                    continue

                if ts < cutoff:
                    continue

                trend[ts.strftime("%Y-%m-%d %H:00")] += states.get("ok", 0)

        sorted_trend = sorted(trend.items())

        return [
            {"time": t, "healthy_workers": v}
            for t, v in sorted_trend
        ]

    def get_worker_comparison(self, days=7):

        data = self.load()

        cutoff = datetime.now() - timedelta(days=days)

        result = defaultdict(lambda: 0)

        for worker, hours in data.items():

            if worker == "_meta":
                continue

            total_ok = 0
            total = 0

            for hour_key, states in hours.items():

                try:
                    ts = datetime.strptime(hour_key, "%Y-%m-%d %H:%M")
                except:
                    continue

                if ts < cutoff:
                    continue

                total_ok += states.get("ok", 0)
                total += sum(states.values())

            uptime = (total_ok / total * 100) if total else 0

            result[worker] = round(uptime, 2)

        return [
            {"worker": k, "uptime": v}
            for k, v in result.items()
        ]

    def get_state_distribution(self):

        data = self.load()

        ok = low = off = 0

        for worker, hours in data.items():

            if worker == "_meta":
                continue

            for hour_key, states in hours.items():

                ok += states.get("ok", 0)
                low += states.get("low", 0)
                off += states.get("off", 0)

        return [
            {"state": "OK", "count": ok},
            {"state": "Low", "count": low},
            {"state": "Offline", "count": off}
        ]