# SecureIoMT Data Contract

This document defines the JSON formats used between all modules.

---

## devices.json

Each device record must follow this structure:

```json
{
  "device_id": "HRM001",
  "patient_id": "P001",
  "device_type": "heart_monitor",
  "value": 72,
  "unit": "bpm",
  "timestamp": "2026-06-15T13:00:00",
  "status": "normal"
}
```

Field descriptions:

| Field | Description |
|---------|---------|
| device_id | Unique device identifier |
| patient_id | Patient identifier |
| device_type | Device type |
| value | Measured value |
| unit | Measurement unit |
| timestamp | ISO timestamp |
| status | normal / suspicious / compromised |

---

## alerts.json

```json
{
  "type": "Data Injection",
  "device": "HRM001",
  "severity": "High",
  "timestamp": "2026-06-15T13:05:00",
  "description": "Abnormal heart rate detected"
}
```

---

## logs.json

```json
{
  "timestamp": "2026-06-15T13:00:00",
  "source": "Gateway",
  "level": "INFO",
  "message": "Message received from HRM001"
}
```

---

## Data Flow
```text
Simulator (Rayane)
    ↓
Gateway (Youssef)
    ↓
IDS (Ilyas)
    ↓
Dashboard + LLM (Karim)
```