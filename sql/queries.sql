-- ==========================================
-- Event Manager: SQL-запросы проекта
-- Значения подставляются параметрами (?), а не склеиваются в текст запроса.
-- ==========================================

-- 1. Выборка: список площадок по названию
SELECT id, name, address, capacity
FROM venues
ORDER BY name;

-- 2. Выборка: все мероприятия по времени начала
SELECT id, title, venue_id, starts_at, ends_at, capacity
FROM events
ORDER BY starts_at;

-- 3. Выборка с ограничением: три ближайших предстоящих мероприятия
-- (параметр: текущие дата и время, ГГГГ-ММ-ДДTЧЧ:ММ)
SELECT id, title, starts_at
FROM events
WHERE is_published = 1 AND starts_at >= ?
ORDER BY starts_at
LIMIT 3;

-- 4. WHERE: площадки, вмещающие не меньше заданного числа человек
-- (параметр: минимальная вместимость)
SELECT id, name, capacity
FROM venues
WHERE capacity >= ?
ORDER BY capacity DESC;

-- 5. WHERE: мероприятия, начинающиеся с заданной даты
-- (параметр: дата ГГГГ-ММ-ДД)
SELECT id, title, starts_at
FROM events
WHERE starts_at >= ?
ORDER BY starts_at;

-- 6. WHERE: активные регистрации (участники и лист ожидания) на мероприятие
-- (параметр: id мероприятия)
SELECT id, participant, status, registered_at
FROM registrations
WHERE event_id = ? AND status IN ('registered', 'waitlist')
ORDER BY status DESC, registered_at;

-- 7. JOIN: мероприятия с названием и адресом площадки
SELECT
    events.id,
    events.title,
    events.starts_at,
    venues.name AS venue_name,
    venues.address
FROM events
JOIN venues ON events.venue_id = venues.id
ORDER BY events.starts_at;

-- 8. JOIN трёх таблиц: активные регистрации с мероприятием и площадкой
SELECT
    registrations.id,
    registrations.participant,
    registrations.status,
    events.title AS event_title,
    venues.name AS venue_name
FROM registrations
JOIN events ON registrations.event_id = events.id
JOIN venues ON events.venue_id = venues.id
WHERE registrations.status != 'cancelled'
ORDER BY registrations.id;

-- 9. Свободные площадки на выбранную дату: нет мероприятий в этот день
-- (параметр: дата ГГГГ-ММ-ДД)
SELECT id, name, capacity
FROM venues
WHERE id NOT IN (
    SELECT venue_id
    FROM events
    WHERE substr(starts_at, 1, 10) = ?
)
ORDER BY name;

-- 10. Агрегат: число подтверждённых участников и участников в листе ожидания
SELECT
    COUNT(CASE WHEN status = 'registered' THEN 1 END) AS registered,
    COUNT(CASE WHEN status = 'waitlist' THEN 1 END) AS waitlist
FROM registrations;

-- 11. Агрегат: число мероприятий, средняя и максимальная вместимость
SELECT
    COUNT(*) AS events_count,
    ROUND(AVG(capacity), 1) AS average_capacity,
    MAX(capacity) AS max_capacity
FROM events;

-- 12. GROUP BY: число подтверждённых участников на каждом мероприятии
-- (LEFT JOIN сохраняет мероприятия без регистраций)
SELECT
    events.title AS event_title,
    events.capacity,
    COUNT(registrations.id) AS registered_count
FROM events
LEFT JOIN registrations
    ON registrations.event_id = events.id
    AND registrations.status = 'registered'
GROUP BY events.id, events.title, events.capacity
ORDER BY registered_count DESC;

-- 13. GROUP BY: число мероприятий на каждой площадке
SELECT
    venues.name AS venue_name,
    COUNT(events.id) AS events_count
FROM venues
LEFT JOIN events ON events.venue_id = venues.id
GROUP BY venues.id, venues.name
ORDER BY events_count DESC, venues.name;

-- 14. HAVING: мероприятия, на которые есть лист ожидания
SELECT
    events.title AS event_title,
    COUNT(registrations.id) AS waitlist_count
FROM events
JOIN registrations ON registrations.event_id = events.id
WHERE registrations.status = 'waitlist'
GROUP BY events.id, events.title
HAVING COUNT(registrations.id) >= 1;
