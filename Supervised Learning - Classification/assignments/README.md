# Simple logistic classification

This example creates two small Gaussian-shaped groups of points and fits a
binary logistic classifier in two ways:

1. `scikit-learn`'s `LogisticRegression`.
2. A short implementation using gradient descent.

The feature matrix includes a leading column of ones. Its weight is the
intercept, so the gradient code can treat the intercept just like every other
parameter.

At the bottom of the script, a third class is added. The script then compares
scikit-learn's multiclass logistic regression with a simple softmax gradient
descent implementation.

## Run it

From this directory:

```bash
uv run logistic_classification.py
```

The script prints the learned weights, intercept, accuracy, and a few loss
values from gradient descent. The two methods should make similar predictions,
even though the optimization code is deliberately written out step by step.
The exact coefficients can differ because the data is highly separable and the
two methods use different optimization details.
