"""Reference solution: Cross-Validation and Honest Model Selection, From Scratch.

One script, run with:  uv run solution.py

Organised into the same five parts as the assignment. The split logic, the
k-fold logic and `cross_val_score` are all written out with numpy. scikit-learn
is used only for the ridge/linear *models* and for the planted-leak preprocessing
objects in Part 3.

    Part 1 - one random split is noisy
    Part 2 - k-fold from scratch; what actually stabilises; the U-curve
    Part 3 - the leakage lab (3 planted leaks)
    Part 4 - the split must match the data (grouped, time-ordered)
    Part 5 - the full model-selection workflow, and the peeking failure mode
"""

import numpy as np
import plotly.graph_objects as go
from sklearn.feature_selection import SelectKBest, f_regression
from sklearn.preprocessing import StandardScaler


# ---------------------------------------------------------------------
# Shared helpers: a 1-D polynomial-ridge model, written functionally.
# A "fitted model" here is just a function that maps new x -> predictions.
# ---------------------------------------------------------------------

def poly_features(x, degree):
    """Design matrix with columns x^0, x^1, ..., x^degree."""
    return np.vander(np.asarray(x, float), degree + 1, increasing=True)


def fit_poly_ridge(x, y, degree, alpha=0.0):
    """Closed-form ridge regression on polynomial features.

    Returns a `predict(x_new)` function. The intercept column (index 0) is not
    penalised, which is the usual convention.
    """
    X = poly_features(x, degree)
    penalty = alpha * np.eye(X.shape[1])
    penalty[0, 0] = 0.0
    beta = np.linalg.solve(X.T @ X + penalty, X.T @ y)
    return lambda x_new: poly_features(x_new, degree) @ beta


def mse(y_true, y_pred):
    return float(np.mean((np.asarray(y_true) - np.asarray(y_pred)) ** 2))


def make_sine_data(n, seed):
    """y = sin(1.5 pi x) + noise, x uniform on [0, 1]. Same truth as the
    Bias-Variance deck, so the U-curve in Part 2 should look familiar."""
    rng = np.random.default_rng(seed)
    x = rng.uniform(0, 1, n)
    y = np.sin(1.5 * np.pi * x) + rng.normal(scale=0.20, size=n)
    return x, y


# =====================================================================
# Part 1 - one random split is noisy
# =====================================================================

def train_test_split(x, y, test_frac, seed):
    """Shuffle the row indices, then slice off the last `test_frac` as test."""
    rng = np.random.default_rng(seed)
    idx = rng.permutation(len(x))
    cut = int(round(len(x) * (1 - test_frac)))
    tr, te = idx[:cut], idx[cut:]
    return x[tr], x[te], y[tr], y[te]


x1, y1 = make_sine_data(n=100, seed=0)

# One fixed model (degree-4 polynomial). Only the random split changes.
split_errors = []
for seed in range(200):
    x_tr, x_te, y_tr, y_te = train_test_split(x1, y1, test_frac=0.25, seed=seed)
    predict = fit_poly_ridge(x_tr, y_tr, degree=4, alpha=0.0)
    split_errors.append(mse(y_te, predict(x_te)))
split_errors = np.array(split_errors)

print("=" * 64)
print("Part 1 - one random split is noisy (degree-4 poly, 200 random splits)")
print("=" * 64)
print(f"  held-out MSE  mean = {split_errors.mean():.4f}"
      f"   std = {split_errors.std():.4f}"
      f"   min = {split_errors.min():.4f}   max = {split_errors.max():.4f}")
print(f"  the std is {split_errors.std() / split_errors.mean():.0%} of the mean"
      f" - same model, same data, only the split seed changed.")

fig1 = go.Figure()
fig1.add_histogram(x=split_errors, nbinsx=30, marker_color="#60a5fa")
fig1.add_vline(x=split_errors.mean(), line_color="#f59e0b",
               annotation_text="mean")
fig1.update_layout(title="Part 1: 200 held-out MSE scores for ONE model on ONE dataset",
                   xaxis_title="held-out MSE", yaxis_title="count",
                   template="plotly_white")
fig1.write_html("part1_split_histogram.html")
print("  wrote part1_split_histogram.html")


# =====================================================================
# Part 2 - k-fold cross-validation from scratch
# =====================================================================

def kfold_indices(n, k, seed=0):
    """Return k disjoint index arrays whose union is 0..n-1."""
    rng = np.random.default_rng(seed)
    return np.array_split(rng.permutation(n), k)


