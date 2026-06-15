import json
import random
import time
from datetime import datetime

import paho.mqtt.client as mqtt

BROKER = "localhost"
PORT = 1883
TOPIC = "iomt/devices"

client = mqtt.Client()
client.connect(BROKER, PORT)

devices = [
    {
        "device_id": "HRM001",
        "device_type": "heart_monitor",
        "unit": "bpm",
        "min": 60,
        "max": 100
    },
    {
        "device_id": "INS001",
        "device_type": "insulin_pump",
        "unit": "u/h",
        "min": 1,
        "max": 10
    },
    {
        "device_id": "TMP001",
        "device_type": "smart_thermometer",
        "unit": "°C",
        "min": 36,
        "max": 38
    },
    {
        "device_id": "OXY001",
        "device_type": "oximeter",
        "unit": "%",
        "min": 95,
        "max": 100
    }
]

while True:

    device = random.choice(devices)

    message = {
        "device_id": device["device_id"],
        "patient_id": f"P{random.randint(1,5):03}",
        "device_type": device["device_type"],
        "value": round(
            random.uniform(device["min"], device["max"]),
            2
        ),
        "unit": device["unit"],
        "timestamp": datetime.now().isoformat(),
        "status": "normal"
    }

    client.publish(
        TOPIC,
        json.dumps(message)
    )

    print(message)

    time.sleep(3)mport json
import random
import time
from datetime import datetime

import paho.mqtt.client as mqtt

client = mqtt.Client()

client.connect("localhost", 1883)

while True:
    message = {
        "device_id": "HRM001",
        "patient_id": "P001",
        "device_type": "heart_monitor",
        "value": random.randint(60, 100),
        "unit": "bpm",
        "timestamp": datetime.now().isoformat(),
        "status": "normal"
    }

    client.publish(
        "iomt/devices",
        json.dumps(message)
    )

    print(message)

    time.sleep(5)
