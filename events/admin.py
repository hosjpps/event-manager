from django.contrib import admin

from registrations.models import Registration

from .models import Event


class RegistrationInline(admin.TabularInline):
    """Регистрации участников на странице мероприятия."""

    model = Registration
    fields = ("participant", "email", "status", "registered_at")
    extra = 0


@admin.register(Event)
class EventAdmin(admin.ModelAdmin):
    list_display = (
        "title", "venue", "starts_at", "capacity", "status", "is_published",
    )
    list_display_links = ("title",)
    list_editable = ("status",)
    list_filter = ("status", "venue", "is_published", "starts_at")
    search_fields = ("title", "venue__name")
    ordering = ("starts_at",)
    list_per_page = 20
    list_select_related = ("venue",)
    date_hierarchy = "starts_at"
    inlines = (RegistrationInline,)
    actions = ("mark_cancelled", "mark_completed", "mark_active")

    @admin.action(description="Отметить как отменённые")
    def mark_cancelled(self, request, queryset):
        updated = queryset.update(status=Event.Status.CANCELLED)
        self.message_user(request, f"Отменено мероприятий: {updated}")

    @admin.action(description="Отметить как завершённые")
    def mark_completed(self, request, queryset):
        updated = queryset.update(status=Event.Status.COMPLETED)
        self.message_user(request, f"Завершено мероприятий: {updated}")

    @admin.action(description="Вернуть в запланированные")
    def mark_active(self, request, queryset):
        updated = queryset.update(status=Event.Status.ACTIVE)
        self.message_user(request, f"Запланировано мероприятий: {updated}")
