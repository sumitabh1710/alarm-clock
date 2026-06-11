from __future__ import annotations

from dataclasses import dataclass
from datetime import datetime, timedelta

from alarm_clock.application.ports import AlarmRepositoryPort, ClockPort, NotifierPort
from alarm_clock.domain.models import Alarm
from alarm_clock.domain.time_parsing import next_daily_occurrence


@dataclass
class SchedulerConfig:
    poll_interval_seconds: float = 1.0
    snooze_minutes: int = 5


def next_due_alarm(alarms: list[Alarm], now: datetime) -> Alarm | None:
    candidates = [alarm for alarm in alarms if alarm.enabled and alarm.next_trigger_at <= now]
    if not candidates:
        return None
    return min(candidates, key=lambda alarm: alarm.next_trigger_at)


class SchedulerService:
    def __init__(
        self,
        repository: AlarmRepositoryPort,
        clock: ClockPort,
        notifier: NotifierPort,
        config: SchedulerConfig | None = None,
    ) -> None:
        self.repository = repository
        self.clock = clock
        self.notifier = notifier
        self.config = config or SchedulerConfig()

    def run_forever(self) -> None:
        while True:
            alarms = self.repository.get_all()
            now = self.clock.now()
            due = next_due_alarm(alarms, now)

            if due is None:
                self.clock.sleep(self._next_sleep_seconds(alarms, now))
                continue

            action = self.notifier.ring(due)
            self._apply_action(due, action, self.clock.now())
            self.repository.save_all(alarms)

    def _next_sleep_seconds(self, alarms: list[Alarm], now: datetime) -> float:
        enabled = [alarm for alarm in alarms if alarm.enabled]
        if not enabled:
            return self.config.poll_interval_seconds
        nearest = min(enabled, key=lambda alarm: alarm.next_trigger_at)
        seconds = (nearest.next_trigger_at - now).total_seconds()
        if seconds <= 0:
            return 0.0
        return min(self.config.poll_interval_seconds, seconds)

    def _apply_action(self, alarm: Alarm, action: str, now: datetime) -> None:
        if action == "snooze":
            alarm.next_trigger_at = (now + timedelta(minutes=self.config.snooze_minutes)).replace(
                second=0, microsecond=0
            )
            alarm.enabled = True
            return

        if alarm.daily:
            alarm.next_trigger_at = next_daily_occurrence(alarm.time, now)
            alarm.enabled = True
            return

        alarm.enabled = False
