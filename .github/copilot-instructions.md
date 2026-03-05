# Ralph-Beads Protocol

This project uses the Ralph-Beads framework for autonomous, dependency-aware development. These instructions apply to every Copilot chat session in this workspace.

## Core Rule

Use `bd` (beads CLI) for ALL task tracking. Never use markdown TODOs, task lists, or external issue trackers. Beads is the single source of truth.

## Workflow

Before starting any work:

1. Check for ready work: `bd ready --json`
2. Claim your task atomically: `bd update <id> --claim --json`
3. Read the issue: `bd show <id> --json`
4. Implement the work described in the issue
5. Run validation (see Build & Validate below)
6. Commit on green with a descriptive message
7. Close the issue: `bd close <id> --reason "..." --json`

One task at a time. Do not pick up additional work until the current task is closed.

## Build & Validate

Run ALL quality gates before committing:

```bash
python -m pytest tests/ -v
python -m mypy src/ --strict
python -m ruff check src/ tests/
```

Do not commit code that fails validation. Fix issues and re-run until green.

## Beads CLI Quick Reference

```bash
bd ready --json                # Unblocked work — what to do next
bd show <id> --json            # Issue details + dependencies
bd update <id> --claim --json  # Claim work atomically
bd close <id> --reason "..."   # Complete work with context
bd create "Title" -p <0-4> -t <type> --json  # Create new issue
bd dep add <id> <blocker> --type blocks      # Add dependency
bd dep tree <id>               # Visualize dependency graph
bd dep cycles                  # Check for circular dependencies
bd prime                       # Session context summary
```

## Discovering New Work

If you find bugs, missing features, or tech debt while working on a task, file them as new issues linked to the current task. Do not fix them in the current iteration.

```bash
bd create "Discovered: <title>" \
    --description="<context>" \
    -p <priority> -t <type> \
    --deps discovered-from:<current-id> --json
```

## Issue Types and Priorities

Types: `bug`, `feature`, `task`, `epic`, `chore`

Priorities:
- 0: Critical (security, data loss, broken builds)
- 1: High (core features, important bugs)
- 2: Medium (standard features)
- 3: Low (polish, optimization)
- 4: Backlog (future ideas)

## Coding Standards

- Python 3.12+
- Type annotations on public APIs
- Tests for all new functionality
- Keep functions small and focused
- Study existing patterns before writing new code

## Project Structure

- `specs/` — Requirement documents (one per topic)
- `AGENTS.md` — Operational guide with build commands and patterns
- `PROMPT_plan.md` — Planning mode instructions (specs to task graph)
- `PROMPT_build.md` — Build mode instructions (claim, implement, close)
- `.beads/` — Beads database (managed by bd, do not edit directly)

## Important

- Always use `--json` flag when parsing bd output programmatically
- Link discovered work with `discovered-from` dependencies
- Check `bd ready` before asking "what should I work on?"
- Read AGENTS.md at the start of each session for project-specific patterns
