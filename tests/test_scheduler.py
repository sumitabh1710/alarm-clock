from datetime import datetime

from alarm_clock.application.scheduler import SchedulerConfig, SchedulerService, next_due_alarm
from alarm_clock.domain.models import Alarm


class FakeRepo:
    def __init__(self, alarms: list[Alarm]) -> None:
        self.alarms = alarms

    def get_all(self) -> list[Alarm]:
        return self.alarms

    def save_all(self, alarms: list[Alarm]) -> None:
        self.alarms = alarms


class FakeClock:
    def __init__(self, now_value: datetime) -> None:
        self.now_value = now_value
        self.slept_seconds: list[float] = []

    def now(self) -> datetime:
        return self.now_value

    def sleep(self, seconds: float) -> None:
        self.slept_seconds.append(seconds)


class FakeNotifier:
    def __init__(self, action: str) -> None:
        self.action = action

    def ring(self, alarm: Alarm) -> str:
        return self.action


def test_next_due_alarm_returns_earliest_due() -> None:
    now = datetime(2026, 1, 1, 9, 0)
    alarms = [
        Alarm("1", "08:00", "A", False, True, datetime(2026, 1, 1, 8, 59)),
        Alarm("2", "09:00", "B", False, True, datetime(2026, 1, 1, 9, 0)),
    ]
    due = next_due_alarm(alarms, now)
    assert due is not None
    assert due.id == "1"


def test_apply_action_snooze_moves_alarm() -> None:
    alarm = Alarm("1", "09:00", "A", False, True, datetime(2026, 1, 1, 9, 0))
    repo = FakeRepo([alarm])
    clock = FakeClock(datetime(2026, 1, 1, 9, 0))
    notifier = FakeNotifier("snooze")
    service = SchedulerService(repo, clock, notifier, SchedulerConfig(snooze_minutes=5))

    service._apply_action(alarm, "snooze", clock.now())  # noqa: SLF001
    assert alarm.next_trigger_at == datetime(2026, 1, 1, 9, 5)
    assert alarm.enabled is True


def test_apply_action_daily_reschedules() -> None:
    alarm = Alarm("1", "07:30", "Daily", True, True, datetime(2026, 1, 1, 7, 30))
    repo = FakeRepo([alarm])
    clock = FakeClock(datetime(2026, 1, 1, 8, 0))
    notifier = FakeNotifier("dismiss")
    service = SchedulerService(repo, clock, notifier)

    service._apply_action(alarm, "dismiss", clock.now())  # noqa: SLF001
    assert alarm.next_trigger_at == datetime(2026, 1, 2, 7, 30)
    assert alarm.enabled is True


def test_apply_action_one_time_disables() -> None:
    alarm = Alarm("1", "07:30", "One", False, True, datetime(2026, 1, 1, 7, 30))
    repo = FakeRepo([alarm])
    clock = FakeClock(datetime(2026, 1, 1, 8, 0))
    notifier = FakeNotifier("dismiss")
    service = SchedulerService(repo, clock, notifier)

    service._apply_action(alarm, "dismiss", clock.now())  # noqa: SLF001
    assert alarm.enabled is False
