"""Generate the data behind every chart in the Gaussian Mixture Models deck.

Run from the deck folder:

    uv run --no-project --with scikit-learn==1.9.1 --with scipy python scripts/make_data.py

Writes small JSON files into data/. Every number on the slides comes from here,
with fixed seeds, so rerunning reproduces the deck exactly.

Shared toy datasets use the same recipes as the k-Means deck (blobs3, aniso,
unequal, moons), so the hand-off between decks shows the same points.

EM is written out by hand below (numpy, log-sum-exp) so every iteration can be
recorded; the result is checked against sklearn's GaussianMixture started from
the same parameters.

Real datasets (stored in data/raw/):
  * Old Faithful geyser, 272 eruptions (R datasets::faithful, Härdle 1991):
    https://vincentarelbundock.github.io/Rdatasets/csv/datasets/faithful.csv
  * Iris (Fisher 1936), shipped with scikit-learn.
"""

import csv
import json
import warnings
from pathlib import Path

import numpy as np
from scipy.special import logsumexp
from scipy.stats import multivariate_normal, norm
from sklearn.cluster import KMeans
from sklearn.datasets import load_iris, make_blobs, make_moons
from sklearn.exceptions import ConvergenceWarning
from sklearn.metrics import adjusted_rand_score
from sklearn.mixture import GaussianMixture

warnings.filterwarnings("ignore", category=ConvergenceWarning)

DECK = Path(__file__).resolve().parent.parent
OUT = DECK / "data"
RAW = OUT / "raw"
REG = 1e-6  # sklearn's default reg_covar


def r(a, k=3):
    return np.round(np.asarray(a, dtype=float), k).tolist()


def dump(name, obj):
    (OUT / f"{name}.json").write_text(json.dumps(obj, separators=(",", ":")))
    print(f"wrote data/{name}.json")


def ari(a, b):
    return round(float(adjusted_rand_score(a, b)), 2)


def full_covs(g):
    """Covariances of a fitted GaussianMixture as a (K, d, d) array, whatever its covariance_type."""
    K, d = g.means_.shape
    c = g.covariances_
    if g.covariance_type == "full":
        return c
    if g.covariance_type == "tied":
        return np.repeat(c[None], K, 0)
    if g.covariance_type == "diag":
        return np.array([np.diag(v) for v in c])
    return np.array([np.eye(d) * v for v in c])  # spherical


def params(w, mu, cov, k=4):
    return {"w": r(w, k), "mu": r(mu, k), "cov": r(cov, k)}


def gparams(g, k=4):
    return params(g.weights_, g.means_, full_covs(g), k)


def order_by(g_or_mu, key):
    """Permutation that sorts components by key(mean), so colors are stable across fits."""
    mu = g_or_mu.means_ if hasattr(g_or_mu, "means_") else g_or_mu
    return np.array(sorted(range(len(mu)), key=lambda k: key(mu[k])))


def permute(p, perm):
    return {k: [v[i] for i in perm] for k, v in p.items()}


def relabel(lab, perm):
    inv = np.empty_like(perm)
    inv[perm] = np.arange(len(perm))
    return inv[np.asarray(lab)].tolist()


# ---------------------------------------------------------------------------
# EM by hand
# ---------------------------------------------------------------------------
def log_joint(X, w, mu, cov):
    """log(pi_k N(x_i | mu_k, Sigma_k)), shape (n, K)."""
    return np.column_stack([np.log(w[k]) + multivariate_normal(mu[k], cov[k]).logpdf(X) for k in range(len(w))])


def e_step(X, w, mu, cov):
    lj = log_joint(X, w, mu, cov)
    lse = logsumexp(lj, axis=1)
    return np.exp(lj - lse[:, None]), lse.sum()


def m_step(X, g):
    Nk = g.sum(0)
    w = Nk / len(X)
    mu = (g.T @ X) / Nk[:, None]
    cov = []
    for k in range(g.shape[1]):
        D = X - mu[k]
        cov.append((g[:, k, None] * D).T @ D / Nk[k] + REG * np.eye(X.shape[1]))
    return w, mu, np.array(cov)


