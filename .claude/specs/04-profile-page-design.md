# Spec: Profile Page Design

## Overview

Replace the "Your profile page is coming soon" placeholder at `/profile` with a real, read-only account page for the signed-in user. The page shows the user's name, email and member-since date in a card that matches Spendly's existing design system, and offers one primary "Add expense" action. `/profile` is where login (Step 3) and registration redirect a signed-in user, and CLAUDE.md lists it as the Step 4 placeholder. Today it renders `profile.html` with only a greeting, and its guard checks only that `session["user_id"]` is set. A session pointing at a deleted user therefore reaches the template with `current_user = None` and fails on `current_user["name"]`. This step gives users a proper landing spot after sign-in and closes that gap, without adding expense data views (those belong to later steps).

## Depends on

- Step 1: Database Setup (`users` table with `name`, `email`, `created_at`; `get_db()` in `database/db.py`)
- Step 2: Registration (users created with `created_at` defaulted by SQLite)
- Step 3: Login (`session["user_id"]`, `get_user_by_id()`, `is_signed_in()`, `current_user` context processor, navbar Logout)

## Open Questions

Resolved with the user before writing this spec:

1. Content: **account info plus an all-time expense overview** (revised after the first build; originally "account info only"). The overview has summary stats (total spent, number of expenses, top category), a per-category breakdown with bars, and the 10 most recent expenses, all read-only.
2. Period: **all time**.
3. Actions: **one "Add expense" button** linking to `url_for('add_expense')`. No edit/delete controls. Until Step 7 lands, the button leads to the existing placeholder text; this is accepted.
4. Editing: **read-only**. No name or password changes in this step.

Still unconfirmed (out of scope unless requested):

5. `users.created_at` is stored by SQLite `datetime('now')`, which is UTC text (`YYYY-MM-DD HH:MM:SS`). The page shows only the date part, so a user registering near midnight may see a date off by one in their local time zone. No time-zone handling is planned.
6. The footer in `base.html` hardcodes `/terms` and `/privacy`, which breaks the `url_for()` rule. It isn't caused by this step and is left unchanged, because `base.html` is shared.

## Routes

- `GET /profile`: existing route, now implemented. **Logged-in only.**
  - Signed out, or a session holding a `user_id` that no longer exists: 302 redirect to `login` (`url_for("login")`). A stale `user_id` is removed from the session so the visitor isn't treated as signed in.
  - Signed in: fetches the user with the existing `get_user_by_id()`, plus the overview via the new `db.py` helpers (summary, category totals, recent expenses), and renders `profile.html`. Returns 200. Only the signed-in user's own expenses are ever queried.
  - Inputs: none (no query parameters, no form).
  - No other methods: `POST /profile` keeps returning 405 (Flask default for a GET-only route).

No other route changes. `/expenses/add`, `/expenses/<id>/edit` and `/expenses/<id>/delete` remain placeholders and must not be implemented here.

## Database Changes

No schema changes. `users` and `expenses` already have every column needed, and `get_user_by_id(user_id)` already exists.

New read-only helpers in `database/db.py`, all filtered by `user_id` with `?` placeholders and `with closing(get_db())`:
- `get_expense_summary(user_id)` returns `{"total": float, "count": int, "top_category": str | None}`.
- `get_category_totals(user_id)` returns rows of `category, total, count`, ordered by total descending.
- `get_recent_expenses(user_id, limit=10)` returns rows of `id, amount, category, date, description`, ordered by `date DESC, id DESC`.

## Template

