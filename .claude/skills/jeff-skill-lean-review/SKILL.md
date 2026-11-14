---
name: jeff-skill-lean-review
description: Review and audit method — read the connected code, not just the diff; rank problems correct > safe > holds under load > tested > fast > lean; require a concrete failure case for every finding; report numbered Must fix / Should fix / Nice to have findings in plain English, each with what it is, the problem, the fix, and what happens if skipped. Use when reviewing a diff, commit, branch or PR, auditing a whole repo, or asked "is this over-engineered", "find bloat", or "what can I delete".
---

# Lean Review

Review like the senior developer who gets paged when it breaks. Order of importance: correct, safe, holds under load, tested, fast, lean. Lean still matters: every extra line must be read, tested and fixed later.

## 1. Understand first

**A change** (the default):

- Review what the user names: uncommitted or staged changes, a branch, a PR, or files. Nothing named: the uncommitted changes, or the last commit if there are none.
- Read the diff, then the code it touches: callers of every changed function, the functions it calls, the tests, the README.
- A change can break code it does not touch. When a signature, return value or behavior changes, grep every caller.

**A whole repo** (when asked to audit):

- Read the README, build and deploy config, dependency list, entry points (main, routes, handlers, jobs, CLI commands) and tests.
- Trace the main flows end to end and read those paths fully: user input, money, auth, data writes, background jobs, state shared between processes.
- Big repo: go deep where a mistake costs the most, not file by file. Say which parts you did not read.

**Both:** find the expected load (README, deploy config): one person running a script, or many users and processes at once. Judge scale against that and say which load you assumed.

## 2. Look for

1. **Bug:** wrong result, crash, missed edge case (empty, zero, last item, rounding, time zones), a caller broken by the change, a fix applied in one caller while the shared function stays broken, the same rule applied differently in two places.
2. **Risk:** security holes (injection, weak randomness, secrets, unchecked user input), data loss (swallowed errors, writes in the wrong order, no transaction).
3. **Scale:** fine for one user, wrong for many: check-then-write races, the same work done by every process, memory or lists that only grow, a query per item, O(n²) on big input, per-process state that must be shared.
4. **Missing test:** risky logic (a branch, a parser, money, security, data writes, a bug fix) with no test that fails when it breaks. One good test, not coverage — unless the project sets a coverage threshold.
5. **Speed:** big slowdowns are problems; small wins (work repeated in a hot loop) are suggestions.
6. **Lean:** code that should not exist or should be smaller.
   - delete: dead code, unused options, flags and config, speculative features
   - reuse: the repo already has this helper (name the path)
   - stdlib / native: the standard library or platform already does it; a new dependency for a few lines
   - yagni: interface with one implementation, factory with one product, wrapper that only passes calls through, config nobody sets
   - merge: near-copies that must change together
   - split: one function doing unrelated jobs. Split by job, never by line count, and never into helpers that exist only to shorten a function.

## 3. Check before you report

- Every finding needs a concrete case: "this input or situation leads to this wrong result". No case, no finding.
- Re-read the lines and confirm: the caller exists, the value can really be empty. Before calling code unused, grep the whole tree, including tests, fixtures, config, and string or dynamic references.
- A `shortcut:` comment that names its limit is a decision, not a finding, unless the expected load already crosses that limit.
- Propose the smallest fix that works. Prefer fixes that delete code. Never add layers, frameworks or config the problem does not need.
- Project standards from the reviewer agent or stack skill are findings even when they are conventions. Personal style taste, "consider…" and vague worries are not.

## 4. Output

Very simple English: short sentences, everyday words. Explain a technical term the first time you use it. The reader may never have seen this code.

Start with `What this change does:` (or `What this repo does:` plus the load you assumed) in two or three sentences.

Then the findings, most important first, skipping empty groups:

- **Must fix:** bug, security, data loss, breaks at the expected load.
- **Should fix:** risky code without a test, real slowness, duplication, a function that mixes jobs, code that should not exist.
- **Nice to have:** small speed-ups, shorter forms.

Number findings across all groups so the user can say "fix 2 and 5". A repo audit lists at most 20; say how many smaller ones you left out. Every finding has all four parts, each one or two short sentences:

```
2. **Orders land on the wrong day** (`billing/close_day.py:40-52`)
   - **What this is:** At midnight this job closes the day and bills all orders of that day.
   - **Problem:** It takes "today" from the server clock, which runs in UTC. An order placed
     at 00:30 in Berlin is billed on the day before.
   - **Fix:** Compute the day once in the shop's time zone:
     `datetime.now(ZoneInfo("Europe/Berlin")).date()`. One line, nothing else changes.
   - **If we skip it:** Late orders show the wrong date, and accounting fixes them by hand.
```

End with:

- `Verdict: Ship.` or `Verdict: fix 1 and 3 first.`
- `Lean: -<N> lines possible.` (audit: `-<N> lines, -<M> dependencies possible.`) when lean findings exist.
- `Not checked:` one line, if something mattered and you could not check or run it.

Nothing found: the opening line, then `Looks good. Ship.` (audit: `Healthy. Nothing to fix.`) and one line on what you checked.

Report only; change no code unless the user asks you to fix specific findings.
