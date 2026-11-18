
from database import (
    initialize_database,
    save_message,
    load_messages
)

initialize_database()

save_message("user", "Hello AI assistant")
save_message("assistant", "Hello! How can I help you?")

messages = load_messages()

print("Saved conversation:")

for message in messages:
    print(f"{message['role']}: {message['content']}")
