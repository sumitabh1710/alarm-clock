from __future__ import annotations

from pathlib import Path

import typer

from alarm_clock.application.scheduler import SchedulerConfig, SchedulerService
from alarm_clock.application.use_cases import add_alarm, delete_alarm, list_alarms
from alarm_clock.infrastructure.json_repository import JsonAlarmRepository
from alarm_clock.infrastructure.system_clock import SystemClock
from alarm_clock.interfaces.notifier import TerminalNotifier

app = typer.Typer(help="Alarm clock CLI.")


def _repo(storage_path: str) -> JsonAlarmRepository:
    return JsonAlarmRepository(Path(storage_path))


@app.command("add")
def add_command(
    time: str | None = typer.Option(None, "--time", help="Time in HH:MM (24-hour)."),
    in_value: str | None = typer.Option(
        None,
        "--in",
        help="Relative duration like 10m, 2h, or 1h30m.",
    ),
    label: str = typer.Option("Alarm", "--label", help="Alarm label."),
    daily: bool = typer.Option(False, "--daily", help="Repeat every day."),
    storage_path: str = typer.Option("alarms.json", "--storage-path", help="JSON file path."),
) -> None:
    repository = _repo(storage_path)
    clock = SystemClock()
    try:
        alarm = add_alarm(
            repository,
            clock.now(),
            time_value=time,
            in_value=in_value,
            label=label,
            daily=daily,
        )
    except ValueError as exc:
        raise typer.BadParameter(str(exc)) from exc

    typer.echo(f"Added alarm {alarm.id} at {alarm.next_trigger_at.strftime('%Y-%m-%d %H:%M')}.")


@app.command("list")
def list_command(
    storage_path: str = typer.Option("alarms.json", "--storage-path", help="JSON file path."),
) -> None:
    repository = _repo(storage_path)
    alarms = list_alarms(repository)
    if not alarms:
        typer.echo("No alarms found.")
        return

    typer.echo("ID  Status   Daily  Time   Next Trigger       Label")
    for alarm in alarms:
        status = "on" if alarm.enabled else "off"
        daily_value = "yes" if alarm.daily else "no"
        next_time = alarm.next_trigger_at.strftime("%Y-%m-%d %H:%M")
        typer.echo(
            f"{alarm.id:>2}  {status:<7} {daily_value:<5} {alarm.time:<5} {next_time:<18} {alarm.label}"
        )


@app.command("delete")
def delete_command(
    alarm_id: str = typer.Argument(..., help="Alarm ID to delete."),
    storage_path: str = typer.Option("alarms.json", "--storage-path", help="JSON file path."),
) -> None:
    repository = _repo(storage_path)
    if delete_alarm(repository, alarm_id):
        typer.echo(f"Deleted alarm {alarm_id}.")
        return
    raise typer.BadParameter(f"Alarm {alarm_id} does not exist.")


@app.command("run")
def run_command(
    storage_path: str = typer.Option("alarms.json", "--storage-path", help="JSON file path."),
    snooze_minutes: int = typer.Option(5, "--snooze-minutes", min=1, help="Snooze duration."),
    poll_interval: float = typer.Option(1.0, "--poll-interval", min=0.1, help="Loop sleep."),
) -> None:
    repository = _repo(storage_path)
    service = SchedulerService(
        repository,
        SystemClock(),
        TerminalNotifier(),
        SchedulerConfig(poll_interval_seconds=poll_interval, snooze_minutes=snooze_minutes),
    )
    typer.echo("Scheduler running. Press Ctrl+C to exit.")
    service.run_forever()
