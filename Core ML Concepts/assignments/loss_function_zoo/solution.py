"""Reference solution: The Loss Function Zoo.

One script, run with:  uv run solution.py

It is organised into the same parts as the assignment. Every loss, gradient and
optimiser is written out with numpy so you can read exactly what is happening;
scikit-learn is used only to *generate* the classification blobs.

Structure:
    Part 1 - Regression losses (MSE / MAE / Huber), the outlier effect,
             the Huber delta sweep, and the maximum-likelihood tie-in.
    Part 2 - Classification losses (0-1 / hinge / log), why 0-1 has no gradient,
             training a linear classifier, the cross-entropy table, and a
             cost-sensitive re-fit.
"""

import numpy as np
import plotly.graph_objects as go
from sklearn.datasets import make_blobs


# =====================================================================
# Part 1 - Regression losses
# =====================================================================
#
# Model:  y_hat = w * x + b        (two parameters, theta = [w, b])
# We fit theta by plain gradient descent. The ONLY thing that changes
# between the three losses is the gradient function we hand to `fit`.

rng = np.random.default_rng(0)

# --- data: y = 2x + 1 + noise, then 3 points turned into gross outliers ------
# x is kept in [0, 1] so a fixed learning rate is well behaved - with x up to 10
# the squared-error gradient (which carries a factor of x**2) would explode.
N = 60
x = rng.uniform(0, 1, N)
y = 2.0 * x + 1.0 + rng.normal(scale=0.1, size=N)

outlier_idx = np.array([10, 30, 50])
y[outlier_idx] += np.array([5.0, -4.0, 5.0])  # data-entry-error sized blunders


def predict(theta, x):
    """Linear model. theta = [w, b]."""
    w, b = theta
    return w * x + b


# --- the three losses and their gradients w.r.t. theta = [w, b] --------------
#
# For every loss we need d(loss)/dw and d(loss)/db, averaged over the data.
# Write the residual as  r = y - y_hat = y - (w*x + b).  Then
#     dr/dw = -x        dr/db = -1
# and the chain rule gives
#     d(loss)/dw = mean( dL/dr * (-x) )
#     d(loss)/db = mean( dL/dr * (-1) )
# so each gradient function below only has to supply dL/dr, the derivative of
# the per-point loss with respect to the residual itself.


def mse_loss(theta, x, y):
    r = y - predict(theta, x)
    return np.mean(r**2)


def mse_grad(theta, x, y):
    r = y - predict(theta, x)
    dL_dr = 2.0 * r  # d/dr of r**2
    return np.array([np.mean(dL_dr * -x), np.mean(dL_dr * -1.0)])


def mae_loss(theta, x, y):
    r = y - predict(theta, x)
    return np.mean(np.abs(r))


def mae_grad(theta, x, y):
    r = y - predict(theta, x)
    dL_dr = np.sign(r)  # d/dr of |r|  (0 exactly at r = 0)
    return np.array([np.mean(dL_dr * -x), np.mean(dL_dr * -1.0)])


def huber_loss(theta, x, y, delta=1.0):
    r = y - predict(theta, x)
    small = np.abs(r) <= delta
    # quadratic near zero, linear in the tails - the two pieces meet smoothly
    return np.mean(np.where(small, 0.5 * r**2, delta * (np.abs(r) - 0.5 * delta)))


def huber_grad(theta, x, y, delta=1.0):
    r = y - predict(theta, x)
    # dL/dr is just r when |r| <= delta, and delta*sign(r) beyond that -
    # i.e. the residual "clipped" to +/- delta. That clipping is the whole
    # reason Huber ignores how far away an outlier is.
    dL_dr = np.clip(r, -delta, delta)
    return np.array([np.mean(dL_dr * -x), np.mean(dL_dr * -1.0)])


# --- one gradient-descent fitter, reused for every loss ---------------------
def fit(grad_fn, x, y, lr=0.1, steps=40_000):
    theta = np.zeros(2)  # start at w = 0, b = 0
    for _ in range(steps):
        theta = theta - lr * grad_fn(theta, x, y)
    return theta


