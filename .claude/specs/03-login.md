# Spec: Login

## Overview

Make the existing `/login` page functional so a registered user can sign in, and make `/logout` end the session. Today `login()` in `app.py` only renders `login.html` (GET only, so the form's POST has nowhere to go) and `logout()` is a placeholder string. This step verifies the submitted email and password against the `users` table (Step 1) populated by registration (Step 2), stores the user's id in the Flask session, and lets the navbar reflect who is signed in. CLAUDE.md marks both `/login` POST handling and `/logout` as Step 3.

## Depends on

- Step 1: Database Setup (`users` table, `get_db()`, `init_db()`, `seed_db()` in `database/db.py`)
- Step 2: Registration (`create_user()`, `get_user_by_email()`, `app.secret_key`, Werkzeug password hashing)

## Open Questions

Resolved with the user before writing this spec:

1. Post-login destination: **profile page** (`url_for("profile")`), changed from the landing page after review. `/profile` is still a Step 4 placeholder returning plain text until that step is built; it is not implemented here.
2. `/logout` method: **POST only**, triggered by a button in a small form.
3. Shared `base.html` navbar: **may be modified** to show Logout when signed in; the signed-out navbar stays unchanged.
4. Signed-in visitor on `/login`: **redirected** to the profile page. Failed logins use one generic message, "Invalid email or password."

Still unconfirmed (treated as out of scope; confirm if wanted):

5. Brute-force protection, lockout and "remember me" are not in the repo or the request. The session is a normal browser-session cookie.
6. `tests/test_register.py::test_register_page_loads_and_form_posts_to_register` asserts the literal `action="/register"`, while `register.html` currently uses `url_for('register')`. Not caused by this step and not verified by running the suite; decide separately whether to update it.

## Routes

- `GET /login` - existing route; renders the sign-in form. Public. A signed-in visitor is redirected (302) to `profile`.
- `POST /login` - new method on the same route. Public.
  - Inputs: form fields `email`, `password`. Email is trimmed and lowercased before lookup (registration stores it lowercase).
  - Success: `session["user_id"]` set to the user's `id`; 302 redirect to `profile`.
  - Failure (missing field, unknown email, wrong password): HTTP 200, `login.html` re-rendered with `error` and the submitted `email` pre-filled. The password is never echoed back.
- `POST /logout` - existing placeholder route, replaced; methods become `POST` only (a GET returns 405). Access: logged-in in intent, but harmless when signed out.
  - Clears the session and redirects (302) to `landing`. No raw string response.

No other route changes. `/profile` and the `/expenses/...` placeholders stay as they are.

## Database Changes

No database changes. `users` already has `id`, `name`, `email` (`NOT NULL UNIQUE`) and `password_hash`.

`database/db.py` already provides `get_user_by_email(email)`. Add one helper in the same style (`with closing(get_db()) as conn`, `?` placeholders):

- `get_user_by_id(user_id)` - returns the matching `sqlite3.Row` or `None`, so a session pointing at a deleted user can be treated as signed out.

Credential checking uses `check_password_hash` from `werkzeug.security`. It may live in a small `db.py` helper (for example `verify_user(email, password)`, returning the row or `None`) or in `app.py`; either way all SQL stays in `db.py`.

## Template

- Create: none.
- Modify:
  - `templates/login.html`
    - Change the hardcoded `action="/login"` to `action="{{ url_for('login') }}"`.
    - Pre-fill email with `value="{{ email or '' }}"` after an error (autoescaping stays on). Password is never pre-filled.
    - Add `maxlength="254"` to the email input to match registration. No password length attributes (login must not enforce or reveal password rules).
    - Keep the existing `.auth-error` block as the single place for error text.
  - `templates/base.html`
    - When a user is signed in, replace the "Sign in" and "Get started" links with a Logout button inside a `<form method="POST" action="{{ url_for('logout') }}">`. Signed-out rendering is unchanged, so landing, terms, privacy, register and login look the same for visitors.
- UI states and messages:
  - Missing fields, unknown email, or wrong password: "Invalid email or password." (HTTP 200, never a 500).
  - Success: redirect to the profile page; no message on the form.
- Client behavior: `static/js/main.js` already clears `.auth-error` on edit for the registration form; confirm during implementation whether it also covers the login form and extend the selector only if it does not.

## File to create

- `tests/test_login.py` - pytest tests for login and logout. Uses the same temporary-database fixture as `tests/test_register.py` (monkeypatch `database.db.DB_PATH` to a `tmp_path` file, then `init_db()` and `seed_db()`), so the real `expense_tracker.db` is never touched.

## File to changes

- `app.py` - allow `POST` on `/login`; read `email` and `password`; verify credentials; set `session["user_id"]`; redirect or re-render with `error`; redirect already-signed-in visitors away from `/login`; implement `POST /logout` (clear session, redirect to `landing`); expose the signed-in user to templates (for example via a context processor that uses `get_user_by_id`). Imports needed: `session` and the new db helpers.
- `database/db.py` - add `get_user_by_id()` (and the optional credential-check helper).
- `templates/login.html` - as described under Template.
- `templates/base.html` - signed-in navbar state.
- `static/js/main.js` - only if error clearing does not already cover the login form.
- `static/css/style.css` - styling for the navbar Logout button, using existing variables only.
- `CLAUDE.md` - update the Routes table: `/login` done (form + POST) and `/logout` done.

## New Dependency

No new dependencies. `flask.session` and `werkzeug.security` are already available.

## Rules for implementations

- Do not use SQLAlchemy or another ORM.
- Use parameterized SQL queries (`?`); never build queries by interpolating user input.
- Verify passwords with Werkzeug's `check_password_hash` against `password_hash`; never store, compare or log the plain password.
- Use existing CSS variables; do not hardcode color hex values in new CSS.
- Extend `base.html` for any new page; use `url_for()` for every internal link, form action and redirect.
- All DB logic stays in `database/db.py`; route functions only read the form, call helpers, and render, redirect or abort (CLAUDE.md).
- Apply SOLID principles where useful without adding unnecessary complexity: keep credential checking in one small helper, not inline in the route.
- Use the existing `app.secret_key` for the session; add no new configuration mechanism.
- Use one generic error message for unknown email and wrong password.
- Store only the user's `id` in the session, never the hash or other user data.
- Replace the `/logout` raw-string placeholder with a redirect (CLAUDE.md). Do not implement `/profile` or any `/expenses/...` route in this step.
- The app stays on port 5001. Do not install packages.

## Definition of Done

- [ ] `GET /login` returns 200 and the form posts to the URL generated by `url_for('login')`.
- [ ] `POST /login` with the seeded demo credentials (`demo@spendly.com` / `demo123`) returns 302 to `/profile` and sets `session["user_id"]` to that user's id.
- [ ] Login works for a user created via `/register`; email matching ignores case and surrounding spaces (`  Demo@Spendly.com `).
- [ ] A wrong password for an existing email re-renders the form (200) with "Invalid email or password." and no `user_id` in the session.
- [ ] An unknown email shows the identical message and response status.
- [ ] A hand-crafted POST with missing `email` or `password` returns 200 with the error, not a 500.
- [ ] After a failed attempt the email field keeps what the user typed and the password field is empty.
- [ ] The error message disappears when the user edits a field after an error.
- [ ] HTML such as `<script>alert(1)</script>` in the email is rendered escaped on the re-rendered form.
- [ ] `x' OR '1'='1` as email or password logs nobody in and the `users` table still exists afterwards.
- [ ] The `password_hash` never appears in any response body or in the session.
- [ ] A signed-in `GET /login` redirects to `/profile`.
- [ ] `POST /logout` clears the session and redirects to the landing page; a later request has no `user_id`; calling it while signed out does not error.
- [ ] `GET /logout` returns 405.
- [ ] A session holding a non-existent user id is treated as signed out.
- [ ] The navbar shows a Logout button when signed in and the original Sign in / Get started links when signed out.
- [ ] Registration, landing, terms and privacy pages render unchanged for signed-out visitors.
- [ ] Tests never modify the real `expense_tracker.db`.
- [ ] `make test` passes, including `tests/test_login.py` (to be confirmed by actually running it during implementation).
- [ ] `make run` starts on port 5001 with no errors, and sign-in and logout work in the browser.
