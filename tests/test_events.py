from datetime import date, datetime

import pytest

from models import Event, Venue
from models.events import (add_event, find_event_by_id, find_events,
                           get_free_seats, get_upcoming_events, is_venue_free)

VENUE = Venue(1, "Актовый зал", "адрес", 100)


def make_events() -> list[Event]:
    events: list[Event] = []
    add_event(events, VENUE, "Лекция", datetime(2026, 10, 15, 10),
              datetime(2026, 10, 15, 12), 80)
    return events


def test_event_keeps_link_to_venue():
    event = make_events()[0]
    assert event.venue is VENUE
    assert event.venue.name == "Актовый зал"
    assert event.capacity == 80


def test_event_str_contains_title_and_venue():
    text = str(make_events()[0])
    assert "Лекция" in text and "Актовый зал" in text


def test_event_fits_venue():
    start, end = datetime(2026, 10, 15, 10), datetime(2026, 10, 15, 12)
    assert Event(1, "A", VENUE, start, end, 100).fits_venue()
    assert not Event(1, "A", VENUE, start, end, 101).fits_venue()


def test_get_free_seats_never_negative():
    assert get_free_seats(100, 97) == 3
    assert get_free_seats(100, 105) == 0


def test_days_until_event():
    event = make_events()[0]
    assert event.days_until(date(2026, 10, 1)) == 14


def test_registration_open_until_event_start():
    event = make_events()[0]
    assert event.is_registration_open(datetime(2026, 10, 15, 9, 59))
    assert not event.is_registration_open(datetime(2026, 10, 15, 10, 0))


def test_unpublished_event_is_closed():
    event = Event(1, "A", VENUE, datetime(2026, 10, 15, 10),
                  datetime(2026, 10, 15, 12), 10, is_published=False)
    assert not event.is_registration_open(datetime(2026, 10, 1))


def test_venue_busy_when_intervals_overlap():
    events = make_events()
    assert not is_venue_free(events, VENUE, datetime(2026, 10, 15, 11),
                             datetime(2026, 10, 15, 13))


def test_venue_free_right_after_previous_event():
    events = make_events()
    assert is_venue_free(events, VENUE, datetime(2026, 10, 15, 12),
                         datetime(2026, 10, 15, 13))


def test_other_venue_is_not_blocked():
    other = Venue(2, "Аудитория", "адрес", 50)
    assert is_venue_free(make_events(), other, datetime(2026, 10, 15, 10),
                         datetime(2026, 10, 15, 12))


def test_add_event_rejects_capacity_over_venue():
    with pytest.raises(ValueError):
        add_event([], VENUE, "Конференция", datetime(2026, 11, 1, 10),
                  datetime(2026, 11, 1, 18), 150)


def test_add_event_rejects_end_before_start():
    with pytest.raises(ValueError):
        add_event([], VENUE, "Лекция", datetime(2026, 11, 1, 12),
                  datetime(2026, 11, 1, 10), 10)


def test_add_event_rejects_busy_venue():
    events = make_events()
    with pytest.raises(ValueError):
        add_event(events, VENUE, "Семинар", datetime(2026, 10, 15, 11),
                  datetime(2026, 10, 15, 13), 10)
    assert len(events) == 1


def test_find_event_by_id():
    events = make_events()
    assert find_event_by_id(events, 1) is events[0]
    assert find_event_by_id(events, 99) is None


def test_find_events_ignores_case():
    assert [e.id for e in find_events(make_events(), "ЛЕК")] == [1]


def test_upcoming_events_skip_past_and_sorted():
    events = make_events()
    add_event(events, VENUE, "Семинар", datetime(2026, 10, 10, 10),
              datetime(2026, 10, 10, 12), 20)
    upcoming = get_upcoming_events(events, datetime(2026, 10, 12))
    assert [e.title for e in upcoming] == ["Лекция"]
