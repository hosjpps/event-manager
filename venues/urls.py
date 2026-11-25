from django.urls import path

from . import views

app_name = "venues"

urlpatterns = [
    path("", views.venues, name="list"),
    path("available/", views.available_venues, name="available"),
    path("<slug:slug>/", views.venue_detail, name="detail"),
    path("<slug:slug>/photo/", views.venue_photo, name="photo"),
]