def em(X, w, mu, cov, iters):
    """Run EM; frame t holds the parameters after t iterations and their log-likelihood."""
    w, mu, cov = np.asarray(w, float), np.asarray(mu, float), np.asarray(cov, float)
    frames = []
    for t in range(iters + 1):
        g, ll = e_step(X, w, mu, cov)
        frames.append({"w": w, "mu": mu, "cov": cov, "ll": ll})
        if t < iters:
            w, mu, cov = m_step(X, g)
    return frames


def frames_json(frames, perm, k=3):
    return [{"w": r(f["w"][perm], k), "mu": r(f["mu"][perm], k), "cov": r(f["cov"][perm], k), "ll": round(float(f["ll"]), 2)} for f in frames]


# ---------------------------------------------------------------------------
# Shared toy data (same recipes as the k-Means deck)
# ---------------------------------------------------------------------------
X3, y3 = make_blobs(n_samples=300, centers=3, cluster_std=0.8, random_state=0)
rng = np.random.default_rng(0)
A1 = rng.multivariate_normal([0, 0], [[3, 1.6], [1.6, 1]], 150)
A2 = rng.multivariate_normal([1.2, -2.4], [[3, 1.6], [1.6, 1]], 150)
Xa, ya = np.vstack([A1, A2]), np.r_[np.zeros(150, int), np.ones(150, int)]
Xu, yu = make_blobs(n_samples=[350, 60, 30], centers=[(-4, 0), (3, 2.5), (3.2, -2)], cluster_std=[2.0, 0.5, 0.4], random_state=170)
Xm, ym = make_moons(300, noise=0.06, random_state=0)

# ---------------------------------------------------------------------------
# Where k-means failed: the stretched ellipses and the unequal blobs
# ---------------------------------------------------------------------------
fixes = {}
for name, X, y, k in [("aniso", Xa, ya, 2), ("unequal", Xu, yu, 3)]:
    km = KMeans(k, n_init=10, random_state=0).fit(X)
    # sklearn's default init runs k-means first, and EM then stays in k-means' wrong answer (kmInitAri).
    # Twenty starts from random data points find the right one.
    g0 = GaussianMixture(k, covariance_type="full", random_state=0).fit(X)
    g = GaussianMixture(k, covariance_type="full", init_params="random_from_data", n_init=20, random_state=0).fit(X)
    perm = order_by(g, lambda m: (m[0], m[1]))
    kperm = order_by(km.cluster_centers_, lambda m: (m[0], m[1]))
    fixes[name] = {
        "pts": r(X), "truth": y.tolist(),
        "km": relabel(km.labels_, kperm), "kmC": r(km.cluster_centers_[kperm]), "kmAri": ari(y, km.labels_),
        "gmm": permute(gparams(g), perm), "gmmAri": ari(y, g.predict(X)),
        "kmInitAri": ari(y, g0.predict(X)), "ll": round(float(g.score(X) * len(X)), 1), "kmInitLl": round(float(g0.score(X) * len(X)), 1),
    }
dump("fixes", fixes)
print(f"  ARI k-means / GMM / GMM from k-means init: { {k: (v['kmAri'], v['gmmAri'], v['kmInitAri'], v['ll'], v['kmInitLl']) for k, v in fixes.items()} }")

# ---------------------------------------------------------------------------
# The running example: three overlapping Gaussians of different shape and weight
# ---------------------------------------------------------------------------
TRUE = {
    "w": np.array([0.45, 0.35, 0.20]),
    "mu": np.array([[0.0, 0.0], [4.2, 1.4], [2.6, -2.6]]),
    "cov": np.array([[[2.2, 1.3], [1.3, 1.1]], [[0.7, -0.35], [-0.35, 0.9]], [[0.35, 0.0], [0.0, 0.3]]]),
}
N = 500
rs = np.random.default_rng(7)
z = rs.choice(3, N, p=TRUE["w"])
X = np.array([rs.multivariate_normal(TRUE["mu"][k], TRUE["cov"][k]) for k in z])

