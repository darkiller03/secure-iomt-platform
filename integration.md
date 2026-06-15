# IDS Integration Specification

This document describes exactly how the IDS service integrates with the Gateway and the Dashboard/LLM.
It includes input and output schema, API endpoints, Docker Compose example, and severity policy.

## INPUT FROM GATEWAY

The Gateway sends medical telemetry to the IDS using the `POST /detect` endpoint.

### Expected JSON payload

```json
{
  "device_id": "HRM001",
  "patient_id": "P001",
  "device_type": "HeartRateMonitor",
  "heart_rate": 72,
  "timestamp": "2026-06-01T10:15:00Z"
}
```

### Required fields

- `device_id`: string, unique identifier for the device.
- `patient_id`: string, identifier for the patient.
- `device_type`: string, type of medical device.
- `heart_rate`: integer or float, measured heart rate.
- `timestamp`: string, ISO 8601 UTC timestamp.

### Optional fields

- Any extra metadata fields are allowed but ignored by the current IDS logic.
- Examples: `location`, `device_firmware`, `signal_quality`.

### Validation rules

- `device_id` must be present and non-empty.
- `patient_id` must be present and non-empty.
- `device_type` must be present and non-empty.
- `heart_rate` must be a numeric value.
- `timestamp` must be a valid ISO 8601 UTC string.
- If a required field is missing or invalid, the IDS should reject the request with an HTTP 400 error.

## OUTPUT TO DASHBOARD / LLM

When the IDS detects an alert, it returns alert JSON in the following format.

### Alert JSON

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

### Alert fields

- `alert_id`: unique ID for the alert.
- `timestamp`: ISO 8601 UTC timestamp when the alert was generated.
- `device_id`: originating device identifier.
- `alert_type`: category of detection, such as `Data Injection`, `Device Spoofing`, `DoS`, or `Anomaly`.
- `severity`: one of `LOW`, `MEDIUM`, `HIGH`, `CRITICAL`.
- `anomaly_score`: numeric score between 0 and 1 representing the confidence or anomaly severity.
- `description`: short human-readable description of the alert.
- `recommended_action`: short instruction for the operator or system.

## API ENDPOINTS

### POST /detect

- Accepts one medical device message.
- Returns `NORMAL` if no alert is detected.
- Returns `ALERT` with alert JSON when an anomaly is detected.

#### Request example

```bash
curl -X POST http://localhost:8000/detect \
  -H "Content-Type: application/json" \
  -d '{
    "device_id": "HRM001",
    "patient_id": "P001",
    "device_type": "HeartRateMonitor",
    "heart_rate": 250,
    "timestamp": "2026-06-01T10:15:00Z"
  }'
```

#### Successful response when no alert

```json
{
  "status": "NORMAL",
  "alert": null
}
```

#### Successful response when alert detected

```json
{
  "status": "ALERT",
  "alert": {
    "alert_id": "ALT-0001",
    "timestamp": "2026-06-01T10:15:12Z",
    "device_id": "HRM001",
    "alert_type": "Data Injection",
    "severity": "HIGH",
    "anomaly_score": 0.94,
    "description": "Heart rate value exceeds normal range",
    "recommended_action": "Verify sensor integrity"
  }
}
```

### GET /alerts

- Returns all alerts generated since the IDS service started.
- Useful for Dashboard or LLM polling.

#### Response example

```json
{
  "alerts": [
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
  ]
}
```

### GET /health

- Returns the health status of the IDS service.

#### Response example

```json
{
  "status": "IDS running"
}
```

## Docker Compose integration snippet

Example service definition for `docker-compose.yml`.

```yaml
ids:
  build: ./ids
  container_name: ids
  ports:
    - "8000:8000"
```

### How the Gateway should call the IDS

- When running in a Docker Compose network, the Gateway should call `http://ids:8000/detect`.
- The Gateway should send each medical device message as JSON using `POST /detect`.
- The Gateway can optionally inspect the response and forward alerts to the Dashboard.

## Alert severity policy

The IDS assigns one of four severities to alerts.

- `LOW`: Minor anomaly with little immediate risk.
  - Example: a slightly unusual heart rate still in valid range.
- `MEDIUM`: Suspicious behavior that should be investigated.
  - Example: an isolated anomalous reading flagged by the Isolation Forest.
- `HIGH`: Data Injection or other strong evidence of malicious input.
  - Example: heart rate far outside the normal range.
- `CRITICAL`: Denial-of-Service or high-confidence attack requiring immediate action.
  - Example: too many messages too quickly from the same device.

## Information flow

1. **Gateway** forwards medical telemetry to the IDS via `POST /detect`.
2. **IDS** evaluates each message and generates alerts when needed.
3. **Dashboard** retrieves alert data from `GET /alerts`.
4. **LLM** can query the Dashboard or use the IDS alerts to enrich its responses.

After reading this document, another student should be able to connect the Gateway to `POST /detect` and let the Dashboard consume alerts from `GET /alerts` without additional clarification.
