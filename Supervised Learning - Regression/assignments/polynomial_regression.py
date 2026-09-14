# /// script
# dependencies = [
#   "numpy>=2.0",
#   "plotly>=6.0",
#   "scikit-learn>=1.5",
# ]
# ///

"""A small comparison of polynomial regression methods.

Run with:
    uv run assignments/polynomial_regression.py
"""

import numpy as np
import plotly.graph_objects as go
from sklearn.linear_model import Lasso, LinearRegression, Ridge
from sklearn.preprocessing import PolynomialFeatures


# Make printed arrays short and easy to read.
np.set_printoptions(precision=3, suppress=True)


# -----------------------------------------------------------------------------
# 1. Create synthetic polynomial data
# -----------------------------------------------------------------------------
rng = np.random.default_rng(seed=7)
x = np.linspace(-1, 1, 100).reshape(-1, 1)

# The true relationship is y = 1 + 2x - 3x^2 + 0.5x^3, plus random noise.
y_true = 1 + 2 * x[:, 0] - 3 * x[:, 0] ** 2 + 0.5 * x[:, 0] ** 3
y = y_true + rng.normal(loc=0, scale=0.35, size=len(x))

# Convert x into the columns [1, x, x^2, x^3].
polynomial = PolynomialFeatures(degree=3, include_bias=True)
X = polynomial.fit_transform(x)


def mse(y_actual, y_predicted):
    """Return mean squared error."""
    return np.mean((y_actual - y_predicted) ** 2)


def show_result(name, weights, features=X):
    """Print a model's coefficients and training MSE."""
    print(f"{name:32} weights = {weights}")
    print(f"{'':32} MSE     = {mse(y, features @ weights):.4f}\n")


# -----------------------------------------------------------------------------
# 2. Ordinary polynomial regression: closed-form solution
# -----------------------------------------------------------------------------
# The pseudoinverse is a numerically safer version of:
# weights = inv(X.T @ X) @ X.T @ y
closed_form_weights = np.linalg.pinv(X.T @ X) @ X.T @ y
show_result("Ordinary: closed form", closed_form_weights)


# -----------------------------------------------------------------------------
# 3. Ordinary polynomial regression: scikit-learn
# -----------------------------------------------------------------------------
# X already contains a column of ones, so sklearn does not need another intercept.
linear_model = LinearRegression(fit_intercept=False)
linear_model.fit(X, y)
show_result("Ordinary: sklearn", linear_model.coef_)


# -----------------------------------------------------------------------------
# 4. Ordinary polynomial regression: gradient descent
# -----------------------------------------------------------------------------
def mse_gradient(X, y, weights):
    """Compute the gradient of mean squared error."""
    n = len(y)
    return (2 / n) * X.T @ (X @ weights - y)


def gradient_descent(X, y, learning_rate=0.05, steps=10_000):
    """Minimize MSE by repeatedly taking a small step downhill."""
    weights = np.zeros(X.shape[1])

    for _ in range(steps):
        weights -= learning_rate * mse_gradient(X, y, weights)

    return weights


gd_weights = gradient_descent(X, y)
show_result("Ordinary: gradient descent", gd_weights)


# -----------------------------------------------------------------------------
# 5. Ridge polynomial regression: closed-form solution
# -----------------------------------------------------------------------------
ridge_strength = 0.1

# Ridge minimizes MSE + ridge_strength * sum(non-intercept weights^2).
# The first diagonal value is zero so the intercept is not regularized.
penalty = np.eye(X.shape[1])
penalty[0, 0] = 0
ridge_closed_weights = np.linalg.solve(
    X.T @ X + len(y) * ridge_strength * penalty,
    X.T @ y,
)
show_result("Ridge: closed form", ridge_closed_weights)


# -----------------------------------------------------------------------------
# 6. Ridge polynomial regression: scikit-learn
# -----------------------------------------------------------------------------
# sklearn uses sum(error^2) + alpha * sum(weights^2), while our formula uses
# mean(error^2). Therefore alpha = number_of_samples * ridge_strength.
# We omit X's column of ones because sklearn fits an unpenalized intercept itself.
ridge_model = Ridge(alpha=len(y) * ridge_strength)
ridge_model.fit(X[:, 1:], y)
ridge_sklearn_weights = np.r_[ridge_model.intercept_, ridge_model.coef_]
show_result("Ridge: sklearn", ridge_sklearn_weights)


