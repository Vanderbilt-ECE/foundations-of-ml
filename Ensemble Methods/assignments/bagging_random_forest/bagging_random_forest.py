"""Single tree vs bagging vs random forest on the two-moons dataset.

1. Fit all three models on the same noisy training data and plot their
   decision boundaries side by side. The single deep tree carves little
   islands around noisy points; averaging many trees smooths them away.
2. Plot test accuracy as trees are added, with the single tree as a baseline.

Run with:  uv run bagging_random_forest.py
"""

import numpy as np
from sklearn.datasets import make_moons
from sklearn.ensemble import BaggingClassifier, RandomForestClassifier
from sklearn.tree import DecisionTreeClassifier
import plotly.graph_objects as go
from plotly.subplots import make_subplots

# ---- data: 300 noisy training points, 5,000 fresh test points ----
X_train, y_train = make_moons(n_samples=300, noise=0.3, random_state=3)
X_test, y_test = make_moons(n_samples=5000, noise=0.3, random_state=4)

# ---- models ----
# Bagging: every split may look at all features.
# Random forest: every split looks at a random subset of features ("sqrt").
models = {
    "Single deep tree": DecisionTreeClassifier(random_state=0),
    "Bagging (100 trees)": BaggingClassifier(DecisionTreeClassifier(), n_estimators=100, random_state=0),
    "Random forest (100 trees)": RandomForestClassifier(n_estimators=100, max_features="sqrt", random_state=0),
}

# ---- figure 1: decision boundaries ----
xs = np.linspace(-1.6, 2.6, 200)
ys = np.linspace(-1.2, 1.7, 150)
grid = np.c_[np.meshgrid(xs, ys)[0].ravel(), np.meshgrid(xs, ys)[1].ravel()]

fig = make_subplots(rows=1, cols=3, subplot_titles=list(models), horizontal_spacing=0.03)
for col, (name, model) in enumerate(models.items(), start=1):
    model.fit(X_train, y_train)
    acc = model.score(X_test, y_test)
    prob = model.predict_proba(grid)[:, 1].reshape(len(ys), len(xs))

    fig.add_trace(go.Heatmap(x=xs, y=ys, z=prob, zmin=0, zmax=1, colorscale="RdBu", reversescale=True,
                             showscale=False, opacity=0.6), row=1, col=col)
    fig.add_trace(go.Scatter(x=X_train[:, 0], y=X_train[:, 1], mode="markers", showlegend=False,
                             marker=dict(color=y_train, colorscale="RdBu", reversescale=True,
                                         line=dict(color="black", width=0.5), size=6)), row=1, col=col)
    fig.layout.annotations[col - 1].text = f"{name}<br>test accuracy {acc:.1%}"
    print(f"{name:28s} test accuracy {acc:.3f}")

fig.update_xaxes(showticklabels=False)
fig.update_yaxes(showticklabels=False)
fig.update_layout(title="Shading = predicted probability of the red class", width=1200, height=450)
fig.write_html("boundaries.html")
fig.show()

# ---- figure 2: test accuracy as trees are added ----
sizes = [1, 2, 5, 10, 25, 50, 100, 200]
single_acc = models["Single deep tree"].score(X_test, y_test)
bag_acc, rf_acc = [], []
for n in sizes:
    bag = BaggingClassifier(DecisionTreeClassifier(), n_estimators=n, random_state=0).fit(X_train, y_train)
    rf = RandomForestClassifier(n_estimators=n, max_features="sqrt", random_state=0).fit(X_train, y_train)
    bag_acc.append(bag.score(X_test, y_test))
    rf_acc.append(rf.score(X_test, y_test))

fig2 = go.Figure()
fig2.add_trace(go.Scatter(x=sizes, y=bag_acc, mode="lines+markers", name="Bagging"))
fig2.add_trace(go.Scatter(x=sizes, y=rf_acc, mode="lines+markers", name="Random forest"))
fig2.add_hline(y=single_acc, line_dash="dash", annotation_text="single deep tree")
fig2.update_xaxes(type="log", title="Number of trees")
fig2.update_yaxes(title="Test accuracy")
fig2.update_layout(title="More trees help, then level off", width=800, height=450)
fig2.write_html("accuracy_vs_trees.html")
fig2.show()
