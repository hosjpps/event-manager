# Сервис управления мероприятиями организации

Приложение для учёта площадок организации, её мероприятий и регистрации
участников. Консольная версия (ПР1–ПР3) дополнена веб-интерфейсом на Django
(ПР5), шаблонами (ПР6) и базой данных SQLite (ПР7).

## Назначение

Приложение помогает организации (институту, компании, клубу) вести афишу своих
мероприятий: назначать мероприятиям площадки, следить за числом свободных мест
и регистрировать участников. Сервис заменяет разрозненные онлайн-формы и общий
календарь залов, из-за которых одна аудитория оказывается занята дважды, а на
популярные события записывается больше людей, чем помещается в зал.

## Целевая аудитория

- организаторы мероприятий — сотрудники и активисты организации;
- администраторы организации — отвечают за площадки и статистику;
- участники — студенты, сотрудники и гости, которые записываются на мероприятия.

## Предметная область

Организация располагает площадками (залы, аудитории) с ограниченной
вместимостью. На площадках проходят мероприятия — лекции, семинары, собрания —
у каждого есть время проведения и число мест. Пользователи регистрируются на
мероприятия; если мест нет, они попадают в лист ожидания и получают место,
когда кто-то отменит регистрацию.

## Основные сущности

- **Организация** — владелец площадок и мероприятий;
- **Площадка** — зал или аудитория с адресом и вместимостью;
- **Мероприятие** — название, время начала и окончания, площадка, число мест;
- **Участник** — регистрация пользователя на мероприятие со статусом
  «участник» или «лист ожидания».

## Возможности

- просмотр площадок и подбор площадки по вместимости;
- добавление площадки;
- просмотр предстоящих мероприятий и поиск по названию;
- создание мероприятия с проверкой вместимости и занятости площадки;
- проверка, открыта ли регистрация на мероприятие;
- регистрация участника; при отсутствии мест — лист ожидания;
- отмена регистрации с автоматическим переводом первого из листа ожидания;
- список участников мероприятия;
- статистика: число участников, лист ожидания, средняя заполненность,
  самое востребованное мероприятие;
- справка по пунктам меню.

## Объектная модель (ПР3)

Сущности предметной области представлены классами пакета `models/`.
Данные и поведение объединены в объектах; коллекции приложения —
`list[Venue]`, `list[Event]`, `list[Registration]`.

### Venue — площадка (`models/venues.py`)

Атрибуты: `id`, `name`, `address`, `capacity`.
Методы: `can_host(people_count)` — вмещает ли площадка людей;
`validate_capacity()` (`@staticmethod`) — проверка вместимости;
`from_data()` (`@classmethod`) — создание из записи JSON; `__str__()`.

### Event — мероприятие (`models/events.py`)

Атрибуты: `id`, `title`, `venue` (объект `Venue`), `starts_at`, `ends_at`,
`capacity`, `is_published`.
Методы: `fits_venue()`, `overlaps()` — пересечение по времени,
`days_until()`, `is_registration_open()`, `__str__()`.

### Registration — регистрация участника (`models/registrations.py`)

Атрибуты: `id`, `event` (объект `Event`), `participant`, `email`,
`registered_at`, `status` (`registered`, `waitlist`, `cancelled`).
Методы: `is_active()`, `cancel()`, `confirm()`, `__str__()`.

### Взаимодействие объектов

```text
Registration ──event──▶ Event ──venue──▶ Venue
```

Регистрация хранит ссылку на объект мероприятия, а мероприятие — на объект
площадки, поэтому `registration.event.venue.name` доступно напрямую.
Отмена регистрации меняет её статус, объект остаётся в коллекции. Функции
модулей (`add_venue()`, `add_event()`, `register_participant()`,
`cancel_registration()`, `get_statistics()` и др.) работают с коллекциями
объектов и вызывают методы классов, не дублируя их логику.

## Веб-интерфейс на Django (ПР5, ПР6)

Используются Django 5.2, Django Template Language, HTML5, CSS, JavaScript и
Bootstrap 5.3 (через CDN). Веб-страницы получают данные из базы SQLite SQL-запросами
(см. ниже); Django ORM пока не используется, веб-формы ещё не реализованы.

