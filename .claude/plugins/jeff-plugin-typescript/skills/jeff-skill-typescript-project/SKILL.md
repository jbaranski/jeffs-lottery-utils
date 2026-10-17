---
name: jeff-skill-typescript-project
description: Configure or update Node.js TypeScript projects with opinionated best practices. Use when a repo should contain a TypeScript project (backend, CLI, library) with modern tooling, strict type checking, and testing requirements.
---

This is an opinionated view for how Node.js TypeScript projects should be configured and maintained.

## Prerequisites

Before proceeding:

1. Ensure nvm (Node Version Manager) and Node.js are installed using the `jeff-skill-install-nodejs` skill.
2. Ensure prettier is installed using the `jeff-skill-install-prettier` skill.
3. Use WebSearch to verify current versions:
   - "TypeScript latest version [current-year]"
   - "Vitest latest version [current-year]"
   - "ESLint TypeScript latest version [current-year]"
   - Visit https://nodejs.org/en to find the current Node.js LTS major version (look for the "LTS" badge)
   - Update all version numbers in examples below with verified versions
   - Verify rather than guess; versions in this skill go stale.

## Goals

- Use latest Node.js LTS runtime
- Enforce strict TypeScript type checking
- Use ESLint for linting with TypeScript support
- Use Prettier for code formatting (via `jeff-skill-install-prettier` skill)
- Use Vitest for testing with 80%+ code coverage
- Keep dependencies minimal and deliberate
- Make test/lint/build repeatable and auditable

## Required Layout

### Project Structure

```
project-root/
├── src/
│   ├── index.ts
│   └── lib/
│       └── example.ts
├── tests/
│   └── example.test.ts
├── dist/                   # Build output (gitignored)
├── tsconfig.json
├── tsconfig.build.json     # Separate config for building
├── package.json
├── eslint.config.js
├── .gitignore
├── vitest.config.ts
└── README.md
```

## Configuration Files

### package.json

```json
{
  "name": "project-name",
  "version": "1.0.0",
  "type": "module",
  "description": "Project description",
  "main": "./dist/index.js",
  "types": "./dist/index.d.ts",
  "engines": {
    "node": ">= <NODE_LTS>.0.0"
  },
  "scripts": {
    "build": "tsc -p tsconfig.build.json",
    "watch": "tsc -p tsconfig.build.json --watch",
    "dev": "tsx watch src/index.ts",
    "start": "node dist/index.js",
    "test": "vitest",
    "test:run": "vitest run",
    "test:coverage": "vitest run --coverage",
    "lint": "eslint src tests",
    "lint:fix": "eslint src tests --fix",
    "prettier:fix": "prettier --write .",
    "prettier:check": "prettier --check .",
    "typecheck": "tsc --noEmit",
    "clean": "rm -rf dist node_modules",
    "prepublishOnly": "npm run build"
  },
  "dependencies": {},
  "devDependencies": {
    "@eslint/js": "^10.0.1",
    "@types/node": "^<NODE_LTS>.0.0",
    "@vitest/coverage-v8": "^5.0.4",
    "eslint": "^10.12.0",
    "typescript-eslint": "^8.71.2",
    "tsx": "^4.23.15",
    "typescript": "~6.0.3",
    "vitest": "^5.0.4"
  }
}
```

TypeScript stays on `~6.0.x` until `typescript-eslint` supports 7.x — as of October 2026 its peer range is `>=4.8.4 <6.1.0`, while TypeScript 7.0 is the npm `latest`. Check `npm view typescript-eslint peerDependencies` before moving to 7.

### tsconfig.json

Type-checks sources and tests (`npm run typecheck`); it never emits.

```json
{
  "compilerOptions": {
    "target": "ES2022",
    "module": "ESNext",
    "moduleResolution": "Bundler",
    "lib": ["ES2022"],
    "types": ["node"],
    "strict": true,
    "noEmit": true,
    "noUnusedLocals": true,
    "noUnusedParameters": true,
    "noFallthroughCasesInSwitch": true,
    "noImplicitReturns": true,
    "esModuleInterop": true,
    "skipLibCheck": true,
    "forceConsistentCasingInFileNames": true,
    "resolveJsonModule": true
  },
  "include": ["src/**/*", "tests/**/*"]
}
```

### tsconfig.build.json

Emits `src/` only, with declarations, into `dist/`:

```json
{
  "extends": "./tsconfig.json",
  "compilerOptions": {
    "noEmit": false,
    "rootDir": "./src",
    "outDir": "./dist",
    "declaration": true
  },
  "include": ["src/**/*"]
}
```

### eslint.config.js

ESLint 10 only reads flat config — `.eslintrc.*` files and the `--ext` flag were removed, so don't create or keep them.

