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

while True:
    message = {
        "device_id": "HRM001",
        "patient_id": "P001",
        "device_type": "heart_monitor",
        "value": random.randint(220, 300),
        "unit": "bpm",
        "timestamp": datetime.now().isoformat(),
        "status": "compromised"
    }

    client.publish(TOPIC, json.dumps(message))
    print("ATTACK DATA SENT:", message)

    time.sleep(5)
