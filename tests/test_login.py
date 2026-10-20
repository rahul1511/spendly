import pytest

import database.db as db
from app import app as flask_app

DEMO = {"email": "demo@spendly.com", "password": "demo123"}
ERROR = b"Invalid email or password."


@pytest.fixture
def app(tmp_path, monkeypatch):
    monkeypatch.setattr(db, "DB_PATH", str(tmp_path / "test.db"))
    db.init_db()
    db.seed_db()
    flask_app.config.update(TESTING=True)
    return flask_app


def post_login(client, **overrides):
    return client.post("/login", data={**DEMO, **overrides})


def demo_id():
    return db.get_user_by_email(DEMO["email"])["id"]


def test_login_page_loads_and_form_posts_to_login(client):
    response = client.get("/login")
    assert response.status_code == 200
    assert b'action="/login"' in response.data


def test_valid_login_redirects_to_profile_and_sets_session(client):
    response = post_login(client)
    assert response.status_code == 302
    assert response.headers["Location"] == "/profile"
    with client.session_transaction() as sess:
        assert sess["user_id"] == demo_id()


def test_login_works_for_registered_user(client):
    db.create_user("Asha Rao", "asha@example.com", "secret123")
    response = post_login(client, email="asha@example.com", password="secret123")
    assert response.status_code == 302


def test_email_is_case_and_space_insensitive(client):
    assert post_login(client, email="  Demo@Spendly.com ").status_code == 302


@pytest.mark.parametrize(
    "overrides",
    [{"password": "wrong-password"}, {"email": "nobody@example.com"}],
)
def test_bad_credentials_show_identical_generic_error(client, overrides):
    response = post_login(client, **overrides)
    assert response.status_code == 200
    assert ERROR in response.data
    with client.session_transaction() as sess:
        assert "user_id" not in sess


@pytest.mark.parametrize("data", [{}, {"email": DEMO["email"]}, {"password": "demo123"}])
def test_missing_fields_show_error_not_500(client, data):
    response = client.post("/login", data=data)
    assert response.status_code == 200
    assert ERROR in response.data


def test_email_kept_and_password_not_echoed_after_error(client):
    response = post_login(client, password="wrong-password")
    assert b'value="demo@spendly.com"' in response.data
    assert b"wrong-password" not in response.data


def test_html_in_email_is_escaped(client):
    response = post_login(client, email="<script>alert(1)</script>")
    assert b"<script>alert(1)</script>" not in response.data
    assert b"&lt;script&gt;" in response.data


@pytest.mark.parametrize("value", ["x' OR '1'='1", "x'); DROP TABLE users;--"])
def test_sql_injection_strings_are_plain_text(client, value):
    assert post_login(client, email=value, password=value).status_code == 200
    assert post_login(client, password=value).status_code == 200
    assert db.get_user_by_email(DEMO["email"]) is not None
    with client.session_transaction() as sess:
        assert "user_id" not in sess


def test_password_hash_never_in_response(client):
    hashed = db.get_user_by_email(DEMO["email"])["password_hash"].encode()
    assert hashed not in post_login(client, password="wrong").data
    post_login(client)
    assert hashed not in client.get("/").data


def test_signed_in_login_page_redirects_to_profile(client):
    post_login(client)
    response = client.get("/login")
    assert response.status_code == 302
    assert response.headers["Location"] == "/profile"


def test_logout_clears_session_and_redirects(client):
    post_login(client)
    response = client.post("/logout")
    assert response.status_code == 302
    assert response.headers["Location"] == "/"
    with client.session_transaction() as sess:
        assert "user_id" not in sess


def test_logout_while_signed_out_is_harmless(client):
    assert client.post("/logout").status_code == 302


def test_get_logout_is_not_allowed(client):
    assert client.get("/logout").status_code == 405


def test_stale_session_user_is_signed_out(client):
    with client.session_transaction() as sess:
        sess["user_id"] = 99999
    assert client.get("/login").status_code == 200
    assert b"Logout" not in client.get("/").data


def test_navbar_shows_logout_only_when_signed_in(client):
    signed_out = client.get("/").data
    assert b"Sign in" in signed_out and b"Get started" in signed_out
    assert b"Logout" not in signed_out
    post_login(client)
    signed_in = client.get("/").data
    assert b"Logout" in signed_in
    assert b"Get started" not in signed_in


def test_profile_shows_logout_when_signed_in(client):
    post_login(client)
    response = client.get("/profile")
    assert response.status_code == 200
    assert b"Logout" in response.data
    assert b'action="/logout"' in response.data


def test_profile_redirects_to_login_when_signed_out(client):
    response = client.get("/profile")
    assert response.status_code == 302
    assert response.headers["Location"].endswith("/login")


@pytest.mark.parametrize("method", ["get", "post"])
def test_signed_in_register_redirects_to_profile(client, method):
    post_login(client)
    before = len(db.get_db().execute("SELECT id FROM users").fetchall())
    response = getattr(client, method)("/register")
    assert response.status_code == 302
    assert response.headers["Location"] == "/profile"
    after = len(db.get_db().execute("SELECT id FROM users").fetchall())
    assert after == before


def test_register_open_again_after_logout(client):
    post_login(client)
    client.post("/logout")
    assert client.get("/register").status_code == 200
