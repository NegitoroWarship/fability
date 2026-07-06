---
name: spec-first
description: Use before starting any implementation task with 3 or more steps. Produces a mini-spec (success criteria, files to touch, out-of-scope, verification method) that later feeds fresh-verify. Well-specified tasks are executed dramatically better — specify your own task before executing it.
---

# Spec First

Write the mini-spec BEFORE touching code. It takes two minutes and doubles as the verifier's contract.

## Mini-spec format

Write to `.fability/minispec.md` (create the directory if needed; overwrite per task):

- **Goal**: one sentence.
- **Success criteria**: numbered; each one mechanically checkable (a command plus its expected observation).
- **Files to touch**: exact paths.
- **Out of scope**: what you will NOT change.
- **Verification method**: the exact commands that will prove each criterion.

## Rules

1. If the request allows two readings, pick one and state it in the Goal line — or ask the user, if the readings diverge materially.
2. Success criteria must be executable checks, not adjectives. "Works correctly" is not a criterion; "`pytest tests/ -x` exits 0" is.
3. Write the mini-spec for a reader with zero conversation context: it is the exact input later passed to the fresh-verify verifier.
4. When you believe you are done — before invoking fresh-verify — re-read the mini-spec. If scope legitimately changed, update it and note why.
