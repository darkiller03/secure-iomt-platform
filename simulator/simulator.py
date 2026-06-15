import json
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
