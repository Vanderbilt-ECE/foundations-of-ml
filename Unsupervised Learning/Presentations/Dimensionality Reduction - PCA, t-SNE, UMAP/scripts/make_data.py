"""Generate the data behind every chart in the Dimensionality Reduction deck.

Run from the deck folder:

    uv run --no-project --with scikit-learn==1.9.1 --with scipy --with umap-learn==0.5.12 python scripts/make_data.py

Writes small JSON files into data/. Every number on the slides comes from here,
with fixed seeds, so rerunning reproduces the deck exactly.

The opening slide reuses the Gaussian Mixture Models deck's running example
(../Gaussian Mixture Models/data/em.json), lifted onto a tilted plane in 3D,
so the hand-off between decks shows the same points.

t-SNE is written out by hand below (numpy, exact gradient) for the small live
demo, mirroring the JavaScript version in utils/tsne.ts; its final KL divergence
is checked against sklearn's exact TSNE on the same points.

Datasets: all ship with scikit-learn or are generated.
  * Digits: 1797 handwritten digits, 8x8 pixels, values 0-16 (UCI optdigits).
  * Wine: 178 wines, 13 chemical measurements, 3 cultivars.
  * Swiss roll: make_swiss_roll.
  * Worked example: the 10 points from Lindsay Smith's "A tutorial on
    Principal Components Analysis" (2002).
"""

import json
import time
import warnings
from pathlib import Path

import numpy as np
import umap
from scipy.linalg import orthogonal_procrustes
from scipy.spatial.distance import pdist, squareform
from sklearn.cluster import KMeans
from sklearn.datasets import load_digits, load_wine, make_swiss_roll
from sklearn.decomposition import PCA
from sklearn.linear_model import LogisticRegression
from sklearn.manifold import TSNE, trustworthiness
from sklearn.metrics import adjusted_rand_score
from sklearn.mixture import GaussianMixture
from sklearn.model_selection import cross_val_score, train_test_split
from sklearn.pipeline import make_pipeline
from sklearn.preprocessing import StandardScaler

warnings.filterwarnings("ignore")

DECK = Path(__file__).resolve().parent.parent
OUT = DECK / "data"
GMM = DECK.parent / "Gaussian Mixture Models" / "data" / "em.json"


def r(a, k=3):
    return np.round(np.asarray(a, dtype=float), k).tolist()


def dump(name, obj):
    (OUT / f"{name}.json").write_text(json.dumps(obj, separators=(",", ":")))
    print(f"wrote data/{name}.json  ({(OUT / f'{name}.json').stat().st_size / 1024:.0f} KB)")


def ari(a, b):
    return round(float(adjusted_rand_score(a, b)), 2)


def norm2d(E):
    """Center a 2D embedding and scale it so the largest |coordinate| is 1."""
    E = E - E.mean(0)
    return E / np.abs(E).max()


def align(E, ref):
    """Rotate/reflect a normalized embedding onto ref (orthogonal Procrustes), so tweens between maps don't spin."""
    R, _ = orthogonal_procrustes(E, ref)
    return norm2d(E @ R)


def sign_fix(V):
    """Flip each principal direction (row) so its largest-|.| entry is positive: a fixed sign convention."""
    s = np.sign(V[np.arange(len(V)), np.abs(V).argmax(1)])
    return V * s[:, None]


def enc(img):
    """An 8x8 digit (values 0-16) as a 64-character string, one base-17 digit per pixel: '0'-'9' then 'a'-'g'."""
    return "".join("0123456789abcdefg"[int(v)] for v in img)


