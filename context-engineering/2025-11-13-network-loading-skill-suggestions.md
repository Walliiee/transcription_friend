# Suggestions for Python-Quality Skill in Network Loading Repo

## Overview
Suggestions for adapting the python-quality skill template for a network loading/HTTP client codebase that handles API requests, data fetching, and network operations.

## Domain-Specific Examples to Add

### 1. Type Hints for HTTP/Network Code

Replace the generic `DataProcessor` example with network-specific class:

```python
from typing import Optional
from dataclasses import dataclass

@dataclass
class RequestConfig:
    """Configuration for HTTP requests."""

    base_url: str
    timeout: int = 30
    max_retries: int = 3
    headers: dict[str, str] | None = None

class NetworkLoader:
    """HTTP client for loading data from network endpoints."""

    config: RequestConfig
    session: requests.Session

    def __init__(self, config: RequestConfig) -> None:
        self.config = config
        self.session = requests.Session()
        if config.headers:
            self.session.headers.update(config.headers)

    def get(self, endpoint: str, params: dict[str, str] | None = None) -> dict[str, Any]:
        """
        Perform GET request to endpoint.

        Args:
            endpoint: API endpoint path
            params: Query parameters

        Returns:
            JSON response as dictionary

        Raises:
            requests.HTTPError: If request fails
            requests.Timeout: If request times out
        """
        url = f"{self.config.base_url}/{endpoint}"
        response = self.session.get(url, params=params, timeout=self.config.timeout)
        response.raise_for_status()
        return response.json()

    @property
    def is_connected(self) -> bool:
        """Check if session is active."""
        return self.session is not None
```

### 2. Async/Await Type Hints

Add examples for async network operations:

```python
import asyncio
import aiohttp
from typing import AsyncIterator

class AsyncNetworkLoader:
    """Async HTTP client for concurrent requests."""

    def __init__(self, base_url: str, max_connections: int = 10) -> None:
        self.base_url = base_url
        self.connector = aiohttp.TCPConnector(limit=max_connections)
        self.session: aiohttp.ClientSession | None = None

    async def __aenter__(self) -> "AsyncNetworkLoader":
        self.session = aiohttp.ClientSession(connector=self.connector)
        return self

    async def __aexit__(self, exc_type, exc_val, exc_tb) -> None:
        if self.session:
            await self.session.close()

    async def fetch(self, endpoint: str) -> dict[str, Any]:
        """Fetch data from endpoint."""
        if not self.session:
            raise RuntimeError("Session not initialized. Use async with.")

        url = f"{self.base_url}/{endpoint}"
        async with self.session.get(url) as response:
            response.raise_for_status()
            return await response.json()

    async def fetch_many(self, endpoints: list[str]) -> list[dict[str, Any]]:
        """Fetch data from multiple endpoints concurrently."""
        tasks = [self.fetch(endpoint) for endpoint in endpoints]
        return await asyncio.gather(*tasks)
```

### 3. Error Handling Patterns

Add network-specific error handling examples:

```python
import requests
from requests.exceptions import RequestException, Timeout, HTTPError
from typing import TypedDict

class RetryConfig(TypedDict):
    max_retries: int
    backoff_factor: float
    retry_statuses: list[int]

def fetch_with_retry(
    url: str,
    config: RetryConfig,
    timeout: int = 30
) -> requests.Response:
    """
    Fetch URL with exponential backoff retry logic.

    Args:
        url: URL to fetch
        config: Retry configuration
        timeout: Request timeout in seconds

    Returns:
        Successful response

    Raises:
        RequestException: If all retries exhausted
    """
    last_exception: Exception | None = None

    for attempt in range(config["max_retries"]):
        try:
            response = requests.get(url, timeout=timeout)

            # Retry on specific status codes
            if response.status_code in config["retry_statuses"]:
                raise HTTPError(f"Retry status: {response.status_code}")

            response.raise_for_status()
            return response

        except (Timeout, HTTPError) as e:
            last_exception = e
            wait_time = config["backoff_factor"] * (2 ** attempt)
            time.sleep(wait_time)

    raise RequestException(f"Failed after {config['max_retries']} retries") from last_exception
```

