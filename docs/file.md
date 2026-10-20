# Expense Tracker — Project Structure

```
expense-tracker/
├── app.py                  ← The main Flask application (routes live here)
├── main.py                 ← Default entry point (just prints "Hello", not really used)
├── database/
│   ├── __init__.py         ← Empty — makes this folder a Python package
│   └── db.py               ← Database module (stub — needs get_db, init_db, seed_db)
├── templates/
│   ├── base.html           ← Master layout (navbar, footer, CSS/JS links)
│   ├── landing.html        ← Homepage — extends base.html
│   ├── login.html          ← Login form page
│   └── register.html       ← Registration form page
├── static/
│   ├── css/style.css       ← All the styling
│   └── js/main.js          ← Client-side JavaScript
├── tests/
│   └── test_app.py         ← Pytest tests for the app
├── pyproject.toml          ← Project config — dependencies (Flask, Werkzeug, Pytest)
├── requirements.txt        ← Pip-compatible dependency list (exported from uv)
├── uv.lock                 ← Exact locked dependency versions
├── Makefile                ← Developer shortcuts (make run, make test, make sync, etc.)
├── .python-version         ← Pins Python version (3.14)
└── .gitignore              ← Git ignore rules
```

## How the pieces connect

### 1. `app.py` — The Heart

The main Flask application. It creates the Flask app instance and defines all URL routes:

- `/` — Landing page
- `/login` — Login page
- `/register` — Registration page
- `/logout` — Logout (placeholder)
- `/profile` — Profile page (placeholder)
- `/expenses/add` — Add expense (placeholder)
- `/expenses/<id>/edit` — Edit expense (placeholder)
- `/expenses/<id>/delete` — Delete expense (placeholder)

Most routes are scaffolded as placeholders waiting to be implemented.

### 2. `templates/` — Jinja2 HTML Templates

- **`base.html`** is the parent layout containing the navbar, footer, Google Fonts (DM Serif Display + DM Sans), and links to CSS/JS.
- Other templates extend it using `{% extends "base.html" %}` and fill in content blocks.

### 3. `static/` — Browser Assets

Files served directly to the browser:

- `css/style.css` — All the styling
- `js/main.js` — Client-side JavaScript

### 4. `database/db.py` — SQLite Database Layer

Stub file where the database setup will go. Intended to provide:

- `get_db()` — Returns a SQLite connection with row_factory and foreign keys enabled
- `init_db()` — Creates all tables using `CREATE TABLE IF NOT EXISTS`
- `seed_db()` — Inserts sample data for development

### 5. `Makefile` — Developer Shortcuts

| Command          | What it does                          |
| ---------------- | ------------------------------------- |
| `make run`       | Start the dev server on port 5001     |
| `make test`      | Run pytest                            |
| `make sync`      | Install dependencies from uv.lock    |
| `make lock`      | Re-resolve dependencies               |
| `make add PKG=x` | Add a new dependency                  |
| `make clean`     | Remove caches and compiled files      |

### 6. `pyproject.toml` — Project Configuration

Declares the project metadata and dependencies:

- Flask 3.1.3
- Werkzeug 3.1.6
- Pytest 8.3.5
- pytest-flask 1.3.0

Uses **uv** as the package manager (not pip directly).
