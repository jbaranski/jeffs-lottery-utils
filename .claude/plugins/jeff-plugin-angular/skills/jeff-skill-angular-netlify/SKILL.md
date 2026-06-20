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
	npm run prod:build

# netlify-cli is NOT added as a devDependency — npx downloads it at deploy time.
# Update --dir to match angular.json outputPath (typically dist/<app-name>/browser).
deploy: build
	npx netlify-cli deploy --prod --dir=dist/<app-name>/browser
```

> If `lint`, `test`, or `build` targets already exist in the Makefile, only add the `deploy` target and update the `.PHONY` line.

---

### `.github/workflows/<workflow-name>.yml`

Fill in `<workflow-name>`, `<app-directory>`, `<node-version>`, `<lockfile-path>`, and `<github-environment>` from Steps 1–2.

```yaml
name: <workflow-name>

on:
  workflow_dispatch: # manual trigger only — no auto-deploy on push

concurrency:
  group: <concurrency-group>
  cancel-in-progress: false # never cancel an in-flight deploy

jobs:
  deploy:
    name: Angular — lint, test & deploy to Netlify
    runs-on: ubuntu-latest
    environment: <github-environment> # GitHub environment gate; secrets live here
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
```

**Why `workflow_dispatch` only?**
Netlify deployments are intentional, not automatic. This prevents a bad push from immediately going to production. Trigger from the GitHub Actions UI or via `gh workflow run <workflow-name>`.

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

## Step 4 — Post-generation checklist

Remind the user to complete these manual steps before the first deploy:

- [ ] **Create the Netlify site** — go to app.netlify.com, add a new site (import from Git or create manually)
- [ ] **Set the publish directory** in Netlify site settings to match the `--dir` value in the Makefile (e.g. `dist/<app-name>/browser`)
- [ ] **Add `NETLIFY_AUTH_TOKEN`** to the GitHub `<github-environment>` environment secrets — generate at: Netlify → User Settings → Applications → Personal access tokens
- [ ] **Add `NETLIFY_SITE_ID`** to the same GitHub environment secrets — find it at: Netlify → Site Settings → General → Site details → Site ID
- [ ] **Trigger the workflow** from the GitHub Actions UI to confirm end-to-end deployment works
