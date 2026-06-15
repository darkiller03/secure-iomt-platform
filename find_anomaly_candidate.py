import json
from ids import IDS

for hr in [45, 50, 55, 60, 65, 70, 80, 90, 100, 110, 120, 130, 140, 150, 160, 170, 180]:
    ids = IDS()
    score = ids.if_model.score(hr)
    print(hr, score)
    msg = {
        "device_id": "HRM001",
        "patient_id": "P999",
        "device_type": "HeartRateMonitor",
        "heart_rate": hr,
        "timestamp": "2026-06-01T15:00:00Z",
    }
    alert = ids.detect(msg)
    if alert:
        print('alert', alert['alert_type'], alert['description'])
    else:
        print('normal')
    print()
