from __future__ import annotations

from orchestrated_loop.adapters.base import BuildResult, Criteria
from orchestrated_loop.adapters.dummy import (
    DummyJudge,
    DummyOrchestrator,
    DummyResearcher,
)


def test_dummy_orchestrator_emits_basic_plan() -> None:
    o = DummyOrchestrator()
    plan = o.plan(task_name="T", iteration=1, previous_score=0.0)
    assert plan.iteration == 1
    assert plan.goal == "T"
    assert plan.tasks
    assert plan.questions
    assert plan.acceptance_criteria


def test_dummy_researcher_returns_offline_answer() -> None:
    r = DummyResearcher()
    res = r.ask(questions=["q1", "q2"], iteration=1)
    assert res.answer
    assert res.error is None


def test_dummy_judge_passes_when_returncode_zero() -> None:
    j = DummyJudge()
    build = BuildResult(command="x", returncode=0, stdout="hello world", stderr="", artifacts=["a"])
    score = j.score(Criteria(required_terms=["hello"], required_artifacts=["a"]), build)
    assert score.passed is True
    assert score.overall >= 0.85


def test_dummy_judge_fails_when_missing_term() -> None:
    j = DummyJudge()
    build = BuildResult(command="x", returncode=0, stdout="hi", stderr="", artifacts=[])
    score = j.score(Criteria(required_terms=["absent_term"]), build)
    assert score.passed is False
    assert any("absent_term" in r for r in score.fail_reasons)
