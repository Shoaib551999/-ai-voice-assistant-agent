
from database import (
    save_note,
    get_notes,
    create_task,
    get_tasks,
    complete_task
)


# ==========================================
# AI TOOL DEFINITIONS
# ==========================================

TOOLS = [
    # --------------------------------------
    # Tool 1: Save Note
    # --------------------------------------
    {
        "type": "function",
        "function": {
            "name": "save_note",
            "description": (
                "Save a personal note when the user "
                "explicitly asks to save or remember something."
            ),
            "parameters": {
                "type": "object",
                "properties": {
                    "content": {
                        "type": "string",
                        "description": "The text of the note to save."
                    }
                },
                "required": ["content"],
                "additionalProperties": False
            }
        }
    },

    # --------------------------------------
    # Tool 2: Get Notes
    # --------------------------------------
    {
        "type": "function",
        "function": {
            "name": "get_notes",
            "description": (
                "Retrieve personal notes previously saved "
                "by the user."
            ),
            "parameters": {
                "type": "object",
                "properties": {},
                "additionalProperties": False
            }
        }
    },

    # --------------------------------------
    # Tool 3: Create Task
    # --------------------------------------
    {
        "type": "function",
        "function": {
            "name": "create_task",
            "description": (
                "Create a new task when the user explicitly "
                "asks to add something to their task list."
            ),
            "parameters": {
                "type": "object",
                "properties": {
                    "title": {
                        "type": "string",
                        "description": "Title of the new task."
                    }
                },
                "required": ["title"],
                "additionalProperties": False
            }
        }
    },

    # --------------------------------------
    # Tool 4: Get Tasks
    # --------------------------------------
    {
        "type": "function",
        "function": {
            "name": "get_tasks",
            "description": (
                "Retrieve tasks filtered by pending, "
                "completed, or all statuses."
            ),
            "parameters": {
                "type": "object",
                "properties": {
                    "status": {
                        "type": "string",
                        "enum": [
                            "pending",
                            "completed",
                            "all"
                        ],
                        "description": "Task status filter."
                    }
                },
                "required": ["status"],
                "additionalProperties": False
            }
        }
    },

    # --------------------------------------
    # Tool 5: Complete Task
    # --------------------------------------
    {
        "type": "function",
        "function": {
            "name": "complete_task",
            "description": (
                "Mark an existing task as completed using "
                "its exact numeric task ID. "
                "Do not guess task IDs."
            ),
            "parameters": {
                "type": "object",
                "properties": {
                    "task_id": {
                        "type": "integer",
                        "description": (
                            "The exact ID of the task to complete."
                        )
                    }
                },
                "required": ["task_id"],
                "additionalProperties": False
            }
        }
    }
]


# ==========================================
# TOOL EXECUTION FUNCTION
# ==========================================

def execute_tool(name, arguments):
    """
    Execute an AI-requested tool operation.

    Args:
        name: Name of the requested tool.
        arguments: Dictionary containing tool arguments.

    Returns:
        Dictionary containing the operation result.
    """

    if not isinstance(arguments, dict):
        raise ValueError("Tool arguments must be a dictionary.")

    # --------------------------------------
    # Execute Tool 1: Save Note
    # --------------------------------------

    if name == "save_note":
        content = arguments.get("content", "")

        if not isinstance(content, str):
            raise ValueError("Note content must be text.")

        if not content.strip():
            raise ValueError("Note cannot be empty.")

        if len(content) > 2000:
            raise ValueError("Note is too long.")

        note_id = save_note(content)

        return {
            "success": True,
            "note_id": note_id,
            "message": "Note saved successfully."
        }

    # --------------------------------------
    # Execute Tool 2: Get Notes
    # --------------------------------------

    elif name == "get_notes":
        notes = get_notes()

        return {
            "success": True,
            "notes": notes,
            "count": len(notes)
        }

    # --------------------------------------
    # Execute Tool 3: Create Task
    # --------------------------------------

    elif name == "create_task":
        title = arguments.get("title", "")

        if not isinstance(title, str):
            raise ValueError("Task title must be text.")

        if not title.strip():
            raise ValueError("Task title cannot be empty.")

        if len(title) > 500:
            raise ValueError("Task title is too long.")

        task_id = create_task(title)

        return {
            "success": True,
            "task_id": task_id,
            "message": "Task created successfully."
        }

    # --------------------------------------
    # Execute Tool 4: Get Tasks
    # --------------------------------------

    elif name == "get_tasks":
        status = arguments.get("status", "all")

        if status not in ["pending", "completed", "all"]:
            raise ValueError("Invalid task status.")

        db_status = None if status == "all" else status

        tasks = get_tasks(db_status)

        return {
            "success": True,
            "tasks": tasks,
            "count": len(tasks),
            "status_filter": status
        }

    # --------------------------------------
    # Execute Tool 5: Complete Task
    # --------------------------------------

    elif name == "complete_task":
        task_id = arguments.get("task_id")

        if type(task_id) is not int or task_id <= 0:
            raise ValueError("A valid numeric task ID is required.")

        completed = complete_task(task_id)

        if completed:
            return {
                "success": True,
                "task_id": task_id,
                "message": "Task completed successfully."
            }


        return {
            "success": False,
            "task_id": task_id,
            "message": "Task not found or already completed."
        }

    # --------------------------------------
    # Handle Unknown Tools
    # --------------------------------------

    else:
        raise ValueError(f"Unknown tool requested: {name}")