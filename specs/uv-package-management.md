# UV Package Management

## Job To Be Done
Use uv as the Python package manager and virtual environment tool for the project.

## Requirements
- `pyproject.toml` fully defines project metadata, dependencies, and dev dependencies (already exists, may need cleanup)
- `uv venv` creates the virtual environment during project initialization (`init.sh`)
- `uv sync` installs dependencies during initialization
- All Python invocations in scripts (`loop.sh`, `init.sh`, `scripts/`) use `uv run` instead of bare `python3`
- `uv` is listed as a prerequisite in `scripts/prereqs.py`
- `CLAUDE.md` and `README.md` document uv as the package manager
- Duplicate `[project.optional-dependencies] dev` and `[dependency-groups] dev` in `pyproject.toml` are reconciled (keep `[dependency-groups]` per PEP 735)

## Constraints
- uv must be installed on the host (`pip install uv` or `curl` installer)
- Python >= 3.12 (already specified in pyproject.toml)
- `init.sh` must remain idempotent — skip venv creation if `.venv/` already exists
- Scripts must not break if run outside the venv (uv run handles this)

## Notes
- uv is the fastest Python package manager; aligns with modern Python tooling
- `uv run` auto-activates the venv, so no `source .venv/bin/activate` is needed in scripts
- The `.venv/` directory should be in `.gitignore`
