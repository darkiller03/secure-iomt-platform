import json
from datetime import datetime
from pathlib import Path

import paho.mqtt.client as mqtt

BROKER_HOST = "localhost"
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

    return True, "Valid message"


def on_connect(client, userdata, flags, rc):
    if rc == 0:
        print("Gateway connected to MQTT broker")
        client.subscribe(TOPIC)
        print(f"Subscribed to topic: {TOPIC}")
        write_log("INFO", "Gateway connected to MQTT broker")
    else:
        print("Connection failed")
        write_log("ERROR", "Gateway connection failed")


def on_message(client, userdata, msg):
    try:
        payload = msg.payload.decode()
        data = json.loads(payload)

        is_valid, reason = validate_message(data)

        if is_valid:
            device_id = data["device_id"]

            print(f"VALID MESSAGE from {device_id}")

            write_log(
                "INFO",
                f"Valid message received from {device_id}"
            )

            save_validated_data(data)

        else:
            print("INVALID MESSAGE")

            write_log(
                "WARNING",
                f"Invalid message received: {reason}"
            )

    except json.JSONDecodeError:
        print("INVALID MESSAGE")
        write_log("ERROR", "Invalid JSON received")

    except Exception as error:
        print("GATEWAY ERROR")
        write_log("ERROR", f"Gateway error: {error}")


client = mqtt.Client()

client.on_connect = on_connect
client.on_message = on_message

client.connect(BROKER_HOST, BROKER_PORT)

print("Gateway started")

client.loop_forever()

