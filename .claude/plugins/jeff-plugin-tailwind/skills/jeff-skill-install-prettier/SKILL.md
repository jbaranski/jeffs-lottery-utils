---
name: jeff-skill-install-prettier
description: Install and configure Prettier for JavaScript/TypeScript projects. Use when setting up a dev environment, fixing formatting issues, or asked to "install prettier", "configure prettier", or "set up code formatting".
---

Before proceeding, ensure nvm (Node Version Manager) and Node.js are installed using the `jeff-skill-install-nodejs` skill.

## Universal Config Rules

These six formatting options are a fixed fingerprint — apply them exactly in every project and sub-package. Never change, omit, or add to them without explicit instruction:

```json
{
  "printWidth": 120,
  "singleQuote": true,
  "semi": true,
  "tabWidth": 2,
  "trailingComma": "none",
  "endOfLine": "lf"
}
```

## Config File Format by Context

- **Root-level, CDK/infra packages, backend packages**: use `.prettierrc.json`
- **Angular client sub-packages** (inside a monorepo `client/` or `apps/web/` directory): use `.prettierrc.yaml`

`.prettierrc.yaml` format:

```yaml
printWidth: 120
singleQuote: true
semi: true
tabWidth: 2
trailingComma: 'none'
endOfLine: 'lf'
```

**Sub-packages never extend or reference a parent config.** Each package that has its own config duplicates the full rule set verbatim.

## Prettier Version

Add prettier as a dev dependency at the latest stable version:

```bash
npm install --save-dev prettier@latest
```

## npm Scripts

Every `package.json` that uses prettier defines exactly these two scripts. Use `prettier` directly (not `npx prettier`):

```json
{
  "scripts": {
    "prettier:check": "prettier --check .",
    "prettier:fix": "prettier --write ."
  }
}
```

## Makefile (non-JS projects only)

If no `package.json` exists in the project root, create or append these targets to a `Makefile`:

```makefile
.PHONY: prettier-fix prettier-check

prettier-fix:
	npx prettier --write .

prettier-check:
	npx prettier --check .
```

## Monorepo Root Makefile

In a monorepo where sub-packages own their own prettier config, the root `Makefile` must have `prettier` and `prettier-check` targets that:

1. Delegate to each sub-package that owns its own prettier (via its `npm run prettier:fix` / `npm run prettier:check` script)
2. Run the root prettier last (covering everything the sub-packages exclude)

Each sub-package that has a buildable output (e.g. an Angular app) must also have a dedicated `build-<name>` target using `$(MAKE) -C <dir> build` — **never** `cd <dir> && make build`. This keeps the pattern consistent with other subproject targets and allows root-level build checks without entering subdirectories.

```makefile
prettier:
	cd apps/web && npm run prettier:fix
	cd infra && npm run prettier:fix
	npx prettier --write .

prettier-check:
	cd apps/web && npm run prettier:check
	cd infra && npm run prettier:check
	npx prettier --check .

build-web:
	$(MAKE) -C apps/web build
```

Add `prettier`, `prettier-check`, and `build-web` (and any other build targets) to the `.PHONY` declaration.

**Always run `make prettier` (not `npx prettier --write .` directly) when formatting the whole monorepo.** Running prettier from the root without the Makefile target skips sub-package formatting.

**Always run `make build-web` (not `cd apps/web && make build`) for pre-commit build checks.** All subproject operations must go through root Makefile targets.

## .prettierignore Patterns by Context

### Single-package Angular project (one `.prettierignore` at root)

```
node_modules
/dist/*
build
coverage
src/index.html
*.js
*.gitkeep
*.ico
*.png
public/site.webmanifest
```

Also add `scripts/update-csp-hash.js` if that file exists in the project.

### Angular client sub-package (inside a monorepo)

Same as single-package Angular above — applied within the sub-package directory.

### Root monorepo `.prettierignore`

The root `.prettierignore` must **exclude the entire directory** of every sub-package that owns its own prettier config. This prevents the root prettier from touching files those sub-packages manage themselves:

```
node_modules
dist
build
coverage
client/src/index.html
apps/web/
infra/
```

Replace `apps/web/` and `infra/` with the actual sub-package directories (e.g. `client/`, `client/src/`). Do **not** list individual file exclusions from sub-packages here — exclude the whole directory instead.

### CDK / infra package

```
node_modules/
dist/
cdk.out/
*.js
```

### Backend-only root (no separate client/infra sub-packages)

```
node_modules
dist
cdk.out
build
coverage
*.js
*.d.ts
```

## What NOT to Do

- Do not add prettier config under a `"prettier"` key in `package.json`
- Do not create `prettier.config.js` or `prettier.config.ts`
- Do not add prettier to `dependencies` (only `devDependencies`)
- Do not put additional prettier config in sub-package `package.json` files beyond the two scripts
- Do not have sub-package configs inherit or extend a parent config
- Do not run `npx prettier --write .` from the monorepo root directly — always use `make prettier`

If extra prettier configuration exists in `package.json` or any other non-standard location, remove it and consolidate everything into `.prettierrc.json` / `.prettierrc.yaml` and `.prettierignore`.

## `<!-- prettier-ignore -->` Is a Last Resort

Never add a `<!-- prettier-ignore -->` (or `// prettier-ignore` / `# prettier-ignore`) comment to silence a formatting failure. First try, in order:

1. Reformat the offending block by hand so Prettier's own output is acceptable.
2. Adjust the file's config (`.prettierrc.json` / `.prettierrc.yaml`) if the universal fingerprint genuinely doesn't fit the file type.
3. Exclude the specific file or directory via `.prettierignore` if it shouldn't be formatted at all.

Only reach for an inline `prettier-ignore` directive after all three of the above are exhausted and there is no other path forward — e.g. hand-aligned ASCII tables or output that must preserve exact whitespace for a downstream tool. Treat every use as exceptional: state in a PR description or nearby comment why none of the alternatives worked.
