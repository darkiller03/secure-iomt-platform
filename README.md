# IDS Prototype for IoMT Cybersecurity Project

This repository contains a simple Python IDS prototype for an IoMT (Internet of Medical Things) project. The IDS processes JSON-formatted medical device data and emits alert JSON when anomalies or attacks are detected.

**Role of the IDS**
- Receive device telemetry (local JSON files for this prototype).
- Detect suspicious behavior: Data Injection, Device Spoofing, DoS, and statistical anomalies via Isolation Forest.
- Output alerts as JSON for downstream systems (Gateway, Dashboard).

**Input JSON format**
A single message must be a JSON object with these fields:

```
{
  "device_id": "HRM001",
  "patient_id": "P001",
  "device_type": "heart_monitor",
  "value": 72,
  "unit": "bpm",
  "timestamp": "2026-06-01T10:15:00Z",
  "status": "normal"
}
```

**Alert output JSON format**
Each alert produced by the IDS matches this structure exactly:

```
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

**Detection methods implemented**
- Data Injection: heart rate outside the rule-based range (40–180 bpm).
- Device Spoofing: device_id not in the known devices list (default: `HRM001`, `THM001`, `OXY001`).
- DoS: rate-based detection — more than a threshold of messages in a short window from the same device.
- Isolation Forest: trained on synthetic normal heart rates (~60–100 bpm) and used to flag statistical anomalies.

**Files**
- `ids.py`: main IDS logic (process_message and detect).
- `alert_generator.py`: helper to build alert JSON objects.
- `isolation_forest_model.py`: trains and scores Isolation Forest anomalies.
- `api.py`: FastAPI application exposing `/detect`, `/alerts`, and `/health`.
- `multi_device_dataset.json`: mixed sample messages used by tests for the four supported device types.
- `test_ids.py`: test runner; reads `multi_device_dataset.json`, sends messages to IDS, writes `alerts_output.json`.
- `alerts_output.json`: output file where alerts are saved (created/overwritten by tests).
- `requirements.txt`: Python dependencies.

**How to run tests (local, no MQTT)**
1. Create a virtual environment and activate it.

Windows PowerShell:
```powershell
python -m venv venv
venv\Scripts\Activate.ps1
pip install -r requirements.txt
python test_ids.py
```

After running, `alerts_output.json` will contain all generated alerts from the multi-device dataset. Normal messages only print `NORMAL`.

**Next steps**
- Integrate the IDS with the Gateway (MQTT or REST) by replacing the local file input with a networked input function.
- Persist trained Isolation Forest models for faster startup.
- Tune thresholds and model contamination for production.

**Docker**

This project can be run inside Docker as a self-contained service. The container runs `python test_ids.py` by default to exercise the IDS locally using `multi_device_dataset.json`.

Build the image:

```bash
docker build -t iomt-ids .
```

Run the container:

```bash
docker run --rm iomt-ids
```

Expected behavior when running the container:
- Normal messages will print `NORMAL`.
- Alerts will print as formatted JSON and be written to `alerts_output.json` inside the container (not persisted unless you mount a volume).
- Evaluation metrics will be printed and saved to `metrics_output.json` inside the container.

Note: For local persistence of output files, mount a host directory when running the container, for example:

```bash
docker run --rm -v "%cd%:/app" iomt-ids
```

**API mode**

The IDS now exposes a FastAPI endpoint when running the Docker container or the app directly.

Available endpoints:
- `POST /detect`: send one medical device message and receive either `NORMAL` or an alert.
- `GET /alerts`: retrieve all alerts generated since the service started.
- `GET /health`: verify the IDS service is running.

Example POST request:

```bash
curl -X POST http://localhost:8000/detect \
  -H "Content-Type: application/json" \
  -d '{
    "device_id": "HRM001",
    "patient_id": "P001",
    "device_type": "heart_monitor",
    "value": 250,
    "unit": "bpm",
    "timestamp": "2026-06-01T10:15:00Z",
    "status": "alert"
  }'
```

Expected API response:

```json
{
  "status": "ALERT",
  "alert": {
    "alert_id": "ALT-0001",
    "timestamp": "2026-06-01T10:15:00Z",
    "device_id": "HRM001",
    "alert_type": "Data Injection",
    "severity": "HIGH",
    "anomaly_score": 1.0,
    "description": "Heart rate value outside acceptable range",
    "recommended_action": "Verify sensor integrity"
  }
}
```

To start the API server locally without Docker:

```powershell
python -m venv venv
venv\Scripts\Activate.ps1
pip install -r requirements.txt
uvicorn api:app --host 0.0.0.0 --port 8000
```

Then use `curl` or any HTTP client to call `/detect` and `/alerts`.

## Integration Architecture

The IDS is designed to sit between the Gateway and the Dashboard/LLM in the global architecture.

```text
Gateway
  ↓
IDS
  ↓
Dashboard
  ↓
LLM
```

- `Gateway` sends medical telemetry to the IDS via `POST /detect`.
- `IDS` evaluates the message and stores generated alerts in memory.
- `Dashboard` or LLM retrieves current alerts from `GET /alerts`.
- `GET /health` confirms the IDS service is running.

### Docker Compose snippet for IDS only

```yaml
ids:
  build: ./ids
  container_name: ids
  ports:
    - "8000:8000"
```

The Gateway should call the IDS at `http://ids:8000/detect` when running in a compose network, or `http://localhost:8000/detect` for local Docker testing.

### Connecting the Gateway and Dashboard

1. Gateway posts telemetry to `POST /detect`.
2. IDS returns either `NORMAL` or the alert object.
3. Dashboard polls `GET /alerts` or uses its own refresh logic to display active IDS alerts.
4. LLM can query the Dashboard or the IDS alerts endpoint to provide context-aware response.

