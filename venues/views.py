from datetime import date, datetime, time, timedelta

from django.http import HttpResponse
from django.utils.html import escape

from homepage.views import page
from models.events import is_venue_free
from models.venues import find_venue_by_id
from storage import load_all


def venues(request):
    venues_list, _, _ = load_all()
    items = ""
    for venue in venues_list:
        text = f"{escape(venue.name)} – вместимость {venue.capacity} мест"
        items += (
            '<li class="list-group-item">'
            f'<a href="/venues/{venue.id}/">{text}</a></li>'
        )
    content = f"""
    <h1>Площадки</h1>
    <ul class="list-group">{items}</ul>
    """
    return HttpResponse(page("Event Manager – площадки", content))


def venue_detail(request, venue_id):
    venues_list, events_list, _ = load_all()
    venue = find_venue_by_id(venues_list, venue_id)

    if venue is None:
        content = """
        <h1 class="text-danger">Площадка не найдена</h1>
        <a href="/venues/" class="btn btn-outline-secondary">
            ← к списку площадок
        </a>
        """
        return HttpResponse(
            page("Площадка не найдена", content),
            status=404,
        )

    day_start = datetime.combine(date.today(), time.min)
    available = is_venue_free(
        events_list,
        venue,
        day_start,
        day_start + timedelta(days=1),
    )
    status = "свободна" if available else "занята мероприятием"
    badge = "bg-success" if available else "bg-danger"

    content = f"""
    <div class="card">
        <div class="card-body">
            <h5 class="card-title">{escape(venue.name)}</h5>
            <p class="card-text"><strong>ID:</strong> {venue.id}</p>
            <p class="card-text">
                <strong>Адрес:</strong> {escape(venue.address)}
            </p>
            <p class="card-text">
                <strong>Вместимость:</strong> {venue.capacity} мест
            </p>
            <p class="card-text">
                Занятость сегодня:
                <span class="badge {badge}">{status}</span>
            </p>
            <a href="/venues/" class="btn btn-outline-secondary">
                ← к списку площадок
            </a>
        </div>
    </div>
    """
    return HttpResponse(page(venue.name, content), status=200)
