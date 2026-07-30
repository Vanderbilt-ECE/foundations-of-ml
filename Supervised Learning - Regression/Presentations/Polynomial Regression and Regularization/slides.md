---
theme: default
highlighter: shiki
css: unocss
colorSchema: dark
title: 'Polynomial Regression and Regularization'
info: |
  ## Polynomial Regression and Regularization
  Fitting curves while controlling variance with ridge and lasso.
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
glowSeed: 341
---

# Polynomial Regression

### Ridge, Lasso, and the Price of Flexibility

<div class="pt-5 opacity-80 text-lg">Fit curves with a model that is still linear in its parameters</div>

<div class="grid grid-cols-3 gap-4 mt-8 text-sm">
<div border="2 solid blue-800" bg="blue-800/20" rounded-lg p-3>
<div class="font-bold text-blue-300">degree 1</div>
<svg viewBox="0 0 220 120" class="w-full"><g fill="#cbd5e1"><circle cx="20" cy="96" r="3"/><circle cx="50" cy="62" r="3"/><circle cx="82" cy="30" r="3"/><circle cx="118" cy="41" r="3"/><circle cx="154" cy="71" r="3"/><circle cx="198" cy="95" r="3"/></g><line x1="15" y1="82" x2="205" y2="53" stroke="#60a5fa" stroke-width="4"/></svg>
underfit
</div>
<div border="2 solid teal-800" bg="teal-800/20" rounded-lg p-3>
<div class="font-bold text-teal-300">degree 4</div>
<svg viewBox="0 0 220 120" class="w-full"><g fill="#cbd5e1"><circle cx="20" cy="96" r="3"/><circle cx="50" cy="62" r="3"/><circle cx="82" cy="30" r="3"/><circle cx="118" cy="41" r="3"/><circle cx="154" cy="71" r="3"/><circle cx="198" cy="95" r="3"/></g><path d="M15 103 Q91 2 205 103" fill="none" stroke="#2dd4bf" stroke-width="4"/></svg>
captures signal
</div>
<div border="2 solid orange-800" bg="orange-800/20" rounded-lg p-3>
<div class="font-bold text-orange-300">degree 15</div>
<svg viewBox="0 0 220 120" class="w-full"><g fill="#cbd5e1"><circle cx="20" cy="96" r="3"/><circle cx="50" cy="62" r="3"/><circle cx="82" cy="30" r="3"/><circle cx="118" cy="41" r="3"/><circle cx="154" cy="71" r="3"/><circle cx="198" cy="95" r="3"/></g><path d="M15 104 C32 116,35 45,50 62 S67 58,82 30 S102 57,118 41 S140 48,154 71 S178 119,205 91" fill="none" stroke="#fb923c" stroke-width="4" class="wiggle"/></svg>
overfit
</div>
</div>

<div class="mt-5 text-sm opacity-60">Topic 2 of Supervised Learning: Regression</div>

<style>
.wiggle { stroke-dasharray: 300; animation: reveal-wiggle 2.5s ease-out both; }
@keyframes reveal-wiggle { from { stroke-dashoffset: 300; } to { stroke-dashoffset: 0; } }
</style>

<!--
Open with the apparent paradox in the title: how can a "linear model" fit a visibly curved line? The resolution, which the next slide makes precise, is that "linear" describes how the model depends on its parameters w, not on the input x — we transform the features into powers of x, and then fit an ordinary linear model on top of that transformed representation, so every derivation from last lecture (the normal equations, the gradient, the solvers) carries over completely unchanged. The three panels preview the entire lecture's arc: degree 1 is too rigid to capture the curvature in the data (underfitting, high bias), degree 4 captures the true signal well, and degree 15 chases the specific noise in this one sample (overfitting, high variance) rather than the underlying pattern. Today's job is choosing the right amount of flexibility and controlling it directly through regularization.
-->

---
glowSeed: 342
---

# Expand the Features, Keep the Linear Model

<div class="grid grid-cols-[.9fr_1.1fr] gap-8 mt-4 items-center text-left">

<div>
<svg viewBox="0 0 430 315" class="w-full" role="img" aria-label="One input feature expands into polynomial feature columns">
  <rect x="20" y="70" width="82" height="170" rx="12" fill="#1e3a8a55" stroke="#60a5fa" stroke-width="3"/>
  <text x="61" y="48" text-anchor="middle" fill="#93c5fd" style="font-size: 18px">input</text>
  <g fill="#f8fafc" text-anchor="middle" style="font-size: 20px"><text x="61" y="112">x₁</text><text x="61" y="154">x₂</text><text x="61" y="196">⋮</text><text x="61" y="226">xₙ</text></g>
  <path d="M115 155 L165 155" stroke="#2dd4bf" stroke-width="4" marker-end="url(#poly-arrow)"/>
  <defs><marker id="poly-arrow" markerWidth="8" markerHeight="8" refX="7" refY="4" orient="auto"><path d="M0,0 L8,4 L0,8 Z" fill="#2dd4bf"/></marker></defs>
  <text x="140" y="135" text-anchor="middle" fill="#5eead4" style="font-size: 14px">φ</text>
  <rect x="180" y="35" width="225" height="240" rx="12" fill="#0f766e33" stroke="#2dd4bf" stroke-width="3"/>
  <text x="292" y="20" text-anchor="middle" fill="#5eead4" style="font-size: 18px">expanded design matrix</text>
  <g fill="#f8fafc" text-anchor="middle" style="font-size: 17px">
    <text x="210" y="78">1</text><text x="258" y="78">x₁</text><text x="317" y="78">x₁²</text><text x="375" y="78">x₁³</text>
    <text x="210" y="122">1</text><text x="258" y="122">x₂</text><text x="317" y="122">x₂²</text><text x="375" y="122">x₂³</text>
    <text x="210" y="170">⋮</text><text x="258" y="170">⋮</text><text x="317" y="170">⋮</text><text x="375" y="170">⋮</text>
    <text x="210" y="220">1</text><text x="258" y="220">xₙ</text><text x="317" y="220">xₙ²</text><text x="375" y="220">xₙ³</text>
  </g>
