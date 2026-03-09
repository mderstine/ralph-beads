# Pathlib Migration

## Job To Be Done
Replace `os.path` and `os` path operations with `pathlib.Path` throughout the codebase for cleaner, more idiomatic Python.

## Requirements

### Code Migration
- Replace `os.path.join(...)` with `Path(...) / ...`
- Replace `os.path.exists(...)` with `Path(...).exists()`
- Replace `os.makedirs(...)` with `Path(...).mkdir(parents=True, exist_ok=True)`
- Replace `os.path.dirname(os.path.abspath(__file__))` with `Path(__file__).parent`
- Keep `os.environ` usage — that is not path management
- Keep `os.pathsep` usage — that is platform constant, not path management
- Retain `import os` only if non-path `os` usage remains (e.g. `os.environ`, `os.pathsep`)

### Affected Files
- `scripts/config.py` — uses `import os` (for `os.environ` in `_apply_env_overrides`) — may already be clean
- `scripts/gh_triage.py` — `os.path.exists()`, `os.makedirs()`
- `scripts/add_spec.py` — `os.path.join()`, `os.path.dirname()`, `os.path.abspath()`, `os.makedirs()`
- `scripts/loop.py` — uses `import os` (check what for)
- `scripts/cli_utils.py` — uses `os.environ`, `os.pathsep` (keep `import os`, no path migration needed)

### Convention Update
- Add a line to AGENTS.md Coding Standards: "Use `pathlib.Path` for all path operations — never `os.path`"

## Constraints
- Python stdlib only
- Must not change behavior — pure refactor
- Existing tests must continue to pass

## Notes
- `config.py` already uses `pathlib.Path` extensively — `import os` is only for `os.environ` access
- `cli_utils.py` uses `os.environ` and `os.pathsep` which are not path operations — leave as-is
- Each file can be migrated independently
