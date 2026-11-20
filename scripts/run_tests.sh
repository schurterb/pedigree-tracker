#!/bin/bash
# Run the pytest suite against an isolated temporary database.
# Usage: ./scripts/run_tests.sh [pytest args]
set -e

SCRIPT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
PROJECT_ROOT="$(dirname "$SCRIPT_DIR")"
cd "$PROJECT_ROOT"

TMP_DIR="$(mktemp -d /tmp/pedigree-tests.XXXXXX)"
trap 'rm -rf "$TMP_DIR"' EXIT

export PYTHONPATH="$PROJECT_ROOT/src${PYTHONPATH:+:$PYTHONPATH}"
export DATABASE_URL="sqlite:///$TMP_DIR/test.db"
export LOG_FILE="$TMP_DIR/app.log"
export PYTHONDONTWRITEBYTECODE=1
export TESTING=1

"$PROJECT_ROOT/venv/bin/python" -m pytest src/tests "$@"
