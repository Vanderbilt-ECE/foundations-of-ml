"""Estimate bias² and variance for polynomial models of degrees 1 through 5."""

import numpy as np
import plotly.express as px
from sklearn.linear_model import LinearRegression
from sklearn.pipeline import make_pipeline
from sklearn.preprocessing import PolynomialFeatures

RANDOM_STATE = 7
TRAINING_SAMPLES = 18
RESAMPLES = 500
DEGREES = range(1, 6)


def true_function(x):
    """The cubic function from which every noisy training set is sampled."""
    return 0.5 - x + 2.0 * x**2 - 1.5 * x**3


def main() -> None:
    rng = np.random.default_rng(RANDOM_STATE)
    # Evaluate every fitted model at the same points across the full input range.
    x_grid = np.linspace(-1, 1, 200).reshape(-1, 1)
    true_y_grid = true_function(x_grid[:, 0])

    results = []

    for degree in DEGREES:
        # Store one prediction curve from each independently sampled training dataset.
        prediction_curves = []
        for _ in range(RESAMPLES):
            x_train = rng.uniform(-1, 1, size=TRAINING_SAMPLES)
            y_train = true_function(x_train) + rng.normal(
                0, 0.45, size=TRAINING_SAMPLES
            )

            # The pipeline builds polynomial columns, then fits ordinary least squares.
            model = make_pipeline(
                PolynomialFeatures(degree, include_bias=False), LinearRegression()
            )
            model.fit(x_train.reshape(-1, 1), y_train)
            prediction_curves.append(model.predict(x_grid))

        predictions = np.array(prediction_curves)
        mean_prediction = predictions.mean(axis=0)

        # Bias²: how far the average fitted curve is from the true cubic curve.
        bias_squared = np.mean((mean_prediction - true_y_grid) ** 2)
        # Variance: how much fitted curves vary when the training data change.
        variance = np.mean(predictions.var(axis=0))
        results.append(
            {"degree": str(degree), "Bias²": bias_squared, "Variance": variance}
        )

    # A grouped bar chart exposes the bias-variance trade-off as degree rises.
    plot_data = [
        {"degree": result["degree"], "quantity": "Bias²", "value": result["Bias²"]}
        for result in results
    ] + [
        {
            "degree": result["degree"],
            "quantity": "Variance",
            "value": result["Variance"],
        }
        for result in results
    ]
    chart = px.bar(
        plot_data,
        x="degree",
        y="value",
        color="quantity",
        barmode="group",
        title=f"Bias² and variance across {RESAMPLES} random training sets",
        labels={"degree": "Polynomial degree", "value": "Average squared error"},
        template="simple_white",
    )
    chart.show()

    print(f"Results from {RESAMPLES} random training sets")
    print("degree    bias²    variance")
    for result in results:
        print(
            f"{result['degree']:>6}  {result['Bias²']:>8.4f}  {result['Variance']:>10.4f}"
        )


if __name__ == "__main__":
    main()
