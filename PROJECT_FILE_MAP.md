# Project File Map & Teacher Request Traceability

Complete inventory of all project files, their purposes, and implementation of teacher-requested features.

---

## Section 1: Complete File Inventory

### Root Directory Files

**File: README.md**
- **Purpose**: Main project documentation; overview of IoMT IDS system, setup, and usage
- **Production Required**: No (informational)
- **Testing Required**: No (informational)
- **Teacher-Requested**: No (pre-existing)
- **Content**: Project overview, architecture diagram, feature summary

**File: requirements.txt**
- **Purpose**: Root-level Python dependencies (currently empty; IDS-specific dependencies are in ids/requirements.txt)
- **Production Required**: No
- **Testing Required**: No
- **Teacher-Requested**: No (pre-existing)

**File: .gitignore**
- **Purpose**: Git ignore rules for version control
- **Production Required**: No (VCS artifact)
- **Testing Required**: No
- **Teacher-Requested**: No (pre-existing)

**File: ALGORITHM_COMPARISON_REPORT.md**
- **Purpose**: Educational comparison of Rule-Based, Isolation Forest, and Z-Score detection methods
- **Production Required**: No (informational/educational)
- **Testing Required**: No (reference for LLM)
- **Teacher-Requested**: Yes ✓ (Part of "Test another detection algorithm" request)
- **Content**: Principles, advantages, limitations, use cases for each algorithm; hybrid recommendation

**File: INTEGRATION_REPORT.md**
- **Purpose**: Documentation of system integration, component communication, and data flow
- **Production Required**: No (informational)
- **Testing Required**: No (reference)
- **Teacher-Requested**: No (pre-existing)

**File: PIPELINE_COMPATIBILITY_REPORT.md**
- **Purpose**: Documentation of file-based pipeline compatibility and integration constraints
- **Production Required**: No (informational)
- **Testing Required**: No (reference)
- **Teacher-Requested**: No (pre-existing)

**File: IDS_FINAL_SUMMARY.md**
- **Purpose**: Complete summary of all teacher-requested improvements and their implementation status
- **Production Required**: No (informational)
- **Testing Required**: No (reference)
- **Teacher-Requested**: Yes ✓ (Generated as final deliverable summary)
- **Content**: Status of all 8 improvements, validation results, deployment checklist

---

### ids/ Directory - Core IDS Engine

**File: ids/ids.py**
- **Purpose**: Main IDS detection engine; runs all detection rules per message and end-of-file
- **Production Required**: **Yes** (core detection logic)
- **Testing Required**: **Yes** (unit tests, integration tests)
- **Teacher-Requested**: Partially (4 new detections added to existing core)
- **Classes/Methods**:
  - `IDS` class: Main detection engine
  - `__init__()`: Initialize detection state
  - `detect()`: Per-message detection (rule-based, patient ID change, replay attack, programming change)
  - `finalize()`: End-of-file processing (silent device detection)
  - `_compute_z_score()`: Z-score anomaly calculation
  - `_extract_measurement()`: Measurement validation
  - `_build_alert()`: Alert construction
  - `process_message()`: Debug method for manual testing

**Existing Features**:
- Data Injection detection (range checks)
- Device Spoofing detection (unknown device ID)
- DoS detection (message rate analysis)
- Isolation Forest anomaly scoring

**Teacher-Requested Features Added**:
- Silent Device Detection (finalize method, last_seen tracking)
- Patient ID Change Detection (first_patient tracking, per-message check)
- Replay Attack Detection (fingerprint tracking, per-message check)
- Programming Change Detection (insulin_history sliding window, per-message check)
- Z-Score Detection (_compute_z_score method, score storage)

---

**File: ids/detection_file.py**
- **Purpose**: Entry point for file-based IDS pipeline; reads validated_data.json, processes messages, writes alerts.json
- **Production Required**: **Yes** (pipeline orchestrator)
- **Testing Required**: **Yes** (end-to-end pipeline tests)
- **Teacher-Requested**: Partially (updated to call finalize() for EOF alerts)
- **Functions**:
  - `to_dashboard_alert()`: Converts internal alert format to dashboard format
  - `load_messages()`: Reads JSON message file
  - `save_alerts()`: Writes JSON alert file
  - `__main__`: Pipeline orchestration (load → detect → finalize → save)

**Changes for Teacher Requests**:
- Added EOF processing: compute latest dataset timestamp and call `ids.finalize()`
- Normalized severity formatting (title-case)

---

