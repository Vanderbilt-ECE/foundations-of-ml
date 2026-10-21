"""Generate the data behind every chart in the Hierarchical and Density-Based Clustering deck.

Run from the deck folder:

    uv run --no-project --with scikit-learn==1.9.1 --with scipy python scripts/make_data.py

Writes small JSON files into data/. Every number on the slides comes from here,
with fixed seeds, so rerunning reproduces the deck exactly.

Shared toy datasets use the same recipes as the k-Means deck (blobs3, moons,
unequal, blobs + outliers), so the hand-off between decks shows the same points.

Scoring convention: noise is not a group. Before computing ARI, every point
labeled -1 (DBSCAN/HDBSCAN noise, or a true outlier) becomes its own singleton
cluster. Otherwise all noise points would count as one cluster and a method
could score well by calling a whole sparse cluster "noise".

Real datasets (stored in data/raw/):
  * UCI Zoo (id 111, Forsyth 1990, CC BY 4.0): 101 animals, 16 traits.
  * USGS earthquake catalog, every M4.5+ event in 2024 (public domain):
    https://earthquake.usgs.gov/fdsnws/event/1/query?format=csv&starttime=2024-01-01&endtime=2025-01-01&minmagnitude=4.5
  * Natural Earth 1:110m coastline (public domain), for the maps.
  * California housing block-group coordinates (fetch_california_housing; cached
    in ~/scikit_learn_data after the first download).

The HDBSCAN condensed tree uses sklearn's private _condense_tree, which is why
the scikit-learn version is pinned above.
"""

import csv
import json
import warnings
from pathlib import Path

import numpy as np
from scipy.cluster.hierarchy import dendrogram, fcluster, linkage
from scipy.ndimage import label as cc_label
from sklearn.cluster import DBSCAN, HDBSCAN, AgglomerativeClustering, KMeans
from sklearn.cluster._hdbscan._tree import _condense_tree
from sklearn.datasets import fetch_california_housing, make_blobs, make_circles, make_moons
from sklearn.metrics import adjusted_rand_score
from sklearn.neighbors import KernelDensity, NearestNeighbors

warnings.filterwarnings("ignore", category=FutureWarning)

DECK = Path(__file__).resolve().parent.parent
OUT = DECK / "data"
RAW = OUT / "raw"


def r(a, k=3):
    return np.round(np.asarray(a, dtype=float), k).tolist()


def dump(name, obj):
    (OUT / f"{name}.json").write_text(json.dumps(obj, separators=(",", ":")))
    print(f"wrote data/{name}.json")


def singletons(lab):
    lab = np.asarray(lab).copy()
    m = lab < 0
    lab[m] = lab.max() + 1 + np.arange(m.sum())
    return lab


def ari(y, lab):
    return round(float(adjusted_rand_score(singletons(y), singletons(lab))), 2)


def by_size(lab):
    """Relabel clusters 0, 1, 2, ... from largest to smallest (noise stays -1), so colors are stable."""
    lab = np.asarray(lab)
    ids = [k for k in np.unique(lab) if k >= 0]
    ids.sort(key=lambda k: -(lab == k).sum())
    out = np.full_like(lab, -1)
    for new, k in enumerate(ids):
        out[lab == k] = new
    return out


def by_x(X, lab):
    """Relabel clusters left to right by mean x (noise stays -1)."""
    lab = np.asarray(lab)
    ids = sorted((k for k in np.unique(lab) if k >= 0), key=lambda k: X[lab == k, 0].mean())
    out = np.full_like(lab, -1)
    for new, k in enumerate(ids):
        out[lab == k] = new
    return out


def knee(curve):
    """Index of the point farthest from the chord of a sorted curve (a simple elbow rule)."""
    y = np.asarray(curve, float)
    x = np.linspace(0, 1, len(y))
    yn = (y - y[0]) / (y[-1] - y[0])
    return int(np.argmax(x - yn))


def kdist(X, min_samples):
    """Sorted distance to the (min_samples - 1)-th other point: the radius a point needs to be a core point."""
    d, _ = NearestNeighbors(n_neighbors=min_samples).fit(X).kneighbors(X)
    return np.sort(d[:, -1])


