#!/usr/bin/env bash
# Ralph-Beads Loop: Autonomous AI development with dependency-aware task tracking
#
# Usage:
#   ./loop.sh              # Build mode, unlimited iterations
#   ./loop.sh 20           # Build mode, max 20 iterations
#   ./loop.sh plan         # Planning mode, unlimited
#   ./loop.sh plan 5       # Planning mode, max 5 iterations
#   ./loop.sh sync         # Sync beads issues to GitHub (single-shot)
#   ./loop.sh triage       # Triage spec-candidate GitHub Issues (single-shot)
#   ./loop.sh changelog    # Generate changelog from closed issues (single-shot)

set -euo pipefail

MODE="build"
MAX_ITERATIONS=0
ITERATION=0
CLAUDE_PID=""           # PID of current Claude subshell; empty when idle
SHUTDOWN_REQUESTED=false
SIGNAL_GRACE=30         # Seconds to wait for Claude to exit before force-kill

# ─── Signal handling ──────────────────────────────────────────────────────────

print_summary() {
    echo ""
    echo "=== Loop finished after $ITERATION iteration(s) ==="
    bd prime 2>/dev/null || true
}

cleanup() {
    local sig="${1:-SIGINT}"
    SHUTDOWN_REQUESTED=true
    echo ""
    echo "=== Signal received ($sig). Shutting down gracefully... ==="

    if [[ -n "$CLAUDE_PID" ]] && kill -0 "$CLAUDE_PID" 2>/dev/null; then
        echo "Waiting for Claude (PID $CLAUDE_PID) to exit (grace: ${SIGNAL_GRACE}s)..."
        # Kill the entire process group to reach all pipeline members
        kill -TERM -- -"$CLAUDE_PID" 2>/dev/null || kill -TERM "$CLAUDE_PID" 2>/dev/null || true

        local elapsed=0
        while kill -0 "$CLAUDE_PID" 2>/dev/null && [[ $elapsed -lt $SIGNAL_GRACE ]]; do
            sleep 1
            elapsed=$((elapsed + 1))
        done

        if kill -0 "$CLAUDE_PID" 2>/dev/null; then
            echo "Grace period expired. Force-killing Claude..."
            kill -KILL -- -"$CLAUDE_PID" 2>/dev/null || kill -KILL "$CLAUDE_PID" 2>/dev/null || true
        else
            echo "Claude exited cleanly."
        fi
    fi

    print_summary
    exit 130
}

trap 'cleanup SIGINT'  INT
trap 'cleanup SIGTERM' TERM

# ─── Argument parsing ─────────────────────────────────────────────────────────

PASSTHROUGH_ARGS=()
for arg in "$@"; do
    case "$arg" in
        plan)      MODE="plan" ;;
        sync)      MODE="sync" ;;
        triage)    MODE="triage" ;;
        changelog) MODE="changelog" ;;
        --dry-run) PASSTHROUGH_ARGS+=("$arg") ;;
        *[0-9]*)   MAX_ITERATIONS="$arg" ;;
    esac
done

# ─── Single-shot modes: delegate to scripts and exit ──────────────────────────

case "$MODE" in
    sync)
        echo "=== Ralph-Beads: GitHub Sync ==="
        exec scripts/gh-sync.sh "${PASSTHROUGH_ARGS[@]}"
        ;;
    triage)
        echo "=== Ralph-Beads: Issue Triage ==="
        exec scripts/gh-triage.sh "${PASSTHROUGH_ARGS[@]}"
        ;;
    changelog)
        echo "=== Ralph-Beads: Changelog ==="
        exec scripts/gh-changelog.sh "${PASSTHROUGH_ARGS[@]}"
        ;;
esac

PROMPT_FILE="PROMPT_${MODE}.md"

if [[ ! -f "$PROMPT_FILE" ]]; then
    echo "Error: $PROMPT_FILE not found"
    exit 1
fi

# Verify bd is available
if ! command -v bd &>/dev/null; then
    echo "Error: bd (beads) CLI not found. Install with: npm install -g @beads/bd"
    exit 1
fi

echo "=== Ralph-Beads Loop ==="
echo "Mode: $MODE"
echo "Prompt: $PROMPT_FILE"
echo "Max iterations: ${MAX_ITERATIONS:-unlimited}"
echo "========================"

# ─── Main loop ────────────────────────────────────────────────────────────────

while true; do
    ITERATION=$((ITERATION + 1))

    if [[ "$MAX_ITERATIONS" -gt 0 && "$ITERATION" -gt "$MAX_ITERATIONS" ]]; then
        echo "Reached max iterations ($MAX_ITERATIONS). Stopping."
        break
    fi

    if [[ "$SHUTDOWN_REQUESTED" == "true" ]]; then
        break
    fi

    echo ""
    echo "--- Iteration $ITERATION ($(date '+%H:%M:%S')) ---"

    # Check if there's work to do (build mode only)
    if [[ "$MODE" == "build" ]]; then
        READY_COUNT=$(bd ready --json 2>/dev/null | python3 -c "import sys,json; print(len(json.load(sys.stdin)))" 2>/dev/null || echo "0")
        if [[ "$READY_COUNT" == "0" ]]; then
            echo "No ready work found. All tasks complete or blocked."
            echo "Run './loop.sh plan' to generate new tasks, or check blockers with 'bd list --status open'."
            break
        fi
        echo "Ready work: $READY_COUNT issue(s)"
    fi

    # Run Claude in a background subshell so we can track and signal it.
    # Exit code is written to a temp file since PIPESTATUS isn't available after wait.
    CLAUDE_EXITCODE_FILE=$(mktemp)
    (
        cat "$PROMPT_FILE" | claude -p \
            --output-format=stream-json \
            --verbose \
            --model opus \
            2>&1 | tee "/tmp/ralph-beads-iter-${ITERATION}.log"
        echo "${PIPESTATUS[1]:-0}" > "$CLAUDE_EXITCODE_FILE"
    ) &
    CLAUDE_PID=$!

    # Wait for Claude; interruptible by signal handler
    wait "$CLAUDE_PID" 2>/dev/null || true
    EXIT_CODE=$(cat "$CLAUDE_EXITCODE_FILE" 2>/dev/null || echo "1")
    rm -f "$CLAUDE_EXITCODE_FILE"
    CLAUDE_PID=""

    if [[ "$SHUTDOWN_REQUESTED" == "true" ]]; then
        break
    fi

    if [[ "$EXIT_CODE" -ne 0 ]]; then
        echo "Claude exited with code $EXIT_CODE. Pausing for review."
        echo "Press Enter to continue or Ctrl+C to stop."
        read -r
    fi

    echo "--- Iteration $ITERATION complete ---"
done

print_summary
