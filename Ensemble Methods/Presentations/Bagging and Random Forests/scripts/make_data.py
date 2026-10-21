"""Generate the data behind every chart in the Bagging and Random Forests deck.

Run from the deck folder:  python scripts/make_data.py
Writes small JSON files into data/. Every number on the slides comes from here,
with fixed seeds, so rerunning reproduces the deck exactly.
Generated with scikit-learn 1.9.1 and NumPy; other versions may shift the numbers slightly,
and the slide text quotes several of them directly.
"""

import json
from pathlib import Path

import numpy as np
from sklearn.datasets import fetch_california_housing, make_moons
from sklearn.ensemble import BaggingClassifier, RandomForestRegressor
from sklearn.inspection import permutation_importance
from sklearn.linear_model import LinearRegression
from sklearn.tree import DecisionTreeClassifier, DecisionTreeRegressor

OUT = Path(__file__).resolve().parent.parent / "data"
OUT.mkdir(exist_ok=True)


def r(a, k=3):
    return np.round(np.asarray(a, dtype=float), k).tolist()


def dump(name, obj):
    (OUT / f"{name}.json").write_text(json.dumps(obj, separators=(",", ":")))
    print(f"wrote data/{name}.json")


# ---------------------------------------------------------------------------
# 1D toy regression: y = sin(2πx) + noise
# ---------------------------------------------------------------------------
NOISE_1D = 0.3
N_1D = 50
truth = lambda x: np.sin(2 * np.pi * x)


def draw_1d(rng, n=N_1D):
    x = np.sort(rng.uniform(0, 1, n))
    return x, truth(x) + rng.normal(0, NOISE_1D, n)


rng = np.random.default_rng(610)
x, y = draw_1d(rng)
grid = np.linspace(0, 1, 201)
B_1D = 25
boots = [rng.integers(0, N_1D, N_1D) for _ in range(B_1D)]
tree_fits, lin_fits, counts = [], [], []
for b, idx in enumerate(boots):
    t = DecisionTreeRegressor(random_state=b).fit(x[idx, None], y[idx])
    tree_fits.append(t.predict(grid[:, None]))
    lm = LinearRegression().fit(x[idx, None], y[idx])
    lin_fits.append([lm.intercept_, lm.coef_[0]])
    counts.append(np.bincount(idx, minlength=N_1D))
full_tree = DecisionTreeRegressor(random_state=0).fit(x[:, None], y).predict(grid[:, None])
full_lin = LinearRegression().fit(x[:, None], y)
dump("oned", {
    "x": r(x), "y": r(y), "grid": r(grid, 4), "truth": r(truth(grid)),
    "trees": [r(f) for f in tree_fits],
    "avg": r(np.mean(tree_fits, axis=0)),
    "fullTree": r(full_tree),
    "counts": [c.tolist() for c in counts[:3]],
    "lin": r(lin_fits, 4),
    "fullLin": r([full_lin.intercept_, full_lin.coef_[0]], 4),
})

# Sampling distribution of the prediction at one input x0, over fresh training sets
X0 = 0.3
R_1D, B_BAG = 400, 50
single, bagged, members = [], [], []
for i in range(R_1D):
    xi, yi = draw_1d(rng)
    preds = []
    for b in range(B_BAG):
        idx = rng.integers(0, N_1D, N_1D)
        t = DecisionTreeRegressor(random_state=b).fit(xi[idx, None], yi[idx])
        preds.append(t.predict([[X0]])[0])
    single.append(DecisionTreeRegressor(random_state=0).fit(xi[:, None], yi).predict([[X0]])[0])
    members.append(preds[0])
    bagged.append(np.mean(preds))
sig2 = np.var(members)
vbag = np.var(bagged)
rho = (vbag / sig2 - 1 / B_BAG) / (1 - 1 / B_BAG)
dump("atx0", {
    "x0": X0, "truth": round(float(truth(X0)), 3), "B": B_BAG,
    "single": r(single), "bagged": r(bagged),
    "meanSingle": round(float(np.mean(single)), 3), "meanBagged": round(float(np.mean(bagged)), 3),
    "varSingle": round(float(np.var(single)), 4), "varMember": round(float(sig2), 4),
    "varBagged": round(float(vbag), 4), "rho": round(float(rho), 3),
})
print(f"  x0: var single {np.var(single):.4f}, member {sig2:.4f}, bagged {vbag:.4f}, rho {rho:.3f}")

# ---------------------------------------------------------------------------
# 2D classification: decision boundaries on two moons
# ---------------------------------------------------------------------------
Xm, ym = make_moons(300, noise=0.3, random_state=3)
Xt, yt = make_moons(5000, noise=0.3, random_state=4)
xs = np.linspace(-1.6, 2.6, 84)
ys = np.linspace(-1.2, 1.7, 58)
gx, gy = np.meshgrid(xs, ys)
G = np.c_[gx.ravel(), gy.ravel()]
models = {
    "tree": DecisionTreeClassifier(random_state=0),
    "bag": BaggingClassifier(DecisionTreeClassifier(), n_estimators=300, random_state=0),
}
bound = {"xs": r(xs), "ys": r(ys), "X": r(Xm), "y": ym.tolist()}
for k, m in models.items():
    m.fit(Xm, ym)
    bound[k] = r(m.predict_proba(G)[:, 1].reshape(len(ys), len(xs)), 2)
    bound[k + "Acc"] = round(float(m.score(Xt, yt)), 3)
    print(f"  moons {k}: test acc {bound[k + 'Acc']}")