</svg>
</div>

<div>
<div border="2 solid teal-800" bg="teal-800/20" rounded-lg p-4>

$$
\hat y=w_0+w_1x+w_2x^2+\cdots+w_px^p=\phi(x)^\top w
$$

</div>

<v-clicks>

- nonlinear in the original input $x$
- linear in the learned parameters $w$
- same least-squares objective
- same closed-form or gradient-based solvers

</v-clicks>

<div v-click class="mt-4 text-sm" border="2 solid white/5" bg="white/5" rounded-lg p-3>“Linear model” describes how parameters enter the equation—not whether the plotted prediction is a straight line.</div>
</div>

</div>

<!--
Nothing about the previous lecture's fitting derivation changes at all — not the loss, not the normal equations, not the gradient. The only new step is a deterministic, fixed transformation φ from the raw input x into an expanded feature vector φ(x)=[1, x, x², ..., x^p], applied before anything else happens. Once that transformation is applied, ŷ=φ(x)^T w is exactly the same dot-product form as ŷ=x^T w from last lecture — the model is nonlinear as a function of the original x (the plotted curve visibly bends) but perfectly linear as a function of the parameters w (each parameter multiplies one fixed feature and the results add up). This is precisely what "linear model" technically means, and why the same closed-form and gradient-descent machinery solves both problems without modification. This general pattern — expand the input into a richer fixed feature space, then fit something linear on top — reappears throughout the course, most notably in kernel methods, where the expansion can even become infinite-dimensional.
-->

---
glowSeed: 343
---

# Polynomial Features in scikit-learn

<div class="grid grid-cols-2 gap-7 mt-3 text-left">

<div>

```python {1-3|5-7|9-10|all}
import numpy as np
from sklearn.linear_model import LinearRegression
from sklearn.pipeline import make_pipeline
from sklearn.preprocessing import PolynomialFeatures

rng = np.random.default_rng(0)
X = rng.uniform(-3, 3, 30).reshape(-1, 1)
y = .5 * X[:, 0]**3 - X[:, 0]**2 + rng.normal(0, 2, 30)

model = make_pipeline(
    PolynomialFeatures(degree=3, include_bias=False),
    LinearRegression()
).fit(X, y)
```

</div>

<div>
<div v-click border="2 solid blue-800" bg="blue-800/20" rounded-lg p-4>
<div class="font-bold text-blue-300 mb-2">Pipeline data flow</div>
<div class="flex items-center justify-between text-center mt-4">
<span bg="white/5" rounded-lg px-3 py-3>x</span><span class="text-teal-300">→</span><span bg="white/5" rounded-lg px-3 py-3>[x, x², x³]</span><span class="text-teal-300">→</span><span bg="white/5" rounded-lg px-3 py-3>ŷ</span>
</div>
</div>

<v-clicks>

- transformation is learned only where needed
- prediction automatically repeats every step
- `include_bias=False` avoids duplicating the intercept

</v-clicks>

<div v-click class="mt-4 text-sm" border="2 solid amber-800" bg="amber-800/20" rounded-lg p-3>Keep preprocessing inside the pipeline so cross-validation cannot leak information.</div>
</div>

</div>

<!--
The pipeline is the practical unit of correctness here, not just convenience: it guarantees that whatever transformation is fit on the training data — here, PolynomialFeatures simply records which powers to compute, but a scaler would record a mean and variance — gets applied identically at prediction time and, crucially, inside every fold of cross-validation. Without a pipeline, a common bug is to call `PolynomialFeatures().fit_transform(X)` once on the entire dataset before splitting it, which lets information about the validation fold leak into the features used for training. `include_bias=False` matters because `LinearRegression` already fits its own intercept internally; leaving the default `include_bias=True` would add a redundant constant column of ones, creating exact collinearity with the intercept term and reintroducing the rank-deficiency problem from last lecture's "When the Inverse Does Not Exist" slide.
-->

---
glowSeed: 344
---

# Degree Is a Complexity Dial

<div class="grid grid-cols-3 gap-4 mt-6 text-center text-sm">

