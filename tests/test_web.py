import pytest
from django.test import override_settings

pytestmark = pytest.mark.usefixtures("sample_data")

PAGES = [
    "/",
    "/venues/",
    "/venues/aktovyy-zal-1/",
    "/events/",
    "/events/1/",
    "/registrations/",
    "/registrations/1/",
    "/registrations/statistics/",
    "/venues/available/",
]
MISSING = [
    "/venues/999/",
    "/venues/no-such-venue/",
    "/events/999/",
    "/registrations/999/",
]


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


def test_non_numeric_id_does_not_match_event_route(client):
    assert client.get("/events/abc/").status_code == 404


def test_custom_404_page_when_debug_is_off(client):
    with override_settings(DEBUG=False):
        response = client.get("/nonexistent/")
    assert response.status_code == 404
    assert "страница не найдена" in response.content.decode()


def test_pages_use_base_template_and_static(client):
    html = client.get("/venues/").content.decode()
    assert "/static/homepage/css/style.css" in html
    assert "/static/homepage/js/main.js" in html


def test_venues_page_shows_data_from_database(client):
    html = client.get("/venues/").content.decode()
    assert "Всего площадок: 3" in html
    assert "Актовый зал" in html


def test_venue_page_lists_its_events_via_related_name(client):
    html = client.get("/venues/aktovyy-zal-1/").content.decode()
    assert "Лекция «Введение в Django»" in html
    assert "Карьерный день" in html


def test_registration_status_include_for_each_state(client):
    html = client.get("/registrations/").content.decode()
    assert "registration-status-registered" in html
    assert "registration-status-waitlist" in html


def test_cancelled_registrations_are_not_listed(client):
    html = client.get("/registrations/").content.decode()
    assert "Ольга Волкова" not in html


def test_event_page_shows_related_venue_and_counts(client):
    html = client.get("/events/2/").content.decode()
    assert "Аудитория А-305" in html
    assert "20.10.2026 14:00" in html
    assert "зарегистрировано 3" in html


def test_events_are_paginated(client):
    first = client.get("/events/?status=all").context
    assert first["total"] == 10
    assert len(first["events"]) == 5
    second = client.get("/events/?status=all&page=2").context
    assert second["page_obj"].number == 2


def test_bad_page_number_opens_first_page(client):
    assert client.get("/events/?page=abc").context["page_obj"].number == 1


def test_events_filter_by_venue_and_sort_by_title(client):
    context = client.get("/events/?status=all&venue=1&sort=title").context
    titles = [event.title for event in context["events"]]
    assert context["total"] == 4
    assert titles == sorted(titles)


def test_events_filter_by_date(client):
    context = client.get("/events/?date=2026-12-12").context
    assert [e.title for e in context["events"]] == ["Семинар по Django ORM"]


def test_events_search_ignores_case_for_cyrillic(client):
    assert client.get(
        "/events/?status=all&q=лекция").context["total"] == 2


def test_events_bad_date_shows_error(client):
    html = client.get("/events/?date=15.10.2026").content.decode()
    assert "ГГГГ-ММ-ДД" in html


def test_pagination_keeps_filters(client):
    html = client.get("/events/?sort=title").content.decode()
    assert "?sort=title&amp;page=2" in html


def test_available_venues_for_busy_date(client):
    html = client.get(
        "/venues/available/?date=2026-12-03").content.decode()
    assert "Актовый зал" not in html
    assert "Коворкинг" in html


def test_available_venues_rejects_bad_date(client):
    html = client.get(
        "/venues/available/?date=15.10.2026").content.decode()
    assert "ГГГГ-ММ-ДД" in html


def test_available_venues_is_not_vulnerable_to_injection(client):
    response = client.get("/venues/available/?date=' OR 1=1 --")
    assert response.status_code == 200
    assert "Актовый зал" not in response.content.decode()


def test_statistics_page(client):
    html = client.get("/registrations/statistics/").content.decode()
    assert "Участников: 9" in html
    assert "в листе ожидания: 2" in html
    assert "Мероприятий: 10" in html
    assert "Семинар по Django ORM: в очереди 1" in html


def test_events_list_shows_only_active_by_default(client):
    from events.models import Event
    Event.objects.filter(pk=4).update(status=Event.Status.CANCELLED)
    titles = [e.title for e in client.get("/events/").context["events"]]
    assert "Мастер-класс по Docker" not in titles
    cancelled = client.get("/events/?status=cancelled").context["events"]
    assert [e.title for e in cancelled] == ["Мастер-класс по Docker"]


def test_cancelled_event_does_not_block_venue(client):
    from events.models import Event
    Event.objects.filter(pk=4).update(status=Event.Status.CANCELLED)
    html = client.get(
        "/venues/available/?date=2026-12-03").content.decode()
    assert "Актовый зал" in html


def test_statistics_counts_event_statuses(client):
    html = client.get("/registrations/statistics/").content.decode()
    assert "завершено: 3" in html


def test_footer_uses_context_processor(client):
    html = client.get("/").content.decode()
    assert "площадок: 3" in html
