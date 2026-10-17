---
name: jeff-skill-angular-project
description: Install or update the Angular CLI and create zoneless, Tailwind-styled Angular apps with Node version pinning and a GitHub Actions CI workflow. Use when setting up an Angular dev environment, creating a new Angular app, updating Angular, or asked to "install Angular", "update Angular", or "create a new Angular app".
---

## Prerequisites

1. Ensure nvm (Node Version Manager) and Node.js are installed using the `jeff-skill-install-nodejs` skill.
2. Use WebSearch to verify current versions:
   - "Angular latest version [current-year]"
   - "Tailwind CSS latest version [current-year]"
   - Visit https://nodejs.org/en to find the current Node.js LTS major version (look for the "LTS" badge)
   - Update any version references in examples below with verified versions; don't guess them.

## Steps

1. Run `npm install -g @angular/cli` to install or update the CLI globally. For an existing app, update it with `ng update @angular/core @angular/cli`, following https://angular.dev/update-guide.
2. Confirm with `ng version` that the CLI is the latest release.
3. Create the app: `ng new <project-name> --style=css --ssr=false` (zoneless is the default from v21; on v20 add `--zoneless`).
   - For an existing app that still has zone.js, follow the zoneless steps in the Angular developer agent: `provideZonelessChangeDetection()` on v20, remove `zone.js` from `polyfills` in both `build` and `test` targets, `npm uninstall zone.js`.
   - Add `"build:prod": "ng build --configuration production"` to `package.json` scripts (the Netlify skill's Makefile uses it).
4. Use the latest stable version of `tailwindcss` as a `devDependency`. Refer to the documentation at https://tailwindcss.com/docs.
   - To install run `ng add tailwindcss` and confirm any prompts. This is equivalent to doing the following (just here for your reference in case something goes wrong or needs to be fixed):
     - `npm install -D tailwindcss @tailwindcss/postcss postcss`
     - Configure `.postcssrc.json` with the following content:

     ```
     {
        "plugins": {
           "@tailwindcss/postcss": {}
        }
     }
     ```

     - `src/styles.css` should contain `@import "tailwindcss"`;

5. Set up Netlify deployment using the `jeff-skill-angular-netlify` skill.

6. Create `.nvmrc` at the repo root (not inside the Angular project directory if it is a subproject) with the current Node LTS major version (visit https://nodejs.org/en and look for the "LTS" badge):

   ```
   <NODE_LTS>
   ```

7. Add an `engines` field to `package.json` and create `.npmrc` to enforce the Node version:

   In `package.json`, add (replacing `<NODE_LTS>` with the current LTS major version):

   ```json
   "engines": {
     "node": ">= <NODE_LTS>.0.0"
   }
   ```

   Create `.npmrc` in the same directory as `package.json` (npm does not traverse up beyond the package root):

   ```
   engine-strict=true
   ```

   With `engine-strict=true`, any `npm` command on the wrong Node version will error immediately instead of silently corrupting the lock file.

## GitHub Actions

Create `.github/workflows/<project>-ci.yml`.

Name the file after the project (e.g. `web-ci.yml`, `api-ci.yml`) rather than a generic `ci.yml`, so several projects in one repo each get their own workflow instead of overwriting each other.

**Scope triggers to this project's directory.** If this project lives at the repo root, omit `paths:` entirely — every change in the repo is relevant. If it shares a monorepo with other stacks (e.g. this Angular app next to a `golang/` backend or `infra/`), scope `paths:` to the project directory so an unrelated change (a README edit, another service's change) doesn't trigger this build. Always include the workflow file itself in `paths:` so edits to the CI config are still validated.

**Skip Dependabot-triggered runs.** Every job carries the Dependabot guard from `jeff-skill-install-dependabot` so Dependabot PRs and pushes don't consume Actions minutes. If you add a job, give it the same `if:`. If a job already has an `if:` condition, combine it with the guard using `&&` rather than replacing it, wrapping the existing condition in parentheses (e.g. `if: (existing-condition) && github.actor != 'dependabot[bot]' && ...`).

**Run steps in the project directory.** `defaults.run.working-directory` makes every `run:` step execute inside `<project-dir>`, where `package.json` lives. Omit the `defaults:` block entirely if the project is at the repo root. It does not apply to `uses:` steps, which is why the setup-node cache path below is spelled out relative to the repo root.

**Least privilege.** The workflow grants only `contents: read`, and checkout uses `persist-credentials: false` so the token is not left in `.git/config` for later steps.

The `prettier:check` script comes from the `jeff-skill-install-prettier` skill.

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

      - name: Format check
        run: npm run prettier:check

      - name: Run tests
        run: npx ng test --watch=false

      - name: Build
        run: npx ng build --configuration production
```

## npm ci vs npm install

`npm ci` in CI, fresh checkouts and Claude Code web sessions; `npm install <package>` only to add or update a dependency; never bare `npm install` in CI or scripts (it can rewrite the lockfile).

## Integration with Other Skills

- **jeff-skill-angular-aws-cognito**: Integrate AWS Cognito authentication into the Angular app
- **jeff-skill-angular-netlify**: Set up production Netlify deployment — full `netlify.toml` with caching headers, Makefile deploy target, and GitHub Actions CI/CD workflow
- **jeff-skill-tailwind-design-system**: Apply Tailwind v4 design tokens, component patterns, and theming after initial project setup
