from datetime import datetime

import pytest

from alarm_clock.domain.time_parsing import next_occurrence_for_time, parse_duration, parse_hhmm


def test_parse_hhmm_valid() -> None:
    assert parse_hhmm("07:30") == (7, 30)
    assert parse_hhmm("0:05") == (0, 5)


def test_parse_hhmm_invalid() -> None:
    with pytest.raises(ValueError):
        parse_hhmm("25:10")
    with pytest.raises(ValueError):
        parse_hhmm("bad")


def test_parse_duration_valid() -> None:
    assert int(parse_duration("10m").total_seconds()) == 600
    assert int(parse_duration("1h30m").total_seconds()) == 5400


def test_parse_duration_invalid() -> None:
    with pytest.raises(ValueError):
        parse_duration("0m")
    with pytest.raises(ValueError):
        parse_duration("1x")


def test_next_occurrence_rolls_to_next_day() -> None:
    now = datetime(2026, 1, 1, 8, 0)
    occurrence = next_occurrence_for_time(7, 30, now)
    assert occurrence == datetime(2026, 1, 2, 7, 30)
