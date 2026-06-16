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

attacks = [
    {
        "device_id": "HRM001",
        "device_type": "heart_monitor",
        "unit": "bpm",
        "value": lambda: random.randint(220, 300)
    },
    {
        "device_id": "TMP001",
        "device_type": "smart_thermometer",
        "unit": "°C",
        "value": lambda: random.randint(45, 55)
    },
    {
        "device_id": "OXY001",
        "device_type": "oximeter",
        "unit": "%",
        "value": lambda: random.randint(10, 40)
    },
    {
        "device_id": "INS001",
        "device_type": "insulin_pump",
        "unit": "u/h",
        "value": lambda: random.randint(50, 100)
    }
]

while True:

    attack = random.choice(attacks)

    message = {
        "device_id": attack["device_id"],
        "patient_id": f"P{random.randint(1,5):03}",
        "device_type": attack["device_type"],
        "value": attack["value"](),
        "unit": attack["unit"],
        "timestamp": datetime.now().isoformat(),
        "status": "compromised"
    }

    client.publish(
        TOPIC,
        json.dumps(message)
    )

    print("ATTACK DATA SENT:", message)

    time.sleep(3)