# EM from a deliberately rough start: three data points as means, the overall covariance, equal weights
start_idx = [37, 41, 63]
w0 = np.full(3, 1 / 3)
mu0 = X[start_idx]
cov0 = np.repeat(np.cov(X.T)[None] * 0.5, 3, 0)
ITERS = 60
frames = em(X, w0, mu0, cov0, ITERS)
lls = np.array([f["ll"] for f in frames])
assert np.all(np.diff(lls) >= -1e-6), "EM log-likelihood decreased"
conv = int(np.argmax(np.abs(np.diff(lls)) / N < 1e-3)) + 1  # sklearn's stopping rule (tol=1e-3 on mean log-lik)

ref = GaussianMixture(3, covariance_type="full", max_iter=ITERS, tol=0, weights_init=w0, means_init=mu0,
                      precisions_init=np.linalg.inv(cov0)).fit(X)
assert np.allclose(ref.means_, frames[-1]["mu"], atol=1e-6), "hand EM disagrees with sklearn"
assert np.allclose(ref.covariances_, frames[-1]["cov"], atol=1e-6)

perm = order_by(frames[-1]["mu"], lambda m: m[0] + 0.01 * m[1])  # left, bottom-middle, right
# make color 0 = the big tilted one, 1 = the right one, 2 = the small one (matches TRUE order)
fin = frames[-1]
perm = np.array([int(np.argmin([np.linalg.norm(fin["mu"][j] - TRUE["mu"][k]) for j in range(3)])) for k in range(3)])
assert sorted(perm.tolist()) == [0, 1, 2]
g_fin, _ = e_step(X, fin["w"], fin["mu"], fin["cov"])
lab_fin = g_fin.argmax(1)
km = KMeans(3, n_init=10, random_state=0).fit(X)
kperm = np.array([int(np.argmin([np.linalg.norm(km.cluster_centers_[j] - TRUE["mu"][k]) for j in range(3)])) for k in range(3)])
ent = -(g_fin * np.log(np.clip(g_fin, 1e-12, 1))).sum(1) / np.log(3)
dump("em", {
    "pts": r(X), "truth": z.tolist(), "true": params(TRUE["w"], TRUE["mu"], TRUE["cov"]),
    "start": start_idx, "frames": frames_json(frames, perm), "conv": conv,
    "km": relabel(km.labels_, kperm), "kmC": r(km.cluster_centers_[kperm]),
    "kmAri": ari(z, km.labels_), "gmmAri": ari(z, lab_fin),
    "nUnsure": int((g_fin.max(1) < 0.9).sum()),
})
print(f"  EM: ll {lls[0]:.1f} -> {lls[-1]:.1f}, sklearn-style convergence at iter {conv}; ARI km {ari(z, km.labels_)} gmm {ari(z, lab_fin)}; "
      f"points with max resp < 0.9: {(g_fin.max(1) < 0.9).sum()}; mean entropy {ent.mean():.3f}")
print("  EM ll by iter:", np.round(lls[:12], 1).tolist(), "...", round(lls[-1], 1))
print("  fitted w:", np.round(fin['w'][perm], 3).tolist(), " mu:", np.round(fin['mu'][perm], 2).tolist())

# ---------------------------------------------------------------------------
# sklearn API outputs for the code slide (default init: k-means, n_init=1)
# ---------------------------------------------------------------------------
gm = GaussianMixture(n_components=3, covariance_type="full", random_state=0).fit(X)
P = gm.predict_proba(X)
api_perm = np.array([int(np.argmin([np.linalg.norm(gm.means_[j] - TRUE["mu"][k]) for j in range(3)])) for k in range(3)])
unsure = int(np.argmin(np.abs(P[:, api_perm[0]] - 0.5) + (P[:, api_perm[2]] > 0.02)))  # a 0/1 boundary point
show_rows = [0, 1, unsure]
api = {
    "weights": r(gm.weights_[api_perm], 2), "means": r(gm.means_[api_perm], 2),
    "proba": [r(P[i, api_perm], 2) for i in show_rows], "rows": show_rows,
    "pred": [int(np.argmax(P[i, api_perm])) for i in show_rows],
    "iters": int(gm.n_iter_), "converged": bool(gm.converged_),
    "bic": round(float(gm.bic(X)), 1), "aic": round(float(gm.aic(X)), 1),
    "lb": round(float(gm.lower_bound_), 3), "score": round(float(gm.score(X)), 3),
    "unsurePt": r(X[unsure], 2),
}
dump("api", api)
print(f"  API: {api}")

