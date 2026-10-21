"""Generate the data behind every chart in the k-Means Clustering deck.

Run from the deck folder:

    uv run --no-project --with scikit-learn==1.9.1 --with pillow python scripts/make_data.py

Writes small JSON files into data/ and quantized images into data/img/.
Every number on the slides comes from here, with fixed seeds, so rerunning
reproduces the deck exactly. The slide text quotes several of these numbers.

Real datasets:
  * Wholesale customers (UCI id 292, Cardoso 2014, CC BY 4.0), stored in data/raw/.
  * scikit-learn's bundled sample image china.jpg and wine dataset.
  * California housing block-group coordinates (fetch_california_housing; cached
    in ~/scikit_learn_data after the first download).
"""

import csv
import json
from pathlib import Path

import numpy as np
from PIL import Image
from sklearn.cluster import KMeans
from sklearn.datasets import (
    fetch_california_housing,
    load_sample_image,
    load_wine,
    make_blobs,
    make_moons,
)
from sklearn.metrics import adjusted_rand_score, silhouette_samples, silhouette_score
from sklearn.preprocessing import StandardScaler

DECK = Path(__file__).resolve().parent.parent
OUT = DECK / "data"
IMG = OUT / "img"
IMG.mkdir(parents=True, exist_ok=True)


def r(a, k=3):
    return np.round(np.asarray(a, dtype=float), k).tolist()


def dump(name, obj):
    (OUT / f"{name}.json").write_text(json.dumps(obj, separators=(",", ":")))
    print(f"wrote data/{name}.json")


def inertia(X, C, lab):
    return float(((X - C[lab]) ** 2).sum())


def assign(X, C):
    return ((X[:, None, :] - C[None]) ** 2).sum(-1).argmin(1)


def lloyd(X, C0, max_iter=100):
    """Plain Lloyd's algorithm, recording every half-step.

    Frames: init (centroids only) -> assign -> update -> assign -> ... and the
    last frame is the assign step whose labels did not change (converged).
    """
    C = np.array(C0, dtype=float)
    frames = [{"phase": "init", "c": C.copy(), "lab": None, "J": None}]
    lab = None
    for _ in range(max_iter):
        new = assign(X, C)
        frames.append({"phase": "assign", "c": C.copy(), "lab": new, "J": inertia(X, C, new)})
        if lab is not None and np.array_equal(new, lab):
            break
        lab = new
        C = np.array([X[lab == k].mean(0) if (lab == k).any() else C[k] for k in range(len(C))])
        frames.append({"phase": "update", "c": C.copy(), "lab": lab, "J": inertia(X, C, lab)})
    return frames


def run_json(X, frames, k=3):
    return {
        "pts": r(X, k),
        "frames": [
            {
                "phase": f["phase"],
                "c": r(f["c"], k),
                "lab": None if f["lab"] is None else np.asarray(f["lab"]).tolist(),
                "J": None if f["J"] is None else round(f["J"], 1),
            }
            for f in frames
        ],
    }


def final_run(X, C, lab, k=3):
    return {"pts": r(X, k), "frames": [{"phase": "assign", "c": r(C, k), "lab": np.asarray(lab).tolist(), "J": round(inertia(X, C, lab), 1)}]}


# ---------------------------------------------------------------------------
# blobs3: the running example (title, two groupings, Lloyd animation)
# ---------------------------------------------------------------------------
X3, y3 = make_blobs(n_samples=300, centers=3, cluster_std=0.8, random_state=0)
km3 = KMeans(3, n_init=10, random_state=0).fit(X3)
best3 = km3.inertia_

# Pick a random initialization (three data points) that reaches the best
# solution in 4-6 iterations (few enough to click through) and starts as badly
# as possible (the most to watch).
best_seed, worst_start = None, 0
for s in range(400):
    idx = np.random.default_rng(s).choice(len(X3), 3, replace=False)
    fr = lloyd(X3, X3[idx])
    if fr[-1]["J"] <= best3 * 1.0001 and 9 <= len(fr) <= 13 and fr[1]["J"] > worst_start:
        best_seed, worst_start = s, fr[1]["J"]
