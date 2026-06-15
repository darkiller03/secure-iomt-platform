from fastapi import FastAPI, HTTPException
from typing import Any, Dict

from ids import IDS

app = FastAPI(title="IoMT IDS Service")

# Persistent IDS instance and in-memory alert store for the service lifetime.
ids = IDS()
alerts = []


@app.post("/detect")
def detect(message: Dict[str, Any]):
    """Receive one medical device message and run IDS detection."""
    if not isinstance(message, dict):
        raise HTTPException(status_code=400, detail="Invalid JSON payload")

    alert = ids.detect(message)
    if alert is None:
        return {"status": "NORMAL", "alert": None}

    alerts.append(alert)
    return {"status": "ALERT", "alert": alert}


@app.get("/alerts")
def get_alerts():
    """Return alerts generated since the service started."""
    return alerts


@app.get("/health")
def health():
    return {"status": "IDS running"}