# --------------------------------------------------------------------------------------------
# Opening: GMM's running example, three numbers per point, lying near a tilted plane
# --------------------------------------------------------------------------------------------
em = json.loads(GMM.read_text())
P2 = np.array(em["pts"])
e1 = np.array([0.8, 0.2, 0.55]); e1 /= np.linalg.norm(e1)
e2 = np.array([-0.3, 0.9, 0.3]); e2 -= (e2 @ e1) * e1; e2 /= np.linalg.norm(e2)
nrm = np.cross(e1, e2)
rs = np.random.default_rng(3)
X3 = P2[:, :1] * e1 + P2[:, 1:] * e2 + 0.15 * rs.standard_normal((len(P2), 1)) * nrm
p3 = PCA(3).fit(X3)
V3 = sign_fix(p3.components_)
Z3 = (X3 - p3.mean_) @ V3[:2].T
dump("teaser", {
    "pts": r(X3), "truth": em["truth"], "mean": r(p3.mean_), "V": r(V3, 4),
    "sd": r(np.sqrt(p3.explained_variance_)), "evr": r(p3.explained_variance_ratio_, 4), "Z": r(Z3),
})

# --------------------------------------------------------------------------------------------
# Projection demo: a correlated 2D cloud (also used, un-centered, for the "PCA is a rotation" steps)
# --------------------------------------------------------------------------------------------
rs = np.random.default_rng(7)
th = np.deg2rad(32)
Rm = np.array([[np.cos(th), -np.sin(th)], [np.sin(th), np.cos(th)]])
Xd = rs.standard_normal((48, 2)) * [1.7, 0.55] @ Rm.T
Xd -= Xd.mean(0)
Sd = np.cov(Xd.T)
lam, vec = np.linalg.eigh(Sd)
dump("drag", {
    "pts": r(Xd), "S": r(Sd, 4), "lam": r(lam[::-1], 4), "v1": r(sign_fix(vec[:, ::-1].T)[0], 4),
    "offset": [3.2, 2.1],  # where the raw (un-centered) cloud sits on the rotation slide
})

# --------------------------------------------------------------------------------------------
# Worked example (Lindsay Smith 2002)
# --------------------------------------------------------------------------------------------
W = np.array([[2.5, 2.4], [0.5, 0.7], [2.2, 2.9], [1.9, 2.2], [3.1, 3.0],
              [2.3, 2.7], [2.0, 1.6], [1.0, 1.1], [1.5, 1.6], [1.1, 0.9]])
Sw = np.cov(W.T)
lw, vw = np.linalg.eigh(Sw)
lw, vw = lw[::-1], sign_fix(vw[:, ::-1].T)
zw = (W - W.mean(0)) @ vw[0]
assert np.allclose(np.round(lw, 3), [1.284, 0.049]) and np.allclose(np.round(vw[0], 3), [0.678, 0.735])
dump("worked", {
    "pts": r(W, 2), "mean": r(W.mean(0)), "S": r(Sw, 3), "lam": r(lw, 3), "V": r(vw, 3),
    "evr": round(float(lw[0] / lw.sum()), 4), "z": r(zw), "solver": PCA(1).fit(W)._fit_svd_solver,
})

# --------------------------------------------------------------------------------------------
# Wine: why to standardize before PCA
# --------------------------------------------------------------------------------------------
wine = load_wine()
Xw, yw = wine.data, wine.target
wout = {"features": [f.replace("_", " ").replace("od280/od315 of diluted wines", "OD280/OD315") for f in wine.feature_names],
        "y": yw.tolist(), "sd": r(Xw.std(0, ddof=1), 2)}
for key, Xs in [("raw", Xw), ("std", StandardScaler().fit_transform(Xw))]:
    p = PCA(2).fit(Xs)
    V = sign_fix(p.components_)
    wout[key] = {"Z": r(norm2d((Xs - p.mean_) @ V.T)), "load": r(V, 3), "evr": r(p.explained_variance_ratio_, 3)}
dump("wine", wout)

# --------------------------------------------------------------------------------------------
# Digits: PCA, t-SNE, UMAP
# --------------------------------------------------------------------------------------------
dg = load_digits()
X, y = dg.data, dg.target
n = len(X)
pca = PCA().fit(X)
assert pca._fit_svd_solver == "covariance_eigh"  # tall and skinny: sklearn forms the 64x64 covariance and eigendecomposes it
Vd = sign_fix(pca.components_)
Zd = (X - pca.mean_) @ Vd.T
evr = pca.explained_variance_ratio_
cum = np.cumsum(evr)
k_at = {str(t): int(np.searchsorted(cum, t) + 1) for t in (0.5, 0.8, 0.9, 0.95, 0.99)}
assert PCA(0.95).fit(X).n_components_ == k_at["0.95"]

