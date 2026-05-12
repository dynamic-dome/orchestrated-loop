from __future__ import annotations

import json
import subprocess

import pytest

from orchestrated_loop.adapters.base import AdapterUnavailable
from orchestrated_loop.adapters.notebooklm_cli import NotebookLMCliResearcher


def test_raises_when_cli_missing(monkeypatch: pytest.MonkeyPatch) -> None:
    monkeypatch.setattr("shutil.which", lambda name: None)
    with pytest.raises(AdapterUnavailable, match="notebooklm"):
        NotebookLMCliResearcher(notebook_id="abc123")


def test_ask_invokes_notebooklm_ask_per_question(monkeypatch: pytest.MonkeyPatch) -> None:
    monkeypatch.setattr("shutil.which", lambda name: "/usr/local/bin/notebooklm")

    calls: list[list[str]] = []

    def fake_run(cmd, **kwargs):
        calls.append(cmd)
        if "use" in cmd:
            return subprocess.CompletedProcess(cmd, 0, stdout="{\"ok\": true}", stderr="")
        if "ask" in cmd:
            payload = json.dumps({
                "answer": "Antwort auf Frage",
                "citations": [{"source": "s1", "loc": "p.1"}],
            })
            return subprocess.CompletedProcess(cmd, 0, stdout=payload, stderr="")
        return subprocess.CompletedProcess(cmd, 0, stdout="", stderr="")

    monkeypatch.setattr(subprocess, "run", fake_run)

    r = NotebookLMCliResearcher(notebook_id="abc123")
    result = r.ask(questions=["q1", "q2"], iteration=1)

    use_calls = [c for c in calls if "use" in c]
    ask_calls = [c for c in calls if "ask" in c]
    assert len(use_calls) == 1
    assert len(ask_calls) == 2
    assert result.answer
    assert result.citations
    assert result.error is None


def test_ask_returns_error_when_cli_fails(monkeypatch: pytest.MonkeyPatch) -> None:
    monkeypatch.setattr("shutil.which", lambda name: "/usr/local/bin/notebooklm")

    def fake_run(cmd, **kwargs):
        if "use" in cmd:
            return subprocess.CompletedProcess(cmd, 0, stdout="{}", stderr="")
        return subprocess.CompletedProcess(cmd, 2, stdout="", stderr="session expired")

    monkeypatch.setattr(subprocess, "run", fake_run)

    r = NotebookLMCliResearcher(notebook_id="abc123")
    result = r.ask(questions=["q1"], iteration=1)
    assert result.error is not None
    assert "session expired" in result.error
