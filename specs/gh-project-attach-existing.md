# GitHub Project Attach to Existing

## Job To Be Done
Allow the user to connect their repository to an existing GitHub Project during `purser-init`.

## Requirements
- When no project is detected during init, the user must be offered three choices: (1) attach to an existing project, (2) create a new project, (3) skip
- Choice 1 lists the user's existing GitHub Projects (both personal and org) and lets the user pick one
- The selected project is linked to the repository and its number saved to `.purser.yml`
- If the user's account has no existing projects, choice 1 is shown but gracefully informs the user and returns to the menu
- Acceptance: `uv run purser-init` on a repo that already has a GitHub Project board lets the user select it from a numbered list

## Constraints
- `init.py`'s `step_github_project()` currently calls `detect_or_setup(check_only=True)` and presents its own simple Y/n prompt — this must be replaced with a call to `detect_or_setup(check_only=False)` so the full three-choice menu in `gh_project_setup.py` is used
- `gh_project_setup.detect_or_setup()` already implements `list_owner_projects()`, `link_project_to_repo()`, and the menu UI — reuse it, do not duplicate
- No new dependencies

## Notes
- `gh_project_setup.py` already has a working `detect_or_setup(check_only=False)` path with all three choices (lines 454–506) — the fix in `init.py` is small: remove the hand-rolled prompt and delegate entirely to `detect_or_setup()`
- `list_owner_projects(owner)` fetches both user-owned and org-owned projects via GraphQL (lines 115–164)
- `link_project_to_repo()` performs the GraphQL mutation to associate a project with a repo (lines 167–191)
