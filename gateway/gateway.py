import os
import json
from datetime import datetime
from pathlib import Path

import paho.mqtt.client as mqtt

BROKER_HOST = os.getenv("BROKER_HOST", "localhost")
BROKER_PORT = 1883
TOPIC = "iomt/devices"

LOG_FILE = Path("data/logs.json")
VALIDATED_FILE = Path("data/validated_data.json")

REQUIRED_FIELDS = [
    "device_id",
    "patient_id",
    "device_type",
    "value",
    "unit",
    "timestamp"
]

AUTHORIZED_DEVICES = {
    "HRM001": {
        "device_type": "heart_monitor"
    },
    "INS001": {
        "device_type": "insulin_pump"
    },
    "TMP001": {
        "device_type": "smart_thermometer"
    },
    "OXY001": {
        "device_type": "oximeter"
    }
}


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

    with open(VALIDATED_FILE, "w", encoding="utf-8") as file:
        json.dump(validated, file, indent=2)


def validate_message(data):
    for field in REQUIRED_FIELDS:
        if field not in data:
            return False, f"Missing field: {field}"

    device_id = data["device_id"]
    device_type = data["device_type"]
    value = data["value"]

    if device_id not in AUTHORIZED_DEVICES:
        return False, f"Unknown device ID: {device_id}"

    expected_type = AUTHORIZED_DEVICES[device_id]["device_type"]

    if device_type != expected_type:
        return False, (
            f"Invalid device type for {device_id}. "
            f"Expected {expected_type}"
        )

    if not isinstance(value, (int, float)):
        return False, "Value must be numeric"

    return True, "Valid message"


def on_connect(client, userdata, flags, rc):
    if rc == 0:
        print("Gateway connected to MQTT broker")
        client.subscribe(TOPIC)
        print(f"Subscribed to topic: {TOPIC}")

        write_log(
            "INFO",
            "Gateway connected to MQTT broker"
        )

    else:
        print("Connection failed")

        write_log(
            "ERROR",
            "Gateway connection failed"
        )


def on_message(client, userdata, msg):
    try:
        payload = msg.payload.decode()
        data = json.loads(payload)

        is_valid, reason = validate_message(data)

        if is_valid:
            device_id = data["device_id"]
            device_type = data["device_type"]

            print(
                f"VALID MESSAGE from "
                f"{device_id} ({device_type})"
            )

            write_log(
                "INFO",
                f"Valid message received from "
                f"{device_id} ({device_type})"
            )

            save_validated_data(data)

        else:
            print("INVALID MESSAGE")

            write_log(
                "WARNING",
                f"Invalid message received: {reason}"
            )

    except json.JSONDecodeError:
        print("INVALID JSON")

        write_log(
            "ERROR",
            "Invalid JSON received"
        )

    except Exception as error:
        print("GATEWAY ERROR")

        write_log(
            "ERROR",
            f"Gateway error: {error}"
        )


client = mqtt.Client()

client.on_connect = on_connect
client.on_message = on_message

client.connect(
    BROKER_HOST,
    BROKER_PORT
)

print("Gateway started")

client.loop_forever()
