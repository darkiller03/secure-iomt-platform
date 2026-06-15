"""
Gateway compatibility test for the IDS.

This test loads multi_device_dataset.json, sends every message to the IDS,
prints each result, and summarizes totals at the end.
"""
import json
from ids import IDS


def load_gateway_messages(path="multi_device_dataset.json"):
    with open(path, "r", encoding="utf-8") as f:
        return json.load(f)


def is_value_in_normal_range(msg):
    value = msg.get("value")
    return isinstance(value, (int, float)) and 40 <= value <= 180


def run_gateway_compatibility_test(sample_path="multi_device_dataset.json"):
    ids = IDS()
    messages = load_gateway_messages(sample_path)

    total_messages = len(messages)
    normal_detected = 0
    alerts_generated = 0
    errors = 0

    print("Running Gateway compatibility test...")

    for index, message in enumerate(messages, start=1):
        result = ids.detect(message)
        expected_status = message.get("status")
        is_expected_normal = expected_status == "normal"
        is_range_normal = is_value_in_normal_range(message)

        if result is None:
            outcome = "NORMAL"
            normal_detected += 1
        else:
            outcome = f"ALERT ({result.get('alert_type')})"
            alerts_generated += 1

        print(f"Message #{index}: {outcome}")

        if is_expected_normal and result is not None:
            errors += 1
            print("  FAILURE: normal message generated an alert")
            print("  Original message:", json.dumps(message, indent=2))
            print("  Reason: expected NORMAL for status='normal'")
            print("  Problem field: status/value/device_type/unit")
            print()
            continue

        if is_expected_normal and is_range_normal and result is not None:
            errors += 1
            print("  FAILURE: normal-range value generated an alert")
            print("  Original message:", json.dumps(message, indent=2))
            print("  Reason: status='normal' message in 40-180 bpm range should not trigger an alert")
            print("  Problem field: value")
            print()
            continue

        if not is_expected_normal and result is None:
            errors += 1
            print("  FAILURE: attack message did not generate an alert")
            print("  Original message:", json.dumps(message, indent=2))
            print("  Reason: expected an alert for this attack scenario")
            print("  Problem field: device_id/value/status/device_type/unit")
            print()
            continue

    print("\nGateway compatibility summary:")
    print(f"  Total messages: {total_messages}")
    print(f"  Normal detected: {normal_detected}")
    print(f"  Alerts generated: {alerts_generated}")
    print(f"  Errors: {errors}")

    return errors == 0


if __name__ == "__main__":
    success = run_gateway_compatibility_test()
    if not success:
        raise SystemExit(1)
