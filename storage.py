"""Сохранение и загрузка данных проекта в JSON-файлах."""
import json
from datetime import datetime
from pathlib import Path

DATA_DIR = Path(__file__).parent / "data"
VENUES_FILE = DATA_DIR / "venues.json"
EVENTS_FILE = DATA_DIR / "events.json"
REGISTRATIONS_FILE = DATA_DIR / "registrations.json"

EVENT_DATETIME_FIELDS = ("starts_at", "ends_at")
REGISTRATION_DATETIME_FIELDS = ("registered_at",)


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


def _decode_dates(item: dict, fields: tuple[str, ...]) -> dict:
    """Вернуть копию записи, где строки ISO в полях fields стали datetime."""
    return {
        key: datetime.fromisoformat(value) if key in fields else value
        for key, value in item.items()
    }


def _encode_dates(item: dict, fields: tuple[str, ...]) -> dict:
    """Вернуть копию записи, где datetime в полях fields стали строками ISO."""
    return {
        key: value.isoformat(timespec="minutes") if key in fields else value
        for key, value in item.items()
    }


def load_venues(path: Path = VENUES_FILE) -> dict[int, dict]:
    """Загрузить площадки в словарь {id: площадка}."""
    return {venue["id"]: venue for venue in load_items(path)}


def save_venues(venues: dict[int, dict], path: Path = VENUES_FILE) -> None:
    """Сохранить площадки."""
    save_items(path, list(venues.values()))


def load_events(path: Path = EVENTS_FILE) -> dict[int, dict]:
    """Загрузить мероприятия в словарь {id: мероприятие}."""
    return {
        item["id"]: _decode_dates(item, EVENT_DATETIME_FIELDS)
        for item in load_items(path)
    }


def save_events(events: dict[int, dict], path: Path = EVENTS_FILE) -> None:
    """Сохранить мероприятия."""
    save_items(
        path,
        [_encode_dates(e, EVENT_DATETIME_FIELDS) for e in events.values()],
    )


def load_registrations(path: Path = REGISTRATIONS_FILE) -> list[dict]:
    """Загрузить регистрации в список."""
    return [
        _decode_dates(item, REGISTRATION_DATETIME_FIELDS)
        for item in load_items(path)
    ]


def save_registrations(
    registrations: list[dict],
    path: Path = REGISTRATIONS_FILE
) -> None:
    """Сохранить регистрации."""
    save_items(
        path,
        [_encode_dates(r, REGISTRATION_DATETIME_FIELDS)
         for r in registrations],
    )
