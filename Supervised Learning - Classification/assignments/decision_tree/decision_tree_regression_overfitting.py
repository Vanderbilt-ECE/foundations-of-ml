"""
Decision Tree Regression: Controlling Overfitting

A decision tree regressor can fit *any* training data perfectly if it's
allowed to grow deep enough -- it just keeps splitting until every leaf
has one point. That's overfitting: the tree memorizes noise instead of
learning the true underlying pattern.

max_depth is one way to regularize a tree, but not the only one. This
script also varies min_samples_leaf (the minimum number of points a leaf
must contain) while leaving depth unlimited, showing that limiting leaf
size controls overfitting just as well as limiting depth does.
"""

import numpy as np
import plotly.graph_objects as go
from sklearn.tree import DecisionTreeRegressor

# ---------------------------------------------------------------------------
# 1. Create a noisy synthetic dataset: y = sin(x) + random noise
# ---------------------------------------------------------------------------
rng = np.random.RandomState(42)
X = np.sort(rng.uniform(0, 2 * np.pi, size=80)).reshape(-1, 1)
y = np.sin(X).ravel() + rng.normal(scale=0.3, size=X.shape[0])

# A fine grid of x-values for drawing smooth prediction curves.
X_plot = np.linspace(0, 2 * np.pi, 500).reshape(-1, 1)

# ---------------------------------------------------------------------------
# 2. Fit trees of increasing depth and plot each one's predictions
# ---------------------------------------------------------------------------
fig = go.Figure()
fig.add_trace(go.Scatter(x=X.ravel(), y=y, mode="markers", name="noisy data"))
fig.add_trace(go.Scatter(x=X_plot.ravel(), y=np.sin(X_plot).ravel(), mode="lines", name="true sin(x)"))

# None = no depth limit, so the tree grows until every leaf is pure --
# maximum overfitting.
for max_depth in [2, 4, 10, None]:
    tree = DecisionTreeRegressor(max_depth=max_depth, random_state=42)
    tree.fit(X, y)
    predictions = tree.predict(X_plot)
    fig.add_trace(
        go.Scatter(x=X_plot.ravel(), y=predictions, mode="lines", name=f"max_depth={max_depth}")
    )

# ---------------------------------------------------------------------------
# 3. Fit trees with unlimited depth but increasing min_samples_leaf
# ---------------------------------------------------------------------------
# With max_depth=None the tree would normally overfit completely, but
# requiring each leaf to contain more points forces it to generalize
# instead of carving out a leaf for every noisy point.
for min_samples_leaf in [1, 5, 10, 20]:
    tree = DecisionTreeRegressor(max_depth=None, min_samples_leaf=min_samples_leaf, random_state=42)
    tree.fit(X, y)
    predictions = tree.predict(X_plot)
    fig.add_trace(
        go.Scatter(
            x=X_plot.ravel(),
            y=predictions,
            mode="lines",
            line=dict(dash="dash"),
            name=f"min_samples_leaf={min_samples_leaf}",
        )
    )

fig.update_layout(
    title="Decision Tree Regression: Regularizing with max_depth vs. min_samples_leaf",
    xaxis_title="x",
    yaxis_title="y",
)
fig.show()
