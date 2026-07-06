---
name: fresh-verify
description: HARD GATE before any completion claim ("done", "fixed", "works", "complete"). Dispatches a fresh-context verifier subagent with only the mini-spec and deliverable paths. A fresh context does not share your blind spots; self-review does.
---

# Fresh Verify

Self-critique shares your assumptions; a fresh context does not. The verifier must not inherit them.

## Protocol

1. Assemble the input contract: the mini-spec from `.fability/minispec.md` (if none exists, write one now — success criteria, files touched, verification method) plus deliverable paths. Nothing else. Do NOT include your implementation approach, your reasoning, or a summary of the conversation — that contaminates the fresh context.
2. Dispatch the `verifier` agent with exactly that contract.
3. On FAIL or significant findings: fix, then re-dispatch with the same contract. Repeat until PASS.
4. In your completion report, cite the verifier's EVIDENCE section. A completion claim without verifier evidence is a protocol violation.
5. If the verifier cannot be dispatched (agent unavailable, subagent limits), report "NOT VERIFIED" prominently instead of claiming completion. Silently skipping verification and claiming completion is the single worst failure mode of this harness.
