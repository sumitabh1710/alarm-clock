from __future__ import annotations

from datetime import datetime

from alarm_clock.application.ports import AlarmRepositoryPort
from alarm_clock.domain.models import Alarm
from alarm_clock.domain.time_parsing import (
    canonical_hhmm,
    next_occurrence_for_time,
    parse_duration,
    parse_hhmm,
)


def list_alarms(repository: AlarmRepositoryPort) -> list[Alarm]:
    alarms = repository.get_all()
    return sorted(alarms, key=lambda alarm: alarm.next_trigger_at)


def delete_alarm(repository: AlarmRepositoryPort, alarm_id: str) -> bool:
    alarms = repository.get_all()
    before = len(alarms)
    filtered = [alarm for alarm in alarms if alarm.id != alarm_id]
    if len(filtered) == before:
        return False
    repository.save_all(filtered)
    return True


def add_alarm(
    repository: AlarmRepositoryPort,
    now: datetime,
    *,
    time_value: str | None,
    in_value: str | None,
    label: str,
    daily: bool,
) -> Alarm:
    cleaned_label = label.strip()
    if not cleaned_label:
        raise ValueError("Label cannot be empty.")
    if time_value and in_value:
        raise ValueError("Use either --time or --in, not both.")
    if not time_value and not in_value:
        raise ValueError("Provide one of --time or --in.")
    if daily and in_value:
        raise ValueError("Daily alarms support --time only.")

    if time_value:
        hour, minute = parse_hhmm(time_value)
        canonical_time = canonical_hhmm(hour, minute)
        next_trigger = next_occurrence_for_time(hour, minute, now)
    else:
        delta = parse_duration(in_value or "")
        next_trigger = now + delta
        canonical_time = canonical_hhmm(next_trigger.hour, next_trigger.minute)

    alarms = repository.get_all()
    alarm = Alarm(
        id=_next_id(alarms),
        time=canonical_time,
        label=cleaned_label,
        daily=daily,
        enabled=True,
        next_trigger_at=next_trigger.replace(second=0, microsecond=0),
    )
    alarms.append(alarm)
    repository.save_all(alarms)
    return alarm


def _next_id(alarms: list[Alarm]) -> str:
    max_id = 0
    for alarm in alarms:
        try:
            value = int(alarm.id)
            max_id = max(max_id, value)
        except ValueError:
            continue
    return str(max_id + 1)
