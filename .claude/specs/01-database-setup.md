# Plan: 01 — Database Setup

## Context
`database/db.py` is a comment-only stub, and `app.py` has no DB wiring. Spec: `.claude/specs/01_databse_setup.md` (note the filename typo; the dir is `specs`, not `spec`). This step builds the SQLite data layer that auth, profile and expenses will use. No new routes, no new packages.

## Files to change
- `database/db.py` — implement everything (all DB logic lives here only).
- `app.py` — import and call startup helpers; placeholder routes untouched.
- `tests/test_db.py` — new tests (optional but recommended; `tests/test_app.py` has the `app` fixture pattern).

## `database/db.py`
- Constants: `DB_PATH` = `<project root>/expense_tracker.db` (via `os.path` relative to this file; already gitignored per CLAUDE.md), and `CATEGORIES = ["Food","Transport","Bills","Health","Entertainment","Shopping","Other"]`.
- `get_db()`: `sqlite3.connect(DB_PATH)`, `row_factory = sqlite3.Row`, `PRAGMA foreign_keys = ON`, return conn.
- `init_db()`: open conn, `executescript` with two `CREATE TABLE IF NOT EXISTS` statements:
  - `users(id INTEGER PRIMARY KEY AUTOINCREMENT, name TEXT NOT NULL, email TEXT NOT NULL UNIQUE, password_hash TEXT NOT NULL, created_at TEXT DEFAULT (datetime('now')))`
  - `expenses(id INTEGER PRIMARY KEY AUTOINCREMENT, user_id INTEGER NOT NULL REFERENCES users(id), amount REAL NOT NULL, category TEXT NOT NULL, date TEXT NOT NULL, description TEXT, created_at TEXT DEFAULT (datetime('now')))`
  - Commit and close (use `with closing(...)`/try-finally).
- `seed_db()`: `SELECT COUNT(*) FROM users`; return early if > 0. Else insert demo user (`Demo User`, `demo@spendly.com`, `generate_password_hash("demo123")`), grab `cursor.lastrowid`, then `executemany` 8 parametrized expense rows. Dates built from `date.today().replace(day=n)` formatted `%Y-%m-%d`, using days ≤ 28 so every month is valid. 8 rows covering all 7 categories (one category repeated, e.g. Food twice). All `?` placeholders; no f-strings in SQL.

## `app.py`
- Add `from database.db import get_db, init_db, seed_db` (`get_db` imported per spec even though unused until later steps).
- After `app = Flask(__name__)`:
  ```python
  with app.app_context():
      init_db()
      seed_db()
  ```
- Leave placeholder routes as-is (CLAUDE.md: don't implement them yet).

## Decisions / notes
- Spec allows `spendly.db` or `expense_tracker.db`; choose `expense_tracker.db` to match CLAUDE.md.
- Functions take no Flask context, so the `app_context()` wrapper is just per spec; harmless.
- Running at import time means tests importing `app` will create/seed the real DB file; tests for db.py should monkeypatch `DB_PATH` to a `tmp_path` file.
- Errors: let `sqlite3.IntegrityError` propagate (duplicate email, bad FK) — no swallowing.

## Verification
1. `make test` — existing page tests still pass.
2. New `tests/test_db.py` (tmp DB via monkeypatch): tables exist; `init_db()` twice is fine; `seed_db()` twice gives 1 user and 8 expenses; all 7 categories present; password hash verifies with `check_password_hash`; duplicate email raises `IntegrityError`; expense with nonexistent `user_id` raises `IntegrityError`; `get_db()` rows support `row["name"]` and `PRAGMA foreign_keys` returns 1.
3. `make run` (port 5001) starts cleanly; `expense_tracker.db` is created; `sqlite3 expense_tracker.db "select count(*) from expenses"` → 8; restart and confirm still 8.
