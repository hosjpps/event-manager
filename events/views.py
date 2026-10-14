from contextlib import closing
from datetime import date

from django.shortcuts import render

from db.database import get_connection
from models.events import get_free_seats
from models.registrations import get_registration_status

EVENT_SELECT = """
    SELECT
        events.id,
        events.title,
        events.venue_id,
        venues.name AS venue_name,
        strftime('%d.%m.%Y %H:%M', events.starts_at) AS starts_at_text,
        strftime('%d.%m.%Y %H:%M', events.ends_at) AS ends_at_text,
        events.capacity,
        events.is_published,
        CAST(
            julianday(substr(events.starts_at, 1, 10)) - julianday(?)
            AS INTEGER
        ) AS days_left,
        COUNT(registrations.id) AS registered
    FROM events
    JOIN venues ON events.venue_id = venues.id
    LEFT JOIN registrations
        ON registrations.event_id = events.id
        AND registrations.status = 'registered'
"""


def events(request):
    with closing(get_connection()) as conn:
        events_list = conn.execute(
            EVENT_SELECT + """
            GROUP BY events.id, venues.name
            ORDER BY events.starts_at;
            """,
            [date.today().isoformat()],
        ).fetchall()

    return render(
        request,
        "events/event_list.html",
        {"events": events_list},
    )


def event_detail(request, event_id):
    with closing(get_connection()) as conn:
        event = conn.execute(
            EVENT_SELECT + """
            WHERE events.id = ?
            GROUP BY events.id, venues.name;
            """,
            [date.today().isoformat(), event_id],
        ).fetchone()

    context = {"event": event}
    if event is not None:
        free_seats = get_free_seats(event["capacity"], event["registered"])
        context.update({
            "free_seats": free_seats,
            "status": get_registration_status(
                bool(event["is_published"]),
                free_seats,
                event["days_left"],
            ),
        })

    return render(
        request,
        "events/event_detail.html",
        context,
        status=404 if event is None else 200,
    )
