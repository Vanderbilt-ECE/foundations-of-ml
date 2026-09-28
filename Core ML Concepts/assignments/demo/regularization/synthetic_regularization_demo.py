"""Show how Ridge and Lasso regularize an overly flexible polynomial fit."""

import numpy as np
import plotly.express as px
import plotly.graph_objects as go
from sklearn.linear_model import Lasso, LinearRegression, Ridge
from sklearn.pipeline import make_pipeline
from sklearn.preprocessing import PolynomialFeatures

RANDOM_STATE = 7
DEGREE = 10


def print_coefficients(name, model) -> None:
    """Print the intercept and coefficients in the x, x², ..., x^DEGREE basis."""
    print(f"\n{name}")
    print(f"  intercept: {model.intercept_: .3f}")
    for power, coefficient in enumerate(model.coef_, start=1):
        print(f"  x^{power:>2}: {coefficient: .3f}")


def main() -> None:
    # Keep x in [-1, 1] so x, x², ..., x^DEGREE remain directly comparable.
    rng = np.random.default_rng(RANDOM_STATE)
    x_train = rng.uniform(-1, 1, size=18)

    # The hidden relationship is a simple cubic polynomial.
    y_train = 0.5 - 1.0 * x_train + 2.0 * x_train**2 - 1.5 * x_train**3
    y_train += rng.normal(0, 0.45, size=x_train.size)

    # Each pipeline first creates [x, x², x³, ..., x^DEGREE], then fits a regressor.
    # Therefore, every model can receive the original one-column x data directly.
    unregularized_model = make_pipeline(
        PolynomialFeatures(DEGREE, include_bias=False), LinearRegression()
    )
    ridge_model = make_pipeline(
        PolynomialFeatures(DEGREE, include_bias=False), Ridge(alpha=0.03)
    )
    lasso_model = make_pipeline(
        PolynomialFeatures(DEGREE, include_bias=False), Lasso(alpha=0.02, max_iter=100_000)
    )

    # Ordinary least squares has no penalty, so it can fit noise with large coefficients.
    unregularized_model.fit(x_train.reshape(-1, 1), y_train)
    # Ridge applies an L2 penalty: it pulls every coefficient toward zero.
    ridge_model.fit(x_train.reshape(-1, 1), y_train)
    # Lasso applies an L1 penalty: it can set coefficients exactly to zero.
    lasso_model.fit(x_train.reshape(-1, 1), y_train)

    x_plot = np.linspace(-1, 1, 400)
    x_plot_column = x_plot.reshape(-1, 1)
    ground_truth = 0.5 - x_plot + 2.0 * x_plot**2 - 1.5 * x_plot**3

    # Step 3: plot the noisy observations, true relationship, and each high-degree fit.
    curves = go.Figure()
    curves.add_scatter(x=x_train, y=y_train, mode="markers", name="Noisy samples")
    curves.add_scatter(
        x=x_plot, y=ground_truth, mode="lines", name="True cubic", line={"dash": "dash"}
    )
    curves.add_scatter(
        x=x_plot,
        y=unregularized_model.predict(x_plot_column),
        mode="lines",
        name="Unregularized",
    )
    curves.add_scatter(
        x=x_plot,
        y=ridge_model.predict(x_plot_column),
        mode="lines",
        name="Ridge (L2)",
    )
    curves.add_scatter(
        x=x_plot,
        y=lasso_model.predict(x_plot_column),
        mode="lines",
        name="Lasso (L1)",
    )
    curves.update_layout(
        title=f"Overfitting a noisy cubic with a degree-{DEGREE} polynomial",
        template="simple_white",
        xaxis_title="x",
        yaxis_title="y",
    )
    curves.show()

    # A coefficient plot makes Ridge shrinkage and Lasso's exact zeros visible.
    coefficient_rows = (
        [
            {"power": f"x^{power}", "coefficient": coefficient, "model": "Unregularized"}
            for power, coefficient in enumerate(
                unregularized_model.named_steps["linearregression"].coef_, start=1
            )
        ]
        + [
            {"power": f"x^{power}", "coefficient": coefficient, "model": "Ridge (L2)"}
            for power, coefficient in enumerate(ridge_model.named_steps["ridge"].coef_, start=1)
        ]
        + [
            {"power": f"x^{power}", "coefficient": coefficient, "model": "Lasso (L1)"}
            for power, coefficient in enumerate(lasso_model.named_steps["lasso"].coef_, start=1)
        ]
    )
    coefficients = px.bar(
        coefficient_rows,
        x="power",
        y="coefficient",
        color="model",
        barmode="group",
        title="Regularization shrinks high-degree polynomial coefficients",
        template="simple_white",
    )
    coefficients.add_hline(y=0, line_color="black", line_width=1)
    coefficients.show()

    print_coefficients("Unregularized", unregularized_model.named_steps["linearregression"])
    print_coefficients("Ridge (L2)", ridge_model.named_steps["ridge"])
    print_coefficients("Lasso (L1)", lasso_model.named_steps["lasso"])
    print(
        f"\nLasso zero coefficients: {(lasso_model.named_steps['lasso'].coef_ == 0).sum()}"
        f" / {DEGREE}"
    )


if __name__ == "__main__":
    main()
