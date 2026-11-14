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
   - Update all version numbers in the reference examples with verified versions
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

## Configuration Rules

- ESM only: `"type": "module"` in package.json.
- `tsconfig.json` is `strict`, type-checks `src/` and `tests/` (`npm run typecheck`), and never emits.
  `tsconfig.build.json` extends it and emits `src/` only, with declarations, into `dist/`.
- ESLint 10 only reads flat config (`eslint.config.js` with `typescript-eslint` `recommendedTypeChecked`) — `.eslintrc.*`
  files and the `--ext` flag were removed, so don't create or keep them.
- TypeScript stays on `~6.0.x` until `typescript-eslint` supports 7.x — as of October 2026 its peer range is
  `>=4.8.4 <6.1.0`, while TypeScript 7.0 is the npm `latest`. Check `npm view typescript-eslint peerDependencies` before
  moving to 7.
- **Node runs the TypeScript source directly** (type stripping is stable since Node 24.12), so there is no `tsx`:
  `npm run dev` is `node --watch src/index.ts`; `tsc` builds `dist/` for production. This only works for code Node can
  strip, which `tsconfig.json` enforces:
  - `"module": "NodeNext"` — never `Bundler`/`ESNext` for code that runs in Node without a bundler. Bundler resolution
    accepts extensionless relative imports that type-check and build cleanly, then crash at runtime with
    `ERR_MODULE_NOT_FOUND`.
  - Relative imports name the `.ts` file (`import { greet } from './lib/greet.ts'`);
    `rewriteRelativeImportExtensions` turns them into `.js` in `dist/`.
  - `erasableSyntaxOnly`: no `enum`, runtime `namespace`, parameter properties or `import =` — use `as const` objects
    and plain constructor assignments.
  - `verbatimModuleSyntax`: type-only imports use `import type` (or an inline `type` modifier), or Node fails on them.
- Place `.nvmrc` (containing the current LTS major version from https://nodejs.org/en) at the repo root — nvm traverses
  up so one file covers all subprojects.
- Place `.npmrc` containing `engine-strict=true` co-located with `package.json` — npm does not traverse up beyond the
  package root, so it must live alongside `package.json`.

## npm ci vs npm install

- **Use `npm ci`** in CI pipelines, fresh checkouts, and Claude Code web sessions. It installs exactly what is in `package-lock.json`, never modifies the lock file, and fails fast if the lock file is missing or inconsistent.
- **Use `npm install <package>`** only when intentionally adding or updating a dependency.
- **Never run bare `npm install`** (no arguments) in CI or fresh environments — it re-resolves versions and may silently rewrite the lock file, which defeats reproducibility and can break CI.

## Testing Requirements

- Use Vitest for all tests
- Tests must live in `tests/` directory
- Minimum 80% code coverage required (enforced by `thresholds` in `vitest.config.ts`)
- Coverage reports generated in `coverage/` directory
- Tests must be runnable via `npm test`

## CI

Workflow named `<project>-ci.yml`, `contents: read` only, checkout with `persist-credentials: false`, every action pinned to a commit SHA (see the reference), the Dependabot
guard on every job, `paths:` scoped to the project directory in a monorepo. It runs `npm ci`, typecheck, lint, format
check, tests with coverage, and build.

## For Library Projects

If building a library (not an application):

- Set `"main"` and `"types"` in package.json
- Build declaration files with `"declaration": true`
- Consider dual ESM/CJS exports if needed
- Test your library as a consumer would use it

## References (read on demand)

| Read                                                         | When                                                                                   |
| ------------------------------------------------------------ | -------------------------------------------------------------------------------------- |
| [references/config-files.md](references/config-files.md)     | Creating a project or changing package.json, tsconfig, ESLint, Vitest, or `.gitignore` |
| [references/github-actions.md](references/github-actions.md) | Creating or changing the CI workflow                                                   |
| [references/aws-lambda.md](references/aws-lambda.md)         | Writing AWS Lambda functions in TypeScript (Powertools, routing, cold starts)          |

## Integration with Other Skills

- **jeff-skill-install-dependabot** — Set up Dependabot to keep npm dependencies up to date
- **jeff-skill-dependabot-issue-resolution** — Resolve Dependabot PRs for npm package updates