def tree_json(Z, n, Ks):
    """Dendrogram geometry for SVG: leaf order, x/height of every node, and flat labels for each K.

    Labels for a K are numbered by first appearance left to right in the leaf order,
    so a cluster keeps its color as the cut moves down.
    """
    order = dendrogram(Z, no_plot=True)["leaves"]
    x = np.empty(2 * n - 1)
    x[order] = np.arange(n)
    h = np.zeros(2 * n - 1)
    rep = list(range(n))
    kids = []
    for i, (a, b, hh, _) in enumerate(Z):
        a, b = int(a), int(b)
        x[n + i] = (x[a] + x[b]) / 2
        h[n + i] = hh
        rep.append(rep[a])
        kids.append([a, b])
    labs, cuts = {}, {}
    for K in Ks:
        raw = fcluster(Z, K, "maxclust")
        first = {}
        for leaf in order:
            first.setdefault(raw[leaf], len(first))
        labs[K] = [first[c] for c in raw]
        top = Z[n - K, 2] if K > 1 else Z[-1, 2] * 1.15
        cuts[K] = round(float((Z[n - K - 1, 2] + top) / 2), 3)
    return {"order": order, "x": r(x, 2), "h": r(h, 3), "rep": rep, "kids": kids, "labs": labs, "cuts": cuts}


def dbscan_waves(X, eps, min_samples):
    """DBSCAN by hand, recording the order clusters grow in.

    Visits points in index order like sklearn; each unvisited core point seeds a cluster that is
    expanded breadth-first. Returns labels (-1 noise), BFS depth ("wave") of each point, core mask.
    """
    nb = NearestNeighbors(radius=eps).fit(X).radius_neighbors(X, return_distance=False)
    core = np.array([len(v) >= min_samples for v in nb])
    lab = np.full(len(X), -1)
    wave = np.full(len(X), -1)
    k = 0
    for s in range(len(X)):
        if lab[s] != -1 or not core[s]:
            continue
        lab[s], wave[s] = k, 0
        queue = [s]
        while queue:
            nxt = []
            for p in queue:
                if not core[p]:
                    continue  # border points join but do not expand
                for q in nb[p]:
                    if lab[q] == -1:
                        lab[q], wave[q] = k, wave[p] + 1
                        nxt.append(q)
            queue = nxt
        k += 1
    return lab, wave, core


# ---------------------------------------------------------------------------
# Shared toy datasets (same recipes as the k-Means deck)
# ---------------------------------------------------------------------------
X3, y3 = make_blobs(n_samples=300, centers=3, cluster_std=0.8, random_state=0)
Xm, ym = make_moons(300, noise=0.06, random_state=0)
Xc, yc = make_circles(300, factor=0.5, noise=0.05, random_state=0)
Xu, yu = make_blobs(n_samples=[350, 60, 30], centers=[(-4, 0), (3, 2.5), (3.2, -2)], cluster_std=[2.0, 0.5, 0.4], random_state=170)
out15 = np.random.default_rng(3).uniform(X3.min(0) - 6, X3.max(0) + 6, (15, 2))
Xo, yo = np.vstack([X3, out15]), np.r_[y3, np.full(15, -1)]  # true outliers are noise

# varied density: two tight blobs close together, one wide uniform disk above them.
# Any eps loose enough to hold the disk together also bridges the gap between the tight blobs.
rng = np.random.default_rng(0)
_A = rng.normal([0, 0], 0.22, (120, 2))
_B = rng.normal([1.15, 0], 0.22, (120, 2))
_t = rng.uniform(0, 2 * np.pi, 200)
_rr = 2.4 * np.sqrt(rng.uniform(0, 1, 200))
_C = np.c_[0.575 + _rr * np.cos(_t), 4.3 + _rr * np.sin(_t)]
Xv = np.vstack([_A, _B, _C])
yv = np.r_[np.zeros(120, int), np.ones(120, int), np.full(200, 2)]

# ---------------------------------------------------------------------------
# Title: DBSCAN flood-fill on moons + rings + noise
# ---------------------------------------------------------------------------
hm, _ = make_moons(260, noise=0.05, random_state=4)
hc, _ = make_circles(300, factor=0.45, noise=0.035, random_state=4)
hero_noise = np.random.default_rng(4).uniform([-1.4, -1.25], [5.4, 1.6], (40, 2))
H = np.vstack([hm * [1.05, 1.1] + [-0.5, -0.1], hc * 1.15 + [3.9, 0.2], hero_noise])
hl, hw, _ = dbscan_waves(H, 0.2, 5)
assert adjusted_rand_score(hl, DBSCAN(eps=0.2, min_samples=5).fit_predict(H)) == 1.0
dump("hero", {"pts": r(H, 3), "lab": by_x(H, hl).tolist(), "wave": hw.tolist()})
print(f"  hero: {hl.max() + 1} clusters, {(hl == -1).sum()} noise, max wave {hw.max()}")

