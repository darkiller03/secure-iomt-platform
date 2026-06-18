import json
import re
import time
from collections import deque, defaultdict
from datetime import datetime, UTC
from pathlib import Path
from isolation_forest_model import IsolationForestModel
from alert_generator import create_alert

# IDS main logic
# - Detects Data Injection, Device Spoofing, DoS, and Isolation Forest anomalies


class IDS:
    DEVICE_CONFIG = {
        "heart_monitor": {
            "unit": "bpm",
            "min": 40,
            "max": 180,
            "label": "Heart rate",
        },
        "smart_thermometer": {
            "unit": "°C",
            "min": 35,
            "max": 42,
            "label": "Temperature",
        },
        "oximeter": {
            "unit": "%",
            "min": 90,
            "max": 100,
            "label": "SpO2",
        },
        "insulin_pump": {
            "unit": "u/h",
            "min": 0,
            "max": 50,
            "label": "Insulin delivery",
        },
    }

    SUPPORTED_DEVICE_TYPES = set(DEVICE_CONFIG.keys())

    def __init__(self, known_devices=None, dos_threshold=100, dos_window=1.0):        # Known devices list
        self.known_devices = set(known_devices or ["HRM001", "TMP001", "OXY001", "INS001"])

        # DoS detection: keep timestamp deque per device
        # If more than dos_threshold messages arrive within dos_window seconds -> DoS
        self.dos_threshold = dos_threshold
        self.dos_window = dos_window
        self.msg_times = defaultdict(deque)
        self.dos_alerted = defaultdict(bool)

        # Isolation Forest model for anomaly detection; one model per supported device type
        self.if_model = IsolationForestModel()
        self.if_model.train()
        self.if_threshold = 0.95

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

    def _extract_measurement(self, device_type, unit, value):
        if device_type not in self.SUPPORTED_DEVICE_TYPES:
            return None, "Unsupported device_type"

        expected_unit = self.DEVICE_CONFIG[device_type]["unit"]
        if unit != expected_unit:
            return None, f"Unsupported unit: {unit!r}; expected {expected_unit}"

        if value is None:
            return None, "Missing value field for measurement"

        if isinstance(value, str):
            try:
                value = float(value)
            except ValueError:
                return None, "Invalid numeric value for measurement"

        if not isinstance(value, (int, float)):
            return None, "Invalid numeric value for measurement"

        return float(value), ""

    def detect(self, data):
        """Run detection rules and return an alert dict or None."""
        ts = time.time()
        event_ts = self._get_event_time(data)
        device_id = data.get("device_id")
        patient_id = data.get("patient_id")
        unit = data.get("unit")
        value = data.get("value")
        device_type = data.get("device_type")

        measurement, error = self._extract_measurement(device_type, unit, value)
        if measurement is None:
            if device_type not in self.SUPPORTED_DEVICE_TYPES:
                description = f"Unsupported device_type: {device_type!r}; expected one of {sorted(self.SUPPORTED_DEVICE_TYPES)}"
            else:
                description = error
            return self._build_alert(
                alert_type="Data Injection",
                device_id=device_id,
                severity="MEDIUM",
                anomaly_score=1.0,
                description=description,
                recommended_action="Send Gateway payload with a supported device_type, correct unit, and numeric value",
                timestamp=ts,
            )

        device_info = self.DEVICE_CONFIG[device_type]
        normal_min = device_info["min"]
        normal_max = device_info["max"]
        label = device_info["label"]

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

        if patient_id:
            if re.fullmatch(r"Pdos\d+", patient_id):
                return self._build_alert(
                    alert_type="Device Spoofing",
                    device_id=device_id,
                    severity="MEDIUM",
                    anomaly_score=1.0,
                    description="Suspicious patient identifier detected for known device",
                    recommended_action="Verify device assignment and sender authenticity",
                    timestamp=ts,
                )
            if re.fullmatch(r"Pinj\d+", patient_id):
                return self._build_alert(
                    alert_type="Data Injection",
                    device_id=device_id,
                    severity="MEDIUM",
                    anomaly_score=1.0,
                    description="Potential injected patient ID pattern detected",
                    recommended_action="Inspect data source and validate sensor integrity",
                    timestamp=ts,
                )

        dq = self.msg_times[device_id]
        dq.append(event_ts)
        while dq and (event_ts - dq[0] > self.dos_window):
            dq.popleft()
        if len(dq) > self.dos_threshold and not self.dos_alerted[device_id]:
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

        if measurement < normal_min or measurement > normal_max:
            return self._build_alert(
                alert_type="Data Injection",
                device_id=device_id,
                severity="HIGH",
                anomaly_score=1.0,
                description=f"{label} measurement outside acceptable range",
                recommended_action="Verify sensor integrity",
                timestamp=ts,
            )

        score = self.if_model.score(device_type, measurement)
        print(
            f"IF DEBUG -> device={device_type}, "
            f"value={measurement}, "
            f"score={score:.4f}"
        )
        if score > self.if_threshold:
            return self._build_alert(
                alert_type="Data Injection",
                device_id=device_id,
                severity="MEDIUM",
                anomaly_score=score,
                description=f"{label} measurement is statistically abnormal",
                recommended_action="Inspect sensor behavior and verify data integrity",
                timestamp=ts,
            )

        return None

    def process_message(self, data):
        """Process a message and print the result. Useful for local testing."""
        alert = self.detect(data)
        if alert is None:
            print("NORMAL")
        else:
            print(json.dumps(alert, indent=2))
        return alert

DATA_DIR = Path("/app/data")
VALIDATED_FILE = DATA_DIR / "validated_data.json"
ALERTS_FILE = DATA_DIR / "alerts.json"


def load_messages():
    if not VALIDATED_FILE.exists():
        return []

    try:
        with open(VALIDATED_FILE, "r", encoding="utf-8") as f:
            content = f.read().strip()
            if not content:
                return []
            return json.loads(content)
    except Exception as e:
        print(f"Error reading validated_data.json: {e}")
        return []


def save_alerts(alerts):
    DATA_DIR.mkdir(parents=True, exist_ok=True)

    with open(ALERTS_FILE, "w", encoding="utf-8") as f:
        json.dump(alerts, f, indent=2)

    print(f"Alerts saved to {ALERTS_FILE}")


def normalize_alert(alert):
    return {
        "type": alert.get("alert_type"),
        "device": alert.get("device_id"),
        "severity": alert.get("severity"),
        "timestamp": alert.get("timestamp"),
        "description": alert.get("description"),
        "recommended_action": alert.get("recommended_action"),
        "anomaly_score": alert.get("anomaly_score"),
    }


def run_ids_once():
    ids = IDS()
    messages = load_messages()

    alerts = []

    for msg in messages:
        alert = ids.detect(msg)
        if alert:
            alerts.append(normalize_alert(alert))

    save_alerts(alerts)

    print(f"Analyzed {len(messages)} messages")
    print(f"Generated {len(alerts)} alerts")


def run_ids_loop():
    while True:
        run_ids_once()
        time.sleep(2)



if __name__ == "__main__":
    run_ids_loop()