import json
from pathlib import Path
from ids import IDS

sample = json.loads(Path('sample_data_large.json').read_text(encoding='utf-8'))
ids = IDS()
for msg in sample:
    alert = ids.detect(msg)
    if alert and alert['alert_type'] == 'Anomaly':
        print('MESSAGE:')
        print(json.dumps(msg, indent=2))
        print('\nALERT:')
        print(json.dumps(alert, indent=2))
        break
else:
    print('No Anomaly alerts found')
