"""Local verification: runs all engine tests, then the demo. Exit 0 on success."""

from __future__ import annotations

import subprocess
import sys
from pathlib import Path


def main() -> int:
    plugin_root = Path(__file__).resolve().parents[2]
    env = {
        **__import__("os").environ,
        "PYTHONPATH": str(plugin_root / "engine" / "src"),
    }
    print("[verify] pytest ...")
    r1 = subprocess.run(
        [sys.executable, "-m", "pytest", str(plugin_root / "engine" / "tests"), "-q"],
        env=env,
        stdin=subprocess.DEVNULL,
    )
    if r1.returncode != 0:
        return r1.returncode

    print("[verify] demo ...")
    r2 = subprocess.run(
        [sys.executable, str(plugin_root / "engine" / "scripts" / "run_demo.py")],
        env=env,
        stdin=subprocess.DEVNULL,
    )
    return r2.returncode


if __name__ == "__main__":
    raise SystemExit(main())