t0 = time.perf_counter(); PCA(2).fit_transform(X); t_pca = time.perf_counter() - t0
E_pca = norm2d(Zd[:, :2])
t0 = time.perf_counter(); E_tsne = TSNE(perplexity=30, random_state=0, init="pca").fit_transform(X); t_tsne = time.perf_counter() - t0
t0 = time.perf_counter(); E_umap = umap.UMAP(random_state=0).fit_transform(X); t_umap = time.perf_counter() - t0
E_tsne = align(norm2d(E_tsne), E_pca)
E_umap = align(norm2d(E_umap), E_tsne)
trust = {k: round(float(trustworthiness(X, E, n_neighbors=10)), 3) for k, E in [("pca", E_pca), ("tsne", E_tsne), ("umap", E_umap)]}

# how well do k-means clusters match the true digits, run on different representations
km = lambda Z: KMeans(10, n_init=10, random_state=0).fit_predict(Z)
Z95 = PCA(k_at["0.95"]).fit_transform(X)
pipe = {
    "raw": ari(y, km(X)), "pca2": ari(y, km(E_pca)), "pca95": ari(y, km(Z95)),
    "tsne": ari(y, km(E_tsne)), "umap": ari(y, km(E_umap)),
    "gmm_pca95": ari(y, GaussianMixture(10, covariance_type="full", n_init=3, random_state=0).fit_predict(Z95)),
    "k95": k_at["0.95"],
}

# a few digits to rebuild on the reconstruction slide: one clean example of each of 0, 2, 3, 4, 7, 8
picks = [int(np.flatnonzero(y == d)[0]) for d in (0, 2, 3, 4, 7, 8)]

dump("digits", {
    "img": [enc(x) for x in X], "y": y.tolist(),
    "mean": r(pca.mean_), "V": r(Vd, 4), "evr": r(evr, 5), "cum": r(cum, 4), "kAt": k_at,
    "lam": r(pca.explained_variance_, 3), "picks": picks,
    "emb": {"pca": r(E_pca), "tsne": r(E_tsne), "umap": r(E_umap)},
    "time": {"pca": round(t_pca * 1000, 1), "tsne": round(t_tsne, 2), "umap": round(t_umap, 2)},
    "trust": trust, "ari": pipe,
})

# --------------------------------------------------------------------------------------------
# Denoising: fit PCA on clean training digits, project noisy test digits
# --------------------------------------------------------------------------------------------
Xtr, Xte = train_test_split(X, test_size=300, random_state=0)
pd_ = PCA().fit(Xtr)
Vdn = sign_fix(pd_.components_)
rs = np.random.default_rng(1)
Xn = np.clip(Xte + rs.normal(0, 4, Xte.shape), 0, 16)
mse = []
for k in range(65):
    Zk = (Xn - pd_.mean_) @ Vdn[:k].T
    Xh = pd_.mean_ + Zk @ Vdn[:k]
    mse.append(float(((Xh - Xte) ** 2).mean()))
mse = np.array(mse)
dump("denoise", {
    "clean": [enc(x) for x in Xte[:8]], "noisy": r(Xn, 1), "mean": r(pd_.mean_), "V": r(Vdn, 4),
    "mse": r(mse, 3), "best": int(mse.argmin()), "noisyMse": round(float(((Xn - Xte) ** 2).mean()), 2),
})

# --------------------------------------------------------------------------------------------
# PCA before a classifier: accuracy and fit time against k
# --------------------------------------------------------------------------------------------
ks = [1, 2, 3, 4, 5, 6, 8, 10, 12, 15, 20, 25, 30, 40, 50, 64]
acc, sec = [], []
for k in ks:
    model = make_pipeline(StandardScaler(), PCA(k), LogisticRegression(max_iter=5000))
    t0 = time.perf_counter()
    acc.append(float(cross_val_score(model, X, y, cv=5).mean()))
    sec.append(time.perf_counter() - t0)
