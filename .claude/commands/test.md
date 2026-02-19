---
description: Run tests with coverage reporting
allowed-tools: Bash, Read
argument-hint: "[pytest_args]"
---

# Run Tests with Coverage

Run pytest with coverage reporting. Pass additional pytest arguments if needed (e.g., `-k test_name`, `-m "not slow"`).

**Additional args:** $ARGUMENTS

## Steps:

1. Run pytest with coverage:
   ```bash
   pytest -v --cov=. --cov-report=term-missing --cov-report=html $ARGUMENTS
   ```

2. Display the test results:
   - Show number of tests passed/failed
   - Display coverage percentage
   - Highlight any uncovered lines
   - Note any slow tests

3. If tests fail:
   - Summarize which tests failed
   - Show the failure reasons
   - Suggest potential fixes

4. Coverage analysis:
   - Report overall coverage percentage
   - Identify files with low coverage
   - Note: HTML coverage report available at `htmlcov/index.html`

Provide a summary of test health and coverage status.