<div v-click border="2 solid blue-800" bg="blue-800/20" rounded-lg p-4>
<div class="text-2xl">—</div><div class="font-bold text-blue-300 mt-2">Low degree</div>
<svg viewBox="0 0 210 125" class="w-full"><g fill="#cbd5e1"><circle cx="20" cy="100" r="3"/><circle cx="50" cy="66" r="3"/><circle cx="85" cy="28" r="3"/><circle cx="120" cy="40" r="3"/><circle cx="158" cy="73" r="3"/><circle cx="195" cy="99" r="3"/></g><line x1="15" y1="85" x2="200" y2="55" stroke="#60a5fa" stroke-width="4"/></svg>
<strong>high bias</strong><br/>too rigid
</div>

<div v-click border="2 solid teal-800" bg="teal-800/20" rounded-lg p-4>
<div class="text-2xl">⌒</div><div class="font-bold text-teal-300 mt-2">Useful degree</div>
<svg viewBox="0 0 210 125" class="w-full"><g fill="#cbd5e1"><circle cx="20" cy="100" r="3"/><circle cx="50" cy="66" r="3"/><circle cx="85" cy="28" r="3"/><circle cx="120" cy="40" r="3"/><circle cx="158" cy="73" r="3"/><circle cx="195" cy="99" r="3"/></g><path d="M15 106 Q88 4 200 105" fill="none" stroke="#2dd4bf" stroke-width="4"/></svg>
<strong>balanced</strong><br/>captures signal
</div>

<div v-click border="2 solid orange-800" bg="orange-800/20" rounded-lg p-4>
<div class="text-2xl">〰</div><div class="font-bold text-orange-300 mt-2">High degree</div>
<svg viewBox="0 0 210 125" class="w-full"><g fill="#cbd5e1"><circle cx="20" cy="100" r="3"/><circle cx="50" cy="66" r="3"/><circle cx="85" cy="28" r="3"/><circle cx="120" cy="40" r="3"/><circle cx="158" cy="73" r="3"/><circle cx="195" cy="99" r="3"/></g><path d="M15 107 C32 120,37 45,50 66 S68 58,85 28 S103 56,120 40 S143 49,158 73 S180 118,200 94" fill="none" stroke="#fb923c" stroke-width="4"/></svg>
<strong>high variance</strong><br/>chases noise
</div>

</div>

<div v-click class="mt-8 text-xl">Training error keeps falling; validation error usually forms a <strong class="text-teal-300">U-shape</strong>.</div>

<!--
Polynomial degree makes the abstract bias-variance tradeoff completely literal and visible, which is why it is such a useful teaching example. Bias is the systematic error from a model that is too simple to represent the true relationship — a straight line genuinely cannot bend to follow curved data, no matter how much training data you give it, so its error stays high even as the dataset grows. Variance is the error from a model being too sensitive to the specific noise in one training sample — a degree-15 polynomial has enough free parameters to pass through points that are, in this particular sample, slightly above or below the true curve due to noise, and a different noisy sample would pull that same high-degree curve into a completely different shape. Training error is a bad guide to picking degree because it only ever decreases as degree increases — a higher-degree polynomial can always fit the training points at least as well. Validation error instead traces the U-shape shown next: too low a degree is bias-dominated, too high a degree is variance-dominated, and the bottom of the U identifies the sweet spot.
-->

---
glowSeed: 345
---

# Let Cross-Validation Choose the Degree

<div class="grid grid-cols-[1.05fr_.95fr] gap-8 mt-2 text-left items-center">

<div>

```python {1-2|4|5-8|10|all}
from sklearn.model_selection import cross_val_score

degrees = [1, 2, 3, 4, 9, 15]
for degree in degrees:
    model = make_pipeline(
        PolynomialFeatures(degree, include_bias=False),
        LinearRegression()
    )
    mse = -cross_val_score(
        model, X, y, cv=5, scoring="neg_mean_squared_error"
    ).mean()
    print(degree, round(mse, 2))
```

</div>

<div>
<svg viewBox="0 0 430 310" class="w-full" role="img" aria-label="U-shaped cross-validation error versus polynomial degree">
  <line x1="48" y1="265" x2="405" y2="265" stroke="#64748b" stroke-width="2"/><line x1="48" y1="265" x2="48" y2="25" stroke="#64748b" stroke-width="2"/>
  <path d="M60 65 C115 135,150 210,220 225 C285 230,332 160,390 55" fill="none" stroke="#2dd4bf" stroke-width="5"/>
  <circle cx="220" cy="225" r="9" fill="#f8fafc"/><line x1="220" y1="225" x2="220" y2="265" stroke="#f8fafc" stroke-dasharray="5 5"/>
  <text x="235" y="215" fill="#f8fafc" style="font-size: 14px">best CV degree</text>
  <text x="175" y="297" fill="#94a3b8" style="font-size: 14px">polynomial degree</text><text x="8" y="28" fill="#94a3b8" style="font-size: 14px">CV MSE</text>
</svg>
<div v-click class="text-sm text-center opacity-75">Choose from held-out folds—not the prettiest training curve.</div>
</div>

</div>

<!--
The negative sign is purely a scikit-learn API convention, not a mathematical necessity: every scorer passed to `cross_val_score` is defined so that a larger returned value always means a better model, which lets the same optimization utilities work uniformly whether the underlying metric is a loss to minimize (like MSE) or a score to maximize (like R² or accuracy). Since MSE is a loss where lower is better, scikit-learn's `neg_mean_squared_error` reports its negative, so a "less negative" (larger) value is correctly interpreted as better. We negate it back with the leading minus sign in the code to report an ordinary, human-readable MSE. Substantively, this loop is doing exactly what the previous slide's U-shaped curve visualizes: for each candidate degree, average the validation error across 5 held-out folds, then compare those averages — never the training error — across degrees to choose the winner.
-->

