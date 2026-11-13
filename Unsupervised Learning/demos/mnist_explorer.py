"""Interactive MNIST explorer: click a point to see the handwritten digit.

Shows 10,000 MNIST digits squeezed from 784 dimensions to 2 with PCA, t-SNE,
or UMAP. Click any point to see the image behind it. Switch methods to see
where the same digit lands in each picture.

Run with:  uv run mnist_explorer.py
Then open: http://127.0.0.1:8050
"""

import urllib.request
import warnings
from pathlib import Path

import numpy as np
import pandas as pd
import plotly.express as px
from dash import Dash, Input, Output, dcc, html
from sklearn.decomposition import PCA
from sklearn.manifold import TSNE
from umap import UMAP

# UMAP prints a couple of technical warnings that don't matter here, so we hide them.
warnings.filterwarnings("ignore", module="umap")

DATA_DIR = Path(__file__).parent / "data"
MNIST_FILE = DATA_DIR / "mnist.npz"
EMBEDDINGS_FILE = DATA_DIR / "mnist_embeddings.npz"

# 1. Load MNIST and take the same random sample of 10,000 digits as mnist_tsne_umap.py.
if not MNIST_FILE.exists():
    print("Downloading MNIST ...")
    DATA_DIR.mkdir(exist_ok=True)
    urllib.request.urlretrieve("https://storage.googleapis.com/tensorflow/tf-keras-datasets/mnist.npz", MNIST_FILE)

mnist = np.load(MNIST_FILE)
rng = np.random.default_rng(0)
sample = rng.choice(len(mnist["x_train"]), size=10_000, replace=False)
images = mnist["x_train"][sample]      # shape (10000, 28, 28), kept for display
labels = mnist["y_train"][sample]
X = images.reshape(-1, 784) / 255.0

# 2. Compute the three 2D embeddings.
# t-SNE and UMAP take about 30 seconds, so we save the results and reuse them next time.
if EMBEDDINGS_FILE.exists():
    embeddings = dict(np.load(EMBEDDINGS_FILE))
else:
    print("Computing PCA, t-SNE, and UMAP (about 30 seconds, only the first time) ...")
    X_50 = PCA(n_components=50).fit_transform(X)
    embeddings = {
        "PCA": PCA(n_components=2).fit_transform(X),
        "t-SNE": TSNE(n_components=2, perplexity=30, random_state=0).fit_transform(X_50),
        "UMAP": UMAP(n_components=2, n_neighbors=15, min_dist=0.1, random_state=0).fit_transform(X_50),
    }
    np.savez(EMBEDDINGS_FILE, **embeddings)

# 3. Build the web page: method buttons, the scatter plot, and an image panel.
app = Dash(__name__)
app.layout = html.Div(
    style={"fontFamily": "sans-serif", "padding": "16px"},
    children=[
        html.H2("MNIST explorer: click a point to see its digit"),
        dcc.RadioItems(id="method", options=["PCA", "t-SNE", "UMAP"], value="UMAP", inline=True),
        html.Div(
            style={"display": "flex", "gap": "16px"},
            children=[
                dcc.Graph(id="scatter", style={"flex": "2", "height": "75vh"}),
                html.Div(style={"flex": "1"}, children=[
                    dcc.Graph(id="digit-image"),
                    html.H3(id="caption"),
                ]),
            ],
        ),
    ],
)


def clicked_index(click_data):
    """Return the index of the clicked digit (or digit 0 before any click)."""
    if click_data is None:
        return 0
    return int(click_data["points"][0]["customdata"][0])


# 4. Redraw the scatter plot when the method changes or a point is clicked.
@app.callback(Output("scatter", "figure"), Input("method", "value"), Input("scatter", "clickData"))
def draw_scatter(method, click_data):
    points = pd.DataFrame({
        "x": embeddings[method][:, 0],
        "y": embeddings[method][:, 1],
        "digit": labels.astype(str),
        # Stored as text on purpose: Dash only reports `customdata` on a click
        # when it is sent as plain text, not as a packed array of numbers.
        "index": np.arange(len(labels)).astype(str),
    })
    fig = px.scatter(
        points,
        x="x",
        y="y",
        color="digit",
        custom_data=["index"],   # lets us find out which image was clicked
        category_orders={"digit": [str(d) for d in range(10)]},
        title=f"{method}: 10,000 digits from 784 dimensions to 2",
    )
    fig.update_traces(marker_size=4)

    # Circle the selected digit so it's easy to find (even after switching methods).
    i = clicked_index(click_data)
    fig.add_scatter(
        x=[points.x[i]], y=[points.y[i]], mode="markers", hoverinfo="skip", showlegend=False,
        marker={"size": 20, "symbol": "circle-open", "color": "black", "line_width": 3},
    )
    fig.update_xaxes(showticklabels=False, title="")
    fig.update_yaxes(showticklabels=False, title="")
    fig.update_layout(uirevision=method)   # keep the zoom level when clicking points
    return fig


# 5. Show the image of the clicked digit.
@app.callback(Output("digit-image", "figure"), Output("caption", "children"), Input("scatter", "clickData"))
def show_digit(click_data):
    i = clicked_index(click_data)
    fig = px.imshow(images[i], color_continuous_scale="gray_r")
    fig.update_xaxes(showticklabels=False)
    fig.update_yaxes(showticklabels=False)
    fig.update_layout(coloraxis_showscale=False, margin={"l": 0, "r": 0, "t": 0, "b": 0})
    return fig, f"This is a {labels[i]}  (image #{i})"


if __name__ == "__main__":
    app.run(port=8050)
