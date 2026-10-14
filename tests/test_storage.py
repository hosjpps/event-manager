from datetime import datetime

import pytest

from models import Event, Registration, Venue
from storage import (load_events, load_items, load_registrations,
                     load_venues, save_events, save_registrations,
                     save_venues)

VENUE = Venue(1, "Актовый зал", "адрес", 120)
EVENT = Event(1, "Лекция", VENUE, datetime(2026, 10, 15, 18),
              datetime(2026, 10, 15, 19, 30), 100)


def test_missing_file_gives_empty_list(tmp_path):
    assert load_items(tmp_path / "absent.json") == []


def test_broken_json_raises_value_error(tmp_path):
    path = tmp_path / "broken.json"
    path.write_text("[{", encoding="utf-8")
    with pytest.raises(ValueError):
        load_items(path)


def test_venues_round_trip(tmp_path):
    path = tmp_path / "venues.json"
    save_venues([VENUE], path)
    loaded = load_venues(path)
    assert isinstance(loaded[0], Venue)
    assert vars(loaded[0]) == vars(VENUE)


def test_events_round_trip_restores_venue_object(tmp_path):
    path = tmp_path / "events.json"
    save_events([EVENT], path)
    loaded = load_events([VENUE], path)
    assert loaded[0].venue is VENUE
    assert vars(loaded[0]) == vars(EVENT)


def test_events_file_stores_ids_not_objects(tmp_path):
    path = tmp_path / "events.json"
    save_events([EVENT], path)
    assert load_items(path)[0]["venue_id"] == 1


def test_registrations_round_trip_restores_event_object(tmp_path):
    path = tmp_path / "registrations.json"
    registration = Registration(1, EVENT, "Иван", "i@test.ru",
                                datetime(2026, 9, 20, 10, 15), "waitlist")
    save_registrations([registration], path)
    loaded = load_registrations([EVENT], path)
    assert loaded[0].event is EVENT
    assert vars(loaded[0]) == vars(registration)


def test_event_with_unknown_venue_is_rejected(tmp_path):
    path = tmp_path / "events.json"
    save_events([EVENT], path)
    with pytest.raises(ValueError):
        load_events([], path)


def test_registration_with_unknown_event_is_rejected(tmp_path):
    path = tmp_path / "registrations.json"
    registration = Registration(1, EVENT, "Иван", "i@test.ru",
                                datetime(2026, 9, 20, 10, 15))
    save_registrations([registration], path)
    with pytest.raises(ValueError):
        load_registrations([], path)


def test_project_data_files_load_as_objects():
    venues = load_venues()
    events = load_events(venues)
    registrations = load_registrations(events)
    assert venues and events and registrations
