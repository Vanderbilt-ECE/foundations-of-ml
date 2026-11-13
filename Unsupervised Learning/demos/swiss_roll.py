"""Swiss roll: where PCA fails and t-SNE / UMAP succeed.

The Swiss roll is a flat 2D sheet that has been rolled up in 3D, like a
cinnamon roll. The "right" 2D picture is the unrolled sheet.

PCA can only rotate and flatten (a linear projection), so in 2D the sheet is
still rolled up: it just shows the spiral from the side. t-SNE and UMAP only try
to keep *neighbors* close, so they can unroll it. The price: they sometimes tear
the sheet into pieces, because they don't care about far-apart points.

Run with:  uv run swiss_roll.py
"""

import time
import warnings

import pandas as pd
import plotly.express as px
from sklearn.datasets import make_swiss_roll
from sklearn.decomposition import PCA
from sklearn.manifold import TSNE
from umap import UMAP

# UMAP prints a couple of technical warnings (about future versions and
# parallelism) that don't matter here, so we hide them.
warnings.filterwarnings("ignore", module="umap")

# 1. Make the Swiss roll.
# `position` says how far along the rolled-up sheet each point is.
# We use it only for coloring, so we can see whether neighbors stay neighbors.
X, position = make_swiss_roll(n_samples=3000, noise=0.1, random_state=0)
print(f"Points: {X.shape[0]}, dimensions: {X.shape[1]}\n")

fig = px.scatter_3d(
    x=X[:, 0],
    y=X[:, 1],
    z=X[:, 2],
    color=position,
    color_continuous_scale="Viridis",
    labels={"color": "position"},
    title="The Swiss roll in 3D (color = position along the sheet)",
)
fig.update_traces(marker_size=3)
fig.show()

# 2. Reduce from 3D to 2D with each method.
methods = {
    "PCA": PCA(n_components=2),
    "t-SNE": TSNE(n_components=2, perplexity=50, random_state=0),
    "UMAP": UMAP(n_components=2, n_neighbors=30, random_state=0),
}

results = []
for name, model in methods.items():
    start = time.time()
    embedding = model.fit_transform(X)
    print(f"{name:>5} took {time.time() - start:.1f} seconds")

    results.append(pd.DataFrame({
        "x": embedding[:, 0],
        "y": embedding[:, 1],
        "position": position,
        "method": name,
    }))

results = pd.concat(results)

# 3. Compare the three 2D pictures side by side.
# PCA: still a spiral. t-SNE / UMAP: flat bands where the color changes
# smoothly, which means neighbors on the sheet stayed neighbors.
fig = px.scatter(
    results,
    x="x",
    y="y",
    color="position",
    facet_col="method",
    color_continuous_scale="Viridis",
    title="Swiss roll in 2D: PCA keeps it rolled up, t-SNE and UMAP unroll it (sometimes in pieces)",
)
# Each method uses its own scale, so give every panel its own axes.
fig.update_xaxes(matches=None, showticklabels=False, title="")
fig.update_yaxes(matches=None, showticklabels=False, title="")
fig.update_traces(marker_size=4)
fig.for_each_annotation(lambda a: a.update(text=a.text.split("=")[1]))
fig.show()
