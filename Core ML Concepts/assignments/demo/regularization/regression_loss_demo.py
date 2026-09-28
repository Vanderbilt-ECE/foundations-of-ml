"""Compare MSE and MAE regression loss functions on noisy cubic data with outliers."""

import numpy as np
import plotly.graph_objects as go
from sklearn.preprocessing import PolynomialFeatures

RANDOM_STATE = 7
DEGREE = 3

# The two losses are ordinary Python functions expressed as lambdas.
MSE_LOSS = lambda y_true, y_pred: np.mean((y_true - y_pred) ** 2)
MAE_LOSS = lambda y_true, y_pred: np.mean(np.abs(y_true - y_pred))


def true_function(x):
    """The cubic relationship that generates the non-outlier observations."""
    return 0.5 - x + 2.0 * x**2 - 1.5 * x**3


def mse_gradient(X, y_true, y_pred):
    """Derivative of mean squared error with respect to the weight vector."""
    return 2 * X.T @ (y_pred - y_true) / len(y_true)


def mae_subgradient(X, y_true, y_pred):
    """A valid subgradient of MAE; MAE has no unique gradient at residual zero."""
    return X.T @ np.sign(y_pred - y_true) / len(y_true)


def gradient_descent(X, y, loss, gradient, learning_rate, iterations):
    """Fit weights by repeatedly moving in the direction that reduces a loss."""
    weights = np.zeros(X.shape[1])
    for _ in range(iterations):
        predictions = X @ weights
        weights -= learning_rate * gradient(X, y, predictions)
    return weights, loss(y, X @ weights)


def print_coefficients(name, weights) -> None:
    """Print the intercept and polynomial coefficients learned by gradient descent."""
    print(f"\n{name}")
    print(f"  intercept: {weights[0]: .3f}")
    for power, coefficient in enumerate(weights[1:], start=1):
        print(f"  x^{power}: {coefficient: .3f}")


def main() -> None:
    rng = np.random.default_rng(RANDOM_STATE)
    x_train = rng.uniform(-1, 1, size=30)
    y_train = true_function(x_train) + rng.normal(0, 0.25, size=x_train.size)

    # A few extreme values make MSE's stronger penalty for large residuals visible.
    outlier_indices = np.array([2, 11, 25])
    y_train[outlier_indices] += np.array([3.0, -3.0, 2.5])
    x_train_column = x_train.reshape(-1, 1)

    # Build [1, x, x², x³]. The first column of ones is the intercept term.
    polynomial_features = PolynomialFeatures(DEGREE, include_bias=True)
    X_train_polynomial = polynomial_features.fit_transform(x_train_column)

    # Fit one polynomial by minimizing each custom loss with batch gradient descent.
    mse_weights, mse_training_loss = gradient_descent(
        X_train_polynomial,
        y_train,
        MSE_LOSS,
        mse_gradient,
        learning_rate=0.08,
        iterations=10_000,
    )
    mae_weights, mae_training_loss = gradient_descent(
        X_train_polynomial,
        y_train,
        MAE_LOSS,
        mae_subgradient,
        learning_rate=0.01,
        iterations=20_000,
    )

    x_plot = np.linspace(-1, 1, 400)
    x_plot_column = x_plot.reshape(-1, 1)
    X_plot_polynomial = polynomial_features.transform(x_plot_column)
    ground_truth = true_function(x_plot)

    # Plot 1: MSE is pulled toward outliers; MAE is less affected by them.
    curves = go.Figure()
    normal_mask = np.ones(x_train.size, dtype=bool)
    normal_mask[outlier_indices] = False
    curves.add_scatter(
        x=x_train[normal_mask], y=y_train[normal_mask], mode="markers", name="Noisy samples"
    )
    curves.add_scatter(
        x=x_train[outlier_indices],
        y=y_train[outlier_indices],
        mode="markers",
        name="Outliers",
        marker={"color": "crimson", "size": 10, "symbol": "x"},
    )
    curves.add_scatter(
        x=x_plot, y=ground_truth, mode="lines", name="True cubic", line={"dash": "dash"}
    )
    curves.add_scatter(
        x=x_plot,
        y=X_plot_polynomial @ mse_weights,
        mode="lines",
        name="MSE fit (gradient descent)",
    )
    curves.add_scatter(
        x=x_plot,
        y=X_plot_polynomial @ mae_weights,
        mode="lines",
        name="MAE fit (subgradient descent)",
    )
    curves.update_layout(
        title="MSE is more sensitive to outliers than MAE",
        template="simple_white",
        xaxis_title="x",
        yaxis_title="y",
    )
    curves.show()

    print("Training-set loss (includes the deliberately added outliers)")
    print(f"MSE model: MSE={mse_training_loss:.3f}")
    print(f"MAE model: MAE={mae_training_loss:.3f}")
    print_coefficients("MSE model", mse_weights)
    print_coefficients("MAE model", mae_weights)


if __name__ == "__main__":
    main()
