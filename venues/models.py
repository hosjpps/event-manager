from django.db import models


class Venue(models.Model):
    """Площадка организации: зал или аудитория с ограниченной вместимостью."""

    name = models.CharField("Название", max_length=200, unique=True)
    address = models.CharField("Адрес", max_length=255)
    capacity = models.PositiveIntegerField("Вместимость, чел.")

    class Meta:
        ordering = ["name"]
        verbose_name = "Площадка"
        verbose_name_plural = "Площадки"

    def __str__(self):
        return self.name

    def can_host(self, people_count):
        """Вернуть True, если площадка вмещает указанное число людей."""
        return self.capacity >= people_count
