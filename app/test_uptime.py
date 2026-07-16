from services.uptime_engine import UptimeEngine

engine = UptimeEngine()

engine.record({

    "Miner01": "ok",

    "Miner02": "low",

    "Miner03": "off"

})

print("Done")