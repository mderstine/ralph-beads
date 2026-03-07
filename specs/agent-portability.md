# Agent Portability

## Job To Be Done
Make the purser operating model work with multiple AI agent frontends (Claude Code, VS Code Copilot, and future agents) by separating agent-neutral conventions from agent-specific configuration adapters.

## Requirements

### Agent-Neutral Core Files
- `AGENTS.md` — operational guide (build commands, bd CLI reference, coding standards, workflow rules) usable by any agent
- `PROMPT_plan.md` and `PROMPT_build.md` — describe what to do in agent-neutral terms (these are consumed by loop.sh for Claude Code but serve as reference for other agents)
- `specs/` — requirement documents readable by any agent
- `.beads/` — task database accessible via `bd` CLI from any agent's shell

### Claude Code Adapter
- `CLAUDE.md` — project instructions loaded automatically by Claude Code
- `.claude/commands/*.md` — slash commands (plan, build, status, add-spec, create-issue)
- `loop.sh` — the Ralph Loop orchestrator that drives Claude Code in headless mode
- These files are Claude Code-specific but must not contain logic that contradicts the agent-neutral files

### VS Code Copilot Adapter
- `.github/copilot-instructions.md` — repo-level instructions equivalent to CLAUDE.md content relevant to VS Code agents
- `.github/prompts/*.prompt.md` — prompt files equivalent to `.claude/commands/` slash commands, using VS Code front matter (`mode`, `tools`, `description`)
- Agent instructions encode the same build loop (bd ready → implement → bd close) and plan loop (specs → task graph)
- VS Code agents can invoke `bd` CLI via terminal tool
- One-task-per-session discipline is preserved (VS Code doesn't have loop.sh, so the agent self-limits)

### Parity Requirements
- Both adapters must express the same workflow: plan mode and build mode
- Both must reference `AGENTS.md` for operational guidance
- Both must enforce backpressure (quality gates before commits)
- Both must support discovered-work linking via `bd create --deps discovered-from:<id>`
- A mapping document or README section explains which Claude Code file maps to which VS Code file

### Adapter Independence
- Removing all `.claude/` files must not break VS Code Copilot operation
- Removing all `.github/prompts/` files must not break Claude Code operation
- The agent-neutral core (AGENTS.md, specs/, .beads/) is the shared foundation

## Constraints
- VS Code 1.108.2+ Copilot agent mode — no extensions beyond GitHub Copilot
- `.claude/` directory and contents must remain intact for Claude Code users
- VS Code prompt files live in `.github/prompts/` per VS Code conventions
- No runtime dependency between adapters — they are parallel, not layered
- Memory/persistence between sessions is out of scope for VS Code (no equivalent to `.claude/projects/*/memory/`)

## Notes
- User has a reference repo: https://github.com/mderstine/beads-vscode-agents with agents (beads-pm, beads-dev) and skills (workflow, create, triage)
- VS Code supports `.github/agents/*.agent.md` for named agents and `.github/skills/*.skill.md` for invocable skills — these may be used in addition to or instead of prompt files
- The Ralph Loop concept (loop.sh) doesn't directly apply to VS Code Copilot since it has its own iteration model — the VS Code adapter encodes the loop discipline in agent instructions rather than an external orchestrator
- This spec subsumes the previous `vscode-copilot-agent-integration.md` and `vscode-convention-parity.md` specs
