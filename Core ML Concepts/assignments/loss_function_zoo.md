# Assignment: The Loss Function Zoo

**Unit:** Core ML Concepts
**Decks this builds on:** *Loss Functions and Empirical Risk Minimization*, *Bias–Variance Tradeoff*
**Reference solution:** `loss_function_zoo/` (run with `uv run solution.py`)

## Why this assignment

The loss function is not a number you compute after training to write in a report.
It **is** the definition of "better" that the entire fitting procedure chases. Change
the loss and you change which model is optimal, even with the model class and the
data held fixed.

By the end you should be able to say, from things you have verified in code — not
from slogans:

- why 0–1 loss cannot be optimized directly, and what a smooth *surrogate* buys you;
- how squared error, absolute error, and Huber loss respond differently to one bad
  data point.

You may use `numpy` for everything and `scikit-learn` **only** to generate toy
datasets. Implement every loss, gradient, and optimizer yourself.

---

## Part 1 — Regression losses

Generate a 1-D dataset: `y = 2x + 1 + noise` with 60 points, then overwrite 3 of
the `y` values with large outliers (this mirrors the `y_true = [3, -.5, 2, 7, 50]`
example from the deck).

1. **Implement three losses and their gradients** with respect to the parameters
   `(w, b)` of the model `ŷ = w·x + b`:
   - mean squared error `(y − ŷ)²`
   - mean absolute error `|y − ŷ|`
   - *(optional)* Huber loss with parameter `δ` (quadratic for small residuals,
     linear beyond `δ`)

2. **Write one gradient-descent fitter** `fit(loss_grad, ...)` and reuse it for
   whichever losses you implement — the only thing that changes is which gradient
   function you pass in.

3. **Fit MSE and MAE (and Huber, if you implemented it)** and produce:
   - a scatter plot of the data with the fitted lines overlaid;
   - a table of `(slope, intercept)` for each fit.

   You should see the MSE line pulled visibly toward the outliers and the MAE line
   barely moving. If you implemented Huber, it should sit between them.

4. *(optional)* **Huber `δ` sweep.** Fit Huber for `δ` in
   `[0.05, 0.1, 0.3, 1, 3, 10, 100]` and plot the fitted slope against `δ`. Confirm
   that small `δ` reproduces the MAE slope and large `δ` reproduces the MSE slope —
   Huber *interpolates* between them.

---

## Part 2 — Classification losses

Generate a 2-class, 2-D dataset with some overlap between the classes
(`sklearn.datasets.make_blobs` is fine).

1. **Plot three losses as a function of the signed margin `m = y·f(x)`** (with `y`
   encoded as ±1), for `m` from −3 to 3, on one set of axes:
   - 0–1 loss `1[m < 0]`
   - hinge loss `max(0, 1 − m)`
   - log loss `log(1 + e^(−m))`

   This is the "surrogate losses supply a direction" figure from the deck — you are
   regenerating it yourself.

2. **Show 0–1 loss has no usable gradient.** Estimate its derivative by finite
   differences on a grid of margins and show the result is zero everywhere it is
   defined. State in one sentence why gradient descent cannot use it.

3. **Train a linear classifier** `f(x) = w·x + b` by gradient descent, once under
   hinge loss and once under log loss. Plot both decision boundaries over the data.

4. **Reproduce the cross-entropy table.** For a true label `y = 1`, print log loss
   at `p̂ ∈ {0.99, 0.5, 0.01}`. You should get approximately `{0.01, 0.69, 4.61}`.
   Then show what happens at `p̂ = 0` (the loss becomes infinite / NaN) and fix it
   by clipping `p̂` into `[1e-7, 1 − 1e-7]`.

5. **Cost-sensitive log loss.** Re-train the log-loss classifier with a 10×
   weight on the positive class (i.e. false negatives cost 10× a false positive).
   Show how the decision boundary shifts and describe the effect on the two error
   types in words. (This is a forward pointer to the Model Evaluation unit.)

---

## What to submit

```
loss_function_zoo/
  solution.py        # your single script, run with: uv run solution.py
  README.md          # a "What to expect" section with the numbers YOUR run produced
  *.html / *.png     # the figures from Parts 1 and 2
writeup.md            # ~1 page, see below
```

In `writeup.md`, answer in one or two sentences each:

- Which regression loss would you choose for house-price prediction where some rows
  contain data-entry errors? Why?
- Which classification loss / weighting for a cancer screening model? Why?
- If a weather model's probabilities need to be trustworthy (well-calibrated),
  which classification loss, and why?

## Stretch (optional)

- Add an L2 penalty and minimize `MSE + λ‖w‖²`; show `w` shrinking as `λ` grows.
  This is the bridge to the *Overfitting and Regularization* deck.
- Implement the pinball (quantile) loss and show that minimizing it fits a
  conditional quantile of `y` rather than the conditional mean.
