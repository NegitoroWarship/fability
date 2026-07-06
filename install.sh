#!/usr/bin/env bash
# fability installer: install skills with npx skills add, link agents into
# ~/.claude, and print settings guidance.
set -euo pipefail

ROOT="$(cd "$(dirname "$0")" && pwd)"
AGENTS_DST="$HOME/.claude/agents"
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

cat <<EOF

Skills were installed via npx skills add into ~/.claude/skills.
Existing unrelated skills are left alone; same-named skills may be updated.

Almost done. Add the SessionStart hook by merging this fragment into
~/.claude/settings.json (this script does NOT edit it automatically):

$(cat "$ROOT/settings-fragment.json")

Then start a new Claude Code session and confirm the kernel is active
(the session context will contain "fability kernel").
EOF
