
import database


def test_save_and_get_notes(test_db):
    note_id = database.save_note(
        "Learn Python testing"
    )

    notes = database.get_notes()

    assert note_id > 0
    assert len(notes) == 1
    assert notes[0]["content"] == "Learn Python testing"


def test_create_task(test_db):
    task_id = database.create_task(
        "Complete AI Voice Assistant"
    )

    tasks = database.get_tasks("pending")

    assert task_id > 0
    assert len(tasks) == 1
    assert tasks[0]["status"] == "pending"


def test_complete_task(test_db):
    task_id = database.create_task(
        "Test task completion"
    )

    success = database.complete_task(task_id)

    assert success is True

    completed_tasks = database.get_tasks("completed")

    assert len(completed_tasks) == 1
    assert completed_tasks[0]["id"] == task_id


def test_complete_nonexistent_task(test_db):
    success = database.complete_task(999999)

    assert success is False


def test_save_and_load_conversation(test_db):
    database.save_message(
        "user",
        "Hello assistant"
    )

    database.save_message(
        "assistant",
        "Hello!"
    )

    messages = database.load_messages()

    assert len(messages) == 2
    assert messages[0]["role"] == "user"
    assert messages[1]["role"] == "assistant"


def test_clear_conversation(test_db):
    database.save_message(
        "user",
        "Test message"
    )

    database.clear_messages()

    assert database.load_messages() == []
