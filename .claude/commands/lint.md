---
description: Run linting checks on Python code
allowed-tools: Bash, Read, Grep
argument-hint: "[file_or_directory]"
---

# Run Linting Checks

Run Ruff linter on the specified files or directory (defaults to current directory if not specified).

**Target:** $ARGUMENTS

## Steps:

1. Run Ruff linter to check for code quality issues:
   ```bash
   ruff check $ARGUMENTS
   ```

2. Check formatting with Ruff:
   ```bash
   ruff format --check $ARGUMENTS
   ```

3. Run Mypy type checker (advisory only):
   ```bash
   mypy $ARGUMENTS --no-error-summary || true
   ```

4. Summarize the findings:
   - Report any errors or warnings found
   - Suggest fixes for common issues
   - Note any files that need attention

If no issues found, confirm that the code passes all linting checks.
