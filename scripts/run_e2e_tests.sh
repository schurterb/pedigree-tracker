#!/usr/bin/env bash
# Run the Playwright e2e suite against an isolated app instance (port 8001).
set -euo pipefail

cd "$(dirname "$0")/.."

E2E_DIR="$(mktemp -d /tmp/pedigree-e2e-XXXXXX)"
trap 'rm -rf "$E2E_DIR"' EXIT
export E2E_DIR

npx playwright test --config tests/e2e/playwright.config.js "$@"
