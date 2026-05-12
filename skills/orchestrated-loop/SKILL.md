---
name: orchestrated-loop
description: Run a 4-role iterative loop (Orchestrator/Researcher/Builder/Judge) in the current project. Reads .loop/config.toml, writes state to .loop/<run-id>/. Use when the user wants to iterate on a coding or research task with explicit per-iteration plans, quality gates, and persisted state files. Trigger phrases: "loop run", "iterative loop", "orchestrated loop", "run a loop", "iterate on this task", "build and judge loop", "loop ausführen", "iterativ verbessern".
---

# Orchestrated Loop

## When to use

Use this skill when the user wants iterative, persisted, multi-role execution on a task. Each iteration:

1. Orchestrator plans tasks and questions.
2. Researcher answers the questions (offline by default, NotebookLM if configured).
3. Builder runs a shell command or invokes Codex.
4. Judge scores the output against required terms/artifacts.

Stops when score >= target or after max_iterations.

## When NOT to use

- Autonomous multi-agent execution → use `agent-orchestrator`.
- Self-improvement of a plugin → use `agentic-os:self-improve`.
- 3-phase Plan/Implement/Review with Codex → use `multi-model-orchestrator`.
- Recurring schedule → use built-in `/loop` or `/schedule`.

## Workflow

When invoked via `/loop-run [task]` or matching trigger phrases:

1. **Locate config.** Check for `.loop/config.toml` in CWD. If missing, offer to generate a default one (from `references/state-format.md` snippet).
2. **Generate run-id.** Format: `YYYY-MM-DD-HHMMSS-<slug>` where `<slug>` is a 6-char hash of task text.
3. **Create run dir.** `mkdir -p .loop/<run-id>`.
4. **Invoke engine.** PowerShell:
   ```powershell
   $env:PYTHONPATH = "${env:CLAUDE_PLUGIN_ROOT}/engine/src"
   python -m orchestrated_loop run `
     --config .loop/config.toml `
     --run-dir .loop/<run-id> `
     --project-root $PWD `
     --task "<task text>"
   ```
   Unix:
   ```bash
   PYTHONPATH="$CLAUDE_PLUGIN_ROOT/engine/src" python -m orchestrated_loop run \
     --config .loop/config.toml \
     --run-dir .loop/<run-id> \
     --project-root "$PWD" \
     --task "<task text>"
   ```
5. **Update `.loop/latest`.** Write the run-id (or full path) into `.loop/latest` as a single line.
6. **Summarize.** Read `.loop/<run-id>/RESULTS.json` and present to the user:
   - Number of iterations
   - Final score and passed/failed
   - Fail reasons (if any)
   - Next actions

## References

- `references/adapter-catalog.md` — which adapters exist and what they need
- `references/state-format.md` — schema of PLAN/TODO/LOG/DECISIONS/RESULTS plus default config TOML
- `references/role-prompts/` — prompts for `openai_chat` adapter

## Notes

- Engine runs as a subprocess. The skill does not implement loop logic itself.
- `notebooklm_cli` adapter needs the `notebooklm` CLI on PATH and a valid login.
- `codex_rescue` adapter needs the `codex` CLI on PATH.
- `openai_chat` adapter needs `OPENAI_API_KEY` and `httpx` (optional dep).
