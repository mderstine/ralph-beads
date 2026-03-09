# Improve GitHub Remote Detection and Setup Flow

## Job To Be Done
Make init reliably detect GitHub remotes on cloned repos and offer "connect to existing" as an alternative to "create new" when detection fails.

## Requirements

### Improve Detection
- After `git remote -v` parsing, fall back to `gh repo view --json` in the current directory to detect the GitHub repo even when URL parsing fails
- Handle `url.<base>.insteadOf` rewrites by resolving the effective URL via `git remote get-url <name>` (which applies insteadOf rules) instead of parsing raw `-v` output
- Add a final fallback: parse `.git/config` `[remote "origin"]` section directly if `git remote` commands fail

### Improve Interactive Flow When No Remote Detected
- When no GitHub remote is found and `auto_create != "skip"`, present the user with a numbered menu:
  1. **Connect to existing GitHub repository** — prompt for `owner/repo`, run `gh repo view` to validate, then `git remote add origin <url>`
  2. **Create a new GitHub repository** — current behavior (prompt for name and visibility)
  3. **Skip** — continue in local-only mode
- When connecting to an existing remote, offer to create a new branch (for the case where the user is setting up a second working copy)
- The `--check` flag must still skip all prompts (no behavior change)
- The `auto_create: auto` config must still auto-create without prompting (no behavior change)

### Return Value Consistency
- `detect_or_create()` return dict must add `"status": "connected"` for the connect-to-existing case
- The `init.py` `step_github_remote()` function must handle the new status

## Constraints
- Python stdlib only (no third-party imports)
- Must not break `--check`, `--json`, or `auto_create` config behavior
- `gh` CLI is optional — if missing, skip GitHub features gracefully (existing behavior)

## Notes
- The likely root cause on cloned repos is git's `url.<base>.insteadOf` config: the user may have `url.git@github.com:.insteadOf = https://github.com/` (or vice versa), making the raw remote URL look non-GitHub
- `git remote get-url origin` resolves insteadOf rules and returns the effective URL
- `gh repo view --json owner,name` run in a git repo auto-detects the GitHub repo without needing the URL at all — this is the most robust fallback
- The connect-to-existing flow is useful when the user clones a template and wants to point it at their own fork/repo
