from datetime import date

from django.shortcuts import render

from models.events import find_event_by_id, get_free_seats, sort_events_by_date
from models.registrations import count_registered, get_registration_status
from storage import load_all


def events(request):
    _, events_list, _ = load_all()

    context = {
        "events": sort_events_by_date(events_list),
    }

    return render(
        request,
        "events/event_list.html",
        context,
    )


def event_detail(request, event_id):
    _, events_list, registrations_list = load_all()
    event = find_event_by_id(events_list, event_id)

    context = {
        "event": event,
    }
    if event is not None:
        registered = count_registered(registrations_list, event)
        free_seats = get_free_seats(event.capacity, registered)
        days_left = event.days_until(date.today())
        context.update({
            "registered": registered,
            "free_seats": free_seats,
            "days_left": days_left,
            "status": get_registration_status(
                event.is_published,
                free_seats,
                days_left,
            ),
        })

    return render(
        request,
        "events/event_detail.html",
        context,
        status=404 if event is None else 200,
    )
