"""Loop driver: instantiates adapters from config and iterates."""

from __future__ import annotations

from pathlib import Path
from typing import Any

from orchestrated_loop.adapters import (
    BUILDERS,
    JUDGES,
    ORCHESTRATORS,
    RESEARCHERS,
)
from orchestrated_loop.adapters.base import (
    AdapterUnavailable,
    Builder,
    Criteria,
    Judge,
    Orchestrator,
    Researcher,
)
from orchestrated_loop.config import LoopConfig
from orchestrated_loop.state import StateStore, utc_now


def run_loop(config: LoopConfig, run_dir: Path) -> dict[str, Any]:
    store = StateStore(run_dir)
    store.reset_core_files(config.task_name)

    orchestrator = _build_role(config, "orchestrator", ORCHESTRATORS)
    researcher = _build_role(config, "researcher", RESEARCHERS)
    builder = _build_builder(config)
    judge = _build_role(config, "judge", JUDGES)

    criteria = Criteria(
        required_terms=list(config.judge_options.get("required_terms", [])),
        required_artifacts=list(config.judge_options.get("required_artifacts", [])),
        min_passing_score=float(config.judge_options.get("min_passing_score", config.target_score)),
    )

    results: dict[str, Any] = store.load_results()
    results["config"] = {
        "config_path": str(config.config_path),
        "project_root": str(config.project_root),
        "roles": config.roles,
        "max_iterations": config.max_iterations,
        "target_score": config.target_score,
    }

    final_score = 0.0
    for iteration in range(1, config.max_iterations + 1):
        plan = orchestrator.plan(config.task_name, iteration, final_score)
        store.write_plan({
            "goal": plan.goal,
            "iteration": plan.iteration,
            "tasks": plan.tasks,
            "questions": plan.questions,
            "acceptance_criteria": plan.acceptance_criteria,
        })
        store.write_todo(plan.tasks)

        research = researcher.ask(plan.questions, iteration)
        build = builder.run(plan, research)
        score = judge.score(criteria, build)
        final_score = score.overall

        iteration_result = {
            "iteration": iteration,
            "timestamp": utc_now(),
            "plan": {
                "goal": plan.goal,
                "tasks": plan.tasks,
                "questions": plan.questions,
                "acceptance_criteria": plan.acceptance_criteria,
            },
            "research": {
                "answer": research.answer,
                "citations": research.citations,
                "open_questions": research.open_questions,
                "error": research.error,
            },
            "build": {
                "command": build.command,
                "returncode": build.returncode,
                "stdout_tail": build.stdout[-4000:],
                "stderr_tail": build.stderr[-4000:],
                "artifacts": build.artifacts,
            },
            "judge": score.to_dict(),
        }
        results.setdefault("iterations", []).append(iteration_result)
        results["latest_score"] = score.to_dict()
        store.write_results(results)

        store.append_log(f"Iteration {iteration}", _render_iteration_log(iteration_result))
        store.append_decision(_render_decision(score.overall, score.passed, score.next_actions))

        if build.returncode != 0:
            store.append_log("Abbruch", "Builder schlug fehl. Siehe RESULTS.json.")
            break
        if score.passed:
            store.append_log("Abbruch", f"Quality Gate erreicht: overall={score.overall}")
            break

    return results


def _build_role(config: LoopConfig, role: str, registry: dict[str, Any]):
    name = config.roles[role]
    if name not in registry:
        raise AdapterUnavailable(f"Adapter '{name}' not registered for role '{role}'.")
    options = dict(config.adapter_options.get(name, {}))
    return registry[name](**options)


def _build_builder(config: LoopConfig) -> Builder:
    name = config.roles["builder"]
    if name not in BUILDERS:
        raise AdapterUnavailable(f"Builder adapter '{name}' not registered.")
    options = dict(config.adapter_options.get(name, {}))
    if name == "local_shell":
        options.setdefault("project_root", config.project_root)
        # Do NOT pre-substitute {python} here — LocalShellBuilder._exec handles it
        # with platform-aware quoting (Windows: double-quotes, POSIX: shlex.quote).
        return BUILDERS[name](**options)
    if name == "codex_rescue":
        handoff = options.pop("handoff_dir", None)
        if handoff is None:
            handoff = config.project_root / ".loop" / "handoff"
        options["handoff_dir"] = handoff
        return BUILDERS[name](**options)
    return BUILDERS[name](**options)


def _render_iteration_log(iteration_result: dict[str, Any]) -> str:
    judge = iteration_result.get("judge", {})
    build = iteration_result.get("build", {})
    return (
        f"Build-Returncode: {build.get('returncode')}\n\n"
        f"Judge overall: {judge.get('overall')}, passed: {judge.get('passed')}\n\n"
        f"Fail-Reasons: {judge.get('fail_reasons') or 'none'}\n\n"
        "Details in RESULTS.json."
    )


def _render_decision(score: float, passed: bool, next_actions: list[str]) -> str:
    status = "erreicht" if passed else "nicht erreicht"
    lines = [f"Quality Gate {status}. Overall-Score: {score}", "Nächste Aktionen:"]
    lines.extend(f"  - {item}" for item in next_actions)
    return " | ".join(lines)
