"""
Simple tests for the IDS prototype. This script runs a set of sample messages
covering normal data and each attack type required by the assignment.

Run: python test_ids.py
"""
import json
import time
from ids import IDS


def run_tests(sample_path="sample_data.json", output_path="alerts_output.json"):
    ids = IDS()
    alerts = []
    predictions = []

    # Load sample messages from JSON
    with open(sample_path, "r", encoding="utf-8") as f:
        messages = json.load(f)

    for msg in messages:
        # Send each message to IDS
        result = ids.process_message(msg)
        if result is None:
            predicted_label = "normal"
        else:
            predicted_label = "attack"
            alerts.append(result)

        expected_label = msg.get("expected_label", "normal")
        if expected_label == "normal" and predicted_label == "attack":
            print("FALSE POSITIVE detected:")
            print(json.dumps(msg, indent=2))
            print("Reason:", result.get("alert_type"), "-", result.get("description"))
            print()

        # record prediction alongside expected label (if present)
        predictions.append({
            "expected_label": expected_label,
            "predicted_label": predicted_label,
        })

    # Save all alerts to output file
    with open(output_path, "w", encoding="utf-8") as f:
        json.dump(alerts, f, indent=2)

    # Save predictions for evaluation (optional)
    with open("predictions.json", "w", encoding="utf-8") as f:
        json.dump(predictions, f, indent=2)

    print(f"\nSaved {len(alerts)} alerts to {output_path}")

    # Run evaluation to compute metrics and save metrics_output.json
    try:
        from evaluation import evaluate

        metrics = evaluate(predictions, output_path="metrics_output.json")
    except Exception as e:
        print("Evaluation failed:", e)


if __name__ == "__main__":
    run_tests()
