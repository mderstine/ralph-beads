# Claude Code to VS Code File Mapping

The purser framework works with both Claude Code and VS Code Copilot.
This document maps each Claude Code file to its VS Code equivalent.

## Project Instructions

| Claude Code | VS Code | Purpose |
|---|---|---|
| `CLAUDE.md` | `.github/copilot-instructions.md` | Global project instructions loaded every session |
| `AGENTS.md` | `AGENTS.md` (shared) | Operational guide: build commands, coding standards, beads workflow |

## Slash Commands / Prompt Files

| Claude Code | VS Code | Purpose |
|---|---|---|
| `.claude/commands/plan.md` | `.github/prompts/plan.prompt.md` | Run planning mode: specs to task graph |
| `.claude/commands/build.md` | `.github/prompts/build.prompt.md` | Run one build iteration: claim, implement, close |
| `.claude/commands/status.md` | `.github/prompts/status.prompt.md` | Project status report |
| `.claude/commands/add-spec.md` | `.github/prompts/add-spec.prompt.md` | Create a new spec file |
| `.claude/commands/create-issue.md` | `.github/prompts/create-issue.prompt.md` | Create a new beads issue |

## Build Prompts

| Claude Code | VS Code | Purpose |
|---|---|---|
| `PROMPT_build.md` | `.github/agents/beads-dev.agent.md` | Build loop instructions (claim, implement, test, commit, close) |
| `PROMPT_plan.md` | `.github/agents/beads-pm.agent.md` | Planning loop instructions (specs to dependency-aware task graph) |

## Loop Invocations

| Claude Code | VS Code | Purpose |
|---|---|---|
| `./loop.sh` or `./loop.sh build` | Invoke `@beads-dev` agent | Build one task |
| `./loop.sh plan` | Invoke `@beads-pm` agent | Decompose specs into tasks |
| `./loop.sh sync` | Run `scripts/gh-sync.sh` in terminal | Sync beads to GitHub |
| `./loop.sh triage` | Run `scripts/gh-triage.sh` in terminal | Triage spec-candidate issues |
| `/build` slash command | `@beads-dev` or `#build` prompt | Same as above |
| `/plan` slash command | `@beads-pm` or `#plan` prompt | Same as above |
| `/status` slash command | `#status` prompt | Same as above |

## Skills (VS Code only)

These have no Claude Code equivalent — they are reusable instruction snippets
for VS Code Copilot agent mode:

| VS Code | Purpose |
|---|---|
| `.github/skills/beads-workflow/SKILL.md` | Beads workflow patterns |
| `.github/skills/beads-create/SKILL.md` | Issue creation patterns |
| `.github/skills/beads-triage/SKILL.md` | Issue triage patterns |

## Files with No Equivalent

| File | Side | Why |
|---|---|---|
| `.claude/projects/*/memory/` | Claude Code only | Persistent memory across sessions (no VS Code equivalent) |
| `loop.sh` | Claude Code only | Autonomous loop — VS Code uses manual agent invocations |
| `.github/instructions/beads-conventions.instructions.md` | VS Code only | Always-on conventions (Claude Code uses CLAUDE.md) |

## Key Differences

- **Claude Code** uses `loop.sh` for autonomous iteration. VS Code uses manual agent invocations.
- **Claude Code** has persistent memory (`.claude/projects/*/memory/`). VS Code does not.
- **Claude Code** slash commands use `$ARGUMENTS` substitution. VS Code prompt files use YAML front matter (`mode: agent`, `description: ...`).
- Both share `AGENTS.md` as the operational guide loaded at session start.
- Both use the same `bd` CLI and beads database for task tracking.
