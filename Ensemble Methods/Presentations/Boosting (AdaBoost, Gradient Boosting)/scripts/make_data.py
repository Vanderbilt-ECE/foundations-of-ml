"""Generate the data behind every chart in the Boosting deck.

Run from the deck folder:  python scripts/make_data.py
Writes small JSON files into data/. Every number on the slides comes from here,
with fixed seeds, so rerunning reproduces the deck exactly.
Generated with scikit-learn 1.9.1 and NumPy; other versions may shift the numbers slightly,
and the slide text quotes several of them directly.

The toy sine data, the two-moons data and the California split are the same ones used in
the Bagging and Random Forests deck, so numbers can be compared across the two decks.
"""

import json
from pathlib import Path

import numpy as np
from sklearn.datasets import fetch_california_housing, make_moons
from sklearn.ensemble import (
    AdaBoostClassifier,
    BaggingRegressor,
    GradientBoostingRegressor,
    HistGradientBoostingRegressor,
    RandomForestRegressor,
)
from sklearn.tree import DecisionTreeClassifier, DecisionTreeRegressor

OUT = Path(__file__).resolve().parent.parent / "data"
OUT.mkdir(exist_ok=True)


def r(a, k=3):
    return np.round(np.asarray(a, dtype=float), k).tolist()


def dump(name, obj):
    (OUT / f"{name}.json").write_text(json.dumps(obj, separators=(",", ":")))
    print(f"wrote data/{name}.json")


# ---------------------------------------------------------------------------
# 1D toy regression: y = sin(2πx) + noise (same 50 points as the bagging deck)
# ---------------------------------------------------------------------------
NOISE_1D = 0.3
N_1D = 50
truth = lambda x: np.sin(2 * np.pi * x)


def draw_1d(rng, n=N_1D):
    x = np.sort(rng.uniform(0, 1, n))
    return x, truth(x) + rng.normal(0, NOISE_1D, n)


x, y = draw_1d(np.random.default_rng(610))
X = x[:, None]
grid = np.linspace(0, 1, 201)
G = grid[:, None]
rt = np.random.default_rng(1)
xt = rt.uniform(0, 1, 5000)
yt = truth(xt) + rt.normal(0, NOISE_1D, 5000)
LEAF = 5  # stumps in the boosting walkthrough keep at least 5 points per side, so no round isolates one point

# Gradient boosting by hand: start from the mean, fit a stump to the residuals, add it (η = 1)
F, Fg = np.full(N_1D, y.mean()), np.full(len(grid), y.mean())
rounds = []
for t in range(3):
    res = y - F
    stump = DecisionTreeRegressor(max_depth=1, min_samples_leaf=LEAF).fit(X, res)
    rounds.append({"F": r(F), "Fg": r(Fg), "res": r(res), "h": r(stump.predict(G)),
                   "thr": round(float(stump.tree_.threshold[0]), 3)})
    F = F + stump.predict(X)
    Fg = Fg + stump.predict(G)
rounds.append({"F": r(F), "Fg": r(Fg), "res": r(y - F)})
# the hand loop is exactly scikit-learn's GradientBoostingRegressor with learning_rate=1, stumps
gb1 = GradientBoostingRegressor(learning_rate=1.0, n_estimators=1000, max_depth=1, min_samples_leaf=LEAF,
                                random_state=0).fit(X, y)
assert np.allclose(list(gb1.staged_predict(X))[2], F)

SNAP = [1, 3, 10, 20, 50, 1000]
staged_g = list(gb1.staged_predict(G))
snaps = {str(m): r(staged_g[m - 1]) for m in SNAP}
snap_train = {str(m): round(float(np.mean((p - y) ** 2)), 3)
              for m, p in zip(range(1, 1001), gb1.staged_predict(X)) if m in SNAP}

