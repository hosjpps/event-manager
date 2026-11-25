from django.db import models

from events.models import Event


class Registration(models.Model):
    """Регистрация участника на мероприятие."""

    STATUS_CHOICES = [
        ("registered", "участник"),
        ("waitlist", "лист ожидания"),
        ("cancelled", "отменена"),
    ]

    event = models.ForeignKey(
        Event,
        on_delete=models.CASCADE,
        related_name="registrations",
        verbose_name="Мероприятие",
    )
    participant = models.CharField("Участник", max_length=200)
    email = models.EmailField("E-mail")
    status = models.CharField(
        "Статус", max_length=20, choices=STATUS_CHOICES, default="registered"
    )
    registered_at = models.DateTimeField("Дата регистрации")

    class Meta:
        ordering = ["registered_at", "pk"]
        verbose_name = "Регистрация"
        verbose_name_plural = "Регистрации"

    def __str__(self):
        return f"{self.participant} — {self.event.title}"

    def cancel(self):
        """Отменить регистрацию, сохранив только изменённое поле."""
        self.status = "cancelled"
        self.save(update_fields=["status"])
