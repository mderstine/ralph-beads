# Cross-Platform Compatibility

## Job To Be Done
Make the Purser framework run on Windows, macOS, and Linux without requiring bash or Unix-specific utilities.

## Requirements

### Replace Shell Script Wrappers with Python Entry Points
- Convert `scripts/gh-sync.sh`, `scripts/gh-triage.sh`, `scripts/gh-changelog.sh`, `scripts/gh-project.sh`, `scripts/gh-pr-body.sh`, `scripts/gh-labels.sh` to Python scripts or `uv run` entry points
- These are thin wrappers (prerequisite checks + `exec uv run python3`) — the Python equivalents should inline the prerequisite checks
- Provide a cross-platform invocation method (e.g., `uv run python3 scripts/gh_sync.py` or pyproject.toml `[project.scripts]` entry points)

### Rewrite `init.sh` in Python
- Convert `init.sh` to a Python script (`scripts/init.py` or entry point)
- Preserve all 8 steps: prerequisites, venv, beads DB, GitHub remote, GitHub Project, labels, config, summary
- Preserve `--check` and `--skip-github` flags
- Use `subprocess` for external commands (`uv`, `bd`, `gh`, `git`) with proper cross-platform process invocation

### Rewrite `loop.sh` in Python
- Convert `loop.sh` to a Python script (`scripts/loop.py` or entry point)
- Preserve all modes: `build`, `plan`, `status`, `sync`, `triage`, `changelog`
- Replace Unix-specific constructs:
  - `timeout` command → Python `subprocess.Popen` with timeout
  - Signal traps (`trap SIGINT/SIGTERM`) → Python `signal` module handlers
  - Process group kill (`kill -TERM -- -$PID`) → `os.killpg()` on Unix, `taskkill` or `Popen.terminate()` on Windows
  - `comm` (set difference) → Python set operations
  - `mktemp` → Python `tempfile`
  - `date '+%s'` → Python `time.time()`
  - `read -r` (pause for input) → Python `input()`
  - `PIPESTATUS` → captured via separate subprocess calls
- Maintain the same CLI interface: `./loop.py`, `./loop.py plan`, `./loop.py 20`, `./loop.py sync`, etc.

### Cross-Platform Process Management
- Claude CLI invocation must work on both `cmd.exe`/PowerShell and Unix shells
- `PYTHONPATH` separator is `:` on Unix and `;` on Windows — use `os.pathsep`
- File paths must use `pathlib.Path` instead of string concatenation
- Shebang lines (`#!/usr/bin/env bash`) replaced by Python shebangs or entry points

### Backward Compatibility
- Keep `.sh` files as thin wrappers that delegate to the Python versions (for existing Unix users)
- Or: remove `.sh` files entirely and update all references in `CLAUDE.md`, `AGENTS.md`, `PROMPT_*.md`, and `loop.sh` references
- Update `CLAUDE.md` "Key Commands" section with new invocation syntax

## Constraints
- Python 3.10+ (already required by the project via `uv`)
- No new dependencies beyond the standard library and existing `pyproject.toml` deps (PyYAML)
- `uv run` must remain the standard invocation method for consistency
- The `claude` CLI (Claude Code) must be available on PATH on all platforms
- `bd` CLI must be available on PATH on all platforms (Node.js-based, already cross-platform)
- `gh` CLI must be available on PATH on all platforms (already cross-platform)

## Notes
- The `scripts/gh-*.sh` wrappers are the easiest wins — they're 20-40 lines each and mostly just check `command -v` then `exec` Python
- `loop.sh` is the hardest — 337 lines with signal handling, process group management, and background subshells
- `gh-labels.sh` is the only wrapper with significant bash logic (label creation loop with `grep`); the rest are pure delegation
- Consider using `pyproject.toml` `[project.scripts]` to create `purser-loop`, `purser-init`, etc. entry points via `uv`
- On Windows, `timeout` command exists but does something completely different (waits for keypress)
- Process group semantics differ significantly between Unix and Windows — may need platform-specific code paths using `sys.platform`
