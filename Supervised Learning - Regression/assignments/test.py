# /// script
# dependencies = [
#   "numpy>=2.0",
#   "plotly>=6.0",
#   "scikit-learn>=1.5",
# ]
# ///

import numpy as np
from sklearn.linear_model import LinearRegression, Ridge, Lasso
from sklearn.preprocessing import PolynomialFeatures


# Define the ground truth function
rng = np.random.default_rng(seed=7)
x = np.linspace(-1, 1, 100).reshape(-1, 1)
y_truth = 1 + 2 * x[:, 0] - 3 * x[:, 0] ** 2 + 0.5 * x[:, 0] ** 3
y = y_truth + rng.normal(loc=0, scale=0.35, size=len(x))

# Create the polynomial feature matrix
polynomial = PolynomialFeatures(degree=3, include_bias=True)
X = polynomial.fit_transform(x)


# Compute closed form model parameters
close_form_weights = np.linalg.pinv(X.T @ X) @ X.T @ y
print(close_form_weights)


# Use built in linear regression
linear_model = LinearRegression(fit_intercept=False)
linear_model.fit(X, y)
print(linear_model.coef_)


# Define MSE loss, gradient, and gradient decent
def mse(y_actual, y_predicted):
    return np.mean((y_actual - y_predicted) ** 2)


def mse_gradient(X, y, weights):
    n = len(y)
    return (2 / n) * X.T @ (X @ weights - y)


def gradient_decent(X, y, learning_rate=0.5, steps=1000):
    weights = np.zeros(X.shape[1])

    for _ in range(steps):
        weights -= learning_rate * mse_gradient(X, y, weights)

    return weights


gd_weights = gradient_decent(X, y)


# Ridge Regression closed form

ridge_strength = 0.1

pentalty = np.eye(X.shape[1])

pentalty[0, 0] = 0

ridge_closed_form = np.linalg.solve(
    X.T @ X + len(y) * ridge_strength * pentalty, X.T @ y
)

print(ridge_closed_form)


# Ridge regression sklearn

ridge_model = Ridge(alpha=len(y) * ridge_strength)
ridge_model.fit(X[:, 1:], y)
ridge_sklearn_weights = np.r_[ridge_model.intercept_, ridge_model.coef_]

print(ridge_sklearn_weights)

# TODO: Ridge regression gradient decent
#


def ridge_gradient(X, y, weights, ridge_strenth):
    regularized_weights = weights.copy()
    regularized_weights[0] = 0

    return mse_gradient(X, y, weights) + 2 * ridge_strength * regularized_weights


def ridge_gradient_decent(X, y, ridge_strenth, learning_rate=0.05, steps=10000):
    weights = np.zeros(X.shape[1])

    for _ in range(steps):
        weights -= learning_rate * ridge_gradient(X, y, weights, ridge_strenth)

    return weights


ridge_gd_weights = ridge_gradient_decent(X, y, ridge_strength)

print(ridge_gd_weights)

# TODO: Over complex model

overfit_polynomial = PolynomialFeatures(degree=4, include_bias=True)
X_overfit = overfit_polynomial.fit_transform(x)

overfit_model = LinearRegression(fit_intercept=False)
overfit_model.fit(X_overfit, y)

overfit_weights = overfit_model.coef_

print(overfit_weights)

overfit_ridge_strength = 0.001
overfit_ridge_model = Ridge(alpha=len(y) * overfit_ridge_strength)
overfit_ridge_model.fit(X_overfit[:, 1:], y)

overfit_ridge_weights = np.r_[overfit_ridge_model.intercept_, overfit_ridge_model.coef_]

print(overfit_ridge_weights)

lasso_strength = 0.001
lasso_model = Lasso(alpha=lasso_strength, max_iter=20_000)
lasso_model.fit(X_overfit[:, 1:], y)
overfit_lasso_weights = np.r_[lasso_model.intercept_, lasso_model.coef_]
print(overfit_lasso_weights)
