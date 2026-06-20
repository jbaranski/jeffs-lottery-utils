---
name: jeff-skill-python-project
description: Configure or update Python projects using uv, ruff, and pytest with opinionated best practices. Use when a repo should contain a Python project with modern tooling, PEP standards, and 80% test coverage requirements.
---

This is an opinionated view for how Python projects should be configured and maintained.

## Prerequisites

Before proceeding:

1. Check if `uv` is installed by running `uv --version`.
   - If not installed, install it: `curl -LsSf https://astral.sh/uv/install.sh | sh` (if on macOS Homebrew is an option as well `brew install uv`)
   - Verify installation: `uv --version`
2. Use WebSearch to verify current versions:
   - "Python latest stable version [current-year]"
   - "pytest latest version [current-year]"
   - "ruff python linter latest version [current-year]"
   - "pytest-cov latest version [current-year]"
   - Update all version numbers in examples below with verified versions
   - DO NOT skip this step. DO NOT guess at version numbers.

## Goals

- Use uv for Python version management and dependency management
- Enforce PEP 8 and modern Python best practices
- Use ruff for fast linting and formatting
- Use pytest with 80%+ code coverage
- Keep dependencies minimal and deliberate
- Make test/lint/format repeatable and auditable

## Required Layout

### Project Structure

```
project-root/
├── src/
│   └── package_name/
│       ├── __init__.py
│       └── main.py
├── tests/
│   ├── __init__.py
│   └── test_main.py
├── pyproject.toml
├── .python-version
├── README.md
└── .github/
    └── workflows/
        └── ci.yml
```

### Python Version

- Always use the latest stable Python version
- Create `.python-version` file in project root:
  ```
  3.14
  ```
  (Update to current latest stable version)

## Configuration Files

### pyproject.toml

This is the single source of truth for project configuration (PEP 621).

```toml
[project]
name = "package-name"
version = "0.1.0"
description = "Project description"
readme = "README.md"
requires-python = ">=3.14"
dependencies = []

[project.optional-dependencies]
dev = [
    "pytest>=9.1.0",
    "pytest-cov>=7.0.0",
    "ruff>=0.15.0",
]

[build-system]
requires = ["hatchling"]
build-backend = "hatchling.build"

[tool.ruff]
line-length = 120
target-version = "py314"

[tool.ruff.lint]
select = [
    "E",   # pycodestyle errors
    "W",   # pycodestyle warnings
    "F",   # pyflakes
    "I",   # isort
    "B",   # flake8-bugbear
    "C4",  # flake8-comprehensions
    "UP",  # pyupgrade
]
ignore = []

[tool.ruff.format]
quote-style = "double"
indent-style = "space"

[tool.pytest.ini_options]
testpaths = ["tests"]
python_files = ["test_*.py"]
python_classes = ["Test*"]
python_functions = ["test_*"]
addopts = [
    "--strict-markers",
    "--strict-config",
    "--cov=src",
    "--cov-report=term-missing",
    "--cov-report=html",
    "--cov-fail-under=80",
]

[tool.coverage.run]
source = ["src"]
omit = ["*/tests/*", "*/__pycache__/*"]

[tool.coverage.report]
precision = 2
show_missing = true
skip_covered = false
```

## Project Setup Commands

### Initialize Project

1. Create project directory: `mkdir project-name && cd project-name`
2. Initialize uv project: `uv init`
3. Create required directories:
   ```bash
   mkdir -p src/package_name tests
   touch src/package_name/__init__.py
   touch tests/__init__.py
   ```
4. Create `.python-version` file with latest stable Python version
5. Install dev dependencies: `uv add --dev pytest pytest-cov ruff`
6. Create `pyproject.toml` with configuration above

### Common Commands

Create a simple script or document these for users:

```bash
# Install dependencies
uv sync

# Run tests with coverage
uv run pytest

# Run linting
uv run ruff check .

# Auto-fix linting issues
uv run ruff check --fix .

# Format code
uv run ruff format .

# Run all checks (lint + format check + tests)
uv run ruff check . && uv run ruff format --check . && uv run pytest
```

## Testing Requirements

- Use pytest for all tests
- Tests must live in `tests/` directory
- Minimum 80% code coverage required
- Coverage reports generated in `htmlcov/` directory
- Tests must be runnable via `uv run pytest`

### Example Test

```python
# tests/test_main.py
import pytest
from package_name.main import example_function


def test_example_function():
    """Test that example function works correctly."""
    result = example_function(5)
    assert result == 10


def test_example_function_edge_case():
    """Test edge cases."""
    with pytest.raises(ValueError):
        example_function(-1)
```

## Code Quality Standards

- All code must pass `ruff check` with no errors
- All code must be formatted with `ruff format`
- Follow PEP 8 style guide
- Use type hints where appropriate (PEP 484)
- Document functions and classes with docstrings (PEP 257)

## GitHub Actions

Create `.github/workflows/ci.yml` for continuous integration:

```yaml
name: jeff-skill-python-project

on:
  push:
    branches: [main]
  pull_request:
    branches: [main]

jobs:
  test:
    runs-on: ubuntu-latest
    steps:
      - uses: actions/checkout@v4

      - name: Install uv
        uses: astral-sh/setup-uv@v4

      - name: Set up Python
        run: uv python install

      - name: Install dependencies
        run: uv sync --all-extras --dev

      - name: Run ruff linting
        run: uv run ruff check .

      - name: Run ruff formatting check
        run: uv run ruff format --check .

      - name: Run tests with coverage
        run: uv run pytest
```

## Best Practices

- Keep dependencies minimal - only add what you truly need
- Pin dependency versions in `pyproject.toml` for reproducibility
- Use virtual environments (uv handles this automatically)
- Never commit `__pycache__/`, `.pytest_cache/`, or `htmlcov/` directories
- Add `.gitignore` with common Python exclusions:
  ```
  __pycache__/
  *.py[cod]
  *$py.class
  .pytest_cache/
  htmlcov/
  .coverage
  .venv/
  dist/
  build/
  *.egg-info/
  ```

## Integration with Other Skills

- **jeff-skill-error-debugging-rca**: Use when debugging errors or test failures in Angular projects or related tools

## Additional Resources

- uv documentation: https://docs.astral.sh/uv/
- ruff documentation: https://docs.astral.sh/ruff/
- pytest documentation: https://docs.pytest.org/
- Python PEPs: https://peps.python.org/