**File: ids/alert_generator.py**
- **Purpose**: Creates alert JSON objects in standardized format
- **Production Required**: **Yes** (alert formatting)
- **Testing Required**: **Yes** (alert schema validation)
- **Teacher-Requested**: No (pre-existing)
- **Functions**:
  - `create_alert()`: Constructs alert dict with required fields (alert_id, timestamp, device_id, alert_type, severity, anomaly_score, description, recommended_action)

---

**File: ids/isolation_forest_model.py**
- **Purpose**: Trains and scores anomalies using Isolation Forest unsupervised ensemble method
- **Production Required**: Optional (available but not primary decision driver)
- **Testing Required**: No (model training is internal)
- **Teacher-Requested**: No (pre-existing; kept for reference/comparison)
- **Classes/Methods**:
  - `IsolationForestModel` class
  - `train()`: Trains model on measurement features
  - `score()`: Returns anomaly score for a measurement

---

**File: ids/README.md**
- **Purpose**: IDS-specific documentation; detection methods, features, examples, and new extensions
- **Production Required**: No (informational)
- **Testing Required**: No (reference)
- **Teacher-Requested**: Yes ✓ (Updated with new detection features section)
- **Content**: 
  - Input/output paths and formats
  - Supported devices and ranges
  - Detection methods (both existing and new)
  - New features documentation (Silent Device, Patient ID Change, Replay Attack, Programming Change, Z-Score)
  - Examples for each detection type
  - Integration notes with Student 4 LLM

---

**File: ids/requirements.txt**
- **Purpose**: IDS-specific Python dependencies (scikit-learn for Isolation Forest)
- **Production Required**: **Yes** (if Isolation Forest model is used)
- **Testing Required**: **Yes** (for running tests)
- **Teacher-Requested**: No (pre-existing)
- **Content**: scikit-learn version specification

---

### data/ Directory - Datasets and LLM Input

**File: data/validated_data.json**
- **Purpose**: Input dataset for IDS; contains 104 MQTT messages representing normal traffic and attacks
- **Production Required**: **Yes** (test/validation dataset; live data would replace this in production)
- **Testing Required**: **Yes** (golden dataset for regression tests)
- **Teacher-Requested**: Partially (extended with test cases for new detections)
- **Content**: 104 messages with fields: device_id, patient_id, device_type, value, unit, timestamp, status, expected_label
- **Coverage**:
  - Normal traffic (60+ messages across all devices)
  - Data Injection examples (out-of-range values)
  - Device Spoofing examples (unknown device IDs)
  - DoS examples (high-frequency messages)
  - Replay Attack examples (duplicate OXY001 message)
  - Patient ID Change examples (HRM001 with different patient_id)
  - Programming Change examples (insulin spike INP001)

---

**File: data/alerts.json**
- **Purpose**: Output file from detection_file.py; contains dashboard-formatted alerts
- **Production Required**: **Yes** (alerts consumed by dashboard)
- **Testing Required**: **Yes** (verification of alert generation)
- **Teacher-Requested**: No (generated output, not a new file)
- **Content**: 29 alerts in dashboard format (type, device, severity, timestamp, description, recommended_action)
- **Generated from**: validated_data.json via ids/detection_file.py

---

**File: data/llm_error_cases.json**
- **Purpose**: Educational dataset showing false positive, false negative, and borderline cases for LLM training
- **Production Required**: No (LLM training resource only)
- **Testing Required**: No (reference data)
- **Teacher-Requested**: Yes ✓ (Part of "Generate false positive and false negative examples for LLM" request)
- **Content**: 9 structured cases with fields:
  - case_id, case_type (false_positive/false_negative/borderline)
  - raw_message (MQTT message)
  - algorithm_outputs (rule_based, z_score, isolation_forest decisions)
  - expected_label (ground truth)
  - explanation (why this is a FP/FN/borderline)
- **Examples**:
  - FP-001: Low resting heart rate (52 bpm) flagged by z-score but medically normal
  - FP-002: Early morning temperature (36.0°C) flagged by z-score but physiologically normal
  - FP-003: High oxygen saturation (98.5%) borderline in Isolation Forest but normal
  - FN-001: Gradual insulin increase attack (within range, missed by all)
  - FN-002: Subtle heart rate manipulation (drift undetected)
  - FN-003: Message replay (detected by fingerprint, not by measurement anomaly)
  - BORDERLINE-001: High fever (39.5°C) medically significant but not attack
  - BORDERLINE-002: Heart rate during exercise (178 bpm) legitimate extreme physiology
  - BORDERLINE-003: High insulin dose (48 IU) at boundary, needs context

---