idx = np.random.default_rng(best_seed).choice(len(X3), 3, replace=False)
frames3 = lloyd(X3, X3[idx])
assert best_seed is not None and frames3[-1]["J"] <= best3 * 1.0001
Js = [f["J"] for f in frames3 if f["J"] is not None]
assert all(a >= b - 1e-9 for a, b in zip(Js, Js[1:])), "J must never increase"
blobs3 = run_json(X3, frames3)
blobs3["seed"] = best_seed
blobs3["k2"] = KMeans(2, n_init=10, random_state=0).fit_predict(X3).tolist()
blobs3["sil"] = round(float(silhouette_score(X3, km3.labels_)), 3)
# a boundary point for the silhouette geometry slide
s3 = silhouette_samples(X3, frames3[-1]["lab"])
probe = int(np.argmin(np.abs(s3 - 0.25)))
blobs3["probe"] = probe
blobs3["probeSil"] = round(float(s3[probe]), 3)
dump("blobs3", blobs3)
print(f"  blobs3: seed {best_seed}, {len(frames3)} frames, J {Js[0]:.1f} -> {Js[-1]:.1f}")

# ---------------------------------------------------------------------------
# Worked example by hand: 6 points, K = 2
# ---------------------------------------------------------------------------
H = np.array([[1, 1], [1.5, 2], [3, 3.5], [5, 7], [3.5, 5], [4.5, 5]], dtype=float)
hf = lloyd(H, H[[0, 3]])
D0 = np.sqrt(((H[:, None] - H[[0, 3]][None]) ** 2).sum(-1))
dump("hand", {
    "pts": r(H, 2),
    "c0": r(H[[0, 3]], 2),
    "d0": r(D0, 2),
    "lab0": hf[1]["lab"].tolist(),
    "J0": round(hf[1]["J"], 2),
    "c1": r(hf[2]["c"], 3),
    "J1": round(hf[2]["J"], 2),
    "lab1": hf[3]["lab"].tolist(),
    "J2": round(hf[3]["J"], 2),
    "frames": run_json(H, hf, 3)["frames"],
})
print(f"  hand: J {hf[1]['J']:.2f} -> {hf[2]['J']:.2f} -> {hf[3]['J']:.2f}, {len(hf)} frames")

# ---------------------------------------------------------------------------
# blobs6: initialization, k-means++, choosing K
# ---------------------------------------------------------------------------
C6 = np.array([(-6, 4), (-1, 6.5), (5, 5), (-5, -3), (1, -1), (6, -4)], dtype=float)
X6, _ = make_blobs(n_samples=600, centers=C6, cluster_std=1.0, random_state=1)
best6 = KMeans(6, n_init=50, random_state=0).fit(X6).inertia_

runs_random, runs_pp = [], []
for s in range(50):
    a = KMeans(6, init="random", n_init=1, random_state=s).fit(X6)
    b = KMeans(6, init="k-means++", n_init=1, random_state=s).fit(X6)
    runs_random.append((a.inertia_, a.n_iter_))
    runs_pp.append((b.inertia_, b.n_iter_))
Jr = np.array([j for j, _ in runs_random])
Jp = np.array([j for j, _ in runs_pp])

# three illustrative random starts: one good, two stuck
showcase = []
for s in range(200):
    idx = np.random.default_rng(1000 + s).choice(len(X6), 6, replace=False)
    fr = lloyd(X6, X6[idx])
    showcase.append((fr[-1]["J"], s, fr))
