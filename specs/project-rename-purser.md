# Project Rename to Purser

## Job To Be Done
Rename the project from "Ralph-Beads" to "Purser" across all code, configuration, documentation, and file references.

## Requirements
- All instances of "Ralph-Beads" (title case) become "Purser"
- All instances of "ralph-beads" (kebab case) become "purser"
- All instances of "ralph_beads" (snake case) become "purser"
- All instances of "RALPH" in variable names (e.g., RALPH_TIMEOUT) become "PURSER" (e.g., PURSER_TIMEOUT)
- `pyproject.toml` project name updated to "purser"
- `.ralph-beads.yml` config file renamed to `.purser.yml`
- `.ralph-beads.example.yml` renamed to `.purser.example.yml`
- All scripts referencing the config filename updated
- `loop.sh` log prefixes and references updated
- `init.sh` references updated
- All markdown docs (CLAUDE.md, README.md, AGENTS.md, PROMPT_*.md) updated
- All `.claude/commands/*.md` slash command files updated
- All `.github/` adapter files updated
- All `specs/` files updated (including renaming `specs/ralph-beads-workflow-diagram.md`)
- All test files updated
- Credits to Ralph Loop (Geoffrey Huntley) and Beads (Steve Yegge) preserved in README.md
- The beads database prefix remains unchanged (beads issues keep their IDs)

## Constraints
- Do NOT rename the git repository itself (that's a GitHub operation the user handles)
- Do NOT rename the `.beads/` directory or beads issue IDs
- Do NOT change "Ralph Loop" when it refers to the methodology/credit (keep attribution)
- Do NOT change "Beads" when it refers to the tool/library (keep attribution)
- The word "Ralph" in "Ralph Loop" (the methodology name) stays — only "Ralph-Beads" (the project name) changes

## Notes
- "Purser" is an homage to the British Royal Navy officer position tasked with keeping track of tasks on vessels
- The rename touches 40+ files — should be split into manageable chunks
- Suggested split: config/scripts first, then docs, then adapter files
- After rename, `grep -ri "ralph.beads" .` should return zero results (excluding .beads/ and .git/)
