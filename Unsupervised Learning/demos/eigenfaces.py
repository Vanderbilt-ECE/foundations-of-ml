"""Eigenfaces: using PCA to find the "building blocks" of human faces.

Each face is a 64 x 64 grayscale photo, so it is a point in 4096-dimensional
space (one dimension per pixel). PCA finds a small number of directions,
called eigenfaces, that describe most of the variation between faces.

Run with:  uv run eigenfaces.py
"""

import numpy as np
import plotly.express as px
from sklearn.datasets import fetch_olivetti_faces
from sklearn.decomposition import PCA


def scale_to_0_1(images):
    """Stretch each image to the range [0, 1] so it is easy to display."""
    lows = images.min(axis=(1, 2), keepdims=True)
    highs = images.max(axis=(1, 2), keepdims=True)
    return (images - lows) / (highs - lows)


def set_panel_titles(fig, titles):
    """Replace Plotly's default panel titles ("facet_col=3") with our own."""
    for annotation in fig.layout.annotations:
        index = int(annotation.text.split("=")[1])
        annotation.text = titles[index]


# 1. Load the faces.
# 400 photos of 40 different people (10 photos each).
faces = fetch_olivetti_faces()
X = faces.data          # shape (400, 4096): one row per face, one column per pixel
person = faces.target   # which person is in each photo (0 to 39)

print(f"Number of faces: {X.shape[0]}")
print(f"Pixels per face (dimensions): {X.shape[1]}\n")

# 2. Fit PCA.
# PCA first subtracts the mean face, then finds the directions of largest variance.
pca = PCA()
scores = pca.fit_transform(X)   # each face's coordinates along the eigenfaces

# 3. Look at the mean face and the first eigenfaces.
# Each principal component is a vector of 4096 numbers, so we can reshape it
# back into a 64 x 64 image. Light and dark areas show which pixels change together.
mean_face = pca.mean_.reshape(1, 64, 64)
eigenfaces = pca.components_[:11].reshape(11, 64, 64)
gallery = scale_to_0_1(np.concatenate([mean_face, eigenfaces]))
titles = ["Mean face"] + [f"Eigenface {i}" for i in range(1, 12)]

fig = px.imshow(
    gallery,
    facet_col=0,
    facet_col_wrap=6,
    color_continuous_scale="gray",
    title="The mean face and the first 11 eigenfaces",
)
set_panel_titles(fig, titles)
fig.update_xaxes(showticklabels=False)
fig.update_yaxes(showticklabels=False)
fig.update_layout(coloraxis_showscale=False)
fig.show()

# 4. How many eigenfaces do we need?
# The cumulative explained variance tells us how much of the variation
# between faces is kept when we use the first k eigenfaces.
cumulative = np.cumsum(pca.explained_variance_ratio_)
for k in [10, 50, 100]:
    print(f"First {k:>3} eigenfaces keep {cumulative[k - 1]:.1%} of the variance")

fig = px.line(
    x=np.arange(1, len(cumulative) + 1),
    y=cumulative,
    labels={"x": "Number of eigenfaces (k)", "y": "Cumulative explained variance"},
    title="A few eigenfaces explain most of the variation (out of 4096 pixels!)",
)
fig.update_yaxes(tickformat=".0%")
fig.show()

# 5. Rebuild one face using only the first k eigenfaces.
# reconstruction = mean face + (score_1 * eigenface_1) + ... + (score_k * eigenface_k)
face_index = 0
k_values = [1, 5, 20, 50, 150, 400]

rebuilt = []
for k in k_values:
    face = pca.mean_ + scores[face_index, :k] @ pca.components_[:k]
    rebuilt.append(face.reshape(64, 64))
rebuilt.append(X[face_index].reshape(64, 64))

fig = px.imshow(
    np.clip(np.array(rebuilt), 0, 1),
    facet_col=0,
    color_continuous_scale="gray",
    title="Rebuilding a face from k eigenfaces (instead of 4096 pixels)",
)
set_panel_titles(fig, [f"k = {k} ({cumulative[k - 1]:.0%})" for k in k_values] + ["Original"])
fig.update_xaxes(showticklabels=False)
fig.update_yaxes(showticklabels=False)
fig.update_layout(coloraxis_showscale=False, height=350)
fig.show()

# 6. Plot faces in the space of the first 3 eigenfaces.
# Photos of the same person usually land near each other, even though
# PCA never saw the labels. We show 8 people so the colors are easy to tell apart.
shown = person < 8
fig = px.scatter_3d(
    x=scores[shown, 0],
    y=scores[shown, 1],
    z=scores[shown, 2],
    color=[f"Person {p}" for p in person[shown]],
    labels={"x": "Eigenface 1", "y": "Eigenface 2", "z": "Eigenface 3"},
    title="Each face as a point in 3D (8 people, 10 photos each)",
)
fig.update_traces(marker_size=5)
fig.show()
