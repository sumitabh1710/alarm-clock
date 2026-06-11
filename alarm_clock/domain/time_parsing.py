from __future__ import annotations

import re
from datetime import datetime, timedelta

TIME_RE = re.compile(r"^(?P<hour>\d{1,2}):(?P<minute>\d{2})$")
DURATION_RE = re.compile(r"(?P<value>\d+)(?P<unit>[mh])", re.IGNORECASE)


def parse_hhmm(value: str) -> tuple[int, int]:
    match = TIME_RE.match(value.strip())
    if not match:
        raise ValueError("Time must be in HH:MM format.")

    hour = int(match.group("hour"))
    minute = int(match.group("minute"))
    if hour < 0 or hour > 23 or minute < 0 or minute > 59:
        raise ValueError("Time must be a valid 24-hour value (00:00-23:59).")
    return hour, minute


def canonical_hhmm(hour: int, minute: int) -> str:
    return f"{hour:02d}:{minute:02d}"


def parse_duration(value: str) -> timedelta:
    source = value.strip().lower()
    if not source:
        raise ValueError("Relative duration cannot be empty.")

    pos = 0
    total_minutes = 0
    for match in DURATION_RE.finditer(source):
        if match.start() != pos:
            raise ValueError("Duration must look like 10m, 2h, or 1h30m.")
        amount = int(match.group("value"))
        unit = match.group("unit")
        if unit == "h":
            total_minutes += amount * 60
        else:
            total_minutes += amount
        pos = match.end()

    if pos != len(source):
        raise ValueError("Duration must look like 10m, 2h, or 1h30m.")
    if total_minutes <= 0:
        raise ValueError("Duration must be greater than zero.")
    return timedelta(minutes=total_minutes)


def next_occurrence_for_time(hour: int, minute: int, now: datetime) -> datetime:
    candidate = now.replace(hour=hour, minute=minute, second=0, microsecond=0)
    if candidate <= now:
        candidate += timedelta(days=1)
    return candidate


def next_daily_occurrence(time_value: str, now: datetime) -> datetime:
    hour, minute = parse_hhmm(time_value)
    return next_occurrence_for_time(hour, minute, now)
