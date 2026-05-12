---
name: loop-run
description: Start an orchestrated loop on a task. Reads .loop/config.toml or generates a default. Writes state to .loop/<run-id>/.
args: "[task-description]"
---

# /loop-run

Starts an orchestrated 4-role loop on the given task.

## Usage

```
/loop-run "Refaktoriere foo.py und passe Tests an"
```

Or without task description (uses `[loop].task_name` from config):

```
/loop-run
```

## What this command does

The `orchestrated-loop` skill handles the full flow:

1. Locates `.loop/config.toml` (offers to generate if missing).
2. Generates a run-id and creates `.loop/<run-id>/`.
3. Invokes the engine via PYTHONPATH (no installation required).
4. Updates `.loop/latest` and summarizes the result.

See `skills/orchestrated-loop/SKILL.md` for details.
