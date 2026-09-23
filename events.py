"""Функции для работы с мероприятиями."""
from collections.abc import Iterator
from datetime import date, datetime

from utils import next_id


def check_event_fits_venue(event_capacity: int, venue_capacity: int) -> bool:
    """Вернуть True, если площадка вмещает всех участников мероприятия."""
    return event_capacity <= venue_capacity


def get_free_seats(event_capacity: int, registered_count: int) -> int:
    """Вернуть число свободных мест (не меньше нуля)."""
    free_seats = event_capacity - registered_count
    if free_seats < 0:
        return 0
    return free_seats


def days_until_event(event_date: date, today: date) -> int:
    """Вернуть количество дней до начала мероприятия."""
    return (event_date - today).days


def is_venue_free(
    events: dict[int, dict],
    venue_id: int,
    starts_at: datetime,
    ends_at: datetime
) -> bool:
    """Проверить, что площадка свободна в интервале [starts_at, ends_at).

    Мероприятия пересекаются, если одно начинается раньше, чем закончится
    другое. Мероприятие, начинающееся ровно в момент окончания другого,
    допускается.
    """
    for event in events.values():
        if event["venue_id"] != venue_id:
            continue
        if starts_at < event["ends_at"] and event["starts_at"] < ends_at:
            return False
    return True


def add_event(
    events: dict[int, dict],
    venues: dict[int, dict],
    title: str,
    venue_id: int,
    starts_at: datetime,
    ends_at: datetime,
    capacity: int
) -> int:
    """Добавить мероприятие и вернуть его идентификатор.

    Raises:
        KeyError: если площадка не найдена.
        ValueError: если время или число мест заданы неверно,
            либо площадка занята в это время.
    """
    if venue_id not in venues:
        raise KeyError(f"Площадка с id={venue_id} не найдена")
    if starts_at >= ends_at:
        raise ValueError("Время окончания должно быть позже времени начала")
    if capacity <= 0:
        raise ValueError("Число мест должно быть больше нуля")
    venue = venues[venue_id]
    if not check_event_fits_venue(capacity, venue["capacity"]):
        raise ValueError(
            f"Площадка «{venue['name']}» вмещает только "
            f"{venue['capacity']} чел."
        )
    if not is_venue_free(events, venue_id, starts_at, ends_at):
        raise ValueError(f"Площадка «{venue['name']}» занята в это время")
    event_id = next_id(events)
    events[event_id] = {
        "id": event_id,
        "title": title,
        "venue_id": venue_id,
        "starts_at": starts_at,
        "ends_at": ends_at,
        "capacity": capacity,
        "is_published": True,
    }
    return event_id


def find_events(events: dict[int, dict], query: str) -> list[dict]:
    """Найти мероприятия по подстроке названия без учёта регистра."""
    query = query.lower()
    return [e for e in events.values() if query in e["title"].lower()]


def sort_events_by_date(events: dict[int, dict]) -> list[dict]:
    """Вернуть мероприятия, упорядоченные по времени начала."""
    return sorted(events.values(), key=lambda e: e["starts_at"])


def get_upcoming_events(
    events: dict[int, dict],
    now: datetime
) -> Iterator[dict]:
    """Вернуть генератор ещё не начавшихся мероприятий в порядке дат."""
    for event in sort_events_by_date(events):
        if event["starts_at"] >= now:
            yield event
