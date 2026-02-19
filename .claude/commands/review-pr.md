---
description: Review code changes before creating a pull request
allowed-tools: Bash, Read, Grep, Task
argument-hint: "[base_branch]"
---

# Review Code Changes for Pull Request

Review your code changes before creating a pull request. Compares against the specified base branch (defaults to 'main').

**Base branch:** ${1:-main}

## Steps:

1. Check git status:
   !`git status`

2. Show staged and unstaged changes:
   !`git diff HEAD`

3. Compare with base branch:
   !`git diff ${1:-main}...HEAD`

4. Run comprehensive checks:

   a. Linting:
   ```bash
   ruff check .
   ```

   b. Formatting:
   ```bash
   ruff format --check .
   ```

   c. Tests:
   ```bash
   pytest -v --cov=. --cov-report=term-missing
   ```

   d. Type checking:
   ```bash
   mypy . --no-error-summary || true
   ```

5. Use the code-reviewer subagent to perform deep code review:
   - Check for bugs and logic errors
   - Review test coverage for changed code
   - Identify potential security issues
   - Assess code quality and maintainability
   - Verify adherence to Python best practices

6. Provide comprehensive PR readiness report:
   - Summary of changes
   - Code quality assessment
   - Test coverage status
   - Linting/formatting status
   - Recommendations before submitting PR
   - Suggested PR title and description

If code is not ready for PR, provide clear action items to address before submission.
