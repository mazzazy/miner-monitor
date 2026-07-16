from app.api.braiins import BraiinsAPI
from app.config import Config
from app.services.logger import LoggerFactory


class LiveDataService:

    def __init__(self):
        self.logger = LoggerFactory.get_logger("Dashboard")
        self.api = BraiinsAPI(
            Config.BRAIINS_API_URL,
            Config.BRAIINS_API_TOKEN,
            self.logger
        )


    def workers(self):
        data = self.api.fetch_workers()
        workers = data.get("btc", {}).get("workers", {})

        # Temporary debug
        first_worker = next(iter(workers.values()), None)

        if first_worker:
            print(first_worker)

        return workers