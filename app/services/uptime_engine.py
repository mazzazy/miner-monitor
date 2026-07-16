import json
from pathlib import Path
from datetime import datetime
from datetime import datetime, timedelta


class UptimeEngine:

    def __init__(self):

        project_root = Path(__file__).resolve().parents[2]
        self.file = project_root / "data" / "uptime.json"

        self.file.parent.mkdir(
            parents=True,
            exist_ok=True
        )

    # ---------------------------------
    # Load
    # ---------------------------------

    def load(self):

        if not self.file.exists():
            return {}

        try:

            return json.loads(
                self.file.read_text(
                    encoding="utf-8"
                )
            )

        except Exception:

            return {}

    # ---------------------------------
    # Save
    # ---------------------------------

    def save(self, data):

        self.file.write_text(

            json.dumps(
                data,
                indent=2
            ),

            encoding="utf-8"
        )
    
    def current_hour(self):

        return datetime.now().strftime(
            "%Y-%m-%d %H:00"
        )
    
    def ensure_worker_hour(self, data, worker, hour):

        if worker not in data:

            data[worker] = {}

        if hour not in data[worker]:

            data[worker][hour] = {

                "ok": 0,

                "low": 0,

                "off": 0
            }

        return data[worker][hour]
    
    def record(self, workers):
        data = self.load()
        last_run = self.get_last_run(data)
        now = datetime.now()
        
        # First run fallback
        if last_run:
            last_run = datetime.fromisoformat(last_run)
        else:
            last_run = now - timedelta(minutes=1)

        # Prevent negative or zero intervals
        if now <= last_run:
            return
        
        # Walk through each minute (cheap + simple + accurate enough for monitoring)
        cursor = last_run
        while cursor < now:
            next_cursor = cursor + timedelta(minutes=1)
            hour_key = cursor.strftime("%Y-%m-%d %H:00")
            for worker, state in workers.items():
                bucket = self.ensure_worker_hour(
                    data,
                    worker,
                    hour_key
                )
                state = (state or "off").lower()
                if state not in bucket:
                    state = "off"
                bucket[state] += 1  # 1 minute per loop step
            cursor = next_cursor

        # update last run time
        self.set_last_run(data)
        self.save(data)

    
    def get_last_run(self, data):
        return data.get("_meta", {}).get("last_run")
    
    def set_last_run(self, data):
        if "_meta" not in data:
            data["_meta"] = {}
        data["_meta"]["last_run"] = datetime.now().isoformat()

    def elapsed_minutes(self, data):
        last = self.get_last_run(data)
        if last is None:
            return 60
        last = datetime.fromisoformat(last)
        delta = datetime.now() - last
        minutes = delta.total_seconds() / 60
        return max(1, round(minutes))

