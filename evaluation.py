"""
evaluation.py

Compute basic detection metrics from a list of predictions.

Functions:
 - evaluate(predictions, output_path): compute metrics and save JSON.

Predictions format (list of dicts):
  {"expected_label": "normal"|"attack", "predicted_label": "normal"|"attack"}

Output JSON: metrics_output.json with fields described in the assignment.
"""
import json
from typing import List, Dict


def evaluate(predictions: List[Dict], output_path: str = "metrics_output.json"):
    """Compute TP, TN, FP, FN and derived metrics, save to JSON and print.

    predictions: list of {'expected_label': 'normal'|'attack', 'predicted_label': 'normal'|'attack'}
    """
    tp = tn = fp = fn = 0
    for p in predictions:
        exp = p.get("expected_label")
        pred = p.get("predicted_label")
        if exp == "attack" and pred == "attack":
            tp += 1
        elif exp == "normal" and pred == "normal":
            tn += 1
        elif exp == "normal" and pred == "attack":
            fp += 1
        elif exp == "attack" and pred == "normal":
            fn += 1

    total = tp + tn + fp + fn

    precision = tp / (tp + fp) if (tp + fp) > 0 else 0.0
    recall = tp / (tp + fn) if (tp + fn) > 0 else 0.0
    false_positive_rate = fp / (fp + tn) if (fp + tn) > 0 else 0.0
    false_negative_rate = fn / (fn + tp) if (fn + tp) > 0 else 0.0
    accuracy = (tp + tn) / total if total > 0 else 0.0

    metrics = {
        "detection_precision": round(precision, 4),
        "detection_recall": round(recall, 4),
        "false_positive_rate": round(false_positive_rate, 4),
        "false_negative_rate": round(false_negative_rate, 4),
        "accuracy": round(accuracy, 4),
        "true_positives": tp,
        "true_negatives": tn,
        "false_positives": fp,
        "false_negatives": fn,
    }

    # Save metrics
    with open(output_path, "w", encoding="utf-8") as f:
        json.dump(metrics, f, indent=2)

    # Print metrics clearly
    print("\nEvaluation metrics:")
    print(f"  True Positives : {tp}")
    print(f"  True Negatives : {tn}")
    print(f"  False Positives: {fp}")
    print(f"  False Negatives: {fn}")
    print(f"  Precision      : {metrics['detection_precision']}")
    print(f"  Recall         : {metrics['detection_recall']}")
    print(f"  False+ Rate    : {metrics['false_positive_rate']}")
    print(f"  False- Rate    : {metrics['false_negative_rate']}")
    print(f"  Accuracy       : {metrics['accuracy']}")

    return metrics


if __name__ == "__main__":
    # When run directly, try to read a predictions file
    try:
        with open("predictions.json", "r", encoding="utf-8") as f:
            preds = json.load(f)
    except FileNotFoundError:
        print("predictions.json not found. Expected format: list of {expected_label,predicted_label} records.")
        preds = []
    evaluate(preds)
