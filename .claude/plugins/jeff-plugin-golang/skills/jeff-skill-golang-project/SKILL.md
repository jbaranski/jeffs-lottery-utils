---
name: jeff-skill-golang-project
description: Configure or update Go projects with opinionated best practices using Go modules, golangci-lint, and built-in testing. Use when a repo should contain a Go project with modern tooling, idiomatic Go code, and 80% test coverage requirements.
---

This is an opinionated view for how Go projects should be configured and maintained.

## Prerequisites

Before proceeding:

1. Check if Go is installed by running `go version`.
   - If not installed on macOS: `brew install go`
   - If not installed on Linux: Download from https://go.dev/dl/
   - Verify installation: `go version`
2. Install golangci-lint:
   - macOS: `brew install golangci-lint`
   - Linux: `curl -sSfL https://raw.githubusercontent.com/golangci/golangci-lint/master/install.sh | sh -s -- -b $(go env GOPATH)/bin`
   - Verify: `golangci-lint --version`
3. Install bc (basic calculator) for coverage threshold checks:
   - macOS: `brew install bc`
   - Linux (Ubuntu/Debian): `sudo apt-get install bc`
   - Linux (RHEL/CentOS): `sudo yum install bc`
   - Verify: `bc --version`
4. Use WebSearch to verify current versions:
   - "Go golang latest stable version [current-year]"
   - "golangci-lint latest version [current-year]"
   - Update all version numbers in examples below with verified versions
   - Ensure Go is updated to the latest stable version if needed
   - DO NOT skip this step. DO NOT guess at version numbers.

## Goals

- Use Go modules for dependency management
- Follow idiomatic Go and Effective Go principles
- Use golangci-lint for comprehensive linting
- Use built-in Go testing with 80%+ code coverage
- Keep dependencies minimal and deliberate
- Make test/lint/build repeatable and auditable

## Required Layout

### Project Structure

For applications (with main package):

```
project-root/
├── cmd/
│   └── appname/
│       └── main.go
├── internal/
│   ├── handler/
│   │   ├── handler.go
│   │   └── handler_test.go
│   └── service/
│       ├── service.go
│       └── service_test.go
├── go.mod
├── go.sum
├── .golangci.yml
├── Makefile
├── README.md
└── .github/
    └── workflows/
        └── ci.yml
```

For libraries (no main package):

```
project-root/
├── example.go
├── example_test.go
├── go.mod
├── go.sum
├── .golangci.yml
├── Makefile
├── README.md
└── .github/
    └── workflows/
        └── ci.yml
```

### Directory Conventions

- `cmd/` - Main applications for this project
- `internal/` - Private application and library code (cannot be imported by other projects)
- `pkg/` - Library code that's ok to use by external applications (optional, use sparingly)

## Configuration Files

### go.mod

Initialize with Go modules:

```bash
go mod init github.com/username/projectname
```

This creates a `go.mod` file:

```go
module github.com/username/projectname

go 1.25

require (
    // Dependencies will be added here automatically
)
```

### .golangci.yml

Comprehensive linting configuration:

```yaml
run:
  timeout: 5m
  tests: true
  skip-dirs:
    - vendor

linters:
  enable:
    - errcheck # Check for unchecked errors
    - gosimple # Simplify code
    - govet # Vet examines Go source code
    - ineffassign # Detect ineffectual assignments
    - staticcheck # Staticcheck is go vet on steroids
    - unused # Check for unused constants, variables, functions and types
    - gofmt # Check whether code was gofmt-ed
    - goimports # Check import statements are formatted
    - misspell # Finds commonly misspelled English words
    - revive # Fast, configurable, extensible, flexible, and beautiful linter for Go
    - goprintffuncname # Check printf-like function names
    - unconvert # Remove unnecessary type conversions
    - gocritic # Highly extensible Go linter
    - gosec # Inspect source code for security problems
    - dupl # Code clone detection
    - exhaustive # Check exhaustiveness of enum switch statements
    - gocyclo # Computes cyclomatic complexity
    - godot # Check if comments end in a period
    - prealloc # Find slice declarations that could potentially be preallocated
    - bodyclose # Check HTTP response body is closed
    - nilerr # Finds code that returns nil even if it checks that error is not nil
    - nolintlint # Reports ill-formed or insufficient nolint directives
    - stylecheck # Replacement for golint
    - unparam # Find unused function parameters

linters-settings:
  gocyclo:
    min-complexity: 15
  dupl:
    threshold: 100
  gocritic:
    enabled-tags:
      - diagnostic
      - performance
      - style
  revive:
    rules:
      - name: var-naming
      - name: exported
      - name: indent-error-flow

issues:
  exclude-use-default: false
  max-same-issues: 0
  max-issues-per-linter: 0
```