# Train and test MSE as rounds are added, for three learning rates (stumps)
Ms = sorted({int(round(v)) for v in np.geomspace(1, 1000, 60)})
curves = {"M": Ms, "noise": NOISE_1D ** 2}
for eta in [1.0, 0.3, 0.1]:
    gb = GradientBoostingRegressor(learning_rate=eta, n_estimators=1000, max_depth=1, min_samples_leaf=LEAF,
                                   random_state=0).fit(X, y)
    te = np.array([np.mean((p - yt) ** 2) for p in gb.staged_predict(xt[:, None])])
    tr = np.array([np.mean((p - y) ** 2) for p in gb.staged_predict(X)])
    curves[str(eta)] = {"test": r(te[np.array(Ms) - 1], 4), "train": r(tr[np.array(Ms) - 1], 4),
                        "best": int(te.argmin() + 1), "bestTest": round(float(te.min()), 3),
                        "lastTest": round(float(te[-1]), 3)}
    print(f"  1D eta {eta}: best M {te.argmin() + 1} test {te.min():.3f}, at 1000 {te[-1]:.3f}, train {tr[-1]:.4f}")
# Averaging stumps: one stump vs 50 bagged stumps on the same 50 points
stump_fit = DecisionTreeRegressor(max_depth=1).fit(X, y).predict(G)
bag_stumps = BaggingRegressor(DecisionTreeRegressor(max_depth=1), n_estimators=50, random_state=0).fit(X, y)
dump("oned", {"x": r(x), "y": r(y), "grid": r(grid, 4), "truth": r(truth(grid)),
              "stump": r(stump_fit), "bagStumps": r(bag_stumps.predict(G)),
              "rounds": rounds, "snaps": snaps, "snapTrain": snap_train, "curves": curves})

# Bias² and variance over 200 fresh datasets, for five learners
R_BV = 200
rb = np.random.default_rng(99)
sets = [draw_1d(rb) for _ in range(R_BV)]
learners = {
    "stump": lambda: DecisionTreeRegressor(max_depth=1),
    "bagStump": lambda: BaggingRegressor(DecisionTreeRegressor(max_depth=1), n_estimators=50, random_state=0),
    "boostStump": lambda: GradientBoostingRegressor(learning_rate=0.1, n_estimators=100, max_depth=1, random_state=0),
    "deep": lambda: DecisionTreeRegressor(random_state=0),
    "bagDeep": lambda: BaggingRegressor(DecisionTreeRegressor(), n_estimators=50, random_state=0),
}
bv = {}
for k, make in learners.items():
    P = np.array([make().fit(xi[:, None], yi).predict(G) for xi, yi in sets])
    bv[k] = {"bias2": round(float(np.mean((P.mean(0) - truth(grid)) ** 2)), 3),
             "var": round(float(np.mean(P.var(0))), 3), "mean": r(P.mean(0)), "one": r(P[0])}
    print(f"  {k}: bias2 {bv[k]['bias2']} var {bv[k]['var']}")
dump("biasvar", {"R": R_BV, "grid": r(grid, 4), "truth": r(truth(grid)), **bv})

# Robust losses: the same points with three corrupted labels
y_out = y.copy()
bad = [12, 13, 30]
y_out[bad] = [2.6, 2.4, -2.6]
robust = {"x": r(x), "y": r(y_out), "bad": bad}
for loss in ["squared_error", "absolute_error"]:
    gb = GradientBoostingRegressor(loss=loss, learning_rate=0.1, n_estimators=200, max_depth=2, random_state=0)
    robust[loss] = r(gb.fit(X, y_out).predict(G))
    robust[loss + "_mse"] = round(float(np.mean((np.asarray(robust[loss]) - truth(grid)) ** 2)), 3)
    print(f"  robust {loss}: MSE vs truth {robust[loss + '_mse']}")
dump("robust", robust)

# ---------------------------------------------------------------------------
# AdaBoost by hand on 12 points: three rounds of stumps, weights and votes
# ---------------------------------------------------------------------------


