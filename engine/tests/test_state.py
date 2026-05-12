from __future__ import annotations

import json
from pathlib import Path

from orchestrated_loop.state import StateStore


def test_reset_core_files_creates_all_five(isolated_run_dir: Path) -> None:
    store = StateStore(isolated_run_dir)
    store.reset_core_files(task_name="Test-Task")

    for name in ("PLAN.md", "TODO.md", "LOG.md", "DECISIONS.md", "RESULTS.json"):
        assert (isolated_run_dir / name).is_file(), f"{name} missing"


def test_write_plan_renders_markdown(isolated_run_dir: Path) -> None:
    store = StateStore(isolated_run_dir)
    store.reset_core_files(task_name="T")
    store.write_plan({
        "goal": "Goal X",
        "iteration": 1,
        "tasks": ["a", "b"],
        "questions": ["q1"],
        "acceptance_criteria": ["c1"],
    })
    content = (isolated_run_dir / "PLAN.md").read_text(encoding="utf-8")
    assert "Goal X" in content
    assert "Iteration 1" in content
    assert "- a" in content
    assert "q1" in content


def test_append_log_is_append_only(isolated_run_dir: Path) -> None:
    store = StateStore(isolated_run_dir)
    store.reset_core_files(task_name="T")
    store.append_log("Section A", "body A")
    store.append_log("Section B", "body B")
    content = (isolated_run_dir / "LOG.md").read_text(encoding="utf-8")
    assert content.index("Section A") < content.index("Section B")


def test_results_roundtrip_json(isolated_run_dir: Path) -> None:
    store = StateStore(isolated_run_dir)
    store.reset_core_files(task_name="T")
    store.write_results({"iterations": [{"i": 1}]})
    data = json.loads((isolated_run_dir / "RESULTS.json").read_text(encoding="utf-8"))
    assert data["iterations"][0]["i"] == 1
