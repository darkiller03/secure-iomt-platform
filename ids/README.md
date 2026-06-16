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
