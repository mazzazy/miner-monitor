from datetime import datetime

from app.config import Config


class TelegramReporter:

    def __init__(self, notification_service):
        self.notification = notification_service
        self.pool_name = Config.POOL_NAME

    def send_daily_report(self, report: dict):

        farm = report["farm"]
        top5 = report["top5"]
        bottom5 = report["bottom5"]

        date = datetime.now().strftime("%Y-%m-%d")

        message = f"📊 Daily Mining Report - {self.pool_name}\n"
        message += f"📅 {date}\n\n"

        # -------------------------
        # Farm Summary
        # -------------------------
        message += "🏭 Farm Summary\n"
        message += f"• Miners: {farm['miners']}\n"
        message += f"• Avg Hashrate: {farm['average_ph']} PH/s\n"
        message += f"• Peak Hashrate: {farm['max_ph']} PH/s\n"
        message += f"• Offline Events: {farm['offline_samples']}\n"
        message += f"• Low Hashrate Events: {farm['low_samples']}\n\n"

        # -------------------------
        # Top 5
        # -------------------------
        message += "🥇 Top Performers\n"

        for i, row in top5.iterrows():
            message += (
                f"{i+1}. {row['worker']} — "
                f"{row['avg_hashrate']:.2f} TH/s (Uptime {row['uptime']}%)\n"
            )

        message += "\n"

        # -------------------------
        # Bottom 5
        # -------------------------
        message += "🔻 Needs Attention\n"

        for i, row in bottom5.iterrows():
            message += (
                f"{i+1}. {row['worker']} — "
                f"{row['avg_hashrate']:.2f} TH/s (Uptime {row['uptime']}%)\n"
            )

        # -------------------------
        # Send
        # -------------------------
        self.notification.send(message)