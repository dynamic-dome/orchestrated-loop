"""Deterministic offline adapters for Orchestrator, Researcher, and Judge."""

from __future__ import annotations

from orchestrated_loop.adapters.base import (
    BuildResult,
    Criteria,
    JudgeScore,
    Plan,
    ResearchResult,
)


class DummyOrchestrator:
    def plan(self, task_name: str, iteration: int, previous_score: float) -> Plan:
        return Plan(
            goal=task_name,
            iteration=iteration,
            previous_score=previous_score,
            tasks=[
                "Lese vorhandenen State.",
                "Führe Builder mit aktuellem Kommando aus.",
                "Bewerte Ergebnis gegen Akzeptanzkriterien.",
            ],
            questions=[
                "Welche Akzeptanzkriterien sind in dieser Iteration kritisch?",
                "Welche Quellenhinweise würden den Builder verbessern?",
            ],
            acceptance_criteria=[
                "Builder-Returncode 0",
                "Required terms vollständig",
                "Required artifacts existieren",
            ],
        )


class DummyResearcher:
    def ask(self, questions: list[str], iteration: int) -> ResearchResult:
        return ResearchResult(
            answer=(
                f"Offline-Hinweis für Iteration {iteration}: "
                f"{len(questions)} Frage(n) erkannt. Keine externe Quelle angefragt."
            ),
            citations=[],
            open_questions=questions,
        )


class DummyJudge:
    def score(self, criteria: Criteria, build: BuildResult) -> JudgeScore:
        fail_reasons: list[str] = []
        scores: dict[str, float] = {}

        scores["build"] = 1.0 if build.returncode == 0 else 0.0
        if build.returncode != 0:
            fail_reasons.append(f"Builder-Returncode {build.returncode}")

        haystack = (build.stdout + "\n" + build.stderr).lower()
        missing_terms = [t for t in criteria.required_terms if t.lower() not in haystack]
        scores["terms"] = 1.0 if not missing_terms else 1.0 - (len(missing_terms) / max(1, len(criteria.required_terms)))
        for t in missing_terms:
            fail_reasons.append(f"Required term fehlt: {t}")

        missing_artifacts = [a for a in criteria.required_artifacts if a not in build.artifacts]
        scores["artifacts"] = 1.0 if not missing_artifacts else 1.0 - (len(missing_artifacts) / max(1, len(criteria.required_artifacts)))
        for a in missing_artifacts:
            fail_reasons.append(f"Required artifact fehlt: {a}")

        overall = sum(scores.values()) / len(scores)
        passed = overall >= criteria.min_passing_score and not fail_reasons

        return JudgeScore(
            scores=scores,
            overall=round(overall, 3),
            fail_reasons=fail_reasons,
            next_actions=fail_reasons or ["Score erreicht. Loop kann enden."],
            passed=passed,
        )
