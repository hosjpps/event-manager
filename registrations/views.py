from django.db.models import Avg, Count, F, Max, Q
from django.shortcuts import get_object_or_404, render

from events.models import Event
from venues.models import Venue

from .models import Registration


def registrations(request):
    registrations_list = (
        Registration.objects
        .exclude(status=Registration.Status.CANCELLED)
        .select_related("event__venue")
        .order_by("pk")
    )
    return render(
        request,
        "registrations/registration_list.html",
        {"registrations": registrations_list},
    )


def registration_detail(request, registration_id):
    registration = get_object_or_404(
        Registration.objects.select_related("event__venue"),
        pk=registration_id,
    )
    return render(
        request,
        "registrations/registration_detail.html",
        {"registration": registration},
    )


def statistics(request):
    totals = Registration.objects.aggregate(
        registered=Count(
            "pk", filter=Q(status=Registration.Status.REGISTERED)
        ),
        waitlist=Count("pk", filter=Q(status=Registration.Status.WAITLIST)),
    )
    by_status = Event.objects.aggregate(
        active=Count("pk", filter=Q(status=Event.Status.ACTIVE)),
        cancelled=Count("pk", filter=Q(status=Event.Status.CANCELLED)),
        completed=Count("pk", filter=Q(status=Event.Status.COMPLETED)),
    )
    capacity = Event.objects.aggregate(
        events_count=Count("pk"),
        average_capacity=Avg("capacity"),
        max_capacity=Max("capacity"),
    )
    by_event = (
        Event.objects
        .annotate(
            event_title=F("title"),
            registered_count=Count(
                "registrations",
                filter=Q(
                    registrations__status=Registration.Status.REGISTERED
                ),
            ),
        )
        .values("event_title", "capacity", "registered_count")
        .order_by("-registered_count", "starts_at")
    )
    # Начинаем с Venue, чтобы площадки без мероприятий тоже попали в
    # результат с нулём (аналог LEFT JOIN ... GROUP BY).
    by_venue = (
        Venue.objects
        .annotate(venue_name=F("name"), events_count=Count("events"))
        .values("venue_name", "events_count")
        .order_by("-events_count", "venue_name")
    )
    # Фильтр по аннотации — это HAVING в SQL.
    with_waitlist = (
        Event.objects
        .annotate(
            event_title=F("title"),
            waitlist_count=Count(
                "registrations",
                filter=Q(
                    registrations__status=Registration.Status.WAITLIST
                ),
            ),
        )
        .filter(waitlist_count__gte=1)
        .values("event_title", "waitlist_count")
    )
    return render(
        request,
        "registrations/statistics.html",
        {
            "totals": totals,
            "capacity": capacity,
            "by_status": by_status,
            "by_event": by_event,
            "by_venue": by_venue,
            "with_waitlist": with_waitlist,
        },
    )
