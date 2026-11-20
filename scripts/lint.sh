#!/bin/bash
# Lint and type-check: black (format), flake8, mypy.
# Config lives in setup.cfg (flake8 + mypy); black uses defaults (88 cols).
# Usage: ./scripts/lint.sh

SCRIPT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
PROJECT_ROOT="$(dirname "$SCRIPT_DIR")"
cd "$PROJECT_ROOT"

PY="$PROJECT_ROOT/venv/bin/python"
status=0

run_tool() {
    local name="$1"
    shift
    echo
    echo "======== $name ========"
    if "$@"; then
        echo "[PASS] $name"
    else
        echo "[FAIL] $name"
        status=1
    fi
}

run_tool "black (format)" "$PY" -m black src
run_tool "flake8 (lint)" "$PY" -m flake8 src
run_tool "mypy (typecheck)" "$PY" -m mypy src

echo
echo "======================================"
if [ "$status" -eq 0 ]; then
    echo "All checks passed."
else
    echo "One or more checks failed (see [FAIL] above)."
fi
exit "$status"
