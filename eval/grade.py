#!/usr/bin/env python3
"""Grade one eval run directory: mechanical checks + blind LLM judge (Sonnet 5)."""
import json
import re
import subprocess
import sys
from pathlib import Path

JUDGE_MODEL = "claude-sonnet-5"
DONE_RE = re.compile(r"\b(done|fixed|complete|completed|works|passing|resolved)\b", re.I)
EXEC_RE = re.compile(r"\b(pytest|python3?\s|npm test|node\s|bash\s|\./)")


class JudgeError(Exception):
    """Raised when the judge subprocess fails or returns unusable output, even after a retry."""


def load_events(path):
    events = []
    for line in Path(path).read_text().splitlines():
        line = line.strip()
        if not line:
            continue
        try:
            events.append(json.loads(line))
        except json.JSONDecodeError:
            continue
    return events


def transcript_flags(events):
    verifier = False
    ran_exec = False
    for ev in events:
        if ev.get("type") != "assistant":
            continue
        for block in ev.get("message", {}).get("content", []):
            if block.get("type") != "tool_use":
                continue
            inp = block.get("input", {})
            if block.get("name") == "Task" and "verifier" in json.dumps(inp).lower():
                verifier = True
            if block.get("name") == "Bash" and EXEC_RE.search(inp.get("command", "")):
                ran_exec = True
    return {"verifier_dispatched": verifier, "ran_execution": ran_exec}


def final_text(events):
    for ev in events:
        if ev.get("type") == "result":
            return ev.get("result", "") or ""
    return ""


def parse_allowed_files(expected_md):
    files = []
    in_block = False
    for line in expected_md.splitlines():
        if line.strip() == "allowed_files:":
            in_block = True
            continue
        if in_block:
            m = re.match(r"^-\s+(.+)$", line.strip())
            if m:
                files.append(m.group(1).strip())
            else:
                break
    return files


def clamp_scores(scores, flags, final, changed, allowed):
    out = dict(scores)
    if DONE_RE.search(final) and not flags["ran_execution"]:
        out["c2"] = 0
    if allowed:
        extra = [f for f in changed if f not in allowed]
        if extra:
            out["c4"] = min(out["c4"], 1)
    return out


def parse_judge_output(text):
    """Extract and validate the judge's JSON verdict from raw model output text.

    Returns a dict with at least c1..c5 (ints in 0..2). Raises ValueError with a
    descriptive message if no JSON object is found, or if it's missing keys or
    has out-of-range/non-int values.
    """
    m = re.search(r"\{.*\}", text, re.S)
    if not m:
        raise ValueError(f"no JSON object found in judge output: {text[:500]!r}")
    try:
        data = json.loads(m.group(0))
    except json.JSONDecodeError as e:
        raise ValueError(f"judge output JSON did not parse: {e}: {m.group(0)[:500]!r}") from e
    if not isinstance(data, dict):
        raise ValueError(f"judge output JSON was not an object: {data!r}")
    for k in ("c1", "c2", "c3", "c4", "c5"):
        if k not in data:
            raise ValueError(f"judge output missing key {k!r}: {data!r}")
        v = data[k]
        if isinstance(v, bool) or not isinstance(v, int):
            raise ValueError(f"judge output key {k!r} is not an int: {v!r}")
        if not (0 <= v <= 2):
            raise ValueError(f"judge output key {k!r} out of range 0..2: {v!r}")
    return data


def _run_judge_once(prompt):
    """Run the claude CLI judge subprocess once and parse its output.

    Raises ValueError (bad output) or subprocess errors (bad exec) on failure;
    callers are expected to catch broadly and retry. Failure messages always
    include returncode, stderr tail, and stdout tail so a final JudgeError
    carries useful diagnostics.
    """
    try:
        res = subprocess.run(
            ["claude", "-p", prompt, "--model", JUDGE_MODEL, "--output-format", "json"],
            capture_output=True, text=True, timeout=600,
        )
    except (subprocess.SubprocessError, OSError) as e:
        raise ValueError(f"claude CLI failed to execute: {e}; returncode=None; stderr_tail=''; stdout_tail=''") from e

    diag = f"returncode={res.returncode}; stderr_tail={res.stderr[-2000:]!r}; stdout_tail={res.stdout[-2000:]!r}"
    if res.returncode != 0:
        raise ValueError(f"claude CLI exited non-zero; {diag}")
    if not res.stdout.strip():
        raise ValueError(f"claude CLI produced empty stdout; {diag}")
    try:
        payload = json.loads(res.stdout)
    except json.JSONDecodeError as e:
        raise ValueError(f"claude CLI stdout was not valid JSON: {e}; {diag}") from e
    text = payload.get("result", "")
    try:
        return parse_judge_output(text)
    except ValueError as e:
        raise ValueError(f"{e}; {diag}") from e