### 4. Rate Limiting Pattern

```python
from time import time, sleep
from collections import deque

class RateLimiter:
    """Token bucket rate limiter for API requests."""

    def __init__(self, max_requests: int, time_window: float) -> None:
        """
        Initialize rate limiter.

        Args:
            max_requests: Maximum requests allowed in time window
            time_window: Time window in seconds
        """
        self.max_requests = max_requests
        self.time_window = time_window
        self.requests: deque[float] = deque()

    def acquire(self) -> None:
        """Wait if necessary to respect rate limit."""
        now = time()

        # Remove old requests outside time window
        while self.requests and self.requests[0] < now - self.time_window:
            self.requests.popleft()

        # Wait if at limit
        if len(self.requests) >= self.max_requests:
            sleep_time = self.time_window - (now - self.requests[0])
            if sleep_time > 0:
                sleep(sleep_time)
            self.requests.popleft()

        self.requests.append(time())
```

### 5. Response Parsing with Type Safety

```python
from typing import TypedDict, Literal
from datetime import datetime

class APIResponse(TypedDict):
    """Typed API response structure."""
    status: Literal["success", "error"]
    data: dict[str, Any]
    timestamp: str
    request_id: str

class User(TypedDict):
    """User data model."""
    id: int
    username: str
    email: str
    created_at: str

def parse_user_response(response: dict[str, Any]) -> User:
    """
    Parse and validate user response.

    Args:
        response: Raw API response

    Returns:
        Validated User object

    Raises:
        ValueError: If response format is invalid
    """
    required_fields = {"id", "username", "email", "created_at"}

    if not all(field in response for field in required_fields):
        missing = required_fields - set(response.keys())
        raise ValueError(f"Missing required fields: {missing}")

    return User(
        id=int(response["id"]),
        username=str(response["username"]),
        email=str(response["email"]),
        created_at=str(response["created_at"])
    )
```

## Additional Ruff Rules to Enable

Add to the Ruff configuration section:

```python
[tool.ruff.lint]
select = [
    # ... existing rules ...
    "ASYNC",  # flake8-async - async/await best practices
    "S",      # flake8-bandit - security checks for network code
    "T20",    # flake8-print - no print statements in production
    "RET",    # flake8-return - return statement consistency
    "ARG",    # flake8-unused-arguments
]

# Network-specific ignores
ignore = [
    "S113",   # Allow requests without timeout (we handle this explicitly)
    "ASYNC109", # Allow async function without timeout in some cases
]
```

### Common Network-Related Ruff Errors

Add to the Common Ruff Error Codes section:

- **S113**: Requests call without timeout specified
- **ASYNC109**: Async function with no timeout
- **ASYNC110**: Control flow in finally block (common in network cleanup)
- **T201**: Print statement found (use logging instead)
- **ARG001**: Unused function argument (common in retry decorators)

## Testing Patterns for Network Code

Add a new section:

### Testing with Mocks and Fixtures

```python
from unittest.mock import Mock, patch
import pytest
import responses

# Using responses library for HTTP mocking
@responses.activate
def test_network_loader_get() -> None:
    """Test GET request with mocked response."""
    # Arrange
    responses.add(
        responses.GET,
        "https://api.example.com/users/1",
        json={"id": 1, "name": "Alice"},
        status=200
    )

    config = RequestConfig(base_url="https://api.example.com")
    loader = NetworkLoader(config)

    # Act
    result = loader.get("users/1")

    # Assert
    assert result["name"] == "Alice"
    assert len(responses.calls) == 1

# Using pytest fixtures for async tests
@pytest.fixture
async def async_loader() -> AsyncNetworkLoader:
    """Fixture providing async network loader."""
    async with AsyncNetworkLoader("https://api.example.com") as loader:
        yield loader

@pytest.mark.asyncio
async def test_async_fetch(async_loader: AsyncNetworkLoader) -> None:
    """Test async fetch operation."""
    with patch.object(async_loader.session, 'get') as mock_get:
        mock_response = Mock()
        mock_response.json = asyncio.coroutine(lambda: {"data": "test"})
        mock_get.return_value.__aenter__.return_value = mock_response

        result = await async_loader.fetch("endpoint")
        assert result == {"data": "test"}
```

