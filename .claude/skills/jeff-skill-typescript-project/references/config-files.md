# Configuration Files and Project Setup

## package.json

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
    "dev": "node --watch src/index.ts",
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
    "typescript": "~6.0.3",
    "vitest": "^5.0.4"
  }
}
```

TypeScript stays on `~6.0.x` until `typescript-eslint` supports 7.x — as of October 2026 its peer range is `>=4.8.4 <6.1.0`, while TypeScript 7.0 is the npm `latest`. Check `npm view typescript-eslint peerDependencies` before moving to 7.

## tsconfig.json

Type-checks sources and tests (`npm run typecheck`); it never emits. The last three module options before
`skipLibCheck` are what let `node src/index.ts` run the source directly — see Configuration Rules in SKILL.md.

```json
{
  "compilerOptions": {
    "target": "ES2022",
    "module": "NodeNext",
    "lib": ["ES2022"],
    "types": ["node"],
    "strict": true,
    "noEmit": true,
    "noUnusedLocals": true,
    "noUnusedParameters": true,
    "noFallthroughCasesInSwitch": true,
    "noImplicitReturns": true,
    "erasableSyntaxOnly": true,
    "verbatimModuleSyntax": true,
    "rewriteRelativeImportExtensions": true,
    "skipLibCheck": true,
    "forceConsistentCasingInFileNames": true,
    "resolveJsonModule": true
  },
  "include": ["src/**/*", "tests/**/*"]
}
```

## tsconfig.build.json

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

## eslint.config.js

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

## vitest.config.ts

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

## .gitignore

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

## Initialize Project

```bash
# Create project directory
mkdir project-name && cd project-name

# Initialize npm project
npm init -y

# Install TypeScript and build tools
npm install -D typescript @types/node

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
