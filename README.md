# IDS File-Based Integration Module

This repository contains the production-ready IDS integration layer for the team.
The IDS reads validated gateway telemetry from `data/validated_data.json`, runs the existing detection engine, and writes dashboard-ready alerts to `data/alerts.json`.

## Input file
- `data/validated_data.json`
- Must be a JSON array of device messages.

## Output file
- `data/alerts.json`
- Will contain an array of alert objects in dashboard format.

## Execution
From the repository root, run:

```bash
python ids/detection_file.py
```

## Expected alert format
Each alert is saved as an object with these keys:

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

## Included files
- `ids/detection_file.py` — file-based integration runner
- `ids/ids.py` — IDS detection logic
- `ids/alert_generator.py` — alert formatting helper
- `ids/isolation_forest_model.py` — anomaly scoring support
- `ids/api.py` — FastAPI service implementation
- `data/validated_data.json` — gateway input sample
- `data/alerts.json` — generated output file (created by execution)
- `requirements.txt` — Python dependencies
