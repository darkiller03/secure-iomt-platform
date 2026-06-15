import json
from pathlib import Path
from isolation_forest_model import IsolationForestModel

for factor in [20, 30]:
    for threshold in [0.5, 0.55, 0.6]:
        m = IsolationForestModel()
        m.train()
        bad = 0
        good = 0
        for msg in json.loads(Path('sample_data_large.json').read_text(encoding='utf-8')):
            hr = msg.get('heart_rate')
            if hr is not None and 40 <= hr <= 180:
                df = m.model.decision_function([[hr]])[0]
                score = 1.0 / (1.0 + __import__('numpy').exp(factor * df))
                if score > threshold:
                    if msg['expected_label'] == 'normal':
                        bad += 1
                    else:
                        good += 1
        print('factor', factor, 'threshold', threshold, 'bad', bad, 'good', good)
