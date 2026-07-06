#!/usr/bin/env bash
# Compatibility wrapper. The supported install path is npx skills add.
set -euo pipefail

ROOT="$(cd "$(dirname "$0")" && pwd)"
SKILLS_CLI_PACKAGE="${SKILLS_CLI_PACKAGE:-skills@latest}"

if ! command -v npx >/dev/null 2>&1; then
  echo "error: npx is required. Please install Node.js/npm first." >&2
  exit 1
fi

echo "Installing fability for Claude Code with npx skills add..."
npx --yes "$SKILLS_CLI_PACKAGE" add "$ROOT" \
  --global \
  --agent claude-code \
  --skill fability \
  --yes

cat <<EOF

Fability was installed into ~/.claude/skills as a Claude Code skills-directory plugin.
Existing unrelated skills were left alone; an existing fability install may be updated.

Start a new Claude Code session, or run /reload-plugins in an existing session.
The plugin provides the protocol skills, verifier/investigator agents, and
SessionStart/Stop hooks without editing ~/.claude/settings.json.
EOF
