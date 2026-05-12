# Changelog

## [0.2.0] - 2026-05-13

### Added

- `LoopChatError` exception class in `orchestrated_loop.adapters.exceptions` for uniform error reporting from chat adapters (HTTP errors, transport failures, malformed responses).
- 5 tests in `engine/tests/test_adapters_openai_exceptions.py` covering 401/429/500 wrapping, transport-failure chaining (`__cause__`), and malformed-response handling.

### Changed

- `openai_chat._chat()` now wraps all failure modes in `LoopChatError` instead of propagating raw `httpx`/transport exceptions or `KeyError`/`ValueError` from response parsing. Callers can now handle a single exception type with `status_code` and `body` attributes.

### Why

Callers had to know about httpx internals to handle chat failures. Wrapping them in `LoopChatError` gives downstream code (orchestrator, judge consumers) a stable surface and structured metadata. Originating exception remains accessible via `__cause__`.

## [0.1.0] - 2026-05-12

### Added

- Plugin scaffold (`plugin.json`, `CLAUDE.md`, `HOW-TO-USE.md`, `README.md`).
- Engine: `orchestrated_loop` package (state, config, scoring, orchestrator, CLI).
- Adapters: `dummy`, `local_shell`, `notebooklm_cli`, `codex_rescue`, `openai_chat`.
- Skills: `orchestrated-loop` (main), `loop-adapter-author` (helper).
- Slash command: `/loop-run`.
- German documentation under `docs/` (8 files).
- Reference role prompts under `skills/orchestrated-loop/references/role-prompts/`.
- Glossary demo under `engine/examples/glossary_demo/`.
- Tempdir-isolated tests with hardguard in `engine/tests/conftest.py`.
- Marketplace.json prepared for future GitHub publication.

### Known Limitations

- Local plugin installation via `claude plugin install` not supported in this Claude Code version (requires GitHub-based marketplace source). Plugin structure is complete; can be installed once published to a GitHub repo.

### Notes

- Engine runs via `PYTHONPATH=${CLAUDE_PLUGIN_ROOT}/engine/src` (no installation).
- `claude_subagent` and `notebooklm_mcp` adapters deferred to a future version.
- Migrated from `~/Desktop/daily-pulse-orchestrated-loop-kit/`. Kit-Repo bleibt 30 Tage als Backup.
