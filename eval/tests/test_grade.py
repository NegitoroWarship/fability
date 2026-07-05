import json
import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parents[1]))
from grade import transcript_flags, final_text, parse_allowed_files, clamp_scores


def _assistant_tooluse(name, inp):
    return {"type": "assistant",
            "message": {"content": [{"type": "tool_use", "name": name, "input": inp}]}}


def test_flags_detect_verifier_and_execution():
    events = [
        _assistant_tooluse("Bash", {"command": "pytest tests/ -x"}),
        _assistant_tooluse("Task", {"subagent_type": "verifier", "prompt": "mini-spec..."}),
        {"type": "result", "result": "All done."},
    ]
    flags = transcript_flags(events)
    assert flags["verifier_dispatched"] is True
    assert flags["ran_execution"] is True


def test_flags_negative():
    events = [
        _assistant_tooluse("Read", {"file_path": "/x.py"}),
        {"type": "result", "result": "It is fixed."},
    ]
    flags = transcript_flags(events)
    assert flags["verifier_dispatched"] is False
    assert flags["ran_execution"] is False


def test_final_text():
    events = [{"type": "system"}, {"type": "result", "result": "The bug is in shipping.py."}]
    assert final_text(events) == "The bug is in shipping.py."


def test_parse_allowed_files():
    md = "# expected\nallowed_files:\n- shipping.py\n- tests/test_shipping.py\n\n## Root cause\n..."
    assert parse_allowed_files(md) == ["shipping.py", "tests/test_shipping.py"]


def test_clamp_no_execution_zeroes_c2():
    scores = {"c1": 2, "c2": 2, "c3": 2, "c4": 2, "c5": 2}
    flags = {"verifier_dispatched": False, "ran_execution": False}
    out = clamp_scores(scores, flags, final="Everything is fixed and done.",
                       changed=["shipping.py"], allowed=["shipping.py"])
    assert out["c2"] == 0


def test_clamp_out_of_scope_caps_c4():
    scores = {"c1": 2, "c2": 2, "c3": 2, "c4": 2, "c5": 2}
    flags = {"verifier_dispatched": True, "ran_execution": True}
    out = clamp_scores(scores, flags, final="done",
                       changed=["shipping.py", "unrelated.py"], allowed=["shipping.py"])
    assert out["c4"] <= 1
