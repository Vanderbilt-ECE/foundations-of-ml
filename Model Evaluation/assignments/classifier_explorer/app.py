"""Classifier Explorer: thresholds, costs, ROC and PR curves on credit-card fraud.

Run this file with:

    uv run app.py

then open http://127.0.0.1:5050 in a browser.

The server does the machine learning once per model setting:

1. Load the credit-card data and make one stratified train/test split.
2. Fit a polynomial logistic regression of the chosen degree.
3. Score the untouched test set and summarise it as ROC and PR curves plus
   confusion-matrix counts over a grid of thresholds.

Everything the slider and the cost boxes change is recomputed in the browser
from those counts, so moving the threshold never needs another model fit.
"""

import argparse
import time
import warnings
from math import comb
from pathlib import Path

import numpy as np
import pandas as pd
from flask import Flask, jsonify, request, send_from_directory
from sklearn.exceptions import ConvergenceWarning
from sklearn.linear_model import LogisticRegression
from sklearn.metrics import (
    average_precision_score,
    log_loss,
    precision_recall_curve,
    roc_auc_score,
    roc_curve,
)
from sklearn.model_selection import train_test_split
from sklearn.pipeline import make_pipeline
from sklearn.preprocessing import PolynomialFeatures, StandardScaler

DATA_PATH = Path(__file__).resolve().parent.parent / "creditcard.csv"
STATIC_DIR = Path(__file__).resolve().parent / "static"

RANDOM_STATE = 0
TEST_FRACTION = 0.3
TRAIN_LEGIT_SAMPLES = 30_000  # non-fraud rows kept for training (all frauds are kept)

MAX_DEGREE = 6
MIN_K, MAX_K, DEFAULT_K = 2, 29, 8
MAX_EXPANDED_FEATURES = 3_500  # keeps each fit to a few seconds


# ---------------------------------------------------------------------
# Data: one split, made once when the server starts.
# ---------------------------------------------------------------------

def load_data():
    """Load the CSV and return (train, test) pieces plus the training weights.

    - `Time` is dropped (seconds since the first transaction is not a useful
      signal for a single model) and `Amount` is log-transformed because it is
      very skewed.
    - The test set keeps the natural fraud rate (~0.17%). Precision and cost
      both depend on that rate, so the test set is never resampled.
    - The training set keeps every fraud but only a random sample of the
      non-fraud rows, which makes fitting fast. Each kept non-fraud row stands
      in for 1 / r original rows, where r is the sampling rate.
    """
    df = pd.read_csv(DATA_PATH)
    df["Amount"] = np.log1p(df["Amount"])
    y = df.pop("Class").astype(int).to_numpy()
    X = df.drop(columns=["Time"])

    X_train, X_test, y_train, y_test = train_test_split(
        X, y, test_size=TEST_FRACTION, stratify=y, random_state=RANDOM_STATE
    )

    # Rank features using the training split only, so the test set cannot
    # influence which features the model gets to see.
    correlations = X_train.corrwith(pd.Series(y_train, index=X_train.index)).abs()
    ranked_features = correlations.sort_values(ascending=False).index.tolist()

    rng = np.random.default_rng(RANDOM_STATE)
    fraud_rows = np.flatnonzero(y_train == 1)
    legit_rows = np.flatnonzero(y_train == 0)
    n_legit = min(TRAIN_LEGIT_SAMPLES, len(legit_rows))
    kept_legit = rng.choice(legit_rows, size=n_legit, replace=False)
    sampling_rate = n_legit / len(legit_rows)

    keep = np.concatenate([fraud_rows, kept_legit])
    X_fit = X_train.iloc[keep]
    y_fit = y_train[keep]

    # Weights that undo the sampling when we *measure* training performance,
    # so train and test metrics are on the same (natural) fraud rate.
    weights_fit = np.where(y_fit == 1, 1.0, 1.0 / sampling_rate)

    return {
        "X_fit": X_fit,
        "y_fit": y_fit,
        "weights_fit": weights_fit,
        "X_test": X_test,
        "y_test": y_test,
        "ranked_features": ranked_features,
        "sampling_rate": sampling_rate,
        "n_train_fraud": len(fraud_rows),
        "n_train_legit_total": len(legit_rows),
    }


def expanded_feature_count(k, degree):
    """Number of columns PolynomialFeatures makes from k inputs (no bias)."""
    return comb(k + degree, degree) - 1


