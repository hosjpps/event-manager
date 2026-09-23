from datetime import datetime

import pytest

from registrations import (cancel_registration, get_registration_status,
                           get_statistics, is_registration_open,
                           register_participant)

NOW = datetime(2026, 10, 1, 12)


def make_events() -> dict[int, dict]:
    return {1: {"id": 1, "title": "Семинар", "capacity": 2,
                "is_published": True,
                "starts_at": datetime(2026, 10, 20, 14)}}


def register(registrations, events, name, minute=0):
    return register_participant(
        registrations, events, 1, name, f"{name}@test.ru",
        NOW.replace(minute=minute),
    )


def test_third_participant_goes_to_waitlist():
    events, registrations = make_events(), []
    register(registrations, events, "a", 0)
    register(registrations, events, "b", 1)
    assert register(registrations, events, "c", 2)["status"] == "waitlist"


def test_duplicate_email_rejected():
    events, registrations = make_events(), []
    register(registrations, events, "a")
    with pytest.raises(ValueError):
        register(registrations, events, "A")


def test_cancel_promotes_first_from_waitlist():
    events, registrations = make_events(), []
    first = register(registrations, events, "a", 0)
    register(registrations, events, "b", 1)
    register(registrations, events, "c", 2)
    register(registrations, events, "d", 3)
    promoted = cancel_registration(registrations, first["id"])
    assert promoted["participant"] == "c"
    assert promoted["status"] == "registered"


def test_cancel_unknown_registration_raises():
    with pytest.raises(KeyError):
        cancel_registration([], 42)


def test_registration_closed_after_start():
    events = make_events()
    with pytest.raises(ValueError):
        register_participant([], events, 1, "a", "a@test.ru",
                             datetime(2026, 10, 21))


def test_registration_status_texts():
    assert get_registration_status(True, 3, 5) == "Регистрация открыта"
    assert get_registration_status(False, 3, 5).startswith("Регистрация ещё")
    assert get_registration_status(True, 0, 5).startswith("Мест нет")


def test_statistics():
    events, registrations = make_events(), []
    for index, name in enumerate("abc"):
        register(registrations, events, name, index)
    stats = get_statistics(events, registrations)
    assert stats["registered"] == 2
    assert stats["waitlist"] == 1
    assert stats["average_fill_percent"] == 100.0


def test_registration_open_until_event_start():
    event = make_events()[1]
    assert is_registration_open(event, datetime(2026, 10, 20, 13, 59))
    assert not is_registration_open(event, datetime(2026, 10, 20, 14, 0))
