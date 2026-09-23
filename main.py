"""Сервис управления мероприятиями организации.

Начальный сценарий (ПР1): проверка возможности зарегистрироваться
на мероприятие организации.
"""
from datetime import date

organization_name = "РТУ МИРЭА"
venue_name = "Актовый зал"
venue_capacity = 120

event_title = "Лекция «Введение в Django»"
event_date = date(2026, 10, 15)
event_capacity = 100
is_published = True

# Данные приходят из формы регистрации строками
registered_count_text = "97"
today_text = "2026-10-01"


def check_event_fits_venue(event_capacity, venue_capacity):
    """Вернуть True, если площадка вмещает всех участников мероприятия."""
    return event_capacity <= venue_capacity


def get_free_seats(event_capacity, registered_count):
    """Вернуть число свободных мест (не меньше нуля)."""
    free_seats = event_capacity - registered_count
    if free_seats < 0:
        return 0
    return free_seats


def get_registration_status(is_published, free_seats, days_left):
    """Вернуть текстовый статус регистрации на мероприятие."""
    if not is_published:
        return "Регистрация ещё не открыта"
    elif days_left < 0:
        return "Мероприятие уже прошло"
    elif free_seats > 0:
        return "Регистрация открыта"
    else:
        return "Мест нет, можно встать в лист ожидания"


def days_until_event(event_date, today):
    """Вернуть количество дней до начала мероприятия."""
    return (event_date - today).days


registered_count = int(registered_count_text)
today = date.fromisoformat(today_text)

free_seats = get_free_seats(event_capacity, registered_count)
days_left = days_until_event(event_date, today)
fill_percent = registered_count / event_capacity * 100

print(f"Организация: {organization_name}")
print(f"Мероприятие: {event_title}")
print(f"Дата: {event_date.strftime('%d.%m.%Y')} (через {days_left} дн.)")
print(f"Площадка: {venue_name}, вместимость {venue_capacity} чел.")

if check_event_fits_venue(event_capacity, venue_capacity):
    print(f"Мест на мероприятии: {event_capacity} — площадка подходит")
else:
    print(f"Мест на мероприятии: {event_capacity} — площадка слишком мала")

print(f"Зарегистрировано: {registered_count} ({fill_percent:.1f}% мест)")
print(f"Свободно мест: {free_seats}")
print(get_registration_status(is_published, free_seats, days_left))
