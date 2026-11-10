import re
from contextlib import closing
from datetime import date
from pathlib import Path

import pytest

import database.db as db
from app import app as flask_app
from app import format_date, format_inr

ROOT = Path(__file__).resolve().parent.parent
DEMO = {"email": "demo@spendly.com", "password": "demo123"}


@pytest.fixture
def app(tmp_path, monkeypatch):
    monkeypatch.setattr(db, "DB_PATH", str(tmp_path / "test.db"))
    db.init_db()
    db.seed_db()
    flask_app.config.update(TESTING=True)
    return flask_app


def sign_in(client, email=DEMO["email"], password=DEMO["password"]):
    return client.post("/login", data={"email": email, "password": password})


def test_profile_redirects_to_login_when_signed_out(client):
    response = client.get("/profile")
    assert response.status_code == 302
    assert response.headers["Location"].endswith("/login")


def test_profile_with_stale_session_redirects_and_clears_user_id(client):
    with client.session_transaction() as sess:
        sess["user_id"] = 9999
    response = client.get("/profile")
    assert response.status_code == 302
    assert response.headers["Location"].endswith("/login")
    with client.session_transaction() as sess:
        assert "user_id" not in sess


def test_profile_shows_demo_account_details(client):
    sign_in(client)
    response = client.get("/profile")
    body = response.get_data(as_text=True)
    assert response.status_code == 200
    assert "Demo User" in body
    assert "demo@spendly.com" in body
    assert "Member since" in body
    assert format_date(date.today().isoformat()) in body
    assert "coming soon" not in body


def test_profile_never_exposes_password_hash(client):
    sign_in(client)
    body = client.get("/profile").get_data(as_text=True)
    password_hash = db.get_user_by_email(DEMO["email"])["password_hash"]
    assert password_hash not in body


def test_registered_user_sees_own_details(client):
    db.create_user("Asha Rao", "asha@example.com", "secret123")
    sign_in(client, "asha@example.com", "secret123")
    body = client.get("/profile").get_data(as_text=True)
    assert "Asha Rao" in body
    assert "asha@example.com" in body
    assert "demo@spendly.com" not in body


def test_profile_escapes_user_name(client):
    db.create_user("<script>alert(1)</script>", "xss@example.com", "secret123")
    sign_in(client, "xss@example.com", "secret123")
    body = client.get("/profile").get_data(as_text=True)
    assert "<script>alert(1)</script>" not in body
    assert "&lt;script&gt;" in body


def test_profile_has_add_expense_link_with_icon_and_stylesheet(client):
    sign_in(client)
    body = client.get("/profile").get_data(as_text=True)
    link = re.search(r'<a href="/expenses/add"[^>]*>(.*?)</a>', body, re.S)
    assert link is not None
    assert '<svg' in link.group(1) and 'aria-hidden="true"' in link.group(1)
    assert "Add expense" in link.group(1)
    assert "css/profile.css" in body


def test_profile_post_not_allowed(client):
    sign_in(client)
    assert client.post("/profile").status_code == 405


@pytest.mark.parametrize(
    "value, expected",
    [
        ("2026-11-12 08:30:00", "12 Nov 2026"),
        ("2026-11-12", "12 Nov 2026"),
        (None, "—"),
        ("not-a-date", "—"),
    ],
)
def test_format_date(value, expected):
    assert format_date(value) == expected


def add_expense_row(user_id, amount, category, day, description=None):
    with closing(db.get_db()) as conn, conn:
        conn.execute(
            "INSERT INTO expenses (user_id, amount, category, date, description)"
            " VALUES (?, ?, ?, ?, ?)",
            (user_id, amount, category, day, description),
        )


def test_profile_overview_for_demo_user(client):
    sign_in(client)
    body = client.get("/profile").get_data(as_text=True)
    assert "₹400.64" in body          # seeded total
    assert "Spending by category" in body
    assert "Recent expenses" in body
    for category in ["Food", "Transport", "Bills", "Health", "Entertainment", "Shopping", "Other"]:
        assert f"cat-{category.lower()}" in body
    assert "No expenses yet" not in body


def test_expense_summary_and_category_totals(app):
    demo = db.get_user_by_email(DEMO["email"])["id"]
    summary = db.get_expense_summary(demo)
    assert summary == {"total": pytest.approx(400.64), "count": 8, "top_category": "Bills"}
    totals = db.get_category_totals(demo)
    assert [r["category"] for r in totals][:2] == ["Bills", "Shopping"]
    assert next(r for r in totals if r["category"] == "Food")["count"] == 2


def test_recent_expenses_newest_first_and_limited(app):
    user_id = db.create_user("Many", "many@example.com", "secret123")
    for day in range(1, 16):
        add_expense_row(user_id, 10, "Food", f"2026-01-{day:02d}", f"Item {day}")
    recent = db.get_recent_expenses(user_id)
    assert len(recent) == 10
    assert [r["date"] for r in recent][:2] == ["2026-01-15", "2026-01-14"]


def test_new_user_sees_empty_state(client):
    db.create_user("Fresh", "fresh@example.com", "secret123")
    sign_in(client, "fresh@example.com", "secret123")
    body = client.get("/profile").get_data(as_text=True)
    assert "No expenses yet" in body
    assert "Total spent" not in body
    assert body.count('class="btn-primary') == 1


def test_profile_only_shows_own_expenses(client):
    user_id = db.create_user("Priya", "priya@example.com", "secret123")
    add_expense_row(user_id, 1234567.5, "Shopping", "2026-02-01", "Priya's laptop")
    sign_in(client, "priya@example.com", "secret123")
    body = client.get("/profile").get_data(as_text=True)
    assert "Priya&#39;s laptop" in body
    assert "₹12,34,567.50" in body
    assert "Groceries" not in body     # demo user's expense


def test_missing_description_falls_back_to_category(client):
    user_id = db.create_user("Nodesc", "nodesc@example.com", "secret123")
    add_expense_row(user_id, 99, "Health", "2026-03-03")
    sign_in(client, "nodesc@example.com", "secret123")
    body = client.get("/profile").get_data(as_text=True)
    assert '<span class="profile-expense-desc">Health</span>' in body
    assert "None" not in body


@pytest.mark.parametrize(
    "value, expected",
    [
        (123456.5, "₹1,23,456.50"),
        (0, "₹0.00"),
        (999, "₹999.00"),
        (1000, "₹1,000.00"),
        (10000000, "₹1,00,00,000.00"),
        (-1500.25, "-₹1,500.25"),
    ],
)
def test_format_inr(value, expected):
    assert format_inr(value) == expected


def test_profile_styles_use_variables_only():
    css = (ROOT / "static/css/profile.css").read_text()
    template = (ROOT / "templates/profile.html").read_text()
    assert not re.search(r"#[0-9a-fA-F]{3,6}\b", css)
    assert "<style" not in template
    assert "style=" not in template