---
glowSeed: 346
---

# Ridge: Add One Term, Gain Stability

<div class="mt-3" border="2 solid white/10" bg="white/5" rounded-lg px-6 py-4>

$$ {1|2|3}
\begin{aligned}
J_{\text{ridge}}(w)&=\|y-Xw\|_2^2+\lambda\|w\|_2^2 \\
\nabla_wJ_{\text{ridge}}(w)&=-2X^\top y+2X^\top Xw+2\lambda w \\
0&=-2X^\top y+2(X^\top X+\lambda I)\hat w
\end{aligned}
$$

</div>

<div v-click class="mt-6" border="2 solid teal-800" bg="teal-800/20" rounded-lg px-6 py-4>

$$
\boxed{\hat w_{\text{ridge}}=(X^\top X+\lambda I)^{-1}X^\top y}
$$

</div>

<div class="grid grid-cols-3 gap-4 mt-5 text-sm text-left">
<div v-click bg="white/5" rounded-lg p-3><strong>λ = 0</strong><br/>ordinary least squares</div>
<div v-click bg="white/5" rounded-lg p-3><strong>larger λ</strong><br/>stronger shrinkage</div>
<div v-click bg="white/5" rounded-lg p-3><strong>intercept</strong><br/>normally left unpenalized</div>
</div>

<div class="mt-4 text-xs opacity-60">Derivation assumes centered data or a separate, unpenalized intercept.</div>

<!--
This is the previous lecture's normal-equation derivation with exactly one new term added to the objective, and the whole derivation reuses last lecture's gradient identities unchanged. The augmented objective J_ridge(w)=‖y−Xw‖₂²+λ‖w‖₂² adds an L2 penalty on the size of the weight vector: λ is a hyperparameter controlling how strongly large weights are punished, and ‖w‖₂²=w^T w is just the sum of squared coefficients. Differentiating the new term uses the same quadratic-form identity as before (∇_w(w^T w)=2w, the special case A=I), so it contributes 2λw to the gradient alongside the familiar OLS gradient. Setting the sum to zero and solving gives ŵ_ridge=(X^T X+λI)^{-1}X^T y — note this is also, technically, the constrained-optimization Lagrangian form of minimizing ‖y−Xw‖₂² subject to ‖w‖₂²≤t for some budget t that corresponds to a given λ; the penalty form and the constraint form are two equivalent ways of writing the same optimization problem, a distinction that matters on the geometric-intuition slide later. In practice, libraries like scikit-learn do not penalize the intercept: this corresponds to centering the data first, or simply excluding the intercept's coordinate from the penalty matrix, since shrinking the intercept toward zero would arbitrarily bias predictions toward zero rather than controlling model complexity.
-->

---
glowSeed: 347
---

# Why Ridge Fixes Singularity

<div class="grid grid-cols-2 gap-8 mt-4 items-center text-left">

<div>
<svg viewBox="0 0 430 300" class="w-full" role="img" aria-label="Eigenvalues shifted away from zero by ridge regularization">
  <line x1="48" y1="245" x2="405" y2="245" stroke="#64748b" stroke-width="2"/>
  <g stroke-width="18">
    <line x1="105" y1="245" x2="105" y2="245" stroke="#ef4444"/><line x1="190" y1="245" x2="190" y2="165" stroke="#60a5fa"/><line x1="275" y1="245" x2="275" y2="95" stroke="#60a5fa"/>
  </g>
  <g fill="#94a3b8" text-anchor="middle" style="font-size: 14px"><text x="105" y="270">0</text><text x="190" y="270">s₂²</text><text x="275" y="270">s₁²</text></g>
  <path d="M330 205 L375 205" stroke="#2dd4bf" stroke-width="4" marker-end="url(#ridge-arrow)"/><defs><marker id="ridge-arrow" markerWidth="8" markerHeight="8" refX="7" refY="4" orient="auto"><path d="M0,0 L8,4 L0,8 Z" fill="#2dd4bf"/></marker></defs>
  <text x="350" y="185" text-anchor="middle" fill="#5eead4" style="font-size: 14px">+ λ</text>
  <line x1="105" y1="245" x2="105" y2="205" stroke="#2dd4bf" stroke-width="18"/>
  <text x="105" y="188" text-anchor="middle" fill="#5eead4" style="font-size: 14px">λ &gt; 0</text>
</svg>
</div>

<div>

$$
X^\top X=V\operatorname{diag}(s_1^2,\ldots,s_d^2)V^\top
$$

$$
X^\top X+\lambda I
=V\operatorname{diag}(s_1^2+\lambda,\ldots,s_d^2+\lambda)V^\top
$$

<v-clicks>

- every eigenvalue shifts upward by $\lambda$
- zero becomes strictly positive
- the inverse now exists for $\lambda>0$
- correlated polynomial columns become manageable

</v-clicks>

</div>

</div>

