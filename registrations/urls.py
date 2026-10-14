from django.urls import path

from . import views

urlpatterns = [
    path("", views.registrations, name="registrations"),
    path(
        "<int:registration_id>/",
        views.registration_detail,
        name="registration_detail",
    ),
]
