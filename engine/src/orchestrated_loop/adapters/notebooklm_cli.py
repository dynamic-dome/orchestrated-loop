"""NotebookLM CLI Researcher: shells out to the local `notebooklm` binary."""

from __future__ import annotations

import json
import shutil
import subprocess
from concurrent.futures import ThreadPoolExecutor

from orchestrated_loop.adapters.base import AdapterUnavailable, ResearchResult


class NotebookLMCliResearcher:
    def __init__(self, notebook_id: str, language: str | None = None, timeout_seconds: int = 120) -> None:
        binary = shutil.which("notebooklm")
        if binary is None:
            raise AdapterUnavailable(
                "notebooklm CLI not on PATH. Install or login via `notebooklm login`."
            )
        self._binary = binary
        self._notebook_id = notebook_id
        self._language = language
        self._timeout = timeout_seconds
        self._used = False

    def _ensure_used(self) -> str | None:
        if self._used:
            return None
        cmd = [self._binary, "use", self._notebook_id, "--json"]
        completed = subprocess.run(
            cmd,
            text=True,
            encoding="utf-8",
            errors="replace",
            capture_output=True,
            stdin=subprocess.DEVNULL,
            timeout=self._timeout,
            check=False,
        )
        if completed.returncode != 0:
            return f"`notebooklm use` failed: {completed.stderr.strip() or completed.stdout.strip()}"
        self._used = True
        return None

    def _ask_one(self, question: str) -> dict:
        cmd = [self._binary, "ask", "--json", question]
        if self._language:
            cmd += ["--language", self._language]
        completed = subprocess.run(
            cmd,
            text=True,
            encoding="utf-8",
            errors="replace",
            capture_output=True,
            stdin=subprocess.DEVNULL,
            timeout=self._timeout,
            check=False,
        )
        if completed.returncode != 0:
            return {"error": completed.stderr.strip() or completed.stdout.strip(), "question": question}
        try:
            return json.loads(completed.stdout)
        except json.JSONDecodeError as exc:
            return {"error": f"non-JSON stdout: {exc}", "question": question}

    def ask(self, questions: list[str], iteration: int) -> ResearchResult:
        err = self._ensure_used()
        if err:
            return ResearchResult(answer="", error=err)

        with ThreadPoolExecutor(max_workers=min(4, max(1, len(questions)))) as pool:
            answers = list(pool.map(self._ask_one, questions))

        errors = [a["error"] for a in answers if "error" in a]
        if errors:
            return ResearchResult(answer="", error="; ".join(errors))

        combined = "\n\n".join(f"Q: {q}\nA: {a.get('answer', '')}" for q, a in zip(questions, answers))
        citations: list[dict[str, str]] = []
        for a in answers:
            citations.extend(a.get("citations", []) or [])

        return ResearchResult(answer=combined, citations=citations)
