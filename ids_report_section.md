# IDS Report Section

## 1. Role of the IDS
The IDS receives normalized medical data from the Gateway and detects abnormal or malicious behavior. It acts as a security layer between the Gateway and the Dashboard/LLM, checking incoming device messages and generating alerts when suspicious activity occurs.

## 2. Detection methods

### Rule-based detection
The IDS uses fixed rules to detect invalid values. For example, heart rate values below 40 or above 180 are treated as potential data injection attacks.

### Isolation Forest anomaly detection
The IDS trains an Isolation Forest model on normal heart rate values and uses it to flag patterns that look statistically unusual. This helps find anomalies that are not covered by simple rules.

### Device Spoofing detection
The IDS checks whether the device_id is in the known device list (`HRM001`, `THM001`, `OXY001`). If an unknown device sends data, the IDS raises a Device Spoofing alert.

### DoS detection
The IDS monitors how often messages arrive from the same device. If too many messages arrive in a short time window, it triggers a DoS alert.

## 3. Input format
The IDS expects medical telemetry as JSON with these fields:

```json
{
  "device_id": "HRM001",
  "patient_id": "P001",
  "device_type": "HeartRateMonitor",
  "heart_rate": 72,
  "timestamp": "2026-06-01T10:15:00Z"
}
```

## 4. Output format
When an alert is generated, the IDS returns alert JSON in this format:

```json
{
  "alert_id": "ALT-0001",
  "timestamp": "2026-06-01T10:15:12Z",
  "device_id": "HRM001",
  "alert_type": "Data Injection",
  "severity": "HIGH",
  "anomaly_score": 0.94,
  "description": "Heart rate value exceeds normal range",
  "recommended_action": "Verify sensor integrity"
}
```

## 5. Evaluation metrics

### Precision
Precision measures how many alerts were actually correct. It is the number of true positives divided by all positive detections.

### Recall
Recall measures how many real attacks were detected. It is the number of true positives divided by all real attacks.

### False positive rate
False positive rate measures how often normal messages were incorrectly flagged as attacks. It is false positives divided by all negative cases.

### False negative rate
False negative rate measures how often real attacks were missed. It is false negatives divided by all real attacks.

### Accuracy
Accuracy measures overall prediction quality. It is the number of correct classifications (true positives + true negatives) divided by all messages.

## 6. Demo scenario

- Normal heart rate = 72 → `NORMAL`
- Heart rate = 250 → `Data Injection` alert
- Unknown `device_id` → `Device Spoofing` alert
- High message frequency from one device → `DoS` alert

## 7. Presentation slides content

### Slide 1: IDS role in the architecture
The IDS receives normalized medical device data from the Gateway, checks each message for suspicious or malicious behavior, and passes alerts to the Dashboard/LLM.

### Slide 2: Detection methods
The IDS uses rule-based checks for invalid values, Isolation Forest anomaly detection for unusual patterns, spoofing detection for unknown devices, and rate-based DoS detection.

### Slide 3: Example of generated alert
Show a sample alert with `alert_id`, `device_id`, `alert_type`, `severity`, `anomaly_score`, `description`, and `recommended_action`.

### Slide 4: Results and metrics
Explain that the IDS was tested locally, outputs alerts for attacks, and reports precision, recall, false positive rate, false negative rate, and overall accuracy.
