"""Compare regularization settings for polynomial and RBF SVMs.

Run from the assignments directory with:

    uv run svm/svm_kernel_regularization.py
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


# 1. Create noisy rings and flip a few labels to mimic mislabeled examples.
features, labels = make_circles(n_samples=420, factor=0.45, noise=0.16, random_state=12)
rng = np.random.default_rng(12)
flipped = rng.choice(len(labels), size=25, replace=False)
labels[flipped] = 1 - labels[flipped]

X_train, X_test, y_train, y_test = train_test_split(
    features, labels, test_size=0.30, random_state=12, stratify=labels
)

# 2. Small C means stronger regularization. Large C encourages the SVM to fit
# the training labels closely, including the mislabeled examples.
polynomial_regularized = make_pipeline(
    StandardScaler(), SVC(kernel="poly", degree=8, C=0.1)
)
polynomial_regularized.fit(X_train, y_train)

polynomial_flexible = make_pipeline(
    StandardScaler(), SVC(kernel="poly", degree=8, C=1000)
)
polynomial_flexible.fit(X_train, y_train)

rbf_regularized = make_pipeline(StandardScaler(), SVC(kernel="rbf", C=0.1, gamma=8))
rbf_regularized.fit(X_train, y_train)

rbf_flexible = make_pipeline(StandardScaler(), SVC(kernel="rbf", C=1000, gamma=8))
rbf_flexible.fit(X_train, y_train)

# Print training and test accuracy to compare fitting the examples with
# performance on examples the models did not see.
print("Polynomial, stronger regularization:")
print(
    f"  train accuracy: {accuracy_score(y_train, polynomial_regularized.predict(X_train)):.1%}"
)
print(
    f"  test accuracy:  {accuracy_score(y_test, polynomial_regularized.predict(X_test)):.1%}"
)
print("Polynomial, weaker regularization:")
print(
    f"  train accuracy: {accuracy_score(y_train, polynomial_flexible.predict(X_train)):.1%}"
)
print(
    f"  test accuracy:  {accuracy_score(y_test, polynomial_flexible.predict(X_test)):.1%}"
)
print("RBF, stronger regularization:")
print(
    f"  train accuracy: {accuracy_score(y_train, rbf_regularized.predict(X_train)):.1%}"
)
print(
    f"  test accuracy:  {accuracy_score(y_test, rbf_regularized.predict(X_test)):.1%}"
)
print("RBF, weaker regularization:")
print(f"  train accuracy: {accuracy_score(y_train, rbf_flexible.predict(X_train)):.1%}")
print(f"  test accuracy:  {accuracy_score(y_test, rbf_flexible.predict(X_test)):.1%}")

# 3. Make a grid for drawing each model's decision regions.
padding = 0.4
x_min, x_max = features[:, 0].min() - padding, features[:, 0].max() + padding
y_min, y_max = features[:, 1].min() - padding, features[:, 1].max() + padding
x_values = np.linspace(x_min, x_max, 150)
y_values = np.linspace(y_min, y_max, 150)
grid_x, grid_y = np.meshgrid(x_values, y_values)
grid = np.c_[grid_x.ravel(), grid_y.ravel()]

class_0 = y_test == 0
class_1 = y_test == 1
blue = "#4C78A8"
orange = "#F58518"
background_colors = [[0, blue], [0.5, blue], [0.5, orange], [1, orange]]
figure = make_subplots(
    rows=2,
    cols=2,
    subplot_titles=[
        "Polynomial: stronger regularization",
        "Polynomial: weaker regularization",
        "RBF: stronger regularization",
        "RBF: weaker regularization",
    ],
    shared_xaxes=True,
    shared_yaxes=True,
)


def add_model_plot(model, row, col, show_legend=False):
    """Draw one model's decision regions and the held-out data points."""
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
            line=dict(color="#333", width=2),
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


# Add each setting explicitly to make the comparisons easy to follow.
add_model_plot(polynomial_regularized, row=1, col=1, show_legend=True)
add_model_plot(polynomial_flexible, row=1, col=2)
add_model_plot(rbf_regularized, row=2, col=1)
add_model_plot(rbf_flexible, row=2, col=2)

figure.update_xaxes(title_text="Feature 1", row=2, col=1)
figure.update_xaxes(title_text="Feature 1", row=2, col=2)
figure.update_yaxes(title_text="Feature 2", row=1, col=1)
figure.update_yaxes(title_text="Feature 2", row=2, col=1)
figure.update_layout(
    title="Regularization and overfitting in nonlinear SVMs", height=800, width=1050
)
figure.show()
