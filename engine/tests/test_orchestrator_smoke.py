from __future__ import annotations

import json
import textwrap
from pathlib import Path

from orchestrated_loop.config import load_config
from orchestrated_loop.orchestrator import run_loop


def test_smoke_loop_writes_all_state_files(tmp_path: Path) -> None:
    cfg_path = tmp_path / "loop.toml"
    cfg_path.write_text(textwrap.dedent("""
        [loop]
        task_name = "Smoke"
        max_iterations = 1
        target_score = 0.5
        [roles]
        orchestrator = "dummy"
        researcher = "dummy"
        builder = "local_shell"
        judge = "dummy"
        [adapter.local_shell]
        command = "{python} -c \\"print('hello-loop')\\""
        timeout_seconds = 30
        [judge]
        required_terms = ["hello-loop"]
        required_artifacts = []
        min_passing_score = 0.5
    """), encoding="utf-8")

    cfg = load_config(cfg_path, project_root=tmp_path)
    run_dir = tmp_path / "run-001"
    run_dir.mkdir()

    results = run_loop(cfg, run_dir=run_dir)

    for name in ("PLAN.md", "TODO.md", "LOG.md", "DECISIONS.md", "RESULTS.json"):
        assert (run_dir / name).is_file(), f"{name} missing"

    data = json.loads((run_dir / "RESULTS.json").read_text(encoding="utf-8"))
    assert data["iterations"]
    assert data["latest_score"]["passed"] is True


def test_loop_breaks_on_builder_failure(tmp_path: Path) -> None:
    cfg_path = tmp_path / "loop.toml"
    cfg_path.write_text(textwrap.dedent("""
        [loop]
        task_name = "Fail"
        max_iterations = 3
        target_score = 0.99
        [roles]
        orchestrator = "dummy"
        researcher = "dummy"
        builder = "local_shell"
        judge = "dummy"
        [adapter.local_shell]
        command = "{python} -c \\"import sys; sys.exit(3)\\""
        timeout_seconds = 30
    """), encoding="utf-8")

    cfg = load_config(cfg_path, project_root=tmp_path)
    run_dir = tmp_path / "run-002"
    run_dir.mkdir()
    results = run_loop(cfg, run_dir=run_dir)
    assert len(results["iterations"]) == 1
    assert results["iterations"][0]["build"]["returncode"] == 3
