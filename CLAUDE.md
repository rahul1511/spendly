# CLAUDE.md

This file provides guidance to Claude Code (claude.ai/code) when working with code in this repository.

## Project

"Spendly" — a light-weighted personal expense tracker built withg Python 3.14, and framework flask, managed with `uv` and SQLite Database.

### File structure (Architecture)

```
expense-tracker/
├── app.py                 # Flask app + all routes (entry point: flask --app app)
├── main.py                # unused `uv init` stub
├── database/
│   ├── __init__.py
│   └── db.py              # stub: get_db(), init_db(), seed_db(), the SQLLite Healper
├── templates/
│   ├── base.html          # layout: navbar, footer, title/head/content blocks
│   ├── landing.html       # "/"         landing page (hero, video modal)
│   ├── register.html      # "/register" sign-up form
│   ├── login.html         # "/login"    sign-in form
│   ├── terms.html         # "/terms"    terms and conditions
│   └── privacy.html       # "/privacy"  privacy policy
├── static/
│   ├── css/style.css      # single stylesheet for the whole site
│   └── js/main.js         # essentially empty
├── tests/
│   └── test_app.py        # pytest-flask; `app` fixture sets TESTING
├── Makefile               # run/stop/sync/test/add/requirements (see `make help`)
├── pyproject.toml         # dependencies (managed by uv)
├── uv.lock                # locked dependency versions
├── requirements.txt       # generated from uv.lock via `make requirements`
├── .python-version        # Python version pin
├── docs/, prompts/        # gitignored local notes
└── expense_tracker.db     # gitignored SQLite DB (created by init_db)
```

**Where things belongs:**
- New routes -> `app.py` only, no blueprints
- DB logic -> `database/db.py` only, never inline in routes
- New Pages -> new `.html` file , extent `base.html`
- Page-Specific style -> new `.css` file not inline `<style>` tags

---
## Code style

- Python: PEP-8, snake_case for all variable and functions
- Templates: Jinja2 with `url_for()` for every internal link - never hardcode URLs
- Route function : Single responsibility ONy - fetch dtaa, render
- Coading Principal : Use `SOLID` Principle
- DB Queries: always use parametrized queries (`?` placeholder) - never f-string in SQL
- Comment and logging : with `f-string` Only where the dynamic content 
- Error handling : Use `abort()` for HTP errors, not bare `return `error

---
## Tech Constraints

- **Flask only** - No FastAPI, No Django no other webframework
- **SQLite only** - no postgresSQL, no SQLAlchemy ORM, no external DB
- **Vanilla JS only** - no React, noJquery, no npm packages
- **No new pip packadges** - work within `requirments.txt` as-is unless explicitily told otherwise


## Commands

All via `make` (see `make help`):

- `make sync` — install deps from `uv.lock` into `.venv`
- `make run` — dev server with debug on port 5001 (`PORT=...` to override); `make stop` kills it
- `make test` — pytest; pass options with `ARGS`, e.g. `make test ARGS="-k test_page_loads -x"`
- `make add PKG=<name>` / `make add-dev PKG=<name>` — add dependencies (updates `pyproject.toml` and `uv.lock`)
- `make requirements` — regenerate `requirements.txt` from `uv.lock` (keep it in sync after dependency changes)

There is no linter configured.


### Request flow

```
Browser
   │  HTTP
   ▼
app.py (Flask routes) ──render_template──▶ templates/*.html ──extends──▶ base.html
   │                                              │
   │ (planned) get_db()                           └─ links ▶ static/css/style.css, static/js/main.js
   ▼
database/db.py ──▶ SQLite (expense_tracker.db, gitignored, not created yet)
```



### Routes

| Route | Status | Template / note |
|---|---|---|
| `/` | Implemented | `landing.html` |
| `/register` | done (form + POST, Step 2) | `register.html` |
| `/login` | done (page only) | `login.html`; POST handling in Step 3 |
| `/terms`, `/privacy` | done | `terms.html`, `privacy.html` |
| `/logout` | placeholder | Step 3 |
| `/profile` | placeholder | Step 4 |
| `/expenses/add` | placeholder | Step 7 |
| `/expenses/<id>/edit` | placeholder | Step 8 |
| `/expenses/<id>/delete` | placeholder | Step 9 |

**Do not implement a placeholder route unless the active task explicitly targets that step.**

---

## Tests

`tests/test_app.py` uses `pytest-flask`; it defines an `app` fixture (sets `TESTING`) so the `client` fixture works. Add new fixtures there.

---

## Notes

- `docs/` and `prompts/` are gitignored local notes (project structure writeup and the prompt history used to build pages); `README.md` is empty.
- Recent commits are prefixed `landing:` for landing-page work.

---

## Warning and things to avoid
- **Never use raw string returns placeholder routes** Once a step is implemenmted - always render a template
- **Never hardcoode URLs** in template - always use `url_for()`
- **Never put DB logic in route functions** - it belongs in `database/db.py`
- **Never install new packages** mid-feature without flagging, keep uv and requirments.txt in sync
- **Never use JS frameworks** - the forntend is intentionaly vanilla
- **`database/db.py` is implemented and db created , do not crreate new DB until specifically asked** 
- **FK enforcement is manual** SQLite forign keys are off by-default; `get_db()` must run `PRAGMA foreign_keys = ON` on every connection
- The app runs on **port 5001**, don't change this