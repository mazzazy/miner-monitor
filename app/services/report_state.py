import json
import os
from datetime import datetime

from app.config import Config


class ReportState:

    def __init__(self):
        self.file = "data/report_state.json"
        os.makedirs("data", exist_ok=True)

    def load(self):
        if not os.path.exists(self.file):
            return {}

        try:
            with open(self.file, "r") as f:
                return json.load(f)
        except json.JSONDecodeError:
            return {}

    def save(self, state: dict):
        with open(self.file, "w") as f:
            json.dump(state, f, indent=2)

    def is_daily_report_sent(self, date_str: str) -> bool:
        state = self.load()
        return state.get("last_daily_report_date") == date_str

    def mark_daily_report_sent(self, date_str: str):
        state = self.load()
        state["last_daily_report_date"] = date_str
        state["last_daily_sent_at"] = datetime.now().isoformat()
        self.save(state)