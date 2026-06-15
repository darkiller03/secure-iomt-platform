import json
from pathlib import Path
from isolation_forest_model import IsolationForestModel

threshold = 0.45
m = IsolationForestModel()
m.train()
results = []
for msg in json.loads(Path('sample_data_large.json').read_text(encoding='utf-8')):
    hr = msg.get('heart_rate')
    if hr is not None and 40 <= hr <= 180:
        score = m.score(hr)
        if score > threshold:
            results.append((hr, score, msg['expected_label'], msg.get('patient_id'), msg.get('timestamp')))
print('threshold', threshold, 'count', len(results))
for item in results[:50]:
    print(item)
