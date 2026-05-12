"""Adapter protocols and shared data classes for the four roles."""

from __future__ import annotations

from dataclasses import dataclass, field
from pathlib import Path
from typing import Any, Protocol, runtime_checkable


@dataclass
class Plan:
    goal: str
    iteration: int
    tasks: list[str] = field(default_factory=list)
    questions: list[str] = field(default_factory=list)
    acceptance_criteria: list[str] = field(default_factory=list)
    previous_score: float = 0.0


@dataclass
class ResearchResult:
    answer: str
    citations: list[dict[str, str]] = field(default_factory=list)
    open_questions: list[str] = field(default_factory=list)
    handoff_file: Path | None = None
    error: str | None = None


@dataclass
class BuildResult:
    command: str
    returncode: int
    stdout: str
    stderr: str
    artifacts: list[str] = field(default_factory=list)
    error: str | None = None


@dataclass
class JudgeScore:
    scores: dict[str, float]
    overall: float
    fail_reasons: list[str] = field(default_factory=list)
    next_actions: list[str] = field(default_factory=list)
    passed: bool = False

    def to_dict(self) -> dict[str, Any]:
        return {
            "scores": self.scores,
            "overall": self.overall,
            "fail_reasons": self.fail_reasons,
            "next_actions": self.next_actions,
            "passed": self.passed,
        }


@dataclass
class Criteria:
    required_terms: list[str] = field(default_factory=list)
    required_artifacts: list[str] = field(default_factory=list)
    min_passing_score: float = 0.85


class AdapterUnavailable(RuntimeError):
    """Raised when an adapter cannot initialize (missing tool, missing key)."""


@runtime_checkable
class Orchestrator(Protocol):
    def plan(self, task_name: str, iteration: int, previous_score: float) -> Plan: ...


@runtime_checkable
class Researcher(Protocol):
    def ask(self, questions: list[str], iteration: int) -> ResearchResult: ...


@runtime_checkable
class Builder(Protocol):
    def run(self, plan: Plan, research: ResearchResult) -> BuildResult: ...


@runtime_checkable
class Judge(Protocol):
    def score(self, criteria: Criteria, build: BuildResult) -> JudgeScore: ...
