---
theme: default
highlighter: shiki
css: unocss
colorSchema: dark
title: 'Linear Regression: Closed-Form and Gradient Descent'
info: |
  ## Linear Regression: Closed-Form and Gradient Descent
  Two routes to the same least-squares solution.
class: text-center
transition: fade-out
lineNumbers: false
drawings:
  persist: false
mdc: true
vite:
  server:
    fs:
      strict: false
glowSeed: 301
---

# Linear Regression

### Closed-Form and Gradient Descent

<div class="pt-5 opacity-80 text-lg">Our first complete machine-learning algorithm</div>

<svg viewBox="0 0 760 235" class="w-full max-w-3xl mx-auto mt-4" role="img" aria-label="Scatter plot with an animated best-fit line">
  <line x1="55" y1="205" x2="720" y2="205" stroke="#64748b" stroke-width="2"/>
  <line x1="55" y1="205" x2="55" y2="20" stroke="#64748b" stroke-width="2"/>
  <g fill="#e2e8f0">
    <circle cx="105" cy="177" r="6"/><circle cx="170" cy="166" r="6"/><circle cx="238" cy="139" r="6"/>
    <circle cx="305" cy="128" r="6"/><circle cx="375" cy="104" r="6"/><circle cx="445" cy="96" r="6"/>
    <circle cx="520" cy="69" r="6"/><circle cx="590" cy="62" r="6"/><circle cx="665" cy="38" r="6"/>
  </g>
  <path d="M80 190 L690 30" fill="none" stroke="#2dd4bf" stroke-width="5" stroke-linecap="round" class="fit-line"/>
  <path d="M80 190 L160 190" stroke="#60a5fa" stroke-width="3"/><path d="M160 190 L160 169" stroke="#60a5fa" stroke-width="3"/>
  <text x="92" y="218" fill="#94a3b8" style="font-size: 14px">run</text><text x="164" y="184" fill="#94a3b8" style="font-size: 14px">rise = slope</text>
  <text x="580" y="34" fill="#5eead4" style="font-size: 15px">ŷ = w₀ + w₁x</text>
</svg>

<div class="text-sm opacity-60">Topic 1 of Supervised Learning: Regression</div>

<style>
.fit-line { stroke-dasharray: 640; animation: draw-fit 2.2s ease-out both; }
@keyframes draw-fit { from { stroke-dashoffset: 640; } to { stroke-dashoffset: 0; } }
</style>

<!--
This is the first complete, end-to-end machine learning algorithm in the course, and everything from the Mathematical Foundations unit lands here. Matrix notation from linear algebra gives a compact way to write predictions for an entire dataset at once. The Gaussian maximum-likelihood argument from probability tells us why squared error, rather than some other loss, is the natural objective. Matrix calculus lets us differentiate that objective with respect to an entire vector of weights at once instead of one coordinate at a time. Gradient descent, from the optimization unit, gives a general-purpose way to search for a minimizer even when no closed form exists. Today these four threads combine into one concrete, useful algorithm, and we introduce a model → loss → optimizer template that every later supervised-learning method in this course reuses, changing only the model and the loss.
-->

---
glowSeed: 302
---

# The Linear Regression Model

<div class="grid grid-cols-2 gap-7 mt-4 items-center text-left">

<div>

<div border="2 solid teal-800" bg="teal-800/20" rounded-lg p-4>

$$
\hat y_i=w_0+w_1x_{i1}+\cdots+w_dx_{id}=x_i^\top w
$$

$$
\hat y=Xw
$$

</div>

<v-clicks>

- $n$ rows are training examples
- $d$ columns are model inputs
- prepend ones to absorb the intercept
- prediction becomes one matrix multiply

</v-clicks>

<div v-click class="mt-3 text-sm opacity-75">

With the bias column included: $X\in\mathbb R^{n\times(d+1)}$ and $w\in\mathbb R^{d+1}$.

</div>

</div>

<div v-click>
<svg viewBox="0 0 420 320" class="w-full" role="img" aria-label="Design matrix with highlighted bias column">
  <rect x="28" y="22" width="270" height="245" rx="12" fill="#ffffff0d" stroke="#475569" stroke-width="2"/>
  <rect x="45" y="40" width="54" height="210" rx="8" fill="#0f766e55" stroke="#2dd4bf" stroke-width="3"/>
  <g fill="#f8fafc" text-anchor="middle" style="font-size: 22px">
    <text x="72" y="75">1</text><text x="72" y="117">1</text><text x="72" y="159">1</text><text x="72" y="201">⋮</text><text x="72" y="237">1</text>
    <text x="135" y="75">x₁₁</text><text x="135" y="117">x₂₁</text><text x="135" y="159">x₃₁</text><text x="135" y="201">⋮</text><text x="135" y="237">xₙ₁</text>
    <text x="215" y="75">⋯</text><text x="215" y="117">⋯</text><text x="215" y="159">⋯</text><text x="215" y="201">⋱</text><text x="215" y="237">⋯</text>
    <text x="267" y="75">x₁d</text><text x="267" y="117">x₂d</text><text x="267" y="159">x₃d</text><text x="267" y="201">⋮</text><text x="267" y="237">xₙd</text>
  </g>
  <path d="M70 272 L70 300 L340 300" fill="none" stroke="#2dd4bf" stroke-width="2"/>
  <text x="350" y="306" fill="#5eead4" style="font-size: 15px">bias trick</text>
  <text x="330" y="95" fill="#94a3b8" style="font-size: 16px">features</text><path d="M319 102 L285 120" stroke="#94a3b8" stroke-width="2"/>