def cross_val_score(fit_fn, x, y, k, seed=0):
    """Fit k times, each time holding out one fold. Return the k fold MSEs.

    `fit_fn(x_train, y_train)` must return a `predict(x)` function.
    """
    folds = kfold_indices(len(x), k, seed)
    errors = []
    for i in range(k):
        val_idx = folds[i]
        train_idx = np.concatenate([folds[j] for j in range(k) if j != i])
        predict = fit_fn(x[train_idx], y[train_idx])
        errors.append(mse(y[val_idx], predict(x[val_idx])))
    return np.array(errors)


print()
print("=" * 64)
print("Part 2 - k-fold cross-validation")
print("=" * 64)

# --- worked example: k = 5, ridge, degree 4 --------------------------------
ridge4 = lambda xt, yt: fit_poly_ridge(xt, yt, degree=4, alpha=1.0)
fold_errs = cross_val_score(ridge4, x1, y1, k=5, seed=0)
print("  k = 5 fold errors:", np.round(fold_errs, 4).tolist())
print(f"  CV error (their average) = {fold_errs.mean():.4f}")

# --- what actually stabilises as k grows ----------------------------------
# For each k: repeat the WHOLE k-fold procedure for 100 different shuffles,
# record the CV mean each time. std(CV means) is the variance of the CV
# ESTIMATE - that is what shrinks. The spread across folds moves the other way.
n = len(x1)
print()
print(f"  {'k':>4}  {'std(CV means)':>14}  {'avg fold-to-fold std':>22}")
ks = [2, 5, 10, n]
std_of_means, fold_spread = [], []
for k in ks:
    cv_means, within = [], []
    for rep in range(100):
        errs = cross_val_score(ridge4, x1, y1, k=k, seed=1000 + rep)
        cv_means.append(errs.mean())
        within.append(errs.std())
    std_of_means.append(np.std(cv_means))
    fold_spread.append(np.mean(within))
    print(f"  {k:>4}  {np.std(cv_means):>14.5f}  {np.mean(within):>22.5f}")
print("  -> std(CV means) DECREASES with k (averaging more folds stabilises the")
print("     estimate); at k = n (leave-one-out) it is exactly 0 because the")
print("     partition is no longer random - every point is its own fold.")
print("     The fold-to-fold spread INCREASES with k because each fold gets")
print("     smaller and noisier; at k = n each 'fold error' is a single")
print("     squared residual. Spread is a diagnostic, not the thing we minimise.")

fig2 = go.Figure()
fig2.add_scatter(x=ks, y=std_of_means, mode="lines+markers",
                 name="std(CV means) across partitions", line=dict(color="#2dd4bf"))
fig2.add_scatter(x=ks, y=fold_spread, mode="lines+markers",
                 name="avg spread across folds", line=dict(color="#f59e0b"))
fig2.update_layout(title="Part 2: what k-fold stabilises (teal) vs what it does not (orange)",
                   xaxis_title="k (number of folds)", yaxis_title="std of MSE",
                   template="plotly_white")
fig2.write_html("part2_stability_vs_k.html")
print("  wrote part2_stability_vs_k.html")

# --- bias-variance callback: CV error vs polynomial degree ---------------
degrees = list(range(1, 13))
cv_by_degree = [cross_val_score(
    (lambda xt, yt, d=d: fit_poly_ridge(xt, yt, degree=d, alpha=0.0)),
    x1, y1, k=5, seed=0).mean() for d in degrees]
best_degree = degrees[int(np.argmin(cv_by_degree))]
print()
print("  5-fold CV error by polynomial degree:")
for d, e in zip(degrees, cv_by_degree):
    mark = "  <- min" if d == best_degree else ""
    print(f"    degree {d:>2}   CV MSE = {e:.4f}{mark}")
print("  U-shaped: underfitting on the left, overfitting on the right.")

fig3 = go.Figure()
fig3.add_scatter(x=degrees, y=cv_by_degree, mode="lines+markers",
                 line=dict(color="#60a5fa"))
fig3.add_vline(x=best_degree, line_dash="dot", line_color="#f59e0b",
               annotation_text=f"best = {best_degree}")
fig3.update_layout(title="Part 2: 5-fold CV error vs polynomial degree (U-shaped)",
                   xaxis_title="polynomial degree", yaxis_title="5-fold CV error",
                   yaxis_type="log", template="plotly_white")
fig3.write_html("part2_cv_ucurve.html")
print("  wrote part2_cv_ucurve.html")