def best_stump(Xs, ys, w):
    best = None
    for f in range(2):
        vals = np.unique(Xs[:, f])
        for t in (vals[:-1] + vals[1:]) / 2:
            for s in (1, -1):
                h = np.where(Xs[:, f] > t, s, -s)
                e = w[h != ys].sum()
                if best is None or e < best[0] - 1e-12:
                    best = (e, f, t, s)
    return best


ra = np.random.default_rng(2863)
Xa = np.round(ra.uniform(0.05, 0.95, (12, 2)), 2)
ya = np.where((Xa[:, 0] < 0.45) & (Xa[:, 1] > 0.3) | (Xa[:, 1] < 0.2), 1, -1)
w = np.full(12, 1 / 12)
Fa = np.zeros(12)
ada_rounds = []
for t in range(3):
    e, f, thr, s = best_stump(Xa, ya, w)
    h = np.where(Xa[:, f] > thr, s, -s)
    a = 0.5 * np.log((1 - e) / e)
    ada_rounds.append({"w": r(w, 4), "e": round(float(e), 4), "alpha": round(float(a), 4), "f": int(f),
                       "thr": round(float(thr), 3), "s": int(s), "miss": (h != ya).tolist()})
    print(f"  ada round {t + 1}: feature {f} thr {thr:.3f} eps {e:.3f} alpha {a:.3f} misses {np.flatnonzero(h != ya)}")
    Fa += a * h
    w = w * np.exp(-a * ya * h)
    w /= w.sum()
assert np.all(np.sign(Fa) == ya)
dump("ada", {"X": r(Xa, 2), "y": ya.tolist(), "rounds": ada_rounds, "wEnd": r(w, 4)})

# ---------------------------------------------------------------------------
# AdaBoost on two moons (same data as the bagging deck)
# ---------------------------------------------------------------------------
Xm, ym = make_moons(300, noise=0.3, random_state=3)
Xt, yt_m = make_moons(5000, noise=0.3, random_state=4)
xs = np.linspace(-1.6, 2.6, 84)
ys_ = np.linspace(-1.2, 1.7, 58)
gx, gy = np.meshgrid(xs, ys_)
Gm = np.c_[gx.ravel(), gy.ravel()]
ab = AdaBoostClassifier(DecisionTreeClassifier(max_depth=1), n_estimators=400, random_state=0).fit(Xm, ym)
acc = [float(np.mean(p == yt_m)) for p in ab.staged_predict(Xt)]
moons = {"xs": r(xs), "ys": r(ys_), "X": r(Xm), "y": ym.tolist(), "acc": r(acc), "stages": {}}
for m, dfun in enumerate(ab.staged_decision_function(Gm), start=1):
    if m in (1, 10, 400):
        moons["stages"][str(m)] = r(dfun.reshape(len(ys_), len(xs)), 2)
for m in (1, 10, 100, 400):
    print(f"  moons AdaBoost {m} stumps: test acc {acc[m - 1]:.3f}")
moons["tree"] = 0.834  # from the bagging deck (data/moons.json there): one deep tree
moons["bag"] = 0.883  # 300 bagged deep trees
dump("moons", moons)

# ---------------------------------------------------------------------------
# California housing, same split as the bagging deck: one training set of 2,000 rows,
# 2,000 held-out evaluation rows.
# ---------------------------------------------------------------------------
cal = fetch_california_housing()
Xc, yc = cal.data, cal.target
perm_c = np.random.default_rng(0).permutation(len(yc))
ev, pool = perm_c[:2000], perm_c[2000:]
Xev, yev = Xc[ev], yc[ev]
idx = np.random.default_rng(0).choice(pool, 2000, replace=False)
Xtr, ytr = Xc[idx], yc[idx]


def mse(p, t=yev):
    return float(np.mean((p - t) ** 2))


