"""Перенос данных из JSON-файлов в базу SQLite."""
import json
import sqlite3
from pathlib import Path

from db.database import get_connection

ROOT = Path(__file__).resolve().parent.parent
DATA_DIR = ROOT / "data"
SCHEMA_FILE = ROOT / "sql" / "schema.sql"


def load_json(filename: Path) -> list[dict]:
    with open(filename, encoding="utf-8") as file:
        return json.load(file)


def create_schema(conn: sqlite3.Connection) -> None:
    """Создать таблицы, если их ещё нет."""
    conn.executescript(SCHEMA_FILE.read_text(encoding="utf-8"))


def clear_tables(conn: sqlite3.Connection) -> None:
    """Очистить таблицы (сначала зависимые): импорт можно повторить."""
    conn.execute("DELETE FROM registrations")
    conn.execute("DELETE FROM events")
    conn.execute("DELETE FROM venues")


def import_venues(conn: sqlite3.Connection, data_dir: Path) -> None:
    venues = load_json(data_dir / "venues.json")
    conn.executemany(
        """
        INSERT INTO venues (id, name, address, capacity)
        VALUES (?, ?, ?, ?)
        """,
        [(v["id"], v["name"], v["address"], v["capacity"]) for v in venues],
    )


def import_events(conn: sqlite3.Connection, data_dir: Path) -> None:
    events = load_json(data_dir / "events.json")
    conn.executemany(
        """
        INSERT INTO events (
            id, title, venue_id, starts_at, ends_at, capacity, is_published
        )
        VALUES (?, ?, ?, ?, ?, ?, ?)
        """,
        [
            (
                e["id"], e["title"], e["venue_id"], e["starts_at"],
                e["ends_at"], e["capacity"], int(e["is_published"]),
            )
            for e in events
        ],
    )


def import_registrations(conn: sqlite3.Connection, data_dir: Path) -> None:
    registrations = load_json(data_dir / "registrations.json")
    conn.executemany(
        """
        INSERT INTO registrations (
            id, event_id, participant, email, status, registered_at
        )
        VALUES (?, ?, ?, ?, ?, ?)
        """,
        [
            (
                r["id"], r["event_id"], r["participant"], r["email"],
                r["status"], r["registered_at"],
            )
            for r in registrations
        ],
    )


def import_all(conn: sqlite3.Connection, data_dir: Path = DATA_DIR) -> None:
    """Создать схему и заново загрузить в неё данные из JSON."""
    create_schema(conn)
    clear_tables(conn)
    import_venues(conn, data_dir)
    import_events(conn, data_dir)
    import_registrations(conn, data_dir)


def main() -> None:
    conn = get_connection()
    try:
        import_all(conn)
        conn.commit()
    except Exception:
        conn.rollback()
        raise
    finally:
        conn.close()


if __name__ == "__main__":
    main()
