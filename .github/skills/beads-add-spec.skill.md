# beads-add-spec Skill

## Purpose
Draft a polished spec from a user prompt and save it to the specs/ directory for review and approval.

## Usage
- Trigger: User provides a prompt describing a desired feature or change.
- Action: The agent generates a well-structured markdown spec and saves it as specs/<title>.md.
- The user reviews and edits the spec as needed before it enters the planning phase.

## Implementation
- Accepts a prompt (title + description) from the user.
- Uses LLM or template logic to expand the prompt into a detailed spec.
- Writes the output to specs/<slugified-title>.md.
- Notifies the user of the new file location.

## Example
User: "Add dark mode support."
Agent: Creates specs/add-dark-mode-support.md with a detailed spec for dark mode.

---

# beads-add-spec
- Input: User prompt
- Output: Markdown spec in specs/
- Review: User edits/approves before planning
