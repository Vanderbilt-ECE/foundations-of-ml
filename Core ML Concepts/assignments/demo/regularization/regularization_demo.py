"""Compare ordinary least squares, ridge, and lasso on diabetes data."""

import plotly.express as px
from sklearn.datasets import load_diabetes
from sklearn.linear_model import LassoCV, LinearRegression, RidgeCV
from sklearn.metrics import mean_squared_error, r2_score
from sklearn.model_selection import train_test_split
from sklearn.pipeline import make_pipeline
from sklearn.preprocessing import StandardScaler

# One seed makes the train/test split reproducible.
RANDOM_STATE = 42


def tune_regularized_models(X_train, y_train):
    """Fit Ridge and Lasso after selecting alpha with five-fold CV."""
    # Search several penalty strengths from very light to fairly strong.
    alphas = [0.001, 0.01, 0.1, 1, 10, 100]

    # Scaling happens inside every CV fold, preventing data leakage.
    ridge = make_pipeline(
        StandardScaler(), RidgeCV(alphas=alphas, scoring="neg_root_mean_squared_error")
    )
    lasso = make_pipeline(
        StandardScaler(),
        # An integer asks LassoCV to generate a 100-value alpha path automatically.
        LassoCV(alphas=100, cv=5, random_state=RANDOM_STATE, max_iter=10_000),
    )
    ridge.fit(X_train, y_train)
    lasso.fit(X_train, y_train)
    return ridge, lasso


def main() -> None:
    # The diabetes dataset contains 10 patient features and a continuous target.
    X, y = load_diabetes(return_X_y=True)
    feature_names = ["age", "sex", "bmi", "bp", "s1", "s2", "s3", "s4", "s5", "s6"]
    X_train, X_test, y_train, y_test = train_test_split(
        X, y, test_size=0.25, random_state=RANDOM_STATE
    )

    ridge, lasso = tune_regularized_models(X_train, y_train)
    print(f"Selected Ridge alpha: {ridge.named_steps['ridgecv'].alpha_}")
    print(f"Selected Lasso alpha: {lasso.named_steps['lassocv'].alpha_}")

    models = {
        "Linear regression": LinearRegression(),
        "Ridge (L2, CV-tuned)": ridge,
        "Lasso (L1, CV-tuned)": lasso,
    }

    results = []
    coefficient_rows = []
    for name, model in models.items():
        model.fit(X_train, y_train)
        predictions = model.predict(X_test)

        # R² is higher-is-better; RMSE is lower-is-better.
        results.append(
            {
                "model": name,
                "R²": r2_score(y_test, predictions),
                "RMSE": mean_squared_error(y_test, predictions) ** 0.5,
            }
        )

        # Pipelines expose the fitted estimator as their final step.
        estimator = model[-1] if hasattr(model, "steps") else model
        coefficient_rows.extend(
            {"feature": feature, "coefficient": coefficient, "model": name}
            for feature, coefficient in zip(feature_names, estimator.coef_)
        )

    # Plot 1: a compact out-of-sample performance comparison.
    performance = px.bar(
        results,
        x="model",
        y="R²",
        color="model",
        text="R²",
        title="Test-set performance",
        template="simple_white",
    )
    performance.update_traces(texttemplate="%{text:.3f}", textposition="outside")
    performance.update_layout(showlegend=False, yaxis_range=[0, 1])
    performance.show()

    # Plot 2: regularization shrinks coefficients, with Lasso able to set some to zero.
    coefficients = px.bar(
        coefficient_rows,
        x="feature",
        y="coefficient",
        color="model",
        barmode="group",
        title="Feature coefficients",
        template="simple_white",
    )
    coefficients.add_hline(y=0, line_color="black", line_width=1)
    coefficients.show()

    print("\nTest-set results")
    for result in results:
        print(f"{result['model']}: R²={result['R²']:.3f}, RMSE={result['RMSE']:.1f}")


if __name__ == "__main__":
    main()
