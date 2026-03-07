# Repository Restructuring

## Job To Be Done
Refactor the ralph-beads repository to cleanly reflect the layered architecture (Core, GitHub Repo, GitHub Projects) with agent-portable conventions, consolidated utilities, and clear documentation.

## Requirements

### Consolidate Shared Utilities
- Extract duplicated functions from gh-sync.sh, gh-triage.sh, gh-changelog.sh, gh-pr-body.sh into `scripts/lib.py`
- Shared module includes: subprocess runner, beads issue loader, GitHub issue number extractor, repo URL resolver, slugify, commit SHA lookup
- Each script imports from lib.py instead of defining its own copies
- lib.py uses only Python stdlib (no external dependencies)

### Guard Optional Layers
- GitHub scripts (gh-sync.sh, gh-triage.sh, etc.) fail fast with a clear message when `gh` CLI is not installed or not authenticated
- loop.sh `sync` and `triage` modes check for `gh` availability before delegating
- All GitHub functionality is skippable — the core loop works without it
- Document which features require which prerequisites (`bd` only vs `bd` + `gh` vs `bd` + `gh` + project)

### Clean Up Superseded Specs
- Archive or remove specs that have been superseded by the first-principles redesign:
  - `vscode-copilot-agent-integration.md` → superseded by `agent-portability.md`
  - `vscode-convention-parity.md` → superseded by `agent-portability.md`
  - `framework-resilience-and-observability.md` → largely implemented; remaining items folded into other specs
- Keep `github-actions-automation.md` and `ralph-beads-workflow-diagram.md` as independent concerns

### Documentation
- README.md clearly describes the layered architecture (L0 Core, L1 GitHub, L2 Projects)
- README.md has a quick-start for each layer (local-only, with GitHub, with Projects)
- README.md documents the agent portability story (Claude Code vs VS Code Copilot)
- A `docs/ARCHITECTURE.md` or README section shows the component diagram

### Verify Existing Implementations
- Audit loop.sh against the core-operating-model spec — confirm all requirements are met
- Audit scripts/ against the github-repo-integration spec — identify gaps
- Audit gh-project.sh against the github-projects-integration spec — identify gaps
- File beads issues for any gaps found

### Remove Dead Code
- Remove `src/__init__.py` and `main.py` if they are placeholder/unused files
- Remove `tests/` if empty or placeholder
- Clean up any other artifacts from initial project scaffolding that aren't part of the framework

## Constraints
- Must not break any currently-working functionality
- Refactoring is incremental — each task should be one commit, one beads issue
- Scripts must continue to work both from loop.sh and standalone
- Existing .beads/ issue history must be preserved

## Notes
- The `framework-resilience-and-observability.md` spec is mostly implemented: loop.sh already has timeouts (line 27-29), signal handling (lines 32-70), structured logging (lines 176-269), and pre-flight checks (lines 122-164). The remaining item (shared lib.py) is captured here.
- `src/__init__.py` and `main.py` appear to be Python project scaffolding that may not be needed since the framework is primarily shell scripts + beads
- This spec drives the refactoring work; the other specs (core, github-repo, github-projects, agent-portability) define the target state