dump("moons", bound)

# ---------------------------------------------------------------------------
# California housing: 8 features, MedInc (median income) is by far the strongest.
# Treat the full dataset as the population; draw training sets of N_C rows from it.
# (fetch_california_housing downloads ~400 KB on first run and caches it.)
# ---------------------------------------------------------------------------
cal = fetch_california_housing()
Xc, yc, FEAT = cal.data, cal.target, list(cal.feature_names)
D = Xc.shape[1]
N_C, M_RF = 2000, 3
perm_c = np.random.default_rng(0).permutation(len(yc))
ev, pool = perm_c[:2000], perm_c[2000:]
Xev, yev = Xc[ev], yc[ev]


def draw_c(seed):
    idx = np.random.default_rng(seed).choice(pool, N_C, replace=False)
    return Xc[idx], yc[idx]


def mse(p, t):
    return round(float(np.mean((p - t) ** 2)), 4)


Xtr, ytr = draw_c(0)


def roots(m):
    return np.bincount([e.tree_.feature[0] for e in m.estimators_], minlength=D).tolist()


bag_c = RandomForestRegressor(300, max_features=None, random_state=0, n_jobs=-1).fit(Xtr, ytr)
rf_c = RandomForestRegressor(300, max_features=M_RF, random_state=0, n_jobs=-1).fit(Xtr, ytr)
dump("roots", {"names": FEAT, "bag": roots(bag_c), "rf": roots(rf_c), "m": M_RF, "d": D, "B": 300})
print(f"  roots bag {roots(bag_c)}\n  roots rf  {roots(rf_c)}")

# Over R_C fresh training sets: test MSE, variance of the forest, member variance σ², implied ρ
R_C, B_C = 20, 200
decomp = []
for m in range(1, D + 1):
    fp, mp, err = [], [], []
    for i in range(R_C):
        Xi, yi = draw_c(100 + i)
        rf = RandomForestRegressor(B_C, max_features=m, random_state=i, n_jobs=-1).fit(Xi, yi)
        p = rf.predict(Xev)
        fp.append(p)
        mp.append(rf.estimators_[0].predict(Xev))
        err.append(np.mean((p - yev) ** 2))
    var = float(np.mean(np.var(fp, axis=0)))
    sig2 = float(np.mean(np.var(mp, axis=0)))
    rho_m = (var / sig2 - 1 / B_C) / (1 - 1 / B_C)
    decomp.append({"m": m, "mse": round(float(np.mean(err)), 4), "var": round(var, 4),
                   "sigma2": round(sig2, 4), "rho": round(rho_m, 3)})
    print(f"  m={m} mse {np.mean(err):.4f} var {var:.4f} sigma2 {sig2:.4f} rho {rho_m:.3f}")
dump("mtradeoff", {"rows": decomp, "B": B_C, "R": R_C, "n": N_C})

# Test error and OOB error as trees are added, on one training set
Bs = [1, 2, 3, 5, 8, 12, 20, 30, 50, 75, 100, 150, 200, 300, 500]
curves = {"B": Bs, "tree": mse(DecisionTreeRegressor(random_state=0).fit(Xtr, ytr).predict(Xev), yev)}
for name, mf in [("bag", None), ("rf", M_RF)]:
    test, oob = [], []
    for B in Bs:
        rf = RandomForestRegressor(B, max_features=mf, random_state=0, n_jobs=-1,
                                   oob_score=B >= 20).fit(Xtr, ytr)
        test.append(mse(rf.predict(Xev), yev))
        oob.append(mse(rf.oob_prediction_, ytr) if B >= 20 else None)
    curves[name], curves[name + "Oob"] = test, oob
    print(f"  {name} test {test}\n  {name} oob  {oob}")
dump("ntrees", curves)

# Feature importance: impurity (MDI) vs permutation, with a meaningless row-id column added
rng_id = np.random.default_rng(7)
Xi_ = np.c_[Xtr, rng_id.permutation(N_C)]
Xit = np.c_[Xev, rng_id.integers(0, N_C, len(yev))]
rf_imp = RandomForestRegressor(300, max_features=M_RF, random_state=0, n_jobs=-1).fit(Xi_, ytr)
pimp = permutation_importance(rf_imp, Xit, yev, n_repeats=10, random_state=0, n_jobs=-1)
pi = np.clip(pimp.importances_mean, 0, None)
dump("importance", {"names": FEAT + ["RowID"], "mdi": r(rf_imp.feature_importances_), "perm": r(pi / pi.sum())})
print("  mdi ", r(rf_imp.feature_importances_))
print("  perm", r(pi / pi.sum()))

# ---------------------------------------------------------------------------

# ---------------------------------------------------------------------------
# Small illustrative bootstrap draws
# ---------------------------------------------------------------------------
rng_b = np.random.default_rng(42)
dump("tokens", {"samples": [sorted((rng_b.integers(0, 10, 10) + 1).tolist()) for _ in range(3)]})
rng_o = np.random.default_rng(616)
dump("oobgrid", {"counts": [np.bincount(rng_o.integers(0, 8, 8), minlength=8).tolist() for _ in range(10)]})
