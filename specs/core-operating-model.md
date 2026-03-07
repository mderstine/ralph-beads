# Core Operating Model

## Job To Be Done
Define the foundational local-only workflow that enables AI agents to autonomously build software one task at a time using the Ralph Loop pattern with Beads dependency-aware task tracking.

## Requirements

### Loop Orchestrator (loop.sh)
- Runs in two modes: `plan` (specs to task graph) and `build` (claim, implement, test, commit, close)
- Each iteration gets fresh agent context — no state leaks between iterations
- Pre-flight checks: verify `bd` CLI, agent CLI, beads database health, git state
- Configurable per-iteration timeout with graceful shutdown on SIGINT/SIGTERM
- Structured iteration logging to `logs/` with JSON summary line per iteration
- Build mode exits when `bd ready` returns zero unblocked issues
- One task per build iteration — enforced by prompt design, not code

### Prompt Architecture
- `PROMPT_plan.md` — planning agent instructions (specs → beads task graph)
- `PROMPT_build.md` — build agent instructions (claim → implement → validate → commit → close)
- `AGENTS.md` — operational guide loaded every iteration (build commands, CLI reference, coding standards, known patterns)
- `CLAUDE.md` — project-level instructions for the AI agent (framework overview, rules, key commands)
- Prompts are agent-neutral in content: they describe WHAT to do, not HOW to invoke a specific tool

### Beads as State Machine
- `bd ready --json` is the sole source of truth for what to work on next
- `bd update <id> --claim` provides atomic work claiming (multi-agent safe)
- `bd close <id> --reason "..."` captures completion context for future iterations
- `bd create ... --deps discovered-from:<id>` links discovered work to its source
- `bd dep` commands express ordering constraints between tasks
- `bd prime` provides session context summary
- The `.beads/` directory is the persistent state — survives across iterations and sessions

### Specs as Requirements
- Each file in `specs/` represents one "topic of concern"
- Specs follow a standard structure: Job To Be Done, Requirements, Constraints, Notes
- Planning mode reads all specs and creates/updates the beads task graph
- Specs are human-authored; the planning agent decomposes them into implementable tasks

### Backpressure (Quality Gates)
- Every build iteration must run validation before committing (tests, lint, type checks)
- Validation commands are defined in `AGENTS.md` so they're project-specific
- Failed validation blocks the commit — the agent must fix or abandon
- Only one subagent for builds/tests to prevent resource contention

### Git Discipline
- Each completed task produces exactly one commit with a descriptive message
- Commit messages include `Closes: <beads-id>` for traceability
- Agents must not modify framework files (loop.sh, prompts, CLAUDE.md)
- Work on feature branches; warn if on main/master

## Constraints
- Zero external service dependencies — works offline with just `bd` and an AI agent CLI
- No Python package dependencies beyond stdlib for framework scripts
- Must work on Linux and macOS
- `.beads/` directory committed to git for portability across machines
- `logs/` directory gitignored (local ephemeral data)

## Notes
- This spec defines Layer 0 — the foundation. GitHub integration (Layer 1) and GitHub Projects (Layer 2) are optional add-ons defined in separate specs
- The loop.sh orchestrator is currently implemented and functional with timeouts, signal handling, structured logging, and pre-flight checks
- The "Ralph Loop" pattern originates from Geoffrey Huntley: `while :; do cat PROMPT.md | claude -p; done`
- Beads (Steve Yegge) replaces IMPLEMENTATION_PLAN.md as the inter-iteration state machine — `bd ready` provides deterministic task selection instead of LLM parsing markdown