</svg>
</div>

</div>

<!--
Define every symbol before using it, because the rest of the lecture builds on this notation. n is the number of training examples (rows of X); d is the number of input features before the bias trick; x_i is the feature vector for a single example i; w is the weight vector we are trying to learn, with one entry per feature plus one for the intercept w_0. Prepending a column of ones to X is the "bias trick": it turns the intercept from a special-cased additive constant into an ordinary coefficient that multiplies a feature that is always equal to 1. After this trick, X has shape n×(d+1), w has shape (d+1)×1, and the entire model for all n examples simultaneously collapses into one matrix expression, ŷ = Xw. Also plant a distinction that resurfaces heavily next lecture: "linear model" means linear in the parameters w, not linear in the inputs x — that is exactly what lets us later feed in polynomial features of x while every derivation in this lecture stays unchanged.
-->

---
glowSeed: 303
---

# Why Squared Error?

<div class="grid grid-cols-2 gap-8 mt-5 items-center text-left">

<div>

<div border="2 solid blue-800" bg="blue-800/20" rounded-lg p-4>

$$
J(w)=\sum_{i=1}^{n}(y_i-x_i^\top w)^2=\|y-Xw\|_2^2
$$

</div>

<v-clicks>

- residual: $r_i=y_i-\hat y_i$
- squaring prevents cancellation
- large mistakes receive larger penalties
- $J(w)$ is a convex quadratic in $w$

</v-clicks>

</div>

<div>
<div v-click border="2 solid white/5" bg="white/5" rounded-lg p-4>
<div class="font-bold text-teal-300 mb-3">Gaussian noise makes it MLE</div>

$$y_i=x_i^\top w+\epsilon_i,\qquad \epsilon_i\sim\mathcal N(0,\sigma^2)$$

$$-\log p(y\mid X,w)=\text{constant}+\frac{1}{2\sigma^2}J(w)$$

</div>

<div v-click class="mt-5 text-center text-lg" border="2 solid teal-800" bg="teal-800/20" rounded-lg p-4>
Minimizing squared error = maximizing likelihood
</div>
</div>

</div>

<!--
Squared error is not chosen for convenience — it falls out of a probabilistic assumption. Assume each observed target is the true linear signal plus independent Gaussian noise, y_i = x_i^T w + ε_i with ε_i ~ N(0, σ²). The likelihood of the observed data is then a product of Gaussian densities, and maximizing that likelihood — equivalently, minimizing its negative log — is algebraically identical to minimizing the sum of squared residuals J(w). That is why "least squares" and "maximum likelihood under Gaussian noise" are the same estimator wearing two names; this is the payoff of the probability unit's MLE derivation applied to a concrete model. Separately, note that J(w) is a convex quadratic function of w: its graph is a bowl with no flat regions and no false valleys. That convexity is what justifies everything for the rest of the lecture — both the closed-form solution and gradient descent are guaranteed to find the global optimum only because there is exactly one basin to fall into.
-->

---
glowSeed: 304
---

# The Loss Really Is a Bowl

<div class="grid grid-cols-2 gap-8 mt-2 items-center">

<div>
<svg viewBox="0 0 470 350" class="w-full" role="img" aria-label="Elliptical contours of squared error with a unique minimum">
  <defs><radialGradient id="bowl" cx="50%" cy="50%"><stop offset="0" stop-color="#2dd4bf" stop-opacity=".35"/><stop offset="1" stop-color="#1e3a8a" stop-opacity=".03"/></radialGradient></defs>
  <rect x="25" y="20" width="420" height="300" rx="16" fill="url(#bowl)" stroke="#334155"/>
  <g fill="none" transform="rotate(-20 235 170)">
    <ellipse cx="235" cy="170" rx="185" ry="100" stroke="#2563eb" stroke-width="3"/>
    <ellipse cx="235" cy="170" rx="140" ry="76" stroke="#3b82f6" stroke-width="3"/>
    <ellipse cx="235" cy="170" rx="96" ry="51" stroke="#38bdf8" stroke-width="3"/>
    <ellipse cx="235" cy="170" rx="50" ry="27" stroke="#5eead4" stroke-width="3"/>
  </g>
  <circle cx="235" cy="170" r="8" fill="#f8fafc"/>
  <text x="250" y="163" fill="#f8fafc" style="font-size: 15px">global minimum</text>
  <text x="220" y="343" fill="#94a3b8" style="font-size: 14px">w₀</text><text x="8" y="40" fill="#94a3b8" style="font-size: 14px">w₁</text>
