---
name: long-run
description: Use at the start of autonomous work expected to exceed roughly 1 hour equivalent (multi-component builds, migrations, large refactors, overnight runs). Sets up state files, verification cadence, and a resumption ritual for multi-context-window work.
---

# Long Run

You will outlive your context window. Externalize state so any fresh context can resume from the filesystem alone.

## Setup (before the first implementation step)

1. Create `.fablity/progress.md` — freeform log: what is done, what is next, surprises encountered. Append at every milestone.
2. Create `.fablity/state.json` — structured component status: `{"components": [{"name": "...", "status": "todo|doing|done|verified"}]}`.
3. If the project needs servers, suites, or linters: create `init.sh` that starts everything, and keep it current.
4. Commit at every green milestone. Git history is state.

## Standing rules

- Never delete or weaken a test to make progress. If a test seems wrong, record that in progress.md and report it; do not work around it.
- At each component completion (at minimum): invoke `fresh-verify` for a mid-run verification before moving on. Do not batch verification to the end.
- Update state.json in the same step as the work it describes, not in batches from memory.

## Resumption ritual (fresh context entering existing work)

1. Read `.fablity/progress.md`, `.fablity/state.json`, and `git log --oneline -20`.
2. Run one fundamental integration test (or `init.sh` plus a smoke check) BEFORE any new work — trust the filesystem, not a summary.
3. Continue from state.json, not from what "seems" done.
