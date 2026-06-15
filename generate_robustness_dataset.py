import json
from pathlib import Path
from random import Random
from datetime import datetime, timedelta

root = Path(__file__).resolve().parent
output_path = root / 'robustness_dataset.json'

DEVICE_CONFIG = {
    'heart_monitor': {
        'device_id': 'HRM001',
        'patient_id': 'P001',
        'unit': 'bpm',
        'normal_min': 40.0,
        'normal_max': 180.0,
        'label': 'Heart rate',
        'borderline': [39, 40, 41, 179, 180, 181],
    },
    'thermometer': {
        'device_id': 'THM001',
        'patient_id': 'P002',
        'unit': '°C',
        'normal_min': 35.0,
        'normal_max': 42.0,
        'label': 'Temperature',
        'borderline': [34.9, 35.0, 35.1, 41.9, 42.0, 42.1],
    },
    'oximeter': {
        'device_id': 'OXY001',
        'patient_id': 'P003',
        'unit': '%',
        'normal_min': 90.0,
        'normal_max': 100.0,
        'label': 'SpO2',
        'borderline': [89, 90, 91, 99, 100, 101],
    },
    'insulin_pump': {
        'device_id': 'INP001',
        'patient_id': 'P004',
        'unit': 'IU',
        'normal_min': 0.0,
        'normal_max': 50.0,
        'label': 'Insulin delivery',
        'borderline': [0, 1, 49, 50, 51],
    },
}

DEVICE_START_OFFSET = {
    'heart_monitor': 0,
    'thermometer': 1,
    'oximeter': 2,
    'insulin_pump': 3,
}

rng = Random(1234)
messages = []
base_time = datetime(2026, 6, 15, 12, 0, 0)

for device_type, info in DEVICE_CONFIG.items():
    device_id = info['device_id']
    patient_id = info['patient_id']
    unit = info['unit']
    normal_min = info['normal_min']
    normal_max = info['normal_max']
    label = info['label']
    borderline_values = info['borderline']
    per_device = []

    def add_message(value, status, expected_label, borderline=False):
        timestamp = base_time + timedelta(
            seconds=DEVICE_START_OFFSET[device_type] + len(per_device) * 3.5 + rng.random()
        )
        per_device.append({
            'device_id': device_id,
            'patient_id': patient_id,
            'device_type': device_type,
            'value': value,
            'unit': unit,
            'timestamp': timestamp.isoformat() + 'Z',
            'status': status,
            'expected_label': expected_label,
            'borderline': borderline,
        })

    for value in borderline_values:
        expected = 'normal' if normal_min <= value <= normal_max else 'attack'
        status = expected
        add_message(value, status, expected, borderline=True)

    near_normals = [normal_min + 0.5, normal_min + 2.0, normal_max - 0.5, normal_max - 2.0]
    for value in near_normals:
        add_message(value, 'normal', 'normal')

    far_attacks = [normal_min - 5.0, normal_max + 5.0, normal_max + 20.0, normal_min - 20.0]
    for value in far_attacks:
        add_message(value, 'attack', 'attack')

    additional_normals = 36 if device_type == 'insulin_pump' else 35
    for _ in range(additional_normals):
        value = rng.uniform(normal_min + 1.0, normal_max - 1.0)
        add_message(round(value, 1), 'normal', 'normal')

    messages.extend(per_device)

# Add explicit spoofing attack messages with safe timestamps outside the 2-second window for each device type.
for device_type, info in DEVICE_CONFIG.items():
    spoof_id = info['device_id'][:-1] + 'X99'
    spoof_time = base_time + timedelta(seconds=360 + DEVICE_START_OFFSET[device_type])
    messages.append({
        'device_id': spoof_id,
        'patient_id': info['patient_id'],
        'device_type': device_type,
        'value': info['normal_min'] + 2,
        'unit': info['unit'],
        'timestamp': spoof_time.isoformat() + 'Z',
        'status': 'attack',
        'expected_label': 'attack',
        'borderline': False,
    })

messages.sort(key=lambda msg: msg['timestamp'])
with open(output_path, 'w', encoding='utf-8') as f:
    json.dump(messages, f, indent=2)

print(f'Generated {len(messages)} messages to {output_path}')