theta_mse = fit(mse_grad, x, y)
theta_mae = fit(mae_grad, x, y)
theta_huber = fit(lambda t, x, y: huber_grad(t, x, y, delta=1.0), x, y)

print("=" * 64)
print("Part 1 - regression fits (true line is y = 2.00 x + 1.00)")
print("=" * 64)
print(f"{'loss':>8}  {'slope w':>10}  {'intercept b':>12}")
for name, th in [("MSE", theta_mse), ("MAE", theta_mae), ("Huber", theta_huber)]:
    print(f"{name:>8}  {th[0]:>10.3f}  {th[1]:>12.3f}")
print("MSE is dragged off the true slope by the 3 outliers; MAE and Huber are not.")

# --- figure: the three fitted lines over the data --------------------------
grid = np.linspace(x.min(), x.max(), 100)
fig1 = go.Figure()
fig1.add_scatter(
    x=x,
    y=y,
    mode="markers",
    name="data (3 outliers)",
    marker=dict(color="#94a3b8", size=7),
)
for name, th, color in [
    ("MSE fit", theta_mse, "#60a5fa"),
    ("MAE fit", theta_mae, "#f59e0b"),
    ("Huber fit", theta_huber, "#2dd4bf"),
]:
    fig1.add_scatter(
        x=grid,
        y=predict(th, grid),
        mode="lines",
        name=name,
        line=dict(color=color, width=3),
    )
fig1.update_layout(
    title="Part 1: one outlier pulls MSE, not MAE / Huber",
    xaxis_title="x",
    yaxis_title="y",
    template="plotly_white",
)
fig1.write_html("part1_regression_fits.html")
print("wrote part1_regression_fits.html")


# --- Huber delta sweep: Huber interpolates MAE <-> MSE ---------------------
deltas = [0.05, 0.1, 0.3, 1.0, 3.0, 10.0, 100.0]
huber_slopes = [
    fit(lambda t, x, y, d=d: huber_grad(t, x, y, delta=d), x, y)[0] for d in deltas
]

print()
print("Huber delta sweep (slope):")
print(f"  MAE slope  = {theta_mae[0]:.3f}   (delta -> 0 limit)")
for d, s in zip(deltas, huber_slopes):
    print(f"  delta={d:<6}  slope = {s:.3f}")
print(f"  MSE slope  = {theta_mse[0]:.3f}   (delta -> infinity limit)")

fig2 = go.Figure()
fig2.add_scatter(
    x=deltas,
    y=huber_slopes,
    mode="lines+markers",
    name="Huber",
    line=dict(color="#2dd4bf"),
)
fig2.add_hline(
    y=theta_mae[0], line_dash="dot", line_color="#f59e0b", annotation_text="MAE slope"
)
fig2.add_hline(
    y=theta_mse[0], line_dash="dot", line_color="#60a5fa", annotation_text="MSE slope"
)
fig2.update_layout(
    title="Part 1: Huber interpolates between MAE and MSE as delta grows",
    xaxis_title="delta (log scale)",
    yaxis_title="fitted slope",
    xaxis_type="log",
    template="plotly_white",
)
fig2.write_html("part1_huber_sweep.html")
print("wrote part1_huber_sweep.html")


# --- maximum-likelihood tie-in -------------------------------------------
#
# Claim from the deck:
#   Gaussian noise  ->  the MLE of w is the value that MINIMISES squared error
#   Laplace noise   ->  the MLE of w is the value that MINIMISES absolute error
#
# We check it directly. Use a clean through-the-origin model y = w*x + noise so
# there is a single parameter w to grid-search over.


