---
name: jeff-skill-angular-netlify
description: Scaffold Netlify deployment for an Angular SPA project. Generates netlify.toml, a Makefile deploy target, and a GitHub Actions workflow. Use when asked to "deploy to Netlify", "set up Netlify for Angular", or "add Netlify CI/CD".
---

# Netlify Angular Deployment Skill

Use this skill to scaffold Netlify deployment for an Angular SPA project.

---

## Step 1 — Discover from the codebase

Before asking the user anything, read these files and extract the values below.

| What                     | Where to find it                                                                                                   |
| ------------------------ | ------------------------------------------------------------------------------------------------------------------ |
| Angular app directory    | Find `angular.json`                                                                                                |
| `dist/` output path      | `angular.json` → `projects.<name>.architect.build.options.outputPath`                                              |
| Node version             | `.nvmrc` at repo root, or `package.json` `engines.node`                                                            |
| `package-lock.json` path | Relative to repo root, alongside `package.json`                                                                    |
| Existing `Makefile`      | Check if one exists in the Angular app directory; note which targets are already defined (`lint`, `test`, `build`) |
| CI `working-directory`   | Same directory that contains `angular.json`                                                                        |

---

## Step 2 — Ask the user (only what can't be discovered)

1. **Static sub-pages:** Does this app serve any static files outside the Angular SPA (e.g. a `/demo` page at `public/demo/index.html`)? If yes, what URL paths?
2. **GitHub environment name:** What is the GitHub Actions environment that holds deployment secrets? _(default: `prod`)_
3. **CI workflow file name:** What should the workflow file be called? _(default: `deploy-web`)_
4. **Concurrency group name:** What should the CI concurrency group be named? _(default: same as workflow file name)_

---

## Step 3 — Generate these files

### `netlify.toml`

Place in the Angular app directory (same level as `angular.json`).

```toml
# --- Only include this block if the user has static sub-pages ---
# Redirect /demo → /demo/ so Netlify serves the directory index, not a 404
[[redirects]]
  from = "/demo"
  to = "/demo/"
  status = 301
# ----------------------------------------------------------------

# SPA catch-all: all Angular routes serve index.html (status 200 = rewrite, not redirect)
[[redirects]]
  from = "/*"
  to = "/index.html"
  status = 200

# index.html: browser must always revalidate; Netlify CDN holds it durably
[[headers]]
  for = "/index.html"
  [headers.values]
    Cache-Control = "no-cache"
    Netlify-CDN-Cache-Control = "public, max-age=31536000, durable"

# Hashed JS assets: immutable on the browser (filename changes every build)
[[headers]]
  for = "/*.js"
  [headers.values]
    Cache-Control = "public, max-age=31536000, immutable"
    Netlify-CDN-Cache-Control = "public, max-age=31536000, durable"

# Hashed CSS assets: same immutable strategy
[[headers]]
  for = "/*.css"
  [headers.values]
    Cache-Control = "public, max-age=31536000, immutable"
    Netlify-CDN-Cache-Control = "public, max-age=31536000, durable"
```

**Caching strategy explained:**

- `index.html` uses a split strategy: `no-cache` forces the browser to revalidate on every load, while `Netlify-CDN-Cache-Control: durable` lets Netlify's CDN cache it long-term and serve it globally at edge speed. When you deploy, Netlify invalidates its own CDN cache automatically.
- JS/CSS files are content-hashed by Angular's build pipeline, so their filenames change on every build. `immutable` tells browsers they never need to revalidate; `durable` keeps them cached at the CDN edge indefinitely.

---

### `Makefile` — `deploy` target

Add to the existing `Makefile` in the Angular app directory, or create one if absent. Fill in `<app-name>` from the `outputPath` discovered in Step 1.

```makefile
.PHONY: all build test lint deploy

all: lint test build

lint:
	npm run prettier:check

test:
	npx ng test --watch=false --browsers=ChromeHeadlessNoSandbox

# update-csp hashes the inline scripts in the BUILT index.html, so it must run after the build.
build:
	npm run build:prod
	npm run update-csp

# netlify-cli is NOT added as a devDependency — npx downloads it at deploy time.
# Update --dir to match angular.json outputPath (typically dist/<app-name>/browser).
deploy: build
	npx netlify-cli deploy --prod --dir=dist/<app-name>/browser
```