# ---------------------------------------------------------------------------
# k-means vs DBSCAN on moons (opening contrast)
# ---------------------------------------------------------------------------
km_m = KMeans(2, n_init=10, random_state=0).fit(Xm)
db_m = DBSCAN(eps=0.2, min_samples=5).fit_predict(Xm)
dump("moons", {
    "pts": r(Xm), "truth": ym.tolist(),
    "km": km_m.labels_.tolist(), "kmC": r(km_m.cluster_centers_), "kmAri": ari(ym, km_m.labels_),
    "db": by_x(Xm, db_m).tolist(), "dbAri": ari(ym, db_m),
})
print(f"  moons: k-means ARI {ari(ym, km_m.labels_)}, DBSCAN ARI {ari(ym, db_m)}")

# ---------------------------------------------------------------------------
# Agglomerative merge loop on 8 points (single linkage)
# ---------------------------------------------------------------------------
P8 = np.array([[1.0, 1.2], [1.6, 0.6], [2.3, 1.5], [5.2, 4.4], [6.0, 4.0], [5.4, 3.2], [3.6, 5.0], [8.6, 1.0]])
names8 = list("ABCDEFGH")
Z8 = linkage(P8, "single")
n8 = len(P8)
members = {i: [i] for i in range(n8)}
color_of = {}
next_color = 0
frames8 = [{"lab": [-1] * n8, "edge": None, "h": 0.0, "pair": None}]
D8 = np.sqrt(((P8[:, None] - P8[None]) ** 2).sum(-1))
for i, (a, b, h, _) in enumerate(Z8):
    a, b = int(a), int(b)
    ma, mb = members[a], members[b]
    # single linkage: the merge is the closest pair across the two clusters
    sub = D8[np.ix_(ma, mb)]
    pi, pj = np.unravel_index(sub.argmin(), sub.shape)
    if a in color_of or b in color_of:
        big = a if (a in color_of and (b not in color_of or len(ma) >= len(mb))) else b
        color_of[n8 + i] = color_of[big]
    else:
        color_of[n8 + i] = next_color
        next_color += 1
    members[n8 + i] = ma + mb
    lab = [-1] * n8
    alive = [c for c in members if c not in {int(x) for row in Z8[: i + 1, :2] for x in row}]
    for c in alive:
        if len(members[c]) > 1:
            for p in members[c]:
                lab[p] = color_of[c]
    frames8.append({"lab": lab, "edge": [int(ma[pi]), int(mb[pj])], "h": round(float(h), 2),
                    "pair": ["".join(sorted(names8[p] for p in ma)), "".join(sorted(names8[p] for p in mb))]})
dump("merge8", {"pts": r(P8, 2), "names": names8, "frames": frames8, "tree": tree_json(Z8, n8, [1, 2, 3])})

# ---------------------------------------------------------------------------
# Worked example by hand: 5 points on a line
# ---------------------------------------------------------------------------
x1 = np.array([1.0, 2.0, 4.5, 8.0, 9.5])
names5 = list("ABCDE")


def hand_merges(method):
    clusters = [[i] for i in range(5)]
    steps = []
    for _ in range(4):
        best = None
        mats = []
        for i in range(len(clusters)):
            row = []
            for j in range(len(clusters)):
                d = np.abs(x1[clusters[i]][:, None] - x1[clusters[j]][None])
                row.append(round(float(d.min() if method == "single" else d.max()), 1) if i != j else 0.0)
                if i < j and (best is None or row[-1] < best[0]):
                    best = (row[-1], i, j)
            mats.append(row)
        h, i, j = best
        steps.append({"names": ["".join(names5[p] for p in c) for c in clusters], "D": mats, "merge": [i, j], "h": h})
        clusters = [c for k, c in enumerate(clusters) if k not in (i, j)] + [clusters[i] + clusters[j]]
        clusters.sort(key=lambda c: x1[c].min())
    return steps


hand = {"x": x1.tolist(), "names": names5, "single": hand_merges("single"), "complete": hand_merges("complete")}
# cross-check heights with scipy
assert [s["h"] for s in hand["single"]] == r(linkage(x1[:, None], "single")[:, 2], 1)
assert [s["h"] for s in hand["complete"]] == r(linkage(x1[:, None], "complete")[:, 2], 1)
dump("hand", hand)
print(f"  hand single heights {[s['h'] for s in hand['single']]}, complete {[s['h'] for s in hand['complete']]}")

# ---------------------------------------------------------------------------
# Dendrogram + cut on blobs3 (Ward)
# ---------------------------------------------------------------------------
Zb = linkage(X3, "ward")
tb = tree_json(Zb, len(X3), [2, 3, 4, 6])
dump("dendro", {"pts": r(X3), **tb, "top": r(Zb[-8:, 2], 2)})
print(f"  dendro: cuts {tb['cuts']}, top merge heights {np.round(Zb[-6:, 2], 1).tolist()}")