</svg>
</div>

<div class="text-left">

$$
J(w)=(y-Xw)^\top(y-Xw)
$$

<div class="grid grid-cols-1 gap-4 mt-7">
<div v-click border="2 solid teal-800" bg="teal-800/20" rounded-lg p-4><strong>One basin</strong><div class="text-sm opacity-75 mt-1">No local minima to trap an optimizer.</div></div>
<div v-click border="2 solid blue-800" bg="blue-800/20" rounded-lg p-4><strong>Elliptical contours</strong><div class="text-sm opacity-75 mt-1">Feature scales and correlations stretch the bowl.</div></div>
<div v-click border="2 solid amber-800" bg="amber-800/20" rounded-lg p-4><strong>Two solution routes</strong><div class="text-sm opacity-75 mt-1">Jump to the bottom algebraically or walk downhill.</div></div>
</div>

</div>

</div>

<!--
Take the picture literally, not as a metaphor: plotting J(w) against two weights produces an actual three-dimensional bowl, and the contour lines drawn here are its cross-sections at equal loss values, like a topographic map. Convexity guarantees a single global minimum, marked by the white dot — no local minima can trap an optimizer here, unlike the loss landscapes we will encounter with neural networks much later in the course. The contours are ellipses rather than circles whenever features are correlated or have different scales; the more elongated and tilted the ellipses, the more the loss changes sharply along one direction and slowly along another. That elongation previews two ideas coming up shortly: gradient descent can zig-zag inefficiently across a narrow, tilted valley, and standardizing features tends to make the bowl rounder and therefore easier to descend efficiently.
-->

---
glowSeed: 305
---

# Deriving the Normal Equations — Expand and Differentiate

<div class="mt-5" border="2 solid white/10" bg="white/5" rounded-lg px-6 py-5>

$$ {1|2|3|4}
\begin{aligned}
J(w) &= (y-Xw)^\top(y-Xw) \\
     &= y^\top y - y^\top Xw - w^\top X^\top y + w^\top X^\top Xw \\
     &= y^\top y - 2w^\top X^\top y + w^\top X^\top Xw \\
\nabla_wJ(w) &= -2X^\top y+2X^\top Xw
\end{aligned}
$$

</div>

<div v-click class="grid grid-cols-2 gap-4 mt-5 text-sm text-left">
<div bg="white/5" rounded-lg p-3>

$y^\top Xw$ is a $1\times1$ scalar, so it equals its own transpose: $y^\top Xw=(y^\top Xw)^\top=w^\top X^\top y$ — that is how the two middle terms combine into one

</div>
<div bg="white/5" rounded-lg p-3>

$\nabla_w(w^\top b)=b,\quad \nabla_w(w^\top Aw)=2Aw$ when $A$ is symmetric ($X^\top X$ always is)

</div>
</div>

<!--
Work line by line, the same way you would differentiate a single-variable quadratic: expand the product, collapse duplicate terms, then differentiate. The one nonobvious step is combining the two middle terms after expansion. y^T X w and w^T X^T y look different, but both are 1x1 scalars — a number has only one transpose of itself — so y^T X w = (y^T X w)^T = w^T X^T y, and the two terms add to 2 w^T X^T y. The final gradient uses two matrix-calculus identities from the calculus unit: the gradient of a linear form w^T b with respect to w is simply b, and the gradient of a quadratic form w^T A w is 2Aw whenever A is symmetric — X^T X is always symmetric, since (X^T X)^T = X^T X regardless of X. Next we set this gradient to zero and solve for the minimizing w.
-->

---
glowSeed: 314
---

# Deriving the Normal Equations — Solve for ŵ

<div class="mt-5" border="2 solid white/10" bg="white/5" rounded-lg px-6 py-5>

$$ {1|2|3}
\begin{aligned}
\nabla_wJ(w) &= -2X^\top y+2X^\top Xw \\
0 &= -2X^\top y+2X^\top X\hat w \qquad \text{(first-order condition)} \\
X^\top X\hat w &= X^\top y
\end{aligned}
$$

</div>

<div v-click class="mt-7" border="2 solid teal-800" bg="teal-800/20" rounded-lg px-6 py-5 text-center>

$$
\boxed{\hat w=(X^\top X)^{-1}X^\top y}
$$

</div>

<div v-click class="mt-5 text-sm text-center opacity-75">
Valid whenever $X^\top X$ is invertible, i.e. whenever $X$ has full column rank.
</div>

