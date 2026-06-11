# Alarm Clock CLI (Clean Architecture)

A Python CLI alarm clock designed for the senior build exercise with a clean, testable architecture.

## Implemented Scope

- Add alarms by absolute time (`--time HH:MM`) or relative duration (`--in 10m`, `1h30m`).
- List alarms.
- Delete alarms.
- Run scheduler loop and trigger alarms.
- Daily repeat (`--daily` with `--time`).
- Snooze on trigger.
- JSON persistence (`alarms.json`).

## Assumptions

- Local machine execution only.
- Local system time is the source of truth.
- Single-user CLI workflow.
- JSON file storage is enough for exercise scope.

## Non-Goals

- Web/mobile UI.
- Database backend.
- Push notifications, email, or cloud sync.
- Multi-device state synchronization.

## Architecture

Layered clean architecture:

- `alarm_clock/domain`: entities and pure time parsing/validation logic.
- `alarm_clock/application`: use-cases, ports, and scheduler orchestration.
- `alarm_clock/infrastructure`: JSON repository and system clock adapter.
- `alarm_clock/interfaces`: Typer CLI and terminal notifier.

This keeps side effects (I/O, sleep, terminal interaction, files) outside business logic so core behavior is easier to test.

## Project Structure

```text
alarm_clock/
  application/
  domain/
  infrastructure/
  interfaces/
tests/
pyproject.toml
README.md
```

## Setup

```bash
cd /Users/sumitbiswas/alarm-clock
python -m venv .venv
source .venv/bin/activate
pip install ".[dev]"
```

## Usage

```bash
alarm add --time "07:30" --label "Wake up"
alarm add --time "09:00" --label "Standup" --daily
alarm add --in "10m" --label "Tea break"

alarm list
alarm delete 2

alarm run
```

Trigger interaction:

```text
ALARM!
Id: 1
Label: Wake up
...
[s] Snooze 5 min  [d] Dismiss (default: d):
```

## Testing

```bash
pytest
```

## Tradeoffs and Decisions

- **Typer over argparse**: cleaner command definitions and user-facing errors for fast development.
- **JSON over SQLite**: lightweight persistence aligned with prompt constraints.
- **Ports/adapters**: enables deterministic unit tests for scheduling logic without real sleeping or wall-clock dependencies.
- **Relative input + daily repeat**: high-signal features that demonstrate requirement interpretation and practical scope control.

## AI-Assisted Workflow Notes

During implementation, AI was used to:

- refine scope from ambiguous prompt;
- draft architecture and edge-case list;
- generate an initial structure;
- review and iterate on validation and scheduling behavior.

All generated code was reviewed and adjusted for correctness, boundaries, and testability.
