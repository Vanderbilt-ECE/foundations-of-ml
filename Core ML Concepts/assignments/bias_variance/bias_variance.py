"""Bias-variance tradeoff by repeated fitting.

The true relationship is sin(1.5 pi x) -- NOT a polynomial. We fit polynomial
regression models of increasing degree (1-10), and for each degree we estimate
bias^2, variance, and total expected loss by retraining on many fresh random
samples. Because a sine is outside every polynomial class, bias declines
smoothly with degree instead of snapping to zero, giving the classic crossing
curves.

The inner loop is deliberately the same shape as the slide-8 snippet from the
"Bias-Variance Tradeoff" deck, so it should look familiar:

    predictions = []
    for _ in range(500):
        x = rng.uniform(0, 1, 20)
        y = true_f(x) + rng.normal(scale=.2, size=20)
        model = make_pipeline(PolynomialFeatures(1), LinearRegression())
        model.fit(x[:, None], y)
        predictions.append(model.predict([[.5]])[0])

Run with:  uv run bias_variance.py
"""

import numpy as np
from sklearn.preprocessing import PolynomialFeatures
from sklearn.linear_model import LinearRegression
from sklearn.pipeline import make_pipeline
import plotly.graph_objects as go

rng = np.random.default_rng(0)

# The ACTUAL function. It is deliberately NOT a polynomial: no polynomial degree
# can represent a sine exactly, so every degree keeps some bias and the bias
# curve declines *smoothly* instead of collapsing to zero at one magic degree.
# (Same true function as slide 8 of the Bias-Variance Tradeoff deck.)
true_f = lambda x: np.sin(1.5 * np.pi * x)

NOISE = 0.20      # std dev of the irreducible noise epsilon
N_TRAIN = 40      # points per training set
N_SETS = 400      # number of training sets drawn per degree

# Fixed test grid where we measure bias and variance.
x_test = np.linspace(0, 1, 100)
f_test = true_f(x_test)

degrees = range(1, 11)
bias_list, var_list, loss_list = [], [], []

for degree in degrees:
    # ---- same shape as the slide-8 snippet ----
    predictions = []
    for _ in range(N_SETS):
        x = rng.uniform(0, 1, N_TRAIN)
        y = true_f(x) + rng.normal(scale=NOISE, size=N_TRAIN)
        model = make_pipeline(PolynomialFeatures(degree), LinearRegression())
        model.fit(x[:, None], y)
        predictions.append(model.predict(x_test[:, None]))
    predictions = np.array(predictions)  # shape (N_SETS, len(x_test))
    # ------------------------------------------

    mean_pred = predictions.mean(axis=0)
    bias_sq = np.mean((mean_pred - f_test) ** 2)
    variance = np.mean(predictions.var(axis=0))
    total = np.mean((predictions - f_test) ** 2)  # empirical expected loss

    bias_list.append(bias_sq)
    var_list.append(variance)
    loss_list.append(total)

# ---- report ----
print(f"true function: sin(1.5 pi x)   noise sigma^2 = {NOISE**2:.4f}")
print(f"{'degree':>6}  {'bias^2':>10}  {'variance':>10}  {'total loss':>10}")
for d, b, v, t in zip(degrees, bias_list, var_list, loss_list):
    print(f"{d:>6}  {b:>10.5f}  {v:>10.5f}  {t:>10.5f}")

# ---- plot 1: bias / variance / total error vs degree ----
fig = go.Figure()
fig.add_scatter(x=list(degrees), y=bias_list, mode="lines+markers", name="bias&sup2;")
fig.add_scatter(x=list(degrees), y=var_list, mode="lines+markers", name="variance")
fig.add_scatter(x=list(degrees), y=loss_list, mode="lines+markers", name="total error")
fig.update_layout(
    title="Bias-variance tradeoff: polynomial degree vs sin(1.5&pi;x)",
    xaxis_title="Polynomial degree",
    yaxis_title="Error",
    yaxis_type="log",
    template="plotly_white",
)
fig.update_xaxes(dtick=1)
fig.write_html("bias_variance.html")
print("\nwrote bias_variance.html")
fig.show()

# ---- plot 2: one training sample with fitted polynomials overlaid ----
# Draw a single fresh sample (its own generator, so plot 1 stays reproducible)
# and fit a few representative degrees so the underfit / good / overfit contrast
# is visible by eye. The legend shows each degree's averaged total loss from the
# experiment above, so the "degree 4 is best" claim is quantified, not just drawn.
SHOWCASE_DEGREES = [1, 2, 4, 10]

demo_rng = np.random.default_rng(1)
x_demo = demo_rng.uniform(0, 1, N_TRAIN)
y_demo = true_f(x_demo) + demo_rng.normal(scale=NOISE, size=N_TRAIN)

fig2 = go.Figure()
fig2.add_scatter(
    x=x_demo, y=y_demo, mode="markers", name="one training sample",
    marker=dict(color="#94a3b8", size=7),
)
fig2.add_scatter(
    x=x_test, y=f_test, mode="lines", name="true f(x) = sin(1.5&pi;x)",
    line=dict(color="#f8fafc", width=3, dash="dash"),
)
for d in SHOWCASE_DEGREES:
    model = make_pipeline(PolynomialFeatures(d), LinearRegression())
    model.fit(x_demo[:, None], y_demo)
    y_hat = model.predict(x_test[:, None])
    fig2.add_scatter(
        x=x_test, y=y_hat, mode="lines",
        name=f"degree {d}  (avg loss {loss_list[d - 1]:.3f})",
    )
fig2.update_layout(
    title="One sample: underfit (deg 1) &rarr; good fit (deg 4) &rarr; overfit (deg 10)",
    xaxis_title="x",
    yaxis_title="y",
    yaxis=dict(range=[-2.5, 2.5]),
    template="plotly_white",
)
fig2.write_html("bias_variance_fits.html")
print("wrote bias_variance_fits.html")
fig2.show()