# ---------------------------------------------------------------------------
# Covariance types on the running example
# ---------------------------------------------------------------------------
cov_types = {}
for ct in ["spherical", "diag", "tied", "full"]:
    g = GaussianMixture(3, covariance_type=ct, n_init=5, random_state=0).fit(X)
    p = np.array([int(np.argmin([np.linalg.norm(g.means_[j] - TRUE["mu"][k]) for j in range(3)])) for k in range(3)])
    cov_types[ct] = {**permute(gparams(g, 3), p), "p": int(g._n_parameters()), "bic": round(float(g.bic(X)), 1),
                     "ari": ari(z, g.predict(X)), "ll": round(float(g.score(X) * N), 1)}
dump("covtypes", cov_types)
print(f"  cov types: { {k: (v['p'], v['bic'], v['ari']) for k, v in cov_types.items()} }")

# ---------------------------------------------------------------------------
# Choosing K: BIC / AIC sweeps on the running example
# ---------------------------------------------------------------------------
Ks = list(range(1, 9))
sweep = {ct: [] for ct in ["spherical", "diag", "tied", "full"]}
fitsK = []
for k in Ks:
    for ct in sweep:
        g = GaussianMixture(k, covariance_type=ct, n_init=5, random_state=0).fit(X)
        sweep[ct].append({"bic": round(float(g.bic(X)), 1), "aic": round(float(g.aic(X)), 1),
                          "ll": round(float(g.score(X) * N), 1), "p": int(g._n_parameters())})
        if ct == "full":
            o = order_by(g, lambda m: (round(m[0], 1), m[1]))
            if k == 3:
                o = np.array([int(np.argmin([np.linalg.norm(g.means_[j] - TRUE["mu"][kk]) for j in range(3)])) for kk in range(3)])
            fitsK.append(permute(gparams(g, 3), o))
best = {ct: Ks[int(np.argmin([s["bic"] for s in v]))] for ct, v in sweep.items()}
bestAic = Ks[int(np.argmin([s["aic"] for s in sweep["full"]]))]
dump("bic", {"K": Ks, "sweep": sweep, "fits": fitsK, "best": best, "bestAic": bestAic})
print(f"  BIC best K: {best}; AIC best K (full): {bestAic}")
print("  full:", [(s["ll"], s["bic"], s["aic"]) for s in sweep["full"]])

# ---------------------------------------------------------------------------
# Restarts: EM finds local optima (K = 5 on five blobs, random-from-data init)
# ---------------------------------------------------------------------------
C5 = np.array([[-6, 0], [-3, 3.5], [0, 0], [3, 3.5], [6, 0]])
X5, y5 = make_blobs(n_samples=400, centers=C5, cluster_std=0.75, random_state=3)
runs = []
for seed in range(12):
    rr = np.random.default_rng(seed)
    idx = rr.choice(len(X5), 5, replace=False)
    fr = em(X5, np.full(5, 0.2), X5[idx], np.repeat(np.eye(2)[None], 5, 0), 40)
    o = order_by(fr[-1]["mu"], lambda m: (m[0], m[1]))
    g_end, _ = e_step(X5, fr[-1]["w"], fr[-1]["mu"], fr[-1]["cov"])
    runs.append({"seed": seed, "ll": [round(float(f["ll"]), 1) for f in fr],
                 "final": params(fr[-1]["w"][o], fr[-1]["mu"][o], fr[-1]["cov"][o], 3),
                 "ari": ari(y5, g_end.argmax(1))})
finals = [run["ll"][-1] for run in runs]
iBest, iWorst = int(np.argmax(finals)), int(np.argmin(finals))
dump("restarts", {"pts": r(X5), "truth": y5.tolist(), "runs": runs, "best": iBest, "worst": iWorst})
print(f"  restarts final ll: {sorted(finals)}; best seed {iBest} ARI {runs[iBest]['ari']}, worst seed {iWorst} ARI {runs[iWorst]['ari']}")