```js
import js from '@eslint/js';
import { defineConfig } from 'eslint/config';
import tseslint from 'typescript-eslint';

export default defineConfig(
  { ignores: ['dist/', 'coverage/'] },
  js.configs.recommended,
  tseslint.configs.recommendedTypeChecked,
  {
    languageOptions: {
      parserOptions: { projectService: true, tsconfigRootDir: import.meta.dirname }
    },
    rules: {
      '@typescript-eslint/no-unused-vars': ['error', { argsIgnorePattern: '^_' }],
      '@typescript-eslint/explicit-function-return-type': 'warn',
      '@typescript-eslint/no-explicit-any': 'error',
      '@typescript-eslint/no-floating-promises': 'error'
    }
  }
);
```

### vitest.config.ts

```typescript
import { defineConfig } from 'vitest/config';

export default defineConfig({
  test: {
    globals: true,
    environment: 'node',
    coverage: {
      provider: 'v8',
      reporter: ['text', 'html', 'json'],
      exclude: ['node_modules/', 'dist/', 'tests/', '**/*.test.ts', '**/*.config.ts'],
      thresholds: {
        lines: 80,
        functions: 80,
        branches: 80,
        statements: 80
      }
    }
  }
});
```

### .gitignore

```
# Dependencies
node_modules/

# Build output
dist/
build/

# Testing
coverage/
.nyc_output/

# Environment
.env
.env.local
.env.*.local

# IDE
.vscode/
.idea/
*.swp
*.swo
*~

# OS
.DS_Store
Thumbs.db

# Logs
*.log
npm-debug.log*

# TypeScript
*.tsbuildinfo
```

## Project Setup Commands

### Initialize Project

```bash
# Create project directory
mkdir project-name && cd project-name

# Initialize npm project
npm init -y

# Install TypeScript and build tools
npm install -D typescript @types/node tsx

# Install testing framework
npm install -D vitest @vitest/coverage-v8

# Install linting
npm install -D eslint @eslint/js typescript-eslint

# Create directory structure
mkdir -p src/lib tests

# Create initial files
touch src/index.ts tests/example.test.ts

# Lock Node version and enforce it
# Replace <NODE_LTS> with the current LTS major version from https://nodejs.org/en
# .nvmrc goes at the repo root, however deep this project is
echo "<NODE_LTS>" > "$(git rev-parse --show-toplevel)/.nvmrc"
# .npmrc goes co-located with package.json (npm does not traverse up beyond the package root)
echo "engine-strict=true" > .npmrc
```

## npm ci vs npm install

- **Use `npm ci`** in CI pipelines, fresh checkouts, and Claude Code web sessions. It installs exactly what is in `package-lock.json`, never modifies the lock file, and fails fast if the lock file is missing or inconsistent.
- **Use `npm install <package>`** only when intentionally adding or updating a dependency.
- **Never run bare `npm install`** (no arguments) in CI or fresh environments — it re-resolves versions and may silently rewrite the lock file, which defeats reproducibility and can break CI.

## Testing Requirements

- Use Vitest for all tests
- Tests must live in `tests/` directory
- Minimum 80% code coverage required
- Coverage reports generated in `coverage/` directory
- Tests must be runnable via `npm test`

## GitHub Actions

Create `.github/workflows/<project>-ci.yml`.

Name the file after the project (e.g. `web-ci.yml`, `api-ci.yml`) rather than a generic `ci.yml`, so several projects in one repo each get their own workflow instead of overwriting each other.

**Scope triggers to this project's directory.** If this project lives at the repo root, omit `paths:` entirely — every change in the repo is relevant. If it shares a monorepo with other stacks (e.g. this TypeScript service next to a `golang/` backend or `infra/`), scope `paths:` to the project directory so an unrelated change (a README edit, another service's change) doesn't trigger this build. Always include the workflow file itself in `paths:` so edits to the CI config are still validated.

**Skip Dependabot-triggered runs.** Every job carries the Dependabot guard from `jeff-skill-install-dependabot` so Dependabot PRs and pushes don't consume Actions minutes. If you add a job, give it the same `if:`. If a job already has an `if:` condition, combine it with the guard using `&&` rather than replacing it, wrapping the existing condition in parentheses (e.g. `if: (existing-condition) && github.actor != 'dependabot[bot]' && ...`).

**Run steps in the project directory.** `defaults.run.working-directory` makes every `run:` step execute inside `<project-dir>`, where `package.json` lives. Omit the `defaults:` block entirely if the project is at the repo root. It does not apply to `uses:` steps, which is why the setup-node cache path below is spelled out relative to the repo root.

**Least privilege.** The workflow grants only `contents: read`, and checkout uses `persist-credentials: false` so the token is not left in `.git/config` for later steps.

