---
name: python-quality
description: Expertise for Python code quality including linting with ruff, formatting with black, type checking with mypy, code style guidelines, and best practices for writing clean Python code
---

# Python Code Quality Skill

Comprehensive guidance for maintaining high-quality Python code using modern tooling.

## When to Use This Skill

Invoke when:
- Writing or reviewing Python code
- Fixing linting errors
- Improving code formatting
- Adding type hints
- Refactoring code for quality
- Setting up code quality tools
- Understanding Python best practices

## Tooling Overview

This project uses:
- **Ruff**: Fast Python linter and formatter (replaces flake8, isort, pyupgrade)
- **Black**: Opinionated code formatter (optional, can use ruff format)
- **Mypy**: Static type checker
- **Pre-commit**: Git hooks for automatic checks

## Ruff - Modern Linting and Formatting

### What Ruff Checks

Ruff combines multiple tools into one fast linter:
- **pycodestyle (E, W)**: Style guide enforcement (PEP 8)
- **pyflakes (F)**: Logical errors (unused imports, undefined names)
- **isort (I)**: Import sorting
- **pep8-naming (N)**: Naming conventions
- **pyupgrade (UP)**: Modernize Python code
- **flake8-bugbear (B)**: Find likely bugs
- **flake8-comprehensions (C4)**: Improve comprehensions
- **flake8-simplify (SIM)**: Simplify code
- **flake8-use-pathlib (PTH)**: Prefer pathlib over os.path

### Running Ruff

```bash
# Check for issues
ruff check .

# Auto-fix issues
ruff check --fix .

# Check specific file
ruff check file.py

# Format code
ruff format .

# Format specific file
ruff format file.py

# Check formatting without changes
ruff format --check .
```

### Common Ruff Rules

#### Import Errors
```python
# F401: Unused import
import os  # Remove if not used

# I001: Import block is un-sorted
# Ruff will auto-sort imports
from typing import List
import os
import sys
```

#### Code Style
```python
# E501: Line too long (>100 chars)
# Solution: Break into multiple lines
result = very_long_function_name(
    argument1, argument2, argument3
)

# W291: Trailing whitespace
# Auto-fixed by ruff

# E302: Expected 2 blank lines
class MyClass:  # Need 2 blank lines before class
    pass
```

#### Naming Conventions
```python
# N802: Function name should be lowercase
def MyFunction():  # Bad
    pass

def my_function():  # Good
    pass

# N806: Variable should be lowercase
MyVariable = 10  # Bad
my_variable = 10  # Good
```

#### Bugbear Rules
```python
# B006: Mutable default argument
def append_to(item, target=[]):  # Bad
    target.append(item)
    return target

def append_to(item, target=None):  # Good
    if target is None:
        target = []
    target.append(item)
    return target

# B008: Function call in default argument
def get_time(when=datetime.now()):  # Bad
    pass

def get_time(when=None):  # Good
    if when is None:
        when = datetime.now()
```

## Black - Code Formatting

### Black Philosophy
- Opinionated: minimal configuration
- Deterministic: same output every time
- Fast: written in Python, optimized
- Automated: no manual formatting needed

### Running Black

```bash
# Format all files
black .

# Check without modifying
black --check .

# Show diff of changes
black --diff .

# Format specific file
black file.py
```

### Black Formatting Rules

```python
# Black prefers double quotes
name = "example"  # Preferred
name = 'example'  # Black will change to double

# Black uses trailing commas in multi-line structures
my_list = [
    1,
    2,
    3,  # Trailing comma
]

# Black line length (default 88, adjust in pyproject.toml)
# Automatically wraps long lines
result = function_name(
    argument1,
    argument2,
    argument3,
)
```

## Mypy - Static Type Checking

### Why Type Hints?
- Catch bugs before runtime
- Better IDE autocomplete
- Self-documenting code
- Easier refactoring

### Running Mypy

```bash
# Check all files
mypy .

# Check specific file
mypy file.py

# Ignore missing imports
mypy . --ignore-missing-imports

# Show error codes
mypy . --show-error-codes
```

### Basic Type Hints

```python
# Function arguments and return types
def greet(name: str) -> str:
    return f"Hello, {name}"

# Variables
age: int = 30
name: str = "Alice"
is_active: bool = True

# Collections
numbers: list[int] = [1, 2, 3]
mapping: dict[str, int] = {"a": 1, "b": 2}
unique_items: set[str] = {"apple", "banana"}

# Optional values
from typing import Optional

def find_user(user_id: int) -> Optional[str]:
    """Returns username or None if not found."""
    if user_id in database:
        return database[user_id]
    return None

# Modern syntax (Python 3.10+)
def find_user(user_id: int) -> str | None:
    pass
```

