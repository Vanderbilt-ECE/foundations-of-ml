"""Compare three SVM kernels on noisy rings.

Run from the assignments directory with:

    uv run svm/svm_kernel_comparison.py
"""

import numpy as np
import plotly.graph_objects as go
from plotly.subplots import make_subplots
from sklearn.datasets import make_circles
from sklearn.metrics import accuracy_score
from sklearn.model_selection import train_test_split
from sklearn.pipeline import make_pipeline
from sklearn.preprocessing import StandardScaler
from sklearn.svm import SVC


# 1. Create two noisy rings. A straight line cannot separate the classes.
features, labels = make_circles(n_samples=500, factor=0.45, noise=0.13, random_state=7)
X_train, X_test, y_train, y_test = train_test_split(
    features, labels, test_size=0.25, random_state=7, stratify=labels
)

# 2. Fit one model for each kernel. Scaling keeps both features comparable.
linear_model = make_pipeline(StandardScaler(), SVC(kernel="linear", C=1))
linear_model.fit(X_train, y_train)

polynomial_model = make_pipeline(StandardScaler(), SVC(kernel="poly", degree=2, C=1))
polynomial_model.fit(X_train, y_train)

rbf_model = make_pipeline(StandardScaler(), SVC(kernel="rbf", C=1))
rbf_model.fit(X_train, y_train)

print(
    f"Linear test accuracy: {accuracy_score(y_test, linear_model.predict(X_test)):.1%}"
)
print(
    f"Polynomial test accuracy: {accuracy_score(y_test, polynomial_model.predict(X_test)):.1%}"
)
print(f"RBF test accuracy: {accuracy_score(y_test, rbf_model.predict(X_test)):.1%}")

# 3. Make a grid of points so we can color the regions each model predicts.
padding = 0.35
x_min, x_max = features[:, 0].min() - padding, features[:, 0].max() + padding
y_min, y_max = features[:, 1].min() - padding, features[:, 1].max() + padding
x_values = np.linspace(x_min, x_max, 150)
y_values = np.linspace(y_min, y_max, 150)
grid_x, grid_y = np.meshgrid(x_values, y_values)
grid = np.c_[grid_x.ravel(), grid_y.ravel()]

# Use the same points and colors in each panel for an easy comparison.
class_0 = y_test == 0
class_1 = y_test == 1
blue = "#4C78A8"
orange = "#F58518"
background_colors = [[0, blue], [0.5, blue], [0.5, orange], [1, orange]]


def add_model_plot(figure, model, row, col, show_legend=False):
    """Add one model's colored decision regions and test points to the figure."""
    regions = model.predict(grid).reshape(grid_x.shape)
    scores = model.decision_function(grid).reshape(grid_x.shape)
    figure.add_trace(
        go.Heatmap(
            x=x_values,
            y=y_values,
            z=regions,
            colorscale=background_colors,
            showscale=False,
            opacity=0.28,
            hoverinfo="skip",
        ),
        row=row,
        col=col,
    )
    figure.add_trace(
        go.Contour(
            x=x_values,
            y=y_values,
            z=scores,
            contours=dict(start=0, end=0, size=1, coloring="none"),
            line=dict(color="#333333", width=2),
            showscale=False,
            hoverinfo="skip",
        ),
        row=row,
        col=col,
    )
    figure.add_trace(
        go.Scatter(
            x=X_test[class_0, 0],
            y=X_test[class_0, 1],
            mode="markers",
            name="Class 0",
            marker=dict(color=blue, size=7),
            showlegend=show_legend,
        ),
        row=row,
        col=col,
    )
    figure.add_trace(
        go.Scatter(
            x=X_test[class_1, 0],
            y=X_test[class_1, 1],
            mode="markers",
            name="Class 1",
            marker=dict(color=orange, size=7),
            showlegend=show_legend,
        ),
        row=row,
        col=col,
    )


figure = make_subplots(
    rows=1,
    cols=3,
    subplot_titles=["Linear", "Polynomial (degree 2)", "RBF"],
    shared_xaxes=True,
    shared_yaxes=True,
)

# Add each model explicitly, so the comparison is easy to follow.
add_model_plot(figure, linear_model, row=1, col=1, show_legend=True)
add_model_plot(figure, polynomial_model, row=1, col=2)
add_model_plot(figure, rbf_model, row=1, col=3)

figure.update_xaxes(title_text="Feature 1", row=1, col=2)
figure.update_yaxes(title_text="Feature 2", row=1, col=1)
figure.update_layout(
    title="SVM kernels on noisy concentric rings", height=500, width=1200
)
figure.show()
