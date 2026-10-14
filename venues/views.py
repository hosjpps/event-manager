from contextlib import closing
from datetime import date, datetime, time, timedelta

from django.shortcuts import render

from db.database import get_connection


def venues(request):
    with closing(get_connection()) as conn:
        venues_list = conn.execute(
            """
            SELECT id, name, address, capacity
            FROM venues
            ORDER BY name;
            """
        ).fetchall()

    return render(
        request,
        "venues/venue_list.html",
        {"venues": venues_list},
    )


def venue_detail(request, venue_id):
    day_start = datetime.combine(date.today(), time.min)
    day_end = day_start + timedelta(days=1)

    with closing(get_connection()) as conn:
        venue = conn.execute(
            """
            SELECT
                venues.id,
                venues.name,
                venues.address,
                venues.capacity,
                NOT EXISTS (
                    SELECT 1
                    FROM events
                    WHERE events.venue_id = venues.id
                    AND events.starts_at < ?
                    AND events.ends_at > ?
                ) AS is_free_today
            FROM venues
            WHERE venues.id = ?;
            """,
            [day_end.isoformat(), day_start.isoformat(), venue_id],
        ).fetchone()

    return render(
        request,
        "venues/venue_detail.html",
        {"venue": venue},
        status=404 if venue is None else 200,
    )


def available_venues(request):
    event_date = request.GET.get("date")
    error = None
    venues_list = []

    if event_date:
        try:
            date.fromisoformat(event_date)
        except ValueError:
            error = "Укажите дату в формате ГГГГ-ММ-ДД."
        else:
            with closing(get_connection()) as conn:
                venues_list = conn.execute(
                    """
                    SELECT id, name, address, capacity
                    FROM venues
                    WHERE id NOT IN (
                        SELECT venue_id
                        FROM events
                        WHERE substr(starts_at, 1, 10) = ?
                    )
                    ORDER BY name;
                    """,
                    [event_date],
                ).fetchall()

    return render(
        request,
        "venues/available.html",
        {
            "venues": venues_list,
            "event_date": event_date,
            "error": error,
        },
    )
