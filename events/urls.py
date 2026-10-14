from django.urls import path

from . import views

urlpatterns = [
    path("", views.events, name="events"),
    path("<int:event_id>/", views.event_detail, name="event_detail"),
]