<!--
This closes the loop from the singular-design slide in the prior lecture, and it is worth deriving the eigenvalue-shift claim explicitly rather than just asserting it. X^T X is symmetric, so it admits an eigendecomposition X^T X=V diag(s₁²,...,s_d²)Vᵀ, where V's columns are orthonormal eigenvectors and each s_i² ≥ 0 is an eigenvalue (written as a square because these are also the squared singular values of X). Adding λI to X^T X adds λ to the diagonal in that same eigenbasis, since V diag(s_i²)Vᵀ + λI = V diag(s_i²)Vᵀ + λVVᵀ = V diag(s_i²+λ)Vᵀ, using VVᵀ=I. So every eigenvalue shifts from s_i² to s_i²+λ — nothing else about the eigenvectors changes. When a redundant or near-redundant feature direction makes some s_i² equal to (or nearly) zero, X^T X is singular or ill-conditioned; adding any λ>0 makes that eigenvalue strictly positive, so X^T X+λI is always invertible for λ>0, regardless of how degenerate X was. Ridge does not invent new information about the redundant direction — it simply refuses to let the solution blow up along it, selecting the smallest-norm solution consistent with the data instead.
-->

---
glowSeed: 353
---

# Ridge Trades Variance for Bias

<div class="grid grid-cols-2 gap-8 mt-4 items-center text-left">

<div>

$$
\hat w_{\text{ridge}}=V\,\operatorname{diag}\!\left(\frac{s_i^2}{s_i^2+\lambda}\right)V^\top\hat w_{\text{OLS}}
$$

<v-clicks>

- each OLS direction is shrunk by a factor $\dfrac{s_i^2}{s_i^2+\lambda}\in(0,1]$
- small $s_i$ (low-signal, high-variance direction) → shrunk hardest
- large $s_i$ (high-signal direction) → barely shrunk
- shrinkage introduces bias, but removes far more variance than it adds

</v-clicks>

</div>

<div>
<div v-click border="2 solid white/5" bg="white/5" rounded-lg p-4>
<div class="font-bold text-teal-300 mb-2">Why this is the bias–variance tradeoff</div>
<div class="text-sm opacity-85">
OLS is unbiased but can have huge variance along directions with small $s_i$, where a tiny amount of noise in $y$ produces a huge change in $\hat w$. Ridge accepts a little bias along exactly those directions in exchange for a large reduction in variance — the same tradeoff degree controls for polynomial features, now controlled continuously by $\lambda$.
</div>
</div>
</div>

</div>

<!--
This slide makes the abstract "regularization trades bias for variance" claim into an explicit, derivable formula rather than a slogan. Starting from ŵ_ridge=(X^T X+λI)^{-1}X^T y and substituting the eigendecomposition X^T X=V diag(s_i²)Vᵀ from the previous slide, algebra shows ŵ_ridge equals the OLS solution ŵ_OLS=(X^T X)^{-1}X^T y with each coordinate, in the V eigenbasis, multiplied by a shrinkage factor s_i²/(s_i²+λ). This factor is always between 0 and 1 for λ>0: directions with a large singular value s_i (strong, well-determined signal) have s_i²/(s_i²+λ) close to 1, so ridge barely touches them, while directions with a small s_i (weak signal, close to the singular case from two slides ago) have a shrinkage factor close to 0, so ridge aggressively pulls those coefficients toward zero. This is precisely the bias-variance tradeoff made concrete: OLS is unbiased in every direction, but its variance in a low-signal direction can be enormous, because a small amount of label noise gets divided by a nearly-zero s_i² and amplified into a huge, unstable coefficient estimate. Ridge sacrifices a small, controlled amount of bias in exactly those fragile directions in order to eliminate a much larger amount of variance, which is why, despite being biased, ridge estimates very often have lower total expected error (bias² + variance) than OLS, especially when features are correlated or numerous relative to n — exactly the polynomial-regression setting of this lecture.
-->

---
glowSeed: 348
---

# One Flexible Basis, Three Fits

<div class="grid grid-cols-[1.2fr_.8fr] gap-8 mt-2 items-center text-left">

<div>
<svg viewBox="0 0 530 350" class="w-full" role="img" aria-label="Degree-15 unregularized, ridge, and lasso curves over noisy points">
  <line x1="45" y1="310" x2="500" y2="310" stroke="#64748b"/><line x1="45" y1="310" x2="45" y2="25" stroke="#64748b"/>
  <g fill="#e2e8f0"><circle cx="70" cy="260" r="5"/><circle cx="105" cy="222" r="5"/><circle cx="145" cy="160" r="5"/><circle cx="190" cy="90" r="5"/><circle cx="235" cy="118" r="5"/><circle cx="280" cy="178" r="5"/><circle cx="330" cy="238" r="5"/><circle cx="380" cy="209" r="5"/><circle cx="430" cy="125" r="5"/><circle cx="475" cy="82" r="5"/></g>
  <path d="M55 285 C72 335,88 135,105 222 S130 190,145 160 S170 5,190 90 S210 215,235 118 S255 125,280 178 S310 315,330 238 S360 104,380 209 S410 218,430 125 S460 10,490 110" fill="none" stroke="#fb923c" stroke-width="3" opacity=".8"/>
  <path d="M55 277 C120 235,150 95,205 102 C265 110,294 245,350 237 C409 230,448 90,490 75" fill="none" stroke="#2dd4bf" stroke-width="5"/>
  <path d="M55 270 C120 225,163 110,210 108 C270 108,310 232,360 226 C415 220,451 102,490 82" fill="none" stroke="#c084fc" stroke-width="4" stroke-dasharray="8 6"/>
