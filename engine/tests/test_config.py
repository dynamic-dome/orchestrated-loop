from __future__ import annotations

import textwrap
from pathlib import Path

import pytest

from orchestrated_loop.config import ConfigError, load_config


def _write(tmp_path: Path, body: str) -> Path:
    p = tmp_path / "loop.toml"
    p.write_text(textwrap.dedent(body), encoding="utf-8")
    return p


def test_load_minimal_config(tmp_path: Path) -> None:
    cfg_path = _write(tmp_path, """
        [loop]
        task_name = "Minimal"
        max_iterations = 2
        target_score = 0.5
        [roles]
        orchestrator = "dummy"
        researcher = "dummy"
        builder = "dummy"
        judge = "dummy"
    """)
    cfg = load_config(cfg_path, project_root=tmp_path)
    assert cfg.task_name == "Minimal"
    assert cfg.max_iterations == 2
    assert cfg.target_score == 0.5
    assert cfg.roles["builder"] == "dummy"


def test_missing_loop_section_raises(tmp_path: Path) -> None:
    cfg_path = _write(tmp_path, "[roles]\nbuilder = \"dummy\"\n")
    with pytest.raises(ConfigError, match="loop"):
        load_config(cfg_path, project_root=tmp_path)


def test_missing_role_raises(tmp_path: Path) -> None:
    cfg_path = _write(tmp_path, """
        [loop]
        task_name = "X"
        max_iterations = 1
        target_score = 0.5
        [roles]
        orchestrator = "dummy"
        researcher = "dummy"
        # missing builder + judge
    """)
    with pytest.raises(ConfigError, match="builder"):
        load_config(cfg_path, project_root=tmp_path)


def test_adapter_section_passthrough(tmp_path: Path) -> None:
    cfg_path = _write(tmp_path, """
        [loop]
        task_name = "X"
        max_iterations = 1
        target_score = 0.5
        [roles]
        orchestrator = "dummy"
        researcher = "dummy"
        builder = "local_shell"
        judge = "dummy"
        [adapter.local_shell]
        command = "echo hi"
        timeout_seconds = 30
    """)
    cfg = load_config(cfg_path, project_root=tmp_path)
    assert cfg.adapter_options["local_shell"]["command"] == "echo hi"
    assert cfg.adapter_options["local_shell"]["timeout_seconds"] == 30
