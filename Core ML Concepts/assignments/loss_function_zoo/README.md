# The Loss Function Zoo — Reference Solution

Single script. Run with:

```
uv run solution.py
```

First run builds the environment automatically. The script prints a set of
tables and writes four figures:

- `part1_regression_fits.html` — the data (with 3 outliers) and the MSE / MAE /
  Huber fitted lines.
- `part1_huber_sweep.html` — fitted slope vs Huber `delta`, with the MAE and MSE
  slopes drawn as reference lines.
- `part2_surrogate_losses.html` — 0–1, hinge, and log loss as functions of the
  signed margin.
- `part2_decision_boundaries.html` — hinge vs log-loss vs cost-sensitive
  log-loss decision boundaries on the blob data.

## What to expect (numbers from a clean run, seed 0)

### Part 1 — regression

The true line is `y = 2.00 x + 1.00`. Three of the sixty points are outliers.

| loss  | fitted slope | fitted intercept |
|-------|-------------:|-----------------:|
| MSE   | 2.415 | 0.899 |
| MAE   | 2.018 | 1.013 |
| Huber (δ=1) | 2.082 | 0.988 |

Squared error is pulled ~20% off the true slope because each outlier contributes
its residual *squared*. Absolute error nearly recovers the truth; Huber sits
just inside it.

**Huber δ sweep** — the fitted slope moves smoothly from the MAE value to the MSE
value as δ grows:

```
MAE slope   = 2.018      (delta -> 0 limit)
delta=0.05    slope = 2.019
delta=0.1     slope = 2.016
delta=0.3     slope = 2.024
delta=1.0     slope = 2.082
delta=3.0     slope = 2.249
delta=10.0    slope = 2.415
delta=100.0   slope = 2.415
MSE slope   = 2.415      (delta -> infinity limit)
```

**Maximum-likelihood tie-in** (true `w = 2.000`):

```
gaussian noise:  argmin SSE = 1.993   argmin SAE = 1.989   -> MSE matches the MLE
laplace  noise:  argmin SSE = 2.018   argmin SAE = 2.008   -> MAE matches the MLE
```

Minimizing squared error is maximum-likelihood estimation *when the noise is
Gaussian*; minimizing absolute error is the MLE *when the noise is Laplace*.

### Part 2 — classification

- The finite-difference derivative of 0–1 loss is `0.0` at every tested margin
  (except the undefined jump at `m = 0`). A gradient optimizer gets no direction
  from it — hence smooth surrogates.
- Cross-entropy for a true label `y = 1`:

  | `p_hat` | log loss |
  |--------:|---------:|
  | 0.99 | 0.01 |
  | 0.50 | 0.69 |
  | 0.01 | 4.61 |
  | 0.00 | 16.12 (would be `+inf` without clipping → `NaN` in training) |

  Being confidently wrong (`p_hat = 0.01` when `y = 1`) costs ~460× more than
  being confidently right.
- **Cost-sensitive log loss.** Weighting the positive class 10× moves the
  boundary hard toward catching positives:

  | model | false negatives | false positives |
  |-------|----------------:|----------------:|
  | equal weights | 20 | 19 |
  | 10× FN weight | 1 | 60 |

  Same model class, same data — only the loss changed, and with it the entire
  notion of the "best" boundary.

## Reading guide

The script mirrors the assignment part-by-part. The three regression gradients
each only supply `dL/dr` (the derivative of the per-point loss with respect to
the residual); a shared two-line chain-rule step turns that into the gradient
with respect to `w` and `b`. The single `fit()` function is plain gradient
descent and is reused for every loss.
