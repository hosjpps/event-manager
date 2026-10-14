"""Класс Event и функции работы с коллекцией мероприятий."""
from collections.abc import Iterator
from datetime import date, datetime
from typing import Optional

from utils import format_datetime, next_id

from .venues import Venue


class Event:
    """Мероприятие, которое проходит на конкретной площадке."""

    def __init__(
        self,
        event_id: int,
        title: str,
        venue: Venue,
        starts_at: datetime,
        ends_at: datetime,
        capacity: int,
        is_published: bool = True
    ) -> None:
        """Создать объект мероприятия, связанный с объектом Venue."""
        self.id = event_id
        self.title = title
        self.venue = venue
        self.starts_at = starts_at
        self.ends_at = ends_at
        self.capacity = capacity
        self.is_published = is_published

    def fits_venue(self) -> bool:
        """Вернуть True, если площадка вмещает всех участников."""
        return self.venue.can_host(self.capacity)

    def overlaps(self, starts_at: datetime, ends_at: datetime) -> bool:
        """Вернуть True, если мероприятие пересекается с интервалом.

        Мероприятия пересекаются, если одно начинается раньше, чем
        закончится другое; начало ровно в момент окончания допускается.
        """
        return starts_at < self.ends_at and self.starts_at < ends_at

    def days_until(self, today: date) -> int:
        """Вернуть количество дней до начала мероприятия."""
        return (self.starts_at.date() - today).days

    def is_registration_open(self, now: datetime) -> bool:
        """Вернуть True, если мероприятие опубликовано и ещё не началось."""
        return self.is_published and self.starts_at > now

    def __str__(self) -> str:
        """Вернуть время, название и площадку мероприятия."""
        return (f"{format_datetime(self.starts_at)}  {self.title} — "
                f"{self.venue.name}")


def get_free_seats(event_capacity: int, registered_count: int) -> int:
    """Вернуть число свободных мест (не меньше нуля)."""
    free_seats = event_capacity - registered_count
    if free_seats < 0:
        return 0
    return free_seats


def is_venue_free(
    events: list[Event],
    venue: Venue,
    starts_at: datetime,
    ends_at: datetime
) -> bool:
    """Проверить, что площадка свободна в интервале [starts_at, ends_at)."""
    for event in events:
        if event.venue.id == venue.id and event.overlaps(starts_at, ends_at):
            return False
    return True


def add_event(
    events: list[Event],
    venue: Venue,
    title: str,
    starts_at: datetime,
    ends_at: datetime,
    capacity: int
) -> Event:
    """Создать мероприятие, добавить его в коллекцию и вернуть.

    Raises:
        ValueError: если время или число мест заданы неверно,
            либо площадка занята в это время.
    """
    if starts_at >= ends_at:
        raise ValueError("Время окончания должно быть позже времени начала")
    if capacity <= 0:
        raise ValueError("Число мест должно быть больше нуля")
    if not venue.can_host(capacity):
        raise ValueError(
            f"Площадка «{venue.name}» вмещает только {venue.capacity} чел."
        )
    if not is_venue_free(events, venue, starts_at, ends_at):
        raise ValueError(f"Площадка «{venue.name}» занята в это время")
    event = Event(
        next_id(e.id for e in events), title, venue, starts_at, ends_at,
        capacity,
    )
    events.append(event)
    return event


def find_events(events: list[Event], query: str) -> list[Event]:
    """Найти мероприятия по подстроке названия без учёта регистра."""
    query = query.lower()
    return [e for e in events if query in e.title.lower()]


def find_event_by_id(events: list[Event], event_id: int) -> Optional[Event]:
    """Найти мероприятие по идентификатору; None, если его нет."""
    for event in events:
        if event.id == event_id:
            return event
    return None


def sort_events_by_date(events: list[Event]) -> list[Event]:
    """Вернуть мероприятия, упорядоченные по времени начала."""
    return sorted(events, key=lambda e: e.starts_at)


def get_upcoming_events(
    events: list[Event],
    now: datetime
) -> Iterator[Event]:
    """Вернуть генератор ещё не начавшихся мероприятий в порядке дат."""
    for event in sort_events_by_date(events):
        if event.starts_at >= now:
            yield event
