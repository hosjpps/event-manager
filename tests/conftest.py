import pytest
from django.core.management import call_command

from db.import_sqlite_to_orm import main as import_from_pr7_database


@pytest.fixture
def sample_data(db):
    """Тестовая база: данные ПР7 (перенос скриптом) и демо-фикстура."""
    import_from_pr7_database()
    call_command("loaddata", "demo", verbosity=0)
