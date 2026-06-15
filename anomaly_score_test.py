import numpy as np
from isolation_forest_model import IsolationForestModel

for factor in [5, 10, 15, 20, 30, 50]:
    m = IsolationForestModel()
    m.train()
    print('factor', factor)
    for hr in [45, 50, 55, 60, 80, 100, 120, 140]:
        x = np.array([[hr]])
        df = m.model.decision_function(x)[0]
        score = 1.0/(1.0+np.exp(factor*df))
        print(hr, df, round(score,4))
    print()