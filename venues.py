"""Функции для работы с площадками организации."""
from collections.abc import Iterator

from utils import next_id


def add_venue(
    venues: dict[int, dict],
    name: str,
    address: str,
    capacity: int
) -> int:
    """Добавить площадку в словарь venues и вернуть её идентификатор.

    Raises:
        ValueError: если вместимость не положительная или площадка
            с таким названием уже есть.
    """
    if capacity <= 0:
        raise ValueError("Вместимость площадки должна быть больше нуля")
    if find_venues(venues, name, exact=True):
        raise ValueError(f"Площадка «{name}» уже существует")
    venue_id = next_id(venues)
    venues[venue_id] = {
        "id": venue_id,
        "name": name,
        "address": address,
        "capacity": capacity,
    }
    return venue_id


def find_venues(
    venues: dict[int, dict],
    query: str,
    exact: bool = False
) -> list[dict]:
    """Найти площадки по подстроке названия без учёта регистра."""
    query = query.lower()
    found = []
    for venue in venues.values():
        name = venue["name"].lower()
        if (exact and name == query) or (not exact and query in name):
            found.append(venue)
    return found


def filter_venues_by_capacity(
    venues: dict[int, dict],
    min_capacity: int
) -> Iterator[dict]:
    """Вернуть генератор площадок вместимостью не меньше min_capacity."""
    return (v for v in venues.values() if v["capacity"] >= min_capacity)


def sort_venues(venues: dict[int, dict]) -> list[dict]:
    """Вернуть площадки, упорядоченные по убыванию вместимости."""
    return sorted(venues.values(), key=lambda v: v["capacity"], reverse=True)
