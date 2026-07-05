#!/usr/bin/env bash
# fable-harness installer: symlink skills/agents into ~/.claude and print settings guidance.
set -euo pipefail

ROOT="$(cd "$(dirname "$0")" && pwd)"
SKILLS_DST="$HOME/.claude/skills"
AGENTS_DST="$HOME/.claude/agents"

mkdir -p "$SKILLS_DST" "$AGENTS_DST"

for d in "$ROOT"/skills/*/; do
  name="$(basename "$d")"
  ln -sfn "${d%/}" "$SKILLS_DST/$name"
  echo "linked skill:  $SKILLS_DST/$name"
done

for f in "$ROOT"/agents/*.md; do
  name="$(basename "$f")"
  ln -sfn "$f" "$AGENTS_DST/$name"
  echo "linked agent:  $AGENTS_DST/$name"
done

cat <<EOF

Almost done. Add the SessionStart hook by merging this fragment into
~/.claude/settings.json (this script does NOT edit it automatically):

$(cat "$ROOT/settings-fragment.json")

Then start a new Claude Code session and confirm the kernel is active
(the session context will contain "fable-harness kernel").
EOF
