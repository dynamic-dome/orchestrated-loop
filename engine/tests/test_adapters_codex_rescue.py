from __future__ import annotations

import json
import subprocess
from pathlib import Path

import pytest

from orchestrated_loop.adapters.base import AdapterUnavailable, Plan, ResearchResult
from orchestrated_loop.adapters.codex_rescue import CodexRescueBuilder


def test_raises_when_codex_missing(monkeypatch: pytest.MonkeyPatch, tmp_path: Path) -> None:
    monkeypatch.setattr("shutil.which", lambda name: None)
    with pytest.raises(AdapterUnavailable, match="codex"):
        CodexRescueBuilder(handoff_dir=tmp_path / "handoff")


def test_run_writes_task_and_reads_result(
    monkeypatch: pytest.MonkeyPatch, tmp_path: Path
) -> None:
    monkeypatch.setattr("shutil.which", lambda name: "/usr/local/bin/codex")

    handoff = tmp_path / "handoff"

    def fake_run(cmd, **kwargs):
        # codex writes the result file
        out_idx = cmd.index("--output") + 1
        out_path = Path(cmd[out_idx])
        out_path.parent.mkdir(parents=True, exist_ok=True)
        out_path.write_text(json.dumps({
            "changes": [{"file": "foo.py", "diff": "..."}],
            "logs": "ok",
            "test_results": {"passed": 1, "failed": 0, "details": []},
            "artifacts": ["foo.py"],
        }), encoding="utf-8")
        return subprocess.CompletedProcess(cmd, 0, stdout="", stderr="")

    monkeypatch.setattr(subprocess, "run", fake_run)

    builder = CodexRescueBuilder(handoff_dir=handoff)
    plan = Plan(goal="g", iteration=1, tasks=["do a thing"])
    result = builder.run(plan, ResearchResult(answer=""))

    assert result.returncode == 0
    assert "foo.py" in result.artifacts
    task_file = next(handoff.glob("**/codex-task.md"))
    assert task_file.read_text(encoding="utf-8")


def test_run_returns_nonzero_when_codex_fails(
    monkeypatch: pytest.MonkeyPatch, tmp_path: Path
) -> None:
    monkeypatch.setattr("shutil.which", lambda name: "/usr/local/bin/codex")

    def fake_run(cmd, **kwargs):
        return subprocess.CompletedProcess(cmd, 5, stdout="", stderr="boom")

    monkeypatch.setattr(subprocess, "run", fake_run)

    builder = CodexRescueBuilder(handoff_dir=tmp_path / "handoff")
    plan = Plan(goal="g", iteration=1, tasks=["x"])
    result = builder.run(plan, ResearchResult(answer=""))
    assert result.returncode == 5
    assert "boom" in result.stderr
