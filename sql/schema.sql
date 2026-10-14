-- ==========================================
-- Event Manager: структура базы данных
-- ==========================================
-- Даты и время хранятся строками ISO 8601 (ГГГГ-ММ-ДДTЧЧ:ММ): такой формат
-- допускает сравнение и сортировку средствами SQL.

CREATE TABLE IF NOT EXISTS venues (
    id INTEGER PRIMARY KEY,
    name TEXT NOT NULL UNIQUE,
    address TEXT NOT NULL,
    capacity INTEGER NOT NULL CHECK (capacity > 0)
);

CREATE TABLE IF NOT EXISTS events (
    id INTEGER PRIMARY KEY,
    title TEXT NOT NULL,
    venue_id INTEGER NOT NULL,
    starts_at TEXT NOT NULL,
    ends_at TEXT NOT NULL,
    capacity INTEGER NOT NULL CHECK (capacity > 0),
    is_published INTEGER NOT NULL DEFAULT 1,
    FOREIGN KEY (venue_id) REFERENCES venues(id)
);

CREATE TABLE IF NOT EXISTS registrations (
    id INTEGER PRIMARY KEY,
    event_id INTEGER NOT NULL,
    participant TEXT NOT NULL,
    email TEXT NOT NULL,
    status TEXT NOT NULL
        CHECK (status IN ('registered', 'waitlist', 'cancelled')),
    registered_at TEXT NOT NULL,
    FOREIGN KEY (event_id) REFERENCES events(id)
);
