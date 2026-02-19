---
description: Automatically fix linting and formatting issues
allowed-tools: Bash, Read, Edit, Write
argument-hint: "[file_or_directory]"
---

# Fix Linting and Formatting Issues

Automatically fix linting and formatting issues in the specified files or directory.

**Target:** $ARGUMENTS

## Steps:

1. Run Ruff linter with auto-fix:
   ```bash
   ruff check --fix $ARGUMENTS
   ```

2. Format code with Ruff:
   ```bash
   ruff format $ARGUMENTS
   ```

3. Sort imports (included in Ruff):
   ```bash
   ruff check --select I --fix $ARGUMENTS
   ```

4. Show a summary of changes:
   - List files that were modified
   - Describe the types of fixes applied
   - Note any issues that require manual intervention

5. Verify the fixes:
   ```bash
   ruff check $ARGUMENTS
   ```

6. If issues remain:
   - List the remaining issues
   - Explain why they can't be auto-fixed
   - Provide guidance on how to fix them manually

Provide a summary of all fixes applied and any remaining issues.