# ---------------------------------------------------------------------
# Model: polynomial logistic regression with a prior correction.
# ---------------------------------------------------------------------

def fit_model(data, degree, k):
    """Fit the pipeline and return (model, feature names, warning messages).

    The second StandardScaler rescales the polynomial columns (x^5 has a very
    different range from x), which helps the optimiser converge.
    """
    features = data["ranked_features"][:k]
    model = make_pipeline(
        StandardScaler(),
        PolynomialFeatures(degree=degree, include_bias=False),
        StandardScaler(),
        LogisticRegression(max_iter=2000),
    )

    with warnings.catch_warnings(record=True) as caught:
        warnings.simplefilter("always", ConvergenceWarning)
        model.fit(data["X_fit"][features], data["y_fit"])
    messages = sorted({str(w.message).split("\n")[0] for w in caught})

    # Prior correction: the model was trained on data with far more fraud than
    # reality, so its log-odds are too high by log(1 / r). Shifting the
    # intercept by log(r) puts the probabilities back on the natural fraud rate.
    model[-1].intercept_ += np.log(data["sampling_rate"])

    return model, features, messages


# ---------------------------------------------------------------------
# Evaluation: everything the browser needs to draw its panels.
# ---------------------------------------------------------------------

def threshold_grid(fraud_scores):
    """Thresholds for the slider: a linear 0..1 grid plus a log-spaced grid.

    Most fraud probabilities are close to 0, so a linear grid alone would put
    almost every interesting threshold in its first few steps.

    The fraud cases' own scores are added too. The total cost only changes
    when the threshold crosses a score, and (for sensible costs) it can only
    reach a minimum right at a fraud score, so this makes the minimum exact.
    """
    linear = np.round(np.linspace(0, 1, 1001), 3)
    logarithmic = 10 ** np.round(np.arange(-6, 0.001, 0.01), 2)
    return np.unique(np.concatenate([linear, logarithmic, fraud_scores]))


def counts_at_thresholds(y, scores, thresholds):
    """TP, FP, TN, FN when we flag fraud for every score >= threshold."""
    fraud_scores = np.sort(scores[y == 1])
    legit_scores = np.sort(scores[y == 0])

    # searchsorted counts how many scores fall below each threshold.
    fn = np.searchsorted(fraud_scores, thresholds, side="left")
    tn = np.searchsorted(legit_scores, thresholds, side="left")
    tp = len(fraud_scores) - fn
    fp = len(legit_scores) - tn
    return tp, fp, tn, fn


def thin(*arrays, max_points=4000):
    """Keep at most `max_points` evenly spaced points (always keeping the ends)."""
    n = len(arrays[0])
    if n <= max_points:
        return [a.tolist() for a in arrays]
    idx = np.unique(np.linspace(0, n - 1, max_points).astype(int))
    return [a[idx].tolist() for a in arrays]


def complexity_metrics(model, data, features):
    """Train vs test log-loss, PR-AUC and ROC-AUC for the model-complexity plot."""
    p_fit = model.predict_proba(data["X_fit"][features])[:, 1]
    p_test = model.predict_proba(data["X_test"][features])[:, 1]
    y_fit, y_test, w = data["y_fit"], data["y_test"], data["weights_fit"]
    return {
        "train_logloss": log_loss(y_fit, p_fit, sample_weight=w),
        "test_logloss": log_loss(y_test, p_test),
        "train_ap": average_precision_score(y_fit, p_fit, sample_weight=w),
        "test_ap": average_precision_score(y_test, p_test),
        "train_auc": roc_auc_score(y_fit, p_fit, sample_weight=w),
        "test_auc": roc_auc_score(y_test, p_test),
    }


