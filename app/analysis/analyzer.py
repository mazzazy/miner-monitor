import time

from app.config import Config


class Analyzer:

    def analyze(self, workers):

        now = int(time.time())

        offline = []

        low = []

        dead = []

        for worker in workers:

            last_seen = now - worker.last_share

            #
            # DEAD
            #

            if worker.hash_rate_5m == 0 and last_seen > Config.DEAD_THRESHOLD:

                dead.append(worker)

                continue

            #
            # OFFLINE
            #

            if worker.state.lower() == "off":

                offline.append(worker)

                continue

            if last_seen > Config.OFFLINE_THRESHOLD:

                offline.append(worker)

                continue

            #
            # LOW
            #

            if worker.state.lower() == "low":

                low.append(worker)

                continue

            if worker.hash_rate_24h > 0:

                ratio = worker.hash_rate_5m / worker.hash_rate_24h

                if ratio < Config.LOW_HASHRATE_RATIO:

                    low.append(worker)

        return offline, low, dead