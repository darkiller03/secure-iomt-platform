import os
import json
import time
from threading import Event
from datetime import datetime
from pathlib import Path

import paho.mqtt.client as mqtt

BROKER_HOST = os.getenv("BROKER_HOST", "localhost")
BROKER_PORT = 1883
TOPIC = "iomt/devices"

DATA_DIR = Path("/app/data")
LOG_FILE = DATA_DIR / "logs.json"
VALIDATED_FILE = DATA_DIR / "validated_data.json"

REQUIRED_FIELDS = [
    "device_id",
    "patient_id",
    "device_type",
    "value",
    "unit",
    "timestamp"
]

connected_event = Event()


def write_log(level, message):
    LOG_FILE.parent.mkdir(parents=True, exist_ok=True)

    log_entry = {
        "timestamp": datetime.now().isoformat(timespec="seconds"),
        "source": "Gateway",
        "level": level,
        "message": message
    }

    if LOG_FILE.exists():
        try:
            with open(LOG_FILE, "r", encoding="utf-8") as file:
                logs = json.load(file)
        except json.JSONDecodeError:
            logs = []
    else:
        logs = []

    logs.append(log_entry)

    with open(LOG_FILE, "w", encoding="utf-8") as file:
        json.dump(logs, file, indent=2)


def save_validated_data(data):
    VALIDATED_FILE.parent.mkdir(parents=True, exist_ok=True)

    if VALIDATED_FILE.exists():
        try:
            with open(VALIDATED_FILE, "r", encoding="utf-8") as file:
                validated = json.load(file)
        except json.JSONDecodeError:
            validated = []
    else:
        validated = []

    validated.append(data)

    temp_file = VALIDATED_FILE.with_suffix(".json.tmp")
    with open(temp_file, "w", encoding="utf-8") as file:
        json.dump(validated, file, indent=2)

    temp_file.replace(VALIDATED_FILE)


def validate_message(data):
    for field in REQUIRED_FIELDS:
        if field not in data:
            return False, f"Missing field: {field}"

    value = data["value"]

    if not isinstance(value, (int, float)):
        return False, "Value must be numeric"

    return True, "Valid message"


def on_connect(client, userdata, flags, rc):
    if rc == 0:
        print("Gateway connected to MQTT broker", flush=True)
        client.subscribe(TOPIC)
        print(f"Subscribed to topic: {TOPIC}", flush=True)
        connected_event.set()

        write_log(
            "INFO",
            "Gateway connected to MQTT broker"
        )

    else:
        print("Connection failed", flush=True)

        write_log(
            "ERROR",
            "Gateway connection failed"
        )


def on_disconnect(client, userdata, rc):
    print(f"Gateway disconnected from MQTT broker: {rc}", flush=True)

    write_log(
        "WARNING",
        f"Gateway disconnected from MQTT broker: {rc}"
    )


def on_message(client, userdata, msg):
    try:
        payload = msg.payload.decode()
        print(f"Received message: {payload}", flush=True)
        data = json.loads(payload)

        is_valid, reason = validate_message(data)

        if is_valid:
            write_log(
                "INFO",
                f"Valid message received: {payload}"
            )

            save_validated_data(data)
            print("Saved validated message to /app/data/validated_data.json", flush=True)

        else:
            print(f"INVALID MESSAGE: {reason}", flush=True)

            write_log(
                "WARNING",
                f"Invalid message received: {reason}"
            )

    except json.JSONDecodeError:
        print("INVALID JSON", flush=True)

        write_log(
            "ERROR",
            "Invalid JSON received"
        )

    except Exception as error:
        print("GATEWAY ERROR", flush=True)

        write_log(
            "ERROR",
            f"Gateway error: {error}"
        )


client = mqtt.Client()

client.on_connect = on_connect
client.on_message = on_message
client.on_disconnect = on_disconnect


def connect_with_retry():
    while True:
        try:
            client.connect(BROKER_HOST, BROKER_PORT)
            return
        except OSError as error:
            print(
                f"Gateway failed to connect to MQTT broker at {BROKER_HOST}:{BROKER_PORT}: {error}",
                flush=True,
            )
            write_log(
                "ERROR",
                f"Gateway failed to connect to MQTT broker at {BROKER_HOST}:{BROKER_PORT}: {error}",
            )
            time.sleep(2)


connect_with_retry()

print("Gateway started", flush=True)

client.loop_start()

if not connected_event.wait(timeout=10):
    print("Gateway failed to connect to MQTT broker")

    write_log(
        "ERROR",
        "Gateway failed to connect to MQTT broker"
    )

try:
    while True:
        time.sleep(1)
except KeyboardInterrupt:
    pass
