# NotebookLM-Integration

## Voraussetzungen

- `notebooklm` CLI installiert (User-Skill).
- Aktive Session: `notebooklm login` zuvor ausgeführt.
- Notebook-ID bekannt: `notebooklm list --json` zeigt sie an.

## Adapter konfigurieren

In `.loop/config.toml`:

```toml
[roles]
researcher = "notebooklm_cli"

[adapter.notebooklm_cli]
notebook_id = "deine-notebook-uuid-hier"
language = "de"
timeout_seconds = 120
```

## Wie der Adapter arbeitet

1. Beim ersten `ask()`-Aufruf einer Run-Instanz: `notebooklm use <id> --json`.
2. Pro Frage: `notebooklm ask --json <frage>` (parallel via ThreadPool, max 4 Worker).
3. Antworten werden in `ResearchResult.answer` (combined) und `ResearchResult.citations` (alle Quellen) zurückgegeben.

## Fehlerverhalten

- `notebooklm` nicht auf PATH → `AdapterUnavailable` beim Init.
- Session expired → `ResearchResult.error` gesetzt, Loop läuft weiter, Judge bekommt das mit.
- Non-JSON Stdout → wird als Error behandelt.

## Windows-Hinweis

Immer `--json` (gilt für alle Subcommands). Rich-CLI bricht sonst mit cp1252.