### Makefile

Common commands for consistency:

```makefile
.PHONY: all test build clean lint fmt coverage

# Default target
all: fmt lint test build

# Run tests
test:
	go test -v -race ./...

# Run tests with coverage
coverage:
	go test -v -race -coverprofile=coverage.out -covermode=atomic ./...
	go tool cover -html=coverage.out -o coverage.html
	@echo "Coverage report: coverage.html"
	@go tool cover -func=coverage.out | grep total | awk '{print "Total coverage: " $$3}'

# Check if coverage meets minimum threshold (80%)
coverage-check:
	@go test -race -coverprofile=coverage.out -covermode=atomic ./... > /dev/null
	@COVERAGE=$$(go tool cover -func=coverage.out | grep total | awk '{print $$3}' | sed 's/%//'); \
	if [ $$(echo "$$COVERAGE < 80" | bc -l) -eq 1 ]; then \
		echo "Coverage $$COVERAGE% is below minimum 80%"; \
		exit 1; \
	else \
		echo "Coverage $$COVERAGE% meets minimum 80%"; \
	fi

# Build the application
build:
	go build -v ./...

# Format code
fmt:
	gofmt -w -s .
	goimports -w .

# Run linters
lint:
	golangci-lint run ./...

# Clean build artifacts
clean:
	go clean
	rm -f coverage.out coverage.html

# Tidy dependencies
tidy:
	go mod tidy
	go mod verify

# Run all checks (fmt, lint, test with coverage check)
check: fmt lint coverage-check

# Install development dependencies
deps:
	go install golang.org/x/tools/cmd/goimports@latest
	go install github.com/golangci/golangci-lint/cmd/golangci-lint@latest
```

## Project Setup Commands

### Initialize Project

1. Create project directory: `mkdir project-name && cd project-name`
2. Initialize Go module: `go mod init github.com/username/project-name`
3. Create project structure:
   ```bash
   mkdir -p cmd/appname internal
   touch cmd/appname/main.go
   ```
4. Create `.golangci.yml` with configuration above
5. Create `Makefile` with commands above
6. Initialize git: `git init`

### Common Commands

Use the Makefile for consistency:

```bash
# Format code
make fmt

# Run linters
make lint

# Run tests
make test

# Run tests with coverage report
make coverage

# Run tests and check 80% coverage threshold
make coverage-check

# Build the application
make build

# Run all checks (format, lint, coverage check)
make check

# Clean artifacts
make clean

# Tidy dependencies
make tidy
```

## Testing Requirements

- Use built-in `go test` for all tests
- Tests must live alongside code (e.g., `handler.go` → `handler_test.go`)
- Minimum 80% code coverage required
- Use table-driven tests (idiomatic Go pattern)
- Run tests with race detector: `go test -race`

### Example Test (Table-Driven)

```go
// internal/calculator/calculator.go
package calculator

func Add(a, b int) int {
    return a + b
}

func Divide(a, b int) (int, error) {
    if b == 0 {
        return 0, errors.New("division by zero")
    }
    return a / b, nil
}
```

```go
// internal/calculator/calculator_test.go
package calculator

import (
    "testing"
)

func TestAdd(t *testing.T) {
    tests := []struct {
        name     string
        a        int
        b        int
        expected int
    }{
        {"positive numbers", 2, 3, 5},
        {"negative numbers", -2, -3, -5},
        {"zero", 0, 0, 0},
        {"mixed", -5, 10, 5},
    }

    for _, tt := range tests {
        t.Run(tt.name, func(t *testing.T) {
            result := Add(tt.a, tt.b)
            if result != tt.expected {
                t.Errorf("Add(%d, %d) = %d; want %d", tt.a, tt.b, result, tt.expected)
            }
        })
    }
}

func TestDivide(t *testing.T) {
    tests := []struct {
        name      string
        a         int
        b         int
        expected  int
        expectErr bool
    }{
        {"valid division", 10, 2, 5, false},
        {"division by zero", 10, 0, 0, true},
    }

    for _, tt := range tests {
        t.Run(tt.name, func(t *testing.T) {
            result, err := Divide(tt.a, tt.b)
            if tt.expectErr {
                if err == nil {
                    t.Errorf("Divide(%d, %d) expected error, got nil", tt.a, tt.b)
                }
            } else {
                if err != nil {
                    t.Errorf("Divide(%d, %d) unexpected error: %v", tt.a, tt.b, err)
                }
                if result != tt.expected {
                    t.Errorf("Divide(%d, %d) = %d; want %d", tt.a, tt.b, result, tt.expected)
                }
            }
        })
    }
}
```

