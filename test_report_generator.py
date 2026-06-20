from app.services.report_generator import ReportGenerator

report = ReportGenerator().generate_daily_statistics()

print("\n========== FARM ==========")

for k, v in report["farm"].items():
    print(f"{k:20}: {v}")

print("\n========== TOP 5 ==========")

print(
    report["top5"][
        [
            "worker",
            "avg_hashrate",
            "uptime",
            "offline",
        ]
    ]
)

print("\n========== BOTTOM 5 ==========")

print(
    report["bottom5"][
        [
            "worker",
            "avg_hashrate",
            "uptime",
            "offline",
        ]
    ]
)