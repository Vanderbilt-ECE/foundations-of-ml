# Classifier Explorer

An interactive browser tool for exploring how a fraud classifier's threshold, error costs and
model complexity interact, using polynomial logistic regression on the credit-card fraud dataset.

## Run it

```bash
uv run app.py            # then open http://127.0.0.1:5050
uv run app.py --port 8000
```

The server expects the data at `../creditcard.csv` (the Kaggle "Credit Card Fraud Detection"
dataset: 284,807 transactions, 492 frauds). The file is 151 MB, so it is gitignored and not
committed; download it and place it in `Model Evaluation/assignments/`.

## What you can do

1. **Model** – choose the polynomial degree (1–6) and how many features get expanded (top-k by
   |correlation| with fraud, ranked on training data only). Click **Fit model**, or **Sweep all
   degrees** to fill in the model-complexity chart.
2. **Threshold** – move the slider (linear or log scale). A lower threshold flags more
   transactions: more fraud caught, more false alarms.
3. **Costs** – enter a cost for TN, FP, FN and TP (negative = benefit). The cost-vs-threshold
   chart marks the minimum, and **Jump to minimum** moves the slider there.
4. **Read the panels** – confusion matrix and metrics, cost curve, ROC (with optional log FPR
   axis) and precision–recall curves with the current operating point, and train-vs-test
   PR-AUC and log-loss against degree.

## How it works

- One stratified 70/30 train/test split. The test set (85,443 rows) keeps the natural fraud rate,
  because precision and cost both depend on it.
- Training uses every training fraud plus a random 30,000 non-frauds, to keep fits to a few
  seconds. After fitting, the intercept is shifted by `log(r)` (r = non-fraud sampling rate) so the
  predicted probabilities match the real fraud rate.
- Pipeline: `StandardScaler → PolynomialFeatures → StandardScaler → LogisticRegression`.
- The server sends TP/FP/TN/FN counts on a grid of ~1,600 thresholds; the slider and cost boxes are
  recomputed in the browser, so they respond instantly.

**Leakage caveat:** the threshold is chosen on the same test set it is evaluated on. In a real
project, tune it on a validation split.
