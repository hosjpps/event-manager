from datetime import datetime

import pytest

from models import Event, Registration, Venue
from models.registrations import (cancel_registration, count_registered,
                                  get_event_participants,
                                  get_registration_status, get_statistics,
                                  register_participant)

NOW = datetime(2026, 10, 1, 12)


def make_event(capacity: int = 2) -> Event:
    venue = Venue(1, "Аудитория", "адрес", 50)
    return Event(1, "Семинар", venue, datetime(2026, 10, 20, 14),
                 datetime(2026, 10, 20, 16), capacity)


def register(registrations, event, name, minute=0):
    return register_participant(
        registrations, event, name, f"{name}@test.ru",
        NOW.replace(minute=minute),
    )


def test_registration_keeps_link_to_event():
    event = make_event()
    registrations: list[Registration] = []
    registration = register(registrations, event, "a")
    assert registration.event is event
    assert registration.event.venue.name == "Аудитория"
    assert registration.is_active()


def test_registration_str():
    registration = register([], make_event(), "a")
    assert "a@test.ru" in str(registration)
    assert "Семинар" in str(registration)


def test_cancel_method_changes_state_but_keeps_object():
    registrations: list[Registration] = []
    registration = register(registrations, make_event(), "a")
    registration.cancel()
    assert registration.status == "cancelled"
    assert not registration.is_active()
    assert registration in registrations


def test_third_participant_goes_to_waitlist():
    event, registrations = make_event(), []
    register(registrations, event, "a", 0)
    register(registrations, event, "b", 1)
    assert register(registrations, event, "c", 2).status == "waitlist"


def test_duplicate_email_rejected():
    event, registrations = make_event(), []
    register(registrations, event, "a")
    with pytest.raises(ValueError):
        register(registrations, event, "A")


def test_cancelled_participant_can_register_again():
    event, registrations = make_event(), []
    first = register(registrations, event, "a")
    cancel_registration(registrations, first.id)
    assert register(registrations, event, "a").status == "registered"


def test_cancel_promotes_first_from_waitlist():
    event, registrations = make_event(), []
    first = register(registrations, event, "a", 0)
    register(registrations, event, "b", 1)
    register(registrations, event, "c", 2)
    register(registrations, event, "d", 3)
    promoted = cancel_registration(registrations, first.id)
    assert promoted.participant == "c"
    assert promoted.status == "registered"
    assert count_registered(registrations, event) == 2


def test_cancel_unknown_registration_raises():
    with pytest.raises(KeyError):
        cancel_registration([], 42)


def test_registration_closed_after_start():
    with pytest.raises(ValueError):
        register_participant([], make_event(), "a", "a@test.ru",
                             datetime(2026, 10, 21))


def test_registration_status_texts():
    assert get_registration_status(True, 3, 5) == "Регистрация открыта"
    assert get_registration_status(False, 3, 5).startswith("Регистрация ещё")
    assert get_registration_status(True, 0, 5).startswith("Мест нет")
    assert get_registration_status(True, 3, -1) == "Мероприятие уже прошло"


def test_participants_listed_before_waitlist():
    event, registrations = make_event(1), []
    register(registrations, event, "a", 0)
    register(registrations, event, "b", 1)
    participants = get_event_participants(registrations, event)
    assert [r.participant for r in participants] == ["a", "b"]


def test_statistics():
    event, registrations = make_event(), []
    for index, name in enumerate("abc"):
        register(registrations, event, name, index)
    stats = get_statistics([event], registrations)
    assert stats["registered"] == 2
    assert stats["waitlist"] == 1
    assert stats["average_fill_percent"] == 100.0
    assert stats["most_popular_event"] is event


def test_statistics_without_events():
    stats = get_statistics([], [])
    assert stats["most_popular_event"] is None
    assert stats["average_fill_percent"] == 0
