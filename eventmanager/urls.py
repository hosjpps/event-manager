"""Корневая маршрутизация: адреса распределяются между приложениями."""
from django.contrib import admin
from django.urls import include, path

urlpatterns = [
    path("admin/", admin.site.urls),
    path("", include("homepage.urls")),
    path("venues/", include("venues.urls")),
    path("events/", include("events.urls")),
    path("registrations/", include("registrations.urls")),
]

handler404 = "homepage.views.page_not_found"
