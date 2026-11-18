
from log_reader import read_agent_logs

logs = read_agent_logs()

print(f"Total log entries: {len(logs)}")

for record in logs[-5:]:
    print(record)
