# Logging Migration

## Job To Be Done
Replace `print()` statements with Python `logging` for consistent, configurable diagnostic output across all scripts.

## Requirements

### Logging Setup
- Create a shared logging configuration helper (e.g. in `cli_utils.py` or a new `log.py`)
- Default log level: `INFO` for normal output, controllable via `--verbose`/`--quiet` flags or `PURSER_LOG_LEVEL` env var
- Format: simple human-readable format for CLI use (no timestamps by default)
- Each script module uses `logger = logging.getLogger(__name__)`

### Migration Rules
- `print(message)` for user-facing status → `logger.info(message)`
- `print(message, file=sys.stderr)` for errors → `logger.error(message)` or `logger.warning(message)`
- `print(json.dumps(...))` for `--json` structured output → keep as `print()` (program output, not diagnostics)
- Interactive prompts (`input()` calls) → keep associated `print()` as-is (UI, not logging)
- Progress messages like "added: #42" → `logger.info(...)`
- Debug details (raw API responses, fallback paths tried) → `logger.debug(...)`

### Affected Files (303 print calls across 15 files)
- `scripts/init.py` (88 prints) — largest, mostly user-facing status
- `scripts/loop.py` (54 prints) — orchestrator status
- `scripts/gh_project.py` (38 prints) — board sync progress
- `scripts/gh_remote.py` (26 prints) — detection/creation flow
- `scripts/gh_sync.py` (19 prints) — issue sync progress
- `scripts/gh_project_setup.py` (18 prints) — project setup
- `scripts/gh_triage.py` (17 prints) — triage flow
- `scripts/gh_labels.py` (11 prints) — label bootstrap
- `scripts/prereqs.py` (9 prints) — prerequisite checks
- `scripts/config.py` (5 prints) — CLI dump/get output (keep as print)
- `scripts/gh_changelog.py` (5 prints) — changelog output (keep as print)
- `scripts/cli_utils.py` (3 prints) — utility errors
- `scripts/add_spec.py` (2 prints) — spec creation status
- `scripts/lib.py` (2 prints) — utility errors
- `scripts/gh_pr_body.py` (6 prints) — PR body output (keep as print)

### Convention Update
- Add to AGENTS.md Coding Standards: "Use `logging` for all diagnostic output — never bare `print()`. Reserve `print()` only for program output (JSON, generated content) and interactive prompts."

## Constraints
- Python stdlib only (`logging` is stdlib)
- Must not change behavior visible to end users under default log level
- `--json` output and interactive prompts must remain on stdout via `print()`
- Existing tests must continue to pass (may need `caplog` instead of `capsys` in some tests)

## Notes
- 26 of the 303 prints already go to `stderr` — these are the clearest candidates for `logger.error()`/`logger.warning()`
- Scripts that produce structured output (`config.py dump`, `gh_changelog.py`, `gh_pr_body.py`) should keep `print()` for their primary output
- `loop.py` has its own log file (`logs/summary.jsonl`) — logging migration should not interfere with that
- Migration can be done file-by-file since each script is independent
- Consider batching by size: small files first (add_spec, lib, cli_utils), then medium, then large (init, loop)
