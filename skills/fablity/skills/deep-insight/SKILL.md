---
name: deep-insight
description: Use for bug investigation, root-cause analysis, code review, design assessment, or any "why does X happen" question. Hypothesis-driven protocol with falsification and confidence tracking; prevents anchoring on the first plausible explanation.
---

# Deep Insight

The first plausible explanation is usually shallow. This protocol forces depth.

## Stage 1 — Fix the observations
List the observed facts with evidence (tool output, file:line). Label anything not directly observed as ASSUMPTION. Do not proceed while claims and observations are mixed.

## Stage 2 — Competing hypotheses
Generate at least 3 distinct hypotheses that explain the observations. Give each a prior confidence (low/medium/high). If you cannot produce 3, you have not understood the system yet — read more code first.

## Stage 3 — Falsify, cheapest first
For each hypothesis, design the cheapest test that could DISPROVE it, and run it. Prefer disconfirming evidence: a hypothesis you tried and failed to kill is worth more than one you only fed. Update confidences after each test. When hypotheses are independent and tests don't share state, dispatch `investigator` subagents in parallel, one hypothesis each.

## Stage 4 — Converge with residual risk
State the surviving hypothesis and its evidence chain. Then ask once: "If this conclusion is wrong, what is the most likely reason?" — and check that reason if it is cheap to check. Report the conclusion, the evidence, and the residual risk.

## For review-type tasks (code review, design assessment)
Two passes, always:
1. **Coverage pass**: report every issue found, including uncertain and low-severity ones, each with confidence and severity. Do not filter here — it is better to surface a finding that later gets cut than to silently drop a real bug.
2. **Filter pass**: rank and cut against an explicit bar: keep anything that could cause incorrect behavior, a test failure, or a misleading result; omit pure style and naming preferences.
Never merge the passes; filtering during discovery silently drops real findings.
