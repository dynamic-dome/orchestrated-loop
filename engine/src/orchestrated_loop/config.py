"""Loop configuration loaded from TOML."""

from __future__ import annotations

import sys
from dataclasses import dataclass, field
from pathlib import Path
from typing import Any

if sys.version_info >= (3, 11):
    import tomllib
else:
    import tomli as tomllib


class ConfigError(ValueError):
    """Config file is missing required fields or malformed."""


REQUIRED_ROLES = ("orchestrator", "researcher", "builder", "judge")


@dataclass
class LoopConfig:
    config_path: Path
    project_root: Path
    task_name: str
    max_iterations: int
    target_score: float
    roles: dict[str, str]
    adapter_options: dict[str, dict[str, Any]]
    judge_options: dict[str, Any] = field(default_factory=dict)


def load_config(path: Path, project_root: Path) -> LoopConfig:
    raw = tomllib.loads(Path(path).read_text(encoding="utf-8"))

    loop = raw.get("loop")
    if not isinstance(loop, dict):
        raise ConfigError("Section [loop] is required.")
    for key in ("task_name", "max_iterations", "target_score"):
        if key not in loop:
            raise ConfigError(f"[loop].{key} is required.")

    roles = raw.get("roles") or {}
    for role in REQUIRED_ROLES:
        if role not in roles:
            raise ConfigError(f"[roles].{role} is required.")

    adapter_opts = raw.get("adapter") or {}
    if not isinstance(adapter_opts, dict):
        raise ConfigError("Section [adapter] must be a table of tables.")

    return LoopConfig(
        config_path=Path(path),
        project_root=Path(project_root),
        task_name=str(loop["task_name"]),
        max_iterations=int(loop["max_iterations"]),
        target_score=float(loop["target_score"]),
        roles={k: str(v) for k, v in roles.items()},
        adapter_options=dict(adapter_opts),
        judge_options=dict(raw.get("judge") or {}),
    )