</svg>
</div>

<div class="space-y-4">
<div v-click border="2 solid orange-800" bg="orange-800/20" rounded-lg p-4><span class="text-orange-300 font-bold">Unregularized</span><div class="text-sm opacity-75 mt-1">wild coefficients, high variance</div></div>
<div v-click border="2 solid teal-800" bg="teal-800/20" rounded-lg p-4><span class="text-teal-300 font-bold">Ridge · L2</span><div class="text-sm opacity-75 mt-1">shrinks every term smoothly</div></div>
<div v-click border="2 solid violet-800" bg="violet-800/20" rounded-lg p-4><span class="text-violet-300 font-bold">Lasso · L1</span><div class="text-sm opacity-75 mt-1">can zero higher-order terms</div></div>
</div>

</div>

<!--
All three curves are fit with the exact same degree-15 feature set — the same φ(x), the same nominal model capacity — so any difference in shape comes entirely from the penalty term added to the loss, not from a different choice of features. The unregularized fit (orange) has enough free parameters to chase every noisy fluctuation in the ten plotted points, producing the wild, high-variance wiggle from the title slide. Ridge (teal) uses the shrinkage mechanism from the previous slide: every coefficient is pulled toward zero smoothly, in proportion to how weakly determined its direction is by the data, which tames the wiggle into a much smoother curve without literally zeroing out any high-order term. Lasso (violet) achieves smoothness through a qualitatively different mechanism — it can drive some high-order coefficients to exactly zero, effectively behaving like automatic feature selection that discards terms the data does not support, rather than merely shrinking every term a little. The next two slides derive exactly why L1 and L2 penalties produce these two different behaviors.
-->

---
glowSeed: 349
---

# Ridge Shrinks; Lasso Selects

<div class="grid grid-cols-2 gap-7 mt-3 text-left">

<div v-click border="2 solid blue-800" bg="blue-800/20" rounded-lg p-4>
<div class="font-bold text-blue-300 mb-2">Ridge · λ‖w‖₂²</div>

```python
from sklearn.linear_model import Ridge

ridge = Ridge(alpha=5.0)
ridge.fit(X_poly, y)
print(abs(ridge.coef_).max())
```

<div class="text-sm opacity-75 mt-3">Differentiable penalty; a stable closed-form solution exists.</div>
</div>

<div v-click border="2 solid violet-800" bg="violet-800/20" rounded-lg p-4>
<div class="font-bold text-violet-300 mb-2">Lasso · λ‖w‖₁</div>

```python
from sklearn.linear_model import Lasso

lasso = Lasso(alpha=.05, max_iter=20_000)
lasso.fit(X_poly, y)
print(np.count_nonzero(lasso.coef_))
```

<div class="text-sm opacity-75 mt-3">Nondifferentiable at zero; solved iteratively, often with coordinate descent.</div>
</div>

</div>

<div v-click class="mt-5 text-center text-lg" border="2 solid white/5" bg="white/5" rounded-lg p-4>
Ridge keeps all terms small; lasso can remove terms entirely.
</div>

<!--
Correct a common misconception directly: students often assume ridge and lasso are interchangeable penalties that just happen to use a different exponent. They are not interchangeable computationally. Ridge's penalty λ‖w‖₂² is smooth and differentiable everywhere, including at w=0, so the same closed-form matrix-algebra trick from two slides ago works unchanged. Lasso's penalty λ‖w‖₁=λΣ|w_j| is not differentiable at w_j=0 — the absolute value function has a sharp corner there, so ordinary calculus (setting a gradient to zero) does not directly apply. This is precisely what makes lasso's solution qualitatively different, and the next slide derives, rather than just asserts, why that corner is the mathematical reason lasso can set coefficients to exactly zero. Because no closed form exists, scikit-learn's Lasso solves the optimization iteratively, typically with coordinate descent: repeatedly optimizing one coefficient at a time while holding the others fixed.
-->

---
glowSeed: 354
---

# Deriving Lasso's Sparsity: Soft-Thresholding

<div class="grid grid-cols-2 gap-8 mt-3 items-center text-left">

<div>

Assume an orthonormal design ($X^\top X=I$), so the objective separates coordinatewise:

$$
J_{\text{lasso}}(w)=\text{const}+\sum_j\Big[w_j^2-2w_j\hat w_j^{\text{OLS}}+\lambda|w_j|\Big]
$$

<v-clicks>

- minimize each term in $w_j$ independently
- for $w_j\neq0$, ordinary calculus applies: $2w_j-2\hat w_j^{\text{OLS}}\pm\lambda=0$
- for $w_j=0$, the subgradient of $|w_j|$ spans $[-1,1]$, so $w_j=0$ is optimal whenever $|\hat w_j^{\text{OLS}}|\le\lambda/2$

</v-clicks>

</div>

<div>
<div v-click border="2 solid violet-800" bg="violet-800/20" rounded-lg p-4>

