from __future__ import annotations

from datetime import datetime

import pytest

from alarm_clock.application.use_cases import add_alarm, delete_alarm
from alarm_clock.domain.models import Alarm


class InMemoryRepo:
    def __init__(self, alarms: list[Alarm] | None = None) -> None:
        self.alarms = alarms or []

    def get_all(self) -> list[Alarm]:
        return list(self.alarms)

    def save_all(self, alarms: list[Alarm]) -> None:
        self.alarms = list(alarms)


def test_add_alarm_with_time() -> None:
    repo = InMemoryRepo()
    now = datetime(2026, 1, 1, 8, 0)
    alarm = add_alarm(
        repo,
        now,
        time_value="08:30",
        in_value=None,
        label="Standup",
        daily=True,
    )
    assert alarm.id == "1"
    assert alarm.daily is True
    assert alarm.next_trigger_at == datetime(2026, 1, 1, 8, 30)


def test_add_alarm_with_relative_duration() -> None:
    repo = InMemoryRepo()
    now = datetime(2026, 1, 1, 8, 0)
    alarm = add_alarm(
        repo,
        now,
        time_value=None,
        in_value="45m",
        label="Break",
        daily=False,
    )
    assert alarm.next_trigger_at == datetime(2026, 1, 1, 8, 45)


def test_add_alarm_rejects_daily_with_relative() -> None:
    repo = InMemoryRepo()
    with pytest.raises(ValueError):
        add_alarm(
            repo,
            datetime(2026, 1, 1, 8, 0),
            time_value=None,
            in_value="10m",
            label="Bad",
            daily=True,
        )


def test_delete_alarm_returns_false_for_missing() -> None:
    repo = InMemoryRepo()
    assert delete_alarm(repo, "1") is False


def test_delete_alarm_removes_existing() -> None:
    repo = InMemoryRepo(
        [Alarm("1", "09:00", "A", False, True, datetime(2026, 1, 1, 9, 0))]
    )
    assert delete_alarm(repo, "1") is True
    assert repo.get_all() == []
