from django.db import models
from django.utils import timezone

from events.models import Event


class Registration(models.Model):
    """Регистрация участника на мероприятие."""

    class Status(models.TextChoices):
        REGISTERED = "registered", "Участник"
        WAITLIST = "waitlist", "Лист ожидания"
        CANCELLED = "cancelled", "Отменена"

    event = models.ForeignKey(
        Event,
        on_delete=models.CASCADE,
        related_name="registrations",
        verbose_name="Мероприятие",
    )
    participant = models.CharField("Участник", max_length=200)
    email = models.EmailField("E-mail")
    status = models.CharField(
        "Статус",
        max_length=20,
        choices=Status.choices,
        default=Status.REGISTERED,
    )
    registered_at = models.DateTimeField(
        "Дата регистрации", default=timezone.now
    )

    class Meta:
        ordering = ["registered_at", "pk"]
        verbose_name = "Регистрация"
        verbose_name_plural = "Регистрации"

    def __str__(self):
        return f"{self.participant} — {self.event.title}"

    def cancel(self):
        """Отменить регистрацию, сохранив только изменённое поле."""
        self.status = self.Status.CANCELLED
        self.save(update_fields=["status"])
