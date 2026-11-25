from django.db import models
from django.utils import timezone

from venues.models import Venue


class Event(models.Model):
    """Мероприятие, которое проходит на площадке."""

    title = models.CharField("Название", max_length=200)
    venue = models.ForeignKey(
        Venue,
        on_delete=models.PROTECT,
        related_name="events",
        verbose_name="Площадка",
    )
    starts_at = models.DateTimeField("Начало")
    ends_at = models.DateTimeField("Окончание")
    capacity = models.PositiveIntegerField("Число мест")
    is_published = models.BooleanField("Регистрация открыта", default=True)

    class Meta:
        ordering = ["starts_at", "pk"]
        verbose_name = "Мероприятие"
        verbose_name_plural = "Мероприятия"

    def __str__(self):
        return f"{self.title} ({self.venue})"

    def is_registration_open(self):
        """Вернуть True, если мероприятие опубликовано и ещё не началось."""
        return self.is_published and self.starts_at > timezone.now()
