from app.api.braiins import BraiinsAPI
from app.services.storage import StateStorage
from app.services.state_manager import StateManager
from app.services.notification_service import NotificationService
from app.config import Config
from app.services.cooldown import AlertCooldown
from app.services.history_storage import HistoryStorage
from app.services.telegram_reporter import TelegramReporter
from app.services.report_generator import ReportGenerator
from app.services.report_state import ReportState
from app.services.logger import LoggerFactory
from app.services.alert_engine import AlertEngine
from app.models.alert import Alert
from datetime import date
from app.services.incident_manager import IncidentManager
from app.services.message_formatter import MessageFormatter
from app.services.uptime_engine import UptimeEngine


class Monitor:
    def __init__(self):
        
        self.storage = StateStorage()
        self.state_manager = StateManager()
        self.notification = NotificationService()
        self.cooldown = AlertCooldown(1800)  # 30 min
        self.history = HistoryStorage()
        self.reporter = TelegramReporter(self.notification)
        self.report_generator = ReportGenerator()
        self.report_state = ReportState()
        self.logger = LoggerFactory.get_logger("Monitor")
        self.api = BraiinsAPI(
            Config.BRAIINS_API_URL,
            Config.BRAIINS_API_TOKEN,
            self.logger
        )
        self.alert_engine = AlertEngine()
        self.incidents = IncidentManager()
        self.formatter = MessageFormatter()
        self.uptime_engine = UptimeEngine()

    def _is_daily_time(self):
        from datetime import datetime

        now = datetime.now()
        return now.hour == 8 and now.minute < 5
    
    def _format_alert(self, alert):
        return f"• {alert.worker} — {alert.state.upper()}"

    def _today(self):
        return date.today().isoformat()
    
    def run(self):
        self.logger.info("Monitor started")

        # 1. Fetch data
        try:
            data = self.api.fetch_workers()
        except Exception as e:
            self.notification.send(f"❌ Braiins API Failure\n\n{str(e)}")
            self.logger.info("API failed, alert sent")
            return

        workers_raw = data.get("btc", {}).get("workers", {})

        # 2. Normalize state
        current_state = {
            name: info.get("state", "unknown").lower()
            for name, info in workers_raw.items()
        }

        self.logger.info(f"Workers found: {len(current_state)}")

        # ======================================================
        # ✅ NEW STEP — UPTIME ENGINE INTEGRATION
        # ======================================================
        try:
            self.uptime_engine.record(current_state)
        except Exception as e:
            self.logger.info(f"Uptime engine failed: {str(e)}")

        # 3. Load previous state
        previous_state = self.storage.load()
        incidents = self.incidents.load()

        # 4. Smart alert generation (WITH COOLDOWN)
        alerts, recoveries = self.state_manager.diff(
            previous_state,
            current_state
        )

        filtered_alerts = []
        for alert in alerts:
            key = f"{alert.worker}:{alert.state}"
            if self.cooldown.should_alert(key):
                filtered_alerts.append(alert)

        alerts = filtered_alerts

        # Register incidents
        for alert in alerts:
            incident = self.incidents.register(
                incidents,
                alert
            )

            alert.severity = incident.severity

            alert.message = (
                f"{alert.worker} — {alert.state.upper()}\n"
                f"🕒 Started: {incident.first_seen.strftime('%H:%M')}\n"
                f"⏱ Duration: {self.incidents.duration(incident)}"
            )

        # Resolve incidents
        for recovery in recoveries:
            incident = self.incidents.resolve(
                incidents,
                recovery.worker
            )
            if incident:
                recovery.message = (
                    f"{recovery.worker}\n"
                    f"Recovered after {self.incidents.duration(incident)}"
                )

        self.logger.info(
            "Detected %d alert(s), %d recovery(ies)",
            len(alerts),
            len(recoveries)
        )

        # ==========================================================
        # 5. NOTIFY
        # ==========================================================

        summary = self.alert_engine.build(
            alerts,
            recoveries,
            current_state
        )

        if alerts or recoveries:

            message = self.formatter.build_notification(summary)

            self.notification.send(message)

            self.logger.info("Telegram notification sent")

        else:

            self.logger.info("No state changes detected")

        # 6. Save state
        self.storage.save(current_state)
        self.incidents.save(incidents)

        self.history.append_snapshot(workers_raw)

        self.logger.info("History updated")

        # ----------------------------
        # DAILY REPORT
        # ----------------------------
        if self._is_daily_time():

            today = self._today()

            if not self.report_state.is_daily_report_sent(today):

                report = self.report_generator.generate_daily_statistics()
                self.reporter.send_daily_report(report)
                self.report_state.mark_daily_report_sent(today)

                self.logger.info("Daily report sent")

            else:

                self.logger.info("Daily report already sent today")