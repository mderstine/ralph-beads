#!/usr/bin/env bash
# Create/update GitHub labels for beads metadata sync.
# Idempotent: skips labels that already exist (by name).
#
# Usage:
#   scripts/gh-labels.sh              # Create labels
#   scripts/gh-labels.sh --dry-run    # Preview without creating

set -euo pipefail

DRY_RUN=false
for arg in "$@"; do
    case "$arg" in
        --dry-run) DRY_RUN=true ;;
        -h|--help)
            echo "Usage: $0 [--dry-run]"
            echo "Create GitHub labels for beads metadata sync."
            exit 0
            ;;
    esac
done

# Verify gh is available and authenticated
if ! command -v gh &>/dev/null; then
    echo "Error: gh CLI not found. Install from https://cli.github.com/"
    exit 1
fi

if ! gh auth status &>/dev/null; then
    echo "Error: gh CLI not authenticated. Run: gh auth login"
    exit 1
fi

# Get existing labels
EXISTING=$(gh label list --json name -q '.[].name' 2>/dev/null)

create_label() {
    local name="$1"
    local color="$2"
    local description="$3"

    if echo "$EXISTING" | grep -qxF "$name"; then
        echo "  skip: $name (exists)"
        return
    fi

    if $DRY_RUN; then
        echo "  would create: $name ($description)"
    else
        gh label create "$name" --color "$color" --description "$description"
        echo "  created: $name"
    fi
}

echo "=== Beads GitHub Label Setup ==="
echo ""

# Issue types
echo "Issue types:"
create_label "type:bug"     "d73a4a" "Beads issue type: bug"
create_label "type:feature" "0e8a16" "Beads issue type: feature"
create_label "type:task"    "1d76db" "Beads issue type: task"
create_label "type:epic"    "5319e7" "Beads issue type: epic"
create_label "type:chore"   "c5def5" "Beads issue type: chore"

echo ""

# Priorities
echo "Priorities:"
create_label "priority:0" "b60205" "P0: Critical (security, data loss, broken builds)"
create_label "priority:1" "d93f0b" "P1: High (major features, important bugs)"
create_label "priority:2" "fbca04" "P2: Medium (default)"
create_label "priority:3" "c2e0c6" "P3: Low (polish, optimization)"
create_label "priority:4" "e4e669" "P4: Backlog (future ideas)"

echo ""

# Status/workflow
echo "Workflow:"
create_label "blocked"       "b60205" "Issue is blocked by dependencies"
create_label "spec-candidate" "006b75" "GitHub Issue to be triaged into a spec"
create_label "spec-created"   "0e8a16" "Spec was generated from this issue"

echo ""
echo "Done."
