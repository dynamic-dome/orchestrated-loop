# Changelog

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
