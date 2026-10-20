import os
import sqlite3

from flask import Flask, flash, redirect, render_template, request, session, url_for

from database.db import create_user, get_db, get_user_by_id, init_db, seed_db, verify_user

app = Flask(__name__)
# The fallback key is for local development only; set SECRET_KEY in any real deployment.
app.secret_key = os.environ.get("SECRET_KEY", "dev-only-secret-key")

with app.app_context():
    init_db()
    seed_db()

NAME_MAX_LENGTH = 100
EMAIL_MAX_LENGTH = 254
PASSWORD_MIN_LENGTH = 8
PASSWORD_MAX_LENGTH = 16


def validate_registration(name, email, password, confirm_password):
    """Return an error message for invalid registration input, else None."""
    if not name or len(name) > NAME_MAX_LENGTH:
        return "Please enter your name."

    local, _, domain = email.partition("@")
    if (
        not local
        or not domain
        or len(email) > EMAIL_MAX_LENGTH
        or "." not in domain
        or domain.startswith(".")
        or domain.endswith(".")
        or "@" in domain
    ):
        return "Please enter a valid email address."

    if len(password) < PASSWORD_MIN_LENGTH:
        return f"Password must be at least {PASSWORD_MIN_LENGTH} characters."
    if len(password) > PASSWORD_MAX_LENGTH:
        return f"Password must be at most {PASSWORD_MAX_LENGTH} characters."
    if password != confirm_password:
        return "Passwords do not match."

    return None


def is_signed_in():
    """True when the session holds the id of an existing user."""
    user_id = session.get("user_id")
    return bool(user_id) and get_user_by_id(user_id) is not None


@app.context_processor
def inject_current_user():
    """Expose the signed-in user (or None) to every template."""
    user_id = session.get("user_id")
    return {"current_user": get_user_by_id(user_id) if user_id else None}


# ------------------------------------------------------------------ #
# Routes                                                              #
# ------------------------------------------------------------------ #

@app.route("/")
def landing():
    return render_template("landing.html")


@app.route("/register", methods=["GET", "POST"])
def register():
    if is_signed_in():
        return redirect(url_for("profile"))

    if request.method == "GET":
        return render_template("register.html")

    name = request.form.get("name", "").strip()
    email = request.form.get("email", "").strip().lower()
    password = request.form.get("password", "")
    confirm_password = request.form.get("confirm_password", "")

    error = validate_registration(name, email, password, confirm_password)
    if error is None:
        try:
            create_user(name, email, password)
        except sqlite3.IntegrityError:
            error = "An account with this email already exists."

    if error:
        return render_template("register.html", error=error, name=name, email=email)

    flash("You have successfully registered. Please login to continue.")
    return redirect(url_for("register"))


@app.route("/login", methods=["GET", "POST"])
def login():
    if is_signed_in():
        return redirect(url_for("profile"))

    if request.method == "GET":
        return render_template("login.html")

    email = request.form.get("email", "").strip().lower()
    password = request.form.get("password", "")

    user = verify_user(email, password)
    if user is None:
        return render_template(
            "login.html", error="Invalid email or password.", email=email
        )

    session["user_id"] = user["id"]
    return redirect(url_for("profile"))


@app.route("/logout", methods=["POST"])
def logout():
    session.clear()
    return redirect(url_for("landing"))


@app.route("/terms")
def terms():
    return render_template("terms.html")


@app.route("/privacy")
def privacy():
    return render_template("privacy.html")


# ------------------------------------------------------------------ #
# Placeholder routes — students will implement these                  #
# ------------------------------------------------------------------ #

@app.route("/profile")
def profile():
    if not session.get("user_id"):
        return redirect(url_for("login"))
    return render_template("profile.html")


@app.route("/expenses/add")
def add_expense():
    return "Add expense — coming in Step 7"


@app.route("/expenses/<int:id>/edit")
def edit_expense(id):
    return "Edit expense — coming in Step 8"


@app.route("/expenses/<int:id>/delete")
def delete_expense(id):
    return "Delete expense — coming in Step 9"


if __name__ == "__main__":
    app.run(debug=True, port=5001)
