# Architektur

## Schichten

```
Claude-Code-Session
        │
        ▼
Plugin (orchestrated-loop)
  ├── /loop-run (Slash-Command)
  └── Skill orchestrated-loop
        │
        ▼ (subprocess)
Engine (Python-Paket, kein pip install)
  ├── orchestrator.run_loop()
  ├── StateStore (PLAN/TODO/LOG/DECISIONS/RESULTS)
  └── Adapter-Registry
        │
        ▼
Adapters (5 in v1)
  ├── dummy           (Orchestrator/Researcher/Judge)
  ├── local_shell     (Builder)
  ├── notebooklm_cli  (Researcher)
  ├── codex_rescue    (Builder)
  └── openai_chat     (Orchestrator/Judge)
```

## Datenfluss pro Iteration

1. `Orchestrator.plan(task_name, iteration, previous_score) → Plan`
2. `Researcher.ask(plan.questions, iteration) → ResearchResult`
3. `Builder.run(plan, research) → BuildResult`
4. `Judge.score(criteria, build) → JudgeScore`
5. State-Files werden geschrieben (PLAN/TODO überschrieben, LOG/DECISIONS appended, RESULTS überschrieben mit vollem State).
6. Abbruch wenn `build.returncode != 0` oder `score.passed`.

## State

State lebt projekt-lokal unter `<projekt>/.loop/<run-id>/`. Engine schreibt niemals außerhalb dieser Pfade.
