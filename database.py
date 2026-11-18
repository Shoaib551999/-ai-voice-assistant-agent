

import os
import sqlite3
from pathlib import Path

BASE_DIR = Path(__file__).resolve().parent

DB_PATH = Path(
    os.getenv(
        "VOICE_ASSISTANT_DB_PATH",
        str(BASE_DIR / "voice_assistant.db")
    )
)

DB_PATH.parent.mkdir(
    parents=True,
    exist_ok=True
)



def get_connection():
    return sqlite3.connect(DB_PATH)



def initialize_database():
    with get_connection() as conn:

        # Conversation history
        conn.execute("""
            CREATE TABLE IF NOT EXISTS conversations (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                role TEXT NOT NULL
                    CHECK(role IN ('user', 'assistant')),
                content TEXT NOT NULL,
                created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
            )
        """)

        # Task management table
        conn.execute("""
            CREATE TABLE IF NOT EXISTS tasks (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                title TEXT NOT NULL,
                status TEXT NOT NULL DEFAULT 'pending'
                    CHECK(status IN ('pending', 'completed')),
                created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
                completed_at TIMESTAMP
            )
        """)

        # Personal notes
        conn.execute("""
            CREATE TABLE IF NOT EXISTS notes (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                content TEXT NOT NULL,
                created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
            )
        """)



def save_message(role, content):
    with get_connection() as conn:
        conn.execute(
            "INSERT INTO conversations (role, content) VALUES (?, ?)",
            (role, content)
        )


def load_messages():
    with get_connection() as conn:
        rows = conn.execute(
            """
            SELECT role, content
            FROM conversations
            ORDER BY id ASC
            """
        ).fetchall()

    return [
        {"role": role, "content": content}
        for role, content in rows
    ]


def clear_messages():
    with get_connection() as conn:
        conn.execute("DELETE FROM conversations")

# -----------------------------
# Save personal notes
# -----------------------------

def save_note(content):
    content = content.strip()

    if not content:
        raise ValueError("Note cannot be empty.")

    with get_connection() as conn:
        cursor = conn.execute(
            "INSERT INTO notes (content) VALUES (?)",
            (content,)
        )
        return cursor.lastrowid


# -----------------------------
# Retrieve saved notes
# -----------------------------

def get_notes():
    with get_connection() as conn:
        rows = conn.execute("""
            SELECT id, content, created_at
            FROM notes
            ORDER BY id DESC
        """).fetchall()

    return [
        {
            "id": row[0],
            "content": row[1],
            "created_at": row[2]
        }
        for row in rows
    ]

# -----------------------------
# Create a new task
# -----------------------------

def create_task(title):
    title = title.strip()

    if not title:
        raise ValueError("Task title cannot be empty.")

    if len(title) > 500:
        raise ValueError("Task title is too long.")

    with get_connection() as conn:
        cursor = conn.execute(
            "INSERT INTO tasks (title) VALUES (?)",
            (title,)
        )
        return cursor.lastrowid


# -----------------------------
# Retrieve tasks
# -----------------------------

def get_tasks(status=None):
    if status not in (None, "pending", "completed"):
        raise ValueError("Invalid task status.")

    with get_connection() as conn:
        if status:
            rows = conn.execute(
                """
                SELECT id, title, status
                FROM tasks
                WHERE status = ?
                ORDER BY id DESC
                """,
                (status,)
            ).fetchall()
        else:
            rows = conn.execute(
                """
                SELECT id, title, status
                FROM tasks
                ORDER BY id DESC
                """
            ).fetchall()

    return [
        {
            "id": row[0],
            "title": row[1],
            "status": row[2]
        }
        for row in rows
    ]


# -----------------------------
# Complete a task
# -----------------------------

def complete_task(task_id):
    with get_connection() as conn:
        cursor = conn.execute(
            """
            UPDATE tasks
            SET status = 'completed',
                completed_at = CURRENT_TIMESTAMP
            WHERE id = ? AND status = 'pending'
            """,
            (task_id,)
        )

        return cursor.rowcount > 0
