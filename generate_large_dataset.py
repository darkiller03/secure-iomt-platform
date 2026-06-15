import json
import random
from datetime import datetime, timedelta

random.seed(42)
known_devices = ["HRM001", "THM001", "OXY001"]

messages = []
start = datetime(2026, 6, 1, 10, 0, 0)

# 95 normal non-DoS messages
for i in range(95):
    device = random.choice(known_devices)
    heart_rate = random.randint(60, 100)
    ts = (start + timedelta(seconds=i * 30)).isoformat() + 'Z'
    messages.append({
        "device_id": device,
        "patient_id": f"P{i:03d}",
        "device_type": "HeartRateMonitor",
        "heart_rate": heart_rate,
        "timestamp": ts,
        "expected_label": "normal",
    })

# 20 Data Injection attacks
injection_values = [250, 300, 5, 10, 190, 0, 220, 181, 182, 240, 260, 210, 4, 12, 195, 199, 205, 233, 1700, 400]
for i, hr in enumerate(injection_values):
    ts = (start + timedelta(hours=1, minutes=i)).isoformat() + 'Z'
    messages.append({
        "device_id": random.choice(known_devices),
        "patient_id": f"Pinj{i:02d}",
        "device_type": "HeartRateMonitor",
        "heart_rate": hr,
        "timestamp": ts,
        "expected_label": "attack",
    })

# 20 Device Spoofing attacks
for i in range(20):
    ts = (start + timedelta(hours=2, minutes=i)).isoformat() + 'Z'
    messages.append({
        "device_id": f"FAKE{i:02d}",
        "patient_id": f"Pspoof{i:02d}",
        "device_type": "HeartRateMonitor",
        "heart_rate": random.randint(60, 100),
        "timestamp": ts,
        "expected_label": "attack",
    })

# 20 DoS attack messages
for i in range(5):
    ts = (start + timedelta(hours=3, seconds=i * 0.4)).isoformat() + 'Z'
    messages.append({
        "device_id": "HRM001",
        "patient_id": f"Pdos-warm{i:02d}",
        "device_type": "HeartRateMonitor",
        "heart_rate": random.randint(65, 90),
        "timestamp": ts,
        "expected_label": "normal",
    })
for i in range(20):
    ts = (start + timedelta(hours=3, seconds=2 + i * 0.05)).isoformat() + 'Z'
    messages.append({
        "device_id": "HRM001",
        "patient_id": f"Pdos{i:02d}",
        "device_type": "HeartRateMonitor",
        "heart_rate": random.randint(65, 90),
        "timestamp": ts,
        "expected_label": "attack",
    })

with open('sample_data_large.json', 'w', encoding='utf-8') as f:
    json.dump(messages, f, indent=2)

print('Created sample_data_large.json with', len(messages), 'messages')