**File: data/llm_correlation_input.json**
- **Purpose**: Structured multi-event dataset for LLM-driven correlation and root-cause analysis
- **Production Required**: No (LLM analysis input only)
- **Testing Required**: No (reference data)
- **Teacher-Requested**: Yes ✓ (Part of "Prepare multi-event LLM correlation input" request)
- **Content**: Structured bundle with:
  - `dataset_info`: Metadata (total_messages, total_alerts)
  - `raw_mqtt_messages`: 12 representative messages (normal, attacks, anomalies)
  - `algorithm_outputs`: Detailed per-message results (z_score, isolation_forest_score, rule_based_decision)
  - `generated_alerts`: Dashboard-format alerts from IDS
  - `correlation_analysis_notes`: Timeline, patterns, recommendations
- **Use Case**: Student 4 ingests this to perform multi-event correlation, attack classification, and contextual analysis

---

## Section 2: Teacher Request Traceability

Complete mapping of each teacher-requested feature to its implementation locations.

---

### Request 1: Silent Device Detection

**Specification**: Track last timestamp per known device; after processing all messages, compare to latest dataset timestamp; if > 30 seconds silent → alert.

**Implemented in**:
- **ids/ids.py**:
  - `__init__()`: Initialize `self.last_seen` dict (tracks device last-seen timestamps)
  - `detect()`: Update `self.last_seen[device_id]` per message
  - `finalize(latest_event_ts, silence_threshold=30.0)`: Generate end-of-file alerts for all known devices with no recent activity
  - `Z_SCORE_CONFIG`: Supporting data (device configurations)

- **ids/detection_file.py**:
  - `__main__`: Compute `latest_ts` from dataset, call `ids.finalize(latest_ts)`, append EOF alerts to dashboard

**Dataset Examples**:
- validated_data.json: Last message at 11:16:00; devices HRM001, THM001 have gaps > 30s → Silent Device alerts generated

**Documentation**:
- ids/README.md: "Silent Device Detection" section with example alert
- ALGORITHM_COMPARISON_REPORT.md: Mentioned in context of detection scope
- IDS_FINAL_SUMMARY.md: Implementation status, validation results

**Test Data**:
- data/llm_error_cases.json: No direct example (not an error case)
- data/llm_correlation_input.json: Could generate silent device alerts after msg_012

**Validation**:
- IDS_FINAL_SUMMARY.md: 2 Silent Device alerts in final test run

---

### Request 2: Patient ID Change Detection

**Specification**: Track first patient_id per device; if same device reports different patient_id → alert.

**Implemented in**:
- **ids/ids.py**:
  - `__init__()`: Initialize `self.first_patient` dict (tracks initial patient assignment)
  - `detect()`: 
    - Record first patient_id seen per device
    - Check if current patient_id differs from first; if yes → return alert

- **ids/detection_file.py**: No changes needed (uses standard detect loop)

**Dataset Examples**:
- validated_data.json: HRM001 initially P001, later P999 (around line 1000) → Patient ID Change alert

**Documentation**:
- ids/README.md: "Patient ID Change Detection" section with example alert
- ALGORITHM_COMPARISON_REPORT.md: Mentioned in context of device identity verification
- IDS_FINAL_SUMMARY.md: Implementation status, 1 alert in final test

**Test Data**:
- data/llm_error_cases.json: No direct example (not an error case)
- data/llm_correlation_input.json: msg_007 triggers Patient ID Change (P001 → P999)

**Validation**:
- IDS_FINAL_SUMMARY.md: 1 Patient ID Change alert in final test run

---

### Request 3: Replay Attack Detection

**Specification**: Build fingerprint (device_id|patient_id|device_type|value|unit|timestamp); store seen fingerprints; detect duplicates.

**Implemented in**:
- **ids/ids.py**:
  - `__init__()`: Initialize `self.fingerprints` set (stores seen message fingerprints)
  - `detect()`:
    - Build fingerprint from message fields
    - Check if fingerprint already seen; if yes → return Replay Attack alert
    - Add fingerprint to set for future comparisons

- **ids/detection_file.py**: No changes needed

**Dataset Examples**:
- validated_data.json: OXY001 message with value 95.3% at 11:16:00 repeated immediately → Replay Attack alert on second occurrence

**Documentation**:
- ids/README.md: "Replay Attack Detection" section with example alert
- ALGORITHM_COMPARISON_REPORT.md: Example of signature-based detection
- IDS_FINAL_SUMMARY.md: Implementation status, 1 alert in final test

**Test Data**:
- data/llm_error_cases.json: FN-003 example (replay attack missed by measurement anomaly algorithms, detected by fingerprint)
- data/llm_correlation_input.json: msg_006 is replay of msg_004 (OXY001, 97%, same timestamp) → generates Replay Attack alert