## Best Practices Section Additions

### 8. Always Set Timeouts

```python
# Bad - can hang indefinitely
response = requests.get(url)

# Good - explicit timeout
response = requests.get(url, timeout=30)

# Better - separate connect/read timeouts
response = requests.get(url, timeout=(3.05, 27))  # (connect, read)
```

### 9. Use Session for Multiple Requests

```python
# Bad - creates new connection each time
def fetch_multiple(urls: list[str]) -> list[dict[str, Any]]:
    results = []
    for url in urls:
        response = requests.get(url)
        results.append(response.json())
    return results

# Good - reuses connection pool
def fetch_multiple(urls: list[str]) -> list[dict[str, Any]]:
    results = []
    with requests.Session() as session:
        for url in urls:
            response = session.get(url, timeout=30)
            results.append(response.json())
    return results
```

### 10. Handle Network Errors Gracefully

```python
from requests.exceptions import RequestException, Timeout, ConnectionError

# Bad - generic exception
def fetch_data(url: str) -> dict[str, Any]:
    try:
        response = requests.get(url)
        return response.json()
    except Exception as e:
        print(f"Error: {e}")
        return {}

# Good - specific exception handling
def fetch_data(url: str) -> dict[str, Any] | None:
    try:
        response = requests.get(url, timeout=30)
        response.raise_for_status()
        return response.json()
    except Timeout:
        logger.error(f"Request to {url} timed out")
        return None
    except ConnectionError:
        logger.error(f"Failed to connect to {url}")
        return None
    except RequestException as e:
        logger.error(f"Request failed: {e}")
        return None
```

### 11. Use Async for I/O-Bound Operations

```python
# Bad - sequential (slow)
def fetch_all_users(user_ids: list[int]) -> list[dict[str, Any]]:
    users = []
    for user_id in user_ids:
        response = requests.get(f"https://api.example.com/users/{user_id}")
        users.append(response.json())
    return users

# Good - concurrent (fast)
async def fetch_all_users(user_ids: list[int]) -> list[dict[str, Any]]:
    async with aiohttp.ClientSession() as session:
        tasks = [fetch_user(session, user_id) for user_id in user_ids]
        return await asyncio.gather(*tasks)

async def fetch_user(session: aiohttp.ClientSession, user_id: int) -> dict[str, Any]:
    async with session.get(f"https://api.example.com/users/{user_id}") as response:
        return await response.json()
```

## Dependencies Section

Add a recommended dependencies section:

### Network Loading Dependencies

```toml
[project.dependencies]
# HTTP clients
requests = ">=2.31.0"        # Synchronous HTTP
httpx = ">=0.25.0"           # Modern sync/async HTTP
aiohttp = ">=3.9.0"          # Async HTTP

# Utilities
tenacity = ">=8.2.0"         # Retry logic
requests-cache = ">=1.1.0"   # Response caching
urllib3 = ">=2.0.0"          # Low-level HTTP (auto-installed)

[project.optional-dependencies]
dev = [
    # ... existing dev dependencies ...
    "responses>=0.24.0",      # HTTP mocking
    "aioresponses>=0.7.0",    # Async HTTP mocking
    "pytest-asyncio>=0.21.0", # Async test support
    "pytest-httpx>=0.28.0",   # HTTPX testing
]
```

## Mypy Configuration for Network Code

Add to the Mypy section:

