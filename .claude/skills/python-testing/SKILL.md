---
name: python-testing
description: Expertise for Python testing with pytest, including test structure, fixtures, parametrization, coverage analysis, and testing best practices for Python projects
---

# Python Testing Skill

Comprehensive guidance for writing and maintaining tests in Python using pytest.

## When to Use This Skill

Invoke when:
- Writing new tests
- Improving test coverage
- Debugging failing tests
- Structuring test files and directories
- Using pytest fixtures or parametrization
- Analyzing coverage reports
- Testing async code, classes, or exceptions

## Test Structure and Organization

### Directory Structure

```
project/
├── src/
│   ├── __init__.py
│   ├── module1.py
│   └── module2.py
├── tests/
│   ├── __init__.py
│   ├── conftest.py          # Shared fixtures
│   ├── test_module1.py
│   ├── test_module2.py
│   └── integration/
│       └── test_integration.py
├── pyproject.toml
└── pytest.ini (optional)
```

### Naming Conventions

- Test files: `test_*.py` or `*_test.py`
- Test classes: `Test*` (e.g., `TestTranscription`)
- Test functions: `test_*` (e.g., `test_gpu_availability`)
- Fixtures: Descriptive names (e.g., `sample_audio_file`, `mock_gpu`)

## Writing Tests

### Basic Test Function

```python
def test_function_name():
    """Test description."""
    # Arrange
    input_data = "example"

    # Act
    result = function_to_test(input_data)

    # Assert
    assert result == expected_output
```

### Testing with Fixtures

```python
import pytest

@pytest.fixture
def sample_audio_file(tmp_path):
    """Create a temporary audio file for testing."""
    audio_file = tmp_path / "test.m4a"
    audio_file.write_bytes(b"fake audio data")
    return audio_file

def test_transcription(sample_audio_file):
    """Test transcription with sample audio."""
    result = transcribe(sample_audio_file)
    assert result is not None
```

### Parametrized Tests

```python
@pytest.mark.parametrize("input_val,expected", [
    ("test1.m4a", True),
    ("test2.wav", False),
    ("test3.m4a", True),
])
def test_audio_format_validation(input_val, expected):
    """Test audio format validation with multiple inputs."""
    result = is_valid_audio_format(input_val)
    assert result == expected
```

### Testing Exceptions

```python
def test_invalid_file_raises_error():
    """Test that invalid file raises appropriate error."""
    with pytest.raises(FileNotFoundError):
        transcribe("nonexistent.m4a")

def test_error_message():
    """Test error message content."""
    with pytest.raises(ValueError, match="Invalid audio format"):
        validate_audio("file.txt")
```

### Testing Classes

```python
class TestTranscriptionService:
    """Tests for TranscriptionService class."""

    @pytest.fixture(autouse=True)
    def setup(self):
        """Setup before each test."""
        self.service = TranscriptionService()
        yield
        # Teardown after each test
        self.service.cleanup()

    def test_initialization(self):
        """Test service initializes correctly."""
        assert self.service is not None
        assert self.service.model_loaded is True

    def test_transcribe_audio(self, sample_audio_file):
        """Test transcription functionality."""
        result = self.service.transcribe(sample_audio_file)
        assert isinstance(result, str)
        assert len(result) > 0
```

## Markers and Test Organization

### Using Markers

```python
import pytest

@pytest.mark.slow
def test_large_batch_processing():
    """Test that takes a long time."""
    # Process large batch
    pass

@pytest.mark.gpu
def test_gpu_acceleration():
    """Test that requires GPU."""
    # GPU-specific test
    pass

@pytest.mark.integration
def test_full_workflow():
    """Integration test for entire workflow."""
    pass
```

### Running Specific Tests