def mle_check(noise_kind):
    xc = rng.uniform(0, 10, 400)
    true_w = 2.0
    if noise_kind == "gaussian":
        yc = true_w * xc + rng.normal(scale=2.0, size=xc.size)
    else:  # laplace
        yc = true_w * xc + rng.laplace(scale=2.0, size=xc.size)

    w_grid = np.linspace(1.0, 3.0, 4001)
    # squared-error objective and absolute-error objective as functions of w
    sse = [(np.sum((yc - w * xc) ** 2)) for w in w_grid]
    sae = [(np.sum(np.abs(yc - w * xc))) for w in w_grid]
    # negative log-likelihoods (drop constants that don't depend on w):
    #   Gaussian nll ~ sum of squared residuals
    #   Laplace  nll ~ sum of absolute residuals
    w_mse = w_grid[int(np.argmin(sse))]
    w_mae = w_grid[int(np.argmin(sae))]
    return w_mse, w_mae


print()
print("Maximum-likelihood tie-in (true w = 2.000):")
for kind in ("gaussian", "laplace"):
    w_mse, w_mae = mle_check(kind)
    match = "MSE" if kind == "gaussian" else "MAE"
    print(
        f"  {kind:>8} noise:  argmin SSE = {w_mse:.3f}   argmin SAE = {w_mae:.3f}"
        f"   -> {match} matches the MLE"
    )


# =====================================================================
# Part 2 - Classification losses
# =====================================================================
#
# Everything here is a function of the SIGNED MARGIN
#       m = y * f(x),      with y encoded as +1 / -1
# m > 0 means "correct", and larger m means "more confidently correct".


def zero_one(m):
    return (m < 0).astype(float)


def hinge(m):
    return np.maximum(0.0, 1.0 - m)


def logistic(m):
    # log(1 + e^-m), written in the numerically stable way
    return np.logaddexp(0.0, -m)


# --- figure: the three losses vs the margin ------------------------------
m = np.linspace(-3, 3, 400)
fig3 = go.Figure()
fig3.add_scatter(
    x=m,
    y=zero_one(m),
    mode="lines",
    name="0-1 loss",
    line=dict(color="#f87171", width=3),
)
fig3.add_scatter(
    x=m,
    y=hinge(m),
    mode="lines",
    name="hinge loss",
    line=dict(color="#60a5fa", width=3),
)
fig3.add_scatter(
    x=m,
    y=logistic(m),
    mode="lines",
    name="log loss",
    line=dict(color="#2dd4bf", width=3),
)
fig3.update_layout(
    title="Part 2: hinge and log loss are smooth surrogates for 0-1 loss",
    xaxis_title="signed margin  m = y * f(x)",
    yaxis_title="loss",
    template="plotly_white",
)
fig3.write_html("part2_surrogate_losses.html")
print()
print("=" * 64)
print("Part 2 - classification losses")
print("=" * 64)
print("wrote part2_surrogate_losses.html")

# --- why 0-1 loss cannot be optimised: its gradient is 0 almost everywhere -
h = 1e-3
fd = (zero_one(m + h) - zero_one(m - h)) / (2 * h)  # finite-difference slope
print(
    f"0-1 loss: finite-difference slope is {np.abs(fd).max():.1f} at every "
    f"tested margin except the jump at m = 0."
)
print(
    "  -> gradient descent gets no direction to move the parameters. That is "
    "why we train on a smooth surrogate instead."
)


# --- train a linear classifier by gradient descent ----------------------
# Two-class blobs with deliberate overlap.
Xc, yc01 = make_blobs(
    n_samples=200, centers=[(-1.5, -1.5), (1.5, 1.5)], cluster_std=2.2, random_state=0
)
yc_pm = np.where(yc01 == 1, 1.0, -1.0)  # +1 / -1 encoding for hinge
X_aug = np.c_[Xc, np.ones(len(Xc))]  # add a column of 1s so b is just w[2]


def sigmoid(z):
    return 1.0 / (1.0 + np.exp(-z))


def train_hinge(X, y_pm, lr=0.01, steps=5000):
    w = np.zeros(X.shape[1])
    for _ in range(steps):
        margin = y_pm * (X @ w)
        active = margin < 1  # points inside / violating the margin
        # gradient of mean hinge:  -y*x on the active points, 0 elsewhere
        grad = -(X * (y_pm * active)[:, None]).mean(axis=0)
        w -= lr * grad
    return w


