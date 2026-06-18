# Algorithm Comparison Report: IDS Anomaly Detection Methods

This report compares three detection approaches used in the IoMT IDS system: rule-based detection, Isolation Forest, and Z-score anomaly detection.

## 1. Rule-Based Detection

### Principle
Rule-based detection applies hard thresholds and medical domain constraints to identify anomalies. It checks if measurements fall within predefined acceptable ranges for each device type.

**Ranges:**
- Heart Monitor: 40–180 bpm
- Thermometer: 35–42 °C
- Oximeter: 90–100 %
- Insulin Pump: 0–50 IU

### Advantages
- **Interpretable**: Decisions are immediately explainable to medical staff.
- **Fast**: Simple comparisons, no model training required.
- **Reliable for clear violations**: Works well for obvious out-of-range values.
- **No false positives for medical ranges**: If a value is inside the accepted range, it is trusted.
- **Easy to audit**: Thresholds can be updated quickly if clinical guidelines change.

### Limitations
- **Rigid**: Cannot adapt to patient-specific or temporal patterns.
- **Blind to subtle anomalies**: A borderline value inside the range passes inspection even if it may warrant investigation.
- **Limited context**: Does not account for historical trends or device behavior.

### When It Works Well
- Detecting obvious sensor failures or spoofed data (values like 200 bpm or –10 IU).
- Filtering out clearly invalid inputs (negative temperature, impossible oxygen saturation).
- Initial triage for downstream analysis.

### False Positives / False Negatives
- **False positives**: Rare; only when medical ranges are too strict or when valid edge cases are excluded.
- **False negatives**: Higher risk; subtle attacks that respect medical ranges (e.g., a slow drift in insulin delivery) pass undetected.

---

## 2. Isolation Forest

### Principle
Isolation Forest is an unsupervised ensemble method that builds random decision trees to isolate anomalies. Observations that are "easy to isolate" (require fewer splits) are considered anomalous.

### Advantages
- **Detects subtle patterns**: Can identify anomalies that respect normal ranges but deviate from the learned data distribution.
- **No assumptions about data distribution**: Works without assuming Gaussian or other distributions.
- **Unsupervised**: Requires no labeled anomaly data; trains on all traffic (normal and attack).
- **Scales well**: Efficient even with high-dimensional data.
- **Adaptable**: Can be retrained periodically to capture evolving normal behavior.

### Limitations
- **Black-box**: Provides an anomaly score but little explanation of why a sample is anomalous.
- **Sensitivity to training data**: If training data includes attacks, those patterns become "normal."
- **Requires representative training data**: Performance degrades if the training set does not cover all normal device behaviors (e.g., overnight inactivity, patient-specific patterns).
- **Hyperparameter tuning**: Threshold selection (e.g., 0.95 anomaly score) is often empirical and dataset-dependent.

### When It Works Well
- Detecting deviations from historical patterns (e.g., unusual insulin timing or heart rate spikes in context).
- Catching data distributions that shift over time.
- Supporting ensemble decisions (combining with rule-based or statistical methods).

### False Positives / False Negatives
- **False positives**: High risk during early deployment; any measurement pattern not seen in training can trigger alerts.
- **False negatives**: If attacks mimic normal traffic closely or if training data inadvertently includes attack patterns.

---

## 3. Z-Score Anomaly Detection

### Principle
Z-score measures how many standard deviations a value is from the population mean. For each device type, a reference mean and standard deviation are defined. The absolute Z-score is computed; values with |z| > 3 are flagged as anomalous.

**Z-Score Formula:**
```
z = |value - mean| / std_dev
```

**Reference Parameters (defined for each device type):**
- Heart Monitor: mean = 80 bpm, std = 8 bpm
- Thermometer: mean = 38.5 °C, std = 0.7 °C
- Oximeter: mean = 96 %, std = 2 %
- Insulin Pump: mean = 25 IU, std = 5 IU

### Advantages
- **Simple and fast**: Single arithmetic calculation per measurement.
- **Explainable**: The Z-score directly shows deviation from population mean.
- **Statistically grounded**: Based on probability theory; z > 3 represents ~99.7% confidence.
- **No training needed**: Uses predefined reference statistics, making it immediately applicable.
- **Low computational cost**: No model training or complex algorithms.
- **Interpretable for clinicians**: "This value is 3.5 standard deviations from normal"—meaningful in medical context.

### Limitations
- **Assumes Gaussian distribution**: If measurements are not normally distributed, interpretation can be misleading.
- **Requires representative mean/std**: Must be calibrated from correct data; if parameters are wrong, sensitivity suffers.
- **Ignores context**: Does not account for temporal trends, device state, or patient-specific factors.
- **Threshold choice (z > 3) is arbitrary**: May need adjustment based on clinical requirements.

### When It Works Well
- Identifying measurements that deviate significantly from population normal (e.g., a heart rate of 30 bpm or 200 bpm).
- Quick anomaly screening in real-time systems.
- Serving as a statistical baseline for comparison with other methods.

### False Positives / False Negatives
- **False positives**: If an unusual but valid measurement (e.g., athlete with low resting heart rate) is flagged as z > 3.
- **False negatives**: If an attack produces a value that is still within 3 standard deviations of the mean (e.g., a subtle drift in insulin from 25 IU to 32 IU).

---

## Comparative Summary

| Aspect | Rule-Based | Isolation Forest | Z-Score |
|--------|-----------|-----------------|---------|
| **Speed** | Very Fast | Fast | Very Fast |
| **Explainability** | Excellent | Poor | Good |
| **Sensitivity to Subtle Anomalies** | Low | High | Medium |
| **False Positive Risk** | Low | High | Medium |
| **False Negative Risk** | High | Low | Medium |
| **Adaptability** | Manual | Automatic (retrain) | Manual (parameter update) |
| **Training Data Requirement** | None | Yes | No |
| **Interpretability to Clinicians** | Direct | Opaque | Statistical |

---

## Recommendation for IoMT IDS

A **hybrid approach** combining all three methods is optimal:

1. **Rule-based detection** as the primary gate: Fast, safe, and explainable. Filters obvious violations.
2. **Z-score detection** as a statistical baseline: Low-cost, interpretable anomaly scoring for clinician confidence.
3. **Isolation Forest** as an optional enhancement: Deep pattern detection for security research or advanced analytics.

**Final Alert Decision:** Remain rule-based (medical range checks). Use anomaly scores from Z-score and Isolation Forest as:
- Supporting evidence in alert descriptions
- Input for LLM-based correlation and root-cause analysis
- Metrics for anomaly confidence reporting

This approach maintains safety (no false negatives from rule violations), explainability (clinicians understand why alerts are raised), and extensibility (anomaly scores inform downstream analysis).

---

## Files and References

- **ids/ids.py**: Contains `_compute_z_score()` method and anomaly score tracking.
- **ids/detection_file.py**: Main pipeline; generates `data/alerts.json`.
- **data/llm_error_cases.json**: Examples of false positives/negatives for LLM analysis.
- **data/llm_correlation_input.json**: Sample data with algorithm outputs for multi-event correlation.
