---
name: session-memory
description: Use when the user corrects you, when a confirmed approach works after difficulty, or when you discover a non-obvious project fact worth keeping. One lesson per file; lessons are recalled at task start in future sessions.
---

# Session Memory

## Store

Write to `.fability/lessons/<kebab-slug>.md` (create the directory if needed):

    # <one-line summary>
    **What**: the fact or correction.
    **Why it mattered**: the consequence observed.
    **How to apply**: the behavioral rule going forward.

## Rules

- One lesson per file. Update an existing file rather than duplicating; delete lessons proven wrong.
- Don't store what the repo, git history, or CLAUDE.md already records. Store the non-obvious residue: corrections, confirmed approaches, traps.

## Recall

At the start of a task in a repo that has `.fability/lessons/`, list the files and read their first lines (the summaries); read fully only the relevant ones.
