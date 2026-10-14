import pytest
from django.test import Client, override_settings

PAGES = [
    "/",
    "/venues/",
    "/venues/1/",
    "/events/",
    "/events/1/",
    "/registrations/",
    "/registrations/1/",
]
MISSING = [
    "/venues/999/",
    "/events/999/",
    "/registrations/999/",
]


@pytest.fixture
def client() -> Client:
    return Client()


@pytest.mark.parametrize("url", PAGES)
def test_page_opens(client, url):
    response = client.get(url)
    assert response.status_code == 200
    assert "<!DOCTYPE html>" in response.content.decode()


@pytest.mark.parametrize("url", MISSING)
def test_missing_object_gives_404(client, url):
    assert client.get(url).status_code == 404


def test_unknown_url_gives_404(client):
    assert client.get("/nonexistent/").status_code == 404


def test_non_numeric_id_does_not_match_route(client):
    assert client.get("/venues/abc/").status_code == 404


def test_venues_page_shows_data_from_json(client):
    assert "Актовый зал" in client.get("/venues/").content.decode()


def test_custom_404_page_when_debug_is_off(client):
    with override_settings(DEBUG=False):
        response = client.get("/nonexistent/")
    assert response.status_code == 404
    assert "страница не найдена" in response.content.decode()
