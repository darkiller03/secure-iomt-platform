"""
Validate IDS alert output derived from the multi-device dataset.

This script loads multi_device_dataset.json, runs the IDS on each message,
writes alert_payload.json, and validates that each generated alert matches
the required alert schema.
"""
import json
from typing import Any, Dict, List, Tuple

from ids import IDS

GATEWAY_SAMPLE_PATH = "multi_device_dataset.json"
ALERT_PAYLOAD_PATH = "alert_payload.json"

REQUIRED_FIELDS = [
    "alert_id",
    "timestamp",
    "device_id",
    "alert_type",
    "severity",
    "anomaly_score",
    "description",
    "recommended_action",
]

EXPECTED_TYPES = {
    "alert_id": str,
    "timestamp": str,
    "device_id": str,
    "alert_type": str,
    "severity": str,
    "anomaly_score": (int, float),
    "description": str,
    "recommended_action": str,
}


def load_json(path: str) -> Any:
    with open(path, "r", encoding="utf-8") as f:
        return json.load(f)


def validate_alert(alert: Dict[str, Any]) -> Tuple[bool, str]:
    if not isinstance(alert, dict):
        return False, "Alert must be a JSON object"

    missing = [field for field in REQUIRED_FIELDS if field not in alert]
    if missing:
        return False, f"Missing required fields: {missing}"

    extra = [field for field in alert if field not in REQUIRED_FIELDS]
    if extra:
        return False, f"Unexpected fields present: {extra}"

    for field, expected_type in EXPECTED_TYPES.items():
        if not isinstance(alert[field], expected_type):
            return False, f"Field '{field}' has wrong type {type(alert[field]).__name__}; expected {expected_type}"

    return True, ""


def build_alert_payload() -> List[Dict[str, Any]]:
    messages = load_json(GATEWAY_SAMPLE_PATH)
    ids = IDS()
    alerts: List[Dict[str, Any]] = []

    for message in messages:
        alert = ids.detect(message)
        if alert is not None:
            alerts.append(alert)

    with open(ALERT_PAYLOAD_PATH, "w", encoding="utf-8") as f:
        json.dump(alerts, f, indent=2)

    return alerts


def run_alert_interface_test() -> bool:
    print("Running Gateway -> alert payload interface validation...")
    errors = 0

    alerts = build_alert_payload()
    print(f"Generated {len(alerts)} alerts from {GATEWAY_SAMPLE_PATH} into {ALERT_PAYLOAD_PATH}")

    if not alerts:
        print("No alerts generated from the gateway sample. The payload file is still valid.")

    print("\nValidating generated alerts...")
    for index, alert in enumerate(alerts, start=1):
        valid, message = validate_alert(alert)
        if valid:
            print(f"  Alert #{index}: OK")
        else:
            errors += 1
            print(f"  Alert #{index}: FAIL - {message}")
            print(json.dumps(alert, indent=2))

    if errors == 0:
        print("\nAlert interface validation passed.")
    else:
        print(f"\nAlert interface validation failed with {errors} error(s).")

    return errors == 0


if __name__ == "__main__":
    success = run_alert_interface_test()
    if not success:
        raise SystemExit(1)
