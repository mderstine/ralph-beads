# GitHub Enterprise Server Support

## Job To Be Done
Make the Purser framework detect and connect to repositories hosted on GitHub Enterprise Server instances (e.g. `github.wellsfargo.com`), not just `github.com`.

## Requirements

### URL Parsing (`gh_remote.py: _parse_github_url`)
- Regex patterns must match any GitHub-like hostname, not just `github.com`
- Specifically handle: `git@<host>:owner/repo.git`, `https://<host>/owner/repo.git`, `ssh://git@<host>/owner/repo.git`
- Return a 3-tuple `(host, owner, repo)` instead of 2-tuple, so the caller knows the hostname
- All downstream consumers of `_parse_github_url` must be updated for the new return shape
- The remote dict should include a `"host"` field alongside `owner` and `repo`

### Remote Connection (`gh_remote.py: connect_existing`)
- `connect_existing()` hardcodes `git@github.com:{owner}/{repo}.git` — must use the detected or configured hostname
- When connecting to an existing repo interactively, prompt should accept `host:owner/repo` or default to the configured/detected hostname

### gh CLI Compatibility
- `gh` supports GHE via `gh auth login -h <hostname>` — no code changes needed for `gh repo view`, `gh repo create`, etc. as long as the user is authenticated
- The auth refresh hint in `gh_project.py:563` hardcodes `github.com` — make it use the detected hostname

### Validation
- `validate_remote()` already calls `gh repo view owner/repo` which works with GHE — no change needed
- `_detect_via_gh_cli()` auto-detects from git config — works with GHE — no change needed

## Constraints
- Python stdlib only (no third-party imports)
- Must not break existing `github.com` behavior — that's the default when no explicit host is configured
- The `gh` CLI handles GHE authentication; Purser should not manage tokens or auth

## Notes
- GitHub Enterprise URLs look like: `https://github.wellsfargo.com/org/repo`, `git@github.wellsfargo.com:org/repo.git`
- The hostname does NOT always contain "github" — some enterprises use custom domains like `git.corp.example.com`
- The `gh` CLI uses `GH_HOST` env var or `gh auth status` to determine which host to target
- Consider adding a `github.host` config field in `.purser.yml` (default: `github.com`) so users can configure once
- The `_detect_via_gh_cli()` fallback is the most reliable approach for GHE since it auto-detects from git config
- Affected files: `gh_remote.py` (primary), `gh_project.py` (auth hint), `lib.py` (URL conversion — already generic)
