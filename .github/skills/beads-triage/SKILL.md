# /beads-triage

Assess and classify a new piece of work into a properly structured beads issue. Use this when you have a raw idea, bug report, or request that needs to become a beads issue with correct priority, type, and dependencies.

## Input

Describe the work in natural language. Example:
- "The CLI crashes when bd ready is run on an empty database"
- "We need a way to export all issues to CSV"
- "Refactor the dependency resolver to use topological sort"

## Steps

### 1. Check for duplicates

Search existing issues before creating anything new:

```bash
bd search "<keyword from your description>"
bd list --status open --json | grep -i "<keyword>"
```

If a duplicate exists, note the existing issue ID and stop — link to it instead of creating a new one.

### 2. Classify the work

Determine:

**Type:**
- `bug` — Something broken or producing incorrect results
- `feature` — New capability or behavior
- `task` — Implementation work, refactoring, migration
- `chore` — Maintenance, dependencies, tooling
- `epic` — Large feature that needs to be broken into subtasks

**Priority:**
- `0` — Critical: security, data loss, broken builds, blocks everything
- `1` — High: core feature, important bug, other work depends on it
- `2` — Medium: standard feature, non-critical bug (default)
- `3` — Low: polish, optimization, developer experience
- `4` — Backlog: future idea, nice-to-have

### 3. Identify dependencies

Ask: Does this work require anything to be done first?

```bash
bd list --status open --json  # Find potential blockers
```

Note the IDs of any issues that must complete before this one.

### 4. Create the issue

```bash
bd create \
    --title="<clear, actionable title — start with a verb>" \
    --description="<what needs to be done, why it matters, any context>" \
    --type=<type> \
    --priority=<0-4>
```

### 5. Add dependencies

```bash
# This issue is blocked by another
bd dep add <new-id> <blocker-id>

# This issue is related to (but not blocked by) another
bd dep add <new-id> <related-id> --type related
```

### 6. Confirm

```bash
bd show <new-id> --json
```

Report the new issue ID, title, type, priority, and any dependencies added.

## Rules

- Never create a duplicate — always search first
- Titles must start with a verb (Add, Fix, Create, Update, Refactor, ...)
- Descriptions must explain the *why*, not just restate the title
- When in doubt, default to priority 2 (medium)
- If it's too large for one iteration, create an epic and plan subtasks separately