# ---------------------------------------------------------------------------
# 1D: a three-component mixture and its samples
# ---------------------------------------------------------------------------
M1 = {"w": [0.3, 0.5, 0.2], "mu": [-2.0, 1.5, 5.0], "sd": [0.8, 1.2, 0.6]}
r1 = np.random.default_rng(11)
z1 = r1.choice(3, 600, p=M1["w"])
x1 = r1.normal(np.array(M1["mu"])[z1], np.array(M1["sd"])[z1])
dump("mix1d", {**M1, "x": r(x1, 3), "z": z1.tolist()})

# ---------------------------------------------------------------------------
# Why EM climbs: the lower bound, for a 1D two-component model with only mu_1 free
# ---------------------------------------------------------------------------
B = {"w": [0.5, 0.5], "mu2": 4.0, "sd": [1.0, 1.0]}
rb = np.random.default_rng(5)
zb = rb.choice(2, 200, p=B["w"])
xb = rb.normal(np.where(zb == 0, 0.0, 4.0), 1.0)
grid = np.linspace(-4, 6, 201)


def ll_mu1(m):
    return float(logsumexp(np.column_stack([np.log(0.5) + norm.logpdf(xb, m, 1), np.log(0.5) + norm.logpdf(xb, 4, 1)]), axis=1).sum())


def resp_mu1(m):
    lj = np.column_stack([np.log(0.5) + norm.logpdf(xb, m, 1), np.log(0.5) + norm.logpdf(xb, 4, 1)])
    return np.exp(lj - logsumexp(lj, axis=1)[:, None])


def bound(m_t, m):
    """sum_i sum_k gamma_ik(m_t) log(pi_k N(x_i | theta(m)) / gamma_ik(m_t)): touches log L at m = m_t."""
    g = resp_mu1(m_t)
    lj = np.column_stack([np.log(0.5) + norm.logpdf(xb, m, 1), np.log(0.5) + norm.logpdf(xb, 4, 1)])
    return float((g * (lj - np.log(np.clip(g, 1e-300, 1)))).sum())


m = -3.0
steps = []
for _ in range(7):
    g = resp_mu1(m)
    m_new = float((g[:, 0] * xb).sum() / g[:, 0].sum())
    steps.append({"mu": round(m, 3), "ll": round(ll_mu1(m), 2), "next": round(m_new, 3),
                  "bound": r([bound(m, q) for q in grid], 2)})
    assert ll_mu1(m_new) >= ll_mu1(m) - 1e-9
    m = m_new
dump("bound", {"grid": r(grid, 3), "ll": r([ll_mu1(q) for q in grid], 2), "steps": steps,
               "opt": round(float(grid[np.argmax([ll_mu1(q) for q in grid])]), 2), "x": r(xb, 2)})
print(f"  bound: mu1 path {[s['mu'] for s in steps]}")

# ---------------------------------------------------------------------------
# Real data 1: Old Faithful. Two features, BIC sweep, density surface, anomalies, samples
# ---------------------------------------------------------------------------
rows = list(csv.DictReader(open(RAW / "faithful.csv")))
F = np.array([[float(row["eruptions"]), float(row["waiting"])] for row in rows])
fs = []
for k in range(1, 7):
    g = GaussianMixture(k, covariance_type="full", n_init=10, random_state=0).fit(F)
    fs.append({"k": k, "bic": round(float(g.bic(F)), 1), "aic": round(float(g.aic(F)), 1)})
