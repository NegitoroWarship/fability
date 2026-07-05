---
name: grounded-report
description: Use when writing a summary or report after extended work (many tool calls, a long autonomous run, or any report that is the user's first look at the work). Produces evidence-audited, re-grounded summaries.
---

# Grounded Report

Your final message is the user's first look at the work. Write it as a re-grounding, not a continuation of your working thread.

## Evidence audit (before writing)

For each claim you intend to make, point to the tool result in this session that backs it. Three labels only:

- VERIFIED: you observed it via execution this session.
- DONE-UNVERIFIED: you did it but did not verify it; say so explicitly.
- NOT DONE: say so plainly.

Anything you cannot label is speculation — cut it or mark it as such.

## Writing rules

1. First sentence: the outcome — what happened or what you found.
2. Then the one or two things the user needs to know or decide, each explained as if new.
3. Drop the working vocabulary you built during the task: no labels you invented, no arrow chains, no abbreviations. Complete sentences, terms spelled out.
4. Failures verbatim: quote failing test output and error text; never paraphrase them into optimism.
5. If something was skipped or is unverified, it appears in the report. Omission is fabrication.
