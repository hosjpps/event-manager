from events.models import Event
from venues.models import Venue


def site_stats(request):
    """Общие цифры для подвала каждой страницы."""
    return {
        "nav_venues_count": Venue.objects.count(),
        "nav_upcoming_count": Event.objects.active().upcoming().count(),
    }