- Create: none (`templates/profile.html` already exists).
- Modify:
  - `templates/profile.html`: replace the placeholder content and keep `{% extends "base.html" %}`.
    - `{% block title %}`: "Profile — Spendly" (unchanged).
    - `{% block head %}`: link `static/css/profile.css` via `url_for('static', filename='css/profile.css')`.
    - Page header: `h1` in the display font, "Your profile", with a muted subtitle such as "Your Spendly account details."
    - Account card (`section`, card styling from the design system):
      - An avatar circle with the user's initial (first character of `name`, uppercased), on `--accent-light` with `--accent` text, marked `aria-hidden="true"`.
      - A `<dl>` with three rows: **Name**, **Email**, **Member since** (formatted like `12 Nov 2026`; shows "—" if `created_at` is missing or unparseable).
      - A primary "Add expense" link styled with the existing `.btn-primary` class, `href="{{ url_for('add_expense') }}"`.
    - All user values output with normal `{{ }}` autoescaping. Never use `|safe`.
  - `templates/base.html`: **no change**. The navbar already shows Logout for signed-in users, and `tests/test_login.py::test_profile_shows_logout_when_signed_in` relies on it.
    - Overview (below the account card):
      - Three stat tiles: Total spent (`₹1,23,456.00`, Indian grouping via an `inr` filter), Expenses (count), Top category.
      - Spending by category: one row per category with an icon tile, the name, an amount and a proportional bar (an inline SVG `rect` with a percentage width, so there are no `style=` attributes). Colours come from new `--cat-*` variables.
      - Recent expenses: the 10 latest, each with the category icon, description (or the category name if it's empty), date (`format_date`) and amount (tabular figures).
- UI states:
  - Signed in with expenses: the account card plus the overview.
  - Signed in with no expenses: the account card plus an empty state ("No expenses yet") that points to the existing Add expense button. There's no second primary button.
  - Signed out or stale session: no page is rendered, only a redirect to the sign-in page. No flash message is needed.
  - Long names or emails (up to the 100- and 254-character limits used at registration) wrap inside the card (`overflow-wrap: anywhere`) and never cause horizontal scroll at 360px.
  - No forms, so no validation messages.

## File to create

- `static/css/profile.css`: page-specific styles (CLAUDE.md: page-specific style goes in a new `.css` file, not inline `<style>`). This covers the page container, card, avatar, definition-list rows and responsive tweaks at the existing `900px` and `600px` breakpoints. Use only the `:root` variables from `style.css`.
- `templates/macros/icons.html`: inline Lucide SVG icon macro (`plus` plus the seven category icons).
- `tests/test_profile.py`: pytest tests for the page. Use the same temporary-database `app` fixture pattern as `tests/test_login.py` (monkeypatch `database.db.DB_PATH` to a `tmp_path` file, `init_db()`, `seed_db()`) so the real `expense_tracker.db` is never touched.

## File to changes

- `app.py`
  - `profile()`: guard with the existing signed-in check (fetch the user via `get_user_by_id`; if `None`, drop `user_id` from the session and redirect to `login`), then `render_template("profile.html", user=user)`. No SQL in the route.
  - Add one small Jinja filter (for example `format_date`), registered with `@app.template_filter`. It turns a `YYYY-MM-DD[ HH:MM:SS]` string into `12 Nov 2026` using the standard library `datetime`, and returns "—" on `None` or bad input. This keeps date formatting out of the template and reusable in later expense pages.
- `templates/profile.html`: as described under Template.
- `database/db.py`: the three read-only overview helpers.
- `app.py`: also an `inr` Jinja filter (Indian digit grouping, standard library only).
- `static/css/style.css`: add the `--cat-*` category colour variables to `:root` (shared, so later expense pages reuse them).
- `CLAUDE.md`: update the Routes table row for `/profile` from "placeholder" to "done (account page, Step 4)".

## New Dependency

No new dependencies. Date formatting uses Python's standard `datetime`.

## Rules for implementations

- Do not use SQLAlchemy or another ORM.
- Use parameterized SQL queries (`?`); never build queries by interpolating user input. (This step should add no new SQL; reuse `get_user_by_id`.)
- No password handling in this step. Never render or pass `password_hash` to the template; the template may only read `name`, `email` and `created_at`.
- Use existing CSS variables; do not hardcode color hex values. Reuse `.btn-primary`; don't invent a new button style.
- Extend the project's `base.html` template; use `url_for()` for every link, stylesheet and redirect.
- Page-specific CSS goes in `static/css/profile.css`, linked from `{% block head %}`. No inline `<style>` or `style=""`.
- All DB logic stays in `database/db.py`; the route only fetches the user and renders or redirects (CLAUDE.md single-responsibility rule).
- Apply SOLID principles where useful without adding unnecessary complexity. The date formatter is a single-purpose filter, not a utility module.
- Do not implement `/expenses/add`, `/expenses/<id>/edit` or `/expenses/<id>/delete`; only link to `add_expense`.
- Do not change the existing tests' expectations: `/profile` redirects to `/login` when signed out and shows the navbar Logout form when signed in.
- No JavaScript is needed for this page; add none.
- No new packages; the app stays on port 5001.

## Definition of Done

- [ ] `GET /profile` while signed out returns 302 with `Location` ending in `/login`.
- [ ] `GET /profile` with a session `user_id` that doesn't exist in `users` returns 302 to `/login` (not a 500), and afterwards the session has no `user_id`.
- [ ] After signing in as `demo@spendly.com` / `demo123`, `GET /profile` returns 200 and the body contains "Demo User", "demo@spendly.com" and a "Member since" date in `DD Mon YYYY` format.
- [ ] A user registered via `/register` sees their own name and email on `/profile`, not the demo user's.
- [ ] The response body never contains the user's `password_hash`.
- [ ] A user whose name is `<script>alert(1)</script>` sees it rendered escaped (`&lt;script&gt;`).
- [ ] The page contains an "Add expense" link whose `href` is `/expenses/add`, generated via `url_for`.
- [ ] The page contains no edit, delete, or account-edit forms.
- [ ] For the seeded demo user, Total spent shows `₹400.64` and Expenses shows `8`; the category breakdown lists every category they've spent in; the recent list shows at most 10 rows, newest first.
- [ ] A user with no expenses sees the "No expenses yet" empty state and no stats.
- [ ] One user's expenses never appear on another user's profile.
- [ ] `inr` formats `123456.5` as `₹1,23,456.50`, `0` as `₹0.00`, and `999` as `₹999.00`.
- [ ] The placeholder text "Your profile page is coming soon." no longer appears.
- [ ] The page links `static/css/profile.css`; `profile.html` has no inline `<style>` and no `style=` attributes; `profile.css` contains no hex colors.
- [ ] `format_date` returns `12 Nov 2026` for `2026-11-12 08:30:00` and for `2026-11-12`, and "—" for `None` and for `"not-a-date"`.
- [ ] `POST /profile` returns 405.
- [ ] Existing tests `test_profile_shows_logout_when_signed_in` and `test_profile_redirects_to_login_when_signed_out` in `tests/test_login.py` still pass.
- [ ] Tests never modify the real `expense_tracker.db`.
- [ ] `make test` passes, including `tests/test_profile.py` (to be confirmed by actually running it during implementation).
- [ ] With `make run` (port 5001), the page looks consistent with the login and register pages at 360px, 600px, 900px and 1200px widths, with no horizontal scroll for a 100-character name or a 254-character email.
- [ ] CLAUDE.md's Routes table marks `/profile` as done for Step 4.
