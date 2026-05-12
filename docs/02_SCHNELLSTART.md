# Schnellstart

## In einer Claude-Code-Session

```
/loop-run "Refaktoriere foo.py und passe Tests an"
```

Wenn `.loop/config.toml` fehlt, fragt der Skill, ob eine Default-Config angelegt werden soll.

## Manuell via Engine

```powershell
$env:PYTHONPATH = "${env:CLAUDE_PLUGIN_ROOT}/engine/src"
python -m orchestrated_loop run `
  --config .loop/config.toml `
  --run-dir .loop/2026-05-12-1530-refactor `
  --project-root $PWD
```

## Demo offline

```powershell
cd <plugin-root>
$env:PYTHONPATH = "$PWD/engine/src"
python engine/scripts/run_demo.py
```

Ergebnisse in `<plugin-root>/.loop/demo-run/`.
