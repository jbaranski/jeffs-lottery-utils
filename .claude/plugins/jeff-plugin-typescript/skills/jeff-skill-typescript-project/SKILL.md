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
   - DO NOT skip this step. DO NOT guess at version numbers.

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
├── .eslintrc.json
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
    "lint": "eslint src tests --ext .ts",
    "lint:fix": "eslint src tests --ext .ts --fix",
    "prettier:fix": "prettier --write .",
    "prettier:check": "prettier --check .",
    "typecheck": "tsc --noEmit",
    "clean": "rm -rf dist node_modules",
    "prepublishOnly": "npm run build"
  },
  "dependencies": {},
  "devDependencies": {
    "@types/node": "^22.0.0",
    "@typescript-eslint/eslint-plugin": "^8.54.0",
    "@typescript-eslint/parser": "^8.54.0",
    "@vitest/coverage-v8": "^4.0.18",
    "eslint": "^10.0.0",
    "tsx": "^4.0.0",
    "typescript": "^5.9.0",
    "vitest": "^4.0.18"
  }
}
```

### tsconfig.json

Main TypeScript configuration with strict settings:

```json
{
  "compilerOptions": {
    "target": "ES2022",
    "module": "ESNext",
    "moduleResolution": "Bundler",
    "lib": ["ES2022"],
    "outDir": "./dist",
    "rootDir": "./src",
    "declaration": true,
    "declarationMap": true,
    "sourceMap": true,
    "strict": true,
    "noUnusedLocals": true,
    "noUnusedParameters": true,
    "noFallthroughCasesInSwitch": true,
    "noImplicitReturns": true,
    "esModuleInterop": true,
    "skipLibCheck": true,
    "forceConsistentCasingInFileNames": true,
    "resolveJsonModule": true,
    "allowSyntheticDefaultImports": true
  },
  "include": ["src/**/*", "tests/**/*"],
  "exclude": ["node_modules", "dist"]
}
```

### tsconfig.build.json

Separate configuration for production builds:

```json
{
  "extends": "./tsconfig.json",
  "compilerOptions": {
    "sourceMap": false,
    "declarationMap": false
  },
  "include": ["src/**/*"],
  "exclude": ["node_modules", "dist", "tests", "**/*.test.ts"]
}
```

### .eslintrc.json

```json
{
  "parser": "@typescript-eslint/parser",
  "parserOptions": {
    "ecmaVersion": 2022,
    "sourceType": "module",
    "project": "./tsconfig.json"
  },
  "extends": [
    "eslint:recommended",
    "plugin:@typescript-eslint/recommended",
    "plugin:@typescript-eslint/recommended-requiring-type-checking"
  ],
  "plugins": ["@typescript-eslint"],
  "root": true,
  "env": {
    "node": true,
    "es2022": true
  },
  "rules": {
    "@typescript-eslint/no-unused-vars": ["error", { "argsIgnorePattern": "^_" }],
    "@typescript-eslint/explicit-function-return-type": "warn",
    "@typescript-eslint/no-explicit-any": "error",
    "@typescript-eslint/no-floating-promises": "error"
  }
}
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
npm install -D eslint @typescript-eslint/parser @typescript-eslint/eslint-plugin

# Create directory structure
mkdir -p src/lib tests

# Create initial files
touch src/index.ts tests/example.test.ts

# Lock Node version and enforce it
# Replace <NODE_LTS> with the current LTS major version from https://nodejs.org/en
# .nvmrc goes at the repo root — if this project lives in a subdirectory, write it one level up
echo "<NODE_LTS>" > .nvmrc
# .npmrc goes co-located with package.json (npm does not traverse up beyond the package root)
echo "engine-strict=true" > .npmrc
```

## npm ci vs npm install

- **Use `npm ci`** in CI pipelines, fresh checkouts, and Claude Code web sessions. It installs exactly what is in `package-lock.json`, never modifies the lock file, and fails fast if the lock file is missing or inconsistent.
- **Use `npm install <package>`** only when intentionally adding or updating a dependency.
- **Never run bare `npm install`** (no arguments) in CI or fresh environments — it re-resolves versions and may silently rewrite the lock file, which defeats reproducibility and can break CI.

### Common Commands

```bash
# Development with hot reload
npm run dev

# Build for production
npm run build

# Run tests
npm test

# Run tests with coverage
npm run test:coverage

# Lint code
npm run lint

# Format code
npm run prettier:fix

# Type check
npm run typecheck

# Run all checks (lint + format + typecheck + test)
npm run lint && npm run prettier:check && npm run typecheck && npm run test:run
```

## Testing Requirements

- Use Vitest for all tests
- Tests must live in `tests/` directory
- Minimum 80% code coverage required
- Coverage reports generated in `coverage/` directory
- Tests must be runnable via `npm test`

### Example Test

```typescript
// tests/example.test.ts
import { describe, it, expect } from 'vitest';
import { add } from '../src/lib/example';

