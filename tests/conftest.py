
import pytest
import database


@pytest.fixture
def test_db(tmp_path, monkeypatch):
    """
    Use a temporary SQLite database
    instead of the real application database.
    """

    temporary_db = tmp_path / "test_voice_assistant.db"

    monkeypatch.setattr(
        database,
        "DB_PATH",
        temporary_db
    )

    database.initialize_database()

    return temporary_db
