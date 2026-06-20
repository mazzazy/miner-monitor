import json
from pathlib import Path
from datetime import datetime
from app.models.alert import Alert


class StateManager:
    def __init__(self, file_path="data/state.json"):
        self.file_path = Path(file_path)
        self.file_path.parent.mkdir(parents=True, exist_ok=True)

    def load_state(self):
        if not self.file_path.exists():
            return {}

        try:
            content = self.file_path.read_text(encoding="utf-8").strip()
            if not content:
                return {}
            return json.loads(content)

        except json.JSONDecodeError:
            return {}

        except Exception as e:
            print(f"[StateManager] Load error: {e}")
            return {}

    def save_state(self, state: dict):
        try:
            self.file_path.write_text(
                json.dumps(state, indent=2),
                encoding="utf-8"
            )
        except Exception as e:
            print(f"[StateManager] Save error: {e}")

    def diff(self, previous_state: dict, current_state: dict):
        """
        Compare previous and current worker states.

        Returns:
        alerts      -> list[Alert]
        recoveries  -> list[Alert]
        """

        previous_state = previous_state or {}

        alerts = []
        recoveries = []

        for worker, new_status in current_state.items():

            old_status = previous_state.get(worker)

            # --------------------------------------
            # No change
            # --------------------------------------
            if old_status == new_status:
                continue

            # --------------------------------------
            # OFFLINE
            # --------------------------------------
            if new_status == "off":

                alerts.append(
                    Alert(
                        worker=worker,
                        state="off",
                        severity="critical",
                        message=f"{worker} is offline"
                    )
                )

            # --------------------------------------
            # LOW HASHRATE
            # --------------------------------------
            elif new_status == "low":

                alerts.append(
                    Alert(
                        worker=worker,
                        state="low",
                        severity="warning",
                        message=f"{worker} has low hashrate"
                    )
                )

             # --------------------------------------
            # RECOVERED
            # --------------------------------------
            elif old_status in ["off", "low"] and new_status == "ok":

                recoveries.append(
                    Alert(
                        worker=worker,
                        state="ok",
                        severity="info",
                        message=f"{worker} recovered"
                    )
                )

        return alerts, recoveries