```bash
# Run all tests
pytest

# Run specific test file
pytest tests/test_module.py

# Run specific test function
pytest tests/test_module.py::test_function

# Run tests with specific marker
pytest -m slow
pytest -m "not slow"
pytest -m "gpu and not integration"

# Run tests matching pattern
pytest -k "transcription"
pytest -k "test_gpu or test_cuda"

# Verbose output
pytest -v

# Show print statements
pytest -s

# Stop on first failure
pytest -x

# Run last failed tests
pytest --lf
```

## Coverage Analysis

### Running with Coverage

```bash
# Basic coverage
pytest --cov=.

# Coverage with missing lines
pytest --cov=. --cov-report=term-missing

# HTML coverage report
pytest --cov=. --cov-report=html

# XML coverage (for CI)
pytest --cov=. --cov-report=xml

# Coverage for specific module
pytest --cov=src/module --cov-report=term-missing
```

### Coverage Configuration

In `pyproject.toml`:

```toml
[tool.coverage.run]
source = ["."]
omit = ["*/tests/*", "*/venv/*", "*/__pycache__/*"]
branch = true

[tool.coverage.report]
fail_under = 80  # Fail if coverage below 80%
show_missing = true
exclude_lines = [
    "pragma: no cover",
    "def __repr__",
    "raise NotImplementedError",
    "if __name__ == .__main__.:",
    "if TYPE_CHECKING:",
]
```

### Excluding Code from Coverage

```python
def utility_function():  # pragma: no cover
    """Function excluded from coverage."""
    pass

if __name__ == "__main__":  # pragma: no cover
    main()
```

## Fixtures Best Practices

### Fixture Scopes

```python
@pytest.fixture(scope="function")  # Default: runs for each test
def per_test_fixture():
    return "new instance each test"

@pytest.fixture(scope="class")  # Runs once per test class
def per_class_fixture():
    return "shared by class tests"

@pytest.fixture(scope="module")  # Runs once per module
def per_module_fixture():
    return "shared by module tests"

@pytest.fixture(scope="session")  # Runs once per test session
def per_session_fixture():
    return "shared by all tests"
```

### Fixture in conftest.py

Place shared fixtures in `tests/conftest.py`:

```python
# tests/conftest.py
import pytest

@pytest.fixture
def gpu_available():
    """Check if GPU is available for tests."""
    import torch
    return torch.cuda.is_available()

@pytest.fixture
def sample_audio_files(tmp_path):
    """Create multiple sample audio files."""
    files = []
    for i in range(3):
        audio_file = tmp_path / f"test_{i}.m4a"
        audio_file.write_bytes(b"fake audio data")
        files.append(audio_file)
    return files
```

## Mocking and Patching

### Using unittest.mock

```python
from unittest.mock import Mock, patch, MagicMock

def test_with_mock():
    """Test using mock object."""
    mock_model = Mock()
    mock_model.transcribe.return_value = "test transcription"

    result = mock_model.transcribe("file.m4a")
    assert result == "test transcription"
    mock_model.transcribe.assert_called_once_with("file.m4a")

@patch('module.WhisperModel')
def test_with_patch(mock_whisper):
    """Test with patched class."""
    mock_whisper.return_value.transcribe.return_value = ("segments", "info")

    result = transcribe_audio("file.m4a")
    assert result is not None
```

### Using pytest-mock

```python
def test_with_mocker(mocker):
    """Test using pytest-mock plugin."""
    mock_func = mocker.patch('module.expensive_function')
    mock_func.return_value = "mocked result"

    result = call_expensive_function()
    assert result == "mocked result"
```

## Testing Async Code

```python
import pytest

@pytest.mark.asyncio
async def test_async_function():
    """Test async function."""
    result = await async_transcribe("file.m4a")
    assert result is not None
```

## Common Pytest Patterns

### Setup and Teardown

```python
class TestExample:
    def setup_method(self):
        """Setup before each test method."""
        self.resource = allocate_resource()

    def teardown_method(self):
        """Cleanup after each test method."""
        self.resource.cleanup()

    def test_something(self):
        assert self.resource is not None
```

### Temporary Files and Directories