$$
\boxed{\hat w_j=\operatorname{sign}\!\big(\hat w_j^{\text{OLS}}\big)\max\!\Big(|\hat w_j^{\text{OLS}}|-\tfrac{\lambda}{2},\,0\Big)}
$$

</div>

<div v-click class="mt-4 text-sm" border="2 solid white/5" bg="white/5" rounded-lg p-4>
"Soft-thresholding": any OLS coefficient smaller than $\lambda/2$ in magnitude is pushed to exactly zero; larger ones are shrunk by a constant amount, not a constant factor.
</div>
</div>

</div>

<!--
This is the derivation that turns "lasso induces sparsity" from an asserted fact into something proven. Assume, purely to make the algebra tractable, that the design is orthonormal — X^T X=I, as if every polynomial feature were uncorrelated with every other. Under that assumption, expanding ‖y−Xw‖₂² and dropping constants that don't depend on w shows the full objective decomposes into a sum of independent one-dimensional problems, one per coefficient w_j, each of the form w_j²−2w_j·â_j+λ|w_j|, where â_j is the j-th OLS coefficient. For w_j>0, differentiate normally: 2w_j−2â_j+λ=0 gives w_j=â_j−λ/2, valid only while this is positive, i.e. â_j>λ/2. By symmetry, for w_j<0, w_j=â_j+λ/2, valid while â_j<−λ/2. In between, when |â_j|≤λ/2, no ordinary stationary point exists on either side — the corner of |w_j| at zero has a whole range of valid "subgradients" between −1 and 1, and zero is the point where the objective's subgradient can contain zero, making w_j=0 the true minimizer. Combining all three cases gives the boxed soft-thresholding formula: it is a shift-and-clip operation, not a rescaling — contrast this explicitly with ridge's shrinkage factor from two slides ago, which multiplies every OLS coefficient by a constant between 0 and 1 and therefore never produces an exact zero for a nonzero input. That contrast is the entire mechanical reason lasso selects features and ridge does not. Note for correctness: real polynomial features are rarely orthonormal, so scikit-learn's coordinate-descent solver does not use this closed form directly, but the qualitative sparsity behavior it proves carries over to the general case.
-->

---
glowSeed: 350
---

# Why L1 Finds Exact Zeros

<div class="text-sm opacity-70 mb-3">Equivalent view: minimize the loss subject to a budget $\|w\|_1\le t$ (or $\|w\|_2^2\le t$) — the constraint form of the same penalized objective from the earlier slides.</div>

<div class="grid grid-cols-2 gap-8 mt-4 text-center">

<div v-click border="2 solid violet-800" bg="violet-800/20" rounded-lg p-4>
<div class="font-bold text-violet-300">L1 constraint</div>
<svg viewBox="0 0 320 235" class="w-full max-w-80 mx-auto">
  <line x1="25" y1="118" x2="295" y2="118" stroke="#64748b"/><line x1="160" y1="15" x2="160" y2="220" stroke="#64748b"/>
  <path d="M160 30 L255 118 L160 206 L65 118 Z" fill="#7c3aed33" stroke="#c084fc" stroke-width="3"/>
  <ellipse cx="258" cy="40" rx="112" ry="68" fill="none" stroke="#f8fafc" stroke-width="2" transform="rotate(-25 258 40)"/>
  <circle cx="160" cy="30" r="8" fill="#f59e0b"/><text x="175" y="27" fill="#fbbf24" style="font-size: 13px">axis corner</text>
</svg>
Corners lie on axes → one coordinate is exactly zero
</div>

<div v-click border="2 solid blue-800" bg="blue-800/20" rounded-lg p-4>
<div class="font-bold text-blue-300">L2 constraint</div>
<svg viewBox="0 0 320 235" class="w-full max-w-80 mx-auto">
  <line x1="25" y1="118" x2="295" y2="118" stroke="#64748b"/><line x1="160" y1="15" x2="160" y2="220" stroke="#64748b"/>
  <circle cx="160" cy="118" r="88" fill="#2563eb33" stroke="#60a5fa" stroke-width="3"/>
  <ellipse cx="258" cy="40" rx="112" ry="68" fill="none" stroke="#f8fafc" stroke-width="2" transform="rotate(-25 258 40)"/>
  <circle cx="218" cy="52" r="8" fill="#f59e0b"/><text x="228" y="47" fill="#fbbf24" style="font-size: 13px">smooth tangent</text>
</svg>
Smooth boundary → coefficients are usually small but nonzero
</div>

</div>

<!--
This is the geometric companion to the algebraic soft-thresholding derivation from the previous slide, and it is worth naming explicitly that these are two views of the same problem: minimizing ‖y−Xw‖₂²+λ‖w‖₁ (the penalty form used everywhere else in this lecture) is, by Lagrangian duality, equivalent to minimizing ‖y−Xw‖₂² subject to the hard constraint ‖w‖₁≤t (the constraint form drawn here), for a budget t that corresponds to a particular λ — larger λ corresponds to a smaller allowed budget t. The picture to build in two weights: draw the elliptical contours of the unconstrained least-squares loss, centered at the OLS solution, and imagine inflating them outward like a balloon; the constrained solution is wherever the smallest inflated ellipse first touches the allowed region's boundary. The L1 diamond has sharp corners sitting exactly on the coordinate axes, and because ellipses are much more likely to first touch a pointed corner than a flat edge, the constrained solution lands on an axis — meaning one coordinate is exactly zero — for a wide range of ellipse orientations and shapes. The L2 circle has no corners and no preferred axis at all, so the first point of contact is essentially always some smooth point on the boundary with every coordinate nonzero. This geometric picture and the algebraic soft-thresholding derivation are two independent proofs of the identical conclusion.
-->

