from __future__ import annotations

from datetime import datetime
from typing import Protocol

from alarm_clock.domain.models import Alarm


class AlarmRepositoryPort(Protocol):
    def get_all(self) -> list[Alarm]:
        ...

    def save_all(self, alarms: list[Alarm]) -> None:
        ...


class ClockPort(Protocol):
    def now(self) -> datetime:
        ...

    def sleep(self, seconds: float) -> None:
        ...


class NotifierPort(Protocol):
    def ring(self, alarm: Alarm) -> str:
        ...
