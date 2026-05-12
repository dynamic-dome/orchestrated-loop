from __future__ import annotations

import sys
from pathlib import Path

import pytest

from orchestrated_loop.adapters.base import Plan, ResearchResult
from orchestrated_loop.adapters.local_shell import LocalShellBuilder


def test_runs_echo_and_returns_zero(tmp_path: Path) -> None:
    builder = LocalShellBuilder(
        command=f"{sys.executable} -c \"print('hello')\"",
        timeout_seconds=30,
        project_root=tmp_path,
    )
    plan = Plan(goal="t", iteration=1)
    result = builder.run(plan, ResearchResult(answer=""))
    assert result.returncode == 0
    assert "hello" in result.stdout


def test_nonzero_returncode_is_reported(tmp_path: Path) -> None:
    builder = LocalShellBuilder(
        command=f"{sys.executable} -c \"import sys; sys.exit(7)\"",
        timeout_seconds=30,
        project_root=tmp_path,
    )
    plan = Plan(goal="t", iteration=1)
    result = builder.run(plan, ResearchResult(answer=""))
    assert result.returncode == 7


def test_timeout_returns_124(tmp_path: Path) -> None:
    builder = LocalShellBuilder(
        command=f"{sys.executable} -c \"import time; time.sleep(5)\"",
        timeout_seconds=1,
        project_root=tmp_path,
    )
    plan = Plan(goal="t", iteration=1)
    result = builder.run(plan, ResearchResult(answer=""))
    assert result.returncode == 124
    assert "Timeout" in result.stderr
