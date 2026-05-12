"""Codex Rescue Builder: writes a task file, invokes `codex rescue`, reads result."""

from __future__ import annotations

import json
import shutil
import subprocess
from pathlib import Path

from orchestrated_loop.adapters.base import (
    AdapterUnavailable,
    BuildResult,
    Plan,
    ResearchResult,
)


class CodexRescueBuilder:
    def __init__(
        self,
        handoff_dir: Path,
        profile: str | None = None,
        timeout_seconds: int = 600,
    ) -> None:
        binary = shutil.which("codex")
        if binary is None:
            raise AdapterUnavailable("codex CLI not on PATH.")
        self._binary = binary
        self._handoff = Path(handoff_dir)
        self._profile = profile
        self._timeout = timeout_seconds

    def run(self, plan: Plan, research: ResearchResult) -> BuildResult:
        iter_dir = self._handoff / f"iter-{plan.iteration:02d}"
        iter_dir.mkdir(parents=True, exist_ok=True)

        task_file = iter_dir / "codex-task.md"
        task_file.write_text(self._render_task(plan, research), encoding="utf-8")

        result_file = iter_dir / "codex-result.json"

        cmd = [self._binary, "rescue", "--plan", str(task_file), "--output", str(result_file)]
        if self._profile:
            cmd += ["--profile", self._profile]

        try:
            completed = subprocess.run(
                cmd,
                text=True,
                encoding="utf-8",
                errors="replace",
                capture_output=True,
                stdin=subprocess.DEVNULL,
                timeout=self._timeout,
                check=False,
            )
        except subprocess.TimeoutExpired as exc:
            return BuildResult(
                command=" ".join(cmd),
                returncode=124,
                stdout=exc.stdout or "",
                stderr=f"codex rescue Timeout nach {self._timeout}s\n{exc.stderr or ''}",
                artifacts=[],
            )

        if completed.returncode != 0:
            return BuildResult(
                command=" ".join(cmd),
                returncode=completed.returncode,
                stdout=completed.stdout,
                stderr=completed.stderr,
                artifacts=[],
            )

        if not result_file.exists():
            return BuildResult(
                command=" ".join(cmd),
                returncode=1,
                stdout=completed.stdout,
                stderr="codex rescue ended with 0 but no result file.",
                artifacts=[],
            )

        payload = json.loads(result_file.read_text(encoding="utf-8"))
        return BuildResult(
            command=" ".join(cmd),
            returncode=0,
            stdout=payload.get("logs", "") or completed.stdout,
            stderr=completed.stderr,
            artifacts=list(payload.get("artifacts", [])),
        )

    @staticmethod
    def _render_task(plan: Plan, research: ResearchResult) -> str:
        parts = [
            f"# Codex Task — Iteration {plan.iteration}",
            "",
            f"## Goal\n{plan.goal}",
            "",
            "## Tasks",
            *(f"- {t}" for t in plan.tasks),
            "",
            "## Acceptance",
            *(f"- {c}" for c in plan.acceptance_criteria),
            "",
            "## Research",
            research.answer or "(no research)",
        ]
        return "\n".join(parts) + "\n"
