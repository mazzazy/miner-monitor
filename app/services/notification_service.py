from app.services.logger import LoggerFactory
from app.services.notifier import TelegramNotifier
from app.config import Config


class NotificationService:

    def __init__(self):

        self.logger = LoggerFactory.get_logger(
            "NotificationService"
        )
        self.telegram = TelegramNotifier()

        # Future channels
        self.email = None
        self.slack = None
        self.teams = None

    # ----------------------------------------------------
    # Send alert to every enabled channel
    # ----------------------------------------------------
    def send(self, message):

        self.logger.info("Sending notification")
        if Config.ENABLE_TELEGRAM:
            self.telegram.send(message)
            self.logger.info("Telegram notification sent")

        # Future
        if Config.ENABLE_EMAIL and self.email:
            self.email.send(message)

        if Config.ENABLE_SLACK and self.slack:
            self.slack.send(message)

        if Config.ENABLE_TEAMS and self.teams:
            self.teams.send(message)