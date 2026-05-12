# Glossary Demo

Referenz-Demo: extrahiert aus drei Beispielnotizen ein Glossar und prüft Muss-Begriffe.

## Ausführen (offline)

````powershell
cd <plugin-root>
$env:PYTHONPATH = "$PWD/engine/src"
python -m orchestrated_loop run `
  --config engine/examples/glossary_demo/config/loop.dryrun.toml `
  --run-dir .loop/demo-run `
  --project-root $PWD
````

Erwartete Artefakte in `.loop/demo-run/`:
- PLAN.md, TODO.md, LOG.md, DECISIONS.md, RESULTS.json
- glossar.md, glossar.json (vom Extractor erzeugt)

Score-Ziel: `overall >= 0.85`.
