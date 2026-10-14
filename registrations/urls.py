from django.urls import path

from . import views

app_name = "registrations"

urlpatterns = [
    path("", views.registrations, name="list"),
    path("statistics/", views.statistics, name="statistics"),
    path(
        "<int:registration_id>/",
        views.registration_detail,
        name="detail",
    ),
]
