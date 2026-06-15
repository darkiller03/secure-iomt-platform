import time
from collections import deque, defaultdict
from datetime import datetime, timezone
import json
from isolation_forest_model import IsolationForestModel
from alert_generator import create_alert

# IDS main logic
# - Detects Data Injection, Device Spoofing, DoS, and Isolation Forest anomalies


class IDS:
    def __init__(self, known_devices=None, dos_threshold=5, dos_window=2.0):
        # Known devices list
        self.known_devices = set(known_devices or ["HRM001", "THM001", "OXY001"])

        # DoS detection: keep timestamp deque per device
        # If more than dos_threshold messages arrive within dos_window seconds -> DoS
        self.dos_threshold = dos_threshold
        self.dos_window = dos_window
        self.msg_times = defaultdict(deque)
        self.dos_alerted = defaultdict(bool)

        # Isolation Forest model for anomaly detection on heart_rate
        self.if_model = IsolationForestModel()
        self.if_model.train()
        self.if_threshold = 0.98

        # Counter for alerts to make readable alert IDs
        self.alert_counter = 0

    def _next_alert_id(self):
        self.alert_counter += 1
        return f"ALT-{self.alert_counter:04d}"

    def _get_event_time(self, data):
        timestamp = data.get("timestamp")
        if isinstance(timestamp, str):
            try:
                return datetime.fromisoformat(timestamp.replace("Z", "+00:00")).timestamp()
            except ValueError:
                pass
        return time.time()

    def detect(self, data):
        """Run detection rules and return an alert dict or None."""
        ts = time.time()
        event_ts = self._get_event_time(data)
        device_id = data.get("device_id")
        heart_rate = data.get("heart_rate")

        # 1) Device Spoofing detection
        if device_id not in self.known_devices:
            return self._build_alert(
                alert_type="Device Spoofing",
                device_id=device_id,
                severity="MEDIUM",
                anomaly_score=1.0,
                description="Unknown device identifier detected",
                recommended_action="Verify device identity and network access",
                timestamp=ts,
            )

        # 2) DoS detection: record timestamp and check frequency
        dq = self.msg_times[device_id]
        dq.append(event_ts)
        while dq and (event_ts - dq[0] > self.dos_window):
            dq.popleft()
        if len(dq) > self.dos_threshold:
            if not self.dos_alerted[device_id]:
                self.dos_alerted[device_id] = True
                return self._build_alert(
                    alert_type="DoS",
                    device_id=device_id,
                    severity="HIGH",
                    anomaly_score=1.0,
                    description=f"High message rate from device ({len(dq)} msgs in {self.dos_window}s)",
                    recommended_action="Rate-limit or isolate the device",
                    timestamp=ts,
                )
        else:
            self.dos_alerted[device_id] = False

        # 3) Data Injection detection via simple rules
        if heart_rate is None:
            return self._build_alert(
                alert_type="Data Injection",
                device_id=device_id,
                severity="MEDIUM",
                anomaly_score=1.0,
                description="Missing heart rate value",
                recommended_action="Check device sensor and data integrity",
                timestamp=ts,
            )

        if heart_rate < 40 or heart_rate > 180:
            return self._build_alert(
                alert_type="Data Injection",
                device_id=device_id,
                severity="HIGH",
                anomaly_score=1.0,
                description="Heart rate value outside acceptable range",
                recommended_action="Verify sensor integrity",
                timestamp=ts,
            )

        # 4) Isolation Forest anomaly detection
        score = self.if_model.score(heart_rate)
        if score > self.if_threshold:
            return self._build_alert(
                alert_type="Anomaly",
                device_id=device_id,
                severity="MEDIUM",
                anomaly_score=round(score, 2),
                description="Isolation Forest detected anomalous heart rate",
                recommended_action="Inspect device readings and patient status",
                timestamp=ts,
            )

        return None

    def _build_alert(self, alert_type, device_id, severity, anomaly_score, description, recommended_action, timestamp):
        return create_alert(
            alert_id=self._next_alert_id(),
            timestamp=time.strftime("%Y-%m-%dT%H:%M:%SZ", time.gmtime(timestamp)),
            device_id=device_id,
            alert_type=alert_type,
            severity=severity,
            anomaly_score=anomaly_score,
            description=description,
            recommended_action=recommended_action,
        )

    def process_message(self, data):
        """Process a message and print the result. Useful for local testing."""
        alert = self.detect(data)
        if alert is None:
            print("NORMAL")
        else:
            print(json.dumps(alert, indent=2))
        return alert


if __name__ == "__main__":
    # Simple demo when running directly
    demo = IDS()
    sample = {
        "device_id": "HRM001",
        "patient_id": "P001",
        "device_type": "HeartRateMonitor",
        "heart_rate": 72,
        "timestamp": "2026-06-01T10:15:00Z",
    }
    demo.process_message(sample)
