# State-Format

## Verzeichnislayout pro Run

```
<projekt>/.loop/<run-id>/
├── PLAN.md              # überschrieben pro Iteration
├── TODO.md              # überschrieben pro Iteration
├── LOG.md               # append-only pro Iteration
├── DECISIONS.md         # append-only
├── RESULTS.json         # voller maschinenlesbarer State
├── handoff/             # Adapter-Handoffs (codex, notebooklm)
└── artifacts/           # Builder-Artefakte (optional)
```

`<projekt>/.loop/latest` enthält den Pfad zum letzten Run.

## RESULTS.json Schema

```json
{
  "task_name": "string",
  "started_at": "ISO8601",
  "config": {
    "config_path": "...",
    "project_root": "...",
    "roles": {"orchestrator": "dummy", "researcher": "dummy", "builder": "local_shell", "judge": "dummy"},
    "max_iterations": 3,
    "target_score": 0.85
  },
  "iterations": [
    {
      "iteration": 1,
      "timestamp": "ISO8601",
      "plan": {"goal": "...", "tasks": [...], "questions": [...], "acceptance_criteria": [...]},
      "research": {"answer": "...", "citations": [...], "open_questions": [...], "error": null},
      "build": {"command": "...", "returncode": 0, "stdout_tail": "...", "stderr_tail": "...", "artifacts": [...]},
      "judge": {"scores": {...}, "overall": 0.9, "fail_reasons": [], "next_actions": [...], "passed": true}
    }
  ],
  "latest_score": {"...": "..."}
}
```

## Default-Config (zum Auto-Generieren)

```toml
[loop]
task_name = "<füllt der Skill ein>"
max_iterations = 3
target_score = 0.85

[roles]
orchestrator = "dummy"
researcher = "dummy"
builder = "local_shell"
judge = "dummy"

[adapter.local_shell]
command = "echo 'replace me'"
timeout_seconds = 120

[judge]
required_terms = []
required_artifacts = []
min_passing_score = 0.85
```
