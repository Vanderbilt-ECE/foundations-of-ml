"""Reproduce the deck's illustrative fraud example.

Run: python3 examples/threshold_demo.py
Dependencies: numpy, scikit-learn
These are invented validation scores, not a real trained fraud model.
"""
import json
from pathlib import Path

import numpy as np
from sklearn.metrics import (
    average_precision_score, confusion_matrix, f1_score,
    precision_score, recall_score, roc_auc_score,
)

bins = json.loads(Path(__file__).with_name('fraud-data.json').read_text())
y_val = np.concatenate([
    np.r_[np.ones(b['positive'], dtype=int), np.zeros(b['negative'], dtype=int)]
    for b in bins
])
s_val = np.concatenate([
    np.full(b['positive'] + b['negative'], b['score']) for b in bins
])

print('Illustrative validation cohort: 100 fraud, 900 legitimate transactions')
print('Rows: actual [legitimate, fraud]; columns: predicted [legitimate, fraud]')
print(' threshold   TN  FP  FN  TP  alerts  precision  recall     F1  cost(5,100)  cost(100,20)')
for threshold in [0.80, 0.50, 0.20]:
    pred_val = (s_val >= threshold).astype(int)
    tn, fp, fn, tp = confusion_matrix(y_val, pred_val, labels=[0, 1]).ravel()
    precision = precision_score(y_val, pred_val, zero_division=0)
    recall = recall_score(y_val, pred_val, zero_division=0)
    f1 = f1_score(y_val, pred_val, zero_division=0)
    print(f'{threshold:10.2f} {tn:4d} {fp:3d} {fn:3d} {tp:3d} {tp+fp:7d}'
          f' {precision:10.3f} {recall:7.3f} {f1:6.3f}'
          f' {5*fp+100*fn:12d} {100*fp+20*fn:13d}')

# Ranking metrics take scores, not the thresholded predictions.
print(f'ROC-AUC: {roc_auc_score(y_val, s_val):.6f}')
print(f'Average precision: {average_precision_score(y_val, s_val):.6f}')

# A complete threshold search for the simplified low-friction review cost.
# 1.01 permits no positive predictions; unique scores cover all other outcomes.
candidates = np.r_[1.01, np.unique(s_val)]
results = []
for threshold in candidates:
    tn, fp, fn, tp = confusion_matrix(
        y_val, (s_val >= threshold).astype(int), labels=[0, 1]
    ).ravel()
    results.append((5*fp + 100*fn, threshold, tp+fp, tp/100))
best_cost, chosen_threshold, alerts, recall = min(results)
print(f'Full search for FP=$5, FN=$100: choose t={chosen_threshold:.2f}, '
      f'cost=${best_cost:,}, alerts={alerts}, recall={recall:.1%}')
print('Freeze the threshold before evaluating on an independent test set.')
