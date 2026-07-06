#!/usr/bin/env bash
# Stop hook: mechanically enforce the completion hard gate.
# Blocks the first stop attempt unless the transcript shows a full-suite
# pytest run. Always allows the second attempt (stop_hook_active) to
# prevent loops. Reads the hook JSON on stdin, emits a block decision on
# stdout when verification evidence is missing.
HOOK_JSON="$(cat)"
export HOOK_JSON
python3 - <<'PY'
import json
import os
import re
import sys

try:
    data = json.loads(os.environ["HOOK_JSON"])
except (KeyError, json.JSONDecodeError):
    sys.exit(0)  # malformed hook input: never trap the session
if data.get("stop_hook_active"):
    sys.exit(0)

# A full-suite run is `pytest` (or `python -m pytest`) NOT narrowed to a
# single test file or ::test id. `pytest tests/` counts; `pytest tests/x.py`
# and `pytest -k foo` do not.
PYTEST = re.compile(r"(^|[;&|]\s*)(python3?\s+-m\s+)?pytest\b(?P<args>[^;&|]*)")


def full_suite(cmd):
    for m in PYTEST.finditer(cmd):
        args = m.group("args")
        if "::" in args or ".py" in args or re.search(r"(^|\s)-k\s", args):
            continue
        return True
    return False


verified = False
try:
    with open(data["transcript_path"]) as fh:
        for line in fh:
            try:
                ev = json.loads(line)
            except json.JSONDecodeError:
                continue
            msg = ev.get("message") or {}
            content = msg.get("content")
            if not isinstance(content, list):
                continue
            for block in content:
                if (
                    isinstance(block, dict)
                    and block.get("type") == "tool_use"
                    and block.get("name") == "Bash"
                    and full_suite(block.get("input", {}).get("command", ""))
                ):
                    verified = True
except (OSError, KeyError):
    sys.exit(0)  # cannot read transcript: never trap the session

if verified:
    sys.exit(0)

print(json.dumps({
    "decision": "block",
    "reason": (
        "HARD GATE (fability): no full-test-suite run found in this "
        "session. Before finishing: (1) run the COMPLETE test suite from the "
        "workspace root (bare `pytest` — every test file; a single-file or "
        "-k run does not count); (2) if you changed any source behavior, add "
        "or update a test that locks the change in, then re-run the full "
        "suite; (3) re-check every claim in your final message against "
        "actual tool output — if the task was analysis-only, do not modify "
        "files, just verify your claims are evidence-backed. Then finish, "
        "reporting the verification evidence."
    ),
}))
PY
