# GitHub Actions

Create `.github/workflows/<project>-ci.yml`.

Name the file after the project (e.g. `web-ci.yml`, `api-ci.yml`) rather than a generic `ci.yml`, so several projects in one repo each get their own workflow instead of overwriting each other.

**Scope triggers to this project's directory.** If this project lives at the repo root, omit `paths:` entirely — every change in the repo is relevant. If it shares a monorepo with other stacks (e.g. this TypeScript service next to a `golang/` backend or `infra/`), scope `paths:` to the project directory so an unrelated change (a README edit, another service's change) doesn't trigger this build. Always include the workflow file itself in `paths:` so edits to the CI config are still validated.

**Skip Dependabot-triggered runs.** Every job carries the Dependabot guard from `jeff-skill-install-dependabot` so Dependabot PRs and pushes don't consume Actions minutes. If you add a job, give it the same `if:`. If a job already has an `if:` condition, combine it with the guard using `&&` rather than replacing it, wrapping the existing condition in parentheses (e.g. `if: (existing-condition) && github.actor != 'dependabot[bot]' && ...`).

**Run steps in the project directory.** `defaults.run.working-directory` makes every `run:` step execute inside `<project-dir>`, where `package.json` lives. Omit the `defaults:` block entirely if the project is at the repo root. It does not apply to `uses:` steps, which is why the setup-node cache path below is spelled out relative to the repo root.

**Least privilege.** The workflow grants only `contents: read`, and checkout uses `persist-credentials: false` so the token is not left in `.git/config` for later steps.

**Pin every action to a commit SHA.** Each `uses:` is `owner/repo@<commit-sha> # <tag>`: replace `<commit-sha>` with the full commit the tag points to — `git ls-remote https://github.com/<owner>/<repo> 'refs/tags/<tag>^{}' refs/tags/<tag> | tail -1 | cut -f1` — and keep the tag comment. A tag can be moved to different code; a commit SHA can't. Dependabot's `github-actions` entry keeps both up to date.

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
      - uses: actions/checkout@<commit-sha> # v7.0.1
        with:
          persist-credentials: false

      - name: Setup Node.js
        uses: actions/setup-node@<commit-sha> # v7.1.0
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
