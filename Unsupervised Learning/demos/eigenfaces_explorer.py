"""Interactive eigenfaces explorer: click a face, then rebuild it from k eigenfaces.

Every one of the 400 faces is shown as a point using its first two PCA
coordinates (eigenface 1 and eigenface 2). Click a point to see that face,
and drag the slider to rebuild it from more or fewer eigenfaces.

Run with:  uv run eigenfaces_explorer.py
Then open: http://127.0.0.1:8051
"""

import numpy as np
import pandas as pd
import plotly.express as px
from dash import Dash, Input, Output, dcc, html
from sklearn.datasets import fetch_olivetti_faces
from sklearn.decomposition import PCA

# 1. Load the faces and fit PCA (fast: less than a second).
faces = fetch_olivetti_faces()
X = faces.data          # shape (400, 4096): one row per face
person = faces.target   # which of the 40 people is in each photo

pca = PCA()
scores = pca.fit_transform(X)
cumulative = np.cumsum(pca.explained_variance_ratio_)


def rebuild(i, k):
    """Rebuild face i from the mean face plus its first k eigenfaces."""
    return pca.mean_ + scores[i, :k] @ pca.components_[:k]


def face_figure(pixels, title):
    """Draw a 64 x 64 face as a grayscale image."""
    fig = px.imshow(pixels.reshape(64, 64), color_continuous_scale="gray", zmin=0, zmax=1, title=title)
    fig.update_xaxes(showticklabels=False)
    fig.update_yaxes(showticklabels=False)
    fig.update_layout(coloraxis_showscale=False, margin={"l": 0, "r": 0, "t": 40, "b": 0}, height=300)
    return fig


# 2. Build the web page: scatter plot on the left, faces and slider on the right.
app = Dash(__name__)
app.layout = html.Div(
    style={"fontFamily": "sans-serif", "padding": "16px"},
    children=[
        html.H2("Eigenfaces explorer: click a face, then change k"),
        html.Div(
            style={"display": "flex", "gap": "16px"},
            children=[
                dcc.Graph(id="scatter", style={"flex": "1", "height": "75vh"}),
                html.Div(style={"flex": "1"}, children=[
                    html.Div(style={"display": "flex"}, children=[
                        dcc.Graph(id="original", style={"flex": "1"}),
                        dcc.Graph(id="rebuilt", style={"flex": "1"}),
                    ]),
                    html.P("Number of eigenfaces used (k):"),
                    dcc.Slider(
                        id="k",
                        min=1,
                        max=400,
                        step=1,
                        value=20,
                        marks={k: str(k) for k in [1, 50, 100, 150, 200, 250, 300, 350, 400]},
                    ),
                ]),
            ],
        ),
    ],
)


def clicked_index(click_data):
    """Return the index of the clicked face (or face 0 before any click)."""
    if click_data is None:
        return 0
    return int(click_data["points"][0]["customdata"][0])


# 3. Draw the scatter plot and circle the selected face.
@app.callback(Output("scatter", "figure"), Input("scatter", "clickData"))
def draw_scatter(click_data):
    points = pd.DataFrame({
        "Eigenface 1": scores[:, 0],
        "Eigenface 2": scores[:, 1],
        "person": [f"Person {p}" for p in person],
        # Stored as text on purpose: Dash only reports `customdata` on a click
        # when it is sent as plain text, not as a packed array of numbers.
        "index": np.arange(len(X)).astype(str),
    })
    fig = px.scatter(
        points,
        x="Eigenface 1",
        y="Eigenface 2",
        color="person",
        custom_data=["index"],   # lets us find out which face was clicked
        title="400 faces, placed by their first two eigenface weights",
    )
    fig.update_traces(marker_size=8)
    fig.update_layout(showlegend=False, uirevision="keep")   # keep the zoom level when clicking

    i = clicked_index(click_data)
    fig.add_scatter(
        x=[scores[i, 0]], y=[scores[i, 1]], mode="markers", hoverinfo="skip", showlegend=False,
        marker={"size": 22, "symbol": "circle-open", "color": "black", "line_width": 3},
    )
    return fig


# 4. Show the clicked face and its reconstruction from k eigenfaces.
@app.callback(
    Output("original", "figure"),
    Output("rebuilt", "figure"),
    Input("scatter", "clickData"),
    Input("k", "value"),
)
def show_faces(click_data, k):
    i = clicked_index(click_data)
    original = face_figure(X[i], f"Original (person {person[i]})")
    rebuilt = face_figure(np.clip(rebuild(i, k), 0, 1), f"k = {k}  ({cumulative[k - 1]:.0%} of variance)")
    return original, rebuilt


if __name__ == "__main__":
    app.run(port=8051)
