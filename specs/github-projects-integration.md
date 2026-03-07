# GitHub Projects Integration

## Job To Be Done
Extend the GitHub repository integration with optional GitHub Projects v2 board sync so that beads task state is reflected on a kanban board with columns, custom fields, and epic grouping.

## Requirements

### Project Board Management
- A GitHub Project (v2) board is created or adopted on first sync if one doesn't exist
- Board columns map to beads statuses: Backlog, Ready, In Progress, Done
- Issues move between columns automatically based on beads status changes during sync
- Priority and type are represented as custom Project fields
- Epic/subtask relationships are visible via GitHub's sub-issue or tasklist features

### Status-to-Column Mapping
| Beads Status | Project Column |
|---|---|
| open (no claim) | Backlog |
| open (ready, unclaimed) | Ready |
| open (claimed) | In Progress |
| closed | Done |
| blocked | Backlog (with "blocked" label) |

### Sync Integration
- Project board sync runs as part of `./loop.sh sync` after issue sync completes
- Also callable standalone via `scripts/gh-project.sh`
- Supports `--dry-run` for preview
- Idempotent — safe to run repeatedly

### Project Discovery
- If the repo has exactly one GitHub Project, use it automatically
- If multiple projects exist, require explicit selection via config or flag
- If no project exists, create one with the repo name and default columns

## Constraints
- Must use GitHub Projects v2 (GraphQL-based, via `gh api graphql`)
- Requires `gh` CLI authenticated with project write permissions
- Depends on GitHub Repository Integration (Layer 1) being configured — issues must exist before board placement
- Must not run if GitHub integration is not configured (fail gracefully)
- Must handle projects with custom column names that don't match defaults

## Notes
- This is Layer 2 of the architecture, building on GitHub Repository Integration (Layer 1)
- `scripts/gh-project.sh` already exists with basic functionality
- GitHub Projects v2 API uses GraphQL exclusively — the `gh api graphql` command handles auth and endpoint routing
- Project item mutations require the project's node ID, which must be discovered and cached
