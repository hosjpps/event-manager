"""Сервис управления мероприятиями организации: консольное приложение."""
from collections.abc import Callable
from datetime import datetime

import storage
from events import (add_event, days_until_event, find_events, get_free_seats,
                    get_upcoming_events)
from registrations import (cancel_registration, count_registered,
                           get_event_participants, get_registration_status,
                           get_statistics, is_registration_open,
                           register_participant)
from utils import format_datetime, input_datetime, input_int, input_text
from venues import add_venue, filter_venues_by_capacity, sort_venues

ORGANIZATION_NAME = "РТУ МИРЭА"
STATUS_TITLES = {"registered": "участник", "waitlist": "лист ожидания"}


def print_venue_table(venues: list[dict]) -> None:
    """Вывести площадки таблицей."""
    if not venues:
        print("Площадки не найдены.")
        return
    print(f"{'id':>3}  {'Площадка':<22} {'Мест':>5}  Адрес")
    for venue in venues:
        print(f"{venue['id']:>3}  {venue['name']:<22} "
              f"{venue['capacity']:>5}  {venue['address']}")


def print_event_table(events: list[dict], data: dict) -> None:
    """Вывести мероприятия таблицей с числом свободных мест."""
    if not events:
        print("Мероприятия не найдены.")
        return
    for event in events:
        venue = data["venues"][event["venue_id"]]
        registered = count_registered(data["registrations"], event["id"])
        free = get_free_seats(event["capacity"], registered)
        print(f"{event['id']:>3}  {format_datetime(event['starts_at'])}  "
              f"{event['title']} — {venue['name']}, "
              f"свободно {free} из {event['capacity']}")


def show_venues(data: dict) -> bool:
    """Показать площадки, от самых вместительных к меньшим."""
    print_venue_table(sort_venues(data["venues"]))
    return False


def search_venues(data: dict) -> bool:
    """Найти площадки, вмещающие не меньше заданного числа человек."""
    min_capacity = input_int("Минимальная вместимость: ", min_value=1)
    print_venue_table(
        list(filter_venues_by_capacity(data["venues"], min_capacity))
    )
    return False


def add_venue_menu(data: dict) -> bool:
    """Добавить площадку организации."""
    venue_id = add_venue(
        data["venues"],
        input_text("Название площадки: "),
        input_text("Адрес: "),
        input_int("Вместимость: ", min_value=1),
    )
    print(f"Площадка добавлена, id={venue_id}.")
    return True


def show_events(data: dict) -> bool:
    """Показать предстоящие мероприятия в порядке дат."""
    upcoming = list(get_upcoming_events(data["events"], datetime.now()))
    print_event_table(upcoming, data)
    return False


def search_events(data: dict) -> bool:
    """Найти мероприятия по части названия."""
    query = input_text("Часть названия: ")
    print_event_table(find_events(data["events"], query), data)
    return False


def add_event_menu(data: dict) -> bool:
    """Создать мероприятие с проверкой вместимости и занятости площадки."""
    print_venue_table(sort_venues(data["venues"]))
    event_id = add_event(
        data["events"],
        data["venues"],
        input_text("Название мероприятия: "),
        input_int("id площадки: "),
        input_datetime("Начало (ДД.ММ.ГГГГ ЧЧ:ММ): "),
        input_datetime("Окончание (ДД.ММ.ГГГГ ЧЧ:ММ): "),
        input_int("Число мест: ", min_value=1),
    )
    print(f"Мероприятие создано, id={event_id}.")
    return True


def check_registration(data: dict) -> bool:
    """Проверить, открыта ли регистрация на мероприятие (сценарий ПР1)."""
    event = data["events"].get(input_int("id мероприятия: "))
    if event is None:
        print("Мероприятие не найдено.")
        return False
    now = datetime.now()
    registered = count_registered(data["registrations"], event["id"])
    free_seats = get_free_seats(event["capacity"], registered)
    days_left = days_until_event(event["starts_at"].date(), now.date())
    print(f"{event['title']}: {format_datetime(event['starts_at'])}, "
          f"через {days_left} дн.")
    print(f"Зарегистрировано {registered} из {event['capacity']}, "
          f"свободно {free_seats}")
    if event["is_published"] and not is_registration_open(event, now):
        print("Мероприятие уже началось, регистрация закрыта")
    else:
        print(get_registration_status(event["is_published"], free_seats,
                                      days_left))
    return False