> If `lint`, `test`, or `build` targets already exist in the Makefile, only add the `deploy` target and update the `.PHONY` line.

---

### `.github/workflows/deploy-web.yml`

Fill in `<app-directory>`, `<node-version>`, and `<lockfile-path>` from Step 1. Add any additional environment secrets your app needs (e.g. API URLs, feature flags) alongside `NETLIFY_AUTH_TOKEN` and `NETLIFY_SITE_ID` in the Deploy step.

```yaml
name: deploy-web

on:
  push:
    branches: [main]
    paths:
      - <app-directory>/** # scope to this Angular app so other stacks in the repo (e.g. a golang/ service) don't trigger a deploy
      - .github/workflows/deploy-web.yml
  workflow_dispatch: # also triggerable ad-hoc from the GitHub Actions UI

concurrency:
  group: deploy-web
  cancel-in-progress: false # never cancel an in-flight deploy

jobs:
  deploy:
    name: Angular — lint, test & deploy to Netlify
    runs-on: ubuntu-latest
    environment: prod # GitHub environment gate; secrets live here
    defaults:
      run:
        working-directory: <app-directory>
    steps:
      - uses: actions/checkout@v6

      - uses: actions/setup-node@v6
        with:
          node-version: '<node-version>'
          cache: npm
          cache-dependency-path: <lockfile-path>

      - name: Install dependencies
        run: npm ci

      - name: Lint
        run: make lint

      - name: Test
        run: make test

      - name: Deploy
        run: make deploy
        env:
          NETLIFY_AUTH_TOKEN: ${{ secrets.NETLIFY_AUTH_TOKEN }}
          NETLIFY_SITE_ID: ${{ secrets.NETLIFY_SITE_ID }}
          # Add any additional secrets the app needs at build/deploy time:
          # MY_API_URL: ${{ secrets.MY_API_URL }}

      # Must run after Deploy: `make build` regenerates the CSP hashes from the built index.html.
      - name: Commit netlify.toml if CSP hashes were updated
        working-directory: ${{ github.workspace }}
        run: |
          git diff --quiet <app-directory>/netlify.toml && exit 0
          git config user.name "JEFF-bot"
          git config user.email "actions@users.noreply.github.com"
          git add <app-directory>/netlify.toml
          git commit -m "chore: update CSP script hashes [skip ci]"
          git push
```

The job also needs `permissions: contents: write` for that push.

**Triggers:** Deploys automatically on every merge to `main` that touches `<app-directory>/**` (or the workflow file itself), and can also be triggered ad-hoc from the GitHub Actions UI or via `gh workflow run deploy-web`. If `<app-directory>` is the repo root (not a monorepo), drop the `paths:` filter — every change is relevant.

**Why `cancel-in-progress: false`?**
An in-flight deploy to Netlify should never be interrupted mid-upload. A new deploy queues behind the current one.

---

### Angular route guard for static sub-pages

Only needed if the user answered "yes" in Step 2, question 1.

`ng serve` uses `historyApiFallback`, which intercepts every URL and returns Angular's `index.html`. A static file at `public/demo/index.html` would never be reached in development without this guard.

Add to `app.routes.ts` for each static sub-page path:

```typescript
{
  path: 'demo',    // replace with the actual path, without leading slash
  canActivate: [
    () => {
      // In production, Netlify serves public/demo/index.html directly.
      // In development, ng serve intercepts this route — redirect to escape the SPA router.
      window.location.href = '/demo/index.html';
      return false;
    }
  ],
  component: AppComponent,    // placeholder, never rendered
},
```

In production, Netlify serves the real file and the `301` redirect in `netlify.toml` handles the `/demo` → `/demo/` trailing-slash normalisation. The route guard only fires locally.

---

