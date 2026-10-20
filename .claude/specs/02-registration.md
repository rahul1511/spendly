# Spec: Registration

## Overview

Make the existing `/register` page functional so a visitor can create a Spendly account. Today `register()` in `app.py` only renders `register.html`, and the form has no handler. This step accepts the submitted name, email and password, validates them, stores the user with a hashed password in the `users` table created in Step 1, and sends the visitor to the sign-in page. It is the first write path in the app and gives Step 3 (Login and Logout) real users to authenticate.

## Depends on

- Step 1: Database Setup (`users` table, `get_db()`, `init_db()` in `database/db.py`)

## Open Questions

1. **After successful registration, where does the user go?** Proposed: redirect to `/login` with a one-time success message. Alternative: log the user in immediately. This spec assumes the redirect, because no session or login exists yet (login and logout appear to belong to Step 3; CLAUDE.md only confirms `/logout` is Step 3). Confirm before implementing- works for now
2. **Success message on `/login`.** Showing it needs a small additive change to `login.html` (a flash block) and an `app.secret_key`. Confirm this is acceptable, or drop the message and redirect silently. - acceptable
3. **Password rules.** Only "Min. 8 characters" is confirmed in the `register.html` placeholder. No maximum length, complexity rule or confirm-password field is specified anywhere in the repo. This spec uses minimum 8 characters only.- Keep the max 16 characters (resolved: password must be 8-16 characters)
4. **Secret key source.** No `SECRET_KEY` exists in the repo. Proposed: read it from the `SECRET_KEY` environment variable with a dev-only fallback. Confirm. - skip for now (resolved: `SECRET_KEY` env var with dev-only fallback, needed by `flash`)


## Routes

- `GET /register` - existing route; renders the sign-up form. Public.
- `POST /register` - new method on the same route. Public.
  - Inputs: form fields `name`, `email`, `password`, `confirm_password`.
  - Success: user row created, redirect (302) back to `/register`, which shows the success card.
  - Failure (validation error or duplicate email): HTTP 200, `register.html` re-rendered with the `error` message and the submitted `name` and `email` pre-filled. The password is never echoed back.

No other route changes. `/login`, `/logout` and the other placeholder routes stay as they are.

## Database Changes

No database changes. `users` in `database/db.py` already has `id`, `name`, `email` (`NOT NULL UNIQUE`), `password_hash` and `created_at`.

New helper functions are added to `database/db.py` (no schema change):

- `create_user(name, email, password)` - hashes the password with `generate_password_hash`, inserts with a parameterized query, returns the new `id`. `sqlite3.IntegrityError` on a duplicate email is allowed to propagate to the caller.
- `get_user_by_email(email)` - returns the matching `sqlite3.Row` or `None`. Not used by the registration route itself; it is added now for Step 3 and for the tests.

Both follow the existing pattern: `with closing(get_db()) as conn`, `?` placeholders, explicit `commit()` on writes.

## Template

- Create: none.
- Modify:
  - `templates/register.html`
    - Change the hardcoded `action="/register"` to `action="{{ url_for('register') }}"`.
    - Pre-fill `name` and `email` with `value="{{ name }}"` and `value="{{ email }}"` after an error (Jinja autoescaping stays on). The password field is never pre-filled.
    - Keep the existing `.auth-error` block as the single place for error text.
  - `templates/login.html` (subject to Open Question 2)
    - Add an additive block above the form that shows messages from `get_flashed_messages()` using a success style. The form, its hardcoded `action="/login"` and all existing behavior are untouched.
- UI states and messages:
  - Empty or whitespace-only name: "Please enter your name."
  - Invalid email: "Please enter a valid email address."
  - Password under 8 characters: "Password must be at least 8 characters."
  - Duplicate email: "An account with this email already exists."
  - Passwords differ (exact, case- and space-sensitive): "Passwords do not match."
  - Success (shown on `/register` as a themed `.auth-notice` card with a Login button linking to `/login` and a close button that reveals the empty form): "Registration successful" / "You have successfully registered. Please login to continue."
- Client behavior: `static/js/main.js` removes the `.auth-error` block as soon as the user edits any field in the form.

## File to create

