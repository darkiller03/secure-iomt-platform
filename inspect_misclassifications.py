import json
from pathlib import Path

preds = json.loads(Path('predictions.json').read_text(encoding='utf-8'))
for i, p in enumerate(preds, 1):
    if p['expected_label'] == 'attack' and p['predicted_label'] == 'normal':
        print(i, p)
