# Installation

## Voraussetzungen

- Python 3.11+ (3.10 mit `tomli` als Fallback).
- Claude Code CLI installiert.
- Optional: `notebooklm` CLI mit gültigem Login (für `notebooklm_cli` Adapter).
- Optional: `codex` CLI (für `codex_rescue` Adapter).
- Optional: `OPENAI_API_KEY` in `.env` (für `openai_chat` Adapter).

## Plugin installieren

```powershell
claude plugin install C:/Users/domes/Desktop/Claude-Plugins-Skills/orchestrated-loop --scope user
```

## Engine läuft ohne Installation

Die Engine wird per `PYTHONPATH` aus dem Plugin-Verzeichnis geladen. Kein `pip install` nötig.

## Verifikation

```powershell
cd C:/Users/domes/Desktop/Claude-Plugins-Skills/orchestrated-loop
$env:PYTHONPATH = "$PWD/engine/src"
python engine/scripts/verify_local.py
```

Erwartet: alle Tests grün, Demo grün, exit 0.
