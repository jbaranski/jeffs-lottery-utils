---
name: jeff-skill-python-project
description: Configure or update Python projects using uv, ruff, and pytest with opinionated best practices. Use when a repo should contain a Python project with modern tooling, PEP standards, and 80% test coverage requirements.
---

This is an opinionated view for how Python projects should be configured and maintained.

## Prerequisites

1. Check `uv --version`. If missing, install with `brew install uv` (macOS) or `curl -LsSf https://astral.sh/uv/install.sh | sh`.
2. Use WebSearch to verify the current stable Python, pytest, pytest-cov and ruff versions, and update the versions below to match. Do not guess version numbers.

## Goals

- uv for Python versions, dependencies and the lockfile
- ruff for linting and formatting
- pytest with 80%+ coverage, enforced
- Minimal, deliberate dependencies; repeatable lint/test runs

## Layout

```
project-root/
├── src/
│   └── package_name/
│       ├── __init__.py
│       └── main.py
├── tests/
│   └── test_main.py
├── pyproject.toml
├── uv.lock                 # committed
├── .python-version
└── README.md
```

`.python-version` holds the latest stable Python (`3.15` as of October 2026).

## Setup

```bash
uv init --package project-name   # src layout with a build backend and .python-version
cd project-name
uv add --dev pytest pytest-cov ruff
mkdir tests
```

Then merge the tool configuration below into the generated `pyproject.toml`.

## pyproject.toml

```toml
[project]
name = "package-name"
version = "0.1.0"
description = "Project description"
readme = "README.md"
requires-python = ">=3.15"
dependencies = []

[dependency-groups]
dev = [
    "pytest>=9.1.1",
    "pytest-cov>=7.1.0",
    "ruff>=0.17.0",
]

[build-system]
requires = ["hatchling"]
build-backend = "hatchling.build"

[tool.ruff]
line-length = 120
target-version = "py315"

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

[tool.pytest.ini_options]
testpaths = ["tests"]
addopts = [
    "--strict-markers",
    "--strict-config",
    "--cov=src",
    "--cov-report=term-missing",
    "--cov-fail-under=80",
]

[tool.coverage.run]
source = ["src"]
```

Dev tools live in `[dependency-groups]` (what `uv add --dev` writes); `uv sync` installs the `dev` group by default.

## Checks

Run before calling work done:

```bash
uv run ruff check . && uv run ruff format --check . && uv run pytest
```

Use `uv run ruff check --fix .` and `uv run ruff format .` to fix. Tests live in `tests/`, use pytest, and must keep coverage at 80% or above.

## GitHub Actions

Create `.github/workflows/<project>-ci.yml`, named after the project (e.g. `api-ci.yml`) so several projects in one repo don't overwrite each other's workflow.

- **Scope triggers to this project's directory.** If the project is at the repo root, omit `paths:`. In a monorepo, scope `paths:` to the project directory, and always include the workflow file itself.
- **Skip Dependabot-triggered runs** with the guard from `jeff-skill-install-dependabot`. If a job already has an `if:`, combine with `&&`, wrapping the existing condition in parentheses.
- **Run steps in the project directory** with `defaults.run.working-directory`; omit it if the project is at the repo root.
- **Least privilege:** `contents: read`, and checkout with `persist-credentials: false`.

```yaml
name: <project>-ci

on:
  push:
    branches: [main]
    paths:
      - '<project-dir>/**' # omit this whole `paths:` key if the project is at repo root
      - '.github/workflows/<project>-ci.yml'
  pull_request:
    branches: [main]
    paths:
      - '<project-dir>/**'
      - '.github/workflows/<project>-ci.yml'

permissions:
  contents: read

jobs:
  test:
    if: github.actor != 'dependabot[bot]' && github.event.pull_request.user.login != 'dependabot[bot]'
    runs-on: ubuntu-latest
    defaults:
      run:
        working-directory: <project-dir> # omit this whole `defaults:` block if the project is at repo root
    steps:
      - uses: actions/checkout@v7
        with:
          persist-credentials: false

      - name: Install uv
        uses: astral-sh/setup-uv@v10
        with:
          enable-cache: true

      - name: Install Python and dependencies
        run: uv sync --locked

      - name: Lint
        run: uv run ruff check .

      - name: Format check
        run: uv run ruff format --check .

      - name: Test with coverage
        run: uv run pytest
```

`uv sync --locked` fails if `uv.lock` is out of date instead of silently re-resolving. CI never sends code or coverage to third-party services; the 80% threshold is enforced by pytest.

## .gitignore

```
__pycache__/
*.py[cod]
.pytest_cache/
.ruff_cache/
htmlcov/
.coverage
.venv/
dist/
build/
*.egg-info/
```

## Integration with Other Skills

- **jeff-skill-install-dependabot** — keep uv/Python dependencies up to date
- **jeff-skill-dependabot-issue-resolution** — resolve Dependabot PRs for Python package updates
