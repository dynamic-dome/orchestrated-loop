"""Test isolation hardguard: refuse to run if RUNDIR points outside tempdir."""

from __future__ import annotations

import os
import sys
import tempfile
from pathlib import Path

import pytest


_TEMP_ROOT = Path(tempfile.gettempdir()).resolve()


def _is_inside_tempdir(p: Path) -> bool:
    try:
        p.resolve().relative_to(_TEMP_ROOT)
        return True
    except ValueError:
        return False


@pytest.fixture
def isolated_run_dir(tmp_path: Path) -> Path:
    run_dir = tmp_path / "run-test"
    run_dir.mkdir()
    if not _is_inside_tempdir(run_dir):
        raise RuntimeError(
            f"REFUSING TO RUN: isolated_run_dir resolved to {run_dir}, "
            f"which is not under {_TEMP_ROOT}"
        )
    return run_dir


def pytest_configure(config: pytest.Config) -> None:
    override = os.environ.get("ORCHESTRATED_LOOP_TEST_RUNDIR_OVERRIDE")
    if override:
        override_path = Path(override).resolve()
        if not _is_inside_tempdir(override_path):
            print(
                f"[conftest] REFUSING TO RUN: "
                f"ORCHESTRATED_LOOP_TEST_RUNDIR_OVERRIDE={override} "
                f"is not under {_TEMP_ROOT}",
                file=sys.stderr,
            )
            raise SystemExit(2)