**Validation**:
- IDS_FINAL_SUMMARY.md: 1 Replay Attack alert in final test run

---

### Request 4: Insulin Pump Programming Change Detection (Prototype)

**Specification**: For insulin_pump only, maintain sliding window of previous insulin values; if current > 2×average AND > 20 IU → alert.

**Implemented in**:
- **ids/ids.py**:
  - `__init__()`: Initialize `self.insulin_history` defaultdict with deques (maxlen=5 per device)
  - `detect()`:
    - For device_type == "insulin_pump":
      - Compute average of history
      - Check if current value > avg×2 AND > 20 IU; if yes → return Programming Change alert
      - Append current value to history

- **ids/detection_file.py**: No changes needed

**Dataset Examples**:
- validated_data.json: INP001 previous avg ~25 IU, new value 50 or 80 IU (out of range) → Programming Change alert

**Documentation**:
- ids/README.md: "Programming Change Suspected" section with example alert and rule explanation
- ALGORITHM_COMPARISON_REPORT.md: Example of temporal/contextual detection
- IDS_FINAL_SUMMARY.md: Implementation status, 4 alerts in final test

**Test Data**:
- data/llm_error_cases.json: No direct FP/FN example (values are usually out of range anyway)
- data/llm_correlation_input.json: msg_008 (INP001, 50 IU) triggers Programming Change alert; shows sliding_window_history and reason

**Validation**:
- IDS_FINAL_SUMMARY.md: 4 Programming Change alerts in final test run (3 in message loop, 1 from spike)

---

### Request 5: Second Anomaly Detection Algorithm - Z-Score

**Specification**: Define mean/std for each device; compute z = |value - mean| / std; if z > 3 → anomaly.

**Implemented in**:
- **ids/ids.py**:
  - `Z_SCORE_CONFIG` class variable: Define mean & std for each device type
    - Heart Monitor: mean=80, std=8
    - Thermometer: mean=38.5, std=0.7
    - Oximeter: mean=96, std=2
    - Insulin Pump: mean=25, std=5
  - `_compute_z_score(device_type, value)`: Calculate z-score (formula: z = |value - mean| / std)
  - `detect()`: Call `_compute_z_score()` for every measurement; store in `self.last_scores[device_id]` dict for LLM analysis
  - Key: Z-score does NOT override rule-based decision; it's supporting evidence only

- **ids/detection_file.py**: No changes needed (z-scores stored internally, not used for alerting)

**Documentation**:
- ids/README.md: "Z-Score Detection" section; explains algorithm, parameters, role as supporting evidence
- ALGORITHM_COMPARISON_REPORT.md: **Dedicated section** on Z-Score method; principles, advantages, limitations, when it works well
- IDS_FINAL_SUMMARY.md: Implementation status, emphasis on supporting evidence role

**Test Data**:
- data/llm_error_cases.json: **Multiple examples** using z-score outputs:
  - FP-001: z_score=3.5 (low heart rate flagged but normal)
  - FP-002: z_score=3.57 (low temperature flagged but normal)
  - FP-003: z_score=1.25 (high oxygen flagged by IF, not z-score)
  - FN-001: z_score=2.0 (insulin increase, below threshold)
  - FN-002: z_score=0.625 (subtle drift, below threshold)
  - BORDERLINE-001: z_score=1.43 (fever, below threshold but clinically significant)
  - BORDERLINE-002: z_score=12.25 (extreme HR during exercise, very high)
  - BORDERLINE-003: z_score=4.6 (high insulin, above threshold)

- data/llm_correlation_input.json: **Algorithm outputs include z-score for every message**:
  - msg_001-012: Shows z_score, z_score_flag for each
  - Example: msg_005 (HRM001, 155 bpm): z_score=9.375, z_score_flag=true

