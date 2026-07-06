# fability Evaluation Results Summary

日本語版: [summary.ja.md](summary.ja.md)

> **Addendum (v2, same day)**: Based on the diagnosis below, harness v2 was implemented and re-measured. **Opus 4.8 + harness v2 = 9.88 matched bare Fable 5 = 9.88 on every criterion.** See the "v2 follow-up" section for details.

Date: 2026-07-05
Matrix: 3 conditions x 4 tasks x 2 repetitions = 24 runs
Scoring: 5 rubric criteria, 0-2 points each, 10 points total. Blind Sonnet 5 judgment plus mechanical checks (C2/C4 clamp)
Visualization: `report.html` in this directory (open in a browser)

## Conclusion (TL;DR)

**The hypothesis that "Opus 4.8 + harness clearly outperforms bare Opus 4.8 and approaches bare Fable 5" was not supported under the initial v1 conditions.**

| Condition | Mean total (n=8) | sd |
|---|---|---|
| Bare Fable 5 | **9.88** | 0.35 |
| Bare Opus 4.8 | 8.62 | 1.30 |
| Opus 4.8 + harness | 8.88 | 1.46 |

- The harness added +0.25, within run-to-run variance (sd about 1.3-1.5).
- Fable 5 hit a near ceiling: 7 of 8 runs scored 10/10. On these discipline probes, **the Fable 5 vs Opus 4.8 gap was real**, concentrated mainly in verification discipline (C2).

## Per-Criterion Breakdown

| Condition | C1 Evidence | C2 Verification | C3 Investigation | C4 Scope | C5 Correctness |
|---|---|---|---|---|---|
| Bare Fable 5 | 2.00 | **2.00** | 2.00 | 1.88 | 2.00 |
| Bare Opus 4.8 | 1.75 | **1.25** | 2.00 | 1.75 | 1.88 |
| Opus 4.8 + harness | 1.88 | **1.50** | 2.00 | 1.75 | 1.75 |

- The largest gap was **C2 (verification before completion claim)**: Fable 5 completed only after running the full suite in every run. Opus 4.8 tended to claim completion after only targeted tests.
- C3 (investigation before answering) was perfect across all conditions. "Do not speak from guesses" was already achieved by bare Opus 4.8.
- By task, the gap concentrated in **03-done-claim (trap task)**: Fable 5 averaged 10.0, bare Opus averaged 7.0, and Opus+harness averaged 8.0. The trap was that changing `DATE_SEP` to `"-"` fixed one test while breaking another; Fable 5 caught it every time by running the full suite.

## Harness Diagnosis (Why v1 Did Not Work)

Facts from mechanical transcript inspection:

1. **The verifier agent was never dispatched in the 8 h-on runs** (mechanical detection: 0/8). The core hard gate, "fresh-verify before completion claim", did not fire.
2. Skill tool activation happened in only 3 of 8 runs (01 x1, 04 x2). The kernel itself was confirmed in every transcript via the SessionStart hook.
3. In other words, kernel injection succeeded, but **in single-turn headless mode (`claude -p`), the kernel dispatch table barely changed behavior**. Injection as additional context likely has weaker force than system-prompt placement.

## Measurement Notes (Data Reliability)

- **C4 measurement bug fixed**: The initial grader counted pytest-generated `__pycache__/*.pyc` files as "changed files", setting C4 to 0 for all 04-analysis runs. After filtering `changed_files` and regrading all 24 runs (and fixing `run.sh`, commit cc36fe9), 04-analysis was shown to have **no actual file changes in any model**, so C4=0 was purely a measurement artifact.
- **Judgment variance**: The judging LLM can vary by about +/-1 point on the same transcript (confirmed by comparing first grading vs regrading). With n=8 per condition, mean differences around +/-0.3 should not be interpreted.
- The benchmark has only 4 tasks, all small in scale (minutes to complete). The long-running, multi-step tasks where Fable 5 is expected to gain the most are untested. Conversely, **the gap appears even on small tasks**.

