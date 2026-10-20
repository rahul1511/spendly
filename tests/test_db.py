import sqlite3

import pytest
from werkzeug.security import check_password_hash

from database import db


@pytest.fixture(autouse=True)
def tmp_db(tmp_path, monkeypatch):
    monkeypatch.setattr(db, "DB_PATH", str(tmp_path / "test.db"))
    db.init_db()


def test_init_db_is_idempotent():
    db.init_db()
    conn = db.get_db()
    names = {r["name"] for r in conn.execute("SELECT name FROM sqlite_master WHERE type='table'")}
    conn.close()
    assert {"users", "expenses"} <= names


def test_seed_db_runs_once():
    db.seed_db()
    db.seed_db()
    conn = db.get_db()
    assert conn.execute("SELECT COUNT(*) FROM users").fetchone()[0] == 1
    assert conn.execute("SELECT COUNT(*) FROM expenses").fetchone()[0] == 8
    categories = {r["category"] for r in conn.execute("SELECT category FROM expenses")}
    user = conn.execute("SELECT * FROM users").fetchone()
    conn.close()
    assert categories == set(db.CATEGORIES)
    assert check_password_hash(user["password_hash"], "demo123")


def test_foreign_keys_enabled():
    conn = db.get_db()
    assert conn.execute("PRAGMA foreign_keys").fetchone()[0] == 1
    conn.close()


def test_duplicate_email_rejected():
    db.seed_db()
    conn = db.get_db()
    with pytest.raises(sqlite3.IntegrityError):
        conn.execute(
            "INSERT INTO users (name, email, password_hash) VALUES (?, ?, ?)",
            ("Other", "demo@spendly.com", "x"),
        )
    conn.close()


def test_invalid_user_id_rejected():
    conn = db.get_db()
    with pytest.raises(sqlite3.IntegrityError):
        conn.execute(
            "INSERT INTO expenses (user_id, amount, category, date) VALUES (?, ?, ?, ?)",
            (999, 1.0, "Food", "2026-01-01"),
        )
    conn.close()
