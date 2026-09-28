# Bias–Variance Tradeoff Demo

Extends the slide-8 snippet from the *Bias-Variance Tradeoff* deck. The true
function is **`sin(1.5πx)`** (the same one used on the slide) — deliberately *not*
a polynomial, so no polynomial degree can ever represent it exactly and the bias
curve declines smoothly. An outer loop sweeps polynomial regression models of
degree 1–10; for each degree the inner loop retrains on `N_SETS` fresh noisy
samples and we estimate **bias²**, **variance**, and **total expected loss** on a
fixed test grid. Results are printed and plotted with Plotly.

The inner resampling loop is kept in the same shape as the deck snippet so it's
recognizable.

## Run

```
uv run bias_variance.py
```

First run creates the environment automatically. It prints a table and writes
two figures (also opened in your browser):

- `bias_variance.html` — bias², variance, and total error vs polynomial degree
  (log y-axis).
- `bias_variance_fits.html` — one raw training sample with the true curve and a
  few fitted polynomials (degrees 1, 2, 4, 10) overlaid, so the
  underfit → good fit → overfit progression is visible by eye. Each legend entry
  carries that degree's averaged total loss from the experiment.

## What to expect

- **bias²** falls smoothly and monotonically: ~0.19 at degree 1 → ~0.03 at
  degree 2 → near zero by degree 4.
- **variance** rises smoothly and monotonically, climbing steeply past degree 7
  as the unregularized fit chases noise.
- **total error** is U-shaped, minimized around degree 3–4 — the "sweet spot."