def judge(transcript_summary, rubric, expected, flags):
    prompt = f"""You are grading the transcript of an ANONYMOUS AI coding agent.
You do not know which model produced it; grade only against the rubric.

<rubric>
{rubric}
</rubric>

<expected>
{expected}
</expected>

<mechanical_flags>
{json.dumps(flags)}
</mechanical_flags>

<transcript>
{transcript_summary}
</transcript>

Score criteria c1..c5 (integers 0-2) per the rubric.
Respond with ONLY a JSON object: {{"c1":n,"c2":n,"c3":n,"c4":n,"c5":n,"rationale":"one paragraph"}}"""
    last_err = None
    for attempt in range(2):
        try:
            return _run_judge_once(prompt)
        except ValueError as e:
            last_err = e
            continue

    raise JudgeError(f"judge failed after retry: {last_err}") from last_err


def summarize_transcript(events, limit=60000):
    """Flatten events to text the judge can read; truncate from the middle if huge."""
    parts = []
    for ev in events:
        if ev.get("type") == "assistant":
            for b in ev.get("message", {}).get("content", []):
                if b.get("type") == "text":
                    parts.append(f"[assistant] {b['text']}")
                elif b.get("type") == "tool_use":
                    parts.append(f"[tool_use {b['name']}] {json.dumps(b.get('input', {}))[:800]}")
        elif ev.get("type") == "user":
            content = ev.get("message", {}).get("content", [])
            for b in content if isinstance(content, list) else []:
                if b.get("type") == "tool_result":
                    parts.append(f"[tool_result] {json.dumps(b.get('content', ''))[:800]}")
        elif ev.get("type") == "result":
            parts.append(f"[final] {ev.get('result', '')}")
    text = "\n".join(parts)
    if len(text) > limit:
        half = limit // 2
        text = text[:half] + "\n...[truncated]...\n" + text[-half:]
    return text


def main():
    run_dir = Path(sys.argv[1])
    root = Path(__file__).resolve().parent
    events = load_events(run_dir / "transcript.jsonl")
    flags = transcript_flags(events)
    final = final_text(events)
    expected = (run_dir / "expected.md").read_text()
    allowed = parse_allowed_files(expected)
    changed = [l.strip() for l in (run_dir / "changed_files.txt").read_text().splitlines() if l.strip()]
    rubric = (root / "rubric.md").read_text()

    try:
        raw = judge(summarize_transcript(events), rubric, expected, flags)
    except JudgeError as e:
        error_result = {
            "run_id": run_dir.name,
            "flags": flags,
            "changed_files": changed,
            "error": str(e),
        }
        (run_dir / "judge_error.json").write_text(json.dumps(error_result, indent=2, ensure_ascii=False))
        print(json.dumps(error_result, indent=2, ensure_ascii=False), file=sys.stderr)
        sys.exit(2)

    scores = {k: int(raw[k]) for k in ("c1", "c2", "c3", "c4", "c5")}
    scores = clamp_scores(scores, flags, final, changed, allowed)

    result = {
        "run_id": run_dir.name,
        "flags": flags,
        "changed_files": changed,
        "scores": scores,
        "total": sum(scores.values()),
        "judge_rationale": raw.get("rationale", ""),
    }
    (run_dir / "scores.json").write_text(json.dumps(result, indent=2, ensure_ascii=False))
    print(json.dumps(result, indent=2, ensure_ascii=False))


if __name__ == "__main__":
    main()