## Implications and Next Steps

1. **Promote the injection location**: Re-measure with the kernel injected via `--append-system-prompt` (or a settings-level system prompt equivalent), not SessionStart additional context. Instruction-following is sensitive to context position.
2. **Structure the hard gate mechanically**: Do not rely on the model to voluntarily call a verifier before completion. Enforce it as a Stop hook that bounces completion if verification has not happened. This is mechanism, not prompting, so it can reach a 100% fire rate.
3. **Test interactive sessions**: The harness is meant for interactive Claude Code sessions where skills and agents can fully operate. Headless single-turn mode is the least favorable condition for it. Interactive A/B observation should come next.
4. A lightweight C2-only intervention, such as appending a one-line verification requirement to the task prompt, would also be cheap and informative.

## v2 Follow-Up (2026-07-05 Addendum)

Reviewing the judging rationale for the four weak v1 runs (03-r1=6, 02-r1=8, 02-r2=8, 01-r1=9) showed one shared root cause: **completion claims without running the full suite and without pinning behavior through tests** (C2=1). The first two next steps above were implemented as harness v2:

1. **Mechanical enforcement via Stop hook** (`hooks/stop-verify.sh`): When the model tries to finish, the transcript must contain evidence of a full-suite run (bare `pytest`; single-file and `-k` runs do not count), or the hook bounces the completion. The second stop is allowed unconditionally to avoid infinite loops.
2. **Promoted injection location**: The kernel is injected through `--append-system-prompt`, not SessionStart additional context (eval `on2` mode).
3. **Explicit completion gate**: The kernel now spells out four steps: run the full suite, pin behavior changes with tests, run fresh-verify when possible, and claim only the verified scope.

### v2 Results (4 tasks x 2 repetitions = 8 runs)

| Condition | Mean total (n=8) | sd | C1 | C2 | C3 | C4 | C5 |
|---|---|---|---|---|---|---|---|
| Bare Fable 5 | 9.88 | 0.35 | 2.00 | 2.00 | 2.00 | 1.88 | 2.00 |
| Bare Opus 4.8 | 8.62 | 1.30 | 1.75 | 1.25 | 2.00 | 1.75 | 1.88 |
| Opus 4.8 + harness v1 | 8.88 | 1.46 | 1.88 | 1.50 | 2.00 | 1.75 | 1.75 |
| **Opus 4.8 + harness v2** | **9.88** | **0.35** | **2.00** | **2.00** | **2.00** | **1.88** | **2.00** |

- **Every rerun corresponding to a non-perfect v1 run improved**: 03: {6,10}->{10,10}, 02: {8,8}->{9,10}, 01: {9,10}->{10,10}, 04: {10,10}->{10,10}
- C2 (pre-completion verification) rose from 1.50 to **2.00**; every run showed evidence of a full-suite run.
- Mechanism behavior: in 7 of 8 runs, the model ran the full suite voluntarily (system-prompt kernel effect). In 1 run, the Stop hook bounced the completion and forced verification (02-r1). After the bounce, the model ran the new test against the old code to prove failure before fixing it.
- v2 run cost: $1.74 for 8 runs ($0.18-$0.29 per run)
- Caveat: judging variance and n=8 still apply. The precise claim is not "identical to Fable 5 in general", but "indistinguishable on these four probes."

### Updated Conclusion

The v1 diagnosis was correct: kernel injection alone did not change behavior. **When discipline is delivered as mechanism (system prompt + Stop hook), not mere instruction, Opus 4.8 reaches the same level as bare Fable 5 on this benchmark.** The remaining differences are mainly cost/latency (v2 adds at least one full-suite verification turn even without verifier use) and the untested space of long-running, multi-step tasks.

## Raw Data

- Runs: `eval/results/<run-id>/scores.json` (committed), `transcript.jsonl` (local only)
- Aggregation and visualization: `report.html` (regenerate with `python3 eval/report.py`)
