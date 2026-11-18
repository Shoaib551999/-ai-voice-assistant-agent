
from database import (
    initialize_database,
    save_note,
    get_notes
)

initialize_database()

note_id = save_note(
    "I have an AI Engineer interview on Friday."
)

print(f"Note saved successfully! ID: {note_id}")

print("\nSaved Notes:")

for note in get_notes():
    print(f"{note['id']}: {note['content']}")
