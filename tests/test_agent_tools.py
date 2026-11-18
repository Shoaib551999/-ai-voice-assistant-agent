
import pytest

from agent_tools import execute_tool


def test_save_note_tool(test_db):
    result = execute_tool(
        "save_note",
        {"content": "Prepare for interview"}
    )

    assert result["success"] is True
    assert result["note_id"] > 0


def test_get_notes_tool(test_db):
    execute_tool(
        "save_note",
        {"content": "Learn machine learning"}
    )

    result = execute_tool(
        "get_notes",
        {}
    )

    assert result["success"] is True
    assert result["count"] == 1


def test_create_task_tool(test_db):
    result = execute_tool(
        "create_task",
        {"title": "Complete project"}
    )

    assert result["success"] is True
    assert result["task_id"] > 0


def test_get_tasks_tool(test_db):
    execute_tool(
        "create_task",
        {"title": "Test task"}
    )

    result = execute_tool(
        "get_tasks",
        {"status": "pending"}
    )

    assert result["success"] is True
    assert result["count"] == 1


def test_complete_task_tool(test_db):
    created = execute_tool(
        "create_task",
        {"title": "Complete me"}
    )

    result = execute_tool(
        "complete_task",
        {"task_id": created["task_id"]}
    )

    assert result["success"] is True


def test_reject_empty_note(test_db):
    with pytest.raises(ValueError):
        execute_tool(
            "save_note",
            {"content": "   "}
        )


def test_reject_invalid_task_id(test_db):
    with pytest.raises(ValueError):
        execute_tool(
            "complete_task",
            {"task_id": -1}
        )


def test_reject_unknown_tool(test_db):
    with pytest.raises(ValueError):
        execute_tool(
            "unknown_tool",
            {}
        )
