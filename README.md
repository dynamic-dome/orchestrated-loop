# Orchestrated Loop Plugin

Deutschsprachiges Claude-Code-Plugin für einen adapter-agnostischen Loop nach dem Schema **Orchestrator / Researcher / Builder / Judge**. State-Dateien (PLAN.md, TODO.md, LOG.md, DECISIONS.md, RESULTS.json) leben pro Projekt unter `.loop/<run-id>/`.

## Quick Start

In jeder Claude-Code-Session:

```
/loop-run "Refaktoriere foo.py und passe Tests an"
```

Details in `HOW-TO-USE.md` und `docs/02_SCHNELLSTART.md`.

## Dokumentation

- `CLAUDE.md` — Agent-Konventionen
- `HOW-TO-USE.md` — User-Wegweiser
- `docs/` — vollständige deutsche Doku (8 Dateien)
