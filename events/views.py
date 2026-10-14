from datetime import date

from django.http import HttpResponse
from django.utils.html import escape

from homepage.views import page
from models.events import find_event_by_id, get_free_seats, sort_events_by_date
from models.registrations import count_registered, get_registration_status
from storage import load_all
from utils import format_datetime


def events(request):
    _, events_list, _ = load_all()
    items = ""
    for event in sort_events_by_date(events_list):
        text = (
            f"{escape(event.title)} – {format_datetime(event.starts_at)}, "
            f"{escape(event.venue.name)}"
        )
        items += (
            '<li class="list-group-item">'
            f'<a href="/events/{event.id}/">{text}</a></li>'
        )
    content = f"""
    <h1>Мероприятия</h1>
    <ul class="list-group">{items}</ul>
    """
    return HttpResponse(page("Event Manager – мероприятия", content))


def event_detail(request, event_id):
    _, events_list, registrations_list = load_all()
    event = find_event_by_id(events_list, event_id)

    if event is None:
        content = """
        <h1 class="text-danger">Мероприятие не найдено</h1>
        <a href="/events/" class="btn btn-outline-secondary">
            ← к списку мероприятий
        </a>
        """
        return HttpResponse(
            page("Мероприятие не найдено", content),
            status=404,
        )

    registered = count_registered(registrations_list, event)
    free_seats = get_free_seats(event.capacity, registered)
    days_left = event.days_until(date.today())
    status = get_registration_status(
        event.is_published,
        free_seats,
        days_left,
    )
    badge = "bg-success" if free_seats > 0 and days_left >= 0 else "bg-danger"

    content = f"""
    <div class="card">
        <div class="card-body">
            <h5 class="card-title">{escape(event.title)}</h5>
            <p class="card-text">
                <strong>Площадка:</strong>
                <a href="/venues/{event.venue.id}/">
                    {escape(event.venue.name)}
                </a>
            </p>
            <p class="card-text">
                <strong>Начало:</strong> {format_datetime(event.starts_at)}
                (через {days_left} дн.)
            </p>
            <p class="card-text">
                <strong>Окончание:</strong> {format_datetime(event.ends_at)}
            </p>
            <p class="card-text">
                <strong>Мест:</strong> {event.capacity},
                зарегистрировано {registered}, свободно {free_seats}
            </p>
            <p class="card-text">
                Регистрация: <span class="badge {badge}">{status}</span>
            </p>
            <a href="/events/" class="btn btn-outline-secondary">
                ← к списку мероприятий
            </a>
        </div>
    </div>
    """
    return HttpResponse(page(event.title, content), status=200)
