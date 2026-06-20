from dataclasses import dataclass
from typing import Optional


@dataclass
class Worker:
    name: str
    state: str
    hash_rate_5m: float
    hash_rate_60m: float
    hash_rate_24h: float
    last_share: int
    hash_rate_unit: str = "Gh/s"

    @property
    def hash_rate_th(self):
        return self.hash_rate_5m / 1000

    @property
    def hash_rate_ph(self):
        return self.hash_rate_5m / 1_000_000


@dataclass
class Alert:

    worker: str
    severity: str
    message: str


@dataclass
class DailySummary:

    timestamp: str

    total_workers: int

    online_workers: int

    offline_workers: int

    low_workers: int

    total_hashrate_ph: float