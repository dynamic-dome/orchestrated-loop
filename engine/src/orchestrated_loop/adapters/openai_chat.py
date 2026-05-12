"""OpenAI Chat Completions adapter for Orchestrator and Judge roles."""

from __future__ import annotations

import json
import os
from pathlib import Path
from typing import Any

from orchestrated_loop.adapters.base import (
    AdapterUnavailable,
    BuildResult,
    Criteria,
    JudgeScore,
    Plan,
)


CHAT_URL = "https://api.openai.com/v1/chat/completions"


def _http_post(url: str, json: dict, headers: dict, timeout: int):  # noqa: A002
    try:
        import httpx
    except ImportError as exc:
        raise AdapterUnavailable(
            "httpx not installed. Run `pip install httpx` or install extras."
        ) from exc
    return httpx.post(url, json=json, headers=headers, timeout=timeout)


def _load_prompt(prompt_name: str) -> str:
    here = Path(__file__).resolve().parent.parent.parent.parent  # plugin root
    candidate = here / "skills" / "orchestrated-loop" / "references" / "role-prompts" / f"{prompt_name}.md"
    if candidate.exists():
        return candidate.read_text(encoding="utf-8")
    return ""


def _require_key() -> str:
    key = os.environ.get("OPENAI_API_KEY")
    if not key:
        raise AdapterUnavailable("OPENAI_API_KEY not set in environment.")
    return key


def _chat(model: str, system: str, user: str, api_key: str, timeout: int = 60) -> str:
    response = _http_post(
        CHAT_URL,
        json={
            "model": model,
            "messages": [
                {"role": "system", "content": system},
                {"role": "user", "content": user},
            ],
            "response_format": {"type": "json_object"},
            "temperature": 0.2,
        },
        headers={"Authorization": f"Bearer {api_key}", "Content-Type": "application/json"},
        timeout=timeout,
    )
    response.raise_for_status()
    data = response.json()
    return data["choices"][0]["message"]["content"]


class OpenAIChatOrchestrator:
    def __init__(self, model: str = "gpt-4o-mini") -> None:
        self._api_key = _require_key()
        self._model = model
        self._system = _load_prompt("orchestrator") or "You are the Orchestrator. Reply JSON."

    def plan(self, task_name: str, iteration: int, previous_score: float) -> Plan:
        user = json.dumps({
            "task_name": task_name,
            "iteration": iteration,
            "previous_score": previous_score,
        })
        raw = _chat(self._model, self._system, user, self._api_key)
        data: dict[str, Any] = json.loads(raw)
        return Plan(
            goal=str(data.get("goal", task_name)),
            iteration=iteration,
            previous_score=previous_score,
            tasks=list(data.get("tasks", [])),
            questions=list(data.get("questions", [])),
            acceptance_criteria=list(data.get("acceptance_criteria", [])),
        )


class OpenAIChatJudge:
    def __init__(self, model: str = "gpt-4o-mini") -> None:
        self._api_key = _require_key()
        self._model = model
        self._system = _load_prompt("judge") or "You are the Judge. Reply JSON."

    def score(self, criteria: Criteria, build: BuildResult) -> JudgeScore:
        user = json.dumps({
            "criteria": {
                "required_terms": criteria.required_terms,
                "required_artifacts": criteria.required_artifacts,
                "min_passing_score": criteria.min_passing_score,
            },
            "build": {
                "returncode": build.returncode,
                "stdout_tail": build.stdout[-2000:],
                "stderr_tail": build.stderr[-2000:],
                "artifacts": build.artifacts,
            },
        })
        raw = _chat(self._model, self._system, user, self._api_key)
        data: dict[str, Any] = json.loads(raw)
        overall = float(data.get("overall", 0.0))
        fail_reasons = list(data.get("fail_reasons", []))
        passed = overall >= criteria.min_passing_score and not data.get("blocking", False)
        return JudgeScore(
            scores=dict(data.get("scores", {})),
            overall=overall,
            fail_reasons=fail_reasons,
            next_actions=list(data.get("next_actions", [])),
            passed=passed,
        )
