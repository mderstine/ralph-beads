# Python Coding Conventions

## Job To Be Done
Establish coding conventions in AGENTS.md so the agent writes modular, well-tested Python code using modern standards and preferred libraries.

## Requirements
- AGENTS.md Coding Standards section includes all conventions below
- Code must be developed modularly (small, focused functions with clear interfaces)
- All new functionality must have unit tests
- Use latest Python 3.12+ standards (match expressions, type unions with `|`, f-strings, etc.)
- Prefer Polars over Pandas for dataframe operations
- Prefer DuckDB over SQLite/other databases for analytical queries
- Only use Pandas when Polars or DuckDB solutions don't readily exist
- Polars method chains must be written vertically for readability:
  ```python
  result = (
      df
      .filter(
          pl.col("status") == "active"
      )
      .group_by(
          "category"
      )
      .agg(
          pl.col("value").sum()
      )
  )
  ```
- Each bracket/brace/paren in Polars chains on its own line

## Constraints
- These conventions apply to all Python code written by the agent
- Conventions must be in AGENTS.md so they are loaded every loop iteration
- Do not add Polars or DuckDB as project dependencies (they are for user projects, not the framework itself)

## Notes
- AGENTS.md already has a Coding Standards section with basic rules (Python 3.12+, type annotations, tests, small functions)
- The update should expand that section, not replace the existing rules
- The Polars formatting convention is about readability — long horizontal chains are hard to review