describe('add', () => {
  it('should add two positive numbers', () => {
    expect(add(2, 3)).toBe(5);
  });

  it('should add negative numbers', () => {
    expect(add(-2, -3)).toBe(-5);
  });

  it('should handle zero', () => {
    expect(add(0, 5)).toBe(5);
  });
});
```

### Example Source

```typescript
// src/lib/example.ts
export function add(a: number, b: number): number {
  return a + b;
}
```

## Code Quality Standards

- All code must pass `npm run lint` with no errors
- All code must be formatted with Prettier
- All code must pass `npm run typecheck` with no errors
- Use strict TypeScript settings
- No `any` types (use `unknown` when necessary)
- Explicit return types for functions
- Handle promises properly (no floating promises)

## GitHub Actions

Create `.github/workflows/ci.yml`:

```yaml
name: jeff-skill-typescript-project

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

      - name: Setup Node.js
        uses: actions/setup-node@v4
        with:
          node-version: '<NODE_LTS>'
          cache: 'npm'

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

- Keep dependencies minimal
- Use `type: "module"` in package.json for ESM
- Pin dependency versions for reproducibility
- Use `tsx` for development with hot reload
- Build with `tsc` for production
- Never commit `node_modules/` or `dist/`
- Place `.nvmrc` (containing the current LTS major version from https://nodejs.org/en) at the repo root — nvm traverses up so one file covers all subprojects
- Place `.npmrc` containing `engine-strict=true` co-located with `package.json` — npm does not traverse up beyond the package root, so it must live alongside `package.json`
- Configure the session-start hook via the `session-start-hook` skill so Claude Code web sessions auto-install the current Node LTS version at container startup
- Export types from your library's main entry point

## For Library Projects

If building a library (not an application):

- Set `"main"` and `"types"` in package.json
- Build declaration files with `"declaration": true`
- Consider dual ESM/CJS exports if needed
- Test your library as a consumer would use it

## For Backend/API Projects

If building a backend API:

- Use environment variables for configuration
- Add request validation
- Use structured logging (pino, winston)

## AWS Lambda Development

When building AWS Lambda functions with TypeScript, use **AWS Lambda Powertools for TypeScript**:

```typescript
import { Logger } from '@aws-lambda-powertools/logger';
import { Tracer } from '@aws-lambda-powertools/tracer';
import type { APIGatewayProxyEvent, APIGatewayProxyResult, Context } from 'aws-lambda';

const logger = new Logger({ serviceName: 'userService' });
const tracer = new Tracer({ serviceName: 'userService' });

export const handler = async (event: APIGatewayProxyEvent, context: Context): Promise<APIGatewayProxyResult> => {
  logger.addContext(context);

  logger.info('Processing request', { requestId: context.requestId });

  try {
    // Your business logic here
    const result = { message: 'Success' };

    return {
      statusCode: 200,
      body: JSON.stringify(result)
    };
  } catch (error) {
    logger.error('Error processing request', { error });

    return {
      statusCode: 500,
      body: JSON.stringify({ error: 'Internal server error' })
    };
  }
};
```

### Key Powertools Features

- **Logger**: Structured JSON logging with context injection
- **Tracer**: X-Ray tracing for debugging and performance (normally disabled, enable when explicitly needed)
- **Event Handler**: Type-safe routing for API Gateway, ALB, Lambda Function URLs, AppSync - handles multiple routes
- **Parameters**: Easy access to SSM Parameter Store and Secrets Manager
- **Idempotency**: Built-in idempotency handling

### Lambda Best Practices for TypeScript

- Keep functions small and focused (single responsibility)
- Use environment variables for configuration
- Optimize for cold starts (minimize dependencies, avoid lazy loading, keep imports at top)
- Use typed event structures from `@types/aws-lambda`
- Return proper API Gateway response format
- Set appropriate memory and timeout values
- Use ARM64 (Graviton) architecture for better price/performance
- Use structured logging, not console.log

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

If you have 10+ routes in a single Lambda (which usually means you're doing something wrong - consider splitting into focused functions), use Event Handler:

```typescript
import { APIGatewayProxyEvent, APIGatewayProxyResult, Context } from 'aws-lambda';
import { Logger } from '@aws-lambda-powertools/logger';
import { ApiGatewayResolver } from '@aws-lambda-powertools/event-handler';

const logger = new Logger();
const app = new ApiGatewayResolver();

app.get('/users', async () => ({ users: [] }));
app.post('/users', async (event) => {
  const body = JSON.parse(event.body || '{}');
  return { user: { id: '123', ...body } };
});
app.get('/users/:id', async (event) => {
  const { id } = event.pathParameters || {};
  return { user: { id } };
});
// ... 7+ more routes (consider splitting!)

export const handler = (event: APIGatewayProxyEvent, context: Context): Promise<APIGatewayProxyResult> => {
  return app.resolve(event, context);
};
```

**Note:** Having 10+ routes in a single Lambda suggests poor function design. Lambda functions should be small and focused. Consider splitting into separate functions or using API Gateway to route to different Lambdas.

### Installing Powertools

```bash
# Core utilities (always install these)
npm install @aws-lambda-powertools/logger @aws-lambda-powertools/tracer
npm install -D @types/aws-lambda

# Event Handler (only if you have 10+ routes - see routing section above)
# npm install @aws-lambda-powertools/event-handler
```

## Integration with Other Skills

- **jeff-skill-install-dependabot** — Set up Dependabot to keep npm dependencies up to date
- **jeff-skill-dependabot-issue-resolution** — Resolve Dependabot PRs for npm package updates
