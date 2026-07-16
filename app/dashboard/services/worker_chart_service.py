import pandas as pd
from app.dashboard.services.dashboard_service import DashboardService


class WorkerChartService:

    def __init__(self):
        self.dashboard = DashboardService()

    def load_history(self):

        df = self.dashboard.load_history()

        if df.empty:
            return df

        df["timestamp"] = pd.to_datetime(df["timestamp"], errors="coerce")
        df = df.dropna(subset=["timestamp"])

        return df

    def get_worker_trend(self, worker_name):

        df = self.load_history()

        df = df[df["worker"] == worker_name]

        if df.empty:
            return pd.DataFrame()

        df = df.sort_values("timestamp")

        df["hashrate_5m"] = df["hashrate_5m"].apply(self.normalize_ths)
        df["hashrate_60m"] = df["hashrate_60m"].apply(self.normalize_ths)
        df["hashrate_24h"] = df["hashrate_24h"].apply(self.normalize_ths)

        return df[[
            "timestamp",
            "hashrate_5m",
            "hashrate_60m",
            "hashrate_24h"
        ]]
    
    def get_worker_chart_data(self, worker_name):

        df = self.get_worker_trend(worker_name)

        if df.empty:
            return df

        df = df.copy()

        df = df.sort_values("timestamp")

        df = df.set_index("timestamp")

        return df
    
    def normalize_ths(self, value, unit="Gh/s"):

        if value is None:
            return 0

        value = float(value)

        if unit.lower() == "gh/s":
            return value / 1000   # GH → TH

        if unit.lower() == "h/s":
            return value / 1e12    # H → TH

        return value
    
    def get_5m_chart(self, worker_name):

        df = self.get_worker_chart_data(worker_name)

        if df.empty:
            return df

        return df[["hashrate_5m"]]
    
    def get_60m_chart(self, worker_name):

        df = self.get_worker_chart_data(worker_name)

        if df.empty:
            return df

        return df[["hashrate_60m"]]
    
    def get_24h_chart(self, worker_name):

        df = self.get_worker_chart_data(worker_name)

        if df.empty:
            return df

        return df[["hashrate_24h"]]