# Python Code Quality Tooling

## Job To Be Done
Use Astral's ruff for linting/formatting and ty for type checking as the project's code quality gates.

## Requirements
- `ruff` is used for linting and formatting Python code (`uv run ruff check`, `uv run ruff format`)
- `ty` is used for type checking Python code (`uv run ty check`), replacing `mypy`
- `pyproject.toml` includes `ruff` and `ty` in `[dependency-groups] dev`, removing `mypy`
- `pyproject.toml` includes a `[tool.ruff]` configuration section (target Python 3.12, sensible defaults)
- All references to `mypy` across docs and config files are replaced with `ty`
- `AGENTS.md` build commands use `uv run ruff check` and `uv run ty check`
- `PROMPT_build.md` validation phase uses `uv run ruff check` and `uv run ty check`
- VS Code Copilot adapter files (`.github/`) reference ruff and ty instead of mypy
- Quality gate commands are uncommented and active in `AGENTS.md` (not template comments)

## Constraints
- Both tools are from Astral (same ecosystem as uv)
- ruff replaces both linting and formatting (no need for black/isort)
- ty replaces mypy for type checking
- Must update all files that reference mypy or python quality tooling

## Notes
- ruff is already in `pyproject.toml` dev dependencies
- mypy is in `pyproject.toml` dev dependencies and should be replaced with ty
- References to mypy/ruff exist in: AGENTS.md, PROMPT_build.md, .github/copilot-instructions.md, .github/agents/beads-dev.agent.md, .github/skills/beads-workflow/SKILL.md
