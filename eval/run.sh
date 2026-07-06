#!/usr/bin/env bash
# Run one eval condition: ./run.sh <task-dir> <model-id> <off|on|on2> [rep]
# on  = harness v1: kernel via SessionStart hook (additionalContext)
# on2 = harness v2: kernel via --append-system-prompt + stop-verify Stop hook
set -euo pipefail

ROOT="$(cd "$(dirname "$0")/.." && pwd)"
TASK_DIR="$(cd "$1" && pwd)"
MODEL="$2"
HARNESS="$3"
REP="${4:-1}"

TASK_NAME="$(basename "$TASK_DIR")"
RUN_ID="${TASK_NAME}_${MODEL}_h-${HARNESS}_r${REP}"
OUT_DIR="$ROOT/eval/results/$RUN_ID"
mkdir -p "$OUT_DIR"

WORK="$(mktemp -d)"
trap 'rm -rf "$WORK"' EXIT
cp -r "$TASK_DIR/workspace/." "$WORK/"

cat > "$WORK/.gitignore" <<'GITIGNORE'
__pycache__/
*.pyc
.fability/
.claude/
GITIGNORE

case "$HARNESS" in
  off) ;;
  on|on2)
    mkdir -p "$WORK/.claude"
    cp -r "$ROOT/skills" "$WORK/.claude/skills"
    mkdir -p "$WORK/.claude/agents"
    cp "$ROOT"/agents/*.md "$WORK/.claude/agents/"
    if [ "$HARNESS" = "on" ]; then
      printf '{"hooks":{"SessionStart":[{"hooks":[{"type":"command","command":"%s/hooks/session-start.sh"}]}]}}\n' \
        "$ROOT" > "$WORK/.claude/settings.json"
    else
      printf '{"hooks":{"Stop":[{"hooks":[{"type":"command","command":"%s/hooks/stop-verify.sh"}]}]}}\n' \
        "$ROOT" > "$WORK/.claude/settings.json"
    fi
    ;;
  *) echo "harness must be off|on|on2, got: $HARNESS" >&2; exit 1 ;;
esac

EXTRA_ARGS=()
if [ "$HARNESS" = "on2" ]; then
  EXTRA_ARGS+=(--append-system-prompt "$(cat "$ROOT/kernel/kernel.md")")
fi

git -C "$WORK" init -q
git -C "$WORK" -c user.email=eval@local -c user.name=eval add -A
git -C "$WORK" -c user.email=eval@local -c user.name=eval commit -qm baseline

PROMPT="$(cat "$TASK_DIR/task.md")"

set +e
(cd "$WORK" && claude -p "$PROMPT" \
    --model "$MODEL" \
    --output-format stream-json --verbose \
    --dangerously-skip-permissions \
    --max-turns 80 "${EXTRA_ARGS[@]+"${EXTRA_ARGS[@]}"}") > "$OUT_DIR/transcript.jsonl" 2> "$OUT_DIR/stderr.log"
STATUS=$?
set -e
echo "$STATUS" > "$OUT_DIR/exit_code.txt"

git -C "$WORK" -c user.email=eval@local -c user.name=eval add -A
git -C "$WORK" diff --cached > "$OUT_DIR/workspace.diff"
git -C "$WORK" diff --cached --name-only | grep -v '^\.claude/' > "$OUT_DIR/changed_files.txt" || true
cp "$TASK_DIR/expected.md" "$OUT_DIR/expected.md"

echo "run $RUN_ID finished (exit $STATUS) -> $OUT_DIR"
