import json
import sys
import time
from pathlib import Path

ROOT_DIR = Path(__file__).resolve().parent.parent
sys.path.insert(0, str(ROOT_DIR))

from ids import IDS

INPUT_PATH = Path("/app/data/validated_data.json")
OUTPUT_PATH = Path("/app/data/alerts.json")


def to_dashboard_alert(alert):
    return {
        "type": alert.get("alert_type", "Unknown"),
        "device": alert.get("device_id", "Unknown"),
        "severity": alert.get("severity", "Unknown"),
        "timestamp": alert.get("timestamp", ""),
        "description": alert.get("description", ""),
        "recommended_action": alert.get("recommended_action", ""),
        "anomaly_score": alert.get("anomaly_score", 0),
    }


def load_messages(path):
    if not path.exists():
        return []

    try:
        with open(path, "r", encoding="utf-8") as f:
            content = f.read().strip()
            if not content:
                return []
            return json.loads(content)
    except Exception as e:
        print(f"Error reading {path}: {e}")
        return []


def save_alerts(path, alerts):
    with open(path, "w", encoding="utf-8") as f:
        json.dump(alerts, f, indent=2)


if __name__ == "__main__":
    ids = IDS()

    while True:
        messages = load_messages(INPUT_PATH)

        dashboard_alerts = []
        message_count = 0

        for message in messages:
            message_count += 1
            alert = ids.detect(message)
            if alert is not None:
                dashboard_alerts.append(to_dashboard_alert(alert))

        save_alerts(OUTPUT_PATH, dashboard_alerts)

        print(f"Analyzed {message_count} messages", flush=True)
        print(f"Generated {len(dashboard_alerts)} alerts", flush=True)
        print(f"Alerts saved to {OUTPUT_PATH}", flush=True)

        time.sleep(2)