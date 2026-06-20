from dataclasses import dataclass
from datetime import datetime


@dataclass
class Incident:
    worker: str
    state: str
    severity: str
    first_seen: datetime
    last_seen: datetime