#!/usr/bin/env bash
# Full experiment matrix: 3 conditions x 4 tasks x 2 reps = 24 runs, then grade all.
set -uo pipefail
ROOT="$(cd "$(dirname "$0")/.." && pwd)"

CONDITIONS=(
  "claude-fable-5 off"
  "claude-opus-4-8 off"
  "claude-opus-4-8 on"
)

for task in "$ROOT"/eval/tasks/*/; do
  for cond in "${CONDITIONS[@]}"; do
    read -r model harness <<< "$cond"
    for rep in 1 2; do
      "$ROOT/eval/run.sh" "$task" "$model" "$harness" "$rep"
    done
  done
done

for run in "$ROOT"/eval/results/*/; do
  [ -f "$run/scores.json" ] || python3 "$ROOT/eval/grade.py" "$run"
done
