---
name: jeff-skill-dependabot-issue-resolution
description: Resolve all open Dependabot PRs by consolidating updates into a single feature branch, with ecosystem-specific ordering rules (Angular first via ng update, Tailwind major upgrades via the official tool), bisecting failures, and commenting on skipped PRs. Use when asked to "resolve dependabot PRs", "batch dependabot updates", or "consolidate dependabot issues".
---

Consolidate every open Dependabot PR into one feature branch, keep the largest set of updates that still builds and passes tests, and explain every update you skip.

## 1. Scope

```bash
gh pr list --author app/dependabot --state open --json number,title,headRefName,url
```

- Only **open** PRs (and their linked issues) authored by Dependabot are in scope. Ignore everything else.
- **If there are none, report "No open Dependabot PRs found — nothing to do." and stop.** Don't look for other work.

## 2. Branch

Reuse an existing `chore/dependabot-batch-*` branch if there is one; otherwise create `chore/dependabot-batch-<YYYY-MM-DD>` off `main`. Never commit to `main` directly.

A repo can contain several independent sub-projects (e.g. an Angular frontend and a Go backend). Each ecosystem is its own track with no ordering between tracks; the ordering rules below apply only within a track.

## 3. Apply updates per track

### Angular sub-project

1. **Update Angular first**, before any other npm dependency in that sub-project: follow https://angular.dev/update-guide for the path from the current version and run `ng update @angular/core @angular/cli` as it directs.
2. Apply the npm updates Angular's new peer dependencies require (TypeScript, test tooling, builder packages). Confirm `ng build` and the full test suite pass.
3. Then apply the remaining standalone npm updates.
4. For every bumped package, run `npm ls <package>` after installing. Two different versions of the same package in the tree (top level plus one nested under another package) is a conflict — treat that bump as a failure (step 4). Never force a version past a peer-dependency conflict.

### Tailwind CSS (if present)

1. Check https://tailwindcss.com/docs for the latest stable release; if Dependabot's target is behind it, bump to the latest. Keep `@tailwindcss/postcss` / `@tailwindcss/vite` in step.
2. Across a major version, run `npx @tailwindcss/upgrade` and follow https://tailwindcss.com/docs/upgrade-guide instead of hand-editing config.
3. Build and run the full test suite.

### Other ecosystems (Go, Python, GitHub Actions, ...)

Apply the bumps from the relevant PRs (`go get <mod>@<ver> && go mod tidy`, `uv lock --upgrade-package <pkg>`, editing workflow `uses:` tags), then run that sub-project's full checks.

## 4. On failure: isolate, exclude, comment

If a build or test fails, or an update can't be applied cleanly:

1. Find the specific update responsible (revert bumps one at a time).
2. Revert just that update.
3. Comment on its Dependabot PR (and linked issue, if any) with the failing check or version conflict, the exact error, and that it was excluded from this batch for follow-up. Leave that PR open.
4. Re-run the checks and continue until everything passes with the largest possible set of updates.

## 5. Finalize

1. Open the consolidated PR. Its body is the record of the run — for each sub-project:
   - every update applied
   - every update skipped, with the reason
   - for Angular and Tailwind, what you did for each step above
2. Once its checks pass, merge it into `main`.
3. Close the Dependabot PRs (and linked issues) for every update that was applied. Leave the excluded ones open.
