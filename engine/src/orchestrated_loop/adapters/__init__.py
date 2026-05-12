"""Adapter registry."""

from __future__ import annotations

from typing import Callable

from orchestrated_loop.adapters.codex_rescue import CodexRescueBuilder
from orchestrated_loop.adapters.dummy import DummyJudge, DummyOrchestrator, DummyResearcher
from orchestrated_loop.adapters.local_shell import LocalShellBuilder
from orchestrated_loop.adapters.notebooklm_cli import NotebookLMCliResearcher
from orchestrated_loop.adapters.openai_chat import OpenAIChatJudge, OpenAIChatOrchestrator


ORCHESTRATORS: dict[str, Callable] = {
    "dummy": DummyOrchestrator,
    "openai_chat": OpenAIChatOrchestrator,
}

RESEARCHERS: dict[str, Callable] = {
    "dummy": DummyResearcher,
    "notebooklm_cli": NotebookLMCliResearcher,
}

BUILDERS: dict[str, Callable] = {
    "local_shell": LocalShellBuilder,
    "codex_rescue": CodexRescueBuilder,
}

JUDGES: dict[str, Callable] = {
    "dummy": DummyJudge,
    "openai_chat": OpenAIChatJudge,
}
