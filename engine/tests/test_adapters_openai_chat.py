from __future__ import annotations

import json

import pytest

from orchestrated_loop.adapters.base import AdapterUnavailable, BuildResult, Criteria
from orchestrated_loop.adapters.openai_chat import OpenAIChatJudge, OpenAIChatOrchestrator


def test_raises_without_api_key(monkeypatch: pytest.MonkeyPatch) -> None:
    monkeypatch.delenv("OPENAI_API_KEY", raising=False)
    with pytest.raises(AdapterUnavailable, match="OPENAI_API_KEY"):
        OpenAIChatOrchestrator(model="gpt-4o-mini")


def test_orchestrator_parses_json_plan(monkeypatch: pytest.MonkeyPatch) -> None:
    monkeypatch.setenv("OPENAI_API_KEY", "test-key")

    captured: dict = {}

    def fake_post(url, json, headers, timeout):  # noqa: A002
        captured["url"] = url
        captured["json"] = json
        return _FakeResponse({
            "choices": [{
                "message": {
                    "content": json_dumps_plan({
                        "goal": "G",
                        "tasks": ["t1"],
                        "questions": ["q1"],
                        "acceptance_criteria": ["c1"],
                    })
                }
            }]
        })

    monkeypatch.setattr(
        "orchestrated_loop.adapters.openai_chat._http_post",
        fake_post,
    )

    o = OpenAIChatOrchestrator(model="gpt-4o-mini")
    plan = o.plan(task_name="G", iteration=1, previous_score=0.0)
    assert plan.goal == "G"
    assert plan.tasks == ["t1"]


def test_judge_parses_score_payload(monkeypatch: pytest.MonkeyPatch) -> None:
    monkeypatch.setenv("OPENAI_API_KEY", "test-key")

    def fake_post(url, json, headers, timeout):  # noqa: A002
        return _FakeResponse({
            "choices": [{
                "message": {
                    "content": json_dumps_plan({
                        "scores": {"functional": 0.9, "docs": 0.8},
                        "overall": 0.85,
                        "fail_reasons": [],
                        "next_actions": [],
                        "blocking": False,
                    })
                }
            }]
        })

    monkeypatch.setattr(
        "orchestrated_loop.adapters.openai_chat._http_post",
        fake_post,
    )

    j = OpenAIChatJudge(model="gpt-4o-mini")
    build = BuildResult(command="x", returncode=0, stdout="ok", stderr="", artifacts=[])
    score = j.score(Criteria(min_passing_score=0.8), build)
    assert score.overall == 0.85
    assert score.passed is True


class _FakeResponse:
    def __init__(self, payload: dict) -> None:
        self._payload = payload
        self.status_code = 200

    def json(self) -> dict:
        return self._payload

    def raise_for_status(self) -> None:
        return None


def json_dumps_plan(obj: dict) -> str:
    return json.dumps(obj)
