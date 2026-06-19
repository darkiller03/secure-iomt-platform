import json
import os
import time
from datetime import datetime, UTC
import paho.mqtt.client as mqtt

BROKER_HOST = os.getenv("BROKER_HOST", "localhost")
BROKER_PORT = 1883
TOPIC = "iomt/devices"

def on_connect(client, userdata, flags, rc):
    print(f"Connected with result code: {rc}")

def on_publish(client, userdata, mid):
    print(f"Message published with mid: {mid}")

client = mqtt.Client()
client.on_connect = on_connect
client.on_publish = on_publish

print(f"Connecting to MQTT broker {BROKER_HOST}:{BROKER_PORT}")
client.connect(BROKER_HOST, BROKER_PORT, 60)
client.loop_start()

time.sleep(1)

data = {
    "device_id": "HRM001",
    "patient_id": "P001",
    "device_type": "heart_monitor",
    "value": 250,
    "unit": "bpm",
    "timestamp": datetime.now(UTC).isoformat(),
    "status": "attack"
}

payload = json.dumps(data)
result = client.publish(TOPIC, payload, qos=1)
result.wait_for_publish()

print("DATA INJECTION SENT:", data)

time.sleep(2)
client.loop_stop()
client.disconnect()