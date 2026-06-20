class MessageFormatter:

    def build_notification(self, summary):

        sections = []

        # ---------------------------------
        # EMERGENCY
        # ---------------------------------
        if summary.get("emergency"):

            sections.append("🚨 EMERGENCY\n")

            for alert in summary["emergency"]:
                sections.append(f"• {alert.message}")

            sections.append("")

        # ---------------------------------
        # CRITICAL
        # ---------------------------------
        if summary.get("critical"):

            sections.append("🔴 CRITICAL\n")

            for alert in summary["critical"]:
                sections.append(f"• {alert.message}")

            sections.append("")

        # ---------------------------------
        # WARNING
        # ---------------------------------
        if summary.get("warning"):

            sections.append("⚠️ WARNING\n")

            for alert in summary["warning"]:
                sections.append(f"• {alert.message}")

            sections.append("")

        # ---------------------------------
        # RECOVERIES
        # ---------------------------------
        if summary.get("recoveries"):

            sections.append("🟢 RECOVERED\n")

            for recovery in summary["recoveries"]:
                sections.append(f"• {recovery.message}")

            sections.append("")

        # ---------------------------------
        # FARM STATUS
        # ---------------------------------

        sections.append("📊 FARM STATUS\n")

        sections.append(
            f"Healthy : {summary['healthy']}/{summary['total']}"
        )

        sections.append(
            f"Offline : {summary['offline']}"
        )

        sections.append(
            f"Low Hash : {summary['low']}"
        )

        sections.append(
            f"Availability : {summary['availability']:.2f}%"
        )

        return "\n".join(sections)