Django-проект `eventmanager` включает четыре приложения: `homepage` (главная,
статические файлы), `venues` (площадки), `events` (мероприятия),
`registrations` (регистрации). Отдельного приложения для пользователей нет:
участники — это регистрации, встроенная модель `User` Django не нужна.

| URL | Имя маршрута | View-функция | Назначение |
|-----|--------------|--------------|------------|
| `/` | `homepage:index` | `homepage.views.index` | главная страница |
| `/venues/` | `venues:list` | `venues.views.venues` | список площадок |
| `/venues/available/` | `venues:available` | `venues.views.available_venues` | свободные площадки на дату |
| `/venues/<int:venue_id>/` | `venues:detail` | `venues.views.venue_detail` | площадка и занятость сегодня |
| `/events/` | `events:list` | `events.views.events` | мероприятия по датам |
| `/events/<int:event_id>/` | `events:detail` | `events.views.event_detail` | свободные места, статус регистрации |
| `/registrations/` | `registrations:list` | `registrations.views.registrations` | список регистраций |
| `/registrations/statistics/` | `registrations:statistics` | `registrations.views.statistics` | статистика |
| `/registrations/<int:registration_id>/` | `registrations:detail` | `registrations.views.registration_detail` | регистрация |

Маршрутизация двухуровневая: `eventmanager/urls.py` подключает `urls.py`
приложений через `include()`; у каждого приложения есть пространство имён
(`app_name`). Для адресов без маршрута задан `handler404`.

### Шаблоны и статические файлы (ПР6)

- `templates/base.html` — базовый шаблон: блоки `title` и `content`,
  Bootstrap, собственные CSS и JavaScript, логотип, навигация, подвал;
- `templates/includes/navigation.html` — навигация со ссылками `{% url %}`;
- `templates/404.html` — страница ошибки 404;
- шаблоны приложений наследуют базовый через `{% extends %}`:
  `homepage/index.html`, `venues/venue_list.html`, `venue_detail.html`,
  `events/event_list.html`, `event_detail.html`,
  `registrations/registration_list.html`, `registration_detail.html`;
- включаемые фрагменты (`{% include %}`): `venues/includes/venue_card.html`,
  `events/includes/event_card.html`,
  `registrations/includes/registration_status.html` — один фрагмент статуса
  используется и в списке, и на странице регистрации;
- view-функции готовят контекст и вызывают `render()`, HTML в Python не
  формируется; если объект не найден, в шаблон передаётся `None`, а ответ
  получает код 404;
- в шаблонах используются циклы `{% for %}…{% empty %}`, условия `{% if %}`,
  фильтры `length`, `default`, `date`;
- статика приложения `homepage`: `static/homepage/css/style.css`,
  `js/main.js` (текущий год в подвале), `img/logo.png`.

Страницы открыты без авторизации; e-mail участников в веб-интерфейсе не
выводятся. Пользователи и разграничение доступа запланированы.

## База данных SQLite и SQL (ПР7)

Файл базы — `data/event_manager.sqlite`. Работа ведётся через стандартный
модуль `sqlite3`, без Django ORM. Структура (`sql/schema.sql`):

| Таблица | Поля | Ключи и ограничения |
|---------|------|---------------------|
| `venues` | `id`, `name`, `address`, `capacity` | PK `id`; `name` уникально; `capacity > 0` |
| `events` | `id`, `title`, `venue_id`, `starts_at`, `ends_at`, `capacity`, `is_published` | PK `id`; FK `venue_id → venues.id` |
| `registrations` | `id`, `event_id`, `participant`, `email`, `status`, `registered_at` | PK `id`; FK `event_id → events.id`; `status` ∈ {registered, waitlist, cancelled} |

Связи: на одной площадке проходит несколько мероприятий; на мероприятие
приходится несколько регистраций. Даты хранятся строками ISO 8601, логический
признак `is_published` — числом 0/1.