# -----------------------------------------------------------------------------
# 7. Ridge polynomial regression: gradient descent
# -----------------------------------------------------------------------------
def ridge_gradient(X, y, weights, ridge_strength):
    """Compute the gradient of MSE plus an L2 (ridge) penalty."""
    regularized_weights = weights.copy()
    regularized_weights[0] = 0  # Do not penalize the intercept.
    return mse_gradient(X, y, weights) + 2 * ridge_strength * regularized_weights


def ridge_gradient_descent(X, y, ridge_strength, learning_rate=0.05, steps=10_000):
    """Minimize the ridge objective with simple gradient descent."""
    weights = np.zeros(X.shape[1])

    for _ in range(steps):
        weights -= learning_rate * ridge_gradient(X, y, weights, ridge_strength)

    return weights


ridge_gd_weights = ridge_gradient_descent(X, y, ridge_strength)
show_result("Ridge: gradient descent", ridge_gd_weights)


# -----------------------------------------------------------------------------
# 8. An overcomplicated model: Ridge shrinks; Lasso can remove a term
# -----------------------------------------------------------------------------
# The data was generated from a degree-3 polynomial, but we give these models
# an extra x^4 feature. Ordinary regression uses that extra flexibility, even
# though x^4 is not part of the true relationship.
overfit_polynomial = PolynomialFeatures(degree=4, include_bias=True)
X_overfit = overfit_polynomial.fit_transform(x)

overfit_model = LinearRegression(fit_intercept=False)
overfit_model.fit(X_overfit, y)
overfit_weights = overfit_model.coef_
show_result("Ordinary: degree 4", overfit_weights, X_overfit)

# Ridge shrinks the extra x^4 coefficient, but leaves it nonzero.
# Convert from our mean-squared-error penalty to sklearn's sum-of-squares form.
overfit_ridge_strength = 0.0001
overfit_ridge_model = Ridge(alpha=len(y) * overfit_ridge_strength)
overfit_ridge_model.fit(X_overfit[:, 1:], y)
overfit_ridge_weights = np.r_[
    overfit_ridge_model.intercept_, overfit_ridge_model.coef_
]
show_result("Ridge: degree 4", overfit_ridge_weights, X_overfit)

# Lasso uses sklearn's objective:
# 1 / (2n) * sum(error^2) + alpha * sum(abs(non-intercept weights)).
# x^4 is unnecessary here, so this penalty drives its coefficient exactly to 0.
lasso_strength = 0.001
lasso_model = Lasso(alpha=lasso_strength, max_iter=20_000)
lasso_model.fit(X_overfit[:, 1:], y)
lasso_weights = np.r_[lasso_model.intercept_, lasso_model.coef_]
show_result("Lasso: degree 4", lasso_weights, X_overfit)


# -----------------------------------------------------------------------------
# 9. Plot the data and every fitted polynomial
# -----------------------------------------------------------------------------
figure = go.Figure()

# Show the noisy observations as points.
figure.add_scatter(
    x=x[:, 0],
    y=y,
    mode="markers",
    name="Noisy data",
    marker={"color": "black", "opacity": 0.55},
)

# Plot one line for each fitted model. Some lines overlap because methods that
# solve the same objective should produce nearly identical answers.
models = {
    "Ordinary: closed form": closed_form_weights,
    "Ordinary: sklearn": linear_model.coef_,
    "Ordinary: gradient descent": gd_weights,
    "Ridge: closed form": ridge_closed_weights,
    "Ridge: sklearn": np.r_[ridge_model.intercept_, ridge_model.coef_],
    "Ridge: gradient descent": ridge_gd_weights,
}

for name, weights in models.items():
    figure.add_scatter(x=x[:, 0], y=X @ weights, mode="lines", name=name)

figure.add_scatter(
    x=x[:, 0],
    y=X_overfit @ overfit_weights,
    mode="lines",
    name="Ordinary: degree 4",
)
figure.add_scatter(
    x=x[:, 0],
    y=X_overfit @ overfit_ridge_weights,
    mode="lines",
    name="Ridge: degree 4",
)
figure.add_scatter(
    x=x[:, 0],
    y=X_overfit @ lasso_weights,
    mode="lines",
    name="Lasso: degree 4",
)

figure.update_layout(
    title="Polynomial Regression Methods",
    xaxis_title="x",
    yaxis_title="y",
    template="plotly_white",
)
figure.show()