## Code Quality Standards

- All code must pass `golangci-lint run` with no errors
- All code must be formatted with `gofmt` and `goimports`
- Follow Effective Go: https://go.dev/doc/effective_go
- Follow Go Code Review Comments: https://go.dev/wiki/CodeReviewComments
- Use meaningful variable names (avoid single-letter unless idiomatic: `i`, `j`, `k` for loops)
- Handle errors explicitly (no ignored errors)
- Document exported functions, types, and packages

## GitHub Actions

Create `.github/workflows/ci.yml` for continuous integration:

```yaml
name: jeff-skill-golang-project

on:
  push:
    branches: [main]
  pull_request:
    branches: [main]

jobs:
  test:
    name: Test
    runs-on: ubuntu-latest
    steps:
      - name: Check out code
        uses: actions/checkout@v4

      - name: Set up Go
        uses: actions/setup-go@v5
        with:
          go-version: '1.25'
          cache: true

      - name: Download dependencies
        run: go mod download

      - name: Verify dependencies
        run: go mod verify

      - name: Format check
        run: |
          gofmt -d -s .
          if [ -n "$(gofmt -l -s .)" ]; then
            echo "Code is not formatted. Run 'make fmt'"
            exit 1
          fi

      - name: Run golangci-lint
        uses: golangci/golangci-lint-action@v6
        with:
          version: latest

      - name: Run tests with coverage
        run: go test -v -race -coverprofile=coverage.out -covermode=atomic ./...

      - name: Check coverage threshold
        run: |
          COVERAGE=$(go tool cover -func=coverage.out | grep total | awk '{print $3}' | sed 's/%//')
          echo "Total coverage: $COVERAGE%"
          if (( $(echo "$COVERAGE < 80" | bc -l) )); then
            echo "Coverage $COVERAGE% is below minimum 80%"
            exit 1
          fi

      - name: Upload coverage to Codecov (optional)
        uses: codecov/codecov-action@v4
        with:
          files: ./coverage.out
          flags: unittests
```

## Best Practices

- Keep dependencies minimal - only add what you truly need
- Use `go mod tidy` regularly to clean up unused dependencies
- Never commit `vendor/` directory unless specifically required
- Use context for cancellation and timeouts in long-running operations
- Prefer `errors.New()` or `fmt.Errorf()` for error creation
- Use error wrapping with `%w` for error context: `fmt.Errorf("failed to process: %w", err)`
- Write idiomatic Go - simple and readable over clever
- Add `.gitignore` with common Go exclusions:

  ```
  # Binaries
  *.exe
  *.exe~
  *.dll
  *.so
  *.dylib
  *.test

  # Output and coverage
  *.out
  coverage.html
  coverage.out

  # Go workspace file
  go.work
  go.work.sum

  # IDE
  .idea/
  .vscode/*
  !.vscode/launch.json
  *.swp
  *.swo
  *~

  # OS
  .DS_Store
  Thumbs.db
  ```

## Idiomatic Go Patterns

- Use short variable names in small scopes
- Error handling: Check errors explicitly, don't ignore them
- Use defer for cleanup (closing files, unlocking mutexes)
- Accept interfaces, return structs
- Keep interfaces small (prefer many small interfaces over large ones)
- Use goroutines and channels for concurrent operations
- Use `sync.WaitGroup` for waiting on multiple goroutines
- Avoid global state and init() functions when possible

## Integration with Other Skills

- **jeff-skill-error-debugging-rca**: Use when debugging errors or test failures in Angular projects or related tools

## Additional Resources

- Official Go documentation: https://go.dev/doc/
- Effective Go: https://go.dev/doc/effective_go
- Go Code Review Comments: https://go.dev/wiki/CodeReviewComments
- Go by Example: https://gobyexample.com/
- golangci-lint: https://golangci-lint.run/
