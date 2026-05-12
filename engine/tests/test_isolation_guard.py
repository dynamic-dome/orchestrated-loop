"""Verify the conftest hardguard refuses unsafe RUNDIR overrides."""

from __future__ import annotations

import subprocess
import sys
from pathlib import Path


def test_hardguard_rejects_user_home_path(tmp_path: Path) -> None:
    repo_root = Path(__file__).resolve().parents[2]  # plugin root
    env = {
        "ORCHESTRATED_LOOP_TEST_RUNDIR_OVERRIDE": str(Path.home() / "should-never-be-written"),
        "PYTHONPATH": str(repo_root / "engine" / "src"),
        **__import__("os").environ,
    }
    cmd = [sys.executable, "-m", "pytest", str(repo_root / "engine" / "tests" / "test_state.py"), "-q"]
    completed = subprocess.run(cmd, env=env, capture_output=True, text=True)
    assert completed.returncode != 0
    assert "REFUSING TO RUN" in (completed.stdout + completed.stderr)


def test_hardguard_accepts_tempdir_path(tmp_path: Path) -> None:
    repo_root = Path(__file__).resolve().parents[2]
    env = {
        "ORCHESTRATED_LOOP_TEST_RUNDIR_OVERRIDE": str(tmp_path),
        "PYTHONPATH": str(repo_root / "engine" / "src"),
        **__import__("os").environ,
    }
    cmd = [sys.executable, "-m", "pytest", str(repo_root / "engine" / "tests" / "test_state.py"), "-q"]
    completed = subprocess.run(cmd, env=env, capture_output=True, text=True)
    assert completed.returncode == 0
