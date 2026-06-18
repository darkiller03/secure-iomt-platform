import json
import sys
from pathlib import Path

ROOT_DIR = Path(__file__).resolve().parent.parent
sys.path.insert(0, str(ROOT_DIR))

from ids import IDS

INPUT_PATH = ROOT_DIR / "data" / "validated_data.json"
OUTPUT_PATH = ROOT_DIR / "data" / "alerts.json"


def to_dashboard_alert(alert):
    return {
        "type": alert.get("alert_type", "Unknown"),
        "device": alert.get("device_id", "Unknown"),
        "severity": alert.get("severity", "Unknown").title(),
        "timestamp": alert.get("timestamp", ""),
        "description": alert.get("description", ""),
        "recommended_action": alert.get("recommended_action", ""),
    }


def load_messages(path):
    with open(path, "r", encoding="utf-8") as f:
        return json.load(f)


def save_alerts(path, alerts):
    with open(path, "w", encoding="utf-8") as f:
        json.dump(alerts, f, indent=2)


if __name__ == "__main__":
    messages = load_messages(INPUT_PATH)
    ids = IDS()
    dashboard_alerts = []
    message_count = 0

    for message in messages:
        message_count += 1
        alert = ids.detect(message)
        if alert is not None:
            dashboard_alerts.append(to_dashboard_alert(alert))

    # End-of-file checks (e.g., Silent Device Detection)
    # Determine latest timestamp in dataset
    latest_ts = None
    for m in messages:
        ts = m.get("timestamp")
        if ts:
            try:
                # parse ISO timestamp
                from datetime import datetime

                t = datetime.fromisoformat(ts.replace("Z", "+00:00")).timestamp()
            except Exception:
                t = None
            if t is not None:
                if latest_ts is None or t > latest_ts:
                    latest_ts = t

    if latest_ts is None:
        latest_ts = __import__("time").time()

    eof_alerts = ids.finalize(latest_ts)
    for a in eof_alerts:
        dashboard_alerts.append(to_dashboard_alert(a))

    save_alerts(OUTPUT_PATH, dashboard_alerts)

    print(f"Analyzed {message_count} messages")
    print(f"Generated {len(dashboard_alerts)} alerts")
    print(f"Alerts saved to {OUTPUT_PATH}")
