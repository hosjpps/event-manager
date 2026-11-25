from django.urls import path

from . import views

app_name = "events"

urlpatterns = [
    path("", views.events, name="list"),
    path("create/", views.event_create, name="create"),
    path("<int:event_id>/", views.event_detail, name="detail"),
    path("<int:event_id>/edit/", views.event_update, name="edit"),
    path("<int:event_id>/cancel/", views.event_cancel, name="cancel"),
]
