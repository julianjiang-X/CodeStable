#!/usr/bin/env bash
set -euo pipefail

ROOT="${CODEX_PROJECT_DIR:-${CLAUDE_PROJECT_DIR:-$(git rev-parse --show-toplevel 2>/dev/null || pwd)}}"
SCRIPT="$ROOT/.codestable/tools/validate-implementation-review.py"

# Since package 3.0.0 tools are not copied into projects; fall back to the copy
# that ships next to this script.
if [[ ! -f "$SCRIPT" ]]; then
  SCRIPT="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)/validate-implementation-review.py"
fi

if [[ ! -f "$SCRIPT" ]]; then
  exit 0
fi

python3 "$SCRIPT" --root "$ROOT"
