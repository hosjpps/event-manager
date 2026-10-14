from datetime import date, datetime, time, timedelta

from django.shortcuts import render

from models.events import is_venue_free
from models.venues import find_venue_by_id
from storage import load_all


def venues(request):
    venues_list, _, _ = load_all()

    context = {
        "venues": venues_list,
    }

    return render(
        request,
        "venues/venue_list.html",
        context,
    )


def venue_detail(request, venue_id):
    venues_list, events_list, _ = load_all()
    venue = find_venue_by_id(venues_list, venue_id)

    context = {
        "venue": venue,
    }
    if venue is not None:
        day_start = datetime.combine(date.today(), time.min)
        context["is_free_today"] = is_venue_free(
            events_list,
            venue,
            day_start,
            day_start + timedelta(days=1),
        )

    return render(
        request,
        "venues/venue_detail.html",
        context,
        status=404 if venue is None else 200,
    )
