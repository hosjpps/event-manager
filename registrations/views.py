from contextlib import closing

from django.shortcuts import render

from db.database import get_connection

REGISTRATION_SELECT = """
    SELECT
        registrations.id,
        registrations.participant,
        registrations.status,
        strftime(
            '%d.%m.%Y %H:%M', registrations.registered_at
        ) AS registered_at_text,
        registrations.event_id,
        events.title AS event_title,
        venues.name AS venue_name
    FROM registrations
    JOIN events ON registrations.event_id = events.id
    JOIN venues ON events.venue_id = venues.id
"""


def registrations(request):
    with closing(get_connection()) as conn:
        registrations_list = conn.execute(
            REGISTRATION_SELECT + """
            WHERE registrations.status != 'cancelled'
            ORDER BY registrations.id;
            """
        ).fetchall()

    return render(
        request,
        "registrations/registration_list.html",
        {"registrations": registrations_list},
    )


def registration_detail(request, registration_id):
    with closing(get_connection()) as conn:
        registration = conn.execute(
            REGISTRATION_SELECT + "WHERE registrations.id = ?;",
            [registration_id],
        ).fetchone()

    return render(
        request,
        "registrations/registration_detail.html",
        {"registration": registration},
        status=404 if registration is None else 200,
    )


def statistics(request):
    with closing(get_connection()) as conn:
        totals = conn.execute(
            """
            SELECT
                COUNT(CASE WHEN status = 'registered' THEN 1 END)
                    AS registered,
                COUNT(CASE WHEN status = 'waitlist' THEN 1 END)
                    AS waitlist
            FROM registrations;
            """
        ).fetchone()
        by_event = conn.execute(
            """
            SELECT
                events.title AS event_title,
                events.capacity,
                COUNT(registrations.id) AS registered_count
            FROM events
            LEFT JOIN registrations
                ON registrations.event_id = events.id
                AND registrations.status = 'registered'
            GROUP BY events.id, events.title, events.capacity
            ORDER BY registered_count DESC;
            """
        ).fetchall()
        by_venue = conn.execute(
            """
            SELECT
                venues.name AS venue_name,
                COUNT(events.id) AS events_count
            FROM venues
            LEFT JOIN events ON events.venue_id = venues.id
            GROUP BY venues.id, venues.name
            ORDER BY events_count DESC, venues.name;
            """
        ).fetchall()
        with_waitlist = conn.execute(
            """
            SELECT
                events.title AS event_title,
                COUNT(registrations.id) AS waitlist_count
            FROM events
            JOIN registrations ON registrations.event_id = events.id
            WHERE registrations.status = 'waitlist'
            GROUP BY events.id, events.title
            HAVING COUNT(registrations.id) >= 1;
            """
        ).fetchall()

    return render(
        request,
        "registrations/statistics.html",
        {
            "totals": totals,
            "by_event": by_event,
            "by_venue": by_venue,
            "with_waitlist": with_waitlist,
        },
    )
