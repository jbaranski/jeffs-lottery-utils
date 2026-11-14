---
name: jeff-skill-lean-code
description: Smallest-complete-change rules for writing code — a reuse-first ladder (skip it, reuse the codebase, stdlib or platform, an installed dependency, one line, then the minimum that works), a never-cut list (trust-boundary validation, data-loss handling, security, accessibility), one test for risky logic, and `shortcut:` comments for deliberate limits. Use on any coding task (writing, fixing, refactoring, choosing dependencies) and when the user says "be lazy", "simplest solution", "yagni", or complains about over-engineering or bloat.
---

# Lean Code

Solve the whole problem with the least new code. Be lazy about the solution, never about reading the code or finishing the change.

Stack standards win. When the agent or a project skill sets a rule (a coverage threshold, JSDoc on exports, a logging library, a test framework), follow it even where it adds code this skill would skip.

## Before you write

Read the task and the code it touches. List every place the change must reach: callers, tests, fixtures, config, exports. Check what it could break for users: data it would destroy or expose, callers that stop working. That is scope. Extra features are not.

## Take the first option that fully works

1. **Does it need to exist?** Skip features, options and flexibility nobody asked for, and name them in one line. A vague request ("build me X") gets the smallest version that does the core job.
2. **Already in this codebase?** A helper, component, service or pattern: use it the way the surrounding code does.
3. **Standard library or platform feature?** Use it, unless the project has its own. A house component beats a native widget.
4. **An installed dependency?** Use it. Never add a dependency for a few lines.
5. **One line a reader gets at a glance?** Write the one line.
6. **Otherwise:** the minimum code that works.

## Rules

- Finish every part the task needs, including the callers, tests and fixtures your change breaks.
- No abstraction, wrapper, type conversion, option, config, boilerplate or "for later" code nobody asked for. Keep values in the form the platform already gives you. Deletion beats addition.
- Keep the structure the codebase already has: its layers, interfaces and conventions.
- The shortest working diff wins, once you know everything it must touch. A one-liner that needs decoding is not short.
- Between options of equal size, take the one that is correct on edge cases.
- Comments say only the why the code cannot show, in one line.
- Bug fix: grep every caller of the function before editing, then fix the root cause once in the shared code.
- Code you move or merge keeps its error handling and validation.
- New non-trivial logic (a branch, a loop, a parser, money, security, or a whole new script) leaves at least one test that fails when it breaks. Trivial changes need none.
- A deliberate shortcut with a known limit gets a comment naming the limit and when to upgrade:
  `// shortcut: in-memory cache, per-process only; move to Redis when we run more than one instance`

**Never cut:** validation at trust boundaries, error handling that prevents data loss, security, accessibility, calibration real hardware needs, anything the user asked for.

## Reply

End with one or two lines: what you skipped or did not check, and any risk the user must know.