# =====================================================================
# Part 3 - the leakage lab
# =====================================================================
# Dataset: 5 real features + 300 pure-noise features, n = 120. One noise
# column has 30% of its values missing.

def make_leaky_dataset(seed=0):
    """Returns two versions of the same feature matrix:

    X_nan          - the leak column still has np.nan where values were missing
    X_target_fill  - someone 'filled' those NaNs with the target y (the bug)

    There are only 4 real features and 400 pure-noise columns, so a feature
    selector that peeks at the whole dataset can find noise columns that
    correlate with y by chance.
    """
    rng = np.random.default_rng(seed)
    n, n_real, n_noise = 120, 4, 400
    X_real = rng.normal(size=(n, n_real))
    beta = rng.normal(size=n_real)
    y = 0.6 * (X_real @ beta) + rng.normal(scale=0.5, size=n)   # modest signal
    X = np.c_[X_real, rng.normal(size=(n, n_noise))]

    leak_col = n_real                       # first noise column
    missing = rng.random(n) < 0.55          # 55% of this column is missing
    X_nan = X.copy()
    X_nan[missing, leak_col] = np.nan
    X_target_fill = X.copy()
    X_target_fill[missing, leak_col] = y[missing]               # filled straight from y
    return X_nan, X_target_fill, y, leak_col


X_nan, X_target_fill, y, leak_col = make_leaky_dataset()
N_SELECT = 15                              # how many features SelectKBest keeps


def linreg_fit(Xtr, ytr):
    """Plain least-squares. Returns predict(X)."""
    Xtr1 = np.c_[np.ones(len(Xtr)), Xtr]
    beta, *_ = np.linalg.lstsq(Xtr1, ytr, rcond=None)
    return lambda Xn: np.c_[np.ones(len(Xn)), Xn] @ beta


def cv_score_matrix(fit_fn, X, y, k=5, seed=0):
    """Same idea as cross_val_score but for an (n, p) feature matrix."""
    folds = kfold_indices(len(X), k, seed)
    errs = []
    for i in range(k):
        va = folds[i]
        tr = np.concatenate([folds[j] for j in range(k) if j != i])
        predict = fit_fn(X[tr], y[tr])
        errs.append(mse(y[va], predict(X[va])))
    return float(np.mean(errs))


print()
print("=" * 64)
print("Part 3 - the leakage lab (a lower CV MSE here means we are FOOLING ourselves)")
print("=" * 64)

# A preprocessing step is either fit ONCE on the whole dataset ("global",
# leaky) or refit on each training fold ("per-fold", honest). We build the
# pipeline as a fit_fn so cross_val_score can drive it.

def make_pipeline_fit(global_scaler=None, global_selector=None, impute_from="mean"):
    """Return a fit_fn(Xtr, ytr) -> predict.

    global_scaler / global_selector : if given, these were fit on the full
        dataset (the leak). If None, a fresh one is fit on the training fold.
    impute_from : 'mean'  -> fill NaNs with the training-fold column mean (safe)
                  'data'  -> the NaNs are already filled with y in the matrix
                             (target leak; nothing to do here, and CV hygiene
                             cannot undo it)
    """
    def fit_fn(Xtr, ytr):
        fill_val = np.nan_to_num(np.nanmean(Xtr[:, leak_col])) if impute_from == "mean" else 0.0
        fill = lambda M: np.where(np.isnan(M), fill_val, M)

        scaler = global_scaler or StandardScaler().fit(fill(Xtr))
        Xs = scaler.transform(fill(Xtr))
        selector = global_selector or SelectKBest(f_regression, k=N_SELECT).fit(Xs, ytr)
        base = linreg_fit(selector.transform(Xs), ytr)
        return lambda Xn: base(selector.transform(scaler.transform(fill(Xn))))
    return fit_fn


# pre-fit the "global" (leaky) transformers on the entire dataset
g_scaler = StandardScaler().fit(np.nan_to_num(X_target_fill))
g_selector = SelectKBest(f_regression, k=N_SELECT).fit(
    g_scaler.transform(np.nan_to_num(X_target_fill)), y)