**Validation**:
- Z-scores computed for all 104 messages (available in internal tracking; not shown in final alerts.json because they don't override rules)

---

### Request 6: Algorithm Comparison Report

**Specification**: Compare Rule-Based, Isolation Forest, and Z-Score detection methods; explain trade-offs; recommend hybrid approach.

**Implemented in**:
- **ALGORITHM_COMPARISON_REPORT.md**: **Dedicated 400+ line document** with:
  - Section 1: Rule-Based Detection (principle, advantages, limitations, when it works, FP/FN)
  - Section 2: Isolation Forest (principle, advantages, limitations, when it works, FP/FN)
  - Section 3: Z-Score Anomaly Detection (principle, advantages, limitations, when it works, FP/FN)
  - Comparative Summary Table (Speed, Explainability, Sensitivity, False Positive Risk, etc.)
  - Recommendation for IoMT IDS (hybrid approach: rule-based gate + z-score baseline + IF enhancement)
  - References to files and LLM integration

**Documentation References**:
- ids/README.md: Links to ALGORITHM_COMPARISON_REPORT.md
- IDS_FINAL_SUMMARY.md: References algorithm tradeoffs

**Use for LLM**:
- data/llm_error_cases.json: Shows real-world examples of each algorithm's strengths/weaknesses
- data/llm_correlation_input.json: Shows side-by-side algorithm outputs for comparison

---

### Request 7: False Positive / False Negative Examples

**Specification**: Generate 3 FP, 3 FN, 3 borderline cases; show algorithm outputs and explanations.

**Implemented in**:
- **data/llm_error_cases.json**: **9 structured cases** (3 FP + 3 FN + 3 borderline) with:
  - case_id (FP-001, FP-002, FP-003, FN-001, FN-002, FN-003, BORDERLINE-001, BORDERLINE-002, BORDERLINE-003)
  - raw_message: Full MQTT message
  - algorithm_outputs: rule_based, z_score, isolation_forest scores
  - expected_label: Ground truth (normal, attack, normal_but_concerning, normal_but_extreme, normal_but_investigate)
  - explanation: Why this is FP/FN/borderline, what each algorithm does

**False Positive Examples**:
- FP-001: Low resting heart rate (52 bpm); z-score=3.5 flags it, but medically normal (athlete/wake-up)
- FP-002: Early morning temperature (36.0°C); z-score=3.57 flags it, but circadian rhythm normal
- FP-003: High oxygen saturation (98.5%); IF flags it if training data didn't include high values, but clinically normal

**False Negative Examples**:
- FN-001: Gradual insulin increase attack (35 IU); all algorithms miss it because it's within range
- FN-002: Subtle heart rate drift (75 bpm); z-score=0.625 and IF don't detect slow manipulation
- FN-003: Replay attack (94%); measurement is normal; fingerprint-based detection needed (measurement anomaly won't catch it)

**Borderline Examples**:
- BORDERLINE-001: High fever (39.5°C); clinically significant but not a cyber-attack; z-score=1.43 (low flag)
- BORDERLINE-002: Exercise heart rate (178 bpm); extreme but legitimate; z-score=12.25 (very high); needs contextual decision
- BORDERLINE-003: High insulin dose (48 IU); at device boundary; z-score=4.6 (above threshold); needs investigation

**Documentation**:
- ALGORITHM_COMPARISON_REPORT.md: References FP/FN patterns
- IDS_FINAL_SUMMARY.md: Notes importance of edge case handling

---

### Request 8: Multi-Event LLM Correlation Input

**Specification**: Bundle raw messages + alerts + algorithm outputs + correlation notes for LLM analysis.

**Implemented in**:
- **data/llm_correlation_input.json**: **Structured 500+ line JSON** with:
  - `dataset_info`: Metadata (12 messages, 6 alerts)
  - `raw_mqtt_messages`: 12 representative MQTT messages (msg_001-msg_012)
    - Normal: msg_001-004, msg_009-012 (devices reporting normal values)
    - Attacks: msg_005 (data injection), msg_006 (replay), msg_007 (patient ID change), msg_008 (programming change)
  - `algorithm_outputs`: 6 detailed entries showing per-message analysis
    - rule_based_decision: NORMAL or ALERT
    - z_score: Computed value
    - z_score_flag: Boolean (z > 3)
    - isolation_forest_score: Anomaly score
    - Key alerts: replay_fingerprint, patient_id_change_detected, sliding_window_history, etc.
  - `generated_alerts`: 4 dashboard-format alerts (Data Injection, Replay Attack, Patient ID Change, Programming Change)
  - `correlation_analysis_notes`:
    - timeline: All events within 55 seconds
    - device_anomaly: HRM001 shows 2 related alerts (possible device compromise)
    - multi_device_pattern: INP001 also shows alert (potential distributed attack)
    - recommended_llm_actions: 5 specific correlation steps for LLM

**Use for LLM**:
- Input for Student 4's multi-event correlation engine
- Shows how individual message anomalies relate to attack patterns
- Demonstrates importance of temporal correlation, device grouping, contextual analysis

**Documentation**:
- ids/README.md: "Integration with Student 4 (LLM System)" section
- IDS_FINAL_SUMMARY.md: "Student 4 / LLM Preparation" section

---

## Section 3: Dependency Map

Complete file relationships and data flow through the system.

```
Project Root
├── README.md (documentation)
├── requirements.txt (root dependencies, currently empty)
├── ALGORITHM_COMPARISON_REPORT.md (algorithm education)
├── INTEGRATION_REPORT.md (integration overview)
├── PIPELINE_COMPATIBILITY_REPORT.md (pipeline constraints)
├── IDS_FINAL_SUMMARY.md (final deliverable summary)
│
├── ids/ (core detection engine)
│   ├── ids.py (main detection logic)
│   │   ├── imports: isolation_forest_model, alert_generator
│   │   ├── exports: IDS class with detect(), finalize(), _compute_z_score()
│   │   └── state: last_seen, first_patient, fingerprints, insulin_history, last_scores
│   │
│   ├── detection_file.py (pipeline orchestrator)
│   │   ├── imports: ids.IDS, json, pathlib
│   │   ├── functions: load_messages(), save_alerts(), to_dashboard_alert()
│   │   └── invokes: ids.detect() per message, ids.finalize() for EOF
│   │
│   ├── alert_generator.py (alert schema)
│   │   ├── function: create_alert()
│   │   └── used by: ids.py _build_alert()
│   │
│   ├── isolation_forest_model.py (optional anomaly scoring)
│   │   ├── class: IsolationForestModel
│   │   └── used by: ids.py during init (trained but not primary decision)
│   │
│   ├── README.md (IDS documentation)
│   │   └── references: ids.py features, detection methods, LLM integration
│   │
│   └── requirements.txt (IDS dependencies: scikit-learn)
│
└── data/ (datasets and LLM input)
    ├── validated_data.json (input messages: 104 messages)
    │   └── read by: detection_file.py load_messages()
    │
    ├── alerts.json (output alerts: 29 alerts)
    │   └── written by: detection_file.py save_alerts()
    │   └── consumed by: Dashboard, LLM
    │
    ├── llm_error_cases.json (LLM training data: 9 edge cases)
    │   └── used by: Student 4 confidence calibration
    │
    └── llm_correlation_input.json (LLM input: 12 messages + algorithm outputs)
        └── used by: Student 4 multi-event correlation and analysis

Data Flow (File-Based Pipeline):
================================

validated_data.json (104 msgs)
    ↓
detection_file.py
    ├─ load_messages()
    ├─ ids.detect() × 104
    │   ├─ check rules (data injection, device spoofing, DoS)
    │   ├─ compute z_score() [store in last_scores]
    │   ├─ check patient ID change [store in first_patient]
    │   ├─ check replay attack [store in fingerprints]
    │   ├─ check programming change [update insulin_history]
    │   ├─ check silent device prep [update last_seen]
    │   └─ return alert or None
    ├─ ids.finalize(latest_ts)
    │   └─ for each known device: check last_seen vs latest_ts; generate Silent Device alerts
    ├─ to_dashboard_alert() × 29
    │   └─ convert internal format to {type, device, severity, timestamp, description, recommended_action}
    └─ save_alerts()
    ↓
alerts.json (29 alerts, dashboard format)
    ↓
┌─ Dashboard display
└─ LLM ingestion
    ├─ consumes: alerts.json
    ├─ references: llm_error_cases.json (confidence calibration)
    ├─ references: llm_correlation_input.json (multi-event analysis)
    └─ references: ALGORITHM_COMPARISON_REPORT.md (algorithm knowledge)

Dependency Relationships:
=========================

ids/ids.py
    ├── imports: isolation_forest_model (IF model training)
    ├── imports: alert_generator (alert schema)
    └── imports: json, re, time, datetime, collections, defaultdict

ids/detection_file.py
    ├── imports: ids.IDS
    ├── imports: json, pathlib
    └── reads: data/validated_data.json
    └── writes: data/alerts.json

ids/alert_generator.py
    ├── imports: json, uuid, time
    └── used by: ids.py _build_alert()

ids/isolation_forest_model.py
    ├── imports: scikit-learn, numpy
    └── used by: ids.py __init__() [training only; model integrated but not primary decision driver]

data/validated_data.json
    └── source: Extended from original with new test cases (replay, patient ID change, programming change)

data/alerts.json
    └── generated: From validated_data.json via detection_file.py

data/llm_error_cases.json
    └── source: Manually created 9 edge cases for LLM training

data/llm_correlation_input.json
    └── source: Manually created representative dataset with algorithm outputs

ALGORITHM_COMPARISON_REPORT.md
    └── source: Manually created algorithm education document

Documentation Flow:
===================

README.md (main overview)
    └─ references: ids/README.md, ALGORITHM_COMPARISON_REPORT.md

ids/README.md (IDS documentation)
    ├─ documents: Detection methods (new and existing)
    ├─ documents: Examples for each detection type
    ├─ references: ALGORITHM_COMPARISON_REPORT.md
    └─ documents: LLM integration (llm_error_cases, llm_correlation_input)

ALGORITHM_COMPARISON_REPORT.md (algorithm comparison)
    ├─ explains: Rule-based, Isolation Forest, Z-Score
    └─ references: llm_error_cases.json, llm_correlation_input.json

IDS_FINAL_SUMMARY.md (final deliverable)
    ├─ documents: Implementation status of all 8 teacher requests
    ├─ documents: Validation results
    ├─ documents: File list
    └─ documents: Deployment checklist
```

---

## Section 4: Quick Reference - "If Clemente Asks Where Feature X Is"

Fast lookup table for teacher inquiry.

| Feature | File | Location | Key Method/Class | Code Lines (approx) |
|---------|------|----------|------------------|-------------------|
| **Silent Device Detection** | ids/ids.py | State init + Per-message + Finalization | `__init__()`, `detect()`, `finalize()` | init:~20, detect:~190, finalize:~200 |
| **Patient ID Change Detection** | ids/ids.py | Per-message check | `detect()` | ~165-180 |
| **Replay Attack Detection** | ids/ids.py | Per-message fingerprinting | `detect()` | ~180-195 |
| **Programming Change Detection** | ids/ids.py | Per-message sliding window | `detect()` | ~216-235 |
| **Z-Score Anomaly Detection** | ids/ids.py | Algorithm + Per-message computation | `_compute_z_score()`, `Z_SCORE_CONFIG` | compute_z_score:~52-62, config:~30-35, invoke:~195-200 |
| **Data Injection Detection** | ids/ids.py | Per-message range check | `detect()` | ~130-160 |
| **Device Spoofing Detection** | ids/ids.py | Per-message known-device check | `detect()` | ~145-155 |
| **DoS Detection** | ids/ids.py | Per-message rate limiting | `detect()` | ~200-210 |
| **Isolation Forest Scoring** | ids/ids.py | Model training + scoring | `__init__()`, IF model invocation | Integrated in init (~280) |
| **End-of-File Alert Processing** | ids/detection_file.py | Main orchestrator | `__main__` | ~30-50 |
| **Dashboard Alert Format** | ids/alert_generator.py | Alert schema | `create_alert()` | Full file ~25-40 lines |
| **False Positive / FN Examples** | data/llm_error_cases.json | 9 cases with algorithm outputs | N/A (data file) | 9 JSON objects |
| **Multi-Event Correlation Input** | data/llm_correlation_input.json | Structured dataset + algorithm outputs | N/A (data file) | 12 messages + 6 algorithm outputs |
| **Algorithm Comparison** | ALGORITHM_COMPARISON_REPORT.md | Educational document | N/A (doc) | Sections 1-3 (compare methods), Section 4 (table), Section 5 (recommendation) |

---

## Section 5: Summary

### Overall Project Statistics

- **Total Files**: 20 (including .git, __pycache__, .gitignore)
- **Production Files**: 7 (core detection + pipeline + data input/output)
- **Documentation Files**: 8 (README, reports, summaries)
- **LLM Integration Files**: 3 (error cases, correlation input, algorithm report)
- **Configuration Files**: 2 (requirements.txt)
- **VCS/Cache**: 3 (.git, .gitignore, __pycache__)

### Essential Files for Demo

**Minimum viable demo** (3 files):
1. **ids/detection_file.py** — Show pipeline execution
2. **data/validated_data.json** — Show input
3. **data/alerts.json** — Show output

**Extended demo** (6 files):
- Add: ids/ids.py, ids/README.md, ALGORITHM_COMPARISON_REPORT.md

**Full demo** (all 20):
- Add: All LLM files, error cases, documentation

### Files Added Specifically After Teacher Feedback

**Core Detection Enhancements** (modified):
- ids/ids.py (added 4 new detections + Z-score + finalize method)
- ids/detection_file.py (added EOF processing)
- ids/README.md (added new detection documentation)
- data/validated_data.json (extended with test cases)

**New Files Created**:
1. ALGORITHM_COMPARISON_REPORT.md (algorithm education)
2. data/llm_error_cases.json (LLM training: 9 edge cases)
3. data/llm_correlation_input.json (LLM input: structured correlation data)
4. IDS_FINAL_SUMMARY.md (final deliverable summary)
5. **PROJECT_FILE_MAP.md** (this file)

**Not Modified**:
- ids/alert_generator.py (unchanged)
- ids/isolation_forest_model.py (unchanged, kept for reference)
- README.md (root, not modified)
- INTEGRATION_REPORT.md (pre-existing)
- PIPELINE_COMPATIBILITY_REPORT.md (pre-existing)

### Files for Student 4 / LLM Integration

**Input/Reference Files**:
1. **data/llm_error_cases.json** — 9 edge cases for confidence calibration
2. **data/llm_correlation_input.json** — Structured multi-event dataset with algorithm outputs
3. **ALGORITHM_COMPARISON_REPORT.md** — Algorithm knowledge base
4. **data/alerts.json** — Generated alerts to correlate

**Process**:
- LLM ingests `llm_error_cases.json` to learn FP/FN patterns
- LLM receives `llm_correlation_input.json` for multi-event analysis
- LLM references `ALGORITHM_COMPARISON_REPORT.md` for algorithm trade-offs
- LLM consumes alerts from `alerts.json` for dashboard/incident response

### Teacher-Requested Feature Implementation Summary

| Feature | Status | File(s) | Lines of Code | LLM Support |
|---------|--------|---------|---------------|-------------|
| Silent Device Detection | ✓ Complete | ids/ids.py | ~50 | llm_correlation_input.json |
| Patient ID Change Detection | ✓ Complete | ids/ids.py | ~20 | llm_correlation_input.json |
| Replay Attack Detection | ✓ Complete | ids/ids.py | ~20 | llm_error_cases.json (FN-003) |
| Programming Change Detection | ✓ Complete | ids/ids.py | ~25 | llm_correlation_input.json |
| Z-Score Algorithm | ✓ Complete | ids/ids.py | ~35 | llm_error_cases.json (multiple), llm_correlation_input.json |
| Algorithm Comparison | ✓ Complete | ALGORITHM_COMPARISON_REPORT.md | ~400 | Reference for LLM |
| FP/FN Examples | ✓ Complete | data/llm_error_cases.json | 9 cases | Direct LLM input |
| LLM Correlation Input | ✓ Complete | data/llm_correlation_input.json | ~500 | Direct LLM input |

---

## Quick Answer Cheat Sheet

**If Clemente asks:** "Where is the Silent Device detection?"
**Answer:** "ids/ids.py, methods `finalize()` and `detect()` which track `last_seen` timestamps. Called from `detection_file.py` after all messages are processed."

**If Clemente asks:** "Where can I see false positive examples?"
**Answer:** "data/llm_error_cases.json has 3 FP cases: FP-001 (low resting heart rate), FP-002 (early morning temperature), FP-003 (high oxygen saturation). Shows algorithm outputs and explanations."

**If Clemente asks:** "What is Z-score and where is it?"
**Answer:** "ids/ids.py, method `_compute_z_score()`. Lightweight anomaly detection using mean/std per device type. Computed for all measurements but doesn't override rule-based decisions. Reference parameters in `Z_SCORE_CONFIG`. Used for LLM analysis via `llm_correlation_input.json` and `llm_error_cases.json`."

**If Clemente asks:** "How do the three algorithms compare?"
**Answer:** "ALGORITHM_COMPARISON_REPORT.md compares Rule-Based, Isolation Forest, and Z-Score. Explains trade-offs: Rule-Based is safe but rigid; IF is sensitive but opaque; Z-Score is fast and explainable. Recommends hybrid: Rule-Based as gate + Z-Score for baseline + IF for enhancement."

**If Clemente asks:** "Is the pipeline still file-based?"
**Answer:** "Yes. data/validated_data.json → python ids/detection_file.py → data/alerts.json. Same format, same contract. All teacher requests implemented without breaking the integration."

**If Clemente asks:** "How does the LLM system integrate?"
**Answer:** "Via three data files: llm_error_cases.json (9 edge cases for calibration), llm_correlation_input.json (12 messages + algorithm outputs for multi-event analysis), and ALGORITHM_COMPARISON_REPORT.md (algorithm knowledge). IDS generates alerts; LLM adds correlation and contextual reasoning."

**If Clemente asks:** "Which files were added for teacher feedback?"
**Answer:** "Core additions: Silent Device, Patient ID Change, Replay Attack, Programming Change, Z-Score (all in ids.py). New files: ALGORITHM_COMPARISON_REPORT.md, llm_error_cases.json, llm_correlation_input.json, IDS_FINAL_SUMMARY.md, PROJECT_FILE_MAP.md (this)."

---

## End of Project File Map

Generated: 2026-06-17
For: Teacher review and presentation
Maintained by: Ilyas (secure-iomt-platform team)
