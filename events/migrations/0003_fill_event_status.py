from django.db import migrations
from django.utils import timezone


def fill_statuses(apps, schema_editor):
    # Правило проекта: мероприятие, закончившееся до применения миграции,
    # считается завершённым; остальные остаются запланированными.
    Event = apps.get_model("events", "Event")
    Event.objects.filter(ends_at__lt=timezone.now()).update(
        status="completed"
    )


def reset_statuses(apps, schema_editor):
    Event = apps.get_model("events", "Event")
    Event.objects.update(status="active")


class Migration(migrations.Migration):

    dependencies = [
        ("events", "0002_event_status"),
    ]

    operations = [
        migrations.RunPython(fill_statuses, reset_statuses),
    ]
