import pandas as pd
from app.config import Config


class ChartService:

    def __init__(self):
        self.file = Config.HISTORY_FILE

    def load_history(self):
        df = pd.read_csv(self.file)

        # Clean broken git conflict lines (safety layer)
        df = df[~df["timestamp"].astype(str).str.contains("<<<<<<|======|>>>>>>", na=False)]

        # Safe datetime parsing
        df["timestamp"] = pd.to_datetime(df["timestamp"], errors="coerce")

        # Detect bad rows BEFORE dropping
        bad_rows = df[df["timestamp"].isna()]
        if len(bad_rows) > 0:
            print(f"⚠️ Removed {len(bad_rows)} corrupted history rows")

        # Remove invalid rows
        df = df.dropna(subset=["timestamp"])

        return df

        

    def get_farm_hashrate_trend(self):
        df = self.load_history()

        # Convert hashrate columns to numeric safety
        df["hashrate_5m"] = pd.to_numeric(df["hashrate_5m"], errors="coerce")

        # Group by time
        trend = df.groupby("timestamp")["hashrate_5m"].sum().reset_index()

        return trend

    def get_worker_trend(self, worker_name):
        df = self.load_history()

        df = df[df["worker"] == worker_name]

        df["hashrate_5m"] = pd.to_numeric(df["hashrate_5m"], errors="coerce")

        return df[["timestamp", "hashrate_5m"]]