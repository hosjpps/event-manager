"""Функции для регистрации участников на мероприятия."""
from datetime import datetime

from events import get_free_seats
from utils import next_id

ACTIVE_STATUSES = ("registered", "waitlist")


def get_registration_status(
    is_published: bool,
    free_seats: int,
    days_left: int
) -> str:
    """Вернуть текстовый статус регистрации на мероприятие."""
    if not is_published:
        return "Регистрация ещё не открыта"
    elif days_left < 0:
        return "Мероприятие уже прошло"
    elif free_seats > 0:
        return "Регистрация открыта"
    else:
        return "Мест нет, можно встать в лист ожидания"


def is_registration_open(event: dict, now: datetime) -> bool:
    """Вернуть True, если мероприятие опубликовано и ещё не началось."""
    return event["is_published"] and event["starts_at"] > now


def count_registered(registrations: list[dict], event_id: int) -> int:
    """Вернуть число подтверждённых участников мероприятия."""
    return sum(
        1 for r in registrations
        if r["event_id"] == event_id and r["status"] == "registered"
    )


def register_participant(
    registrations: list[dict],
    events: dict[int, dict],
    event_id: int,
    participant: str,
    email: str,
    now: datetime
) -> dict:
    """Зарегистрировать участника; при отсутствии мест — в лист ожидания.

    Raises:
        KeyError: если мероприятие не найдено.
        ValueError: если регистрация закрыта или участник
            с этим e-mail уже зарегистрирован.
    """
    if event_id not in events:
        raise KeyError(f"Мероприятие с id={event_id} не найдено")
    event = events[event_id]
    if not is_registration_open(event, now):
        raise ValueError("Регистрация на это мероприятие закрыта")
    email = email.strip().lower()
    for r in registrations:
        if (r["event_id"] == event_id and r["email"] == email
                and r["status"] in ACTIVE_STATUSES):
            raise ValueError(f"Участник {email} уже зарегистрирован")

    free_seats = get_free_seats(
        event["capacity"], count_registered(registrations, event_id)
    )
    registration = {
        "id": next_id(r["id"] for r in registrations),
        "event_id": event_id,
        "participant": participant,
        "email": email,
        "status": "registered" if free_seats > 0 else "waitlist",
        "registered_at": now,
    }
    registrations.append(registration)
    return registration


def cancel_registration(
    registrations: list[dict],
    registration_id: int
) -> dict | None:
    """Отменить регистрацию.

    Если освободилось место, первый участник из листа ожидания
    становится зарегистрированным. Возвращает его регистрацию или None.

    Raises:
        KeyError: если активная регистрация не найдена.
    """
    for r in registrations:
        if r["id"] == registration_id and r["status"] in ACTIVE_STATUSES:
            cancelled = r
            break
    else:
        raise KeyError(f"Активная регистрация id={registration_id} не найдена")

    was_registered = cancelled["status"] == "registered"
    cancelled["status"] = "cancelled"
    if not was_registered:
        return None

    waitlist = [
        r for r in registrations
        if r["event_id"] == cancelled["event_id"] and r["status"] == "waitlist"
    ]
    if not waitlist:
        return None
    promoted = min(waitlist, key=lambda r: r["registered_at"])
    promoted["status"] = "registered"
    return promoted


def get_event_participants(
    registrations: list[dict],
    event_id: int
) -> list[dict]:
    """Вернуть активные регистрации мероприятия: сначала участники."""
    active = [
        r for r in registrations
        if r["event_id"] == event_id and r["status"] in ACTIVE_STATUSES
    ]
    return sorted(
        active, key=lambda r: (r["status"] != "registered", r["registered_at"])
    )


def get_statistics(events: dict[int, dict], registrations: list[dict]) -> dict:
    """Вернуть сводную статистику по мероприятиям и регистрациям."""
    registered = sum(1 for r in registrations if r["status"] == "registered")
    waitlist = sum(1 for r in registrations if r["status"] == "waitlist")
    fill_rates = {
        event_id: count_registered(registrations, event_id) / e["capacity"]
        for event_id, e in events.items()
    }
    most_popular = max(fill_rates, key=fill_rates.get, default=None)
    average = sum(fill_rates.values()) / len(fill_rates) if fill_rates else 0
    return {
        "events": len(events),
        "registered": registered,
        "waitlist": waitlist,
        "average_fill_percent": round(average * 100, 1),
        "most_popular_event_id": most_popular,
    }