## Optional: PostHog Integration

If the project uses PostHog analytics, keep the init snippet **inline in `src/index.html`**. Do not extract it to an external file.

**Why hashes, and why they're generated:** Angular's critical-CSS inliner (Beasties) loads the full stylesheet with `media="print"` and flips it to `all` with inline JS. Beasties < 0.5 used a `<link onload="this.media='all'">` handler (needs `'unsafe-hashes'`); Beasties >= 0.5 (Angular 22.2+) injects an inline `<script>` instead. Either way the CSP must allow it, and its hash changes when Beasties changes — if it's stale, the browser blocks it and the page renders **unstyled**. So the CSP hashes are never maintained by hand: `scripts/update-csp-hash.js` hashes every inline `<script>` in the **built** `index.html` (PostHog + Beasties) and rewrites the whole list. Keep `'unsafe-hashes'` for older Angular versions; it's harmless otherwise.

### 1. Add the PostHog snippet inline in `src/index.html`

Paste the PostHog snippet as the first inline `<script>` in `<head>`. Add a comment so future editors know the hash in `netlify.toml` must stay in sync:

```html
<!-- PostHog analytics — inline; its CSP sha256 is regenerated by `make build`
     (build, then `npm run update-csp`). Commit netlify.toml after changing this. -->
<script>
  /* paste PostHog snippet here */
</script>
```

### 2. Add CSP headers to `netlify.toml`

Add a headers block for `/*`. The `sha256-...` list is generated — it covers every inline script in the built `index.html` (PostHog + Beasties loader):

```toml
# script-src sha256 hashes are generated: `make build` hashes every inline <script> in the built
# index.html (PostHog snippet + Beasties stylesheet loader) and rewrites this list. Don't edit by hand.
[[headers]]
  for = "/*"
  [headers.values]
    Content-Security-Policy = "default-src 'self'; script-src 'self' 'unsafe-hashes' 'sha256-PLACEHOLDER' https://p.jeffsoftware.com; connect-src 'self' https://p.jeffsoftware.com; img-src 'self' data:; style-src 'self' 'unsafe-inline';"
```

Replace `PLACEHOLDER` by running `make build` (see below) — it fills in one hash per inline script. The PostHog custom proxy `https://p.jeffsoftware.com` must appear in both `script-src` and `connect-src` — PostHog's inline init snippet dynamically fetches and injects `array.js` as a `<script>` element, so `connect-src` alone will not unblock it.

### 3. Add `scripts/update-csp-hash.js`

Create this file in the Angular app directory. It hashes every inline `<script>` in the built `index.html` and rewrites the sha256 list in `netlify.toml` — so neither a PostHog edit nor an Angular/Beasties upgrade ever requires touching the CSP by hand. Replace `<app-name>` with the `outputPath` from Step 1. `--check` verifies without writing (used by the PR check below):

```js
#!/usr/bin/env node
// Hashes every inline <script> in the BUILT index.html (PostHog snippet plus anything the
// build injects, e.g. the Beasties stylesheet loader) and rewrites the sha256 list in the
// script-src directive of netlify.toml to match. Run after `npm run build:prod`.
// Pass --check to only verify (exit 1 on mismatch) without writing.
const { createHash } = require('node:crypto');
const { existsSync, readFileSync, writeFileSync } = require('node:fs');
const { join } = require('node:path');

const root = join(__dirname, '..');
const check = process.argv.includes('--check');

const indexPath = join(root, 'dist/<app-name>/browser/index.html');
if (!existsSync(indexPath)) {
  console.error(`${indexPath} not found -- run \`npm run build:prod\` first`);
  process.exit(1);
}

const indexHtml = readFileSync(indexPath, 'utf8');
const inlineScripts = [...indexHtml.matchAll(/<script(?![^>]*\ssrc=)[^>]*>([\s\S]*?)<\/script>/g)];
if (inlineScripts.length === 0) {
  console.error('No inline <script> found in built index.html');
  process.exit(1);
}