<!--
Because J(w) is convex, the first-order condition — setting the gradient to the zero vector — is not just necessary but also sufficient for a global minimum: there is no other critical point to rule out, unlike in a general nonconvex optimization problem. Setting -2X^T y + 2X^T X w equal to zero and dividing by 2 gives the normal equations, X^T X ŵ = X^T y: a system of d+1 linear equations in the d+1 unknown weights. Left-multiplying both sides by (X^T X)^{-1}, when that inverse exists, isolates ŵ directly — no search, no iteration, no learning rate. This closed-form solution exists precisely because the loss is quadratic; almost no other loss function used in this course admits one. The very next slide works this formula through actual numbers so it stops being an abstract symbol manipulation.
-->

---
glowSeed: 315
---

# A Worked Example, By Hand

<div class="grid grid-cols-2 gap-7 mt-3 text-left">

<div>

Three points $(x,y)$: $(1,2)$, $(2,3)$, $(3,5)$.

$$
X=\begin{bmatrix}1&1\\1&2\\1&3\end{bmatrix}
\qquad
y=\begin{bmatrix}2\\3\\5\end{bmatrix}
$$

<div v-click class="mt-3">

$$
X^\top X=\begin{bmatrix}3&6\\6&14\end{bmatrix}
\qquad
X^\top y=\begin{bmatrix}10\\23\end{bmatrix}
$$

</div>

<div v-click class="mt-3">

$$
(X^\top X)^{-1}=\frac{1}{6}\begin{bmatrix}14&-6\\-6&3\end{bmatrix}
\;\Longrightarrow\;
\hat w=\begin{bmatrix}1/3\\3/2\end{bmatrix}
$$

</div>

</div>

<div>

```python
import numpy as np

X = np.array([[1., 1.], [1., 2.], [1., 3.]])
y = np.array([2., 3., 5.])

w, *_ = np.linalg.lstsq(X, y, rcond=None)
print(w)   # [0.333..., 1.5]
```

<div v-click class="mt-4 text-sm" border="2 solid teal-800" bg="teal-800/20" rounded-lg p-4>
By-hand algebra and the numerical solver agree: intercept ≈ 0.33, slope = 1.5.
</div>

</div>

</div>

<!--
Walk through the arithmetic once so the boxed formula stops feeling abstract. The first column of ones and the x-values 1, 2, 3 give X^T X entries: the top-left is the number of rows (3), the off-diagonal is the sum of x-values (1+2+3=6), and the bottom-right is the sum of squared x-values (1+4+9=14). X^T y stacks the sum of y-values (10) and the sum of x times y (1·2+2·3+3·5=23). The 2×2 inverse uses the determinant, 3·14−6·6=6, giving the matrix shown. Multiplying that inverse by X^T y produces ŵ=(1/3, 3/2): an intercept near 0.33 and a slope of exactly 1.5. Note the slope matches the naive average rate of change from the first to last point, (5−2)/(3−1)=1.5, which is a useful sanity check on any hand computation like this one. The code confirms the same answer via a numerically stable solver rather than the explicit inverse.
-->

---
glowSeed: 306
---

# Closed Form in NumPy: Solve, Do Not Invert

<div class="grid grid-cols-2 gap-7 mt-3 text-left">

<div>

```python {1-4|6-7|9-10|all}
import numpy as np

X_raw = np.array([[1200], [1500], [1800], [2200.]])
y = np.array([300_000, 340_000, 400_000, 480_000.])

X = np.c_[np.ones(len(X_raw)), X_raw]
w, *_ = np.linalg.lstsq(X, y, rcond=None)

print(f"intercept={w[0]:,.0f}")
print(f"slope={w[1]:.2f} dollars / ft²")
```

</div>

<div>
<div v-click border="2 solid red-800" bg="red-800/20" rounded-lg p-4>
<div class="font-bold text-red-300">Pedagogical formula</div>
<code>inv(X.T @ X) @ X.T @ y</code>
<div class="text-sm opacity-75 mt-2">Forms an inverse explicitly and amplifies numerical error.</div>
</div>

<div v-click class="mt-4" border="2 solid teal-800" bg="teal-800/20" rounded-lg p-4>
<div class="font-bold text-teal-300">Practical computation</div>
<code>np.linalg.lstsq(X, y)</code>
<div class="text-sm opacity-75 mt-2">Uses a stable least-squares solver and also handles rank deficiency.</div>
</div>

<div v-click class="mt-5 text-center text-lg">Understand the inverse; <strong>call the solver.</strong></div>
</div>

</div>

