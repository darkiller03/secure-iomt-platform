import json
from collections import Counter
from ids import IDS
from evaluation import evaluate


def load_json(path):
    with open(path, "r", encoding="utf-8") as f:
        return json.load(f)


def explain_message(msg, ids):
    alert = ids.detect(msg)
    if alert is None:
        return "No alert generated"
    return f"Alert: {alert['alert_type']} - {alert['description']}"


def main():
    sample = load_json("sample_data_large.json")
    predictions = load_json("predictions.json")
    ids = IDS()

    cm = Counter()
    false_positives = []
    false_negatives = []

    for msg, pred in zip(sample, predictions):
        exp = pred["expected_label"]
        got = pred["predicted_label"]
        cm[(exp, got)] += 1
        if exp == "normal" and got == "attack":
            false_positives.append((msg, explain_message(msg, ids)))
        if exp == "attack" and got == "normal":
            false_negatives.append((msg, explain_message(msg, ids)))

    total = len(sample)
    tp = cm[("attack", "attack")]
    tn = cm[("normal", "normal")]
    fp = cm[("normal", "attack")]
    fn = cm[("attack", "normal")]
    precision = tp / (tp + fp) if tp + fp else 0.0
    recall = tp / (tp + fn) if tp + fn else 0.0
    accuracy = (tp + tn) / total if total else 0.0
    fpr = fp / (fp + tn) if fp + tn else 0.0
    fnr = fn / (fn + tp) if fn + tp else 0.0

    print("Large dataset IDS report")
    print("========================")
    print(f"Total messages tested: {total}")
    print(f"True Positives (TP): {tp}")
    print(f"True Negatives (TN): {tn}")
    print(f"False Positives (FP): {fp}")
    print(f"False Negatives (FN): {fn}")
    print(f"Precision: {precision:.4f}")
    print(f"Recall: {recall:.4f}")
    print(f"Accuracy: {accuracy:.4f}")
    print(f"False Positive Rate: {fpr:.4f}")
    print(f"False Negative Rate: {fnr:.4f}")
    print("\nConfusion matrix:")
    print(f"  attack/attack: {tp}")
    print(f"  attack/normal: {fn}")
    print(f"  normal/attack: {fp}")
    print(f"  normal/normal: {tn}")

    if false_positives:
        print("\nFalse positives details:")
        for i, (msg, reason) in enumerate(false_positives, 1):
            print(f"[{i}] {json.dumps(msg, indent=2)}")
            print(f"Reason: {reason}\n")

    if false_negatives:
        print("\nFalse negatives details:")
        for i, (msg, reason) in enumerate(false_negatives, 1):
            print(f"[{i}] {json.dumps(msg, indent=2)}")
            print(f"Reason: {reason}\n")

    # save the report to a file for review
    with open("large_dataset_report.txt", "w", encoding="utf-8") as f:
        f.write("Large dataset IDS report\n")
        f.write("========================\n")
        f.write(f"Total messages tested: {total}\n")
        f.write(f"True Positives (TP): {tp}\n")
        f.write(f"True Negatives (TN): {tn}\n")
        f.write(f"False Positives (FP): {fp}\n")
        f.write(f"False Negatives (FN): {fn}\n")
        f.write(f"Precision: {precision:.4f}\n")
        f.write(f"Recall: {recall:.4f}\n")
        f.write(f"Accuracy: {accuracy:.4f}\n")
        f.write(f"False Positive Rate: {fpr:.4f}\n")
        f.write(f"False Negative Rate: {fnr:.4f}\n")
        f.write("\nConfusion matrix:\n")
        f.write(f"  attack/attack: {tp}\n")
        f.write(f"  attack/normal: {fn}\n")
        f.write(f"  normal/attack: {fp}\n")
        f.write(f"  normal/normal: {tn}\n")
        if false_positives:
            f.write("\nFalse positives details:\n")
            for i, (msg, reason) in enumerate(false_positives, 1):
                f.write(f"[{i}] {json.dumps(msg)}\n")
                f.write(f"Reason: {reason}\n\n")
        if false_negatives:
            f.write("\nFalse negatives details:\n")
            for i, (msg, reason) in enumerate(false_negatives, 1):
                f.write(f"[{i}] {json.dumps(msg)}\n")
                f.write(f"Reason: {reason}\n\n")

    print("\nSaved detailed report to large_dataset_report.txt")


if __name__ == "__main__":
    main()