const hashes = inlineScripts.map((m) => `'sha256-${createHash('sha256').update(m[1], 'utf8').digest('base64')}'`);

const tomlPath = join(root, 'netlify.toml');
const toml = readFileSync(tomlPath, 'utf8');
const sha256List = /'sha256-[A-Za-z0-9+/=]+'(?: 'sha256-[A-Za-z0-9+/=]+')*/;
if (!sha256List.test(toml)) {
  console.error('No sha256 tokens found in netlify.toml script-src');
  process.exit(1);
}
const updated = toml.replace(sha256List, hashes.join(' '));

if (updated === toml) {
  console.log(`CSP hashes up to date: ${hashes.join(' ')}`);
} else if (check) {
  console.error(`netlify.toml CSP hashes are stale. Expected: ${hashes.join(' ')}`);
  console.error('Run `npm run build:prod && npm run update-csp` and commit netlify.toml.');
  process.exit(1);
} else {
  writeFileSync(tomlPath, updated);
  console.log(`netlify.toml updated with: ${hashes.join(' ')}`);
}
```

### 4. Expose as `npm run update-csp` and wire into `make build`

In `package.json`:

```json
"scripts": {
  "update-csp": "node scripts/update-csp-hash.js"
}
```

In the `Makefile`, the `build` target must run the Angular build **first**, then hash its output:

```makefile
build:
	npm run build:prod
	npm run update-csp
```

### 4b. Fail PRs whose CSP hashes are stale

The deploy workflow self-heals, but a PR (e.g. a Dependabot Angular bump that changes Beasties) should be flagged before merge. Add `.github/workflows/csp-check.yml`:

```yaml
name: csp-check

on:
  pull_request:
    paths:
      - <app-directory>/**
      - .github/workflows/csp-check.yml

jobs:
  csp-check:
    name: CSP hashes match build output
    runs-on: ubuntu-latest
    defaults:
      run:
        working-directory: <app-directory>
    steps:
      - uses: actions/checkout@v6

      - uses: actions/setup-node@v6
        with:
          node-version: '<node-version>'
          cache: npm
          cache-dependency-path: <lockfile-path>

      - run: npm ci

      - run: npm run build:prod

      # Fails if netlify.toml's script-src hashes don't match the built index.html.
      # Fix locally with `make build` and commit netlify.toml.
      - run: node scripts/update-csp-hash.js --check
```

### 5. Allow `scripts/*.js` in `.gitignore`

If the repo's root `.gitignore` blocks `*.js`, add an exception in the Angular app directory's own `.gitignore`:

```
!scripts/*.js
```

### 6. Add `.prettierignore` entries in the Angular app directory

Create (or update) a `.prettierignore` file **inside the Angular app directory** (same level as `angular.json`), not only at the repo root. CI invokes prettier from the Angular app directory, and prettier resolves ignore patterns relative to the CWD where it is invoked — patterns in a parent-directory `.prettierignore` are also resolved relative to that same CWD, so always put these entries in the app-directory `.prettierignore` to be explicit and safe:

```
# CommonJS require() in the CSP hash script may be flagged by prettier
scripts/update-csp-hash.js

# PostHog inline snippet in index.html must never be reformatted by prettier
# (reformatting changes whitespace inside the <script> block, invalidating the sha256 hash)
src/index.html
```

---

## Step 4 — Post-generation checklist

Remind the user to complete these manual steps before the first deploy:

- [ ] **Create the Netlify site** — go to app.netlify.com, add a new site (import from Git or create manually)
- [ ] **Set the publish directory** in Netlify site settings to match the `--dir` value in the Makefile (e.g. `dist/<app-name>/browser`)
- [ ] **Add `NETLIFY_AUTH_TOKEN`** to the GitHub `<github-environment>` environment secrets — generate at: Netlify → User Settings → Applications → Personal access tokens
- [ ] **Add `NETLIFY_SITE_ID`** to the same GitHub environment secrets — find it at: Netlify → Site Settings → General → Site details → Site ID
- [ ] **Trigger the workflow** from the GitHub Actions UI to confirm end-to-end deployment works
