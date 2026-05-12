# Wegweiser: orchestrated-loop Plugin

## Was das Plugin tut

Stellt einen wiederholbaren 4-Rollen-Loop (Orchestrator/Researcher/Builder/Judge) in jeder Claude-Code-Session bereit. Schreibt Standard-State-Dateien (PLAN.md, TODO.md, LOG.md, DECISIONS.md, RESULTS.json) nach `<projekt>/.loop/<run-id>/`.

## Komponenten

| Pfad | Was es ist |
|---|---|
| `plugin.json` | Plugin-Manifest |
| `commands/loop-run.md` | Slash-Command `/loop-run` |
| `skills/orchestrated-loop/` | Hauptskill |
| `skills/loop-adapter-author/` | Helper-Skill zum Schreiben eigener Adapter |
| `engine/src/orchestrated_loop/` | Python-Engine |
| `engine/tests/` | Tempdir-isolierte Tests |
| `engine/examples/glossary_demo/` | Referenz-Demo |
| `engine/scripts/run_demo.py` | Offline-Demo-Runner |
| `docs/` | Deutsche Doku (8 Dateien) |

## Installation

```powershell
claude plugin install C:/Users/domes/Desktop/Claude-Plugins-Skills/orchestrated-loop --scope user
```

## Erste Schritte

1. In einer Claude-Code-Session: `/loop-run "kurze Task-Beschreibung"`
2. Plugin fragt nach Config, falls `.loop/config.toml` fehlt.
3. Ergebnisse landen in `<projekt>/.loop/<run-id>/`.

## Demo (offline)

```powershell
cd C:/Users/domes/Desktop/Claude-Plugins-Skills/orchestrated-loop
$env:PYTHONPATH = "$PWD\engine\src"
python engine/scripts/run_demo.py
# Erwartet: state-Dateien erzeugt, RESULTS.json mit overall >= 0.85
```

## Doku-Index

- `docs/01_INSTALLATION.md`
- `docs/02_SCHNELLSTART.md`
- `docs/03_ARCHITEKTUR.md`
- `docs/04_ADAPTER_KATALOG.md`
- `docs/05_STATE_FORMAT.md`
- `docs/06_EIGENER_ADAPTER.md`
- `docs/07_NOTEBOOKLM_INTEGRATION.md`
- `docs/08_TROUBLESHOOTING.md`

## Troubleshooting

Erster Anlaufpunkt: `docs/08_TROUBLESHOOTING.md`.