rows = [
    ("no leaks (all per-fold, NaNs imputed by train mean)",
     cv_score_matrix(make_pipeline_fit(impute_from="mean"), X_nan, y)),
    ("+ target-derived imputation baked into the data",
     cv_score_matrix(make_pipeline_fit(impute_from="data"), X_target_fill, y)),
    ("+ feature selector fit on the whole dataset",
     cv_score_matrix(make_pipeline_fit(global_selector=g_selector, impute_from="data"),
                     X_target_fill, y)),
    ("+ scaler fit on the whole dataset (all 3 leaks)",
     cv_score_matrix(make_pipeline_fit(global_scaler=g_scaler, global_selector=g_selector,
                                       impute_from="data"), X_target_fill, y)),
]
for label, score in rows:
    print(f"  {label:<52} CV MSE = {score:.4f}")

print()
print("  Reading it:")
print("   - target-derived imputation is the big one, and note that refitting")
print("     the pipeline per fold does NOT save you: y is literally sitting in")
print("     the feature values, so the leak is in the DATA, not the procedure.")
print("   - selecting features on the whole dataset helps a bit more: with 400")
print("     noise columns the selector finds some that match y on the val rows.")
print("   - the global scaler barely moves the number - but it is still wrong:")
print("     in deployment there are no future rows to get the mean/std from.")

fig4 = go.Figure()
fig4.add_bar(x=[r[0].replace("+ ", "") for r in rows], y=[r[1] for r in rows],
             marker_color=["#2dd4bf", "#fbbf24", "#fb923c", "#f87171"])
fig4.update_layout(title="Part 3: each added leak lowers the CV MSE we would have reported",
                   yaxis_title="5-fold CV MSE", template="plotly_white",
                   xaxis_tickangle=-15)
fig4.write_html("part3_leakage.html")
print("  wrote part3_leakage.html")


# =====================================================================
# Part 4 - the split must match the data
# =====================================================================
print()
print("=" * 64)
print("Part 4 - the split must match the data")
print("=" * 64)

# ---- grouped data: 20 patients, 6 rows each -------------------------------
# Each patient has a random "baseline" (a per-patient intercept) that is NOT a
# simple function of the features. One feature, x_id, effectively reveals which
# patient a row came from. A flexible model (here: k-nearest-neighbours) can
# therefore memorise "this patient -> this baseline" whenever it has seen ANY
# of that patient's rows in training.
rng = np.random.default_rng(0)
n_pat, per_pat = 20, 6
patient = np.repeat(np.arange(n_pat), per_pat)
baseline = rng.normal(scale=2.0, size=n_pat)            # per-patient random intercept
x_id = baseline[patient] + rng.normal(scale=0.05, size=patient.size)   # ~ identifies patient
x_signal = rng.uniform(0, 1, patient.size)              # the genuinely useful feature
Xg = np.c_[x_id, x_signal]
yg = np.sin(3 * x_signal) + baseline[patient] + rng.normal(scale=0.3, size=patient.size)


def knn_fit(Xtr, ytr, k=5):
    """Standardise features, then predict each point as the mean y of its k
    nearest training neighbours (Euclidean distance)."""
    mu, sd = Xtr.mean(axis=0), Xtr.std(axis=0) + 1e-9
    Z = (Xtr - mu) / sd

    def predict(Xn):
        Zn = (Xn - mu) / sd
        out = np.empty(len(Zn))
        for i, row in enumerate(Zn):
            d = np.sqrt(((Z - row) ** 2).sum(axis=1))
            out[i] = ytr[np.argsort(d)[:k]].mean()
        return out
    return predict


def group_kfold_indices(groups, k, seed=0):
    """Split by GROUP: every row of a group lands in the same fold."""
    rng = np.random.default_rng(seed)
    uniq = rng.permutation(np.unique(groups))
    group_folds = np.array_split(uniq, k)
    return [np.flatnonzero(np.isin(groups, gf)) for gf in group_folds]


def cv_with_folds(fit_fn, X, y, folds):
    errs = []
    for i in range(len(folds)):
        va = folds[i]
        tr = np.concatenate([folds[j] for j in range(len(folds)) if j != i])
        predict = fit_fn(X[tr], y[tr])
        errs.append(mse(y[va], predict(X[va])))
    return float(np.mean(errs))

naive_folds = [np.array(f) for f in kfold_indices(len(Xg), 5, seed=0)]
grouped_folds = group_kfold_indices(patient, 5, seed=0)
grp_naive = cv_with_folds(knn_fit, Xg, yg, naive_folds)
grp_group = cv_with_folds(knn_fit, Xg, yg, grouped_folds)
print("  grouped data (k-nearest-neighbours model):")
print(f"    naive 5-fold  CV MSE = {grp_naive:.3f}"
      f"   (same patient in train AND val -> model reuses that patient's baseline)")
