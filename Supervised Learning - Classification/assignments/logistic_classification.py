"""A small, educational example of logistic classification.

Run this file with:

    uv run logistic_classification.py

The example fits the same binary classification problem two ways:

1. With scikit-learn's LogisticRegression.
2. With a short, from-scratch gradient descent implementation.
"""

import numpy as np
import plotly.graph_objects as go
from sklearn.linear_model import LogisticRegression


def sigmoid(z):
    """Convert any number into a value between 0 and 1."""
    return 1 / (1 + np.exp(-z))


def softmax(z):
    """Convert scores into probabilities that add up to 1 for each example."""
    exp_z = np.exp(z - np.max(z, axis=1, keepdims=True))
    return exp_z / exp_z.sum(axis=1, keepdims=True)


def compute_gradient(X, y, weights):
    """Calculate the gradient of logistic loss."""
    probabilities = sigmoid(X @ weights)
    errors = probabilities - y

    # The gradient tells us which direction increases the loss.
    return (X.T @ errors) / len(y)


def gradient_descent(X, y, learning_rate, steps):
    """Learn weights by repeatedly taking small steps down the loss curve."""
    weights = np.zeros(X.shape[1])

    for _ in range(steps):
        # Take one small step in the direction that reduces the loss.
        weights -= learning_rate * compute_gradient(X, y, weights)

    return weights


def multiclass_gradient(X, y, weights):
    """Calculate the softmax logistic-loss gradient."""
    probabilities = softmax(X @ weights)

    # Turn labels such as [0, 2, 1] into rows such as [1, 0, 0].
    y_one_hot = np.eye(weights.shape[1])[y.astype(int)]

    return (X.T @ (probabilities - y_one_hot)) / len(y)


def multiclass_gradient_descent(X, y, number_of_classes, learning_rate, steps):
    """Learn one set of weights for each class."""
    weights = np.zeros((X.shape[1], number_of_classes))

    for _ in range(steps):
        weights -= learning_rate * multiclass_gradient(X, y, weights)

    return weights


# 1. Generate a small binary classification dataset.
rng = np.random.default_rng(7)

# Class 0 is centered near (-2, -2).
class_0 = rng.normal(loc=(-2, -2), scale=1.0, size=(50, 2))

# Class 1 is centered near (2, 2).
class_1 = rng.normal(loc=(2, 2), scale=1.0, size=(50, 2))

# Stack the points and make labels: 0 for class 0, 1 for class 1.
features = np.vstack([class_0, class_1])
y = np.hstack([np.zeros(50), np.ones(50)])

# Add a column of 1s so the first weight is the intercept.
X = np.c_[np.ones(len(y)), features]
print(f"Generated {len(y)} examples with {features.shape[1]} features each.\n")

# Show the synthetic data. Each point is one example, colored by its class.
figure = go.Figure()
figure.add_scatter(x=class_0[:, 0], y=class_0[:, 1], mode="markers", name="Class 0")
figure.add_scatter(x=class_1[:, 0], y=class_1[:, 1], mode="markers", name="Class 1")
figure.update_layout(
    title="Synthetic binary classification data",
    xaxis_title="Feature 1",
    yaxis_title="Feature 2",
)
figure.show()

# 2. Let scikit-learn fit logistic regression for us.
sklearn_model = LogisticRegression(C=1_000_000, solver="lbfgs", fit_intercept=False)
sklearn_model.fit(X, y)
sklearn_probabilities = sklearn_model.predict_proba(X)[:, 1]
sklearn_predictions = (sklearn_probabilities >= 0.5).astype(int)

print("Scikit-learn LogisticRegression")
print(f"  weights:  {sklearn_model.coef_[0]}")
print(f"  accuracy:  {np.mean(sklearn_predictions == y):.1%}\n")

# 3. Fit the same kind of model ourselves with gradient descent.
print("Our simple gradient descent implementation")
weights = gradient_descent(X, y, learning_rate=0.1, steps=2_000)
probabilities = sigmoid(X @ weights)
predictions = (probabilities >= 0.5).astype(int)

print(f"  weights:  {weights}")
print(f"  accuracy:  {np.mean(predictions == y):.1%}")


# 4. Add a third class and fit a multiclass logistic regression model.
class_2 = rng.normal(loc=(0, -3), scale=1.0, size=(50, 2))

features_multi = np.vstack([class_0, class_1, class_2])
y_multi = np.hstack(
    [
        np.zeros(50),
        np.ones(50),
        np.full(50, 2),
    ]
)

# Again, the first column of X is the intercept column.
X_multi = np.c_[np.ones(len(y_multi)), features_multi]
number_of_classes = 3

# Show all three classes.
multi_figure = go.Figure()
multi_figure.add_scatter(
    x=class_0[:, 0], y=class_0[:, 1], mode="markers", name="Class 0"
)
multi_figure.add_scatter(
    x=class_1[:, 0], y=class_1[:, 1], mode="markers", name="Class 1"
)
multi_figure.add_scatter(
    x=class_2[:, 0], y=class_2[:, 1], mode="markers", name="Class 2"
)
multi_figure.update_layout(
    title="Synthetic multiclass classification data",
    xaxis_title="Feature 1",
    yaxis_title="Feature 2",
)
multi_figure.show()

# Scikit-learn handles multiclass logistic regression automatically.
sklearn_multi_model = LogisticRegression(
    C=1_000_000, solver="lbfgs", fit_intercept=False
)
sklearn_multi_model.fit(X_multi, y_multi)
sklearn_multi_predictions = sklearn_multi_model.predict(X_multi)

print("\nMulticlass scikit-learn LogisticRegression")
print(f"  weights:\n{sklearn_multi_model.coef_}")
print(f"  accuracy: {np.mean(sklearn_multi_predictions == y_multi):.1%}")

# Our gradient descent version uses softmax instead of sigmoid.
multi_weights = multiclass_gradient_descent(
    X_multi,
    y_multi,
    number_of_classes,
    learning_rate=0.1,
    steps=2_000,
)
multi_probabilities = softmax(X_multi @ multi_weights)
multi_predictions = np.argmax(multi_probabilities, axis=1)

print("\nMulticlass gradient descent")
print(f"  weights:\n{multi_weights.T}")
print(f"  accuracy: {np.mean(multi_predictions == y_multi):.1%}")
