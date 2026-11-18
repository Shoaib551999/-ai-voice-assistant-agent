
from database import (
    initialize_database,
    create_task,
    get_tasks,
    complete_task
)

initialize_database()

# Create tasks
task1 = create_task("Prepare for AI Engineer interview")
task2 = create_task("Complete Python Voice Assistant")

print("\nCreated Tasks:")
for task in get_tasks():
    print(task)

# Complete the first task
result = complete_task(task1)
print("\nTask completed:", result)

print("\nPending Tasks:")
for task in get_tasks("pending"):
    print(task)

print("\nCompleted Tasks:")
for task in get_tasks("completed"):
    print(task)
