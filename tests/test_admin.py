import pytest
from django.contrib.auth import get_user_model

from events.models import Event
from venues.models import Venue

pytestmark = pytest.mark.usefixtures("sample_data")


@pytest.fixture
def admin_client(client, db):
    user = get_user_model().objects.create_superuser(
        "admin", "admin@test.ru", "pass12345")
    client.force_login(user)
    return client


@pytest.mark.parametrize("url", [
    "/admin/",
    "/admin/venues/venue/",
    "/admin/events/event/",
    "/admin/registrations/registration/",
    "/admin/venues/venue/1/change/",
    "/admin/events/event/2/change/",
])
def test_admin_pages_open(admin_client, url):
    assert admin_client.get(url).status_code == 200


def test_admin_requires_login(client):
    response = client.get("/admin/venues/venue/")
    assert response.status_code == 302
    assert "/admin/login/" in response["Location"]


def test_admin_app_names_are_russian(admin_client):
    html = admin_client.get("/admin/").content.decode()
    assert "Площадки" in html and "Мероприятия" in html


def test_admin_search_by_related_field(admin_client):
    response = admin_client.get("/admin/events/event/?q=Коворкинг")
    titles = [e.title for e in response.context["cl"].result_list]
    assert "Хакатон клуба разработчиков" in titles
    assert "Карьерный день" not in titles


def test_admin_event_page_has_registration_inline(admin_client):
    html = admin_client.get("/admin/events/event/2/change/").content.decode()
    assert "Анна Смирнова" in html


def test_admin_action_cancels_events(admin_client):
    admin_client.post("/admin/events/event/", {
        "action": "mark_cancelled",
        "_selected_action": ["4", "5"],
    })
    assert Event.objects.cancelled().count() == 2


def test_view_on_site_uses_get_absolute_url(admin_client):
    venue = Venue.objects.get(pk=1)
    assert venue.get_absolute_url() == "/venues/aktovyy-zal-1/"
