import pytest

from models import Venue
from models.venues import (add_venue, filter_venues_by_capacity, find_venues,
                           find_venue_by_id, sort_venues)


def make_venues() -> list[Venue]:
    venues: list[Venue] = []
    add_venue(venues, "Актовый зал", "пр. Вернадского, 78", 120)
    add_venue(venues, "Аудитория А-305", "пр. Вернадского, 78", 30)
    return venues


def test_venue_creation():
    venue = Venue(1, "Актовый зал", "пр. Вернадского, 78", 120)
    assert venue.id == 1
    assert venue.name == "Актовый зал"
    assert venue.address == "пр. Вернадского, 78"
    assert venue.capacity == 120


def test_venue_str():
    venue = Venue(1, "Актовый зал", "адрес", 120)
    assert str(venue) == "Актовый зал, 120 мест"


def test_venue_can_host():
    venue = Venue(1, "Актовый зал", "адрес", 120)
    assert venue.can_host(100)
    assert venue.can_host(120)
    assert not venue.can_host(121)


def test_validate_capacity_static_method():
    assert Venue.validate_capacity(1)
    assert not Venue.validate_capacity(0)


def test_venue_from_data():
    venue = Venue.from_data(
        {"id": 7, "name": "Зал", "address": "адрес", "capacity": 50}
    )
    assert (venue.id, venue.name, venue.capacity) == (7, "Зал", 50)


def test_add_venue_returns_object_with_next_id():
    venues = make_venues()
    venue = add_venue(venues, "Коворкинг", "ул. Стромынка, 20", 45)
    assert venue.id == 3
    assert venues[-1] is venue


def test_add_venue_rejects_duplicate_name():
    venues = make_venues()
    with pytest.raises(ValueError):
        add_venue(venues, "актовый зал", "другой адрес", 50)


def test_add_venue_rejects_bad_capacity():
    with pytest.raises(ValueError):
        add_venue([], "Зал", "адрес", 0)


def test_find_venues_ignores_case():
    assert [v.id for v in find_venues(make_venues(), "АУДИТОРИЯ")] == [2]


def test_find_venue_by_id():
    venues = make_venues()
    assert find_venue_by_id(venues, 2) is venues[1]
    assert find_venue_by_id(venues, 99) is None


def test_filter_venues_by_capacity():
    found = filter_venues_by_capacity(make_venues(), 50)
    assert [v.name for v in found] == ["Актовый зал"]


def test_sort_venues_by_capacity_desc():
    assert [v.id for v in sort_venues(make_venues())] == [1, 2]
