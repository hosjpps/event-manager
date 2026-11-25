from django.db import models
from django.db.models import Q
from django.urls import reverse

from .slugs import make_slug


class Venue(models.Model):
    """Площадка организации: зал или аудитория с ограниченной вместимостью."""

    LARGE_CAPACITY = 100

    name = models.CharField("Название", max_length=200, unique=True)
    slug = models.SlugField(
        "URL-идентификатор",
        max_length=220,
        unique=True,
        editable=False,
        help_text="Формируется автоматически из названия и id.",
    )
    address = models.CharField("Адрес", max_length=255)
    capacity = models.PositiveIntegerField(
        "Вместимость, чел.",
        help_text="Сколько человек одновременно помещается на площадке.",
    )
    # Признак считает сама база данных при каждой записи.
    is_large = models.GeneratedField(
        expression=models.ExpressionWrapper(
            Q(capacity__gte=LARGE_CAPACITY),
            output_field=models.BooleanField(),
        ),
        output_field=models.BooleanField(),
        db_persist=True,
        verbose_name="Большой зал (от 100 мест)",
    )

    class Meta:
        ordering = ["name"]
        verbose_name = "Площадка"
        verbose_name_plural = "Площадки"

    def __str__(self):
        return self.name

    def save(self, *args, **kwargs):
        super().save(*args, **kwargs)
        # slug включает id, который появляется только после первой записи.
        if not self.slug:
            self.slug = make_slug(self.name, self.pk)
            super().save(update_fields=["slug"])

    def get_absolute_url(self):
        return reverse("venues:detail", kwargs={"slug": self.slug})

    def can_host(self, people_count):
        """Вернуть True, если площадка вмещает указанное число людей."""
        return self.capacity >= people_count
