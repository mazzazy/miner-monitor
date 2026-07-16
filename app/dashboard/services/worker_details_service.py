from datetime import datetime

from app.dashboard.services.dashboard_service import DashboardService
from app.dashboard.services.uptime_dashboard_service import UptimeDashboardService


class WorkerDetailsService:

    def __init__(self):

        self.dashboard = DashboardService()
        self.uptime = UptimeDashboardService()
    
    def get_worker(self, worker_name):

        workers = self.dashboard.get_live_workers()

        worker = workers[
            workers["Worker"] == worker_name
        ]

        if worker.empty:
            return None

        return worker.iloc[0]
    
    def get_uptime(self, worker_name):

        ranking = self.uptime.get_worker_ranking()

        row = ranking[
            ranking["Worker"] == worker_name
        ]

        if row.empty:
            return 0

        return float(row.iloc[0]["Uptime %"])
    
    def get_reliability(self, uptime):

        if uptime >= 99:

            return "★★★★★ Excellent"

        elif uptime >= 97:

            return "★★★★☆ Good"

        elif uptime >= 95:

            return "★★★☆☆ Fair"

        elif uptime >= 90:

            return "★★☆☆☆ Needs Attention"

        return "★☆☆☆☆ Poor"
    
    def format_last_share(self, unix_time):

        if not unix_time:

            return "Unknown"

        last = datetime.fromtimestamp(unix_time)

        delta = datetime.now() - last

        minutes = int(delta.total_seconds() / 60)

        if minutes < 1:
            return "Just now"

        if minutes == 1:
            return "1 minute ago"

        if minutes < 60:
            return f"{minutes} minutes ago"

        hours = minutes // 60

        if hours == 1:
            return "1 hour ago"

        if hours < 24:
            return f"{hours} hours ago"

        return last.strftime("%d %b %Y %H:%M")
    
    def get_current_incident(self, worker_name):

        incidents = self.dashboard.load_incidents()

        return incidents.get(worker_name)