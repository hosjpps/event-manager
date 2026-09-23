from datetime import date, datetime

import pytest

from events import (add_event, days_until_event, get_free_seats,
                    get_upcoming_events, is_venue_free)

VENUES = {1: {"id": 1, "name": "Актовый зал", "capacity": 100}}


def make_events() -> dict[int, dict]:
    events: dict[int, dict] = {}
    add_event(events, VENUES, "Лекция", 1, datetime(2026, 10, 15, 10),
              datetime(2026, 10, 15, 12), 80)
    return events


def test_get_free_seats_never_negative():
    assert get_free_seats(100, 97) == 3
    assert get_free_seats(100, 105) == 0


def test_days_until_event():
    assert days_until_event(date(2026, 10, 15), date(2026, 10, 1)) == 14


def test_venue_busy_when_intervals_overlap():
    events = make_events()
    assert not is_venue_free(events, 1, datetime(2026, 10, 15, 11),
                             datetime(2026, 10, 15, 13))


def test_venue_free_right_after_previous_event():
    events = make_events()
    assert is_venue_free(events, 1, datetime(2026, 10, 15, 12),
                         datetime(2026, 10, 15, 13))


def test_add_event_rejects_capacity_over_venue():
    with pytest.raises(ValueError):
        add_event({}, VENUES, "Конференция", 1, datetime(2026, 11, 1, 10),
                  datetime(2026, 11, 1, 18), 150)


def test_add_event_rejects_unknown_venue():
    with pytest.raises(KeyError):
        add_event({}, VENUES, "Лекция", 99, datetime(2026, 11, 1, 10),
                  datetime(2026, 11, 1, 12), 10)


def test_upcoming_events_skip_past_and_sorted():
    events = make_events()
    add_event(events, VENUES, "Семинар", 1, datetime(2026, 10, 10, 10),
              datetime(2026, 10, 10, 12), 20)
    upcoming = get_upcoming_events(events, datetime(2026, 10, 12))
    assert [e["title"] for e in upcoming] == ["Лекция"]