def evaluate(data, degree, k):
    """Fit one model and summarise its test-set behaviour."""
    start = time.perf_counter()
    model, features, messages = fit_model(data, degree, k)
    fit_seconds = time.perf_counter() - start

    y_test = data["y_test"]
    scores = model.predict_proba(data["X_test"][features])[:, 1]

    fpr, tpr, _ = roc_curve(y_test, scores)
    precision, recall, _ = precision_recall_curve(y_test, scores, drop_intermediate=True)
    thresholds = threshold_grid(scores[y_test == 1])
    tp, fp, tn, fn = counts_at_thresholds(y_test, scores, thresholds)
    fpr, tpr = thin(fpr, tpr)
    precision, recall = thin(precision, recall)

    return {
        "degree": degree,
        "k": k,
        "features_used": features,
        "n_features_expanded": expanded_feature_count(k, degree),
        "fit_seconds": round(fit_seconds, 2),
        "warnings": messages,
        "n_test": int(len(y_test)),
        "n_test_fraud": int(y_test.sum()),
        "prevalence_test": float(y_test.mean()),
        "roc": {"fpr": fpr, "tpr": tpr},
        "roc_auc": float(roc_auc_score(y_test, scores)),
        "pr": {"precision": precision, "recall": recall},
        "average_precision": float(average_precision_score(y_test, scores)),
        "grid": {
            "thresholds": thresholds.tolist(),
            "tp": tp.tolist(),
            "fp": fp.tolist(),
            "tn": tn.tolist(),
            "fn": fn.tolist(),
        },
        "complexity": complexity_metrics(model, data, features),
    }


# ---------------------------------------------------------------------
# Web server
# ---------------------------------------------------------------------

app = Flask(__name__, static_folder=str(STATIC_DIR), static_url_path="/static")
DATA = None
CACHE = {}  # (degree, k) -> result dict, so revisiting a setting is instant


def validate(degree, k):
    """Return an error message, or None if (degree, k) can be fitted."""
    if not 1 <= degree <= MAX_DEGREE:
        return f"Degree must be between 1 and {MAX_DEGREE}."
    if not MIN_K <= k <= MAX_K:
        return f"Number of features must be between {MIN_K} and {MAX_K}."
    n = expanded_feature_count(k, degree)
    if n > MAX_EXPANDED_FEATURES:
        return (
            f"Degree {degree} with {k} features makes {n:,} polynomial columns "
            f"(limit {MAX_EXPANDED_FEATURES:,}). Lower the degree or the number of features."
        )
    return None


def get_result(degree, k):
    key = (degree, k)
    if key not in CACHE:
        CACHE[key] = evaluate(DATA, degree, k)
    return CACHE[key]


@app.get("/")
def index():
    return send_from_directory(STATIC_DIR, "index.html")


@app.get("/api/config")
def config():
    return jsonify(
        {
            "max_degree": MAX_DEGREE,
            "min_k": MIN_K,
            "max_k": MAX_K,
            "default_k": DEFAULT_K,
            "max_expanded_features": MAX_EXPANDED_FEATURES,
            "ranked_features": DATA["ranked_features"],
            "n_fit": int(len(DATA["y_fit"])),
            "n_train_fraud": DATA["n_train_fraud"],
            "n_train_legit_total": DATA["n_train_legit_total"],
            "sampling_rate": DATA["sampling_rate"],
        }
    )


@app.post("/api/fit")
def fit():
    body = request.get_json(force=True)
    degree, k = int(body.get("degree", 1)), int(body.get("k", DEFAULT_K))
    error = validate(degree, k)
    if error:
        return jsonify({"error": error}), 400
    return jsonify(get_result(degree, k))


@app.post("/api/sweep")
def sweep():
    """Fit every allowed degree for one k and return the complexity metrics."""
    body = request.get_json(force=True)
    k = int(body.get("k", DEFAULT_K))
    points, skipped = [], []
    for degree in range(1, MAX_DEGREE + 1):
        if validate(degree, k):
            skipped.append(degree)
            continue
        result = get_result(degree, k)
        points.append({"degree": degree, **result["complexity"]})
    return jsonify({"k": k, "points": points, "skipped": skipped})


def main():
    global DATA
    parser = argparse.ArgumentParser(description=__doc__.split("\n")[0])
    parser.add_argument("--port", type=int, default=5050)
    args = parser.parse_args()

    print(f"Loading {DATA_PATH.name} ...")
    DATA = load_data()
    print(
        f"Training on {len(DATA['y_fit']):,} rows "
        f"({DATA['n_train_fraud']} frauds, non-fraud sampling rate {DATA['sampling_rate']:.3f}); "
        f"testing on {len(DATA['y_test']):,} rows."
    )
    print(f"Open http://127.0.0.1:{args.port}")
    app.run(host="127.0.0.1", port=args.port, debug=False, threaded=True)


if __name__ == "__main__":
    main()
