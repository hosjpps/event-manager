import io
from datetime import timedelta

import pytest
from django.core.files.uploadedfile import SimpleUploadedFile
from django.utils import timezone
from PIL import Image

from events.models import Event
from venues.models import Venue

pytestmark = pytest.mark.usefixtures("sample_data")


@pytest.fixture
def client(client, django_user_model):
    """Формы изменяют данные, поэтому тесты работают от администратора."""
    admin = django_user_model.objects.create_superuser(
        "admin", "admin@test.ru", "pass12345")
    client.force_login(admin)
    return client


def slot(days=40, hour=10, length=2):
    """Время в будущем в формате поля datetime-local."""
    start = timezone.localtime() + timedelta(days=days)
    start = start.replace(hour=hour, minute=0, second=0, microsecond=0)
    end = start + timedelta(hours=length)
    return start.strftime("%Y-%m-%dT%H:%M"), end.strftime("%Y-%m-%dT%H:%M")


def event_data(**changes):
    starts_at, ends_at = slot()
    data = {
        "title": "Новое мероприятие",
        "venue": "3",
        "starts_at": starts_at,
        "ends_at": ends_at,
        "capacity": "20",
        "is_published": "on",
    }
    data.update(changes)
    return data


def test_create_form_page_has_csrf_token(client):
    html = client.get("/events/create/").content.decode()
    assert "csrfmiddlewaretoken" in html


def test_create_event(client):
    response = client.post("/events/create/", event_data())
    event = Event.objects.get(title="Новое мероприятие")
    assert response.status_code == 302
    assert response["Location"] == f"/events/{event.pk}/"
    assert event.status == Event.Status.ACTIVE


def test_cannot_create_event_in_the_past(client):
    past = (timezone.localtime() - timedelta(days=1)).strftime(
        "%Y-%m-%dT%H:%M")
    response = client.post("/events/create/", event_data(starts_at=past))
    assert response.status_code == 200
    assert "starts_at" in response.context["form"].errors
    assert not Event.objects.filter(title="Новое мероприятие").exists()


def test_end_must_be_after_start(client):
    starts_at, _ = slot()
    response = client.post(
        "/events/create/", event_data(ends_at=starts_at))
    assert "ends_at" in response.context["form"].errors


def test_capacity_cannot_exceed_venue(client):
    response = client.post("/events/create/", event_data(capacity="999"))
    assert "capacity" in response.context["form"].errors


def test_busy_venue_is_rejected(client):
    client.post("/events/create/", event_data())
    response = client.post(
        "/events/create/", event_data(title="Второе"))
    errors = response.context["form"].non_field_errors()
    assert "занята" in errors[0]
    assert not Event.objects.filter(title="Второе").exists()


def test_cancelled_event_does_not_block_venue(client):
    client.post("/events/create/", event_data())
    first = Event.objects.get(title="Новое мероприятие")
    client.post(f"/events/{first.pk}/cancel/")
    response = client.post("/events/create/", event_data(title="Второе"))
    assert response.status_code == 302


def test_edit_does_not_conflict_with_itself(client):
    client.post("/events/create/", event_data())
    event = Event.objects.get(title="Новое мероприятие")
    response = client.post(
        f"/events/{event.pk}/edit/", event_data(title="Переименовано"))
    assert response.status_code == 302
    event.refresh_from_db()
    assert event.title == "Переименовано"


def test_edit_form_is_filled_with_current_values(client):
    html = client.get("/events/4/edit/").content.decode()
    assert "Мастер-класс по Docker" in html


def test_edit_missing_event_gives_404(client):
    assert client.get("/events/999/edit/").status_code == 404


def test_cancel_requires_post(client):
    assert client.get("/events/4/cancel/").status_code == 405
    assert Event.objects.get(pk=4).status == Event.Status.ACTIVE


def test_cancel_changes_status_and_hides_from_active_list(client):
    client.post("/events/4/cancel/")
    assert Event.objects.get(pk=4).status == Event.Status.CANCELLED
    titles = [e.title for e in client.get("/events/").context["events"]]
    assert "Мастер-класс по Docker" not in titles


def test_filter_form_rejects_bad_values_without_crash(client):
    response = client.get("/events/?venue=999&status=bad&q=x")
    assert response.status_code == 200
    errors = response.context["form"].errors
    assert {"venue", "status", "q"} <= set(errors)


def test_filter_form_applies_valid_values(client):
    context = client.get("/events/?venue=1&status=all").context
    assert context["form"].is_valid()
    assert context["total"] == 4


def make_png() -> bytes:
    buffer = io.BytesIO()
    Image.new("RGB", (20, 20), "blue").save(buffer, "PNG")
    return buffer.getvalue()


def test_upload_venue_photo(client, settings, tmp_path):
    settings.MEDIA_ROOT = tmp_path
    photo = SimpleUploadedFile("hall.png", make_png(), "image/png")
    response = client.post("/venues/kovorking-3/photo/", {"photo": photo})
    assert response.status_code == 302
    venue = Venue.objects.get(pk=3)
    assert venue.photo.name.startswith("venues/hall")
    assert (tmp_path / venue.photo.name).exists()
    html = client.get("/venues/kovorking-3/").content.decode()
    assert venue.photo.url in html


def test_upload_rejects_not_an_image(client, settings, tmp_path):
    settings.MEDIA_ROOT = tmp_path
    fake = SimpleUploadedFile("hall.png", b"not an image", "image/png")
    response = client.post("/venues/kovorking-3/photo/", {"photo": fake})
    assert response.status_code == 200
    assert "photo" in response.context["form"].errors


@pytest.mark.parametrize("url", [
    "/events/create/", "/events/4/edit/", "/venues/kovorking-3/photo/",
])
def test_anonymous_user_is_sent_to_login(url, django_user_model):
    from django.test import Client
    response = Client().get(url)
    assert response.status_code == 302
    assert "/admin/login/" in response["Location"]


def test_anonymous_user_cannot_cancel_event():
    from django.test import Client
    Client().post("/events/4/cancel/")
    assert Event.objects.get(pk=4).status == Event.Status.ACTIVE


def test_user_without_permission_gets_403(django_user_model):
    from django.test import Client
    user = django_user_model.objects.create_user("guest", password="x12345")
    guest = Client()
    guest.force_login(user)
    assert guest.get("/events/create/").status_code == 403
    assert guest.post("/events/4/cancel/").status_code == 403


def test_buttons_hidden_from_anonymous():
    from django.test import Client
    html = Client().get("/events/4/").content.decode()
    assert "Редактировать" not in html
    assert "Создать мероприятие" not in Client().get(
        "/events/").content.decode()
