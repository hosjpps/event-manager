from datetime import date

from django.core.paginator import Paginator
from django.db.models import Count, Q
from django.shortcuts import get_object_or_404, render
from django.utils import timezone

from models.events import get_free_seats
from models.registrations import get_registration_status
from registrations.models import Registration
from venues.models import Venue

from .models import Event

EVENTS_PER_PAGE = 5
SORT_FIELDS = {
    "date": "starts_at",
    "title": "title",
    "venue": "venue__name",
}


def title_matches(query):
    """Условие поиска по названию без учёта регистра.

    LIKE в SQLite не различает регистр только у латиницы, поэтому для
    кириллицы проверяем типовые варианты написания запроса.
    """
    condition = Q()
    for variant in {query, query.lower(), query.capitalize(), query.upper()}:
        condition |= Q(title__contains=variant)
    return condition


def events(request):
    event_date = request.GET.get("date", "").strip()
    venue_id = request.GET.get("venue", "").strip()
    query = request.GET.get("q", "").strip()
    sort = request.GET.get("sort", "date")
    status = request.GET.get("status", Event.Status.ACTIVE)
    error = None

    events_list = Event.objects.select_related("venue").annotate(
        registered=Count(
            "registrations",
            filter=Q(registrations__status=Registration.Status.REGISTERED),
        )
    )
    # По умолчанию показываем только запланированные; "all" — все статусы.
    if status in Event.Status.values:
        events_list = events_list.filter(status=status)
    elif status != "all":
        status = Event.Status.ACTIVE
        events_list = events_list.active()

    if event_date:
        try:
            selected_date = date.fromisoformat(event_date)
        except ValueError:
            error = "Укажите дату в формате ГГГГ-ММ-ДД."
        else:
            events_list = events_list.filter(starts_at__date=selected_date)
    if venue_id.isdigit():
        events_list = events_list.filter(venue_id=int(venue_id))
    if query:
        events_list = events_list.filter(title_matches(query))

    sort_field = SORT_FIELDS.get(sort, "starts_at")
    events_list = events_list.order_by(sort_field, "pk")

    page_obj = Paginator(events_list, EVENTS_PER_PAGE).get_page(
        request.GET.get("page")
    )

    context = {
        "page_obj": page_obj,
        "events": page_obj.object_list,
        "total": page_obj.paginator.count,
        "venues": Venue.objects.order_by("name"),
        "event_date": event_date,
        "selected_venue": venue_id,
        "query": query,
        "sort": sort,
        "status": status,
        "statuses": Event.Status.choices,
        "error": error,
    }
    return render(request, "events/event_list.html", context)


def event_detail(request, event_id):
    event = get_object_or_404(
        Event.objects.select_related("venue"),
        pk=event_id,
    )
    registered = event.registrations.filter(
        status=Registration.Status.REGISTERED
    ).count()
    free_seats = get_free_seats(event.capacity, registered)
    days_left = (timezone.localtime(event.starts_at).date()
                 - timezone.localdate()).days

    context = {
        "event": event,
        "registered": registered,
        "free_seats": free_seats,
        "days_left": days_left,
        "status": get_registration_status(
            event.is_published, free_seats, days_left
        ),
    }
    if event.status == Event.Status.CANCELLED:
        context["status"] = "Мероприятие отменено"
    return render(request, "events/event_detail.html", context)