<!--
This slide is deliberately about the gap between the formula on the board and the code you should actually write. The literal transcription of ŵ=(X^T X)^{-1}X^T y — computing inv(X.T @ X) @ X.T @ y — is worth showing once because it matches the derivation exactly, but it is bad practice: forming an explicit matrix inverse squares the condition number of the problem, amplifying floating-point error, and it does unnecessary work when all we actually need is the solution to a linear system, not the inverse itself. np.linalg.lstsq solves the same normal equations through a QR or SVD factorization of X directly, without ever forming X^T X or inverting anything, so it is both faster and numerically safer, and it degrades gracefully — returning a minimum-norm solution — even when X is rank-deficient, which an explicit inverse cannot do at all. The rule of thumb to leave students with: understand the inverse to follow the derivation, but never call it in real code.
-->

---
glowSeed: 307
---

# When the Inverse Does Not Exist

<div class="grid grid-cols-2 gap-8 mt-3 items-center text-left">

<div>
<svg viewBox="0 0 430 310" class="w-full" role="img" aria-label="Two redundant feature vectors lying on the same line">
  <line x1="45" y1="260" x2="390" y2="260" stroke="#64748b" stroke-width="2"/><line x1="45" y1="260" x2="45" y2="25" stroke="#64748b" stroke-width="2"/>
  <line x1="65" y1="240" x2="355" y2="50" stroke="#334155" stroke-width="8" opacity=".6"/>
  <path d="M80 230 L220 138" stroke="#60a5fa" stroke-width="6" marker-end="url(#arrow-blue)"/>
  <path d="M80 230 L340 60" stroke="#f59e0b" stroke-width="6" marker-end="url(#arrow-orange)"/>
  <defs>
    <marker id="arrow-blue" markerWidth="8" markerHeight="8" refX="7" refY="4" orient="auto"><path d="M0,0 L8,4 L0,8 Z" fill="#60a5fa"/></marker>
    <marker id="arrow-orange" markerWidth="8" markerHeight="8" refX="7" refY="4" orient="auto"><path d="M0,0 L8,4 L0,8 Z" fill="#f59e0b"/></marker>
  </defs>
  <text x="180" y="167" fill="#93c5fd" style="font-size: 16px">x₂</text><text x="310" y="78" fill="#fbbf24" style="font-size: 16px">x₃ = 2x₂</text>
  <text x="95" y="288" fill="#94a3b8" style="font-size: 14px">two columns, one direction</text>
</svg>
</div>

<div>

$$
X^\top X\text{ singular}
\iff \operatorname{rank}(X)<d
$$

<v-clicks>

- perfectly redundant features
- more columns than examples
- multiple weight vectors make identical predictions
- naive matrix inversion fails

</v-clicks>

```python
X_bad = np.array([[1, 2, 4],
                  [1, 3, 6],
                  [1, 4, 8.]])
print(np.linalg.matrix_rank(X_bad))  # 2, not 3
```

<div v-click class="mt-3 text-sm" border="2 solid violet-800" bg="violet-800/20" rounded-lg p-3>

Next lecture: ridge adds $\lambda I$, restoring invertibility.

</div>

</div>

</div>

<!--
This connects the rank concept from the Linear Algebra unit directly to whether regression has a unique answer. X^T X is a d×d matrix, and it is invertible exactly when X has full column rank — that is, when no feature column can be written as a linear combination of the others. The diagram shows the failure mode concretely: if x₃ = 2x₂, the two columns point along the same direction, so increasing w₂ by 1 and decreasing w₃ by 0.5 leaves every prediction exactly unchanged. Infinitely many weight vectors then fit the data identically well, X^T X becomes singular, and det(X^T X)=0 means no inverse exists. The same failure occurs whenever there are more columns than rows (d+1 > n), since n data points cannot pin down more than n independent directions. Importantly, the predictions ŷ=Xw can still be perfectly well defined and useful even when the specific coefficients w are not unique — it is the coefficients, not the fit, that become ambiguous. Next lecture's ridge penalty fixes this by adding λI before inverting, which we will show algebraically guarantees a unique, invertible solution for any λ>0.
-->

---
glowSeed: 308
---

# Gradient Descent Uses the Same Gradient

<div class="grid grid-cols-2 gap-8 mt-4 text-left items-center">

<div>

<div border="2 solid teal-800" bg="teal-800/20" rounded-lg p-4>

$$
J_{\text{MSE}}(w)=\frac{1}{n}\|y-Xw\|_2^2=\frac{1}{n}J(w)
$$

$$
\nabla_wJ_{\text{MSE}}(w)=\frac{2}{n}X^\top(Xw-y)
$$

$$
w_{t+1}=w_t-\alpha\nabla_wJ_{\text{MSE}}(w_t)
$$

</div>

<v-clicks>

- start from any $w_0$
- compute the current slope of the loss
- step in the opposite direction
- stop when improvement becomes negligible

</v-clicks>

</div>

<div>

```python {1-2|4-6|7|all}
def fit_gd(X, y, learning_rate=.08, steps=2_000):
    w = np.zeros(X.shape[1])

    for _ in range(steps):
        residuals = X @ w - y
        gradient = 2 / len(y) * X.T @ residuals
        w -= learning_rate * gradient
    return w
```