ref = {
    "tree": mse(DecisionTreeRegressor(random_state=0).fit(Xtr, ytr).predict(Xev)),
    "bag": mse(RandomForestRegressor(500, max_features=None, random_state=0, n_jobs=-1).fit(Xtr, ytr).predict(Xev)),
    "rf": mse(RandomForestRegressor(500, max_features=3, random_state=0, n_jobs=-1).fit(Xtr, ytr).predict(Xev)),
}
# must agree with the bagging deck's numbers (0.586, 0.338, 0.310)
assert abs(ref["tree"] - 0.586) < 5e-4 and abs(ref["bag"] - 0.338) < 6e-4 and abs(ref["rf"] - 0.310) < 5e-4, ref

Mc = sorted({int(round(v)) for v in np.geomspace(1, 2000, 70)})
etas = {"M": Mc}
for eta in [1.0, 0.3, 0.1, 0.03]:
    gb = GradientBoostingRegressor(learning_rate=eta, n_estimators=2000, max_depth=3, random_state=0).fit(Xtr, ytr)
    te = np.array([mse(p) for p in gb.staged_predict(Xev)])
    tr = np.array([mse(p, ytr) for p in gb.staged_predict(Xtr)])
    etas[str(eta)] = {"test": r(te[np.array(Mc) - 1], 4), "train": r(tr[np.array(Mc) - 1], 4),
                      "best": int(te.argmin() + 1), "bestTest": round(float(te.min()), 3),
                      "lastTest": round(float(te[-1]), 3)}
    print(f"  cal eta {eta}: best M {te.argmin() + 1} test {te.min():.4f}, at 2000 {te[-1]:.4f}, train {tr[-1]:.4f}")
dump("cal_eta", etas)

depths = {"M": Mc, "rf": round(ref["rf"], 3)}
for dpt in [1, 3, 6]:
    gb = GradientBoostingRegressor(learning_rate=0.1, n_estimators=2000, max_depth=dpt, random_state=0).fit(Xtr, ytr)
    te = np.array([mse(p) for p in gb.staged_predict(Xev)])
    depths[str(dpt)] = {"test": r(te[np.array(Mc) - 1], 4), "best": int(te.argmin() + 1),
                        "bestTest": round(float(te.min()), 3), "lastTest": round(float(te[-1]), 3)}
    print(f"  cal depth {dpt}: best M {te.argmin() + 1} test {te.min():.4f}")
dump("cal_depth", depths)

# The early-stopping recipe from the slides
hgb = HistGradientBoostingRegressor(learning_rate=0.1, max_iter=2000, early_stopping=True,
                                    validation_fraction=0.1, n_iter_no_change=10, random_state=0).fit(Xtr, ytr)
compare = {k: round(v, 4) for k, v in ref.items()}
compare["stumps"] = depths["1"]["lastTest"]  # all 2,000 rounds: not tuned on the test set
compare["gb"] = round(mse(hgb.predict(Xev)), 3)
compare["gbIters"] = int(hgb.n_iter_)
print(f"  hist GB early stopping: {hgb.n_iter_} iterations, test MSE {compare['gb']}")
dump("cal_compare", compare)

# ---------------------------------------------------------------------------
# Feature importance: the depth-3, eta = 0.1 model from the depth slide (325 rounds = its best round),
# on the same California split. Two variants of the feature matrix:
#   A. the 8 real features plus a pure-noise column (uniform random)
#   B. the 8 real features plus a noisy copy of MedInc (a correlated stand-in)
# ---------------------------------------------------------------------------
from sklearn.inspection import permutation_importance

M_IMP = depths["3"]["best"]


def importance_fit(extra_tr, extra_ev, names_extra, seed):
    Xt = np.c_[Xtr, extra_tr]
    Xe = np.c_[Xev, extra_ev]
    gbi = GradientBoostingRegressor(learning_rate=0.1, n_estimators=M_IMP, max_depth=3, random_state=0).fit(Xt, ytr)
    pim = permutation_importance(gbi, Xe, yev, scoring="neg_mean_squared_error", n_repeats=10, random_state=seed)
    return {"names": list(cal.feature_names) + names_extra, "mdi": r(gbi.feature_importances_, 4),
            "perm": r(pim.importances_mean, 4), "permStd": r(pim.importances_std, 4),
            "testMse": round(mse(gbi.predict(Xe)), 3)}


