import json
import os
import time
from datetime import datetime, UTC

import paho.mqtt.client as mqtt


def get_broker_host():
    broker_host = os.getenv("BROKER_HOST")
    if broker_host:
        return broker_host

    if os.getenv("WSL_DISTRO_NAME"):
        return "host.docker.internal"

    return "localhost"


BROKER_HOST = get_broker_host()
BROKER_PORT = 1883
TOPIC = "iomt/devices"

client = mqtt.Client()
client.connect(BROKER_HOST, BROKER_PORT, 60)
client.loop_start()

data = {
    "device_id": "UNKNOWN999",
    "patient_id": "P001",
    "device_type": "heart_monitor",
    "value": 80,
    "unit": "bpm",
    "timestamp": datetime.now(UTC).isoformat(),
    "status": "attack"
}

result = client.publish(TOPIC, json.dumps(data))
result.wait_for_publish()
print("DEVICE SPOOFING SENT:", data)

time.sleep(1)
client.loop_stop()
client.disconnect()