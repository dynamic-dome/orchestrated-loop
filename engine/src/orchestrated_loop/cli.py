"""Command-line interface: `python -m orchestrated_loop run --config ...`."""

from __future__ import annotations

import argparse
import sys
from pathlib import Path

from orchestrated_loop.adapters.base import AdapterUnavailable
from orchestrated_loop.config import ConfigError, load_config
from orchestrated_loop.orchestrator import run_loop


def main(argv: list[str] | None = None) -> int:
    parser = argparse.ArgumentParser(prog="orchestrated-loop")
    sub = parser.add_subparsers(dest="cmd", required=True)

    run_p = sub.add_parser("run", help="Run a single loop.")
    run_p.add_argument("--config", required=True, type=Path)
    run_p.add_argument("--run-dir", required=True, type=Path)
    run_p.add_argument("--project-root", required=True, type=Path)
    run_p.add_argument("--task", default=None, help="Overrides [loop].task_name.")

    args = parser.parse_args(argv)

    if args.cmd != "run":
        parser.print_help()
        return 1

    if not args.config.is_file():
        print(f"Config nicht gefunden: {args.config}", file=sys.stderr)
        return 2

    try:
        cfg = load_config(args.config, project_root=args.project_root)
    except ConfigError as exc:
        print(f"Config-Fehler: {exc}", file=sys.stderr)
        return 2

    if args.task:
        cfg.task_name = args.task

    args.run_dir.mkdir(parents=True, exist_ok=True)

    try:
        run_loop(cfg, run_dir=args.run_dir)
    except AdapterUnavailable as exc:
        print(f"Adapter nicht verfügbar: {exc}", file=sys.stderr)
        return 3
    except Exception as exc:  # noqa: BLE001
        import traceback
        traceback.print_exc()
        print(f"Unerwartete Exception: {exc}", file=sys.stderr)
        return 3
    return 0