print(f"    group 5-fold  CV MSE = {grp_group:.3f}"
      f"   (a patient is entirely in or entirely out -> realistic)")
print("    naive KFold here silently assumes deployment on patients already seen"
      " in training.")

# ---- time-ordered data --------------------------------------------------
n_t = 150
t = np.arange(n_t)
y_t = 0.03 * t + np.sin(t / 6.0) + rng.normal(scale=0.25, size=n_t)


def knn_in_time_fit(t_tr, y_tr, k=3):
    """Predict y(t) as the mean of the k training points closest in time."""
    t_tr = np.asarray(t_tr); y_tr = np.asarray(y_tr)

    def predict(t_new):
        out = np.empty(len(t_new))
        for i, tt in enumerate(np.asarray(t_new)):
            nearest = np.argsort(np.abs(t_tr - tt))[:k]
            out[i] = y_tr[nearest].mean()
        return out
    return predict

# shuffled k-fold: a test point's immediate neighbours t-1, t+1 are in train
shuf_folds = [np.array(f) for f in kfold_indices(n_t, 5, seed=0)]
shuffled_cv = cv_with_folds(lambda a, b: knn_in_time_fit(a, b), t, y_t, shuf_folds)

# forward-chaining: always train on the past, validate on the next block
def time_series_folds(n, k):
    fold = n // (k + 1)
    return [(np.arange(0, fold * (i + 1)), np.arange(fold * (i + 1), fold * (i + 2)))
            for i in range(k)]

fwd_errs = []
for tr, va in time_series_folds(n_t, 5):
    predict = knn_in_time_fit(t[tr], y_t[tr])
    fwd_errs.append(mse(y_t[va], predict(t[va])))
forward_cv = float(np.mean(fwd_errs))

print("  time-ordered data (k-nearest-in-time predictor):")
print(f"    shuffled 5-fold      CV MSE = {shuffled_cv:.3f}"
      f"   (model interpolates between future and past points it has seen)")
print(f"    forward-chaining     CV MSE = {forward_cv:.3f}"
      f"   (train on past, predict forward - how it is really used)")
print("    shuffled KFold here silently assumes you can train on the future.")

fig5 = go.Figure()
fig5.add_bar(x=["grouped: naive", "grouped: group-aware",
               "time: shuffled", "time: forward-chain"],
            y=[grp_naive, grp_group, shuffled_cv, forward_cv],
            marker_color=["#f87171", "#2dd4bf", "#f87171", "#2dd4bf"])
fig5.update_layout(title="Part 4: naive splits (red) look better than they are",
                   yaxis_title="5-fold CV MSE", template="plotly_white")
fig5.write_html("part4_splitters.html")
print("  wrote part4_splitters.html")


# =====================================================================
# Part 5 - the full model-selection workflow
# =====================================================================
print()
print("=" * 64)
print("Part 5 - the full workflow (test set touched exactly once)")
print("=" * 64)

x5, y5 = make_sine_data(n=150, seed=42)

# 1. lock the test set - nothing below looks at x_test/y_test until the end
x_pool, x_test, y_pool, y_test = train_test_split(x5, y5, test_frac=0.2, seed=0)

# 2. grid-search alpha with our own cross_val_score, on the pool only
alphas = [1e-3, 1e-2, 1e-1, 1.0, 10.0]
cv_by_alpha = {a: cross_val_score(
    (lambda xt, yt, a=a: fit_poly_ridge(xt, yt, degree=8, alpha=a)),
    x_pool, y_pool, k=5, seed=0).mean() for a in alphas}
for a, s in cv_by_alpha.items():
    print(f"    alpha = {a:<7}  5-fold CV MSE = {s:.4f}")
best_alpha = min(cv_by_alpha, key=lambda a: cv_by_alpha[a])
print(f"  best alpha by CV = {best_alpha}")

# 3. refit the winner on the ENTIRE pool
final_model = fit_poly_ridge(x_pool, y_pool, degree=8, alpha=best_alpha)

# 4. score the test set - once
test_mse = mse(y_test, final_model(x_test))
print(f"  TEST MSE (reported once, decisions already locked) = {test_mse:.4f}")

print()
print("  The peeking failure mode:")
print("   If we now dislike that number, widen `alphas`, re-run the grid, and")
print("   re-score the test set, the test set has become a second validation")
print("   set. Every score after that first peek is an optimistic estimate,")
print("   because we started choosing hyperparameters to fit THIS test sample.")

print()
print("Done. Open the part*.html figures.")
