# Claude-Konventionen für orchestrated-loop

**Erste Pflichtlektüre:** `HOW-TO-USE.md` (Wegweiser für User und Agent).

## Vorrangregel

1. Globale `~/.claude/CLAUDE.md`
2. `SESSION-WORKFLOW.md` auf dem Desktop
3. **Diese Datei**
4. Projektspezifische CLAUDE.md im Zielprojekt

## Projekt-Spezifika

- **Engine läuft ohne Installation:** `$env:PYTHONPATH = "${env:CLAUDE_PLUGIN_ROOT}\engine\src"` und dann `python -m orchestrated_loop`.
- **Subprocess-Pflicht:** `shutil.which("<tool>")` vor `subprocess.run()`, immer `stdin=subprocess.DEVNULL`, `text=True`, `encoding="utf-8"`, `errors="replace"`.
- **Tests:** dürfen ausschließlich gegen `tempfile.mkdtemp(...)` schreiben. `engine/tests/conftest.py` enthält Hardguard.
- **State:** Engine schreibt nur unter `<projekt>/.loop/<run-id>/`. Niemals außerhalb.
- **Doku:** deutsch. Identifier englisch.

## Tests vor Commit

```powershell
$env:PYTHONPATH = "$PWD\engine\src"
python -m pytest engine/tests -q
```