kF = 1 + int(np.argmin([s["bic"] for s in fs]))
gF = GaussianMixture(kF, covariance_type="full", n_init=10, random_state=0).fit(F)
pF = order_by(gF, lambda m: m[0])
gx = np.linspace(1.2, 5.6, 56)
gy = np.linspace(38, 102, 56)
GX, GY = np.meshgrid(gx, gy)
dens = np.exp(gF.score_samples(np.column_stack([GX.ravel(), GY.ravel()]))).reshape(GY.shape)
logd = gF.score_samples(F)
thr = float(np.percentile(logd, 2))
flag = (logd < thr).tolist()
synth, zs = gF.sample(272)
# sample() returns rows grouped by component; shuffle so the animation draws them in random order
sh = np.random.default_rng(1).permutation(272)
inv = np.empty_like(pF)
inv[pF] = np.arange(len(pF))
PF = gF.predict_proba(F)[:, pF]
dump("faithful", {
    "pts": F.tolist(), "sweep": fs, "k": kF, "gmm": permute(gparams(gF, 4), pF),
    "grid": {"x": r(gx, 3), "y": r(gy, 2), "z": r(dens / dens.max(), 4), "peak": float(dens.max())},
    "logd": r(logd, 2), "thr": round(thr, 2), "flag": flag,
    "synth": r(synth[sh], 2), "synthZ": inv[zs[sh]].tolist(),
    "lab": PF.argmax(1).tolist(), "maxp": r(PF.max(1), 3),
    "nUnsure": int((PF.max(1) < 0.9).sum()),
})
print(f"  faithful: BIC {[(s['k'], s['bic']) for s in fs]} -> K={kF}; weights {np.round(gF.weights_[pF], 3).tolist()}; "
      f"means {np.round(gF.means_[pF], 2).tolist()}; flagged {sum(flag)} below log-density {thr:.2f}; unsure {(PF.max(1) < 0.9).sum()}")
print("  flagged points:", F[np.array(flag)].tolist())

# ---------------------------------------------------------------------------
# Real data 2: Iris in 3D (petal length, petal width, sepal length)
# ---------------------------------------------------------------------------
iris = load_iris()
cols = [2, 3, 0]
I3 = iris.data[:, cols]
yI = iris.target
gI = GaussianMixture(3, covariance_type="full", n_init=10, random_state=0).fit(I3)
kI = KMeans(3, n_init=10, random_state=0).fit(I3)
oI = order_by(gI, lambda m: m[0])
oK = order_by(kI.cluster_centers_, lambda m: m[0])
gI4 = GaussianMixture(3, covariance_type="full", n_init=10, random_state=0).fit(iris.data)
kI4 = KMeans(3, n_init=10, random_state=0).fit(iris.data)
dump("iris", {
    "pts": r(I3, 2), "species": yI.tolist(), "names": [str(n) for n in iris.target_names],
    "features": [iris.feature_names[c].replace(" (cm)", "") for c in cols],
    "gmm": permute(gparams(gI, 4), oI), "lab": relabel(gI.predict(I3), oI), "km": relabel(kI.labels_, oK),
    "gmmAri": ari(yI, gI.predict(I3)), "kmAri": ari(yI, kI.labels_),
    "gmmAri4": ari(yI, gI4.predict(iris.data)), "kmAri4": ari(yI, kI4.labels_),
})
print(f"  iris 3 features ARI: gmm {ari(yI, gI.predict(I3))} km {ari(yI, kI.labels_)}; 4 features: gmm {ari(yI, gI4.predict(iris.data))} km {ari(yI, kI4.labels_)}")

# ---------------------------------------------------------------------------
# Limits: the moons. Two Gaussians cut them; ten Gaussians model the density, not the clusters
# ---------------------------------------------------------------------------
moons = {"pts": r(Xm), "truth": ym.tolist()}
for k in [2, 10]:
    g = GaussianMixture(k, covariance_type="full", n_init=5, random_state=0).fit(Xm)
    o = order_by(g, lambda m: (m[0], m[1]))
    moons[f"k{k}"] = {**permute(gparams(g, 3), o), "lab": relabel(g.predict(Xm), o), "ari": ari(ym, g.predict(Xm))}
mb = [GaussianMixture(k, covariance_type="full", n_init=3, random_state=0).fit(Xm).bic(Xm) for k in range(1, 16)]
moons["bestK"] = 1 + int(np.argmin(mb))
moons["synth"] = r(GaussianMixture(10, covariance_type="full", n_init=5, random_state=0).fit(Xm).sample(300)[0][np.random.default_rng(2).permutation(300)])
dump("moons", moons)
print(f"  moons: ARI K=2 {moons['k2']['ari']}, K=10 {moons['k10']['ari']}; BIC-best K {moons['bestK']}")

# ---------------------------------------------------------------------------
# k-means as a limit: the three blobs from the k-Means deck
# ---------------------------------------------------------------------------
kb = KMeans(3, n_init=10, random_state=0).fit(X3)
dump("blobs3", {"pts": r(X3), "truth": y3.tolist(), "C": r(kb.cluster_centers_), "km": kb.labels_.tolist()})