# ---------------------------------------------------------------------------
# Linkage criteria: two small groups
# ---------------------------------------------------------------------------
g = np.random.default_rng(11)
GA = g.normal([0, 0], 0.55, (6, 2))
GB = g.normal([4.0, 0.9], 0.55, (7, 2))
DAB = np.sqrt(((GA[:, None] - GB[None]) ** 2).sum(-1))
mA, mB = GA.mean(0), GB.mean(0)
ward_inc = len(GA) * len(GB) / (len(GA) + len(GB)) * ((mA - mB) ** 2).sum()
dump("linkdemo", {
    "A": r(GA, 2), "B": r(GB, 2),
    "single": [int(i) for i in np.unravel_index(DAB.argmin(), DAB.shape)], "dSingle": round(float(DAB.min()), 2),
    "complete": [int(i) for i in np.unravel_index(DAB.argmax(), DAB.shape)], "dComplete": round(float(DAB.max()), 2),
    "dAverage": round(float(DAB.mean()), 2), "mA": r(mA, 2), "mB": r(mB, 2), "dWard": round(float(ward_inc), 1),
})

# ---------------------------------------------------------------------------
# Linkage grid: 4 linkages x (blobs3, moons, outliers)
# ---------------------------------------------------------------------------
grid = {}
for name, X, y, k in [("blobs3", X3, y3, 3), ("moons", Xm, ym, 2), ("outliers", Xo, yo, 3)]:
    row = {"pts": r(X), "truth": y.tolist(), "k": k}
    for L in ["single", "complete", "average", "ward"]:
        lab = AgglomerativeClustering(k, linkage=L).fit_predict(X)
        row[L] = {"lab": by_size(lab).tolist(), "ari": ari(y, lab), "sizes": sorted(np.bincount(lab).tolist(), reverse=True)}
    grid[name] = row
dump("linkgrid", grid)
for name, row in grid.items():
    print(f"  linkgrid {name}: " + ", ".join(f"{L} {row[L]['ari']} {row[L]['sizes']}" for L in ["single", "complete", "average", "ward"]))
assert grid["moons"]["single"]["ari"] == 1.0 and grid["outliers"]["single"]["sizes"][0] > 300

# ---------------------------------------------------------------------------
# DBSCAN anatomy: core, border, noise on a small set
# ---------------------------------------------------------------------------
EPS_S, MIN_S = 1.0, 4
for seed in range(5000):
    g = np.random.default_rng(seed)
    S = np.vstack([g.normal([2.0, 2.4], 0.7, (8, 2)), g.normal([6.4, 2.4], 0.7, (8, 2)), g.uniform([0, 0], [8.4, 4.8], (4, 2))])
    gaps = np.sqrt(((S[:, None] - S[None]) ** 2).sum(-1)) + np.eye(len(S)) * 9
    if S.min() < 0 or S[:, 0].max() > 8.4 or S[:, 1].max() > 4.8 or gaps.min() < 0.42:
        continue  # keep points apart so every dot and count is readable
    lab, wave, core = dbscan_waves(S, EPS_S, MIN_S)
    border = (lab >= 0) & ~core
    if lab.max() == 1 and 3 <= border.sum() <= 5 and 2 <= (lab == -1).sum() <= 4:
        break
cnt = [int(len(v)) for v in NearestNeighbors(radius=EPS_S).fit(S).radius_neighbors(S, return_distance=False)]
dump("anatomy", {"pts": r(S, 2), "eps": EPS_S, "minPts": MIN_S, "count": cnt, "core": core.tolist(), "lab": by_x(S, lab).tolist(), "seed": seed})
print(f"  anatomy seed {seed}: core {core.sum()}, border {border.sum()}, noise {(lab == -1).sum()}")

# ---------------------------------------------------------------------------
# DBSCAN growth, step by step (moons + scattered noise)
# ---------------------------------------------------------------------------
gm, gy = make_moons(220, noise=0.07, random_state=1)
gn = np.random.default_rng(1).uniform([-1.3, -0.8], [2.3, 1.3], (14, 2))
GX = np.vstack([gm, gn])
glab, gwave, gcore = dbscan_waves(GX, 0.2, 5)
assert adjusted_rand_score(glab, DBSCAN(eps=0.2, min_samples=5).fit_predict(GX)) == 1.0
order = [int(np.where((glab == k) & (gwave == 0))[0][0]) for k in range(glab.max() + 1)]
dump("grow", {"pts": r(GX), "lab": glab.tolist(), "wave": gwave.tolist(), "core": gcore.tolist(), "seeds": order, "eps": 0.2, "minPts": 5})
print(f"  grow: {glab.max() + 1} clusters, waves {[int(gwave[glab == k].max()) for k in range(glab.max() + 1)]}, noise {(glab == -1).sum()}")

