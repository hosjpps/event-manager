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


def test_pages_use_base_template_and_static(client):
    html = client.get("/venues/").content.decode()
    assert "/static/homepage/css/style.css" in html
    assert "/static/homepage/js/main.js" in html
    assert 'href="/events/"' in html


def test_list_uses_length_filter_and_include(client):
    html = client.get("/events/").content.decode()
    assert "Всего мероприятий: 3" in html
    assert html.count('class="card event-card') == 3


def test_registration_status_include_for_each_state(client):
    html = client.get("/registrations/").content.decode()
    assert "registration-status-registered" in html
    assert "registration-status-waitlist" in html


def test_event_date_is_formatted_by_filter(client):
    assert "20.10.2026 14:00" in client.get("/events/2/").content.decode()


def test_missing_object_shows_message_in_template(client):
    html = client.get("/events/999/").content.decode()
    assert "Мероприятие не найдено" in html
