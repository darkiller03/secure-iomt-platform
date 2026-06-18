import json
import pandas as pd
from pathlib import Path
from sklearn.ensemble import IsolationForest
from sklearn.svm import OneClassSVM
from sklearn.neighbors import LocalOutlierFactor
from sklearn.preprocessing import StandardScaler

DATA_PATH = Path("algo_comparaison/validated_data.json")
OUTPUT_PATH = Path("algo_comparaison/algo_comparison_results.json")

DEVICE_RANGES = {
    "heart_monitor": (40, 180),
    "smart_thermometer": (35, 42),
    "oximeter": (90, 100),
    "insulin_pump": (0, 50),
}


def load_data():
    with open(DATA_PATH, "r", encoding="utf-8") as f:
        return json.load(f)


def rule_label(row):
    min_v, max_v = DEVICE_RANGES.get(row["device_type"], (-9999, 9999))
    return 1 if row["value"] < min_v or row["value"] > max_v else 0


def main():
    data = load_data()
    df = pd.DataFrame(data)

    df = df[["device_id", "patient_id", "device_type", "value", "timestamp"]].copy()
    df["value"] = pd.to_numeric(df["value"], errors="coerce")
    df = df.dropna(subset=["value"])

    # Rule-based label used as reference
    df["expected_anomaly"] = df.apply(rule_label, axis=1)

    results = []

    for device_type in df["device_type"].unique():
        sub = df[df["device_type"] == device_type].copy()

        if len(sub) < 10:
            continue

        X = sub[["value"]].values
        X_scaled = StandardScaler().fit_transform(X)

        models = {
            "Isolation Forest": IsolationForest(
                contamination=0.05,
                random_state=42
            ),
            "One-Class SVM": OneClassSVM(
                kernel="rbf",
                gamma="scale",
                nu=0.05
            ),
            "LOF": LocalOutlierFactor(
                n_neighbors=10,
                contamination=0.05
            )
        }

        for name, model in models.items():
            if name == "LOF":
                pred = model.fit_predict(X_scaled)
            else:
                model.fit(X_scaled)
                pred = model.predict(X_scaled)

            # sklearn: -1 = anomaly, 1 = normal
            sub[f"{name}_anomaly"] = [1 if p == -1 else 0 for p in pred]

            detected = int(sub[f"{name}_anomaly"].sum())
            expected = int(sub["expected_anomaly"].sum())

            true_positive = int(
                ((sub["expected_anomaly"] == 1) & (sub[f"{name}_anomaly"] == 1)).sum()
            )
            false_positive = int(
                ((sub["expected_anomaly"] == 0) & (sub[f"{name}_anomaly"] == 1)).sum()
            )
            false_negative = int(
                ((sub["expected_anomaly"] == 1) & (sub[f"{name}_anomaly"] == 0)).sum()
            )

            results.append({
                "device_type": device_type,
                "algorithm": name,
                "total_messages": len(sub),
                "expected_anomalies_rule_based": expected,
                "detected_anomalies": detected,
                "true_positive": true_positive,
                "false_positive": false_positive,
                "false_negative": false_negative
            })

    with open(OUTPUT_PATH, "w", encoding="utf-8") as f:
        json.dump(results, f, indent=2)

    print("Comparison saved to:", OUTPUT_PATH)
    print(pd.DataFrame(results))


if __name__ == "__main__":
    main()