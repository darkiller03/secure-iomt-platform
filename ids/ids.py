import json
import re
import time
from collections import deque, defaultdict
from datetime import datetime
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

    Z_SCORE_CONFIG = {
        "heart_monitor": {"mean": 80, "std": 8},
        "thermometer": {"mean": 38.5, "std": 0.7},
        "oximeter": {"mean": 96, "std": 2},
        "insulin_pump": {"mean": 25, "std": 5},
    }

    SUPPORTED_DEVICE_TYPES = set(DEVICE_CONFIG.keys())

    def __init__(self, known_devices=None, dos_threshold=5, dos_window=2.0):
        # Known devices list
        self.known_devices = set(known_devices or ["HRM001", "TMP001", "OXY001", "INS001"])

        # DoS detection: keep timestamp deque per device
        # If more than dos_threshold messages arrive within dos_window seconds -> DoS
        self.dos_threshold = dos_threshold
        self.dos_window = dos_window
        self.msg_times = defaultdict(deque)
        self.dos_alerted = defaultdict(bool)

        # Track last seen timestamp per device for silent device detection
        self.last_seen = {}

        # Track first patient_id per device to detect patient assignment changes
        self.first_patient = {}

        # Replay attack detection: store seen fingerprints
        self.fingerprints = set()

        # Insulin pump sliding window history (deque per device)
        self.insulin_history = defaultdict(lambda: deque(maxlen=5))

        # Isolation Forest model for anomaly detection; one model per supported device type
        self.if_model = IsolationForestModel()
        self.if_model.train()
        self.if_threshold = 0.95

        # Counter for alerts to make readable alert IDs
        self.alert_counter = 0

        # Track last anomaly scores for reporting
        self.last_scores = {}

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

    def _compute_z_score(self, device_type, value):
        """Compute Z-score for a measurement.
        
        z = abs(value - mean) / std
        Returns: z_score (float) or None if device_type not supported.
        """
        if device_type not in self.Z_SCORE_CONFIG:
            return None
        cfg = self.Z_SCORE_CONFIG[device_type]
        mean = cfg["mean"]
        std = cfg["std"]
        if std == 0:
            return 0.0
        z = abs(value - mean) / std
        return z

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
                severity="Medium",
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
                severity="Medium",
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
                    severity="Medium",
                    anomaly_score=1.0,
                    description="Potential injected patient ID pattern detected",
                    recommended_action="Inspect data source and validate sensor integrity",
                    timestamp=ts,
                )

        # Update last seen timestamp for silent device detection
        if device_id:
            self.last_seen[device_id] = event_ts

        # Patient ID Change Detection
        if device_id:
            if device_id not in self.first_patient and patient_id:
                self.first_patient[device_id] = patient_id
            elif patient_id and self.first_patient.get(device_id) and patient_id != self.first_patient[device_id]:
                prev = self.first_patient[device_id]
                return self._build_alert(
                    alert_type="Patient ID Change",
                    device_id=device_id,
                    severity="High",
                    anomaly_score=1.0,
                    description=f"Device {device_id} changed patient_id from {prev} to {patient_id}",
                    recommended_action="Verify device assignment and patient identity",
                    timestamp=ts,
                )

        # Replay Attack Detection
        # Build a fingerprint using the message fields (including original timestamp string when available)
        orig_ts = data.get("timestamp") or str(event_ts)
        fingerprint = f"{device_id}|{patient_id}|{device_type}|{value}|{unit}|{orig_ts}"
        if fingerprint in self.fingerprints:
            return self._build_alert(
                alert_type="Replay Attack",
                device_id=device_id,
                severity="High",
                anomaly_score=1.0,
                description=f"Repeated identical message detected for device {device_id}",
                recommended_action="Verify message freshness and communication integrity",
                timestamp=ts,
            )
        self.fingerprints.add(fingerprint)

        dq = self.msg_times[device_id]
        dq.append(event_ts)
        while dq and (event_ts - dq[0] > self.dos_window):
            dq.popleft()
        if len(dq) > self.dos_threshold:
            self.dos_alerted[device_id] = True
            return self._build_alert(
                alert_type="DoS",
                device_id=device_id,
                severity="High",
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
                severity="High",
                anomaly_score=1.0,
                description=f"{label} measurement outside acceptable range",
                recommended_action="Verify sensor integrity",
                timestamp=ts,
            )

        # Insulin Pump Programming Change Suspected (prototype)
        if device_type == "insulin_pump":
            hist = self.insulin_history[device_id]
            if len(hist) > 0:
                prev_avg = sum(hist) / len(hist)
                if measurement > prev_avg * 2 and measurement > 20:
                    return self._build_alert(
                        alert_type="Programming Change Suspected",
                        device_id=device_id,
                        severity="High",
                        anomaly_score=1.0,
                        description="Sudden increase in insulin delivery without contextual justification",
                        recommended_action="Verify insulin pump programming and patient condition",
                        timestamp=ts,
                    )
            # append current value to history
            hist.append(measurement)

        # Compute anomaly scores (supporting evidence, not decision drivers)
        z_score = self._compute_z_score(device_type, measurement)
        
        # Store scores for reporting/LLM analysis
        if device_id:
            self.last_scores[device_id] = {
                "device_type": device_type,
                "value": measurement,
                "z_score": z_score,
                "timestamp": event_ts,
            }

        # Strict normal-range policy: if the measurement is inside the known safe range,
        # do not use Isolation Forest as the primary decision mechanism.
        # Isolation Forest remains available for monitoring, but it cannot override
        # clear rule-based normal values.
        return None

    def finalize(self, latest_event_ts, silence_threshold=30.0):
        """Generate end-of-file alerts such as Silent Device Detection.

        latest_event_ts: float (epoch seconds)
        Returns list of alert dicts.
        """
        alerts = []
        for device in sorted(self.known_devices):
            last = self.last_seen.get(device)
            if last is None or (latest_event_ts - last) > silence_threshold:
                ts = time.time()
                description = f"Device {device} stopped sending data for more than {int(silence_threshold)} seconds"
                alerts.append(
                    self._build_alert(
                        alert_type="Silent Device",
                        device_id=device,
                        severity="Medium",
                        anomaly_score=1.0,
                        description=description,
                        recommended_action="Check device connectivity and patient monitoring status",
                        timestamp=ts,
                    )
                )
        return alerts

    def process_message(self, data):
        """Process a message and print the result. Useful for local testing."""
        alert = self.detect(data)
        if alert is None:
            print("NORMAL")
        else:
            print(json.dumps(alert, indent=2))
        return alert


if __name__ == "__main__":
    demo = IDS()
    sample = {
        "device_id": "HRM001",
        "patient_id": "P001",
        "device_type": "heart_monitor",
        "value": 72,
        "unit": "bpm",
        "timestamp": "2026-06-01T10:15:00Z",
        "status": "normal",
    }
    demo.process_message(sample)
