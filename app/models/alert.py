from dataclasses import dataclass


@dataclass
class Alert:

    worker: str
    state: str          # ok / low / off
    severity: str       # info / warning / critical
    message: str