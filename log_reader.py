
import re
from pathlib import Path

BASE_DIR = Path(__file__).resolve().parent
LOG_FILE = BASE_DIR / "logs" / "agent_execution.log"

LOG_PATTERN = re.compile(
    r"^(.*?) \| INFO \| "
    r"tool=([a-zA-Z_][a-zA-Z0-9_]*) \| "
    r"status=(SUCCESS|FAILED) \| "
    r"duration_ms=([0-9]+(?:\.[0-9]+)?)$"
)


def read_agent_logs():
    """
    Read execution logs and return
    structured records for Streamlit.
    """

    if not LOG_FILE.exists():
        return []

    records = []

    with open(LOG_FILE, "r", encoding="utf-8") as log_file:
        for line in log_file:
            match = LOG_PATTERN.match(line.strip())

            if not match:
                continue

            timestamp, tool, status, duration = match.groups()

            records.append({
                "Timestamp": timestamp,
                "Tool": tool,
                "Status": status,
                "Duration (ms)": float(duration)
            })

    return records
