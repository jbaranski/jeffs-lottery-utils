---
name: jeff-skill-shortcut-debt
description: Collect every `shortcut:` comment in a repo into a debt ledger showing what was simplified, the limit it named, and the trigger to revisit it, and flag shortcuts with no upgrade trigger. Read-only report. Use when asked to "list the shortcuts", "show shortcut debt", "what did we defer", or to check deferred work before a release.
---

# Shortcut Debt

Deliberate shortcuts are marked `shortcut: <the limit>, <when to upgrade>` (see `jeff-skill-lean-code`). This collects them into one ledger so a deferral can't quietly become permanent.

## Scan

From the repo root, grep comment markers, skipping `.git` and everything `.gitignore` ignores:

```bash
git grep --untracked --exclude-standard -nE '(#|//|/\*|--|<!--) ?shortcut:'
```

If the user names their own marker word (e.g. `TODO`), grep for that instead. Skip hits that are not a deferral, such as a note about a keyboard shortcut.

## Output

One row per marker, grouped by file:

`<file>:<line> — <what was simplified>. Limit: <the limit named>. Upgrade: <the trigger to revisit>.`

Tag any marker that names no upgrade path or trigger `no-trigger`: those are the ones that silently rot. Add an owner with `git blame -L<line>,<line> <file>` only if the user asks.

End with `<N> markers, <M> with no trigger.` Nothing found: `No shortcut debt.`

Report only; change nothing. Write the ledger to a file (e.g. `SHORTCUT-DEBT.md`) only if the user asks.
