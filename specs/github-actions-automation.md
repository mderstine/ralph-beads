# GitHub Actions Automation

## Job To Be Done
Automate the sync, triage, project board, and changelog workflows via GitHub Actions so they run on relevant repository events without manual invocation.

## Requirements

### Issue Sync on Push (.github/workflows/beads-sync.yml)
- Trigger on push to `main` branch
- Run `scripts/gh-sync.sh` to sync beads issues to GitHub Issues
- Run `scripts/gh-project.sh` to update the project board
- Requires `bd` CLI and beads database available in the runner (install from npm, checkout .beads/)
- Use a GitHub App token or `GITHUB_TOKEN` with `issues: write` and `project: write` permissions

### Issue Triage on Label (.github/workflows/beads-triage.yml)
- Trigger on `issues.labeled` event when the label is `spec-candidate`
- Run `scripts/gh-triage.sh` to convert the issue into a spec file
- Commit the new spec file back to the repo (on a branch or directly to main)
- Post a comment on the issue confirming the spec was created

### Changelog on Release (.github/workflows/beads-changelog.yml)
- Trigger on `release.created` or manual `workflow_dispatch`
- Run `scripts/gh-changelog.sh --since <last-release-date> --output CHANGELOG.md`
- Attach the changelog as a release asset or commit it to the repo

### PR Body Generation (.github/workflows/beads-pr.yml)
- Trigger on `pull_request.opened` or `pull_request.synchronize`
- Run `scripts/gh-pr-body.sh --base ${{ github.event.pull_request.base.ref }}`
- Update the PR description with the generated body (only if the PR was created by the beads workflow or has a specific label)

### Label Bootstrap (.github/workflows/beads-labels.yml)
- Trigger on `workflow_dispatch` (manual) or repository creation
- Run `scripts/gh-labels.sh` to ensure all beads labels exist
- Idempotent -- safe to run repeatedly

### Shared Workflow Concerns
- All workflows must install `bd` CLI (`npm install -g @beads/bd`) and checkout the `.beads/` directory
- Create a reusable composite action (`.github/actions/setup-beads/action.yml`) that handles bd installation and beads database setup
- Workflows must not run on forks (guard with `if: github.repository == '<owner>/<repo>'` or similar)
- All workflows support `--dry-run` via workflow_dispatch inputs for testing

## Constraints
- Must use GitHub-hosted runners (no self-hosted infrastructure)
- Must not require Claude API access (these are metadata/sync workflows, not build workflows)
- `bd` CLI must be installable via npm in the runner environment
- Beads database (.beads/) must be committed to the repo for workflows to access it
- Workflows must be opt-in: they should be documented but not break repos that don't use GitHub Actions
- Total workflow runtime should stay under 5 minutes per trigger

## Notes
- The build loop itself (`./loop.sh` / `./loop.sh plan`) is NOT a good candidate for GitHub Actions -- it requires Claude API access, long runtimes, and interactive oversight; keep it local
- The sync/triage/changelog scripts are already designed to be non-interactive and idempotent, making them ideal for CI
- Consider a "beads status check" workflow that runs on PRs to verify all referenced beads issues exist and are in the expected state
- The composite action for bd setup could be published separately for reuse by other beads-based projects