### Advanced Type Hints

```python
from typing import Union, Any, Callable, TypeVar

# Union types
def process(value: Union[int, str]) -> str:
    return str(value)

# Modern union syntax (Python 3.10+)
def process(value: int | str) -> str:
    return str(value)

# Callable (function types)
def apply(func: Callable[[int], str], value: int) -> str:
    return func(value)

# Generic types
T = TypeVar('T')

def first(items: list[T]) -> T:
    return items[0]

# Any (escape hatch - use sparingly)
def legacy_function(data: Any) -> Any:
    return data
```

### Type Checking Classes

```python
class DataProcessor:
    """Generic data processing service."""

    config: dict[str, Any]
    is_enabled: bool

    def __init__(self, config: dict[str, Any], is_enabled: bool = True) -> None:
        self.config = config
        self.is_enabled = is_enabled

    def process(self, data: str) -> dict[str, Any]:
        """Process data and return results."""
        # Implementation
        return {"status": "success", "data": data}

    @property
    def status(self) -> str:
        """Get current status."""
        return "active" if self.is_enabled else "inactive"
```

### Common Mypy Issues

```python
# Error: Incompatible return type
def get_name() -> str:
    return None  # Error: None not compatible with str

def get_name() -> str | None:  # Fix
    return None

# Error: Argument type mismatch
def process(x: int) -> None:
    pass

process("string")  # Error: str not compatible with int

# Error: Missing type hint
def calculate(x, y):  # Error if strict mode enabled
    return x + y

def calculate(x: float, y: float) -> float:  # Fix
    return x + y
```

## Pre-commit Hooks

### What Pre-commit Does
Automatically runs checks before each commit to ensure code quality.

### Installation and Setup

```bash
# Install pre-commit
pip install pre-commit

# Install git hooks
pre-commit install

# Run manually on all files
pre-commit run --all-files

# Run on staged files only
pre-commit run

# Update hooks to latest versions
pre-commit autoupdate
```

### How Pre-commit Works

1. You attempt to commit: `git commit -m "message"`
2. Pre-commit runs configured hooks (ruff, mypy, etc.)
3. If any hook fails:
   - Commit is blocked
   - Issues are auto-fixed (if possible)
   - You review changes and retry commit
4. If all hooks pass:
   - Commit proceeds normally

### Skipping Hooks (Use Sparingly)

```bash
# Skip all hooks for one commit
git commit --no-verify -m "WIP: temporary commit"

# Skip specific hook
SKIP=mypy git commit -m "message"
```

## Code Style Guidelines

### PEP 8 - Python Style Guide

#### Naming Conventions

```python
# Module names: lowercase with underscores
# my_module.py

# Class names: CapWords (PascalCase)
class DataProcessor:
    pass

# Function names: lowercase with underscores
def process_data(file_path):
    pass

# Constants: UPPERCASE with underscores
MAX_FILE_SIZE = 1000000
DEFAULT_TIMEOUT = 30

# Private attributes/methods: single underscore prefix
class Example:
    def __init__(self):
        self._private_attr = "private"

    def _private_method(self):
        pass
```

#### Imports

```python
# Standard library first
import os
import sys
from typing import Optional

# Third-party packages second
import numpy as np
import requests

# Local modules third
from myproject.utils import load_config
from myproject.models import DataModel

# Avoid wildcard imports
from module import *  # Bad
from module import specific_function  # Good
```

#### Whitespace

```python
# 2 blank lines before top-level classes/functions
def function1():
    pass


def function2():  # 2 blank lines
    pass


class MyClass:  # 2 blank lines
    pass

# 1 blank line between methods in a class
class Example:
    def method1(self):
        pass

    def method2(self):  # 1 blank line
        pass

# Spaces around operators
x = 1 + 2  # Good
x=1+2  # Bad

# No spaces around keyword arguments
func(arg1=value1, arg2=value2)  # Good
func(arg1 = value1)  # Bad
```

#### Line Length

```python
# Maximum line length (configure in pyproject.toml)
# Break long lines using parentheses

# Long function call
result = some_function(
    argument1,
    argument2,
    argument3,
    keyword_arg=value,
)

# Long string
message = (
    "This is a very long message "
    "that spans multiple lines "
    "for better readability"
)

# Long list
my_list = [
    "item1",
    "item2",
    "item3",
]
```

