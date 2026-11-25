"""Перенос данных из базы ПР7 (data/event_manager.sqlite) в модели Django.

Исходная база только читается. Идентификаторы сохраняются, поэтому связи
между площадками, мероприятиями и регистрациями не теряются. Повторный
запуск обновляет записи, а не создаёт дубликаты.
"""
import os
import sqlite3
import sys
from datetime import datetime
from pathlib import Path

import django
from django.db import transaction
from django.utils import timezone

BASE_DIR = Path(__file__).resolve().parent.parent
SOURCE_DB = BASE_DIR / "data" / "event_manager.sqlite"

sys.path.insert(0, str(BASE_DIR))
os.environ.setdefault("DJANGO_SETTINGS_MODULE", "eventmanager.settings")
django.setup()

from events.models import Event  # noqa: E402
from registrations.models import Registration  # noqa: E402
from venues.models import Venue  # noqa: E402


def aware(text: str) -> datetime:
    """Строку ISO из базы ПР7 превратить в дату-время с часовым поясом."""
    return timezone.make_aware(datetime.fromisoformat(text))


def main() -> None:
    if not SOURCE_DB.exists():
        raise FileNotFoundError(f"Исходная база не найдена: {SOURCE_DB}")
    with sqlite3.connect(SOURCE_DB) as connection:
        connection.row_factory = sqlite3.Row
        venues = connection.execute(
            "SELECT * FROM venues ORDER BY id").fetchall()
        events = connection.execute(
            "SELECT * FROM events ORDER BY id").fetchall()
        registrations = connection.execute(
            "SELECT * FROM registrations ORDER BY id").fetchall()

    # Сначала независимые записи, потом те, что на них ссылаются.
    with transaction.atomic():
        for row in venues:
            Venue.objects.update_or_create(
                pk=row["id"],
                defaults={
                    "name": row["name"],
                    "address": row["address"],
                    "capacity": row["capacity"],
                },
            )
        for row in events:
            ends_at = aware(row["ends_at"])
            # То же правило, что в миграции events.0003: прошедшее —
            # завершено, остальное — запланировано.
            status = (Event.Status.COMPLETED if ends_at < timezone.now()
                      else Event.Status.ACTIVE)
            Event.objects.update_or_create(
                pk=row["id"],
                defaults={
                    "status": status,
                    "title": row["title"],
                    "venue_id": row["venue_id"],
                    "starts_at": aware(row["starts_at"]),
                    "ends_at": ends_at,
                    "capacity": row["capacity"],
                    "is_published": bool(row["is_published"]),
                },
            )
        for row in registrations:
            Registration.objects.update_or_create(
                pk=row["id"],
                defaults={
                    "event_id": row["event_id"],
                    "participant": row["participant"],
                    "email": row["email"],
                    "status": row["status"],
                    "registered_at": aware(row["registered_at"]),
                },
            )

    print("Перенос завершён:")
    print(f"  площадок: {Venue.objects.count()}")
    print(f"  мероприятий: {Event.objects.count()}")
    print(f"  регистраций: {Registration.objects.count()}")


if __name__ == "__main__":
    main()