<div v-click class="mt-4 text-sm" border="2 solid amber-800" bg="amber-800/20" rounded-lg p-3>
Use standardized features here; otherwise one large-scale column can dominate the gradient.
</div>

</div>

</div>

<!--
This is the exact gradient from the closed-form derivation, rescaled by 1/n. The earlier slides worked with J(w)=‖y−Xw‖₂², a sum over n examples, because that made the normal-equations algebra cleanest. Practical gradient descent implementations instead minimize the mean squared error J_MSE(w)=(1/n)J(w), and dividing a function by the constant n only rescales its gradient by 1/n — it does not move the location of the minimum, so ŵ is identical either way. The reason for the rescaling is practical, not mathematical: without the 1/n, the gradient's magnitude — and therefore how large a step size α is stable — would depend on the dataset size n, so doubling your training set would silently require halving your learning rate. Dividing by n makes α a property of the loss landscape's shape rather than of how many rows happen to be in the training set, which is exactly what the code computes with `2 / len(y) * X.T @ residuals`. Point out explicitly that this is why the closed-form and gradient-descent slides use J and J_MSE respectively rather than a mismatched formula.
-->

---
glowSeed: 309
---

# Two Roads, Same Destination

<div class="grid grid-cols-[1.25fr_.75fr] gap-8 mt-2 items-center text-left">

<div>
<svg viewBox="0 0 520 365" class="w-full" role="img" aria-label="Gradient descent path across loss contours toward the closed-form minimum">
  <g fill="none" transform="rotate(-18 255 176)">
    <ellipse cx="255" cy="176" rx="220" ry="120" stroke="#1d4ed8" stroke-width="3"/>
    <ellipse cx="255" cy="176" rx="170" ry="91" stroke="#2563eb" stroke-width="3"/>
    <ellipse cx="255" cy="176" rx="120" ry="63" stroke="#38bdf8" stroke-width="3"/>
    <ellipse cx="255" cy="176" rx="67" ry="34" stroke="#2dd4bf" stroke-width="3"/>
  </g>
  <polyline points="55,66 148,225 205,128 239,193 255,159 264,180 255,176" fill="none" stroke="#f59e0b" stroke-width="5" stroke-linejoin="round" stroke-linecap="round" class="gd-path"/>
  <g fill="#fbbf24"><circle cx="55" cy="66" r="7"/><circle cx="148" cy="225" r="7"/><circle cx="205" cy="128" r="7"/><circle cx="239" cy="193" r="7"/><circle cx="255" cy="159" r="7"/><circle cx="264" cy="180" r="7"/></g>
  <circle cx="255" cy="176" r="10" fill="#f8fafc"/>
  <text x="275" y="173" fill="#f8fafc" style="font-size: 14px">closed form</text>
  <text x="50" y="48" fill="#fbbf24" style="font-size: 14px">GD start</text>
</svg>
</div>

<div class="space-y-4">
<div v-click border="2 solid teal-800" bg="teal-800/20" rounded-lg p-4><strong>Closed form</strong><div class="text-sm opacity-75 mt-2">lands at ŵ directly</div></div>
<div v-click border="2 solid amber-800" bg="amber-800/20" rounded-lg p-4><strong>Gradient descent</strong><div class="text-sm opacity-75 mt-2">approaches the same ŵ iteratively</div></div>
<div v-click class="text-center text-lg pt-2">Same objective.<br/><strong>Same optimum.</strong></div>
</div>

</div>

<style>
.gd-path { stroke-dasharray: 620; animation: walk-path 3.2s ease-out both; }
@keyframes walk-path { from { stroke-dashoffset: 620; } to { stroke-dashoffset: 0; } }
</style>

<!--
The zig-zag traces exactly the stretched geometry of the contours from two slides ago: because the gradient points perpendicular to the contour line at the current position, not directly at the minimum, each step overshoots along the steep direction and undershoots along the shallow one, producing the characteristic bent path. With a suitable learning rate — large enough to make real progress, small enough not to diverge — and enough iterations, gradient descent provably converges to the same point ŵ marked by the normal-equation solution, because J(w) is convex with a single global minimum. This is the central point of the whole lecture: closed form and gradient descent are two different algorithms solving the identical optimization problem, and for ordinary least squares they always agree on the answer, differing only in computational cost and how they get there.
-->

---
glowSeed: 310
---

# Scaling Makes the Walk Easier

<div class="grid grid-cols-2 gap-7 mt-4 text-center">

