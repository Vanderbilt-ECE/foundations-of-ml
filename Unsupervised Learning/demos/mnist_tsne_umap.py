"""PCA vs t-SNE vs UMAP on handwritten digits (MNIST).

Each digit is a 28 x 28 image, so it is a point in 784-dimensional space.
We squeeze all 784 dimensions down to 2 and check whether the ten digits
end up in separate groups. None of the methods see the labels; we only
use them to color the plots.

Run with:  uv run mnist_tsne_umap.py
"""

import time
import urllib.request
import warnings
from pathlib import Path

import numpy as np
import pandas as pd
import plotly.express as px
from sklearn.decomposition import PCA
from sklearn.manifold import TSNE
from umap import UMAP

# UMAP prints a couple of technical warnings (about future versions and
# parallelism) that don't matter here, so we hide them.
warnings.filterwarnings("ignore", module="umap")

# 1. Load MNIST (about 11 MB, downloaded the first time).
DATA_FILE = Path(__file__).parent / "data" / "mnist.npz"
if not DATA_FILE.exists():
    print("Downloading MNIST ...")
    DATA_FILE.parent.mkdir(exist_ok=True)
    urllib.request.urlretrieve("https://storage.googleapis.com/tensorflow/tf-keras-datasets/mnist.npz", DATA_FILE)

mnist = np.load(DATA_FILE)
images = mnist["x_train"]   # shape (60000, 28, 28)
labels = mnist["y_train"]   # the digit in each image, 0 to 9

# 2. Take a random sample and flatten each 28 x 28 image into 784 numbers.
# t-SNE gets slow on all 60,000 images, so we use 10,000.
rng = np.random.default_rng(0)
sample = rng.choice(len(images), size=10_000, replace=False)
X = images[sample].reshape(-1, 784) / 255.0   # pixel values from 0-255 to 0-1
digits = labels[sample].astype(str)           # text labels so Plotly uses one color per digit

print(f"Images: {X.shape[0]}, pixels per image (dimensions): {X.shape[1]}\n")

# 3. PCA straight down to 2 dimensions.
pca_2d = PCA(n_components=2).fit_transform(X)

# 4. A common trick: first use PCA to go from 784 to 50 dimensions.
# This removes noise and makes t-SNE and UMAP much faster.
pca_50 = PCA(n_components=50)
X_50 = pca_50.fit_transform(X)
print(f"50 PCA components keep {pca_50.explained_variance_ratio_.sum():.1%} of the variance\n")

# 5. Run t-SNE and UMAP on the 50-dimensional data.
start = time.time()
tsne_2d = TSNE(n_components=2, perplexity=30, random_state=0).fit_transform(X_50)
print(f"t-SNE took {time.time() - start:.1f} seconds")

start = time.time()
umap_2d = UMAP(n_components=2, n_neighbors=15, min_dist=0.1, random_state=0).fit_transform(X_50)
print(f" UMAP took {time.time() - start:.1f} seconds")

# 6. Put the three results in one table and plot them side by side.
results = pd.concat([
    pd.DataFrame({"x": result[:, 0], "y": result[:, 1], "digit": digits, "method": name})
    for name, result in [("PCA", pca_2d), ("t-SNE", tsne_2d), ("UMAP", umap_2d)]
])

fig = px.scatter(
    results,
    x="x",
    y="y",
    color="digit",
    facet_col="method",
    category_orders={"digit": [str(d) for d in range(10)]},
    title="10,000 handwritten digits squeezed from 784 dimensions to 2",
)
# Each method uses its own scale, so give every panel its own axes.
fig.update_xaxes(matches=None, showticklabels=False, title="")
fig.update_yaxes(matches=None, showticklabels=False, title="")
fig.update_traces(marker_size=3)
fig.for_each_annotation(lambda a: a.update(text=a.text.split("=")[1]))
fig.show()

# 7. Bonus: UMAP into 3 dimensions. Drag to rotate!
umap_3d = UMAP(n_components=3, n_neighbors=15, min_dist=0.1, random_state=0).fit_transform(X_50)

fig = px.scatter_3d(
    x=umap_3d[:, 0],
    y=umap_3d[:, 1],
    z=umap_3d[:, 2],
    color=digits,
    category_orders={"color": [str(d) for d in range(10)]},
    labels={"color": "digit", "x": "UMAP 1", "y": "UMAP 2", "z": "UMAP 3"},
    title="MNIST digits in 3D with UMAP",
)
fig.update_traces(marker_size=2)
fig.show()
