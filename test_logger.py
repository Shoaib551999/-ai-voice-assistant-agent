
from agent_logger import log_tool_execution

log_tool_execution(
    tool_name="get_tasks",
    success=True,
    duration_ms=15.4
)

log_tool_execution(
    tool_name="complete_task",
    success=True,
    duration_ms=8.2
)

log_tool_execution(
    tool_name="save_note",
    success=False,
    duration_ms=23.1
)

print("Agent logging test completed!")
