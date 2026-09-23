"""Вспомогательные функции: идентификаторы, разбор дат и безопасный ввод."""
from collections.abc import Iterable
from datetime import datetime

DATETIME_FORMAT = "%d.%m.%Y %H:%M"


def next_id(existing_ids: Iterable[int]) -> int:
    """Вернуть следующий свободный идентификатор (максимальный + 1)."""
    return max(existing_ids, default=0) + 1


def parse_datetime(text: str) -> datetime:
    """Преобразовать строку «ДД.ММ.ГГГГ ЧЧ:ММ» в datetime.

    Raises:
        ValueError: если строка не соответствует формату.
    """
    return datetime.strptime(text.strip(), DATETIME_FORMAT)


def format_datetime(value: datetime) -> str:
    """Вернуть дату и время в формате «ДД.ММ.ГГГГ ЧЧ:ММ»."""
    return value.strftime(DATETIME_FORMAT)


def input_text(prompt: str) -> str:
    """Запросить непустую строку; при пустом вводе повторить запрос."""
    while True:
        text = input(prompt).strip()
        if text:
            return text
        print("Значение не может быть пустым.")


def input_int(prompt: str, min_value: int | None = None) -> int:
    """Запросить целое число; при некорректном вводе повторить запрос."""
    while True:
        try:
            value = int(input(prompt))
        except ValueError:
            print("Введите целое число.")
            continue
        if min_value is not None and value < min_value:
            print(f"Число должно быть не меньше {min_value}.")
            continue
        return value


def input_datetime(prompt: str) -> datetime:
    """Запросить дату и время; при неверном формате повторить запрос."""
    while True:
        try:
            return parse_datetime(input(prompt))
        except ValueError:
            print("Формат даты: ДД.ММ.ГГГГ ЧЧ:ММ, например 15.10.2026 18:00.")
