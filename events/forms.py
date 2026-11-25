from django import forms
from django.core.exceptions import ValidationError
from django.utils import timezone

from venues.models import Venue

from .models import Event

DATETIME_WIDGET = forms.DateTimeInput(
    attrs={"type": "datetime-local", "class": "form-control"},
    format="%Y-%m-%dT%H:%M",
)


class EventFilterForm(forms.Form):
    """Фильтр списка мероприятий; значения приходят из GET-параметров."""

    date = forms.DateField(
        required=False,
        label="Дата",
        widget=forms.DateInput(attrs={"type": "date"}),
    )
    venue = forms.ModelChoiceField(
        queryset=Venue.objects.order_by("name"),
        required=False,
        label="Площадка",
        empty_label="Все площадки",
    )
    status = forms.ChoiceField(
        required=False,
        label="Статус",
        choices=Event.Status.choices + [("all", "Все")],
    )
    q = forms.CharField(
        required=False,
        label="Название",
        max_length=100,
        widget=forms.TextInput(attrs={"placeholder": "поиск"}),
    )
    sort = forms.ChoiceField(
        required=False,
        label="Сортировка",
        choices=[
            ("date", "по дате"),
            ("title", "по названию"),
            ("venue", "по площадке"),
        ],
    )

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        for field in self.fields.values():
            is_select = isinstance(field.widget, forms.Select)
            field.widget.attrs["class"] = (
                "form-select" if is_select else "form-control")

    def clean_q(self):
        query = self.cleaned_data["q"].strip()
        if len(query) == 1:
            raise ValidationError("Введите хотя бы два символа.")
        return query


class EventForm(forms.ModelForm):
    """Создание и редактирование мероприятия с проверкой правил проекта."""

    class Meta:
        model = Event
        fields = ["title", "venue", "starts_at", "ends_at", "capacity",
                  "is_published"]
        widgets = {
            "title": forms.TextInput(attrs={"class": "form-control"}),
            "venue": forms.Select(attrs={"class": "form-select"}),
            "starts_at": DATETIME_WIDGET,
            "ends_at": DATETIME_WIDGET,
            "capacity": forms.NumberInput(attrs={"class": "form-control"}),
        }

    def clean_starts_at(self):
        starts_at = self.cleaned_data["starts_at"]
        if starts_at < timezone.now():
            raise ValidationError(
                "Нельзя назначить мероприятие на прошедшее время.")
        return starts_at

    def clean(self):
        cleaned_data = super().clean()
        venue = cleaned_data.get("venue")
        starts_at = cleaned_data.get("starts_at")
        ends_at = cleaned_data.get("ends_at")
        capacity = cleaned_data.get("capacity")

        if starts_at and ends_at and ends_at <= starts_at:
            self.add_error(
                "ends_at", "Окончание должно быть позже начала.")
            return cleaned_data
        if venue and capacity and not venue.can_host(capacity):
            self.add_error(
                "capacity",
                f"Площадка «{venue}» вмещает только {venue.capacity} чел.",
            )
        if venue and starts_at and ends_at:
            # Площадку занимают только запланированные мероприятия;
            # при редактировании текущее мероприятие с собой не сравниваем.
            busy = (
                Event.objects.active()
                .filter(venue=venue, starts_at__lt=ends_at,
                        ends_at__gt=starts_at)
                .exclude(pk=self.instance.pk)
            )
            if busy.exists():
                raise ValidationError(
                    f"Площадка «{venue}» в это время занята: "
                    f"{busy.first().title}."
                )
        return cleaned_data
