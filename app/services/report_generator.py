import pandas as pd

from app.config import Config


class ReportGenerator:

    def __init__(self):
        self.history_file = Config.HISTORY_FILE

    def load_history(self):
        return pd.read_csv(self.history_file)

    def generate_daily_statistics(self):

        df = self.load_history()

        # ----------------------------
        # Convert units
        # ----------------------------

        df["hashrate_th"] = df["hashrate_5m"] / 1000
        df["hashrate_ph"] = df["hashrate_5m"] / 1_000_000

        # ----------------------------
        # Farm statistics
        # ----------------------------

        farm = {}

        farm["miners"] = df["worker"].nunique()

        farm["average_ph"] = round(df["hashrate_ph"].mean(), 3)

        farm["max_ph"] = round(df["hashrate_ph"].max(), 3)

        farm["min_ph"] = round(df["hashrate_ph"].min(), 3)

        farm["offline_samples"] = (df["state"] == "off").sum()

        farm["low_samples"] = (df["state"] == "low").sum()

        # ----------------------------
        # Per miner
        # ----------------------------

        miner_stats = (
            df.groupby("worker")
            .agg(
                avg_hashrate=("hashrate_th", "mean"),
                max_hashrate=("hashrate_th", "max"),
                min_hashrate=("hashrate_th", "min"),
                offline=("state", lambda x: (x == "off").sum()),
                low=("state", lambda x: (x == "low").sum()),
                samples=("worker", "count"),
            )
            .reset_index()
        )

        miner_stats["uptime"] = (
            (miner_stats["samples"] - miner_stats["offline"])
            / miner_stats["samples"]
            * 100
        )

        miner_stats["avg_hashrate"] = miner_stats["avg_hashrate"].round(2)
        miner_stats["max_hashrate"] = miner_stats["max_hashrate"].round(2)
        miner_stats["min_hashrate"] = miner_stats["min_hashrate"].round(2)
        miner_stats["uptime"] = miner_stats["uptime"].round(1)

        # ----------------------------
        # Rankings
        # ----------------------------

        top5 = miner_stats.nlargest(5, "avg_hashrate")

        bottom5 = miner_stats.nsmallest(5, "avg_hashrate")

        return {
            "farm": farm,
            "miners": miner_stats,
            "top5": top5,
            "bottom5": bottom5,
        }