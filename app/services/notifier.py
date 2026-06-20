import requests

from app.config import Config


class TelegramNotifier:

    def __init__(self):

        self.bot_token = Config.BOT_TOKEN
        self.chat_id = Config.CHAT_ID

    def send(self, message):

        url = f"https://api.telegram.org/bot{self.bot_token}/sendMessage"

        payload = {
            "chat_id": self.chat_id,
            "text": message
        }

        response = requests.post(
            url,
            data=payload,
            timeout=20
        )

        response.raise_for_status()