```yaml
name: <project>-ci

on:
  push:
    branches: [main]
    paths:
      - '<project-dir>/**' # e.g. 'web/**' — omit this whole `paths:` key if the project is at repo root
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
        working-directory: <project-dir> # e.g. 'web' — omit this whole `defaults:` block if the project is at repo root
    steps:
      - uses: actions/checkout@v7
        with:
          persist-credentials: false

      - name: Setup Node.js
        uses: actions/setup-node@v7
        with:
          node-version-file: .nvmrc # repo root, shared by all Node projects
          cache: 'npm'
          cache-dependency-path: <project-dir>/package-lock.json # 'package-lock.json' if the project is at repo root

      - name: Install dependencies
        run: npm ci

      - name: Type check
        run: npm run typecheck

      - name: Lint
        run: npm run lint

      - name: Format check
        run: npm run prettier:check

      - name: Run tests with coverage
        run: npm run test:coverage

      - name: Build
        run: npm run build
```

## Best Practices

- ESM only: `"type": "module"` in package.json
- `tsx` for development with hot reload; `tsc` for production builds
- Place `.nvmrc` (containing the current LTS major version from https://nodejs.org/en) at the repo root — nvm traverses up so one file covers all subprojects
- Place `.npmrc` containing `engine-strict=true` co-located with `package.json` — npm does not traverse up beyond the package root, so it must live alongside `package.json`

## For Library Projects

If building a library (not an application):

- Set `"main"` and `"types"` in package.json
- Build declaration files with `"declaration": true`
- Consider dual ESM/CJS exports if needed
- Test your library as a consumer would use it

## AWS Lambda Development

When building AWS Lambda functions with TypeScript, use **AWS Lambda Powertools for TypeScript**:

- **Logger** for structured JSON logging with the Lambda context injected (`logger.addContext(context)`); never `console.log`.
- **Tracer** (X-Ray) only when explicitly requested.
- **Parameters** for SSM Parameter Store and Secrets Manager; **Idempotency** where retries could double-apply.
- Type events with `@types/aws-lambda`, preferring `APIGatewayProxyEventV2` / `APIGatewayProxyResultV2`.
- Cold starts: minimal dependencies, static imports at the top, no lazy loading.
- ARM64 (Graviton); explicit memory and timeout; configuration from environment variables.

### Handling Multiple Routes

**Recommended: Manual Path Checking (Cold Start Optimized)**

For 2-5 routes, use simple path checking - no extra dependencies, faster cold starts:

```typescript
import { APIGatewayProxyEventV2, APIGatewayProxyResultV2 } from 'aws-lambda';
import { Logger } from '@aws-lambda-powertools/logger';

const logger = new Logger();

export const handler = async (event: APIGatewayProxyEventV2): Promise<APIGatewayProxyResultV2> => {
  const path = event.rawPath || event.requestContext.http.path;
  const method = event.requestContext.http.method;

  logger.info('Request received', { path, method });

  // Parse body once
  let body: unknown;
  try {
    body = event.body ? JSON.parse(event.body) : {};
  } catch {
    return { statusCode: 400, body: JSON.stringify({ error: 'Invalid JSON' }) };
  }

  // Route handling
  if (method === 'GET' && path === '/users') {
    return handleGetUsers();
  } else if (method === 'POST' && path === '/users') {
    return handleCreateUser(body);
  } else if (method === 'GET' && path.startsWith('/users/')) {
    const id = path.split('/')[2];
    return handleGetUser(id);
  }

  return { statusCode: 404, body: JSON.stringify({ error: 'Not found' }) };
};

async function handleGetUsers(): Promise<APIGatewayProxyResultV2> {
  // Implementation
  return { statusCode: 200, body: JSON.stringify({ users: [] }) };
}

async function handleCreateUser(body: unknown): Promise<APIGatewayProxyResultV2> {
  // Implementation
  return { statusCode: 201, body: JSON.stringify({ user: body }) };
}

async function handleGetUser(id: string): Promise<APIGatewayProxyResultV2> {
  // Implementation
  return { statusCode: 200, body: JSON.stringify({ user: { id } }) };
}
```

**Last Resort: Event Handler (Only for 10+ routes)**

If a single Lambda needs 10+ routes, that usually means it should be split into focused functions, or API Gateway should route to separate Lambdas. Only when splitting isn't an option, use `@aws-lambda-powertools/event-handler` — check its current docs for the router API rather than writing it from memory.

### Installing Powertools

```bash
# Core (always)
npm install @aws-lambda-powertools/logger
npm install -D @types/aws-lambda

# Tracer (only when X-Ray is explicitly requested)
# npm install @aws-lambda-powertools/tracer

# Event Handler (only if you have 10+ routes - see routing section above)
# npm install @aws-lambda-powertools/event-handler
```

## Integration with Other Skills

- **jeff-skill-install-dependabot** — Set up Dependabot to keep npm dependencies up to date
- **jeff-skill-dependabot-issue-resolution** — Resolve Dependabot PRs for npm package updates
