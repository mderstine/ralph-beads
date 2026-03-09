# Attach to Existing GitHub Project

## Job To Be Done
Allow users to connect their repository to an existing GitHub Project during init, instead of only offering to create a new one.

## Requirements

### Interactive Menu
- When no projects are linked to the repo, present a 3-option menu (similar to gh_remote.py's connect flow):
  1. Attach to an existing GitHub Project
  2. Create a new GitHub Project
  3. Skip (no project board)
- Current behavior only offers create/skip — add the attach option

### Attach Flow
- List all projects owned by the authenticated user (not just repo-linked ones) via `user.projectsV2` GraphQL query
- Display them in a numbered menu for selection
- After selection, link the project to the repository using the `linkProjectV2ToRepository` GraphQL mutation
- Return the same result dict shape (`status: "found"`, `project: {...}`) as other paths

### Affected Files
- `scripts/gh_project_setup.py` — main logic: new `list_owner_projects()` function, `link_project_to_repo()` function, updated `detect_or_create()` menu
- `scripts/init.py` — the init flow calls `gh_project_setup.detect_or_create()` which already handles the result dict, so init.py likely needs no changes
- `tests/test_gh_project_setup.py` — new tests for the attach flow

## Constraints
- Python stdlib only
- GraphQL via `gh api graphql` (no direct API tokens)
- Must not break existing create flow
- The `linkProjectV2ToRepository` mutation requires the project node ID and repo node ID

## Notes
- `list_projects()` currently queries `repository.projectsV2` — the new function needs `viewer.projectsV2` to find all the user's projects regardless of repo linkage
- The `_get_repo_id()` helper already exists for getting the repo node ID
- Organization-owned projects may need `organization.projectsV2` query — consider supporting both user and org projects
- The existing `_prompt_select()` function can be reused for the project selection menu
