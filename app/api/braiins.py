import requests
import time
from app.services.logger import LoggerFactory


class BraiinsAPI:

    def __init__(self, url: str, token: str,logger=None):
        self.url = url
        self.token = token
        
        # ✅ FIX: safe logger fallback
        if logger is None:
            import logging
            self.logger = logging.getLogger("BraiinsAPI")
        else:
            self.logger = logger

        self.session = requests.Session()
        self.session.headers.update({
            "Pool-Auth-Token": self.token
        })


        # resilience config
        self.max_retries = 5
        self.base_delay = 2  # seconds
        self.timeout = 30

    def fetch_workers(self):

        last_error = None

        for attempt in range(1, self.max_retries + 1):

            try:
                # print(f"🌐 API call attempt {attempt}")
                if self.logger:
                    self.logger.info(f"API attempt {attempt}")

                response = self.session.get(
                    self.url,
                    timeout=self.timeout
                )

                # Handle HTTP errors explicitly
                if response.status_code == 429:
                    raise Exception("Rate limited (429)")

                if response.status_code >= 500:
                    raise Exception(f"Server error {response.status_code}")

                response.raise_for_status()

                data = response.json()

                # validate structure
                if not isinstance(data, dict):
                    raise ValueError("Invalid API response format (not dict)")

                if "btc" not in data or "workers" not in data["btc"]:
                    raise ValueError("Missing btc/workers in response")

                return data

            except (requests.Timeout, requests.ConnectionError) as e:
                last_error = e
                # print(f"⛔ Network error: {e}")
                if self.logger:
                    self.logger.info(f"Network error: {e}")

            except Exception as e:
                last_error = e
                # print(f"⚠ API error: {e}")
                if self.logger:
                    self.logger.info(f"API error: {e}")

            # exponential backoff
            sleep_time = self.base_delay * (2 ** (attempt - 1))
            print(f"⏳ retrying in {sleep_time}s...")
            if self.logger:
                self.logger.info(f"retrying in {sleep_time}s...")
            time.sleep(sleep_time)

        # if all retries fail
        raise RuntimeError(
            f"Braiins API failed after {self.max_retries} attempts. Last error: {last_error}"
        )