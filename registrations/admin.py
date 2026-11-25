from django.contrib import admin

from .models import Registration


@admin.register(Registration)
class RegistrationAdmin(admin.ModelAdmin):
    list_display = ("participant", "email", "event", "status",
                    "registered_at")
    list_display_links = ("participant",)
    list_filter = ("status", "event__venue", "event")
    search_fields = ("participant", "email", "event__title")
    ordering = ("-registered_at",)
    list_per_page = 20
    list_select_related = ("event", "event__venue")
    readonly_fields = ("registered_at",)
