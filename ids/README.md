# IDS File-Based Integration Module

This module provides file-based intrusion detection for the IoMT platform.

## Input
- Path: `../data/validated_data.json`
- Format: JSON array of device telemetry messages

## Output
- Path: `../data/alerts.json`
- Format: JSON array of alerts in dashboard format

## Execution
From the repository root:

```bash
python ids/detection_file.py
```

## Alert Format
Each alert object contains:

```json
{
  "type": "Data Injection",
  "device": "HRM001",
  "severity": "HIGH",
  "timestamp": "2026-06-15T16:50:00Z",
  "description": "Heart rate value exceeds normal range",
  "recommended_action": "Verify sensor integrity"
}
```

## Supported Devices
- heart_monitor (40-180 bpm)
- thermometer (35-42 °C)
- oximeter (90-100 %)
- insulin_pump (0-50 IU)

## Detection Methods
- Data Injection: values outside acceptable ranges
- Device Spoofing: unknown device IDs or suspicious patterns
- DoS: high message rate detection
- Anomaly: Isolation Forest-based statistical anomalies
## New Detection Features

- Silent Device: tracks the last timestamp seen for each known device (HRM001, THM001, OXY001, INP001). After processing the dataset the IDS compares each device's last timestamp to the latest timestamp in the dataset; if a device has not sent data for more than 30 seconds it raises a `Silent Device` alert.

- Patient ID Change: remembers the first `patient_id` observed for each `device_id`. If the same device later reports a different `patient_id`, the IDS raises a `Patient ID Change` alert.

- Replay Attack: builds a message fingerprint from `device_id + patient_id + device_type + value + unit + timestamp`. If the identical fingerprint is seen again, a `Replay Attack` alert is generated.

- Programming Change Suspected (insulin pump prototype): for `insulin_pump` devices the IDS keeps a short sliding window of recent insulin values. If the current value is more than twice the previous average and greater than 20 IU, the IDS raises a `Programming Change Suspected` alert.

## Examples

1) Silent Device alert (dashboard format):

```json
{
  "type": "Silent Device",
  "device": "HRM001",
  "severity": "Medium",
  "timestamp": "...",
  "description": "Device HRM001 stopped sending data for more than 30 seconds",
  "recommended_action": "Check device connectivity and patient monitoring status"
}
```

2) Patient ID Change example:

```json
{
  "type": "Patient ID Change",
  "device": "HRM001",
  "severity": "High",
  "timestamp": "...",
  "description": "Device HRM001 changed patient_id from P001 to P999",
  "recommended_action": "Verify device assignment and patient identity"
}
```

3) Replay Attack example:

```json
{
  "type": "Replay Attack",
  "device": "OXY001",
  "severity": "High",
  "timestamp": "...",
  "description": "Repeated identical message detected for device OXY001",
  "recommended_action": "Verify message freshness and communication integrity"
}
```

4) Programming Change Suspected (insulin_pump prototype):

```json
{
  "type": "Programming Change Suspected",
  "device": "INP001",
  "severity": "High",
  "timestamp": "...",
  "description": "Sudden increase in insulin delivery without contextual justification",
  "recommended_action": "Verify insulin pump programming and patient condition"
}
```

## Teacher-Requested Extensions Implemented

### 1. Silent Device Detection
- Tracks last timestamp received from each known device (HRM001, THM001, OXY001, INP001)
- Generates "Silent Device" alert if device has not sent data for more than 30 seconds
- Implemented in: `ids.py` method `finalize()`

### 2. Patient ID Change Detection
- Records the first patient_id seen for each device
- Detects and alerts if the same device later reports a different patient_id
- Implemented in: `ids.py` method `detect()`

### 3. Replay Attack Detection
- Builds message fingerprints: `device_id|patient_id|device_type|value|unit|timestamp`
- Detects repeated identical messages
- Implemented in: `ids.py` method `detect()`

### 4. Insulin Pump Programming Change Detection (Prototype)
- Maintains sliding window (max 5 values) of recent insulin measurements per device
- Alerts if current value > previous_average × 2 AND current value > 20 IU
- Implemented in: `ids.py` method `detect()`

### 5. Second Anomaly Detection Algorithm: Z-Score
- Implements lightweight statistical anomaly detection based on mean and standard deviation
- No additional dependencies; uses only built-in arithmetic
- Defined reference parameters for each device type:
  - Heart Monitor: mean = 80 bpm, std = 8 bpm
  - Thermometer: mean = 38.5 °C, std = 0.7 °C
  - Oximeter: mean = 96 %, std = 2 %
  - Insulin Pump: mean = 25 IU, std = 5 IU
- Z-score formula: `z = |value - mean| / std`; anomaly if z > 3
- Computed for all measurements; scores stored for LLM analysis
- Does NOT override rule-based detection; serves as supporting evidence
- Implemented in: `ids.py` method `_compute_z_score()`

### 6. Supporting Files for LLM Analysis

**ALGORITHM_COMPARISON_REPORT.md**
- Compares Rule-Based Detection, Isolation Forest, and Z-Score methods
- Explains principles, advantages, limitations, and use cases for each
- Recommendations for hybrid approach in production

**data/llm_error_cases.json**
- 9 representative test cases (3 false positives, 3 false negatives, 3 borderline)
- Shows algorithm outputs and expected labels
- Provides explanations for LLM training and confidence assessment

**data/llm_correlation_input.json**
- Structured dataset with 12 representative MQTT messages
- Includes algorithm outputs (z-score, isolation forest, rule-based decisions)
- Generated alerts with correlation analysis notes
- Designed for Student 4 / LLM multi-event correlation and root-cause analysis

## Algorithm Selection Notes

- **Rule-Based Detection** remains the primary gate (medical range checks)
- **Z-Score Detection** provides fast, explainable anomaly scoring
- **Isolation Forest** available for advanced pattern detection (optional enhancement)
- **Final decision** remains rule-based (safe, no false negatives from medical violations)
- **Anomaly scores** used as supporting evidence in alerts and for LLM analysis

## Integration with Student 4 (LLM System)

The IDS generates alerts and also produces two data files for upstream correlation and analysis:

1. **data/llm_error_cases.json** — Example scenarios for LLM to understand false positives/negatives and improve confidence calibration
2. **data/llm_correlation_input.json** — Structured multi-event dataset with algorithm outputs for LLM-driven root-cause analysis and attack classification

This separation allows the IDS to remain focused on detection while enabling the LLM system to handle complex correlation, contextualization, and clinical decision support.
