import pytest

from app import app as flask_app


@pytest.fixture
def app():
    flask_app.config.update(TESTING=True)
    return flask_app


@pytest.mark.parametrize("path", ["/", "/register", "/login"])
def test_page_loads(client, path):
    assert client.get(path).status_code == 200