```python
def test_with_temp_file(tmp_path):
    """Test using temporary path."""
    test_file = tmp_path / "test.txt"
    test_file.write_text("test content")

    result = process_file(test_file)
    assert result is not None

def test_with_temp_dir(tmp_path):
    """Test using temporary directory."""
    audio_dir = tmp_path / "audio"
    audio_dir.mkdir()

    # Create test files in directory
    (audio_dir / "test1.m4a").write_bytes(b"data")
    (audio_dir / "test2.m4a").write_bytes(b"data")

    result = process_directory(audio_dir)
    assert len(result) == 2
```

### Capturing Output

```python
def test_output(capsys):
    """Test captured stdout/stderr."""
    print("Hello, world!")

    captured = capsys.readouterr()
    assert "Hello, world!" in captured.out

def test_logs(caplog):
    """Test captured logs."""
    import logging
    logging.warning("Test warning")

    assert "Test warning" in caplog.text
```

## Best Practices

### 1. Test Independence
- Each test should be independent
- Don't rely on test execution order
- Use fixtures for setup/teardown

### 2. Descriptive Names and Docstrings
```python
def test_transcription_handles_empty_audio_file():
    """Test that transcription gracefully handles empty audio files."""
    pass
```

### 3. Arrange-Act-Assert Pattern
```python
def test_example():
    # Arrange: Set up test data
    input_data = create_test_data()

    # Act: Execute the function under test
    result = function_under_test(input_data)

    # Assert: Verify the result
    assert result == expected_value
```

### 4. Test One Thing Per Test
```python
# Good: Single responsibility
def test_audio_file_validation():
    assert is_valid_audio("file.m4a") is True

def test_audio_file_invalid_format():
    assert is_valid_audio("file.txt") is False

# Avoid: Testing multiple things
def test_audio_validation():  # Too broad
    assert is_valid_audio("file.m4a") is True
    assert is_valid_audio("file.txt") is False
    assert get_audio_duration("file.m4a") > 0
```

### 5. Use Parametrization for Similar Tests
```python
@pytest.mark.parametrize("filename,expected", [
    ("test.m4a", True),
    ("test.mp3", True),
    ("test.txt", False),
    ("test.wav", True),
])
def test_audio_formats(filename, expected):
    assert is_valid_audio(filename) == expected
```

### 6. Write Tests First (TDD)
1. Write failing test
2. Write minimal code to pass
3. Refactor
4. Repeat

## Troubleshooting Tests

### Common Issues

1. **Import errors**
   - Ensure `__init__.py` exists in test directories
   - Check PYTHONPATH includes project root
   - Use `pytest` from project root

2. **Fixture not found**
   - Check fixture spelling
   - Ensure conftest.py is in correct location
   - Verify fixture scope

3. **Tests pass locally but fail in CI**
   - Check for environment-specific dependencies
   - Verify test isolation (no shared state)
   - Check file path handling (use pathlib)

4. **Slow tests**
   - Mark slow tests with `@pytest.mark.slow`
   - Use mocking for expensive operations
   - Consider parallel test execution with pytest-xdist

## Quick Reference

### Essential Commands
```bash
pytest                          # Run all tests
pytest -v                       # Verbose output
pytest -s                       # Show print statements
pytest -x                       # Stop on first failure
pytest --lf                     # Run last failed
pytest -k "pattern"             # Run tests matching pattern
pytest -m marker                # Run tests with marker
pytest --cov=. --cov-report=html  # Coverage report
```

### Essential Assertions
```python
assert value                    # Truthy
assert value == expected        # Equality
assert value != expected        # Inequality
assert value > expected         # Greater than
assert value in collection      # Membership
assert isinstance(value, type)  # Type check
```

### Essential Fixtures
```python
tmp_path     # Temporary directory (pathlib.Path)
capsys       # Capture stdout/stderr
caplog       # Capture logs
monkeypatch  # Modify objects/environment
mocker       # Mock objects (pytest-mock)
```
