# Troubleshooting

## "ModuleNotFoundError: orchestrated_loop"

PYTHONPATH nicht gesetzt. Lösung:

```powershell
$env:PYTHONPATH = "${env:CLAUDE_PLUGIN_ROOT}/engine/src"
```

## "notebooklm CLI not on PATH"

Entweder:
- `notebooklm` ist nicht installiert.
- PATH der laufenden Session unterscheidet sich vom User-PATH.

Test:

```powershell
shutil-wegabhängig: where.exe notebooklm
python -c "import shutil; print(shutil.which('notebooklm'))"
```

## "Config nicht gefunden"

`.loop/config.toml` fehlt. Skill kann eine Default-Config generieren. Manuell:
siehe `docs/05_STATE_FORMAT.md`.

## Tests schlagen mit "REFUSING TO RUN" fehl

`ORCHESTRATED_LOOP_TEST_RUNDIR_OVERRIDE` zeigt auf einen Pfad außerhalb von `tempfile.gettempdir()`. Unset oder auf Tempdir setzen:

```powershell
Remove-Item Env:ORCHESTRATED_LOOP_TEST_RUNDIR_OVERRIDE -ErrorAction SilentlyContinue
```

## "OPENAI_API_KEY not set"

Adapter `openai_chat` braucht den Key. In `.env`:

```
OPENAI_API_KEY=sk-...
```

Falls `python-dotenv` nicht installiert: Key direkt in der Session setzen.

## Builder-Timeout (returncode 124)

`[adapter.local_shell].timeout_seconds` erhöhen oder Command splitten.

## Loop bricht nach Iteration 1 mit returncode != 0

Builder ist fehlgeschlagen. RESULTS.json prüfen, dann `LOG.md` für Details.
