import pandas as pd
from app.config import Config
from datetime import datetime


class UptimeService:

    def __init__(self):
        self.file = Config.HISTORY_FILE

    # ---------------------------------
    # FULL UPTIME (ALL TIME)
    # ---------------------------------
    def get_uptime(self):

        df = pd.read_csv(self.file)

        df = df[
            ~df["timestamp"].astype(str).str.contains(
                "<<<<<<|======|>>>>>>",
                na=False
            )
        ]

        workers = []

        for worker, group in df.groupby("worker"):

            total = len(group)

            available = len(
                group[group["state"].isin(["ok", "low"])]
            )

            low = len(
                group[group["state"] == "low"]
            )

            offline = len(
                group[group["state"] == "off"]
            )

            uptime = (available / total * 100) if total else 0

            if uptime >= 99:
                rating = "⭐⭐⭐⭐⭐ Excellent"
            elif uptime >= 97:
                rating = "⭐⭐⭐⭐ Good"
            elif uptime >= 95:
                rating = "⭐⭐⭐ Fair"
            elif uptime >= 90:
                rating = "⭐⭐ Needs Attention"
            else:
                rating = "⭐ Poor"

            workers.append({
                "Worker": worker,
                "Uptime %": round(uptime, 2),
                "Reliability": rating,
                "Low": low,
                "Offline": offline
            })

        if not workers:
            return pd.DataFrame(columns=["Worker", "Uptime %", "Reliability", "Low", "Offline"])

        return pd.DataFrame(workers).sort_values("Uptime %", ascending=False)

    # ---------------------------------
    # UPTIME FOR PERIOD (SAFE)
    # ---------------------------------
    def get_uptime_for_period(self, days):

        df = pd.read_csv(self.file)

        df = df[
            ~df["timestamp"].astype(str).str.contains(
                "<<<<<<|======|>>>>>>",
                na=False
            )
        ]

        df["timestamp"] = pd.to_datetime(df["timestamp"], errors="coerce")
        df = df.dropna(subset=["timestamp"])

        cutoff = pd.Timestamp.now() - pd.Timedelta(days=days)
        df = df[df["timestamp"] >= cutoff]

        workers = []

        for worker, group in df.groupby("worker"):

            total = len(group)

            available = len(
                group[group["state"].isin(["ok", "low"])]
            )

            uptime = (available / total * 100) if total else 0

            workers.append({
                "Worker": worker,
                "Uptime": round(uptime, 2)
            })

        return pd.DataFrame(workers, columns=["Worker", "Uptime"])

    # ---------------------------------
    # PERIOD SUMMARY (SAFE + NO CRASH)
    # ---------------------------------
    def get_period_summary(self):

        day = self.get_uptime_for_period(1)
        week = self.get_uptime_for_period(7)
        month = self.get_uptime_for_period(30)

        def safe(df):
            if df is None or df.empty:
                return pd.DataFrame(columns=["Worker"])
            return df

        day = safe(day)
        week = safe(week)
        month = safe(month)

        day = day.rename(columns={"Uptime": "24 Hours"})
        week = week.rename(columns={"Uptime": "7 Days"})
        month = month.rename(columns={"Uptime": "30 Days"})

        result = (
            day.merge(week, on="Worker", how="outer")
               .merge(month, on="Worker", how="outer")
        )

        result = result.fillna(0)

        def rating(v):
            if v >= 99:
                return "🟢 Excellent"
            elif v >= 97:
                return "🟢 Good"
            elif v >= 95:
                return "🟡 Fair"
            elif v >= 90:
                return "🟠 Needs Attention"
            else:
                return "🔴 Poor"

        result["Reliability"] = result["30 Days"].apply(rating)

        result = result.sort_values(by="30 Days", ascending=True)

        expected_cols = ["24 Hours", "7 Days", "30 Days"]
        for col in expected_cols:
            if col not in result.columns:
                result[col] = 0
            result = result.reindex(columns=[
                "Worker",
                "24 Hours",
                "7 Days",
                "30 Days",
                "Reliability"
            ])
            result[col] = pd.to_numeric(result[col], errors="coerce").fillna(0).round(2)
        

        return result