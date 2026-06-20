import json
from pathlib import Path


class StateStorage:
    def __init__(self, file_path="data/state.json"):
        self.file_path = Path(file_path)
        self.file_path.parent.mkdir(parents=True, exist_ok=True)

    def load(self):
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
            print(f"[Storage] Load error: {e}")
            return {}

    def save(self, state: dict):
        try:
            self.file_path.write_text(
                json.dumps(state, indent=2),
                encoding="utf-8"
            )
        except Exception as e:
            print(f"[Storage] Save error: {e}")