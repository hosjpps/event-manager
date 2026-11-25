from datetime import datetime

import pytest
from django.db.models import ProtectedError
from django.utils import timezone

from db.import_sqlite_to_orm import main as import_from_pr7_database
from events.models import Event
from registrations.models import Registration
from venues.models import Venue


@pytest.fixture
def venue(db):
    return Venue.objects.create(name="Зал", address="ул. Тест, 1",
                                capacity=50)


@pytest.fixture
def event(venue):
    start = timezone.make_aware(datetime(2030, 1, 10, 10))
    return Event.objects.create(
        title="Лекция", venue=venue, starts_at=start,
        ends_at=start.replace(hour=12), capacity=40,
    )


def test_import_from_pr7_database_keeps_ids_and_links(db):
    import_from_pr7_database()
    assert Venue.objects.count() == 3
    assert Event.objects.count() == 3
    assert Registration.objects.count() == 5
    registration = Registration.objects.select_related("event__venue").get(
        pk=5)
    assert registration.event.pk == 2
    assert registration.event.venue.name == "Аудитория А-305"


def test_import_can_be_repeated_without_duplicates(db):
    import_from_pr7_database()
    import_from_pr7_database()
    assert Registration.objects.count() == 5


def test_str_and_model_methods(event):
    assert str(event.venue) == "Зал"
    assert str(event) == "Лекция (Зал)"
    assert event.venue.can_host(50)
    assert not event.venue.can_host(51)
    assert event.is_registration_open()


def test_reverse_relations_by_related_name(event):
    registration = Registration.objects.create(
        event=event, participant="Анна", email="a@test.ru",
        registered_at=timezone.now(),
    )
    assert list(event.venue.events.all()) == [event]
    assert list(event.registrations.all()) == [registration]


def test_venue_with_events_cannot_be_deleted(event):
    with pytest.raises(ProtectedError):
        event.venue.delete()


def test_deleting_event_deletes_its_registrations(event):
    Registration.objects.create(
        event=event, participant="Анна", email="a@test.ru",
        registered_at=timezone.now(),
    )
    event.delete()
    assert Registration.objects.count() == 0


def test_cancel_saves_status(event):
    registration = Registration.objects.create(
        event=event, participant="Анна", email="a@test.ru",
        registered_at=timezone.now(),
    )
    registration.cancel()
    registration.refresh_from_db()
    assert registration.status == "cancelled"
