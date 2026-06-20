import time


class AlertCooldown:
    def __init__(self, cooldown_seconds=1800):
        self.cooldown = cooldown_seconds
        self.last_alert = {}

    def should_alert(self, key):
        now = time.time()

        if key not in self.last_alert:
            self.last_alert[key] = now
            return True

        if now - self.last_alert[key] > self.cooldown:
            self.last_alert[key] = now
            return True

        return False