def train_logloss(X, y01, lr=0.05, steps=5000, pos_weight=1.0):
    w = np.zeros(X.shape[1])
    # weight vector: pos_weight for the positive class, 1 for the negative class
    sample_w = np.where(y01 == 1, pos_weight, 1.0)
    for _ in range(steps):
        p = sigmoid(X @ w)
        # weighted logistic-regression gradient:  mean( wt * (p - y) * x )
        grad = (X * (sample_w * (p - y01))[:, None]).mean(axis=0)
        w -= lr * grad
    return w


w_hinge = train_hinge(X_aug, yc_pm)
w_log = train_logloss(X_aug, yc01)


def boundary_line(w, xs):
    # decision boundary is w0*x + w1*y + w2 = 0  ->  y = -(w0*x + w2) / w1
    return -(w[0] * xs + w[2]) / w[1]


xs = np.linspace(Xc[:, 0].min(), Xc[:, 0].max(), 50)
fig4 = go.Figure()
for cls, color in [(0, "#f59e0b"), (1, "#2dd4bf")]:
    pts = Xc[yc01 == cls]
    fig4.add_scatter(
        x=pts[:, 0],
        y=pts[:, 1],
        mode="markers",
        name=f"class {cls}",
        marker=dict(color=color, size=7),
    )
fig4.add_scatter(
    x=xs,
    y=boundary_line(w_hinge, xs),
    mode="lines",
    name="hinge boundary",
    line=dict(color="#60a5fa", width=3),
)
fig4.add_scatter(
    x=xs,
    y=boundary_line(w_log, xs),
    mode="lines",
    name="log-loss boundary",
    line=dict(color="#a78bfa", width=3),
)
fig4.update_layout(
    title="Part 2: decision boundaries from hinge vs log loss",
    xaxis_title="x1",
    yaxis_title="x2",
    template="plotly_white",
)
fig4.write_html("part2_decision_boundaries.html")
print("wrote part2_decision_boundaries.html")


# --- the cross-entropy table: confident + wrong is punished hardest -------
def log_loss_one(y, p):
    p = np.clip(p, 1e-7, 1 - 1e-7)  # keep log() away from 0
    return -(y * np.log(p) + (1 - y) * np.log(1 - p))


print()
print("Cross-entropy for a true label y = 1:")
for p in (0.99, 0.5, 0.01):
    print(f"  p_hat = {p:<5}  log loss = {log_loss_one(1, p):.2f}")
print(
    f"  p_hat = 0.0    log loss = {log_loss_one(1, 0.0):.2f}  "
    f"(would be +inf without the clip -> NaN in training)"
)


# --- cost-sensitive log loss: make false negatives 10x as expensive -----
w_log_cost = train_logloss(X_aug, yc01, pos_weight=10.0)


def confusion(w, X, y01):
    pred = (sigmoid(X @ w) >= 0.5).astype(int)
    tp = int(((pred == 1) & (y01 == 1)).sum())
    fn = int(((pred == 0) & (y01 == 1)).sum())
    fp = int(((pred == 1) & (y01 == 0)).sum())
    tn = int(((pred == 0) & (y01 == 0)).sum())
    return tp, fn, fp, tn


print()
print("Cost-sensitive log loss (10x weight on the positive class):")
for label, w in [("equal weights ", w_log), ("10x FN weight ", w_log_cost)]:
    tp, fn, fp, tn = confusion(w, X_aug, yc01)
    print(f"  {label}:  false negatives = {fn:>2}   false positives = {fp:>2}")
print(
    "  Up-weighting the positive class pushes the boundary so fewer true "
    "positives are missed, at the cost of more false positives."
)

fig4.add_scatter(
    x=xs,
    y=boundary_line(w_log_cost, xs),
    mode="lines",
    name="log loss, 10x FN weight",
    line=dict(color="#f472b6", width=3, dash="dash"),
)
fig4.write_html("part2_decision_boundaries.html")

print()
print("Done. Open the four part*.html files to see the figures.")