```toml
[[tool.mypy.overrides]]
module = [
    "requests.*",
    "aiohttp.*",
    "httpx.*",
    "urllib3.*",
]
ignore_missing_imports = true

# Stricter settings for network security
[tool.mypy]
warn_return_any = true
disallow_untyped_calls = true  # Ensure typed network calls
check_untyped_defs = true
```

## Pre-commit Hooks for Network Code

Add network-specific pre-commit hooks:

```yaml
# .pre-commit-config.yaml additions
repos:
  - repo: https://github.com/PyCQA/bandit
    rev: 1.7.5
    hooks:
      - id: bandit
        args: ['-c', 'pyproject.toml']
        additional_dependencies: ['bandit[toml]']
        # Check for security issues in network code

  - repo: https://github.com/pre-commit/mirrors-mypy
    rev: v1.7.0
    hooks:
      - id: mypy
        additional_dependencies: [types-requests, types-aiohttp]
```

## Common Pitfalls Section

Add a new section for network-specific pitfalls:

### Common Network Code Pitfalls

1. **Missing timeout causes hanging**
   ```python
   # Bad - no timeout
   requests.get(url)

   # Good - with timeout
   requests.get(url, timeout=30)
   ```

2. **Not using connection pooling**
   ```python
   # Bad - new connection each time
   for url in urls:
       requests.get(url)

   # Good - session reuses connections
   with requests.Session() as session:
       for url in urls:
           session.get(url)
   ```

3. **Ignoring rate limits**
   ```python
   # Bad - could get banned
   for item in items:
       api_call(item)

   # Good - respect rate limits
   limiter = RateLimiter(max_requests=100, time_window=60)
   for item in items:
       limiter.acquire()
       api_call(item)
   ```

4. **Not validating SSL certificates in production**
   ```python
   # Bad - security risk
   requests.get(url, verify=False)

   # Good - validate certificates
   requests.get(url, verify=True)  # or verify='/path/to/cert.pem'
   ```

5. **Blocking async event loop**
   ```python
   # Bad - blocks event loop
   async def fetch():
       time.sleep(5)  # Blocking!
       return await get_data()

   # Good - use async sleep
   async def fetch():
       await asyncio.sleep(5)
       return await get_data()
   ```

## Documentation Examples

Update the docstring example to be network-focused:

```python
async def fetch_paginated_data(
    endpoint: str,
    page_size: int = 100,
    max_pages: int | None = None,
    params: dict[str, str] | None = None
) -> list[dict[str, Any]]:
    """
    Fetch paginated data from API endpoint.

    Args:
        endpoint: API endpoint path (e.g., "users", "posts")
        page_size: Number of items per page (default: 100)
        max_pages: Maximum number of pages to fetch (None = all)
        params: Additional query parameters

    Returns:
        List of all items across all pages.

    Raises:
        HTTPError: If any request fails with non-200 status
        Timeout: If request exceeds timeout threshold
        ValueError: If page_size is not positive

    Example:
        >>> users = await fetch_paginated_data("users", page_size=50, max_pages=10)
        >>> print(f"Fetched {len(users)} users")
        Fetched 500 users

    Note:
        This function handles pagination automatically by following
        the 'next' link in the response. Rate limiting is applied
        between requests to avoid overwhelming the API.
    """
    # Implementation
    pass
```

## Summary of Changes for Network Loading Repo

1. **Replace generic examples** with HTTP/network operations
2. **Add async/await patterns** throughout type hints section
3. **Include network-specific Ruff rules** (ASYNC, S, T20)
4. **Add testing section** with responses/aioresponses examples
5. **Include rate limiting** and retry patterns
6. **Add timeout best practices** prominently
7. **Show session management** and connection pooling
8. **Include security considerations** (SSL, timeouts, auth)
9. **Add async testing** with pytest-asyncio examples
10. **Update dependencies** to include requests, aiohttp, httpx
11. **Add common pitfalls** specific to network operations
12. **Include typed response models** using TypedDict
