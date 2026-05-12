# Adapter-Katalog (v1)

| Adapter | Rolle(n) | Was es macht | Abhängigkeit |
|---|---|---|---|
| `dummy` | Orchestrator, Researcher, Judge | Deterministisch, offline | keine |
| `local_shell` | Builder | `subprocess.run(command, shell=True)` mit Timeout | keine |
| `notebooklm_cli` | Researcher | `notebooklm use <id>` + `notebooklm ask --json <q>` parallel | `notebooklm` CLI + Login |
| `codex_rescue` | Builder | Handoff-Files + `codex rescue --plan ... --output ...` | `codex` CLI |
| `openai_chat` | Orchestrator, Judge | OpenAI Chat Completions mit JSON-Modus | `OPENAI_API_KEY`, `httpx` |

## Adapter-Optionen

### `local_shell`

```toml
[adapter.local_shell]
command = "pytest -q"          # required
test_command = "ruff check ."  # optional, läuft nur wenn command erfolgreich
timeout_seconds = 180          # default 120
```

### `notebooklm_cli`

```toml
[adapter.notebooklm_cli]
notebook_id = "abc-123-uuid"   # required
language = "de"                # optional
timeout_seconds = 120          # default 120
```

### `codex_rescue`

```toml
[adapter.codex_rescue]
profile = "fast"               # optional
timeout_seconds = 600          # default 600
# handoff_dir wird default auf .loop/handoff/ gesetzt
```

### `openai_chat`

```toml
[adapter.openai_chat]
model = "gpt-4o-mini"          # default gpt-4o-mini
```

Voraussetzung: `OPENAI_API_KEY` in der Umgebung (z.B. via `.env`).
