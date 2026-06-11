from __future__ import annotations

from alarm_clock.application.ports import NotifierPort
from alarm_clock.domain.models import Alarm


class TerminalNotifier(NotifierPort):
    def ring(self, alarm: Alarm) -> str:
        print("\n\aALARM!")
        print(f"Id: {alarm.id}")
        print(f"Label: {alarm.label}")
        print(f"Scheduled Time: {alarm.time}")
        print(f"Triggered At: {alarm.next_trigger_at.strftime('%Y-%m-%d %H:%M')}")

        action = input("[s] Snooze 5 min  [d] Dismiss (default: d): ").strip().lower()
        if action == "s":
            return "snooze"
        return "dismiss"
