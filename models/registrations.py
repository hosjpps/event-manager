"""Класс Registration и функции регистрации участников на мероприятия."""
from datetime import datetime
from typing import Optional

from utils import next_id

from .events import Event, get_free_seats

REGISTERED = "registered"
WAITLIST = "waitlist"
CANCELLED = "cancelled"
ACTIVE_STATUSES = (REGISTERED, WAITLIST)


class Registration:
    """Регистрация участника на мероприятие."""

    def __init__(
        self,
        registration_id: int,
        event: Event,
        participant: str,
        email: str,
        registered_at: datetime,
        status: str = REGISTERED
    ) -> None:
        """Создать объект регистрации, связанный с объектом Event."""
        self.id = registration_id
        self.event = event
        self.participant = participant
        self.email = email
        self.registered_at = registered_at
        self.status = status

    def is_active(self) -> bool:
        """Вернуть True, если регистрация не отменена."""
        return self.status in ACTIVE_STATUSES

    def cancel(self) -> None:
        """Отменить регистрацию; запись остаётся в коллекции."""
        self.status = CANCELLED

    def confirm(self) -> None:
        """Перевести регистрацию из листа ожидания в подтверждённую."""
        self.status = REGISTERED

    def __str__(self) -> str:
        """Вернуть участника, мероприятие и статус регистрации."""
        return (f"{self.participant} <{self.email}> — "
                f"{self.event.title} ({self.status})")


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


def count_registered(registrations: list[Registration], event: Event) -> int:
    """Вернуть число подтверждённых участников мероприятия."""
    return sum(
        1 for r in registrations
        if r.event.id == event.id and r.status == REGISTERED
    )


def register_participant(
    registrations: list[Registration],
    event: Event,
    participant: str,
    email: str,
    now: datetime
) -> Registration:
    """Зарегистрировать участника; при отсутствии мест — в лист ожидания.

    Raises:
        ValueError: если регистрация закрыта или участник
            с этим e-mail уже зарегистрирован.
    """
    if not event.is_registration_open(now):
        raise ValueError("Регистрация на это мероприятие закрыта")
    email = email.strip().lower()
    for r in registrations:
        if r.event.id == event.id and r.email == email and r.is_active():
            raise ValueError(f"Участник {email} уже зарегистрирован")

    free_seats = get_free_seats(
        event.capacity, count_registered(registrations, event)
    )
    registration = Registration(
        next_id(r.id for r in registrations),
        event,
        participant,
        email,
        now,
        REGISTERED if free_seats > 0 else WAITLIST,
    )
    registrations.append(registration)
    return registration


def cancel_registration(
    registrations: list[Registration],
    registration_id: int
) -> Optional[Registration]:
    """Отменить регистрацию.

    Если освободилось место, первый участник из листа ожидания
    становится зарегистрированным. Возвращает его регистрацию или None.

    Raises:
        KeyError: если активная регистрация не найдена.
    """
    for r in registrations:
        if r.id == registration_id and r.is_active():
            cancelled = r
            break
    else:
        raise KeyError(f"Активная регистрация id={registration_id} не найдена")

    was_registered = cancelled.status == REGISTERED
    cancelled.cancel()
    if not was_registered:
        return None

    waitlist = [
        r for r in registrations
        if r.event.id == cancelled.event.id and r.status == WAITLIST
    ]
    if not waitlist:
        return None
    promoted = min(waitlist, key=lambda r: r.registered_at)
    promoted.confirm()
    return promoted


def get_event_participants(
    registrations: list[Registration],
    event: Event
) -> list[Registration]:
    """Вернуть активные регистрации мероприятия: сначала участники."""
    active = [
        r for r in registrations if r.event.id == event.id and r.is_active()
    ]
    return sorted(
        active, key=lambda r: (r.status != REGISTERED, r.registered_at)
    )


def get_statistics(
    events: list[Event],
    registrations: list[Registration]
) -> dict:
    """Вернуть сводную статистику по мероприятиям и регистрациям."""
    registered = sum(1 for r in registrations if r.status == REGISTERED)
    waitlist = sum(1 for r in registrations if r.status == WAITLIST)
    fill_rates = {
        e.id: count_registered(registrations, e) / e.capacity for e in events
    }
    most_popular_id = max(fill_rates, key=fill_rates.get, default=None)
    average = sum(fill_rates.values()) / len(fill_rates) if fill_rates else 0
    return {
        "events": len(events),
        "registered": registered,
        "waitlist": waitlist,
        "average_fill_percent": round(average * 100, 1),
        "most_popular_event": next(
            (e for e in events if e.id == most_popular_id), None
        ),
    }
