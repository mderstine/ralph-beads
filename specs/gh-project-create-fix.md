# GitHub Project Creation Fix

## Job To Be Done
Fix the init-time GitHub Project creation so that selecting "Create a new project" produces a fully configured project with Status columns.

## Requirements
- When the user confirms project creation during `purser-init`, the new project must be created with the default Status columns: Backlog, Ready, In Progress, Done
- `_configure_status_field()` in `scripts/gh_project_setup.py` must handle the case where the Status field does not yet exist on the newly created project (create it, then configure options)
- If field creation or configuration fails, log a clear warning (do not silently return)
- Acceptance: running `uv run purser-init` on a fresh repo, answering "Y" to project creation, produces a GitHub Project board with all four default Status columns visible in the GitHub UI

## Constraints
- Use the GitHub GraphQL API (`createProjectV2Field` mutation) to create the Status field when absent
- The `DEFAULT_COLUMNS` list (`scripts/gh_project_setup.py:29`) defines the required columns and colors
- No external libraries beyond `gh` CLI and stdlib

## Notes
- Root cause: `_configure_status_field()` queries for an existing Status field and silently returns when it finds none (lines 256, 261, 270 of `gh_project_setup.py`); newly created GitHub Projects v2 have no Status field until one is explicitly created
- `gh_project.py` already has a `create_single_select_field()` helper that may be reusable or serve as a reference
- The function should: (1) check for existing Status field, (2) create it if absent via `createProjectV2Field`, (3) update options to match `DEFAULT_COLUMNS`
