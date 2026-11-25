from django.contrib import admin

from events.models import Event

from .models import Venue


class EventInline(admin.TabularInline):
    """Мероприятия площадки прямо на её странице в админке."""

    model = Event
    fields = ("title", "starts_at", "ends_at", "capacity", "status")
    extra = 0
    show_change_link = True


@admin.register(Venue)
class VenueAdmin(admin.ModelAdmin):
    list_display = ("name", "address", "capacity", "is_large", "slug")
    list_display_links = ("name",)
    list_editable = ("capacity",)
    search_fields = ("name", "address")
    list_filter = ("is_large",)
    ordering = ("name",)
    list_per_page = 20
    readonly_fields = ("slug", "is_large")
    inlines = (EventInline,)
