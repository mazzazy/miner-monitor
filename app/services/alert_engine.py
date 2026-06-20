from collections import defaultdict


class AlertEngine:

    def build(self, alerts, recoveries, current_state):

        grouped = defaultdict(list)

        # -----------------------------------------
        # Group alerts by severity (NEW MODEL)
        # -----------------------------------------
        for alert in alerts:

            # primary grouping logic
            if alert.severity == "critical":
                grouped["critical"].append(alert)

            elif alert.severity == "warning":
                grouped["warning"].append(alert)

            elif alert.severity == "emergency":
                grouped["emergency"].append(alert)

            else:
                grouped["info"].append(alert)

        # -----------------------------------------
        # Farm stats
        # -----------------------------------------
        total = len(current_state)

        offline = sum(
            1 for state in current_state.values()
            if state == "off"
        )

        low = sum(
            1 for state in current_state.values()
            if state == "low"
        )

        healthy = total - offline - low

        availability = (
            (healthy / total) * 100
            if total else 0
        )

        # -----------------------------------------
        # Return structured report
        # -----------------------------------------
        return {
            "critical": grouped["critical"],
            "warning": grouped["warning"],
            "emergency": grouped["emergency"],
            "info": grouped["info"],
            "recoveries": recoveries,
            "healthy": healthy,
            "offline": offline,
            "low": low,
            "total": total,
            "availability": availability,
        }