dump("clf", {"k": ks, "acc": r(acc, 4), "sec": r(sec, 3)})

# --------------------------------------------------------------------------------------------
# t-SNE: perplexity sweep and seeds on digits
# --------------------------------------------------------------------------------------------
perps = [2, 5, 15, 30, 50, 100]
tsne_p = {}
for p in perps:
    E = E_tsne if p == 30 else align(norm2d(TSNE(perplexity=p, random_state=0, init="pca").fit_transform(X)), E_tsne)
    tsne_p[str(p)] = r(E)
seeds = [r(align(norm2d(TSNE(perplexity=30, random_state=s, init="random").fit_transform(X)), E_tsne)) for s in (1, 2, 3)]
dump("perplexity", {"perps": perps, "emb": tsne_p, "seeds": seeds})

# --------------------------------------------------------------------------------------------
# How not to read t-SNE (after Wattenberg, Viégas & Johnson, Distill 2016)
# --------------------------------------------------------------------------------------------
rs = np.random.default_rng(5)
# (a) a tight and a diffuse cluster: same size in t-SNE
A = np.vstack([rs.normal(0, 1, (150, 2)), rs.normal(0, 10, (150, 2)) + [45, 0]])
# (b) three clusters, gaps 10 and 50 along a line: t-SNE evens the gaps out
B = np.vstack([rs.normal(0, 1, (100, 2)) + [c, 0] for c in (0, 10, 60)])
# (c) pure noise in 30-D: at low perplexity it clumps into fake clusters
C = rs.normal(0, 1, (300, 30))
tsn = lambda Z, p: norm2d(TSNE(perplexity=p, random_state=0, init="random").fit_transform(Z))
dump("pitfalls", {
    "size": {"raw": r(norm2d(A)), "emb": r(tsn(A, 30)), "lab": [0] * 150 + [1] * 150},
    "gap": {"raw": r(norm2d(B)), "emb": r(tsn(B, 30)), "lab": [0] * 100 + [1] * 100 + [2] * 100},
    "noise": {"raw": r(norm2d(C[:, :2])), "emb": r(tsn(C, 3)), "lab": [8] * 300},
})

# --------------------------------------------------------------------------------------------
# Live t-SNE demo: 400 digits. Exact t-SNE by hand, same recipe as utils/tsne.ts
# --------------------------------------------------------------------------------------------
rs = np.random.default_rng(0)
sub = np.sort(rs.choice(n, 400, replace=False))
Xs = X[sub]


def cond_p(D2, perp, tol=1e-5, steps=60):
    """Row-wise Gaussian affinities p_{j|i} with each sigma_i chosen by bisection so 2^H(P_i) = perplexity."""
    m = len(D2)
    P = np.zeros((m, m))
    target = np.log(perp)
    for i in range(m):
        lo, hi, beta = 0.0, np.inf, 1.0
        d = np.delete(D2[i], i)
        for _ in range(steps):
            w = np.exp(-(d - d.min()) * beta)
            s = w.sum()
            H = np.log(s) + beta * (w @ (d - d.min())) / s  # entropy in nats
            if abs(H - target) < tol:
                break
            if H > target:
                lo = beta
                beta = beta * 2 if hi == np.inf else (beta + hi) / 2
            else:
                hi = beta
                beta = (beta + lo) / 2
        P[i, np.arange(m) != i] = w / s
    return P