- `tests/test_register.py` - pytest tests for the registration flow. Uses a temporary database by monkeypatching `database.db.DB_PATH` to a `tmp_path` file and calling `init_db()`, so the real `expense_tracker.db` is never touched.

## File to changes

- `app.py` - allow `POST` on `/register`; read and validate the form; call `create_user`; catch `sqlite3.IntegrityError` for duplicates; `flash` and `redirect` on success; set `app.secret_key`; add a small `validate_registration(name, email, password)` helper that returns an error string or `None`. Imports needed: `request`, `redirect`, `url_for`, `flash`, `sqlite3`, `create_user`.
- `database/db.py` - add `create_user()` and `get_user_by_email()`; import `generate_password_hash` is already present.
- `templates/register.html`, `templates/login.html` - as described under Template.
- `static/css/style.css` - add the `.auth-notice` card styles next to `.auth-error`, built from existing variables (`--accent`, `--accent-light`, `--paper-card`). Only needed if Open Question 2 is confirmed.
- `CLAUDE.md` - update the Routes table so `/register` is marked done (form and POST). Optionally correct the stale "db.py is empty" notes (Open Question 5).

## New Dependency

No new dependencies. `werkzeug.security` and `sqlite3` are already available, and `flask`, `werkzeug`, `pytest` and `pytest-flask` are already in `requirements.txt`.

## Rules for implementations

- Do not use SQLAlchemy or another ORM.
- Use parameterized SQL queries (`?`); never build queries by interpolating user input.
- Hash passwords with Werkzeug (`generate_password_hash`); never store or log the plain password.
- Use existing CSS variables; do not hardcode color hex values in new CSS. The existing `.auth-error` border uses a hardcoded hex; do not copy that pattern.
- Templates extend `base.html` and use `url_for()` for every internal link and redirect.
- All DB logic stays in `database/db.py`; the route only reads the form, calls helpers, and renders or redirects (CLAUDE.md).
- Apply SOLID principles where useful without adding unnecessary complexity: validation lives in one small helper, DB access in `db.py`.
- Validation order: name (trimmed, required, max 100 characters), email (trimmed, lowercased, required, text on both sides of `@`, a `.` in the domain, max 254 characters), password (required, at least 8 characters) and also a confirm password.
- Detect duplicate email by catching `sqlite3.IntegrityError` from the insert, not by a select-then-insert check.
- Do not log the user in on registration; session handling belongs to Step 3.
- Do not implement any other placeholder route. Do not install packages.
- The app stays on port 5001.

## Definition of Done

- [ ] `GET /register` returns 200 and the form posts to the URL generated by `url_for('register')`.
- [ ] A valid name, email and password creates exactly one new row in `users` and returns a 302 redirect to `/register`.
- [ ] The stored `password_hash` differs from the submitted password and passes `check_password_hash`.
- [ ] After registering, `/register` shows the "You have successfully registered. Please login to continue." card once, with a Login button and a close button, and not after a reload (only if Open Question 2 is confirmed).
- [ ] Registering with an existing email, including a different case such as `Demo@Spendly.com` against the seeded `demo@spendly.com`, re-renders the form with the duplicate-email error and creates no row.
- [ ] The password and confirm password should match the exact , if any changes show error.
- [ ] Empty or whitespace-only name shows an error and creates no row.
- [ ] Invalid emails (`abc`, `a@b`, `@x.com`, `a@.com`) show an error and create no row.
- [ ] A password of 7 characters is rejected and one of 8 is accepted.
- [ ] After any error, `name` and `email` keep what the user typed and the password field is empty.
- [ ] The error message should be removed once , `name` and `email` or `password or confirm password` start editing after the error.

- [ ] Leading and trailing spaces are trimmed from name and email, and email is stored lowercase.
- [ ] Input containing HTML such as `<script>alert(1)</script>` is rendered escaped on the re-rendered form.
- [ ] Input such as `x'); DROP TABLE users;--` is handled as plain text and the `users` table still exists afterwards.
- [ ] A hand-crafted POST with missing fields returns the validation error (HTTP 200), not a 500.
- [ ] The seeded demo user is unaffected, and the tests never modify the real `expense_tracker.db`.
- [ ] `make test` passes, including `tests/test_register.py` (to be confirmed by actually running it during implementation).
- [ ] `make run` starts on port 5001 with no errors and `/register` works in the browser.

