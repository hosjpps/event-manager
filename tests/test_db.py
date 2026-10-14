import re
import sqlite3
from pathlib import Path

import pytest

from db.database import get_connection
from db.import_json import ROOT, import_all

QUERIES_FILE = ROOT / "sql" / "queries.sql"


@pytest.fixture
def conn(tmp_path: Path):
    connection = get_connection(tmp_path / "test.sqlite")
    import_all(connection)
    connection.commit()
    yield connection
    connection.close()


def count(conn: sqlite3.Connection, table: str) -> int:
    return conn.execute(f"SELECT COUNT(*) FROM {table}").fetchone()[0]


def test_import_copies_all_json_records(conn):
    assert count(conn, "venues") == 3
    assert count(conn, "events") == 3
    assert count(conn, "registrations") == 5


def test_import_can_be_repeated(conn):
    import_all(conn)
    assert count(conn, "registrations") == 5


def test_rows_are_accessible_by_name(conn):
    row = conn.execute("SELECT * FROM venues WHERE id = 1").fetchone()
    assert row["name"] == "Актовый зал"
    assert row["capacity"] == 120


def test_foreign_keys_are_enforced(conn):
    with pytest.raises(sqlite3.IntegrityError):
        conn.execute(
            "INSERT INTO events "
            "(title, venue_id, starts_at, ends_at, capacity) "
            "VALUES ('X', 99, '2026-10-01T10:00', '2026-10-01T11:00', 5)"
        )


def test_unknown_registration_status_is_rejected(conn):
    with pytest.raises(sqlite3.IntegrityError):
        conn.execute(
            "INSERT INTO registrations "
            "(event_id, participant, email, status, registered_at) "
            "VALUES (1, 'A', 'a@test.ru', 'unknown', '2026-10-01T10:00')"
        )


def test_every_query_in_queries_sql_runs(conn):
    text = re.sub(r"--.*", "", QUERIES_FILE.read_text(encoding="utf-8"))
    statements = [s for s in text.split(";") if "SELECT" in s]
    assert len(statements) >= 10
    for statement in statements:
        params = ["2026-10-20"] * statement.count("?")
        conn.execute(statement, params).fetchall()


def test_queries_file_covers_required_kinds():
    text = QUERIES_FILE.read_text(encoding="utf-8")
    for keyword in ("WHERE", "JOIN", "COUNT(", "GROUP BY"):
        assert text.count(keyword) >= 2
    assert "HAVING" in text


def test_free_venues_query_skips_busy_venue(conn):
    rows = conn.execute(
        "SELECT id FROM venues WHERE id NOT IN ("
        "SELECT venue_id FROM events WHERE substr(starts_at, 1, 10) = ?)",
        ["2026-10-15"],
    ).fetchall()
    assert [r["id"] for r in rows] == [2, 3]
