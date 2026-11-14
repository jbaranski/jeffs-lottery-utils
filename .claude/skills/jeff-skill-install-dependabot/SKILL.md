---
name: jeff-skill-install-dependabot
description: Install and configure Dependabot for automated dependency updates in the project, with grouped PRs, capped intervals, and CI guards so Dependabot doesn't burn Actions minutes. Use when setting up a new repository, adding dependency management, or asked to "install dependabot" or "set up automated updates".
---

## Steps

1. Read `.github/dependabot.yml` if it exists; extend it rather than replacing it.
2. Find every manifest in the repo (root and all subdirectories, excluding `node_modules`, `.venv`, `vendor`): `package.json` → `npm`, `go.mod` → `gomod`, `pyproject.toml` with `uv.lock` → `uv`, `Dockerfile` → `docker`, and so on. Check the [options reference](https://docs.github.com/en/code-security/reference/supply-chain-security/dependabot-options-reference) for the ecosystem name of anything else.
3. Add one entry per manifest directory, plus one `github-actions` entry for `/`.
4. Add the Dependabot guard to every CI job (below).
5. Tell the user, per entry, why you chose its `directory`, `groups` and `interval`.

## Rules for every entry

- **`groups:` is mandatory.** `patterns: ['*']` puts all of the entry's updates in one PR (split by prefix or update type only if the project needs smaller review batches). Without it, Dependabot opens one PR per dependency — the main source of PR floods and wasted Actions minutes.
- **`interval` is `weekly` at most** — never `daily`. Use `monthly` for low-churn directories (one-off scripts, archived tooling). If you can't tell a directory's churn, ask.
- **`open-pull-requests-limit: 5`**, set explicitly.
- **`cooldown: default-days: 7`**, set explicitly. Dependabot waits that many days after a release before proposing it, so
  a compromised or broken release is usually caught and pulled before it reaches you. Without the key it waits 3 days.
  Cooldown never delays security updates.
- Directories that share an ecosystem and an interval may share one entry with `directories: ['/api', '/worker']`
  (globs allowed) instead of `directory:`; keep separate entries when the interval differs.

```yaml
version: 2
updates:
  - package-ecosystem: 'github-actions'
    directory: '/'
    schedule:
      interval: 'weekly'
    open-pull-requests-limit: 5
    cooldown:
      default-days: 7
    groups:
      github-actions:
        patterns: ['*']

  - package-ecosystem: 'npm'
    directory: '/client'
    schedule:
      interval: 'weekly'
    open-pull-requests-limit: 5
    cooldown:
      default-days: 7
    groups:
      client-npm:
        patterns: ['*']

  - package-ecosystem: 'npm'
    directory: '/scripts/backfill' # rarely touched
    schedule:
      interval: 'monthly'
    open-pull-requests-limit: 5
    cooldown:
      default-days: 7
    groups:
      backfill-npm:
        patterns: ['*']
```

## Pin every action to a commit SHA

A tag like `@v7` can be moved to point at different code; a commit SHA can't. Every `uses:` in every workflow is
`owner/repo@<full commit sha> # <exact tag>`:

```yaml
- uses: actions/checkout@3d3c42e5aac5ba805825da76410c181273ba90b1 # v7.0.1
```

Get the commit for a tag (works for annotated and lightweight tags):

```bash
git ls-remote https://github.com/actions/checkout 'refs/tags/v7.0.1^{}' refs/tags/v7.0.1 | tail -1 | cut -f1
```

The `github-actions` entry above keeps the SHA and its tag comment up to date. Never pin to a short SHA.

## Guard every CI job

Dependabot's own update checks are free, but every PR or push it creates re-triggers the repo's workflows, which consume Actions minutes. Add a guard to **every job** in every workflow a Dependabot PR or push can trigger — not just build/test jobs:

- Workflows with a `pull_request` trigger (alone or with others):

  ```yaml
  if: github.actor != 'dependabot[bot]' && github.event.pull_request.user.login != 'dependabot[bot]'
  ```

- Push-only workflows:

  ```yaml
  if: github.actor != 'dependabot[bot]'
  ```

If a job already has an `if:`, combine with `&&` and wrap the existing condition in parentheses: `if: (existing-condition) && github.actor != 'dependabot[bot]' && ...`.

Flag any workflow triggered by Dependabot PRs that runs on larger or self-hosted runners — that compute is billed at the regular rate.

## References

- [dependabot.yml options](https://docs.github.com/en/code-security/reference/supply-chain-security/dependabot-options-reference)
- [Actions billing](https://docs.github.com/en/billing/managing-billing-for-github-actions/about-billing-for-github-actions)
