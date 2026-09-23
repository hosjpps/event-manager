from datetime import datetime

import pytest

from storage import load_events, load_items, save_events


def test_missing_file_gives_empty_list(tmp_path):
    assert load_items(tmp_path / "absent.json") == []


def test_broken_json_raises_value_error(tmp_path):
    path = tmp_path / "broken.json"
    path.write_text("[{", encoding="utf-8")
    with pytest.raises(ValueError):
        load_items(path)


def test_events_round_trip(tmp_path):
    path = tmp_path / "events.json"
    events = {1: {"id": 1, "title": "Лекция", "venue_id": 1,
                  "starts_at": datetime(2026, 10, 15, 18),
                  "ends_at": datetime(2026, 10, 15, 19, 30),
                  "capacity": 100, "is_published": True}}
    save_events(events, path)
    assert load_events(path) == events
