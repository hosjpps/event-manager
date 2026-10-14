"""Класс Venue и функции работы с коллекцией площадок."""
from collections.abc import Iterator
from typing import Optional

from utils import next_id


class Venue:
    """Площадка организации: зал или аудитория с ограниченной вместимостью."""

    def __init__(
        self,
        venue_id: int,
        name: str,
        address: str,
        capacity: int
    ) -> None:
        """Создать объект площадки."""
        self.id = venue_id
        self.name = name
        self.address = address
        self.capacity = capacity

    def can_host(self, people_count: int) -> bool:
        """Вернуть True, если площадка вмещает указанное число людей."""
        return self.capacity >= people_count

    @staticmethod
    def validate_capacity(capacity: int) -> bool:
        """Проверить корректность вместимости: она должна быть больше нуля."""
        return capacity > 0

    @classmethod
    def from_data(cls, data: dict) -> "Venue":
        """Создать площадку из записи JSON."""
        return cls(
            data["id"], data["name"], data["address"], data["capacity"]
        )

    def __str__(self) -> str:
        """Вернуть название площадки и её вместимость."""
        return f"{self.name}, {self.capacity} мест"


def add_venue(
    venues: list[Venue],
    name: str,
    address: str,
    capacity: int
) -> Venue:
    """Создать площадку, добавить её в коллекцию и вернуть.

    Raises:
        ValueError: если вместимость не положительная или площадка
            с таким названием уже есть.
    """
    if not Venue.validate_capacity(capacity):
        raise ValueError("Вместимость площадки должна быть больше нуля")
    if find_venues(venues, name, exact=True):
        raise ValueError(f"Площадка «{name}» уже существует")
    venue = Venue(next_id(v.id for v in venues), name, address, capacity)
    venues.append(venue)
    return venue


def find_venues(
    venues: list[Venue],
    query: str,
    exact: bool = False
) -> list[Venue]:
    """Найти площадки по подстроке названия без учёта регистра."""
    query = query.lower()
    found = []
    for venue in venues:
        name = venue.name.lower()
        if (exact and name == query) or (not exact and query in name):
            found.append(venue)
    return found


def find_venue_by_id(venues: list[Venue], venue_id: int) -> Optional[Venue]:
    """Найти площадку по идентификатору; None, если её нет."""
    for venue in venues:
        if venue.id == venue_id:
            return venue
    return None


def filter_venues_by_capacity(
    venues: list[Venue],
    min_capacity: int
) -> Iterator[Venue]:
    """Вернуть генератор площадок вместимостью не меньше min_capacity."""
    return (v for v in venues if v.can_host(min_capacity))


def sort_venues(venues: list[Venue]) -> list[Venue]:
    """Вернуть площадки, упорядоченные по убыванию вместимости."""
    return sorted(venues, key=lambda v: v.capacity, reverse=True)
