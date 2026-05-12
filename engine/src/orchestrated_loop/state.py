"""StateStore: writes PLAN/TODO/LOG/DECISIONS/RESULTS files."""

from __future__ import annotations

import json
from datetime import datetime, timezone
from pathlib import Path
from typing import Any


def utc_now() -> str:
    return datetime.now(timezone.utc).isoformat(timespec="seconds")


class StateStore:
    """Owns the five core state files inside a single run directory."""

    CORE_FILES = ("PLAN.md", "TODO.md", "LOG.md", "DECISIONS.md", "RESULTS.json")

    def __init__(self, run_dir: Path) -> None:
        self.run_dir = Path(run_dir)
        self.run_dir.mkdir(parents=True, exist_ok=True)

    def reset_core_files(self, task_name: str) -> None:
        (self.run_dir / "PLAN.md").write_text(
            f"# Plan\n\nTask: {task_name}\n", encoding="utf-8"
        )
        (self.run_dir / "TODO.md").write_text("# TODO\n", encoding="utf-8")
        (self.run_dir / "LOG.md").write_text(
            f"# Log\n\nStart: {utc_now()}\n\n", encoding="utf-8"
        )
        (self.run_dir / "DECISIONS.md").write_text("# Decisions\n", encoding="utf-8")
        (self.run_dir / "RESULTS.json").write_text(
            json.dumps({"task_name": task_name, "started_at": utc_now(), "iterations": []}, indent=2),
            encoding="utf-8",
        )

    def write_plan(self, plan: dict[str, Any]) -> None:
        lines = [
            "# Plan",
            "",
            f"Goal: {plan.get('goal', '')}",
            f"Iteration {plan.get('iteration', 0)}",
            "",
            "## Tasks",
        ]
        lines.extend(f"- {t}" for t in plan.get("tasks", []))
        lines += ["", "## Questions"]
        lines.extend(f"- {q}" for q in plan.get("questions", []))
        lines += ["", "## Acceptance"]
        lines.extend(f"- {c}" for c in plan.get("acceptance_criteria", []))
        (self.run_dir / "PLAN.md").write_text("\n".join(lines) + "\n", encoding="utf-8")

    def write_todo(self, tasks: list[str]) -> None:
        lines = ["# TODO", ""]
        lines.extend(f"- [ ] {t}" for t in tasks)
        (self.run_dir / "TODO.md").write_text("\n".join(lines) + "\n", encoding="utf-8")

    def append_log(self, section: str, body: str) -> None:
        path = self.run_dir / "LOG.md"
        existing = path.read_text(encoding="utf-8") if path.exists() else ""
        path.write_text(
            existing + f"\n## {section} ({utc_now()})\n\n{body}\n",
            encoding="utf-8",
        )

    def append_decision(self, body: str) -> None:
        path = self.run_dir / "DECISIONS.md"
        existing = path.read_text(encoding="utf-8") if path.exists() else ""
        path.write_text(existing + f"\n- {utc_now()}: {body}\n", encoding="utf-8")

    def load_results(self) -> dict[str, Any]:
        path = self.run_dir / "RESULTS.json"
        if not path.exists():
            return {}
        return json.loads(path.read_text(encoding="utf-8"))

    def write_results(self, data: dict[str, Any]) -> None:
        (self.run_dir / "RESULTS.json").write_text(
            json.dumps(data, indent=2, ensure_ascii=False), encoding="utf-8"
        )
