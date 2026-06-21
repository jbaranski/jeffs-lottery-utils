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

### Root monorepo `.prettierignore` (covers everything not caught by sub-package ignores)

```
node_modules
dist
build
coverage
client/src/index.html
```

Also add `client/scripts/update-csp-hash.js` if that file exists. Replace `client/` with the actual client directory name (e.g. `apps/web/`).

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

If extra prettier configuration exists in `package.json` or any other non-standard location, remove it and consolidate everything into `.prettierrc.json` / `.prettierrc.yaml` and `.prettierignore`.

## Key Notes

- `src/index.html` is always excluded for Angular projects — it is framework-generated
- `*.js` in TypeScript projects means compiled output — always exclude it
- `cdk.out/` must be in CDK/infra `.prettierignore` — it contains synthesized CloudFormation
- `scripts/update-csp-hash.js` appears in Angular ignore lists whenever a CSP hash update script is present

## Additional Resources

- Prettier documentation: https://prettier.io/docs/
