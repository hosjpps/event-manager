from django.http import HttpResponse
from django.utils.html import escape

from homepage.views import page
from models.registrations import CANCELLED, REGISTERED
from storage import load_all
from utils import format_datetime

STATUS_TITLES = {
    REGISTERED: "участник",
    CANCELLED: "отменена",
}


def status_badge(registration):
    """Вернуть цветной бейдж статуса регистрации."""
    title = STATUS_TITLES.get(registration.status, "лист ожидания")
    if registration.status == REGISTERED:
        badge = "bg-success"
    elif registration.status == CANCELLED:
        badge = "bg-secondary"
    else:
        badge = "bg-warning text-dark"
    return f'<span class="badge {badge}">{title}</span>'


def registrations(request):
    _, _, registrations_list = load_all()
    items = ""
    for registration in registrations_list:
        items += f"""
        <li class="list-group-item d-flex justify-content-between">
            <a href="/registrations/{registration.id}/">
                {escape(registration.participant)} –
                {escape(registration.event.title)}
            </a>
            {status_badge(registration)}
        </li>
        """
    content = f"""
    <h1>Регистрации</h1>
    <ul class="list-group">{items}</ul>
    """
    return HttpResponse(page("Event Manager – регистрации", content))


def registration_detail(request, registration_id):
    _, _, registrations_list = load_all()
    registration = next(
        (r for r in registrations_list if r.id == registration_id), None
    )

    if registration is None:
        content = """
        <h1 class="text-danger">Регистрация не найдена</h1>
        <a href="/registrations/" class="btn btn-outline-secondary">
            ← к списку регистраций
        </a>
        """
        return HttpResponse(
            page("Регистрация не найдена", content),
            status=404,
        )

    content = f"""
    <div class="card">
        <div class="card-body">
            <h5 class="card-title">Регистрация №{registration.id}</h5>
            <p class="card-text">
                <strong>Участник:</strong> {escape(registration.participant)}
            </p>
            <p class="card-text">
                <strong>Мероприятие:</strong>
                <a href="/events/{registration.event.id}/">
                    {escape(registration.event.title)}
                </a>
            </p>
            <p class="card-text">
                <strong>Дата регистрации:</strong>
                {format_datetime(registration.registered_at)}
            </p>
            <p class="card-text">
                Статус: {status_badge(registration)}
            </p>
            <a href="/registrations/" class="btn btn-outline-secondary">
                ← к списку регистраций
            </a>
        </div>
    </div>
    """
    return HttpResponse(
        page(f"Регистрация №{registration.id}", content),
        status=200,
    )