### Docstrings

```python
def process_data(
    input_file: str,
    format: str = "json",
    validate: bool = True
) -> dict[str, Any]:
    """
    Process data from a file and return structured output.

    Args:
        input_file: Path to the input file.
        format: Data format (json, csv, xml).
        validate: Whether to validate data before processing.

    Returns:
        Dictionary containing processed data.

    Raises:
        FileNotFoundError: If input file doesn't exist.
        ValueError: If format is not supported.

    Example:
        >>> result = process_data("data.json", format="json")
        >>> print(result["status"])
        "success"
    """
    # Implementation
    pass
```

## Best Practices

### 1. Follow the Boy Scout Rule
Leave code cleaner than you found it:
```python
# Before (touching this file)
def processData(x,y):  # Poor naming, no types
    return x+y

# After (boy scout rule applied)
def process_data(x: float, y: float) -> float:
    """Add two numbers together."""
    return x + y
```

### 2. Use Type Hints Incrementally
```python
# Start with function signatures
def process(file: str) -> dict[str, Any]:
    result = internal_processing(file)  # Internal variables can wait
    return result

# Gradually add more detail
def process(file: str) -> dict[str, Any]:
    result: dict[str, Any] = internal_processing(file)
    parsed: list[str] = result.get("items", [])
    return {"items": parsed, "count": len(parsed)}
```

### 3. Prefer Pathlib Over os.path
```python
# Old way (os.path)
import os
file_path = os.path.join("data", "files", "document.txt")
if os.path.exists(file_path):
    size = os.path.getsize(file_path)

# Modern way (pathlib)
from pathlib import Path
file_path = Path("data") / "files" / "document.txt"
if file_path.exists():
    size = file_path.stat().st_size
```

### 4. Use F-strings for Formatting
```python
# Old ways
message = "File %s has %d lines" % (filename, count)  # Old
message = "File {} has {} lines".format(filename, count)  # Verbose

# Modern way (f-strings)
message = f"File {filename} has {count} lines"  # Best
```

### 5. Avoid Mutable Default Arguments
```python
# Wrong
def add_item(item, items=[]):  # Bug: list shared across calls
    items.append(item)
    return items

# Correct
def add_item(item, items=None):
    if items is None:
        items = []
    items.append(item)
    return items
```

### 6. Use List Comprehensions Wisely
```python
# Simple comprehension (good)
squares = [x**2 for x in range(10)]

# With condition (good)
even_squares = [x**2 for x in range(10) if x % 2 == 0]

# Too complex (bad - use regular loop)
result = [
    process(x, y, z)
    for x in range(10)
    if x % 2 == 0
    for y in range(x)
    if y > 5
    for z in range(y)
]  # Too hard to read - use nested loops instead
```

### 7. Use Context Managers
```python
# Without context manager (bad - might not close)
file = open("data.txt")
data = file.read()
file.close()

# With context manager (good - auto-closes)
with open("data.txt") as file:
    data = file.read()
```

## Quick Reference

### Essential Commands

```bash
# Linting
ruff check .                    # Check for issues
ruff check --fix .              # Auto-fix issues
ruff format .                   # Format code

# Type checking
mypy .                          # Check types
mypy . --ignore-missing-imports # Ignore missing stubs

# Formatting
black .                         # Format with black
black --check .                 # Check formatting

# Pre-commit
pre-commit run --all-files      # Run all hooks
pre-commit run ruff             # Run specific hook
```

### Common Ruff Error Codes

- **E501**: Line too long
- **F401**: Imported but unused
- **F841**: Local variable assigned but never used
- **I001**: Import block unsorted
- **N802**: Function name should be lowercase
- **B006**: Mutable default argument
- **UP**: Pyupgrade suggestions (modernize code)

### Ignoring Specific Rules

```python
# Ignore for one line
result = function()  # noqa: E501

# Ignore specific rule
result = function()  # noqa: F841

# Ignore entire file (add to top of file)
# ruff: noqa
```

## Incremental Improvement Strategy

For legacy codebases:

1. **Start with formatting**: Run `ruff format .` on files you touch
2. **Fix auto-fixable issues**: Run `ruff check --fix .`
3. **Add type hints gradually**: Start with function signatures
4. **Increase strictness over time**: Tighten mypy configuration
5. **Use pre-commit hooks**: Prevent new issues from being introduced
6. **Track progress**: Monitor linting errors and coverage over time

The goal is gradual improvement, not perfection overnight!
