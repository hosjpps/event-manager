from django.urls import path

from . import views

app_name = "events"

urlpatterns = [
    path("", views.events, name="list"),
    path("<int:event_id>/", views.event_detail, name="detail"),
]
