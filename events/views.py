from django.contrib import messages
from django.core.paginator import Paginator
from django.db.models import Count, Q
from django.shortcuts import get_object_or_404, redirect, render
from django.utils import timezone
from django.views.decorators.http import require_POST

from models.events import get_free_seats
from models.registrations import get_registration_status
from registrations.models import Registration

from .forms import EventFilterForm, EventForm
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
    form = EventFilterForm(request.GET or None)
    events_list = Event.objects.select_related("venue").annotate(
        registered=Count(
            "registrations",
            filter=Q(registrations__status=Registration.Status.REGISTERED),
        )
    )
    status = Event.Status.ACTIVE
    sort = "date"

    # Неверные значения не роняют страницу: форма покажет ошибки,
    # а список останется без фильтров по этим полям.
    if form.is_valid():
        data = form.cleaned_data
        status = data["status"] or Event.Status.ACTIVE
        sort = data["sort"] or "date"
        if data["date"]:
            events_list = events_list.for_date(data["date"])
        if data["venue"]:
            events_list = events_list.filter(venue=data["venue"])
        if data["q"]:
            events_list = events_list.filter(title_matches(data["q"]))

    if status != "all":
        events_list = events_list.filter(status=status)
    events_list = events_list.order_by(SORT_FIELDS[sort], "pk")

    page_obj = Paginator(events_list, EVENTS_PER_PAGE).get_page(
        request.GET.get("page")
    )
    context = {
        "form": form,
        "page_obj": page_obj,
        "events": page_obj.object_list,
        "total": page_obj.paginator.count,
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


def event_create(request):
    form = EventForm(request.POST or None)
    if request.method == "POST" and form.is_valid():
        event = form.save()
        messages.success(request, "Мероприятие создано.")
        return redirect("events:detail", event_id=event.pk)
    return render(
        request,
        "events/event_form.html",
        {"form": form, "is_edit": False},
    )


def event_update(request, event_id):
    event = get_object_or_404(Event, pk=event_id)
    form = EventForm(request.POST or None, instance=event)
    if request.method == "POST" and form.is_valid():
        form.save()
        messages.success(request, "Изменения сохранены.")
        return redirect("events:detail", event_id=event.pk)
    return render(
        request,
        "events/event_form.html",
        {"form": form, "is_edit": True, "event": event},
    )


@require_POST
def event_cancel(request, event_id):
    event = get_object_or_404(Event, pk=event_id)
    event.status = Event.Status.CANCELLED
    event.save(update_fields=["status"])
    messages.success(request, "Мероприятие отменено, площадка освобождена.")
    return redirect("events:detail", event_id=event.pk)