<div v-click border="2 solid orange-800" bg="orange-800/20" rounded-lg p-4>
<div class="font-bold text-orange-300">Raw scales</div>
<svg viewBox="0 0 360 230" class="w-full">
  <g fill="none" transform="rotate(-20 180 115)"><ellipse cx="180" cy="115" rx="155" ry="40" stroke="#fb923c" stroke-width="3"/><ellipse cx="180" cy="115" rx="105" ry="27" stroke="#fdba74" stroke-width="3"/><ellipse cx="180" cy="115" rx="55" ry="14" stroke="#fed7aa" stroke-width="3"/></g>
  <polyline points="55,50 120,168 163,83 190,139 180,115" fill="none" stroke="#f8fafc" stroke-width="4"/>
</svg>
<div class="text-sm opacity-80">narrow valley → tiny learning rate, zig-zag</div>
</div>

<div v-click border="2 solid teal-800" bg="teal-800/20" rounded-lg p-4>
<div class="font-bold text-teal-300">Standardized scales</div>
<svg viewBox="0 0 360 230" class="w-full">
  <circle cx="180" cy="115" r="92" fill="none" stroke="#0f766e" stroke-width="3"/><circle cx="180" cy="115" r="62" fill="none" stroke="#14b8a6" stroke-width="3"/><circle cx="180" cy="115" r="31" fill="none" stroke="#5eead4" stroke-width="3"/>
  <polyline points="78,48 130,79 157,98 174,110 180,115" fill="none" stroke="#f8fafc" stroke-width="4"/>
</svg>
<div class="text-sm opacity-80">rounder bowl → direct, stable progress</div>
</div>

</div>

<div v-click class="mt-3 text-center text-lg" border="2 solid white/5" bg="white/5" rounded-lg px-6 py-3>
Standardize each feature: $x_j^{\text{scaled}}=(x_j-\mu_j)/\sigma_j$
</div>

<!--
Square footage measured in the thousands and a binary indicator living in {0, 1} create wildly different curvature along their respective axes of J(w): a small change in the square-footage weight moves the loss much more than an equal-sized change in the indicator's weight, because the feature values themselves differ by orders of magnitude. That asymmetry is exactly what stretches the bowl into a narrow ellipse. A single learning rate α must be small enough not to diverge along the steep direction, which then makes progress painfully slow along the shallow one — there is no single good α for a badly scaled problem. Standardizing every feature to zero mean and unit variance, x_scaled=(x−μ)/σ, does not change the information in the data or the optimal predictions; it only reparameterizes the optimization so the bowl is closer to circular, letting one learning rate work well in every direction simultaneously. This preprocessing step matters only for gradient-based solvers — the closed-form solution is invariant to feature scaling up to a corresponding rescaling of the coefficients.
-->

---
glowSeed: 311
---

# Which Solver Should You Use?

<div class="grid grid-cols-2 gap-7 mt-5 text-left">

<div v-click border="2 solid blue-800" bg="blue-800/20" rounded-lg overflow-hidden>
<div bg="blue-800/40" px-5 py-3 font-bold>Stable closed-form equivalent</div>
<div px-5 py-4>

- exact least-squares answer
- no learning rate or stopping rule
- excellent for small/medium dense problems
- use QR/SVD via `lstsq`, not explicit inversion

<div class="mt-3 text-sm opacity-75">Cost ≈ $O(nd^2+d^3)$ — cubic in the number of features $d$.</div>
</div>
</div>

<div v-click border="2 solid amber-800" bg="amber-800/20" rounded-lg overflow-hidden>
<div bg="amber-800/40" px-5 py-3 font-bold>Gradient-based optimization</div>
<div px-5 py-4>

- processes mini-batches
- scales to large datasets and feature sets
- needs tuning and a stopping criterion
- works when no closed form exists

<div class="mt-3 text-sm opacity-75">Cost ≈ $O(nd)$ per step — linear in $d$, repeated over many steps.</div>
</div>
</div>

</div>

<div v-click class="mt-8 flex justify-center items-center gap-4 text-lg">
<span border="2 solid white/10" bg="white/5" rounded-lg px-4 py-3>small / medium least squares</span><span class="text-teal-300">→</span><strong><code>lstsq</code> or <code>LinearRegression</code></strong>
</div>

<!--
This is not a contest with one universal winner, and the common misconception is thinking one method is simply "better." The deciding factor is cost as a function of d, the number of features. The direct solver costs roughly O(nd²+d³): forming or factoring X, an n×d matrix, costs O(nd²), and operations tied to the d×d matrix X^T X cost O(d³). When d is small to moderate — tens or low hundreds of features — that cubic term is negligible and the direct solver gives the exact answer in one shot with no tuning at all, which is strictly better than approximating it iteratively. Gradient descent costs roughly O(nd) per step, linear rather than cubic in d, so it becomes the only practical option once d grows into the thousands or millions, once the full dataset no longer fits comfortably in memory for a single factorization, or once you move to a model — like logistic regression or a neural network — that has no closed-form solution at all. The takeaway to state explicitly: prefer the closed form whenever it is available and affordable; reach for gradient-based optimization only when the problem's scale or structure rules the closed form out.
-->

