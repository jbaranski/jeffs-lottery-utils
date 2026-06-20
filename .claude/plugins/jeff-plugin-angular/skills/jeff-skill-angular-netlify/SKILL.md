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

build:
	npm run update-csp
	npm run build:prod

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
```

**Triggers:** Deploys automatically on every merge to `main`, and can also be triggered ad-hoc from the GitHub Actions UI or via `gh workflow run deploy-web`.

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

**Why inline is required:** Angular's build tool (Beasties) generates `<link onload="...">` event handlers for CSS preloading. These are inline event handlers that require `'unsafe-hashes'` in the CSP `script-src` — regardless of PostHog. Since `'unsafe-hashes'` must be present anyway, the PostHog inline script needs only a `sha256-...` hash added alongside it. Removing `'unsafe-hashes'` to avoid the hash breaks CSS entirely.

### 1. Add the PostHog snippet inline in `src/index.html`

Paste the PostHog snippet as the first inline `<script>` in `<head>`. Add a comment so future editors know the hash in `netlify.toml` must stay in sync:

```html
<!-- PostHog analytics — inline so Beasties CSS preload handlers (which also need
     'unsafe-hashes') share the same CSP exception. If you change this snippet,
     run `npm run update-csp` to recompute the sha256 hash in netlify.toml. -->
<script>
  /* paste PostHog snippet here */
</script>
```

### 2. Add CSP headers to `netlify.toml`

Add a headers block for `/*`. The `sha256-...` value covers the PostHog inline script; `'unsafe-hashes'` covers Beasties' `<link onload="...">` handlers. Add a comment so future editors know only the first `sha256-` token is replaced by the automation script:

```toml
# CRITICAL: PostHog sha256 MUST be first — `npm run update-csp` replaces only the first sha256 token.
# Second sha256 = Beasties CSS preload handler (this.media='all') — static, never changes, do not remove.
[[headers]]
  for = "/*"
  [headers.values]
    Content-Security-Policy = "default-src 'self'; script-src 'self' 'unsafe-hashes' 'sha256-PLACEHOLDER' 'sha256-MhtPZXr7+LpJUY5qtMutB+qWfQtMaPccfe7QXtCcEYc='; connect-src 'self' https://us.i.posthog.com https://us-assets.i.posthog.com; img-src 'self' data:; style-src 'self' 'unsafe-inline';"
```

Replace `PLACEHOLDER` by running `npm run update-csp` (see below). Adjust `connect-src` to match the PostHog region/endpoint in your PostHog project settings.

### 3. Add `scripts/update-csp-hash.js`

Create this file in the Angular app directory. It reads the first inline `<script>` from `index.html`, computes its SHA-256, and patches the hash in `netlify.toml` — so updating the PostHog snippet never requires manually touching the CSP:

```js
#!/usr/bin/env node
// Recomputes the SHA-256 hash of the first inline <script> in src/index.html
// and writes the updated hash into the script-src directive in netlify.toml.
// Run this after changing the PostHog snippet, then commit both files.
const { createHash } = require('node:crypto');
const { readFileSync, writeFileSync } = require('node:fs');
const { join } = require('node:path');

const root = join(__dirname, '..');

const indexHtml = readFileSync(join(root, 'src/index.html'), 'utf8');
const match = indexHtml.match(/<script>([\s\S]*?)<\/script>/);
if (!match) {
  console.error('No inline <script> found in src/index.html');
  process.exit(1);
}

const hash = `sha256-${createHash('sha256').update(match[1], 'utf8').digest('base64')}`;

const tomlPath = join(root, 'netlify.toml');
const toml = readFileSync(tomlPath, 'utf8');
const updated = toml.replace(/'sha256-[A-Za-z0-9+/=]+'/, `'${hash}'`);

if (updated === toml) {
  console.log(`CSP hash already up to date: '${hash}'`);
} else {
  writeFileSync(tomlPath, updated);
  console.log(`netlify.toml updated with: '${hash}'`);
}
```

### 4. Expose as `npm run update-csp` and wire into `make build`

In `package.json`:

```json
"scripts": {
  "update-csp": "node scripts/update-csp-hash.js"
}
```

In the `Makefile`, update the `build` target so the hash is recomputed first, then the Angular build runs:

```makefile
build:
	npm run update-csp
	npm run build:prod
```

### 5. Allow `scripts/*.js` in `.gitignore`

If the repo's root `.gitignore` blocks `*.js`, add an exception in the Angular app directory's own `.gitignore`:

```
!scripts/*.js
```

### 6. Add `.prettierignore` for the script

`scripts/update-csp-hash.js` uses CommonJS `require` — Prettier may flag it depending on your config. Add to `.prettierignore`:

```
scripts/update-csp-hash.js
```

---

## Step 4 — Post-generation checklist

Remind the user to complete these manual steps before the first deploy:

- [ ] **Create the Netlify site** — go to app.netlify.com, add a new site (import from Git or create manually)
- [ ] **Set the publish directory** in Netlify site settings to match the `--dir` value in the Makefile (e.g. `dist/<app-name>/browser`)
- [ ] **Add `NETLIFY_AUTH_TOKEN`** to the GitHub `<github-environment>` environment secrets — generate at: Netlify → User Settings → Applications → Personal access tokens
- [ ] **Add `NETLIFY_SITE_ID`** to the same GitHub environment secrets — find it at: Netlify → Site Settings → General → Site details → Site ID
- [ ] **Trigger the workflow** from the GitHub Actions UI to confirm end-to-end deployment works
