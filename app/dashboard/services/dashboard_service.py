from pathlib import Path
import json
import pandas as pd
from app.dashboard.services.live_data import LiveDataService
from app.dashboard.services.dashboard_model import DashboardModel
from app.dashboard.services.hashrate_formatter import HashrateFormatter


class DashboardService:

    def __init__(self):
        self.data_folder = Path("data")
        self.live = LiveDataService()
        self.data_folder = Path("data")

    def load_state(self):

        file = self.data_folder / "state.json"

        if not file.exists():
            return {}

        with open(file, "r", encoding="utf-8") as f:
            return json.load(f)

    def load_incidents(self):
        file = self.data_folder / "incidents.json"
        if not file.exists():
            return {}
        with open(file, "r", encoding="utf-8") as f:
            return json.load(f)
        

    def load_history(self):
        file = self.data_folder / "history.csv"
        if not file.exists():
            return pd.DataFrame()
        return pd.read_csv(file)
    

    def get_current_statistics(self):

        workers = self.live.workers()
        total = len(workers)
        online = 0
        offline = 0
        low = 0

        total_hashrate = 0
        for info in workers.values():
            state = info.get("state", "").lower()
            if state == "ok":
                online += 1
            elif state == "off":
                offline += 1
            elif state == "low":
                low += 1
            total_hashrate += HashrateFormatter.gh_to_th(
                info.get("hash_rate_5m", 0)
                
            )
        availability = (
                online / total * 100
                if total else 0
        )
        return {

            "workers": total,

            "online": online,

            "offline": offline,

            "low": low,

            "availability": availability,

            "hashrate": total_hashrate
        }

    


    
    def get_open_incidents(self):
        incidents = self.load_incidents()
        return len(incidents)
    
    def get_incident_list(self):
        incidents = self.load_incidents()
        rows = []
        for worker, incident in incidents.items():
            rows.append({
                "Worker": worker,
                "State": incident["state"],
                 "Severity": incident["severity"],
                  "First Seen": incident["first_seen"]
            })
        return pd.DataFrame(rows)
    
    def get_workers(self):
        return pd.DataFrame()
    
    def get_live_workers(self):
        workers = self.live.workers()
        rows = DashboardModel.from_api(workers)
        
        return pd.DataFrame(rows)
    
    @staticmethod
    def normalize_hashrate(value):
        """
        Try to normalize raw hashrate into TH/s
        Assumption: raw is in H/s or GH/s depending on source
        """

        if value is None:
            return 0

        value = float(value) / 1000

        return value
        

