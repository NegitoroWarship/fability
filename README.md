# fable-harness

A Claude Code harness that closes the discipline gap between Claude Opus 4.8 and Claude Fable 5 — by mechanism, not by prompt.

日本語版: [README.ja.md](README.ja.md)

## Results

Discipline benchmark: 4 tasks × 5-criterion rubric × 8 runs per condition, scored by a blind Sonnet 5 judge plus mechanical checks.

| Condition | Mean total (/10) | sd |
|---|---|---|
| Fable 5 (bare) | 9.88 | 0.35 |
| Opus 4.8 (bare) | 8.62 | 1.30 |
| Opus 4.8 + harness v1 (prompt injection only) | 8.88 | 1.46 |
| **Opus 4.8 + harness v2** | **9.88** | **0.35** |

On this benchmark, Opus 4.8 + harness v2 scores identical to bare Fable 5 — down to the per-criterion means. Full aggregation and charts: [`eval/results/summary.md`](eval/results/summary.md) (Japanese) and `eval/results/report.html` (open in a browser).

The v1→v2 delta is the project's central finding: **discipline must be delivered as mechanism, not instruction.**

- v1 injected the kernel as session context (SessionStart hook). The verification hard gate almost never fired; scores stayed near bare Opus 4.8.
- v2 (a) injects the kernel into the system prompt, and (b) adds a Stop hook that mechanically bounces any completion claim lacking evidence of a full-test-suite run. Verification discipline (C2) went from 1.25 to 2.00.

## Principle

Fable 5's prompting guide is effectively a catalog of behaviors Fable 5 exhibits naturally. Opus 4.8 follows instructions literally and faithfully. So: convert the Fable 5 behavior catalog into explicit protocols, and use Opus 4.8's instruction-following — backed by hook-level enforcement where instruction alone fails — as the delivery mechanism.

## Layout

- `kernel/kernel.md` — 6 standing disciplines + skill dispatch table + completion gate (v2: injected into the system prompt)
- `hooks/stop-verify.sh` — Stop hook; bounces completion claims that lack a full-suite test run (the core of v2)
- `hooks/session-start.sh` — SessionStart hook (v1-style kernel injection)
- `skills/` — 6 protocol skills (deep-insight, spec-first, fresh-verify, long-run, session-memory, grounded-report)
- `agents/` — verifier (fresh-context adversarial verifier) / investigator (parallel hypothesis tester)
- `eval/` — measurement pipeline (run tasks × models × harness conditions, score against the 5-criterion rubric)

## Install

1. Run `./install.sh` (symlinks into ~/.claude/skills and ~/.claude/agents)
2. Merge the printed settings fragment into ~/.claude/settings.json
3. Start a new Claude Code session

## Running the evaluation

```
./eval/run.sh <task-dir> <model> <off|on|on2> <rep>   # one condition
python3 eval/grade.py <run-dir>                        # score (mechanical checks + blind LLM judge)
python3 eval/report.py                                 # regenerate aggregation + charts (report.html)
./eval/matrix.sh                                       # full matrix
```

`off` = no harness / `on` = v1 (SessionStart injection) / `on2` = v2 (system prompt + Stop hook)

## Documents

- Design spec: `docs/specs/2026-07-05-fable-harness-design.md` (Japanese)
- Implementation plan: `docs/plans/2026-07-05-fable-harness.md` (Japanese)
- Experiment results & diagnosis: `eval/results/summary.md` (Japanese)
