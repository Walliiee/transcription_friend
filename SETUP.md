# Development Setup Guide

Complete guide for setting up linting, testing, and PR workflows for this Python project.

## Table of Contents

1. [Quick Start](#quick-start)
2. [Tool Installation](#tool-installation)
3. [Local Development](#local-development)
4. [GitHub Integration](#github-integration)
5. [Claude Code Integration](#claude-code-integration)
6. [Workflow Guide](#workflow-guide)
7. [Troubleshooting](#troubleshooting)

---

## Quick Start

### 1. Install Development Dependencies

```bash
# Install all dev dependencies
pip install -e ".[dev]"

# Or install individually
pip install pytest pytest-cov ruff black mypy pre-commit
```

### 2. Set Up Pre-commit Hooks

```bash
# Install pre-commit hooks
pre-commit install

# Run hooks on all files (first time)
pre-commit run --all-files
```

### 3. Verify Setup

```bash
# Run linting
ruff check .

# Run tests
pytest -v

# Run with coverage
pytest --cov=. --cov-report=html
```

---

## Tool Installation

### Python Version

This project supports Python 3.8+. Recommended: Python 3.11

```bash
python --version  # Should be 3.8 or higher
```

### Core Development Tools

```bash
# Ruff - Fast Python linter and formatter
pip install ruff

# Black - Code formatter (optional, ruff can format)
pip install black

# Mypy - Static type checker
pip install mypy

# Pytest - Testing framework
pip install pytest pytest-cov

# Pre-commit - Git hooks
pip install pre-commit
```

### Installing from pyproject.toml

```bash
# Install project in editable mode with dev dependencies
pip install -e ".[dev]"

# This installs:
# - Core dependencies (torch, faster-whisper)
# - Dev dependencies (pytest, ruff, mypy, etc.)
```

---

## Local Development

### Running Linting

```bash
# Check for issues
ruff check .

# Auto-fix issues
ruff check --fix .

# Check formatting
ruff format --check .

# Apply formatting
ruff format .

# Run all checks
ruff check . && ruff format --check .
```

### Running Tests

```bash
# Run all tests
pytest -v

# Run with coverage
pytest --cov=. --cov-report=term-missing --cov-report=html

# Run specific test file
pytest tests/test_module.py -v

# Run tests matching pattern
pytest -k "transcription" -v

# Run tests with marker
pytest -m "not slow" -v

# Stop on first failure
pytest -x -v

# View coverage report
# Open htmlcov/index.html in browser
```

### Running Type Checking

```bash
# Check all files
mypy .

# Check specific file
mypy file.py

# Ignore missing imports (for third-party libraries)
mypy . --ignore-missing-imports
```

### Pre-commit Hooks

Pre-commit runs automatically on `git commit`, but you can run manually:

```bash
# Run on all files
pre-commit run --all-files

# Run on staged files only
pre-commit run

# Run specific hook
pre-commit run ruff

# Update hooks to latest versions
pre-commit autoupdate

# Skip hooks for one commit (use sparingly!)
git commit --no-verify -m "message"
```

---

## GitHub Integration

### GitHub Actions

Two workflows are configured:

1. **Lint Workflow** (`.github/workflows/lint.yml`)
   - Runs on PRs and pushes to main
   - Checks code quality with ruff, black, mypy
   - Posts PR comments with results
   - **Currently advisory** (won't block PRs initially)

2. **Test Workflow** (`.github/workflows/test.yml`)
   - Runs on PRs and pushes to main
   - Tests on Python 3.8, 3.9, 3.10, 3.11, 3.12
   - Generates coverage reports
   - Uploads coverage to Codecov (if configured)
   - **Currently advisory** (won't block PRs initially)

### Enabling Required Checks

Once your codebase is ready, enable required checks:

1. Go to repository **Settings** → **Branches**
2. Add branch protection rule for `main`
3. Enable **Require status checks to pass**
4. Select checks: `Lint`, `Test`
5. Enable **Require branches to be up to date**

### PR Template

When creating a PR, you'll see a template with checklist:
- Type of change (bug fix, feature, etc.)
- Testing checklist
- Code quality checklist
- Boy scout rule verification

Fill out all relevant sections.

---

## Claude Code Integration

### Slash Commands

Four slash commands are available:

#### `/lint [path]`
Run linting checks on code.

```bash
/lint                    # Check current directory
/lint src/module.py      # Check specific file
```

#### `/test [args]`
Run tests with coverage.

```bash
/test                    # Run all tests
/test -k "transcription" # Run tests matching pattern
/test -m "not slow"      # Run fast tests only
```

#### `/fix-lint [path]`
Auto-fix linting and formatting issues.

```bash
/fix-lint                # Fix all files
/fix-lint src/module.py  # Fix specific file
```

#### `/review-pr [branch]`
Review code before creating PR.

```bash
/review-pr               # Compare with main
/review-pr develop       # Compare with develop
```

### Skills

Two skills provide domain expertise:

#### `python-testing`
Automatically invoked when working with tests.

Provides guidance on:
- Writing pytest tests
- Using fixtures and parametrization
- Coverage analysis
- Testing best practices

#### `python-quality`
Automatically invoked when working with code quality.

Provides guidance on:
- Ruff linting rules
- Code formatting
- Type hints
- Python best practices

### Subagents

Three specialized agents for specific tasks:

#### `code-reviewer`
Deep code review analysis.

Usage:
```
Use the code-reviewer agent to review my changes
```

Provides:
- Bug detection
- Security analysis
- Test coverage assessment
- Quality recommendations

#### `test-runner`
Execute and analyze tests.

Usage:
```
Use the test-runner agent to run all tests
```

Provides:
- Test execution
- Failure analysis
- Coverage reporting
- Debugging guidance

#### `lint-fixer`
Auto-fix code quality issues.

Usage:
```
Use the lint-fixer agent to fix linting issues
```

Provides:
- Automatic fixes
- Formatting
- Import sorting
- Change summary

---

## Workflow Guide

### Daily Development Workflow

1. **Create feature branch**
   ```bash
   git checkout -b feature/my-feature
   ```

2. **Write code**
   - Make changes
   - Run `/lint` frequently
   - Run `/test` to verify

3. **Boy scout rule** (before commit)
   ```bash
   # Fix files you touched
   /fix-lint src/modified_file.py
   ```

4. **Commit** (pre-commit runs automatically)
   ```bash
   git add .
   git commit -m "feat: add new feature"
   # Pre-commit hooks run and auto-fix issues
   # If hooks modify files, review and commit again
   ```

5. **Before creating PR**
   ```bash
   /review-pr
   # Review output, fix any issues
   ```

6. **Create PR**
   - Push branch
   - Create PR on GitHub
   - Fill out PR template
   - Wait for CI checks
   - Address reviewer feedback

### Incremental Legacy Code Improvement

Follow the **boy scout rule**: Leave code cleaner than you found it.

**When touching a legacy file:**

1. **Fix formatting first**
   ```bash
   ruff format path/to/file.py
   ```

2. **Fix auto-fixable issues**
   ```bash
   ruff check --fix path/to/file.py
   ```

3. **Add type hints** (optional, gradual)
   ```python
   def process(file: str) -> str:  # Add hints to new/modified functions
       pass
   ```

4. **Add tests** (if making logic changes)
   ```python
   def test_process():
       assert process("test.m4a") == "expected"
   ```

**Don't:**
- Modify unrelated legacy code in the same PR
- Reformat entire files you're not changing
- Add tests for code you're not modifying

**Do:**
- Clean up imports in files you touch
- Fix linting issues in code you modify
- Add tests for new functionality

### Creating a Pull Request

1. **Self-review**
   ```bash
   /review-pr
   ```

2. **Check diff**
   ```bash
   git diff main...HEAD
   ```

3. **Verify tests pass**
   ```bash
   /test
   ```

4. **Push and create PR**
   ```bash
   git push -u origin feature/my-feature
   # Create PR on GitHub
   ```

5. **Fill out PR template**
   - Description of changes
   - Type of change
   - Testing performed
   - Checklist items

6. **Wait for CI checks**
   - Lint workflow
   - Test workflow
   - Fix any failures

7. **Request review**
   - Tag reviewers
   - Address feedback
   - Push fixes

8. **Merge**
   - Squash and merge (preferred)
   - Delete branch after merge

---

## Troubleshooting

### Pre-commit Hooks Failing

**Issue:** Pre-commit modifies files then fails

**Solution:**
```bash
# Review changes made by pre-commit
git diff

# Add the auto-fixed changes
git add .

# Retry commit
git commit -m "your message"
```

### Ruff Linting Errors

**Issue:** Ruff reports unfixable errors

**Solution:**
```bash
# See what's wrong
ruff check .

# Check specific file
ruff check path/to/file.py

# Ignore specific line (use sparingly)
# Add comment:
result = function()  # noqa: E501

# Ignore specific rule for file (add to top)
# ruff: noqa: E501
```

### Tests Failing Locally

**Issue:** Tests fail on your machine

**Solution:**
```bash
# Run with verbose output
pytest -v -s

# Run specific failing test
pytest tests/test_module.py::test_name -v -s

# Check for GPU-related failures
pytest -m "not gpu" -v  # Skip GPU tests

# Check Python version compatibility
python --version  # Should be 3.8+
```

### Type Checking Errors

**Issue:** Mypy reports type errors

**Solution:**
```bash
# See detailed errors
mypy . --show-error-codes

# Ignore missing imports
mypy . --ignore-missing-imports

# Ignore specific error (add comment)
result = function()  # type: ignore[error-code]

# Gradual typing: Start with functions you're modifying
```

### CI Checks Failing

**Issue:** GitHub Actions fail but local tests pass

**Solution:**
1. Check Python version in CI vs local
2. Ensure all dependencies in requirements.txt
3. Check for file path issues (use pathlib)
4. Review CI logs for specific errors
5. Run checks locally:
   ```bash
   # Simulate CI checks
   ruff check .
   ruff format --check .
   pytest -v --cov=.
   ```

### Import Errors

**Issue:** `ImportError` or `ModuleNotFoundError`

**Solution:**
```bash
# Reinstall in editable mode
pip install -e .

# Check if package installed
pip show package-name

# Run from project root
cd /path/to/project
pytest
```

### Merge Conflicts

**Issue:** Merge conflicts in PR

**Solution:**
```bash
# Update from main
git fetch origin
git merge origin/main

# Fix conflicts
# Edit conflicted files

# Mark resolved
git add .
git commit

# Push updated branch
git push
```

---

## Quick Reference

### Essential Commands

```bash
# Linting
ruff check .                    # Check for issues
ruff check --fix .              # Auto-fix
ruff format .                   # Format code

# Testing
pytest -v                       # Run tests
pytest --cov=. --cov-report=html  # With coverage

# Type checking
mypy .                          # Check types

# Pre-commit
pre-commit run --all-files      # Run all hooks
pre-commit install              # Install hooks

# Git workflow
git checkout -b feature/name    # New branch
git add .                       # Stage changes
git commit -m "message"         # Commit
git push -u origin branch       # Push
```

### Claude Code Commands

```bash
/lint                           # Run linting
/test                           # Run tests
/fix-lint                       # Auto-fix issues
/review-pr                      # Review before PR
```

### File Locations

```
.
├── .github/
│   ├── workflows/
│   │   ├── lint.yml           # Linting CI
│   │   └── test.yml           # Testing CI
│   └── pull_request_template.md  # PR template
├── .claude/
│   ├── agents/                # Subagents
│   ├── commands/              # Slash commands
│   └── skills/                # Skills
├── .pre-commit-config.yaml    # Pre-commit hooks
├── pyproject.toml             # Tool configuration
└── requirements.txt           # Dependencies
```

---

## Next Steps

1. **Install dependencies**: `pip install -e ".[dev]"`
2. **Set up pre-commit**: `pre-commit install`
3. **Run initial checks**: `ruff check . && pytest -v`
4. **Start development**: Follow workflow guide above
5. **Gradual improvement**: Apply boy scout rule to legacy code

For questions or issues, refer to tool documentation:
- Ruff: https://docs.astral.sh/ruff/
- Pytest: https://docs.pytest.org/
- Mypy: https://mypy.readthedocs.io/
- Pre-commit: https://pre-commit.com/

Happy coding! 🚀
