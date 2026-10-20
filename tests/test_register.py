import sqlite3

import pytest
from werkzeug.security import check_password_hash

import database.db as db
from app import app as flask_app

VALID_FORM = {"name": "Asha Rao", "email": "asha@example.com", "password": "secret123"}
SUCCESS_MESSAGE = b"You have successfully registered. Please login to continue."


@pytest.fixture
def app(tmp_path, monkeypatch):
    monkeypatch.setattr(db, "DB_PATH", str(tmp_path / "test.db"))
    db.init_db()
    db.seed_db()
    flask_app.config.update(TESTING=True)
    return flask_app


def user_count():
    with db.get_db() as conn:
        return conn.execute("SELECT COUNT(*) FROM users").fetchone()[0]


def post_register(client, **overrides):
    data = {**VALID_FORM, **overrides}
    data.setdefault("confirm_password", data["password"])
    return client.post("/register", data=data)


def test_register_page_loads_and_form_posts_to_register(client):
    response = client.get("/register")
    assert response.status_code == 200
    assert b'action="/register"' in response.data


def test_valid_registration_creates_user_and_redirects_to_register(client):
    before = user_count()
    response = post_register(client)
    assert response.status_code == 302
    assert response.headers["Location"].endswith("/register")
    assert user_count() == before + 1


def test_password_is_hashed(client):
    post_register(client)
    user = db.get_user_by_email("asha@example.com")
    assert user["password_hash"] != VALID_FORM["password"]
    assert check_password_hash(user["password_hash"], VALID_FORM["password"])


def test_success_card_shows_once_on_register_with_login_link_and_close(client):
    response = post_register(client)
    first = client.get(response.headers["Location"])
    assert SUCCESS_MESSAGE in first.data
    assert b"auth-notice" in first.data
    assert b'href="/login"' in first.data
    assert b"data-auth-notice-close" in first.data
    second = client.get("/register")
    assert SUCCESS_MESSAGE not in second.data
    assert b"data-auth-notice-close" not in second.data


def test_login_page_does_not_show_success_card(client):
    post_register(client)
    assert SUCCESS_MESSAGE not in client.get("/login").data


@pytest.mark.parametrize("email", ["demo@spendly.com", "Demo@Spendly.com"])
def test_duplicate_email_is_rejected(client, email):
    before = user_count()
    response = post_register(client, email=email)
    assert response.status_code == 200
    assert b"An account with this email already exists." in response.data
    assert user_count() == before


@pytest.mark.parametrize("name", ["", "   ", "x" * 101])
def test_invalid_name_is_rejected(client, name):
    before = user_count()
    response = post_register(client, name=name)
    assert response.status_code == 200
    assert b"Please enter your name." in response.data
    assert user_count() == before


@pytest.mark.parametrize("email", ["", "abc", "a@b", "@x.com", "a@.com", "a@x.", "a@b@x.com"])
def test_invalid_email_is_rejected(client, email):
    before = user_count()
    response = post_register(client, email=email)
    assert response.status_code == 200
    assert b"Please enter a valid email address." in response.data
    assert user_count() == before


@pytest.mark.parametrize("password", ["", "1234567", "x" * 17])
def test_password_length_out_of_range_is_rejected(client, password):
    before = user_count()
    response = post_register(client, password=password)
    assert response.status_code == 200
    assert b"Password must be at" in response.data
    assert user_count() == before


@pytest.mark.parametrize("password", ["x" * 8, "x" * 16])
def test_password_length_boundaries_are_accepted(client, password):
    response = post_register(client, password=password)
    assert response.status_code == 302


@pytest.mark.parametrize("confirm_password", ["", "secret124", "Secret123", "secret123 "])
def test_confirm_password_must_match_exactly(client, confirm_password):
    before = user_count()
    response = post_register(client, confirm_password=confirm_password)
    assert response.status_code == 200
    assert b"Passwords do not match." in response.data
    assert user_count() == before


def test_missing_confirm_password_field_is_rejected(client):
    response = client.post("/register", data=VALID_FORM)
    assert response.status_code == 200
    assert b"Passwords do not match." in response.data


def test_form_has_confirm_password_field(client):
    assert b'name="confirm_password"' in client.get("/register").data


def test_password_fields_have_toggle_and_confirm_blocks_paste(client):
    html = client.get("/register").data.decode()
    assert html.count("data-password-toggle") == 2
    assert html.count("data-no-paste") == 1
    confirm_input = html.split('id="confirm_password"')[1].split(">")[0]
    assert "data-no-paste" in confirm_input


def test_form_keeps_name_and_email_but_not_password_after_error(client):
    response = post_register(client, password="short")
    assert b'value="Asha Rao"' in response.data
    assert b'value="asha@example.com"' in response.data
    assert b"short" not in response.data


def test_name_and_email_are_trimmed_and_email_lowercased(client):
    post_register(client, name="  Asha Rao  ", email="  Asha@Example.COM  ")
    user = db.get_user_by_email("asha@example.com")
    assert user["name"] == "Asha Rao"
    assert user["email"] == "asha@example.com"


def test_html_input_is_escaped(client):
    response = post_register(client, name="<script>alert(1)</script>", password="short")
    assert b"<script>alert(1)</script>" not in response.data
    assert b"&lt;script&gt;" in response.data


def test_sql_injection_input_is_stored_as_plain_text(client):
    name = "x'); DROP TABLE users;--"
    response = post_register(client, name=name)
    assert response.status_code == 302
    with db.get_db() as conn:
        assert conn.execute("SELECT name FROM users WHERE email = ?", ("asha@example.com",)).fetchone()[0] == name
        conn.execute("SELECT 1 FROM users").fetchone()


def test_missing_fields_return_validation_error_not_500(client):
    response = client.post("/register", data={})
    assert response.status_code == 200
    assert b"Please enter your name." in response.data


def test_seeded_demo_user_is_unaffected(client):
    post_register(client)
    demo = db.get_user_by_email("demo@spendly.com")
    assert demo["name"] == "Demo User"
    assert check_password_hash(demo["password_hash"], "demo123")


def test_create_user_duplicate_email_raises_integrity_error(app):
    with pytest.raises(sqlite3.IntegrityError):
        db.create_user("Other", "demo@spendly.com", "whatever1")