---
glowSeed: 312
---

# Linear Regression in scikit-learn

<div class="grid grid-cols-[1.1fr_.9fr] gap-7 mt-2 text-left">

<div>

```python {1-3|5-6|8-9|11-12|all}
from sklearn.datasets import make_regression
from sklearn.linear_model import LinearRegression
from sklearn.metrics import mean_squared_error, r2_score
from sklearn.model_selection import train_test_split

X, y = make_regression(n_samples=200, n_features=3, noise=15,
                       random_state=0)
X_train, X_test, y_train, y_test = train_test_split(
    X, y, test_size=.25, random_state=0)

model = LinearRegression().fit(X_train, y_train)
y_pred = model.predict(X_test)

print("MSE:", mean_squared_error(y_test, y_pred))
print("R²:", r2_score(y_test, y_pred))
```

</div>

<div>
<div border="2 solid teal-800" bg="teal-800/20" rounded-lg p-4>

$$
R^2=1-\frac{\sum_i(y_i-\hat y_i)^2}{\sum_i(y_i-\bar y)^2}
$$

</div>

<div class="grid grid-cols-1 gap-3 mt-5 text-sm">
<div v-click bg="white/5" rounded-lg p-3><strong>R² = 1:</strong> perfect predictions</div>
<div v-click bg="white/5" rounded-lg p-3><strong>R² = 0:</strong> no better than the test-set mean baseline</div>
<div v-click bg="white/5" rounded-lg p-3><strong>R² &lt; 0:</strong> worse than that baseline</div>
</div>

<div v-click class="mt-4 text-sm opacity-75"><code>LinearRegression</code> fits the intercept automatically—do not prepend ones.</div>
</div>

</div>

<!--
This is the practical workflow students will actually use day to day: the derivation earlier in the lecture explains what `.fit()` computes internally, while scikit-learn handles the stable numerical details — internally it uses an SVD-based solver rather than the naive inverse. Always evaluate on a held-out test set rather than the training data, since training-set error is optimistic about how the model will perform on new data. MSE keeps the target's original units squared (dollars squared, for a house-price model), which makes it hard to interpret in isolation, while R² is unitless and comparable across problems: it measures the fraction of the target's variance explained by the model, relative to the naive baseline of always predicting the mean ȳ. An R² of 0 means the model is no better than that constant baseline, and a negative R² — which can happen on a bad test set — means it is actively worse. Also flag the API detail that trips people up: `LinearRegression` fits its own intercept internally, so unlike our by-hand derivation, do not prepend a column of ones to X here.
-->

---
layout: center
class: text-center
glowSeed: 313
---

# Keep the Template

<div class="grid grid-cols-3 gap-5 max-w-5xl mx-auto mt-8 text-left">
<div v-click border="2 solid teal-800" bg="teal-800/20" rounded-lg p-5><div class="text-3xl mb-2">📐</div><strong>Model</strong><div class="text-sm opacity-80 mt-2">ŷ = Xw</div></div>
<div v-click border="2 solid blue-800" bg="blue-800/20" rounded-lg p-5><div class="text-3xl mb-2">🎯</div><strong>Loss</strong><div class="text-sm opacity-80 mt-2">‖y − Xw‖₂²</div></div>
<div v-click border="2 solid amber-800" bg="amber-800/20" rounded-lg p-5><div class="text-3xl mb-2">🧭</div><strong>Optimizer</strong><div class="text-sm opacity-80 mt-2">closed form or GD</div></div>
</div>

<div v-click class="mt-10" border="2 solid white/10" bg="white/5" rounded-lg px-8 py-5 text-xl>

$$
\boxed{\hat w=(X^\top X)^{-1}X^\top y}
\qquad\Longleftrightarrow\qquad
\boxed{w_{t+1}=w_t-\alpha\nabla J(w_t)}
$$

</div>

<div v-click class="mt-8 text-xl">Next: <strong>Polynomial Regression and Regularization</strong></div>

<!--
Close on the reusable recipe that will recur for the rest of the course: define a model (how do inputs produce a prediction?), choose a loss (what makes a prediction good or bad?), and solve an optimization (search for the parameters minimizing that loss, either exactly or iteratively). For linear regression specifically, we derived the closed-form ŵ=(X^T X)^{-1}X^T y by hand from first principles — expand the loss, differentiate, set to zero, solve — and showed gradient descent walks toward that identical point using the same gradient. Next lecture keeps every piece of this machinery unchanged: the same squared-error loss, the same closed-form and gradient-descent solvers. The only new ingredient is transforming the input features nonlinearly before fitting a linear model on top of them, which lets us fit curves, and adding penalty terms to the loss that control how large the weights are allowed to grow, which both controls overfitting and repairs the singular-design problem from earlier in this lecture. Take questions before moving on.
-->