---
glowSeed: 351
---

# Scale Before You Regularize

<div class="grid grid-cols-[.9fr_1.1fr] gap-8 mt-3 text-left items-center">

<div>
<div border="2 solid amber-800" bg="amber-800/20" rounded-lg p-4>

$$
x_j^{\text{scaled}}=\frac{x_j-\mu_j}{\sigma_j}
$$

</div>

<v-clicks>

- penalties act on coefficient magnitude
- coefficient magnitude depends on feature units
- $x,x^2,\ldots,x^p$ live on different scales
- standardization makes the penalty comparable

</v-clicks>

</div>

<div>

```python {1-4|6-10|12|all}
from sklearn.linear_model import RidgeCV
from sklearn.pipeline import make_pipeline
from sklearn.preprocessing import PolynomialFeatures
from sklearn.preprocessing import StandardScaler

model = make_pipeline(
    PolynomialFeatures(9, include_bias=False),
    StandardScaler(),
    RidgeCV(alphas=np.logspace(-4, 4, 40), cv=5),
)

model.fit(X, y)
print(model[-1].alpha_)
```

<div v-click class="mt-3 text-sm" border="2 solid teal-800" bg="teal-800/20" rounded-lg p-3>The pipeline fits scaling separately inside every CV training fold.</div>

</div>

</div>

<!--
This preprocessing detail matters more for polynomial features than almost anywhere else in the course, because powers of the same variable grow at radically different rates: if x ranges over roughly [-3, 3], x² ranges over roughly [0, 9] and x⁹ ranges over tens of thousands — three features spanning many orders of magnitude. Both ridge and lasso penalize raw coefficient magnitude directly, so without standardizing first, the optimizer would be effectively forced to assign a tiny coefficient to x⁹ and a comparatively large one to x just to produce predictions of similar scale, and the penalty would then punish the low-degree terms far more harshly than the high-degree ones for no principled reason — the penalty would be measuring feature units, not genuine importance. Standardizing every polynomial feature to zero mean and unit variance first puts every coefficient on a comparable footing, so the penalty measures relative importance instead. As in every pipeline in this lecture, keeping the scaler as a pipeline step rather than calling it up front prevents validation-fold statistics from leaking into the training fold during cross-validation, which would make the reported RidgeCV performance optimistically biased.
-->

---
layout: center
class: text-center
glowSeed: 352
---

# The Regression Recipe

<div class="grid grid-cols-4 gap-4 max-w-5xl mx-auto mt-8 text-left">
<div v-click border="2 solid teal-800" bg="teal-800/20" rounded-lg p-4><div class="text-3xl">🧩</div><strong>Features</strong><div class="text-sm opacity-80 mt-2">raw or polynomial</div></div>
<div v-click border="2 solid blue-800" bg="blue-800/20" rounded-lg p-4><div class="text-3xl">🎯</div><strong>Loss</strong><div class="text-sm opacity-80 mt-2">squared error</div></div>
<div v-click border="2 solid violet-800" bg="violet-800/20" rounded-lg p-4><div class="text-3xl">🛡️</div><strong>Penalty</strong><div class="text-sm opacity-80 mt-2">L2 or L1</div></div>
<div v-click border="2 solid amber-800" bg="amber-800/20" rounded-lg p-4><div class="text-3xl">🧭</div><strong>Solver</strong><div class="text-sm opacity-80 mt-2">direct or iterative</div></div>
</div>

<div v-click class="mt-9" border="2 solid white/10" bg="white/5" rounded-lg px-8 py-5 text-xl>
Flexible features create capacity; <strong class="text-teal-300">cross-validation and regularization</strong> control it.
</div>

<div v-click class="mt-8 text-xl">Next: <strong>Supervised Learning — Classification</strong></div>

<!--
Close by naming the four-part recipe explicitly, since it is now complete and will be the lens for the rest of the course: choose a feature representation (raw inputs or an expanded basis like polynomial features), choose a loss that measures prediction quality, optionally add a penalty term that controls model capacity independently of feature count, and choose a solver — closed form when it exists and is affordable, iterative optimization otherwise. This lecture's central lesson is that flexibility and control are separate knobs: polynomial degree (or feature count generally) creates capacity to fit complex patterns, while cross-validation, which picks the degree and the penalty strength λ, and regularization, which shapes how that capacity gets used, are what keep that capacity from overfitting. Classification, starting next lecture, keeps this entire recipe intact — a linear score x^Tw survives unchanged — but swaps the loss (from squared error to something suited to discrete labels, like log-loss) and the output interpretation (from a continuous prediction to a class probability), while ridge- and lasso-style penalties and iterative solvers carry over directly. Take questions before moving to classification.
-->
