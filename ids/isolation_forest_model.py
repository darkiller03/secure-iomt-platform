"""
Isolation Forest model prototype.

This module trains separate Isolation Forests for each supported device type.
Each model is trained on synthetic normal measurements for its device range.
The `score` method returns a float in [0,1] where higher means more anomalous.
"""

import numpy as np
from sklearn.ensemble import IsolationForest


class IsolationForestModel:
    TRAIN_CONFIG = {
        "heart_monitor": {"loc": 80.0, "scale": 8.0, "min": 40.0, "max": 180.0},
        "thermometer": {"loc": 38.5, "scale": 0.7, "min": 35.0, "max": 42.0},
        "oximeter": {"loc": 96.0, "scale": 2.0, "min": 90.0, "max": 100.0},
        "insulin_pump": {"loc": 25.0, "scale": 5.0, "min": 0.0, "max": 50.0},
    }

    def __init__(self):
        self.models = {}

    def train(self, n_samples=500):
        """Train an Isolation Forest model for each supported device type."""
        rng = np.random.RandomState(42)
        self.models = {}

        for device_type, config in self.TRAIN_CONFIG.items():
            normal = rng.normal(loc=config["loc"], scale=config["scale"], size=(n_samples, 1))
            normal = np.clip(normal, config["min"], config["max"])

            model = IsolationForest(random_state=42, contamination=0.01)
            model.fit(normal)
            self.models[device_type] = model

    def score(self, device_type, value):
        """Return an anomaly score between 0 and 1 for the given device type."""
        if device_type not in self.models:
            raise RuntimeError(f"Model for device_type '{device_type}' not trained.")

        if self.models[device_type] is None:
            raise RuntimeError("Model not trained. Call train() first.")

        x = np.array([[value]])
        df = self.models[device_type].decision_function(x)[0]
        score = 1.0 / (1.0 + np.exp(20 * df))
        score = float(max(0.0, min(1.0, score)))
        return score


if __name__ == "__main__":
    m = IsolationForestModel()
    m.train()
    print("Sample scores:")
    for device_type, values in {
        "heart_monitor": [72, 85, 35, 190],
        "thermometer": [36.5, 40.0, 30.0, 45.0],
        "oximeter": [95, 99, 85, 102],
        "insulin_pump": [25, 10, 55, 80],
    }.items():
        print(f"{device_type}:")
        for value in values:
            print(" ", value, m.score(device_type, value))
