"""Offline demo runner: runs the glossary demo end-to-end against a tempdir-free local run dir."""

from __future__ import annotations

import shutil
import sys
from pathlib import Path

from orchestrated_loop.cli import main


def run() -> int:
    plugin_root = Path(__file__).resolve().parents[2]
    cfg = plugin_root / "engine" / "examples" / "glossary_demo" / "config" / "loop.dryrun.toml"
    run_dir = plugin_root / ".loop" / "demo-run"
    if run_dir.exists():
        shutil.rmtree(run_dir)
    return main([
        "run",
        "--config", str(cfg),
        "--run-dir", str(run_dir),
        "--project-root", str(plugin_root),
    ])


if __name__ == "__main__":
    raise SystemExit(run())