# ---------------------------------------------------------------------------
# DBSCAN on k-means' failures: moons, circles, blobs + outliers
# ---------------------------------------------------------------------------
gal = {}
for name, X, y, k, eps, ms in [("moons", Xm, ym, 2, 0.2, 5), ("circles", Xc, yc, 2, 0.2, 5), ("outliers", Xo, yo, 3, 0.55, 10)]:
    km = KMeans(k + (name == "outliers"), n_init=10, random_state=0).fit(X)
    db = DBSCAN(eps=eps, min_samples=ms).fit_predict(X)
    gal[name] = {
        "pts": r(X), "truth": y.tolist(), "eps": eps, "minPts": ms,
        "km": km.labels_.tolist(), "kmC": r(km.cluster_centers_), "kmAri": ari(y, km.labels_),
        "db": by_x(X, db).tolist(), "dbAri": ari(y, db), "noise": int((db == -1).sum()),
    }
    if name == "outliers":
        gal[name]["flagged"] = int((db[300:] == -1).sum())
        gal[name]["edge"] = int((db[:300] == -1).sum())
dump("gallery", gal)
print("  gallery: " + ", ".join(f"{k} km {v['kmAri']} db {v['dbAri']} noise {v['noise']}" for k, v in gal.items()), f"outliers flagged {gal['outliers']['flagged']}/15, edge {gal['outliers']['edge']}")

# ---------------------------------------------------------------------------
# Choosing eps: k-distance plot on moons + noise (the growth data)
# ---------------------------------------------------------------------------
kd = kdist(GX, 5)
ki = knee(kd)  # max distance from the chord: a common automatic rule, which lands early on this gradual curve
two = [round(float(e), 2) for e in np.arange(0.05, 0.6, 0.01) if DBSCAN(eps=e, min_samples=5).fit_predict(GX).max() == 1]
EPS_PICK = 0.2  # read off the plot: just past where the curve turns sharply upward
kdj = {"kd": r(kd, 3), "autoKnee": ki, "autoEps": round(float(kd[ki]), 2), "pick": EPS_PICK, "pickRank": int((kd <= EPS_PICK).sum()),
       "good": [min(two), max(two)], "pts": r(GX), "minPts": 5, "runs": []}
for e in [0.08, EPS_PICK, 0.5]:
    lab = DBSCAN(eps=e, min_samples=5).fit_predict(GX)
    kdj["runs"].append({"eps": e, "lab": by_size(lab).tolist(), "k": int(lab.max() + 1), "noise": int((lab == -1).sum())})
dump("kdist", kdj)
print(f"  kdist: auto knee eps {kdj['autoEps']}, two moons for eps in {kdj['good']}; runs " + ", ".join(f"eps {x['eps']}: k {x['k']} noise {x['noise']}" for x in kdj["runs"]))

# ---------------------------------------------------------------------------
# Varying density: DBSCAN's dilemma, HDBSCAN's answer, and the density landscape
# ---------------------------------------------------------------------------
sweep = []
for e in np.round(np.arange(0.05, 1.6, 0.01), 2):
    lab = DBSCAN(eps=e, min_samples=5).fit_predict(Xv)
    sweep.append({"eps": float(e), "ari": ari(yv, lab), "k": int(lab.max() + 1), "noise": int((lab == -1).sum())})
best = max(sweep, key=lambda s: s["ari"])
dil = []
for e in [0.15, 0.3, 0.6]:
    lab = DBSCAN(eps=e, min_samples=5).fit_predict(Xv)
    dil.append({"eps": e, "lab": by_size(lab).tolist(), "ari": ari(yv, lab), "k": int(lab.max() + 1), "noise": int((lab == -1).sum())})
hdb = HDBSCAN(min_cluster_size=25, copy=True).fit(Xv)
hlab = by_x(Xv, hdb.labels_)
assert hdb.labels_.max() == 2 and ari(yv, hdb.labels_) >= 0.9 and best["ari"] < 0.8

# condensed tree (lambda = 1 / mutual-reachability distance). Rows: [parent, child, lambda, size];
# child < n is a point falling out of the cluster, child >= n is a sub-cluster being born.
ct = _condense_tree(hdb._single_linkage_tree_, 25)
nv = len(Xv)
tree_rows = [[int(x["parent"]), int(x["child"]), round(float(x["value"]), 3), int(x["cluster_size"])] for x in ct]
kids, fell = {}, {}
for p_, c_, lam, sz in tree_rows:
    (kids.setdefault(p_, []).append(c_) if c_ >= nv else fell.setdefault(p_, []).append(c_))


def subtree_points(c):
    return fell.get(c, []) + [q for k in kids.get(c, []) for q in subtree_points(k)]


