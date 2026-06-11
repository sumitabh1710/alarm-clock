from __future__ import annotations

import json
import os
import tempfile
from pathlib import Path

from alarm_clock.application.ports import AlarmRepositoryPort
from alarm_clock.domain.models import Alarm


class JsonAlarmRepository(AlarmRepositoryPort):
    def __init__(self, path: str | Path) -> None:
        self.path = Path(path)

    def get_all(self) -> list[Alarm]:
        if not self.path.exists():
            return []
        try:
            raw = self.path.read_text(encoding="utf-8").strip()
            if not raw:
                return []
            data = json.loads(raw)
        except json.JSONDecodeError as exc:
            raise ValueError(
                f"Storage file is not valid JSON: {self.path}"
            ) from exc

        if not isinstance(data, list):
            raise ValueError(f"Storage must contain a JSON list: {self.path}")
        return [Alarm.from_dict(item) for item in data]

    def save_all(self, alarms: list[Alarm]) -> None:
        self.path.parent.mkdir(parents=True, exist_ok=True)
        payload = [alarm.to_dict() for alarm in alarms]
        serialized = json.dumps(payload, indent=2)

        with tempfile.NamedTemporaryFile(
            mode="w",
            encoding="utf-8",
            delete=False,
            dir=str(self.path.parent),
            prefix=f"{self.path.name}.",
            suffix=".tmp",
        ) as temp_file:
            temp_file.write(serialized)
            temp_file.flush()
            os.fsync(temp_file.fileno())
            temp_path = Path(temp_file.name)

        os.replace(temp_path, self.path)
