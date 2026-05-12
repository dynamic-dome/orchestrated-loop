from __future__ import annotations

import textwrap
from pathlib import Path

from orchestrated_loop.cli import main


def test_cli_runs_and_writes_results(tmp_path: Path, capsys, monkeypatch) -> None:
    cfg_path = tmp_path / "loop.toml"
    cfg_path.write_text(textwrap.dedent("""
        [loop]
        task_name = "CLI-Smoke"
        max_iterations = 1
        target_score = 0.5
        [roles]
        orchestrator = "dummy"
        researcher = "dummy"
        builder = "local_shell"
        judge = "dummy"
        [adapter.local_shell]
        command = "{python} -c \\"print('cli-ok')\\""
        timeout_seconds = 30
        [judge]
        required_terms = ["cli-ok"]
        min_passing_score = 0.5
    """), encoding="utf-8")

    run_dir = tmp_path / "run"
    run_dir.mkdir()

    exit_code = main([
        "run",
        "--config", str(cfg_path),
        "--run-dir", str(run_dir),
        "--project-root", str(tmp_path),
    ])
    assert exit_code == 0
    assert (run_dir / "RESULTS.json").is_file()


def test_cli_exits_2_on_missing_config(tmp_path: Path) -> None:
    exit_code = main([
        "run",
        "--config", str(tmp_path / "does-not-exist.toml"),
        "--run-dir", str(tmp_path),
        "--project-root", str(tmp_path),
    ])
    assert exit_code == 2
