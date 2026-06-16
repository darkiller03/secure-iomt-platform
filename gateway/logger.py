import json
from datetime import datetime
from pathlib import Path

LOG_FILE = Path("data/logs.json")


def write_log(level, message):
    LOG_FILE.parent.mkdir(parents=True, exist_ok=True)

    log_entry = {
        "timestamp": datetime.now().isoformat(timespec="seconds"),
        "source": "Gateway",
        "level": level,
        "message": message
    }

    if LOG_FILE.exists():
        try:
            with open(LOG_FILE, "r", encoding="utf-8") as file:
                logs = json.load(file)
        except json.JSONDecodeError:
            logs = []
    else:
        logs = []

    logs.append(log_entry)

    with open(LOG_FILE, "w", encoding="utf-8") as file:
        json.dump(logs, file, indent=2)
