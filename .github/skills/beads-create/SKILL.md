# /beads-create

Create a new beads issue with duplicate checking. Use this when you have a clear, specific piece of work to track and want to ensure it doesn't already exist.

## Input

Provide:
- A title (or a description to derive one from)
- Optionally: type, priority, parent epic ID, or blocker IDs

## Steps

### 1. Check for duplicates

```bash
bd search "<keywords from title>"
```

If a match is found, show the existing issue and stop. Do not create a duplicate.

### 2. Create the issue

```bash
bd create \
    --title="<actionable title starting with a verb>" \
    --description="<what needs to be done and why>" \
    --type=task|bug|feature|epic|chore \
    --priority=<0-4> \
    --json
```

**Priority guide:**
| Priority | When to use |
|----------|-------------|
| 0 | Critical — security, data loss, broken build |
| 1 | High — core feature, blocks other work |
| 2 | Medium — standard work (default) |
| 3 | Low — polish, optimization |
| 4 | Backlog — future idea |

### 3. Link dependencies (if any)

```bash
# This issue is blocked by another issue
bd dep add <new-id> <blocker-id>

# This issue was discovered while working on another
bd dep add <new-id> <parent-id> --type discovered-from

# This issue is a child of an epic
bd dep add <new-id> <epic-id> --type parent-child
```

### 4. Confirm

```bash
bd show <new-id> --json
```

Report the new issue ID, title, and any dependencies added.

## Rules

- Always search for duplicates before creating
- Title must be a clear action: "Fix X", "Add Y", "Refactor Z"
- Description must add context beyond the title
- Default priority is 2 unless there's a clear reason for another level