def register_menu(data: dict) -> bool:
    """Зарегистрировать участника на мероприятие."""
    registration = register_participant(
        data["registrations"],
        data["events"],
        input_int("id мероприятия: "),
        input_text("Имя участника: "),
        input_text("E-mail: "),
        datetime.now(),
    )
    status = STATUS_TITLES[registration["status"]]
    print(f"Регистрация id={registration['id']} создана, статус: {status}.")
    return True


def cancel_menu(data: dict) -> bool:
    """Отменить регистрацию; место получает первый из листа ожидания."""
    promoted = cancel_registration(
        data["registrations"], input_int("id регистрации: ")
    )
    print("Регистрация отменена.")
    if promoted:
        print(f"Из листа ожидания переведён участник "
              f"{promoted['participant']}.")
    return True


def show_participants(data: dict) -> bool:
    """Показать участников и лист ожидания мероприятия."""
    participants = get_event_participants(
        data["registrations"], input_int("id мероприятия: ")
    )
    if not participants:
        print("Регистраций нет.")
    for r in participants:
        print(f"{r['id']:>3}  {r['participant']:<20} {r['email']:<24} "
              f"{STATUS_TITLES[r['status']]}")
    return False


def show_statistics(data: dict) -> bool:
    """Показать статистику по мероприятиям и регистрациям."""
    stats = get_statistics(data["events"], data["registrations"])
    print(f"Мероприятий: {stats['events']}")
    print(f"Участников: {stats['registered']}, "
          f"в листе ожидания: {stats['waitlist']}")
    print(f"Средняя заполненность: {stats['average_fill_percent']}%")
    if stats["most_popular_event_id"] is not None:
        popular = data["events"][stats["most_popular_event_id"]]
        print(f"Самое востребованное: {popular['title']}")
    return False


MENU: dict[str, tuple[str, Callable[[dict], bool]]] = {
    "1": ("Показать площадки", show_venues),
    "2": ("Подобрать площадку по вместимости", search_venues),
    "3": ("Добавить площадку", add_venue_menu),
    "4": ("Показать предстоящие мероприятия", show_events),
    "5": ("Найти мероприятие", search_events),
    "6": ("Создать мероприятие", add_event_menu),
    "7": ("Проверить регистрацию на мероприятие", check_registration),
    "8": ("Зарегистрировать участника", register_menu),
    "9": ("Отменить регистрацию", cancel_menu),
    "10": ("Участники мероприятия", show_participants),
    "11": ("Статистика", show_statistics),
}


def show_help() -> None:
    """Вывести описание пунктов меню по документации функций."""
    for key, (title, handler) in MENU.items():
        print(f"{key:>2}. {title}: {handler.__doc__.splitlines()[0]}")


def save_all(data: dict) -> None:
    """Сохранить все данные приложения в JSON-файлы."""
    storage.save_venues(data["venues"])
    storage.save_events(data["events"])
    storage.save_registrations(data["registrations"])


def main() -> None:
    """Точка запуска: загрузка данных и цикл меню."""
    try:
        data = {
            "venues": storage.load_venues(),
            "events": storage.load_events(),
            "registrations": storage.load_registrations(),
        }
    except (ValueError, KeyError) as error:
        print(f"Не удалось загрузить данные: {error}")
        return

    while True:
        print(f"\n=== Мероприятия организации «{ORGANIZATION_NAME}» ===")
        for key, (title, _) in MENU.items():
            print(f"{key:>2}. {title}")
        print(" ?. Справка\n 0. Выход")
        try:
            choice = input("Выберите действие: ").strip()
        except (EOFError, KeyboardInterrupt):
            break
        if choice == "0":
            break
        if choice == "?":
            show_help()
            continue
        if choice not in MENU:
            print("Такого пункта нет.")
            continue
        try:
            if MENU[choice][1](data):
                save_all(data)
        except (KeyError, ValueError) as error:
            print(f"Ошибка: {error.args[0]}")
        except OSError as error:
            print(f"Не удалось сохранить данные: {error}")
        except (EOFError, KeyboardInterrupt):
            break
    print("До свидания!")


if __name__ == "__main__":
    main()