# selected clusters: the highest nodes whose points all carry one HDBSCAN label
parent_of = {c_: p_ for p_, c_, _, _ in tree_rows if c_ >= nv}
selected = {}
for c in sorted({p_ for p_, *_ in tree_rows} | set(parent_of)):
    labs = {int(hlab[i]) for i in subtree_points(c)}
    if len(labs) == 1 and min(labs) >= 0:
        par = parent_of.get(c)
        if par is None or {int(hlab[i]) for i in subtree_points(par)} != labs:
            selected[c] = min(labs)
assert sorted(selected.values()) == [0, 1, 2], selected
# DBSCAN* at one fixed distance = a horizontal cut through this same tree
cuts = []
for e in [1.25, 0.25]:
    lab = hdb.dbscan_clustering(cut_distance=e, min_cluster_size=25)
    cuts.append({"eps": e, "lam": round(1 / e, 3), "lab": by_x(Xv, lab).tolist(), "k": int(lab.max() + 1), "noise": int((lab == -1).sum()), "ari": ari(yv, lab)})
# KDE landscape on a grid (for the "sea level" picture)
kde = KernelDensity(bandwidth=0.28).fit(Xv)
gx = np.linspace(-1.6, 2.8, 56)
gyy = np.linspace(-1.0, 7.0, 64)
GG = np.array(np.meshgrid(gx, gyy)).reshape(2, -1).T
dens = np.exp(kde.score_samples(GG)).reshape(len(gyy), len(gx))
dens = dens / dens.max()
# three sea levels: high (two tight islands), middle (they merge, disk still under water), low (disk appears, tight pair merged)
levels = []
for lv in [0.6, 0.15, 0.025]:
    comp, ncomp = cc_label(dens > lv)
    levels.append({"level": lv, "n": int(ncomp)})
dump("varied", {
    "pts": r(Xv), "truth": yv.tolist(), "sweep": sweep, "best": best, "dil": dil,
    "hdb": hlab.tolist(), "hdbAri": ari(yv, hdb.labels_), "hdbNoise": int((hdb.labels_ == -1).sum()),
    "prob": r(hdb.probabilities_, 2), "mcs": 25,
    "tree": tree_rows, "selected": {str(k): v for k, v in selected.items()}, "cuts": cuts,
    "grid": {"x": r(gx, 3), "y": r(gyy, 3), "z": r(dens, 3)}, "levels": levels,
})
print(f"  varied: DBSCAN best ARI {best['ari']} at eps {best['eps']} (k {best['k']}, noise {best['noise']}); "
      f"dilemma {[(d['eps'], d['k'], d['noise'], d['ari']) for d in dil]}; HDBSCAN ARI {ari(yv, hdb.labels_)} noise {(hdb.labels_ == -1).sum()}; "
      f"levels {[(l['level'], l['n']) for l in levels]}; selected {selected}; cuts {[(c['eps'], c['k'], c['noise'], c['ari']) for c in cuts]}")

# ---------------------------------------------------------------------------
# Comparing methods: ARI table and stability
# ---------------------------------------------------------------------------
datasets = [("blobs3", X3, y3, 3), ("moons", Xm, ym, 2), ("circles", Xc, yc, 2), ("outliers", Xo, yo, 3), ("varied", Xv, yv, 3)]


def best_params(X, y):
    """Best-case settings for the density methods on one dataset (chosen with the labels: an upper bound)."""
    db = max(((ari(y, DBSCAN(eps=e, min_samples=ms).fit_predict(X)), round(float(e), 2), ms)
              for ms in (5, 10) for e in np.arange(0.05, 1.5, 0.01)), key=lambda t: t[0])
    hd = max(((ari(y, HDBSCAN(min_cluster_size=m, copy=True).fit_predict(X)), m) for m in (5, 10, 15, 25, 40)), key=lambda t: t[0])
    return {"eps": db[1], "minPts": db[2], "mcs": hd[1]}


def fit_all(X, k, p):
    return {
        "k-means": KMeans(k, n_init=10, random_state=0).fit_predict(X),
        "Ward": AgglomerativeClustering(k, linkage="ward").fit_predict(X),
        "single": AgglomerativeClustering(k, linkage="single").fit_predict(X),
        "DBSCAN": DBSCAN(eps=p["eps"], min_samples=p["minPts"]).fit_predict(X),
        "HDBSCAN": HDBSCAN(min_cluster_size=p["mcs"], copy=True).fit_predict(X),
    }


methods = ["k-means", "Ward", "single", "DBSCAN", "HDBSCAN"]
table = {"methods": methods, "datasets": [d[0] for d in datasets], "ari": [], "params": [], "labs": {}}
params = {}
for name, X, y, k in datasets:
    params[name] = best_params(X, y)
    labs = fit_all(X, k, params[name])
    table["ari"].append([ari(y, labs[m]) for m in methods])
    table["params"].append({"k": k, **params[name]})
    table["labs"][name] = {"pts": r(X), "truth": y.tolist(), **{m: by_size(labs[m]).tolist() for m in methods}}
