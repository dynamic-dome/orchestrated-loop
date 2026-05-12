# Eigenen Adapter schreiben

## Schritt 1: Rolle festlegen

Welche Protocol-Klasse implementiert dein Adapter? Genau eine:

- `Orchestrator` — produziert `Plan`-Objekte
- `Researcher` — beantwortet Fragen, liefert `ResearchResult`
- `Builder` — führt Code/Commands aus, liefert `BuildResult`
- `Judge` — bewertet Build, liefert `JudgeScore`

Definitionen in `engine/src/orchestrated_loop/adapters/base.py`.

## Schritt 2: Adapter-Datei anlegen

Zwei Varianten:

### A. Built-in (Plugin-intern)

```
engine/src/orchestrated_loop/adapters/<name>.py
```

Plus Registry-Update in `engine/src/orchestrated_loop/adapters/__init__.py`.

### B. Extern (im Zielprojekt)

```
<projekt>/loop_adapters/<name>.py
```

Geladen via:

```
python -m orchestrated_loop run --adapter-module loop_adapters.<name> ...
```

## Schritt 3: Implementierungsmuster

```python
from orchestrated_loop.adapters.base import AdapterUnavailable, BuildResult, Plan, ResearchResult
import shutil
import subprocess


class MyBuilder:
    def __init__(self, **opts) -> None:
        self._binary = shutil.which("mytool")
        if self._binary is None:
            raise AdapterUnavailable("mytool nicht auf PATH.")
        self._opts = opts

    def run(self, plan: Plan, research: ResearchResult) -> BuildResult:
        completed = subprocess.run(
            [self._binary, "--task", plan.goal],
            text=True, encoding="utf-8", errors="replace",
            capture_output=True, stdin=subprocess.DEVNULL,
            timeout=120, check=False,
        )
        return BuildResult(
            command=self._binary,
            returncode=completed.returncode,
            stdout=completed.stdout,
            stderr=completed.stderr,
            artifacts=[],
        )
```

## Schritt 4: Test mit Mock

In `engine/tests/test_adapters_<name>.py`:

```python
def test_my_builder_smoke(monkeypatch, tmp_path):
    monkeypatch.setattr("shutil.which", lambda n: "/usr/local/bin/mytool")
    monkeypatch.setattr(subprocess, "run",
                        lambda *a, **k: subprocess.CompletedProcess([], 0, stdout="ok", stderr=""))
    b = MyBuilder()
    result = b.run(Plan(goal="x", iteration=1), ResearchResult(answer=""))
    assert result.returncode == 0
```

## Schritt 5: Doku ergänzen

Eintrag in `skills/orchestrated-loop/references/adapter-catalog.md`.