showcase.sort(key=lambda t: t[0])
good = showcase[0]
bad = [t for t in showcase if t[0] > best6 * 1.5]
picks = [good, bad[len(bad) // 3], bad[-1]]

# pure D^2 seeding, step by step
rng = np.random.default_rng(7)
chosen = [int(rng.integers(len(X6)))]
for _ in range(5):
    d2 = ((X6[:, None] - X6[chosen][None]) ** 2).sum(-1).min(1)
    chosen.append(int(rng.choice(len(X6), p=d2 / d2.sum())))

sweep = []
for k in range(1, 9):
    km = KMeans(k, n_init=10, random_state=0).fit(X6)
    sweep.append({
        "k": k,
        "J": round(km.inertia_, 1),
        "sil": None if k == 1 else round(float(silhouette_score(X6, km.labels_)), 3),
        "c": r(km.cluster_centers_),
        "lab": km.labels_.tolist(),
    })

knife = {}
for k in (4, 6, 8):
    lab = sweep[k - 1]["lab"]
    s = silhouette_samples(X6, lab)
    groups = []
    for c in range(k):
        v = np.sort(s[np.array(lab) == c])[::-1]
        groups.append(r(v, 3))
    knife[k] = {"groups": groups, "mean": round(float(s.mean()), 3), "neg": int((s < 0).sum())}

dump("blobs6", {
    "pts": r(X6),
    "best": round(best6, 1),
    "random": {"J": r(Jr, 1), "iter": [int(i) for _, i in runs_random]},
    "pp": {"J": r(Jp, 1), "iter": [int(i) for _, i in runs_pp]},
    "stuckRandom": int((Jr > best6 * 1.01).sum()),
    "stuckPP": int((Jp > best6 * 1.01).sum()),
    "showcase": [run_json(X6, fr)["frames"][-1] for _, _, fr in picks],
    "kpp": chosen,
    "sweep": sweep,
    "knife": knife,
})
print(f"  blobs6: best {best6:.1f}; stuck random {(Jr > best6 * 1.01).sum()}/50, k-means++ {(Jp > best6 * 1.01).sum()}/50")
print(f"  blobs6 showcase J: {[round(t[0], 1) for t in picks]}")
print(f"  knife: { {k: (v['mean'], v['neg']) for k, v in knife.items()} }")

# ---------------------------------------------------------------------------
# Scaling: two wine features in very different units
# ---------------------------------------------------------------------------
wine = load_wine()
fi = [wine.feature_names.index("flavanoids"), wine.feature_names.index("proline")]
W = wine.data[:, fi]
Ws = StandardScaler().fit_transform(W)
lab_raw = KMeans(3, n_init=10, random_state=0).fit_predict(W)
lab_std = KMeans(3, n_init=10, random_state=0).fit_predict(Ws)
dump("wine", {
    "raw": r(W, 3),
    "std": r(Ws, 3),
    "labRaw": lab_raw.tolist(),
    "labStd": lab_std.tolist(),
    "truth": wine.target.tolist(),
    "ariRaw": round(adjusted_rand_score(wine.target, lab_raw), 2),
    "ariStd": round(adjusted_rand_score(wine.target, lab_std), 2),
    "range": {"flav": r([W[:, 0].min(), W[:, 0].max()], 2), "proline": r([W[:, 1].min(), W[:, 1].max()], 0)},
})

# ---------------------------------------------------------------------------
# Failure gallery: moons, unequal, aniso, blobs_outliers
# ---------------------------------------------------------------------------
fails = {}
Xm, ym = make_moons(300, noise=0.06, random_state=0)
Xu, yu = make_blobs(n_samples=[350, 60, 30], centers=[(-4, 0), (3, 2.5), (3.2, -2)], cluster_std=[2.0, 0.5, 0.4], random_state=170)
rng = np.random.default_rng(0)
# two parallel, stretched ellipses (the plan's [[3,1.8],[1.8,1]] is not a valid covariance)
A1 = rng.multivariate_normal([0, 0], [[3, 1.6], [1.6, 1]], 150)
A2 = rng.multivariate_normal([1.2, -2.4], [[3, 1.6], [1.6, 1]], 150)
Xa, ya = np.vstack([A1, A2]), np.r_[np.zeros(150, int), np.ones(150, int)]
out = np.random.default_rng(3).uniform(X3.min(0) - 6, X3.max(0) + 6, (15, 2))
Xo, yo = np.vstack([X3, out]), np.r_[y3, np.full(15, 3)]
for name, X, y, k in [("moons", Xm, ym, 2), ("unequal", Xu, yu, 3), ("aniso", Xa, ya, 2), ("outliers", Xo, yo, 4)]:
    km = KMeans(k, n_init=10, random_state=0).fit(X)
    run = final_run(X, km.cluster_centers_, km.labels_)
    run["truth"] = y.tolist()
    run["ari"] = round(adjusted_rand_score(y, km.labels_), 2)
    fails[name] = run
dump("fails", fails)
print(f"  fails ARI: { {k: v['ari'] for k, v in fails.items()} }")

# ---------------------------------------------------------------------------
# Real data 1: Wholesale customers (annual spend, monetary units, 6 categories)
# ---------------------------------------------------------------------------
rows = list(csv.reader(open(OUT / "raw" / "wholesale_customers.csv")))
cols = rows[0][2:]
A = np.array(rows[1:], dtype=float)
channel = A[:, 0].astype(int)  # 1 = Horeca (hotel/restaurant/cafe), 2 = Retail
S = A[:, 2:]
L = np.log1p(S)
Z = StandardScaler().fit_transform(L)
wsweep = []
for k in range(2, 9):
    km = KMeans(k, n_init=10, random_state=0).fit(Z)
    wsweep.append({"k": k, "J": round(km.inertia_, 1), "sil": round(float(silhouette_score(Z, km.labels_)), 3)})
k2 = KMeans(2, n_init=10, random_state=0).fit_predict(Z)
cross2 = [[int(((k2 == c) & (channel == v)).sum()) for v in (1, 2)] for c in range(2)]
agree = max(cross2[0][0] + cross2[1][1], cross2[0][1] + cross2[1][0]) / len(Z)
raw2 = KMeans(2, n_init=10, random_state=0).fit_predict(S)

km4 = KMeans(4, n_init=10, random_state=0).fit(Z)
lab4 = km4.labels_
# order clusters by total median spend so colors are stable and readable
order = np.argsort([np.median(S[lab4 == c].sum(1)) for c in range(4)])
remap = np.empty(4, int)
remap[order] = np.arange(4)
lab4 = remap[lab4]
stab = [adjusted_rand_score(lab4, KMeans(4, n_init=1, random_state=s).fit_predict(Z)) for s in range(20)]
profiles = []
for c in range(4):
    m = lab4 == c
    profiles.append({
        "n": int(m.sum()),
        "median": r(np.median(S[m], 0), 0),
        "z": r(Z[m].mean(0), 2),
        "horeca": int((channel[m] == 1).sum()),
        "retail": int((channel[m] == 2).sum()),
    })
dump("wholesale", {
    "cols": cols,
    "raw": r(S, 0),
    "log": r(L, 3),
    "sweep": wsweep,
    "cross2": cross2,
    "agree": round(agree, 3),
    "raw2Sizes": np.bincount(raw2).tolist(),
    "std2Sizes": np.bincount(k2).tolist(),
    "lab4": lab4.tolist(),
    "channel": channel.tolist(),
    "profiles": profiles,
    "stability": {"min": round(min(stab), 2), "median": round(float(np.median(stab)), 2)},
})
print(f"  wholesale: K=2 agrees with Channel on {agree:.1%}; cross {cross2}; raw sizes {np.bincount(raw2)}")
print(f"  wholesale K=4 sizes {[p['n'] for p in profiles]}, stability ARI min {min(stab):.2f}")

# ---------------------------------------------------------------------------
# Real data 2: color quantization of china.jpg
# ---------------------------------------------------------------------------
img = load_sample_image("china.jpg")
small = np.asarray(Image.fromarray(img).resize((480, 320), Image.LANCZOS))
Image.fromarray(small).save(IMG / "china_orig.png", optimize=True)
P = small.reshape(-1, 3).astype(float) / 255
fit_idx = np.random.default_rng(0).choice(len(P), 5000, replace=False)
quant = {}
for k in (2, 4, 8, 16, 32):
    km = KMeans(k, n_init=4, random_state=0).fit(P[fit_idx])
    lab = km.predict(P)
    Q = (km.cluster_centers_[lab].reshape(small.shape) * 255).round().astype(np.uint8)
    Image.fromarray(Q).save(IMG / f"china_k{k}.png", optimize=True)
    mse = float(((km.cluster_centers_[lab] - P) ** 2).sum(1).mean())
    quant[k] = {"palette": r(km.cluster_centers_ * 255, 0), "counts": np.bincount(lab, minlength=k).tolist(), "mse": round(mse * 1e4, 1)}
cloud_idx = np.random.default_rng(1).choice(len(P), 2500, replace=False)
km8 = KMeans(8, n_init=4, random_state=0).fit(P[fit_idx])
dump("pixels", {
    "rgb": np.round(P[cloud_idx] * 255).astype(int).tolist(),
    "lab8": km8.predict(P[cloud_idx]).tolist(),
    "c8": r(km8.cluster_centers_ * 255, 0),
    "quant": quant,
    "size": list(small.shape[:2]),
    "nPixels": int(len(P)),
})
print(f"  pixels: {len(P)} pixels; mse x1e4 { {k: v['mse'] for k, v in quant.items()} }")

# ---------------------------------------------------------------------------
# Real data 3: California block groups -> 8 depot locations
# ---------------------------------------------------------------------------
cal = fetch_california_housing()
lat, lon = cal.data[:, 6], cal.data[:, 7]
lat0 = np.deg2rad(lat.mean())
G = np.c_[(lon - lon.mean()) * 111.32 * np.cos(lat0), (lat - lat.mean()) * 110.57]  # km, east/north
ref = KMeans(8, n_init=10, random_state=0).fit(G)
# most random starts get stuck here; use the first seed that reaches the best solution
cal_seed = 0
while True:
    start = G[np.random.default_rng(cal_seed).choice(len(G), 8, replace=False)]
    gf = lloyd(G, start)
    if gf[-1]["J"] <= ref.inertia_ * 1.001:
        break
    cal_seed += 1
show = np.random.default_rng(5).choice(len(G), 3000, replace=False)
cal_frames = []
for f in gf:
    if f["phase"] == "assign" and f is not gf[-1]:
        continue
    cal_frames.append({"c": r(f["c"], 1), "J": None if f["J"] is None else round(f["J"] / len(G), 0)})
centers_ll = np.c_[gf[-1]["c"][:, 0] / (111.32 * np.cos(lat0)) + lon.mean(), gf[-1]["c"][:, 1] / 110.57 + lat.mean()]
dump("california", {
    "pts": r(G[show], 1),
    "lab": gf[-1]["lab"][show].tolist(),
    "frames": cal_frames,
    "sizes": np.bincount(gf[-1]["lab"], minlength=8).tolist(),
    "n": int(len(G)),
    "centersLatLon": r(centers_ll, 2),
    "meanDistKm": round(float(np.sqrt(((G - gf[-1]["c"][gf[-1]["lab"]]) ** 2).sum(1)).mean()), 0),
    "sklearnJ": round(ref.inertia_ / len(G), 0),
    "seed": cal_seed,
})
print(f"  california: {len(cal_frames)} frames; mean dist {np.sqrt(((G - gf[-1]['c'][gf[-1]['lab']]) ** 2).sum(1)).mean():.0f} km; centers {np.round(centers_ll, 2).tolist()}")
print(f"  california J/n ours {gf[-1]['J'] / len(G):.0f} vs sklearn n_init=10 {ref.inertia_ / len(G):.0f}")
