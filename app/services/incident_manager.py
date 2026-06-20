import json
from pathlib import Path
from datetime import datetime

from app.models.incident import Incident
from app.config import Config



class IncidentManager:

    def __init__(self, file_path="data/incidents.json"):
        self.file_path = Path(file_path)
        self.file_path.parent.mkdir(parents=True, exist_ok=True)

    # ---------------------------------
    # Load incidents
    # ---------------------------------
    def load(self):

        if not self.file_path.exists():
            return {}

        try:
            content = self.file_path.read_text(
                encoding="utf-8"
            ).strip()

            if not content:
                return {}

            raw = json.loads(content)

            incidents = {}

            for worker, item in raw.items():

                incidents[worker] = Incident(
                    worker=item["worker"],
                    state=item["state"],
                    severity=item["severity"],
                    first_seen=datetime.fromisoformat(item["first_seen"]),
                    last_seen=datetime.fromisoformat(item["last_seen"])
                )

            return incidents

        except Exception:

            return {}

    # ---------------------------------
    # Save incidents
    # ---------------------------------
    def save(self, incidents):

        raw = {}

        for worker, incident in incidents.items():

            raw[worker] = {
                "worker": incident.worker,
                "state": incident.state,
                "severity": incident.severity,
                "first_seen": incident.first_seen.isoformat(),
                "last_seen": incident.last_seen.isoformat()
            }

        self.file_path.write_text(
            json.dumps(raw, indent=2),
            encoding="utf-8"
        )
    
    def duration(self, incident):

        delta = datetime.now() - incident.first_seen

        total_seconds = int(delta.total_seconds())

        days = total_seconds // 86400
        hours = (total_seconds % 86400) // 3600
        minutes = (total_seconds % 3600) // 60

        if days:
            return f"{days}d {hours}h"

        if hours:

            return f"{hours}h {minutes}m"

        return f"{minutes}m"
    
    def calculate_severity(self, incident):
        minutes = (
        datetime.now() - incident.first_seen
        ).total_seconds() / 60
        if minutes >= Config.CRITICAL_THRESHOLD_MINUTES:
            return "emergency"
        if minutes >= Config.WARNING_THRESHOLD_MINUTES:
            return "critical"
        
        return "warning"
    
    def register(self, incidents, alert):
        now = datetime.now()
        if alert.worker not in incidents:
            incidents[alert.worker] = Incident(
                worker=alert.worker,
                state=alert.state,
                severity=alert.severity,
                first_seen=now,
                last_seen=now
            )
            return incidents[alert.worker]
        incident = incidents[alert.worker]
        incident.last_seen = now
        incident.state = alert.state
        incident.severity = self.calculate_severity(incident)
        return incident
    
    def resolve(self, incidents, worker):
        if worker not in incidents:
            return None
        incident = incidents.pop(worker)
        return incident
    
    def get(self, incidents, worker):
        return incidents.get(worker)


