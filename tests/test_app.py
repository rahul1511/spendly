import pytest

from app import app as flask_app


@pytest.fixture
def app():
    flask_app.config.update(TESTING=True)
    return flask_app


@pytest.mark.parametrize("path", ["/", "/register", "/login"])
def test_page_loads(client, path):
    assert client.get(path).status_code == 200


@pytest.mark.parametrize("path", ["/", "/register", "/login", "/terms", "/privacy"])
def test_page_has_no_text_before_doctype(client, path):
    # Text placed before {% extends %} in a child template is rendered above the page.
    assert client.get(path).get_data(as_text=True).lstrip().startswith("<!DOCTYPE html>")
