# AGENTS.md — Pedigree Tracker

## Commands

- Backend tests: `./scripts/run_tests.sh` (isolated temp SQLite DB)
- E2E tests: `npm install && npx playwright install chromium`, then `./scripts/run_e2e_tests.sh` (app starts on port 8001 with a temp DB)
- Run the app locally: `venv/bin/python -m src.app` → http://localhost:8000 (`PORT` env overrides)
- Docker: `./scripts/docker_start.sh` to build/start, `./scripts/docker_stop.sh` to stop. The container serves http://localhost:8000.
- Lint/format/typecheck: `./scripts/lint.sh` (runs black + flake8 + mypy). Config in `setup.cfg` (flake8 max-line-length=88 to match black; mypy stub overrides). Manual: `venv/bin/python -m black src`, `venv/bin/python -m flake8 src`, `venv/bin/python -m mypy src`

## Architecture

- Single app factory: `src/app/__init__.py::create_app()`. `src/app/__main__.py` only calls it.
- API blueprint at `API_PREFIX` (`/api/v1`), `strict_slashes=False` — endpoints work with or without a trailing slash.
- Sessions: handlers use `database.get_session()`; teardown calls `SessionLocal.remove()`. Never use `next(get_db())` in request handlers.
- Validation lives in `src/app/api/validation.py`; raise `ValidationError(message, errors={field: msg})`.

## API error contract

- Validation errors → HTTP 400 `{"message": str, "errors": {field: str}}`
- 404 / 409 → `{"message": str}`
- 500 → `{"message": "Internal server error"}` (details logged server-side only — never return SQL or exception text)

## Important data rules

- `identifier` unique **per animal type** (composite unique constraint). No migration: existing databases keep the old schema; fresh DBs get per-type uniqueness.
- Strict parent validation: mother=female, father=male, same `type_id`, DOB chronology, no self/cycles. `null` on `mother_id`/`father_id` in PUT clears the parent.
- Do not delete or migrate `data/pedigree.db` without explicit approval.

## Frontend notes

- Vanilla JS in `www/js/`. `Utils.parseISODate`/`formatDate` are timezone-free — never pass `YYYY-MM-DD` strings to `new Date()`.
- All user-controlled strings rendered into HTML must go through `Utils.escapeHTML` (stored-XSS fix).
- Modal a11y goes through `Utils.showModal`/`hideModals` (focus trap, Escape, focus return).
