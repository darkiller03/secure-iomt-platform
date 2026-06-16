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
