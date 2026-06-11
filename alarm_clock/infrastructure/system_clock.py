from __future__ import annotations

import time
from datetime import datetime

from alarm_clock.application.ports import ClockPort


class SystemClock(ClockPort):
    def now(self) -> datetime:
        return datetime.now()

    def sleep(self, seconds: float) -> None:
        time.sleep(seconds)
