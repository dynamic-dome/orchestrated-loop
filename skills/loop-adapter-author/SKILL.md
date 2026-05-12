---
name: loop-adapter-author
description: Guide the user through writing a new orchestrated-loop adapter (Orchestrator, Researcher, Builder, or Judge). Use when the user says "schreibe einen neuen Adapter", "neuer Loop-Adapter", "write a new loop adapter", "add adapter for X", "create a custom researcher/builder/judge". Skip when the user just wants to use an existing adapter.
---

# Loop Adapter Author

## When to use

Use when the user wants to add a custom adapter to the orchestrated-loop plugin or to an external module loaded via `--adapter-module`.

## Workflow

1. **Ask which role.** Orchestrator, Researcher, Builder, or Judge?
2. **Show the Protocol.** Show the matching Protocol from `engine/src/orchestrated_loop/adapters/base.py`.
3. **Scaffold the class.** Write a new file in either:
   - `engine/src/orchestrated_loop/adapters/<name>.py` (built-in) — requires registry update in `adapters/__init__.py`.
   - `<project>/loop_adapters/<name>.py` (external) — loaded via `--adapter-module loop_adapters.<name>`.
4. **Pattern reminders.**
   - Subprocess: `shutil.which(...)` first; raise `AdapterUnavailable` on missing tool.
   - All subprocess calls: `stdin=subprocess.DEVNULL`, `text=True`, `encoding="utf-8"`, `errors="replace"`.
   - Return adapter-specific errors via `.error` field on the result dataclass, not by raising.
   - Add a test file in `engine/tests/test_adapters_<name>.py` that mocks the external call.
5. **Test the new adapter.**
   ```powershell
   $env:PYTHONPATH = "$PWD/engine/src"
   python -m pytest engine/tests/test_adapters_<name>.py -q
   ```
6. **Update docs.** Add an entry to `docs/04_ADAPTER_KATALOG.md`.

## References

See `docs/06_EIGENER_ADAPTER.md` in the plugin for the long-form guide.
