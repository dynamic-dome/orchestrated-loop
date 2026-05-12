"""Local shell Builder: runs a command and captures stdout/stderr."""

from __future__ import annotations

import os
import shlex
import subprocess
import sys
from pathlib import Path

from orchestrated_loop.adapters.base import BuildResult, Plan, ResearchResult


class LocalShellBuilder:
    def __init__(
        self,
        command: str,
        timeout_seconds: int = 120,
        project_root: Path | None = None,
        test_command: str | None = None,
    ) -> None:
        self.command = command
        self.timeout_seconds = timeout_seconds
        self.project_root = Path(project_root) if project_root else Path.cwd()
        self.test_command = test_command

    def run(self, plan: Plan, research: ResearchResult) -> BuildResult:
        primary = self._exec(self.command, label="builder_command")
        if self.test_command and primary.returncode == 0:
            test_result = self._exec(self.test_command, label="test_command")
            primary.stdout += "\n\n--- test_command STDOUT ---\n" + test_result.stdout
            primary.stderr += "\n\n--- test_command STDERR ---\n" + test_result.stderr
            if test_result.returncode != 0:
                primary.returncode = test_result.returncode
        return primary

    def _exec(self, command: str, label: str) -> BuildResult:
        rendered = command.replace("{python}", shlex.quote(sys.executable))
        env = os.environ.copy()
        try:
            completed = subprocess.run(
                rendered,
                shell=True,
                cwd=self.project_root,
                env=env,
                text=True,
                encoding="utf-8",
                errors="replace",
                capture_output=True,
                stdin=subprocess.DEVNULL,
                timeout=self.timeout_seconds,
                check=False,
            )
        except subprocess.TimeoutExpired as exc:
            return BuildResult(
                command=rendered,
                returncode=124,
                stdout=exc.stdout or "",
                stderr=f"{label} Timeout nach {self.timeout_seconds}s\n{exc.stderr or ''}",
                artifacts=[],
            )
        return BuildResult(
            command=rendered,
            returncode=completed.returncode,
            stdout=completed.stdout,
            stderr=completed.stderr,
            artifacts=[],
        )
