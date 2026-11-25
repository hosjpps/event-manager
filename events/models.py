from django.db import models
from django.utils import timezone

from venues.models import Venue


class EventQuerySet(models.QuerySet):
    """Готовые выборки мероприятий для представлений и админки."""

    def active(self):
        return self.filter(status=self.model.Status.ACTIVE)

    def cancelled(self):
        return self.filter(status=self.model.Status.CANCELLED)

    def completed(self):
        return self.filter(status=self.model.Status.COMPLETED)

    def for_date(self, selected_date):
        return self.filter(starts_at__date=selected_date)

    def upcoming(self):
        return self.filter(starts_at__gte=timezone.now())


class EventManager(models.Manager.from_queryset(EventQuerySet)):
    pass


class Event(models.Model):
    """Мероприятие, которое проходит на площадке."""

    class Status(models.TextChoices):
        ACTIVE = "active", "Запланировано"
        CANCELLED = "cancelled", "Отменено"
        COMPLETED = "completed", "Завершено"

    title = models.CharField("Название", max_length=200)
    venue = models.ForeignKey(
        Venue,
        on_delete=models.PROTECT,
        related_name="events",
        verbose_name="Площадка",
    )
    starts_at = models.DateTimeField("Начало")
    ends_at = models.DateTimeField("Окончание")
    capacity = models.PositiveIntegerField(
        "Число мест",
        help_text="Не больше вместимости площадки.",
    )
    is_published = models.BooleanField(
        "Регистрация открыта",
        default=True,
        help_text="Снимите флажок, чтобы закрыть запись на мероприятие.",
    )
    status = models.CharField(
        "Статус",
        max_length=20,
        choices=Status.choices,
        default=Status.ACTIVE,
        help_text="Только запланированные мероприятия занимают площадку.",
    )

    objects = EventManager()

    class Meta:
        ordering = ["starts_at", "pk"]
        verbose_name = "Мероприятие"
        verbose_name_plural = "Мероприятия"

    def __str__(self):
        return f"{self.title} ({self.venue})"

    def is_registration_open(self):
        """Регистрация открыта: запланировано, опубликовано и не началось."""
        return (
            self.status == self.Status.ACTIVE
            and self.is_published
            and self.starts_at > timezone.now()
        )
