"""Use cross-validation to choose Ridge and Lasso penalties for a polynomial fit."""

import numpy as np
import plotly.express as px
import plotly.graph_objects as go
from sklearn.linear_model import LassoCV, LinearRegression, RidgeCV
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
    # Create the same noisy samples from a true cubic relationship.
    rng = np.random.default_rng(RANDOM_STATE)
    x_train = rng.uniform(-1, 1, size=18)
    y_train = 0.5 - x_train + 2.0 * x_train**2 - 1.5 * x_train**3
    y_train += rng.normal(0, 0.45, size=x_train.size)
    x_train_column = x_train.reshape(-1, 1)

    # RidgeCV tests these candidate L2 penalties with five-fold cross-validation.
    ridge_alphas = [0.0001, 0.001, 0.01, 0.1, 1, 10]
    ridge_model = make_pipeline(
        PolynomialFeatures(DEGREE, include_bias=False),
        RidgeCV(alphas=ridge_alphas, cv=5, scoring="neg_root_mean_squared_error"),
    )

    # LassoCV automatically creates and tests a path of 100 L1 penalty values.
    lasso_model = make_pipeline(
        PolynomialFeatures(DEGREE, include_bias=False),
        LassoCV(alphas=100, cv=5, random_state=RANDOM_STATE, max_iter=100_000),
    )

    # The unregularized model remains a reference point; it needs no alpha selection.
    unregularized_model = make_pipeline(
        PolynomialFeatures(DEGREE, include_bias=False), LinearRegression()
    )

    # Each regularized pipeline picks alpha using only training-data folds, then refits on all data.
    unregularized_model.fit(x_train_column, y_train)
    ridge_model.fit(x_train_column, y_train)
    lasso_model.fit(x_train_column, y_train)

    selected_ridge_alpha = ridge_model.named_steps["ridgecv"].alpha_
    selected_lasso_alpha = lasso_model.named_steps["lassocv"].alpha_
    print(f"Selected Ridge alpha: {selected_ridge_alpha:.4f}")
    print(f"Selected Lasso alpha: {selected_lasso_alpha:.4f}")

    x_plot = np.linspace(-1, 1, 400)
    x_plot_column = x_plot.reshape(-1, 1)
    ground_truth = 0.5 - x_plot + 2.0 * x_plot**2 - 1.5 * x_plot**3

    # Compare the degree-10 fits against the noisy observations and true cubic.
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
        name=f"Ridge (CV alpha={selected_ridge_alpha:.4f})",
    )
    curves.add_scatter(
        x=x_plot,
        y=lasso_model.predict(x_plot_column),
        mode="lines",
        name=f"Lasso (CV alpha={selected_lasso_alpha:.4f})",
    )
    curves.update_layout(
        title=f"Degree-{DEGREE} polynomial fits with CV-tuned regularization",
        template="simple_white",
        xaxis_title="x",
        yaxis_title="y",
    )
    curves.show()

    # Inspect how the CV-selected penalties change the polynomial coefficients.
    coefficient_rows = (
        [
            {"power": f"x^{power}", "coefficient": coefficient, "model": "Unregularized"}
            for power, coefficient in enumerate(
                unregularized_model.named_steps["linearregression"].coef_, start=1
            )
        ]
        + [
            {"power": f"x^{power}", "coefficient": coefficient, "model": "Ridge (L2)"}
            for power, coefficient in enumerate(ridge_model.named_steps["ridgecv"].coef_, start=1)
        ]
        + [
            {"power": f"x^{power}", "coefficient": coefficient, "model": "Lasso (L1)"}
            for power, coefficient in enumerate(lasso_model.named_steps["lassocv"].coef_, start=1)
        ]
    )
    coefficients = px.bar(
        coefficient_rows,
        x="power",
        y="coefficient",
        color="model",
        barmode="group",
        title="Coefficients after CV-selected regularization",
        template="simple_white",
    )
    coefficients.add_hline(y=0, line_color="black", line_width=1)
    coefficients.show()

    print_coefficients("Unregularized", unregularized_model.named_steps["linearregression"])
    print_coefficients("Ridge (L2, CV-tuned)", ridge_model.named_steps["ridgecv"])
    print_coefficients("Lasso (L1, CV-tuned)", lasso_model.named_steps["lassocv"])
    zero_count = (lasso_model.named_steps["lassocv"].coef_ == 0).sum()
    print(f"\nLasso zero coefficients: {zero_count} / {DEGREE}")


if __name__ == "__main__":
    main()
