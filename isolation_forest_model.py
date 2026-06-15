"""
Isolation Forest model prototype.

This module trains a small Isolation Forest on synthetic "normal" heart rate
data (60-100 bpm) to provide a simple anomaly score for incoming heart_rate
values. The `score` method returns a float in [0,1] where higher means more
anomalous.

This is a lightweight prototype for testing and does not persist models.
"""

import numpy as np
from sklearn.ensemble import IsolationForest


class IsolationForestModel:
    def __init__(self):
        self.model = None

    def train(self, n_samples=500):
        """
        Train Isolation Forest on synthetic normal heart rates (60-100 bpm).
        """
        # Generate synthetic normal data around 60-100 bpm
        rng = np.random.RandomState(42)
        normal = rng.normal(loc=80, scale=8, size=(n_samples, 1))
        # Clip to a reasonable range
        normal = np.clip(normal, 40, 180)

        self.model = IsolationForest(random_state=42, contamination=0.005)
        self.model.fit(normal)

    def score(self, heart_rate):
        """
        Return an anomaly score between 0 and 1. Uses the signed decision_function
        and converts it so that higher means more anomalous.
        """
        if self.model is None:
            raise RuntimeError("Model not trained. Call train() first.")

        import numpy as _np

        x = _np.array([[heart_rate]])
        # decision_function: higher => more normal, lower => more anomalous
        df = self.model.decision_function(x)[0]
        # Convert to 0..1 anomaly score: map df (approx -0.5..0.5) to 0..1
        # We'll use a simple logistic-like scaling
        score = 1.0 / (1.0 + _np.exp(5 * df))
        # clamp
        score = float(max(0.0, min(1.0, score)))
        return score


if __name__ == "__main__":
    m = IsolationForestModel()
    m.train()
    print("Sample scores:")
    for hr in [72, 85, 35, 190]:
        print(hr, m.score(hr))
