"""Сохранение и загрузка данных проекта в JSON-файлах."""
import json
from datetime import datetime
from pathlib import Path

from models import Event, Registration, Venue
from models.events import find_event_by_id
from models.venues import find_venue_by_id

DATA_DIR = Path(__file__).parent / "data"
VENUES_FILE = DATA_DIR / "venues.json"
EVENTS_FILE = DATA_DIR / "events.json"
REGISTRATIONS_FILE = DATA_DIR / "registrations.json"

DATETIME_FORMAT = "minutes"


def load_items(path: Path) -> list[dict]:
    """Прочитать список записей из JSON-файла.

    Отсутствующий файл считается пустым списком.

    Raises:
        ValueError: если файл повреждён или содержит не список.
    """
    try:
        with open(path, encoding="utf-8") as file:
            items = json.load(file)
    except FileNotFoundError:
        return []
    except json.JSONDecodeError as error:
        raise ValueError(f"Файл {path.name} повреждён: {error}") from error
    if not isinstance(items, list):
        raise ValueError(f"Файл {path.name} должен содержать список записей")
    return items


def save_items(path: Path, items: list[dict]) -> None:
    """Записать список записей в JSON-файл (каталог создаётся сам)."""
    path.parent.mkdir(parents=True, exist_ok=True)
    with open(path, "w", encoding="utf-8") as file:
        json.dump(items, file, ensure_ascii=False, indent=4)


def _format(value: datetime) -> str:
    """Вернуть дату и время в формате ISO 8601 с точностью до минут."""
    return value.isoformat(timespec=DATETIME_FORMAT)


def load_venues(path: Path = VENUES_FILE) -> list[Venue]:
    """Загрузить площадки: записи JSON превращаются в объекты Venue."""
    return [Venue.from_data(item) for item in load_items(path)]


def save_venues(venues: list[Venue], path: Path = VENUES_FILE) -> None:
    """Сохранить площадки: объекты Venue превращаются в записи JSON."""
    save_items(path, [
        {"id": v.id, "name": v.name, "address": v.address,
         "capacity": v.capacity}
        for v in venues
    ])


def load_events(
    venues: list[Venue],
    path: Path = EVENTS_FILE
) -> list[Event]:
    """Загрузить мероприятия, восстановив связь с объектами Venue.

    Raises:
        ValueError: если мероприятие ссылается на несуществующую площадку.
    """
    events = []
    for item in load_items(path):
        venue = find_venue_by_id(venues, item["venue_id"])
        if venue is None:
            raise ValueError(
                f"Мероприятие id={item['id']}: площадка "
                f"id={item['venue_id']} не найдена"
            )
        events.append(Event(
            item["id"], item["title"], venue,
            datetime.fromisoformat(item["starts_at"]),
            datetime.fromisoformat(item["ends_at"]),
            item["capacity"], item["is_published"],
        ))
    return events


def save_events(events: list[Event], path: Path = EVENTS_FILE) -> None:
    """Сохранить мероприятия: вместо объекта Venue пишется venue_id."""
    save_items(path, [
        {"id": e.id, "title": e.title, "venue_id": e.venue.id,
         "starts_at": _format(e.starts_at), "ends_at": _format(e.ends_at),
         "capacity": e.capacity, "is_published": e.is_published}
        for e in events
    ])


def load_registrations(
    events: list[Event],
    path: Path = REGISTRATIONS_FILE
) -> list[Registration]:
    """Загрузить регистрации, восстановив связь с объектами Event.

    Raises:
        ValueError: если регистрация ссылается на несуществующее
            мероприятие.
    """
    registrations = []
    for item in load_items(path):
        event = find_event_by_id(events, item["event_id"])
        if event is None:
            raise ValueError(
                f"Регистрация id={item['id']}: мероприятие "
                f"id={item['event_id']} не найдено"
            )
        registrations.append(Registration(
            item["id"], event, item["participant"], item["email"],
            datetime.fromisoformat(item["registered_at"]), item["status"],
        ))
    return registrations


def save_registrations(
    registrations: list[Registration],
    path: Path = REGISTRATIONS_FILE
) -> None:
    """Сохранить регистрации: вместо объекта Event пишется event_id."""
    save_items(path, [
        {"id": r.id, "event_id": r.event.id, "participant": r.participant,
         "email": r.email, "status": r.status,
         "registered_at": _format(r.registered_at)}
        for r in registrations
    ])
