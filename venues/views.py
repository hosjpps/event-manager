from datetime import date, datetime, time, timedelta

from django.shortcuts import get_object_or_404, render
from django.utils import timezone

from events.models import Event

from .models import Venue


def venues(request):
    venues_list = Venue.objects.order_by("name")
    return render(
        request,
        "venues/venue_list.html",
        {"venues": venues_list},
    )


def venue_detail(request, slug):
    venue = get_object_or_404(Venue, slug=slug)

    day_start = timezone.make_aware(
        datetime.combine(timezone.localdate(), time.min)
    )
    day_end = day_start + timedelta(days=1)
    # Обратная связь related_name="events": мероприятия этой площадки.
    is_free_today = not venue.events.active().filter(
        starts_at__lt=day_end,
        ends_at__gt=day_start,
    ).exists()

    context = {
        "venue": venue,
        "is_free_today": is_free_today,
        "events": venue.events.order_by("starts_at"),
    }
    return render(request, "venues/venue_detail.html", context)


def available_venues(request):
    event_date = request.GET.get("date", "").strip()
    error = None
    venues_list = []

    if event_date:
        try:
            selected_date = date.fromisoformat(event_date)
        except ValueError:
            error = "Укажите дату в формате ГГГГ-ММ-ДД."
        else:
            # Площадку занимают только запланированные мероприятия.
            busy_venue_ids = (
                Event.objects.active()
                .for_date(selected_date)
                .values_list("venue_id", flat=True)
            )
            venues_list = Venue.objects.exclude(
                pk__in=busy_venue_ids,
            ).order_by("name")

    return render(
        request,
        "venues/available.html",
        {
            "venues": venues_list,
            "event_date": event_date,
            "error": error,
        },
    )
