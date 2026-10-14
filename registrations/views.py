from django.shortcuts import render

from storage import load_all


def registrations(request):
    _, _, registrations_list = load_all()

    context = {
        "registrations": registrations_list,
    }

    return render(
        request,
        "registrations/registration_list.html",
        context,
    )


def registration_detail(request, registration_id):
    _, _, registrations_list = load_all()
    registration = next(
        (r for r in registrations_list if r.id == registration_id),
        None,
    )

    context = {
        "registration": registration,
    }

    return render(
        request,
        "registrations/registration_detail.html",
        context,
        status=404 if registration is None else 200,
    )
