import time
import json
from uuid import uuid4

# Alert generator: create alert JSON objects matching required schema


def create_alert(alert_id, timestamp, device_id, alert_type, severity, anomaly_score, description, recommended_action):
    """
    Returns a dict matching the required alert JSON format exactly.

    Fields:
      - alert_id: string like "ALT-0001"
      - timestamp: ISO8601 UTC string
      - device_id: originating device
      - alert_type: e.g. "Data Injection"
      - severity: e.g. "HIGH"
      - anomaly_score: float between 0 and 1
      - description: short text
      - recommended_action: short text
    """
    alert = {
        "alert_id": alert_id,
        "timestamp": timestamp,
        "device_id": device_id,
        "alert_type": alert_type,
        "severity": severity,
        "anomaly_score": float(anomaly_score),
        "description": description,
        "recommended_action": recommended_action,
    }
    return alert


if __name__ == "__main__":
    # Quick sanity demo
    a = create_alert(
        alert_id="ALT-0001",
        timestamp=time.strftime("%Y-%m-%dT%H:%M:%SZ", time.gmtime()),
        device_id="HRM001",
        alert_type="Data Injection",
        severity="HIGH",
        anomaly_score=0.94,
        description="Heart rate value exceeds normal range",
        recommended_action="Verify sensor integrity",
    )
    print(json.dumps(a, indent=2))