def tsne_np(Xh, perp=30, iters=1000, seed=0):
    m = len(Xh)
    D2 = squareform(pdist(Xh, "sqeuclidean"))
    P = cond_p(D2, perp)
    P = (P + P.T) / (2 * m)
    P = np.maximum(P, 1e-12)
    Y = np.random.default_rng(seed).normal(0, 1e-4, (m, 2))
    upd = np.zeros_like(Y); gains = np.ones_like(Y)
    lr = max(m / 12 / 4, 50)
    for it in range(iters):
        ex = 12.0 if it < 250 else 1.0
        mom = 0.5 if it < 250 else 0.8
        num = 1 / (1 + squareform(pdist(Y, "sqeuclidean")))
        np.fill_diagonal(num, 0)
        Q = np.maximum(num / num.sum(), 1e-12)
        PQ = (ex * P - Q) * num
        G = 4 * (np.diag(PQ.sum(1)) - PQ) @ Y
        gains = np.where(np.sign(G) != np.sign(upd), gains + 0.2, gains * 0.8).clip(0.01)
        upd = mom * upd - lr * gains * G
        Y = Y + upd
    num = 1 / (1 + squareform(pdist(Y, "sqeuclidean"))); np.fill_diagonal(num, 0)
    Q = np.maximum(num / num.sum(), 1e-12)
    return Y, float((P * np.log(P / Q)).sum())


Yh, kl_hand = tsne_np(Xs)
sk = TSNE(perplexity=30, method="exact", init="random", random_state=0).fit(Xs)
assert abs(kl_hand - sk.kl_divergence_) / sk.kl_divergence_ < 0.15, (kl_hand, sk.kl_divergence_)
dump("tsnelive", {"idx": sub.tolist(), "final": r(norm2d(Yh)), "kl": round(kl_hand, 3), "klSk": round(float(sk.kl_divergence_), 3)})

# --------------------------------------------------------------------------------------------
# UMAP: layout snapshots over epochs, and the n_neighbors x min_dist grid
# --------------------------------------------------------------------------------------------
epochs = [0, 5, 15, 40, 100, 200]
u = umap.UMAP(n_epochs=epochs, random_state=0).fit(X)
snaps = [align(norm2d(E), E_umap) for E in u.embedding_list_]
dump("umapepochs", {"epochs": epochs, "emb": [r(E) for E in snaps]})

NN = [5, 15, 50, 200]
MD = [0.0, 0.1, 0.5, 0.99]
rs = np.random.default_rng(2)
gsub = np.sort(rs.choice(n, 900, replace=False))
grid = {}
for a in NN:
    for b in MD:
        E = umap.UMAP(n_neighbors=a, min_dist=b, random_state=0).fit_transform(X)
        grid[f"{a}_{b:g}"] = r(align(norm2d(E), E_umap)[gsub])  # key "15_0" for min_dist 0.0, as JavaScript prints it
dump("umapgrid", {"nn": NN, "md": MD, "idx": gsub.tolist(), "emb": grid})

# --------------------------------------------------------------------------------------------
# Swiss roll: three ways
# --------------------------------------------------------------------------------------------
Xr, tr = make_swiss_roll(900, noise=0.15, random_state=0)
Er_pca = norm2d(PCA(2).fit_transform(Xr))
Er_tsne = norm2d(TSNE(perplexity=30, random_state=0).fit_transform(Xr))
Er_umap = norm2d(umap.UMAP(n_neighbors=15, random_state=0).fit_transform(Xr))
arc = 0.5 * (tr * np.sqrt(1 + tr**2) + np.arcsinh(tr))  # length along the roll: the spiral is r = t, so ds = sqrt(1 + t^2) dt
truth = norm2d(np.c_[arc, Xr[:, 1]])
dump("swiss", {
    "pts": r(Xr, 2), "t": r(tr, 2),
    "emb": {"pca": r(Er_pca), "tsne": r(align(Er_tsne, truth)), "umap": r(align(Er_umap, truth)), "truth": r(truth)},
    "trust": {k: round(float(trustworthiness(Xr, E, n_neighbors=10)), 3) for k, E in [("pca", Er_pca), ("tsne", Er_tsne), ("umap", Er_umap)]},
})

print("digits k at", k_at, "trust", trust, "ari", pipe)
print("t-SNE live KL hand", round(kl_hand, 3), "sklearn", round(float(sk.kl_divergence_), 3))
