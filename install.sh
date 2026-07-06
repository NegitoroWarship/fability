#!/usr/bin/env bash
# fability installer: install skills, link agents, and enable the kernel +
# verification gate in Claude Code settings.
set -euo pipefail

ROOT="$(cd "$(dirname "$0")" && pwd)"
AGENTS_DST="$HOME/.claude/agents"
SETTINGS_DST="$HOME/.claude/settings.json"
SKILLS_CLI_PACKAGE="${SKILLS_CLI_PACKAGE:-skills@latest}"

if ! command -v npx >/dev/null 2>&1; then
  echo "error: npx is required to install skills. Please install Node.js/npm first." >&2
  exit 1
fi

echo "Installing Claude Code skills with npx skills add..."
npx --yes "$SKILLS_CLI_PACKAGE" add "$ROOT" \
  --global \
  --agent claude-code \
  --skill '*' \
  --full-depth \
  --yes

mkdir -p "$AGENTS_DST"

for f in "$ROOT"/agents/*.md; do
  name="$(basename "$f")"
  ln -sfn "$f" "$AGENTS_DST/$name"
  echo "linked agent:  $AGENTS_DST/$name"
done

python3 - "$SETTINGS_DST" "$ROOT/hooks/session-start.sh" "$ROOT/hooks/stop-verify.sh" <<'PY'
import json
import os
import shutil
import sys
import time

settings_path, session_hook, stop_hook = sys.argv[1:]


def load_settings(path):
    if not os.path.exists(path):
        return {}
    with open(path, "r", encoding="utf-8") as fh:
        return json.load(fh)


def is_fability_hook(command, hook_name):
    return (
        isinstance(command, str)
        and command.endswith(f"/hooks/{hook_name}")
        and ("fability" in command or "fable" "-harness" in command)
    )


def remove_stale_fability_hooks(settings, event, hook_name, current_command):
    hooks_by_event = settings.setdefault("hooks", {})
    entries = hooks_by_event.setdefault(event, [])
    cleaned = []
    changed = False
    for entry in entries:
        entry_hooks = entry.get("hooks")
        if not isinstance(entry_hooks, list):
            cleaned.append(entry)
            continue
        kept_hooks = [
            hook for hook in entry_hooks
            if not (
                isinstance(hook, dict)
                and hook.get("type") == "command"
                and hook.get("command") != current_command
                and is_fability_hook(hook.get("command"), hook_name)
            )
        ]
        if len(kept_hooks) != len(entry_hooks):
            changed = True
        if kept_hooks:
            new_entry = dict(entry)
            new_entry["hooks"] = kept_hooks
            cleaned.append(new_entry)
    hooks_by_event[event] = cleaned
    return changed


def append_hook(settings, event, command):
    hooks_by_event = settings.setdefault("hooks", {})
    entries = hooks_by_event.setdefault(event, [])
    for entry in entries:
        for hook in entry.get("hooks", []):
            if isinstance(hook, dict) and hook.get("type") == "command" and hook.get("command") == command:
                return False
    entries.append({"hooks": [{"type": "command", "command": command}]})
    return True


try:
    settings = load_settings(settings_path)
except json.JSONDecodeError as exc:
    print(f"error: could not parse {settings_path}: {exc}", file=sys.stderr)
    print("settings were not changed; fix the JSON and re-run ./install.sh", file=sys.stderr)
    sys.exit(1)

if not isinstance(settings, dict):
    print(f"error: {settings_path} must contain a JSON object", file=sys.stderr)
    sys.exit(1)

changed = False
changed |= remove_stale_fability_hooks(settings, "SessionStart", "session-start.sh", session_hook)
changed |= remove_stale_fability_hooks(settings, "Stop", "stop-verify.sh", stop_hook)
changed |= append_hook(settings, "SessionStart", session_hook)
changed |= append_hook(settings, "Stop", stop_hook)

if changed:
    os.makedirs(os.path.dirname(settings_path), exist_ok=True)
    if os.path.exists(settings_path):
        backup = f"{settings_path}.bak.{time.strftime('%Y%m%d%H%M%S')}"
        shutil.copy2(settings_path, backup)
        print(f"backed up settings: {backup}")
    tmp_path = f"{settings_path}.tmp"
    with open(tmp_path, "w", encoding="utf-8") as fh:
        json.dump(settings, fh, indent=2, ensure_ascii=False)
        fh.write("\n")
    os.replace(tmp_path, settings_path)
    print(f"updated settings: {settings_path}")
else:
    print(f"settings already configured: {settings_path}")
PY

cat <<EOF

Skills were installed via npx skills add into ~/.claude/skills.
Existing unrelated skills are left alone; same-named skills may be updated.

Fability is enabled in ~/.claude/settings.json:
- SessionStart hook injects the fability kernel at session start.
- Stop hook blocks completion claims until full-suite verification evidence exists.

Start a new Claude Code session and confirm the kernel is active
(the session context will contain "fability kernel").
EOF