- `sql/schema.sql` — создание таблиц;
- `sql/queries.sql` — 14 проверенных запросов с комментариями: выборки,
  `WHERE`, `JOIN` (в том числе трёх таблиц), агрегаты `COUNT`/`AVG`/`MAX`,
  `GROUP BY`, `HAVING`, `LIMIT`;
- `db/database.py` — `get_connection()`: `PRAGMA foreign_keys = ON` и
  `sqlite3.Row` (доступ к полям по имени, в том числе из шаблонов);
- `db/import_json.py` — создаёт схему и переносит данные из JSON
  (`executemany`, откат при ошибке; импорт можно повторять).

Значения всегда передаются параметрами `?`, а не подстановкой в текст запроса.

Создание и наполнение базы с нуля:

```bash
python -m db.import_json
sqlite3 data/event_manager.sqlite    # проверка запросов в SQLite CLI
```

Страницы, использующие SQL: `/venues/` и `/venues/<id>/`, `/events/` и
`/events/<id>/`, `/registrations/` (активные регистрации, JOIN трёх таблиц),
`/registrations/<id>/`, `/venues/available/?date=ГГГГ-ММ-ДД` (поиск свободных
площадок на дату) и `/registrations/statistics/` (статистика: участники,
заполненность мероприятий, мероприятия по площадкам, листы ожидания).
JSON-файлы остаются источником данных консольной версии и импорта.

## Структура проекта

- `manage.py`, `eventmanager/` — Django-проект (настройки, корневые маршруты);
- `homepage/`, `venues/`, `events/`, `registrations/` — Django-приложения
  (`views.py`, `urls.py`, `templates/`);
- `templates/` — базовый шаблон, навигация и страница 404;
- `main.py` — консольная версия приложения (сохранена);
- `models/` — классы и функции предметной области:
  `venues.py`, `events.py`, `registrations.py`;
- `storage.py` — преобразование JSON ↔ объекты (в JSON хранятся
  идентификаторы `venue_id` и `event_id`, при загрузке восстанавливаются
  ссылки на объекты);
- `utils.py` — идентификаторы, разбор дат, безопасный ввод;
- `db/`, `sql/` — подключение к SQLite, импорт из JSON, схема и запросы;
- `data/` — JSON-файлы данных и база `event_manager.sqlite`;
- `tests/` — автоматизированные тесты pytest, включая проверку страниц.

## Формат данных

Данные хранятся в каталоге `data/` в виде списков записей; при запуске они
преобразуются в объекты, а после каждого изменения объекты сохраняются
заново. Дата и время — строки
ISO 8601.

`data/venues.json`:

```json
[{"id": 1, "name": "Актовый зал", "address": "пр. Вернадского, 78", "capacity": 120}]
```

`data/events.json`:

```json
[{"id": 1, "title": "Лекция «Введение в Django»", "venue_id": 1,
  "starts_at": "2026-10-15T18:00", "ends_at": "2026-10-15T19:30",
  "capacity": 100, "is_published": true}]
```

`data/registrations.json` (status: `registered`, `waitlist`, `cancelled`):

```json
[{"id": 1, "event_id": 1, "participant": "Иван Петров",
  "email": "petrov@edu.mirea.ru", "status": "registered",
  "registered_at": "2026-09-20T10:15"}]
```

Отсутствующий файл считается пустым списком; повреждённый файл не приводит к
аварийному завершению — программа сообщает об ошибке.

## Требования

- Python 3.10+;
- Django 5.2;
- pytest;
- flake8.

Установка зависимостей:

```bash
python3 -m venv .venv
source .venv/bin/activate
pip install -r requirements.txt
```

## Запуск программы

Веб-версия (Django):

```bash
python manage.py runserver
```

Затем открыть http://127.0.0.1:8000/. Консольная версия:

```bash
python main.py
```

## Запуск тестов

```bash
pytest
```

## Проверка качества кода

```bash
flake8
```

## План развития

- модели Django и ORM вместо прямых SQL-запросов;
- пользователи и разграничение доступа;
- REST API;
- контейнеризация в Docker и CI/CD.
