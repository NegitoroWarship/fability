#!/usr/bin/env bash
# SessionStart hook: print the fablity kernel so Claude Code injects it as context.
KERNEL="$(dirname "$(readlink -f "$0")")/../kernel/kernel.md"
[ -f "$KERNEL" ] && cat "$KERNEL"
exit 0
