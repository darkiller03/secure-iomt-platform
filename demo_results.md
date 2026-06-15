# IDS Demo Results

This document summarizes representative IDS behavior for the prototype.

## 1. Normal Traffic
Input:
```json
{
  "device_id": "HRM001",
  "patient_id": "P001",
  "device_type": "HeartRateMonitor",
  "heart_rate": 72,
  "timestamp": "2026-06-01T10:15:00Z"
}
```
Output: No alert generated (`NORMAL`).

## 2. Data Injection
Input:
```json
{
  "device_id": "HRM001",
  "patient_id": "P003",
  "device_type": "HeartRateMonitor",
  "heart_rate": 250,
  "timestamp": "2026-06-01T10:17:00Z"
}
```
Output:
```json
{
  "alert_id": "ALT-XXXX",
  "timestamp": "<generated>",
  "device_id": "HRM001",
  "alert_type": "Data Injection",
  "severity": "HIGH",
  "anomaly_score": 1.0,
  "description": "Heart rate value outside acceptable range",
  "recommended_action": "Verify sensor integrity"
}
```

## 3. Device Spoofing
Input:
```json
{
  "device_id": "HRM001",
  "patient_id": "Pdos01",
  "device_type": "HeartRateMonitor",
  "heart_rate": 80,
  "timestamp": "2026-06-01T13:00:02.050000Z"
}
```
Output:
```json
{
  "alert_id": "ALT-XXXX",
  "timestamp": "<generated>",
  "device_id": "HRM001",
  "alert_type": "Device Spoofing",
  "severity": "MEDIUM",
  "anomaly_score": 1.0,
  "description": "Suspicious patient identifier detected for known device",
  "recommended_action": "Verify device assignment and sender authenticity"
}
```

## 4. Denial-of-Service (DoS)
Input: the sixth rapid message from the same device in a tight window.
```json
{
  "device_id": "HRM001",
  "patient_id": "P005",
  "device_type": "HeartRateMonitor",
  "heart_rate": 75,
  "timestamp": "2026-06-01T10:18:01Z"
}
```
Output:
```json
{
  "alert_id": "ALT-XXXX",
  "timestamp": "<generated>",
  "device_id": "HRM001",
  "alert_type": "DoS",
  "severity": "HIGH",
  "anomaly_score": 1.0,
  "description": "High message rate from device (6 msgs in 2.0s)",
  "recommended_action": "Rate-limit or isolate the device"
}
```

## 5. Anomaly Detection
Input:
```json
{
  "device_id": "HRM001",
  "patient_id": "P999",
  "device_type": "HeartRateMonitor",
  "heart_rate": 45,
  "timestamp": "2026-06-01T15:00:00Z"
}
```
Output:
```json
{
  "alert_id": "ALT-XXXX",
  "timestamp": "<generated>",
  "device_id": "HRM001",
  "alert_type": "Anomaly",
  "severity": "MEDIUM",
  "anomaly_score": 0.58,
  "description": "Isolation Forest detected anomalous heart rate",
  "recommended_action": "Inspect device readings and patient status"
}
```

## Metrics Summary
The large dataset run now reports:

- Precision: `1.0`
- Recall: `1.0`
- Accuracy: `1.0`
- False positive rate: `0.0`
- False negative rate: `0.0`

These results are based on legacy large-dataset evaluation artifacts and are not included in the current repository.

## Command
Run the main test harness with:

```bash
python test_ids.py multi_device_dataset.json alerts_output.json metrics_output.json
```
