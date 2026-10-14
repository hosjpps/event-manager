"""Подключение к базе данных SQLite проекта."""
import sqlite3
from pathlib import Path

ROOT = Path(__file__).resolve().parent.parent
DB_PATH = ROOT / "data" / "event_manager.sqlite"


def get_connection(path: Path = DB_PATH) -> sqlite3.Connection:
    """Открыть соединение: внешние ключи включены, поля доступны по имени."""
    conn = sqlite3.connect(path)
    conn.execute("PRAGMA foreign_keys = ON")
    conn.row_factory = sqlite3.Row
    return conn
