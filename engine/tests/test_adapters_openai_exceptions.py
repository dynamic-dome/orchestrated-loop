from __future__ import annotations

import pytest

from orchestrated_loop.adapters.exceptions import LoopChatError
from orchestrated_loop.adapters.openai_chat import OpenAIChatOrchestrator


class _ErrorResponse:
    def __init__(self, status_code: int, body: str) -> None:
        self.status_code = status_code
        self.text = body

    def json(self) -> dict:
        raise ValueError("error response has no json")


def test_auth_error_wrapped_as_loop_chat_error(monkeypatch: pytest.MonkeyPatch) -> None:
    monkeypatch.setenv("OPENAI_API_KEY", "test-key")

    def fake_post(url, json, headers, timeout):  # noqa: A002
        return _ErrorResponse(401, "Unauthorized")

    monkeypatch.setattr(
        "orchestrated_loop.adapters.openai_chat._http_post",
        fake_post,
    )

    o = OpenAIChatOrchestrator(model="gpt-4o-mini")
    with pytest.raises(LoopChatError) as exc_info:
        o.plan(task_name="G", iteration=1, previous_score=0.0)

    assert exc_info.value.status_code == 401
    assert "401" in str(exc_info.value)
    assert exc_info.value.body == "Unauthorized"


def test_rate_limit_wrapped(monkeypatch: pytest.MonkeyPatch) -> None:
    monkeypatch.setenv("OPENAI_API_KEY", "test-key")

    def fake_post(url, json, headers, timeout):  # noqa: A002
        return _ErrorResponse(429, "Too Many Requests")

    monkeypatch.setattr(
        "orchestrated_loop.adapters.openai_chat._http_post",
        fake_post,
    )

    o = OpenAIChatOrchestrator(model="gpt-4o-mini")
    with pytest.raises(LoopChatError) as exc_info:
        o.plan(task_name="G", iteration=1, previous_score=0.0)

    assert exc_info.value.status_code == 429


def test_server_error_wrapped(monkeypatch: pytest.MonkeyPatch) -> None:
    monkeypatch.setenv("OPENAI_API_KEY", "test-key")

    def fake_post(url, json, headers, timeout):  # noqa: A002
        return _ErrorResponse(500, "Internal Server Error")

    monkeypatch.setattr(
        "orchestrated_loop.adapters.openai_chat._http_post",
        fake_post,
    )

    o = OpenAIChatOrchestrator(model="gpt-4o-mini")
    with pytest.raises(LoopChatError) as exc_info:
        o.plan(task_name="G", iteration=1, previous_score=0.0)

    assert exc_info.value.status_code == 500


def test_transport_failure_wrapped_with_cause(monkeypatch: pytest.MonkeyPatch) -> None:
    monkeypatch.setenv("OPENAI_API_KEY", "test-key")

    original = ConnectionError("network unreachable")

    def fake_post(url, json, headers, timeout):  # noqa: A002
        raise original

    monkeypatch.setattr(
        "orchestrated_loop.adapters.openai_chat._http_post",
        fake_post,
    )

    o = OpenAIChatOrchestrator(model="gpt-4o-mini")
    with pytest.raises(LoopChatError) as exc_info:
        o.plan(task_name="G", iteration=1, previous_score=0.0)

    assert exc_info.value.__cause__ is original
    assert exc_info.value.status_code is None


def test_malformed_response_wrapped(monkeypatch: pytest.MonkeyPatch) -> None:
    monkeypatch.setenv("OPENAI_API_KEY", "test-key")

    class _OkButMalformed:
        status_code = 200
        text = "{}"

        def json(self) -> dict:
            return {}

    def fake_post(url, json, headers, timeout):  # noqa: A002
        return _OkButMalformed()

    monkeypatch.setattr(
        "orchestrated_loop.adapters.openai_chat._http_post",
        fake_post,
    )

    o = OpenAIChatOrchestrator(model="gpt-4o-mini")
    with pytest.raises(LoopChatError) as exc_info:
        o.plan(task_name="G", iteration=1, previous_score=0.0)

    assert "malformed" in str(exc_info.value).lower()