for (name, *_), row in zip(datasets, table["ari"]):
    print(f"  ARI {name:9s} " + "  ".join(f"{m} {a:5.2f}" for m, a in zip(methods, row)) + f"   {params[name]}")

# stability: refit on 30 random 80% subsamples (same settings) and compare with the full-data labels on the shared points
stab = {"methods": methods, "datasets": ["blobs3", "moons"], "runs": 30, "frac": 0.8, "ari": []}
for name, X, y, k in datasets[:2]:
    full = fit_all(X, k, params[name])
    per = [[] for _ in methods]
    for b in range(30):
        idx = np.sort(np.random.default_rng(100 + b).choice(len(X), int(0.8 * len(X)), replace=False))
        sub = fit_all(X[idx], k, params[name])
        for j, m in enumerate(methods):
            per[j].append(ari(full[m][idx], sub[m]))
    stab["ari"].append(per)
    print(f"  stability {name}: " + ", ".join(f"{m} median {np.median(v):.2f} min {min(v):.2f}" for m, v in zip(methods, per)))
dump("compare", {"table": table, "stab": stab})

# ---------------------------------------------------------------------------
# Real data 1: zoo animals, average linkage on their traits
# ---------------------------------------------------------------------------
rows = [line.strip().split(",") for line in (RAW / "zoo.data").read_text().splitlines() if line.strip()]
zn = [row[0] for row in rows]
ZF = np.array([[int(v) for v in row[1:17]] for row in rows], float)
ztype = np.array([int(row[17]) for row in rows])
traits = ["hair", "feathers", "eggs", "milk", "airborne", "aquatic", "predator", "toothed", "backbone", "breathes", "venomous", "fins", "legs", "tail", "domestic", "catsize"]
classes = ["mammal", "bird", "reptile", "fish", "amphibian", "insect", "invertebrate"]
ZS = ZF.copy()
ZS[:, 12] = ZF[:, 12] / 8  # legs 0-8 -> 0-1, so it weighs about as much as one yes/no trait
Zfull = linkage(ZS, "average", metric="cityblock")
full_ari = {K: round(float(adjusted_rand_score(ztype, fcluster(Zfull, K, "maxclust"))), 2) for K in range(2, 9)}
zn = [a if zn.index(a) == i else f"{a} 2" for i, a in enumerate(zn)]  # "frog" appears twice
tz = tree_json(Zfull, len(zn), [2, 3, 4, 5, 6, 7])
groups = {}
for K in [2, 3, 4, 5, 6, 7]:
    lab = np.array(tz["labs"][K])
    groups[K] = []
    for c in range(K):
        m = np.where(lab == c)[0]
        cls = np.bincount(ztype[m] - 1, minlength=7)
        top = int(cls.argmax())
        # example names in leaf order, so they match the picture
        ex = [zn[i] for i in tz["order"] if lab[i] == c][:: max(1, len(m) // 6)][:6]
        groups[K].append({"n": int(len(m)), "major": classes[top], "purity": round(float(cls[top] / len(m)), 2), "ex": ex})
# traits that separate the 7 groups most (largest spread of group means), for the heatmap highlight
lab7 = np.array(tz["labs"][7])
spread = np.array([np.ptp([ZS[lab7 == c, j].mean() for c in range(7)]) for j in range(16)])
dump("zoo", {"names": zn, "traits": traits, "classes": classes, "type": (ztype - 1).tolist(),
             "F": ZF.astype(int).tolist(), **tz, "ari": full_ari, "groups": groups, "keyTraits": np.argsort(-spread)[:6].tolist()})
print(f"  zoo: ARI {full_ari}; cuts {tz['cuts']}")
for c, gg in enumerate(groups[7]):
    print(f"    K=7 group {c}: n {gg['n']} {gg['major']} purity {gg['purity']} ex {gg['ex']}")

# ---------------------------------------------------------------------------
# Real data 2: earthquakes, DBSCAN with the haversine (great-circle) distance
# ---------------------------------------------------------------------------
eq = list(csv.DictReader((RAW / "usgs_m45_2024.csv").open()))
lat = np.array([float(e["latitude"]) for e in eq])
lon = np.array([float(e["longitude"]) for e in eq])
mag = np.array([float(e["mag"]) for e in eq])
dep = np.array([float(e["depth"]) for e in eq])
P = np.radians(np.c_[lat, lon])
EQ_KM, EQ_MS = 150, 10
eql = DBSCAN(eps=EQ_KM / 6371.0, min_samples=EQ_MS, metric="haversine", algorithm="ball_tree").fit_predict(P)
eql = by_size(eql)
nq = int(eql.max() + 1)
# k-means on 3D unit vectors (so 179°E and 179°W are neighbors), K = 20 for the comparison map
U = np.c_[np.cos(P[:, 0]) * np.cos(P[:, 1]), np.cos(P[:, 0]) * np.sin(P[:, 1]), np.sin(P[:, 0])]
eqk = by_size(KMeans(20, n_init=10, random_state=0).fit_predict(U))
# k-distance in km for choosing eps
eqkd = np.sort(NearestNeighbors(n_neighbors=EQ_MS, metric="haversine", algorithm="ball_tree").fit(P).kneighbors(P)[0][:, -1]) * 6371


def greedy_colors(labels, n, k=8):
    """Give clusters colors so that clusters with nearby members get different colors."""
    cents = [U[labels == c].mean(0) for c in range(n)]
    cols = []
    for c in range(n):
        near = sorted(range(c), key=lambda j: np.linalg.norm(cents[c] - cents[j]))[:6]
        used = {cols[j] for j in near}
        cols.append(next(i for i in range(k) if i not in used) if len(used) < k else c % k)
    return cols


def region(c):
    places = [eq[i]["place"].split(", ")[-1] if ", " in eq[i]["place"] else eq[i]["place"] for i in np.where(eql == c)[0]]
    return max(set(places), key=places.count)


coast = json.loads((RAW / "ne_110m_coastline.geojson").read_text())
lines = []
for f in coast["features"]:
    gm_ = f["geometry"]
    for part in ([gm_["coordinates"]] if gm_["type"] == "LineString" else gm_["coordinates"]):
        lines.append(r(part, 1))
dump("quakes", {
    "lat": r(lat, 2), "lon": r(lon, 2), "mag": r(mag, 1), "depth": r(dep, 0),
    "db": eql.tolist(), "km": eqk.tolist(), "dbCol": greedy_colors(eql, nq), "kmCol": greedy_colors(eqk, 20),
    "epsKm": EQ_KM, "minPts": EQ_MS, "n": len(eq), "k": nq, "noise": int((eql == -1).sum()),
    "top": [{"region": region(c), "n": int((eql == c).sum())} for c in range(8)],
    "kd": r(eqkd[:: max(1, len(eqkd) // 400)], 1), "coast": lines,
})
print(f"  quakes: {len(eq)} events, {nq} clusters, noise {(eql == -1).sum()} ({(eql == -1).mean():.0%}); top {[(region(c), int((eql == c).sum())) for c in range(8)]}")

# ---------------------------------------------------------------------------
# Real data 3: California block groups, HDBSCAN finds the metro areas
# ---------------------------------------------------------------------------
cal = fetch_california_housing()
clat, clon = cal.data[:, 6], cal.data[:, 7]
lat0 = np.deg2rad(clat.mean())
G = np.c_[(clon - clon.mean()) * 111.32 * np.cos(lat0), (clat - clat.mean()) * 110.57]  # km east/north, as in the k-Means deck
ch = by_size(HDBSCAN(min_cluster_size=300, min_samples=30, copy=True).fit_predict(G))
ckm = KMeans(8, n_init=10, random_state=0).fit(G)
cities = {"Los Angeles": (34.05, -118.25), "SF Peninsula & San Jose": (37.55, -122.15), "East Bay": (37.85, -122.2),
          "San Diego": (32.75, -117.15), "Sacramento": (38.6, -121.4), "Fresno": (36.75, -119.75),
          "Stockton & Modesto": (37.8, -121.1), "Inland Empire": (34.0, -117.35), "Santa Rosa": (38.45, -122.7),
          "Bakersfield": (35.35, -119.0)}
names_c = []
for c in range(ch.max() + 1):
    m = ch == c
    ll = (clat[m].mean(), clon[m].mean())
    names_c.append(min(cities, key=lambda k: (cities[k][0] - ll[0]) ** 2 + (cities[k][1] - ll[1]) ** 2))
assert len(set(names_c)) == len(names_c), names_c
show = np.random.default_rng(5).choice(len(G), 3000, replace=False)  # same subsample as the k-Means deck
dump("calmetro", {
    "pts": r(G[show], 1), "hdb": ch[show].tolist(), "km": ckm.labels_[show].tolist(), "kmC": r(ckm.cluster_centers_, 1),
    "names": names_c, "sizes": np.bincount(ch[ch >= 0]).tolist(), "noise": int((ch == -1).sum()), "n": len(G),
    "centers": [r(G[ch == c].mean(0), 1) for c in range(ch.max() + 1)],
})
print(f"  calmetro: {ch.max() + 1} metros {list(zip(names_c, np.bincount(ch[ch >= 0]).tolist()))}, noise {(ch == -1).sum()} ({(ch == -1).mean():.0%})")
