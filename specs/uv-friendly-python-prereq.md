# UV/Windows-Friendly Python Prerequisite Check

## Job To Be Done
Make the prerequisite checker find Python regardless of whether the binary is named `python3` or `python`, so it works in uv-managed environments and on Windows.

## Requirements
- `prereqs.py` must check for `python3` first, then fall back to `python`
- On Windows, only check `python` (there is no `python3` binary)
- The reported tool name should remain `python3` in output for consistency, but the detected version should come from whichever binary was found
- `init.py` references `tool_map.get("python3", False)` — this must still work after the change
- Minimum version check: the found Python must be 3.12+ (parse the version string)
- Install instructions should stay platform-appropriate (no change needed)

## Constraints
- Python stdlib only (no third-party imports) — matches existing prereqs.py convention
- Must not break existing Linux/macOS behavior where `python3` exists

## Notes
- `uv` installs Python as `python` not `python3` in its managed environments
- Windows has historically used `python` (and the Python Launcher `py`)
- Consider also checking `py -3 --version` on Windows as a third fallback
- The `_get_version()` helper already returns `None` on `FileNotFoundError`, so fallback logic can simply try multiple commands in order
