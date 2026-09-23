import pytest

from venues import (add_venue, filter_venues_by_capacity, find_venues,
                    sort_venues)


def make_venues() -> dict[int, dict]:
    venues: dict[int, dict] = {}
    add_venue(venues, "Актовый зал", "пр. Вернадского, 78", 120)
    add_venue(venues, "Аудитория А-305", "пр. Вернадского, 78", 30)
    return venues


def test_add_venue_assigns_next_id():
    venues = make_venues()
    assert add_venue(venues, "Коворкинг", "ул. Стромынка, 20", 45) == 3


def test_add_venue_rejects_duplicate_name():
    venues = make_venues()
    with pytest.raises(ValueError):
        add_venue(venues, "актовый зал", "другой адрес", 50)


def test_find_venues_ignores_case():
    assert [v["id"] for v in find_venues(make_venues(), "АУДИТОРИЯ")] == [2]


def test_filter_venues_by_capacity():
    found = filter_venues_by_capacity(make_venues(), 50)
    assert [v["name"] for v in found] == ["Актовый зал"]


def test_sort_venues_by_capacity_desc():
    assert [v["id"] for v in sort_venues(make_venues())] == [1, 2]
