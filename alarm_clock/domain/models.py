from __future__ import annotations

from dataclasses import dataclass
from datetime import datetime


@dataclass
class Alarm:
    id: str
    time: str
    label: str
    daily: bool
    enabled: bool
    next_trigger_at: datetime

    def to_dict(self) -> dict[str, object]:
        return {
            "id": self.id,
            "time": self.time,
            "label": self.label,
            "daily": self.daily,
            "enabled": self.enabled,
            "next_trigger_at": self.next_trigger_at.isoformat(),
        }

    @classmethod
    def from_dict(cls, data: dict[str, object]) -> "Alarm":
        return cls(
            id=str(data["id"]),
            time=str(data["time"]),
            label=str(data["label"]),
            daily=bool(data["daily"]),
            enabled=bool(data.get("enabled", True)),
            next_trigger_at=datetime.fromisoformat(str(data["next_trigger_at"])),
        )
