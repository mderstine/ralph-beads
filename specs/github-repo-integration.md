# GitHub Repository Integration

## Job To Be Done
Enable optional bidirectional sync between the local beads task tracker and a remote GitHub repository's Issues, so that beads-tracked work is visible on GitHub and GitHub Issues can flow back as spec input.

## Requirements

### Outbound Sync (beads → GitHub Issues)
- `bd` issues sync to GitHub Issues with title, description, priority (as labels), type (as labels), and status mapping
- GitHub Issue numbers stored as `external_ref` on beads issues to maintain linkage
- Sync is invocable via `./loop.sh sync` or `scripts/gh-sync.sh` — never implicit
- Sync is idempotent: running twice produces no duplicates or spurious updates
- Conflict resolution: beads is source of truth for task state; GitHub is source of truth for discussion/comments

### Inbound Triage (GitHub Issues → specs)
- GitHub Issues labeled `spec-candidate` are candidates for formalization into `specs/` files
- `./loop.sh triage` or `scripts/gh-triage.sh` lists and processes unprocessed spec-candidate issues
- Triage produces a draft spec file in `specs/` from the issue body, preserving the GitHub Issue link as provenance
- Originating GitHub Issue gets a comment linking to the spec and a `spec-created` label
- The planning loop naturally picks up new specs and decomposes them — closing the feedback loop

### Narrative Artifacts
- Build iterations that close a beads issue with an `external_ref` post a closing comment on the linked GitHub Issue (commit SHA + close reason)
- Git commits reference GitHub Issue numbers (`Closes #N`) for auto-close
- A changelog generator (`./loop.sh changelog` or `scripts/gh-changelog.sh`) reads closed beads issues and produces a markdown summary grouped by epic/type
- PR body generation (`scripts/gh-pr-body.sh`) summarizes beads issues addressed in a branch

### Label Convention
| Beads Field | GitHub Label Format | Examples |
|---|---|---|
| type | `type:<value>` | `type:bug`, `type:feature` |
| priority | `priority:<0-4>` | `priority:0`, `priority:2` |
| epic | `epic:<title>` | `epic:github-integration` |
| triage | `spec-candidate` | marks for spec triage |
| triage | `spec-created` | spec was generated |

### Label Bootstrap
- `scripts/gh-labels.sh` ensures all beads labels exist on the GitHub repo
- Idempotent — safe to run repeatedly

### Status Mapping
| Beads Status | GitHub Issue State |
|---|---|
| open (no claim) | open |
| open (claimed) | open |
| closed | closed |

### Dry-Run Support
- All sync/triage/changelog commands support `--dry-run` to preview changes without side effects

## Constraints
- Uses `gh` CLI for all GitHub operations — no direct API calls, no token management beyond `gh auth`
- Must not break the local-only workflow — GitHub sync is entirely opt-in
- `gh` CLI must be installed and authenticated; scripts fail fast with a clear message if not
- Must handle repos without a GitHub remote gracefully (skip or warn)
- Scripts are standalone bash/python callable from `loop.sh` or independently
- No webhook or GitHub App infrastructure — this is CLI-driven and developer-local

## Notes
- This is Layer 1 of the architecture, building on the Core Operating Model (Layer 0)
- GitHub Projects board sync is a separate concern (Layer 2) defined in `specs/github-projects-integration.md`
- The scripts (`gh-sync.sh`, `gh-triage.sh`, `gh-changelog.sh`, `gh-labels.sh`, `gh-pr-body.sh`) already exist and are functional
- Shared utility functions should be consolidated into `scripts/lib.py` to reduce duplication across scripts
