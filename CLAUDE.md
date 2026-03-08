# Purser Framework

Unified agentic AI development protocol combining Geoffrey Huntley's Ralph Loop
with Beads (`bd`) dependency-aware issue tracking.

## How It Works

```
purser-loop → PROMPT.md → Claude Code → bd ready → implement → bd close → git commit → loop restarts
```

Each iteration gets fresh context. Beads replaces IMPLEMENTATION_PLAN.md as the
persistent state machine between loops. The user writes specs, the framework
breaks them into dependency-ordered tasks, and builds them one at a time.

## User's Role

The user directs by writing specs (`specs/`), setting quality gates (`AGENTS.md`),
and tuning prompts (`PROMPT_*.md`). They watch the loop and intervene via `bd` CLI
commands (re-prioritize, add blockers, skip tasks, inject urgent work).

## First-Time Setup

New to this project? Run `/init` (Claude Code slash command) to bootstrap the project:
- Checks prerequisites (git, python3, uv, gh, bd)
- Creates Python virtual environment (`uv venv` + `uv sync`)
- Initializes the beads database
- Sets up GitHub remote, Project board, and labels
- Saves configuration to `.purser.yml`

Or run `uv run purser-init` directly from the terminal.

## Key Commands

```bash
uv run purser-loop              # Build mode (default)
uv run purser-loop plan         # Planning mode (specs → task graph)
uv run purser-loop plan 5       # Planning mode, max 5 iterations
uv run purser-loop 20           # Build mode, max 20 iterations
uv run purser-loop status       # Print iteration stats from logs/summary.jsonl
uv run purser-loop sync         # Sync beads issues to GitHub Issues/Project board
uv run purser-loop triage       # Triage spec-candidate GitHub Issues into specs/
```

Both `sync` and `triage` support `--dry-run` for preview.

## Files

- `PROMPT_plan.md` — Planning mode prompt (specs → beads issues)
- `PROMPT_build.md` — Build mode prompt (bd ready → implement → close)
- `AGENTS.md` — Operational guide loaded every iteration
- `scripts/loop.py` — The Ralph Loop orchestrator (`uv run purser-loop`)
- `scripts/init.py` — Project initialization (`uv run purser-init`)
- `specs/` — User's requirements documents (one per topic of concern)
- `scripts/` — Python scripts for GitHub integration and CLI entry points
- `.beads/` — Beads database (managed by bd, don't edit)

## Rules

- Use `bd` for ALL task tracking — never markdown TODOs
- One task per loop iteration
- Always run backpressure (tests/lint/build) before committing
- Link discovered work with `discovered-from` dependencies
- Close issues with meaningful reasons