rn_a = np.random.default_rng(7)
imp_a = importance_fit(rn_a.uniform(size=(len(Xtr), 1)), rn_a.uniform(size=(len(Xev), 1)), ["RandomNoise"], 0)
rn_b = np.random.default_rng(1)
imp_b = importance_fit((Xtr[:, 0] + rn_b.normal(0, 0.2, len(Xtr)))[:, None],
                       (Xev[:, 0] + rn_b.normal(0, 0.2, len(Xev)))[:, None], ["MedInc copy"], 0)
for tag, o in (("noise column", imp_a), ("MedInc copy", imp_b)):
    print(f"  importance with {tag}: test MSE {o['testMse']}")
    for n, a, p in zip(o["names"], o["mdi"], o["perm"]):
        print(f"    {n:12s} impurity {a:.3f}  permutation {p:.3f}")
print(f"  corr(Latitude, Longitude) = {np.corrcoef(Xtr[:, 6], Xtr[:, 7])[0, 1]:.2f}")
dump("importance", {"M": M_IMP, "noise": imp_a, "copy": imp_b,
                    "latLonCorr": round(float(np.corrcoef(Xtr[:, 6], Xtr[:, 7])[0, 1]), 2)})

# ---------------------------------------------------------------------------
# Stacking and blending on the same California split. Base models: the forest and the
# early-stopped histogram booster from the scoreboard, plus a linear regression.
# Stacking: 5-fold out-of-fold predictions feed a non-negative linear meta-model.
# Blending: base models fit on 80% of the rows, meta-model fit on the other 20%.
# ---------------------------------------------------------------------------
from sklearn.ensemble import StackingRegressor
from sklearn.linear_model import LinearRegression
from sklearn.model_selection import KFold
from sklearn.pipeline import make_pipeline
from sklearn.preprocessing import StandardScaler


def stack_bases():
    return [("rf", RandomForestRegressor(500, max_features=3, random_state=0, n_jobs=-1)),
            ("gb", HistGradientBoostingRegressor(learning_rate=0.1, max_iter=2000, early_stopping=True,
                                                 validation_fraction=0.1, n_iter_no_change=10, random_state=0)),
            ("lin", make_pipeline(StandardScaler(), LinearRegression()))]


stack = StackingRegressor(stack_bases(), final_estimator=LinearRegression(positive=True),
                          cv=KFold(5, shuffle=True, random_state=0)).fit(Xtr, ytr)
base_pred = {n: m.predict(Xev) for n, m in stack.named_estimators_.items()}
assert abs(mse(base_pred["rf"]) - compare["rf"]) < 5e-4 and abs(mse(base_pred["gb"]) - compare["gb"]) < 5e-4

pb = np.random.default_rng(0).permutation(len(ytr))
fit_idx, meta_idx = pb[:1600], pb[1600:]
blend_bases = [(n, m.fit(Xtr[fit_idx], ytr[fit_idx])) for n, m in stack_bases()]
Zm = np.c_[[m.predict(Xtr[meta_idx]) for _, m in blend_bases]].T
blend_meta = LinearRegression(positive=True).fit(Zm, ytr[meta_idx])
blend_pred = blend_meta.predict(np.c_[[m.predict(Xev) for _, m in blend_bases]].T)

stacking = {
    "lin": round(mse(base_pred["lin"]), 3), "rf": round(mse(base_pred["rf"]), 3), "gb": round(mse(base_pred["gb"]), 3),
    "avg": round(mse(np.mean(list(base_pred.values()), axis=0)), 3),
    "blend": round(mse(blend_pred), 3), "stack": round(mse(stack.predict(Xev)), 3),
    "weights": {n: round(float(c), 2) for n, c in zip(["rf", "gb", "lin"], stack.final_estimator_.coef_)},
}
print(f"  stacking: {stacking}")
dump("stacking", stacking)
