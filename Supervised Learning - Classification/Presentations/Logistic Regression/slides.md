---
theme: default
highlighter: shiki
css: unocss
colorSchema: dark
title: 'Logistic Regression'
info: |
  ## Logistic Regression
  From linear scores to calibrated class probabilities.
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
glowSeed: 401
---

# Logistic Regression

### From predicting numbers to predicting probabilities

<div class="pt-5 opacity-80 text-lg">Supervised Learning · Classification</div>

<svg role="img" aria-label="A sigmoid curve connecting binary class labels zero and one" viewBox="0 0 760 220" class="w-full max-w-3xl mx-auto mt-7">
  <line x1="55" y1="190" x2="720" y2="190" stroke="#64748b" stroke-width="2"/><line x1="380" y1="20" x2="380" y2="200" stroke="#64748b" stroke-width="2"/>
  <path d="M70 178 C240 178 300 165 350 118 C405 65 470 36 700 36" fill="none" stroke="#2dd4bf" stroke-width="6"/>
  <line x1="55" y1="106" x2="720" y2="106" stroke="#60a5fa" stroke-dasharray="7 7"/><text x="728" y="111" fill="#93c5fd">0.5</text>
  <g fill="#fb923c"><circle cx="130" cy="184" r="7"/><circle cx="220" cy="184" r="7"/><circle cx="300" cy="184" r="7"/></g>
  <g fill="#60a5fa"><circle cx="460" cy="28" r="7"/><circle cx="550" cy="28" r="7"/><circle cx="650" cy="28" r="7"/></g>
</svg>

<!--
Connect directly to the regression unit students already completed: the same model → loss → optimizer template applies here, just with a different output function (sigmoid instead of identity) and a different loss (log loss instead of squared error). Flag the naming misconception immediately, since it trips up almost everyone the first time: despite the word "regression" in its name, logistic regression is a classification algorithm. The word "regression" refers only to the intermediate step — it regresses a continuous quantity, the log-odds of the positive class, as a linear function of the features — before squashing that continuous score through the sigmoid into a probability and thresholding to get a discrete class label.

Roadmap for today: why plain linear regression fails as a classifier, the sigmoid function that fixes the output range, the log-loss objective derived from maximum likelihood, its gradient (which has a strikingly familiar shape), gradient descent as the only way to fit it, L1/L2 regularization exactly as in linear regression, and softmax as the natural extension to more than two classes.
-->

---
glowSeed: 402
---

# Why Linear Regression Fails Here

<div class="grid grid-cols-2 gap-7 mt-4 items-center">
<div>
<v-clicks>

- Fit $\hat y=x^\top w$ to labels $y\in\{0,1\}$ and threshold at $0.5$?
- Predictions escape $[0,1]$ — impossible as probabilities
- Far-away, already-correct points still pull the squared-error line
- Classification cares about the boundary, not how far a confident point lies beyond it

</v-clicks>
<div v-click border="2 solid teal-800" bg="teal-800/20" rounded-lg p-4 class="mt-5">We need a bounded probability model <strong>and</strong> a classification loss.</div>
</div>
<svg role="img" aria-label="A linear fit to binary labels extends below zero and above one, and shifts when an outlier is added" viewBox="0 0 500 330" class="w-full">
  <line x1="45" y1="285" x2="465" y2="285" stroke="#64748b"/><line x1="45" y1="285" x2="45" y2="25" stroke="#64748b"/>
  <line x1="45" y1="230" x2="465" y2="230" stroke="#475569" stroke-dasharray="5 5"/><line x1="45" y1="80" x2="465" y2="80" stroke="#475569" stroke-dasharray="5 5"/>
  <text x="15" y="235" fill="#94a3b8">0</text><text x="15" y="85" fill="#94a3b8">1</text>
  <g fill="#fb923c"><circle cx="90" cy="230" r="7"/><circle cx="145" cy="230" r="7"/><circle cx="205" cy="230" r="7"/></g>
  <g fill="#60a5fa"><circle cx="270" cy="80" r="7"/><circle cx="330" cy="80" r="7"/><circle cx="390" cy="80" r="7"/></g>
  <line x1="65" y1="270" x2="440" y2="15" stroke="#f8fafc" stroke-width="4"/><circle cx="455" cy="80" r="9" fill="#60a5fa"/>
  <line x1="65" y1="260" x2="455" y2="50" stroke="#f59e0b" stroke-width="3" stroke-dasharray="8 5"/>
  <text x="250" y="310" fill="#fbbf24" style="font-size:13px">one easy point still shifts the threshold</text>
</svg>
</div>

<!--
Make both failures completely concrete before introducing the fix. First failure: fitting an ordinary linear regression $\hat y = x^\top w$ to labels coded as 0 and 1, then thresholding at 0.5, produces predictions that can be well below 0 or well above 1 for points far from the bulk of the data — nonsensical as probabilities, since a probability must lie in [0,1]. This directly motivates the sigmoid function on the next slide, which squashes any real-valued score into that range.

Second failure, more subtle: even restricting attention to points that already lie safely in [0,1], squared-error loss keeps penalizing a prediction based on numeric distance from the label, so one easy, already-correctly-classified point far from the boundary (e.g., predicted 0.95 for a true label of 1) still contributes a nonzero gradient pulling the fitted line further in that direction — the dashed line in the figure shows the boundary visibly shifting after one such easy point is added, even though that point didn't need to influence the boundary at all. Classification only cares about which side of the boundary a point falls on, not how numerically far a confident correct prediction sits from an arbitrary label encoding — this is exactly why a genuinely different loss function, log loss, is needed rather than simply changing the output range. This also foreshadows a related idea in the SVM deck: that only points near the decision boundary (the support vectors) should influence where that boundary sits.
-->

---
glowSeed: 403
---

# The Sigmoid Function

<div class="grid grid-cols-2 gap-8 mt-3 items-center">
<div>
<div border="2 solid teal-800" bg="teal-800/20" rounded-lg p-4>

$$\sigma(z)=\frac{1}{1+e^{-z}}$$
$$\sigma'(z)=\sigma(z)\bigl(1-\sigma(z)\bigr)$$

</div>

```python
import numpy as np

def sigmoid(z):
    return 1 / (1 + np.exp(-z))

z = np.linspace(-10, 10, 200)
print(sigmoid(np.array([-10, 0, 10])))
```
</div>
<svg role="img" aria-label="Sigmoid S curve with asymptotes zero and one and midpoint at zero comma one half" viewBox="0 0 470 330" class="w-full">
  <line x1="45" y1="285" x2="445" y2="285" stroke="#64748b"/><line x1="245" y1="20" x2="245" y2="300" stroke="#64748b"/>
  <line x1="45" y1="35" x2="445" y2="35" stroke="#60a5fa" stroke-dasharray="6 5"/><line x1="45" y1="285" x2="445" y2="285" stroke="#60a5fa" stroke-dasharray="6 5"/>
  <path d="M55 280 C145 278 185 255 220 190 C235 162 240 160 245 160 C250 160 255 158 270 130 C305 65 345 42 435 40" fill="none" stroke="#2dd4bf" stroke-width="6"/>
  <circle cx="245" cy="160" r="8" fill="#f59e0b"/><text x="257" y="155" fill="#fbbf24">(0, 0.5)</text>
  <text x="15" y="40" fill="#94a3b8">1</text><text x="15" y="290" fill="#94a3b8">0</text><text x="420" y="315" fill="#94a3b8">z</text>
</svg>
</div>

<!--
The sigmoid function σ(z) = 1/(1+e^{-z}) maps any real number z — called the logit or linear score, x^T w — to a value strictly between 0 and 1, with σ(0)=0.5, σ(z)→1 as z→+∞, and σ(z)→0 as z→-∞, giving it the characteristic S-shape shown. Derive σ'(z) quickly with the quotient rule from calculus, writing σ(z) = (1+e^{-z})^{-1}: differentiating gives σ'(z) = e^{-z}/(1+e^{-z})^2, which can be algebraically rearranged into the remarkably clean closed form σ(z)(1-σ(z)) — the derivative is expressible entirely in terms of the function's own output, with no need to re-evaluate the exponential. That self-referential closed form is exactly the algebraic cancellation that makes the log-loss gradient on the next slides simplify so cleanly.

Mention in passing that sigmoid is also the cumulative distribution function (CDF) of the standard logistic distribution, which is the historical origin of the name "logistic regression." Run the code live and note the three sample outputs: sigmoid(-10) is extremely close to 0, sigmoid(0) is exactly 0.5, and sigmoid(10) is extremely close to 1, confirming the asymptotic behavior visually.
-->

---
glowSeed: 404
---

# A Linear Boundary, Soft Probabilities

<div class="grid grid-cols-2 gap-7 mt-3 items-center">
<div>
<div border="2 solid blue-800" bg="blue-800/20" rounded-lg p-4>

$$\hat p=P(y=1\mid x)=\sigma(x^\top w)$$
$$\hat y=1\iff \hat p\ge .5\iff x^\top w\ge0$$

</div>

```python
from sklearn.datasets import make_classification
from sklearn.linear_model import LogisticRegression

X, y = make_classification(
    n_samples=200, n_features=2,
    n_redundant=0, random_state=0)
model = LogisticRegression().fit(X, y)
print(model.predict_proba(X[:3]))
print(model.predict(X[:3]))
```
</div>
<svg role="img" aria-label="Two class scatter with a straight decision boundary and probability bands" viewBox="0 0 470 330" class="w-full">
  <defs><linearGradient id="prob" x1="0" x2="1"><stop stop-color="#f97316" stop-opacity=".35"/><stop offset=".5" stop-color="#0f172a"/><stop offset="1" stop-color="#3b82f6" stop-opacity=".35"/></linearGradient></defs>
  <rect x="35" y="20" width="410" height="280" rx="12" fill="url(#prob)"/>
  <line x1="95" y1="295" x2="370" y2="25" stroke="#f8fafc" stroke-width="4"/>
  <g fill="#fb923c"><circle cx="90" cy="85" r="7"/><circle cx="125" cy="155" r="7"/><circle cx="165" cy="210" r="7"/><circle cx="210" cy="250" r="7"/></g>
  <g fill="#60a5fa"><circle cx="250" cy="75" r="7"/><circle cx="310" cy="115" r="7"/><circle cx="355" cy="170" r="7"/><circle cx="390" cy="230" r="7"/></g>
  <text x="55" y="45" fill="#fdba74">p≈0</text><text x="370" y="285" fill="#93c5fd">p≈1</text><text x="185" y="75" fill="#f8fafc">p=.5</text>
</svg>
</div>

<!--
Composing the linear score with the sigmoid gives the full logistic regression model: p̂ = P(y=1|x) = σ(x^T w), a smooth probability that varies continuously across feature space. The predicted class ŷ=1 exactly when p̂ ≥ 0.5, and because σ is monotonically increasing and σ(0)=0.5, that condition is algebraically equivalent to x^T w ≥ 0 — so even though the probability surface is smooth and curved everywhere, the actual decision boundary (where p̂ crosses 0.5) is the flat hyperplane where the linear score itself crosses zero. This is the key geometric fact about logistic regression: a linear boundary with a nonlinear, smoothly graded confidence field on either side of it.

The heatmap in the figure unifies the hard and soft views of the same model: the color gradient shows the continuous probability field (deep orange near p≈0, deep blue near p≈1), while the sharp white line marks exactly where p=0.5 — a straight line, confirming the boundary is linear. Emphasize that thresholding at exactly 0.5 is a policy choice, not a mathematical requirement: in settings with asymmetric costs (e.g., a missed cancer diagnosis is far worse than a false alarm), a different threshold may be preferred, a topic revisited in the Model Evaluation unit with ROC curves and precision-recall tradeoffs.
-->

---
glowSeed: 404.5
---

# Where Log Loss Comes From: Maximum Likelihood

<div class="grid grid-cols-2 gap-7 mt-3 items-center">
<div>
<div border="2 solid teal-800" bg="teal-800/20" rounded-lg p-4>

$$y_i\mid x_i\sim\operatorname{Bernoulli}(\hat p_i)$$
$$L(w)=\prod_i \hat p_i^{\,y_i}(1-\hat p_i)^{1-y_i}$$

</div>

<v-clicks>

- Treat each label as one flip of a $\hat p_i$-weighted coin
- Take the log: products become sums, powers become multiplication
- Maximize $\log L(w)$ $\iff$ minimize $-\log L(w)=J(w)$
- $J(w)$ is exactly the log-loss / cross-entropy formula

</v-clicks>
</div>

<div>
<div border="2 solid white/10" bg="white/5" rounded-lg p-4>

$$\log L(w)=\sum_i\Bigl[y_i\log\hat p_i+(1-y_i)\log(1-\hat p_i)\Bigr]$$
$$J(w)=-\log L(w)$$

</div>

<div class="mt-4 text-sm" border="2 solid amber-800" bg="amber-800/20" rounded-lg p-3>
Worked: $y=1,\ \hat p=0.8\Rightarrow-\log(0.8)\approx0.223$.
$\quad y=1,\ \hat p=0.2\Rightarrow-\log(0.2)\approx1.609$
</div>
</div>
</div>

<!--
Log loss is not an arbitrary design choice — it falls directly out of maximum likelihood estimation, the same principle used to justify least-squares in linear regression. Model each label y_i as a single flip of a coin biased toward 1 with probability p̂_i = σ(x_i^T w), the model's predicted probability. Because each of the n training labels is drawn independently, the joint likelihood of observing the entire training set is the product, over all i, of the individual Bernoulli probabilities L(w) = ∏ p̂_i^{y_i}(1-p̂_i)^{1-y_i} — note that when y_i=1 the term reduces to p̂_i, and when y_i=0 it reduces to (1-p̂_i), so this compact expression just picks out "the probability the model assigned to the label that actually occurred," for every example.

Maximizing this likelihood directly is numerically awkward because it multiplies many probabilities together, each less than 1, producing numbers that underflow to zero for even modest sample sizes. Taking the logarithm converts the product into a sum without changing which w maximizes it, since log is a strictly increasing function: log L(w) = Σ [y_i log p̂_i + (1-y_i) log(1-p̂_i)]. Because optimization convention is to minimize rather than maximize, define J(w) as the negative of this log-likelihood — minimizing J(w) is mathematically identical to maximizing the likelihood of the observed labels, and J(w) is precisely the log-loss (also called binary cross-entropy) formula used on the next slide. Work the two worked numeric values on screen: when the true label is 1 and the model confidently predicts p̂=0.8, the loss is small (≈0.223); when the model wrongly predicts only p̂=0.2 for a true label of 1, the loss is much larger (≈1.609) — log loss punishes confident wrong predictions far more severely than it rewards confident correct ones, since -log(p) diverges to infinity as p→0.
-->

---
glowSeed: 405
---

# Log Loss: Chain the Local Derivatives

<div border="2 solid violet-800" bg="violet-800/20" rounded-lg px-5 py-3>

$$J(w)=-\sum_i\left[y_i\log\hat p_i+(1-y_i)\log(1-\hat p_i)\right]$$

</div>

<div class="grid grid-cols-3 gap-3 mt-5 text-center">
<div v-click border="2 solid blue-800" bg="blue-800/20" rounded-lg p-4><code>w → z = xᵀw</code><div class="text-sm opacity-70 mt-2">∂z/∂w = x</div></div>
<div v-click border="2 solid teal-800" bg="teal-800/20" rounded-lg p-4><code>z → p̂ = σ(z)</code><div class="text-sm opacity-70 mt-2">∂p̂/∂z = p̂(1−p̂)</div></div>
<div v-click border="2 solid orange-800" bg="orange-800/20" rounded-lg p-4><code>p̂ → J</code><div class="text-sm opacity-70 mt-2">−y/p̂ + (1−y)/(1−p̂)</div></div>
</div>

<div v-click class="mt-6" border="2 solid white/10" bg="white/5" rounded-lg px-6 py-4>

$$\frac{\partial J}{\partial w}=\sum_i(\hat p_i-y_i)x_i$$

</div>

<!--
Do the full chain rule on the board, reusing the computation-graph language from the calculus unit: treat the computation as a chain of three steps, w → z=x^T w → p̂=σ(z) → J, and differentiate each local step. Step 1: z is linear in w, so ∂z/∂w = x. Step 2: p̂=σ(z), so ∂p̂/∂z = σ(z)(1-σ(z)) = p̂(1-p̂), reusing the clean sigmoid derivative from two slides ago. Step 3: differentiating J = -[y log p̂ + (1-y) log(1-p̂)] with respect to p̂ gives -y/p̂ + (1-y)/(1-p̂).

Multiply the three local derivatives together via the chain rule: ∂J/∂w = (∂J/∂p̂)(∂p̂/∂z)(∂z/∂w) = [-y/p̂ + (1-y)/(1-p̂)] · p̂(1-p̂) · x. Walk through the algebra live: distributing p̂(1-p̂) into the bracket, the -y/p̂ term becomes -y(1-p̂), and the (1-y)/(1-p̂) term becomes (1-y)p̂; expanding and collecting terms cancels the cross products, leaving exactly p̂-y. So the whole three-term chain collapses to the strikingly simple ∂J/∂w = (p̂-y)x, summed over all training examples. Pause on this result: it says the gradient contribution of each example is (predicted probability minus true label), scaled by that example's feature vector — larger when the model is more wrong, and pointing in the direction of the input features.
-->

---
glowSeed: 406
---

# The Gradient Has a Familiar Shape

<div class="grid grid-cols-2 gap-7 mt-3">
<div>
<div border="2 solid teal-800" bg="teal-800/20" rounded-lg p-4>

$$\nabla_wJ(w)=X^\top(\hat p-y)$$

</div>
<div class="mt-5 text-lg">Compare linear regression:</div>
<div class="mt-2" border="2 solid white/10" bg="white/5" rounded-lg p-4>

$$\nabla_wJ_{linear}=X^\top(Xw-y)$$

</div>
<div v-click class="mt-4 text-center text-teal-300">features × residual-like error</div>
</div>

```python
def gradient(X, y, w):
    p = sigmoid(X @ w)
    return X.T @ (p - y)

def loss(X, y, w):
    p = np.clip(sigmoid(X @ w), 1e-12, 1-1e-12)
    return -(y*np.log(p)+(1-y)*np.log(1-p)).sum()

def finite_difference(e):
    high = loss(X, y, w + 1e-6*e)
    low = loss(X, y, w - 1e-6*e)
    return (high - low) / 2e-6

numeric = np.array([
    finite_difference(e) for e in np.eye(3)
])
analytical = gradient(X, y, w)
assert np.allclose(analytical, numeric)
```
</div>

<!--
Written in matrix form for the whole dataset at once, the gradient is ∇_w J(w) = X^T(p̂-y), where X is the n×d design matrix (one row per example), p̂ is the length-n vector of predicted probabilities, and y is the length-n vector of true labels. Compare directly to the linear regression gradient ∇_w J_linear = X^T(Xw-y): both have the identical shape, "features transposed times an error vector" — the only thing that changed between the two algorithms is what fills the error vector. In linear regression it is the literal residual Xw-y (predicted number minus actual number); in logistic regression it is the analogous quantity p̂-y (predicted probability minus actual 0/1 label), a "residual-like" term because it plays the same structural role even though probabilities and continuous predictions are conceptually different.

Run the numerical check live: `finite_difference` approximates each partial derivative of the loss by perturbing one coordinate of w by a tiny amount and measuring the change in loss, without using any calculus — the assertion that this numerical approximation matches the closed-form `gradient` function to high precision is strong empirical evidence the chain-rule derivation on the previous two slides was done correctly. This features-times-error pattern recurs throughout the rest of the course, including in neural network backpropagation, so it is worth memorizing its shape now, even as the specific error term changes from model to model.
-->

---
glowSeed: 407
---

# Gradient Descent Is the Solution

<div class="grid grid-cols-2 gap-7 mt-3 items-center">
<div>
<div border="2 solid blue-800" bg="blue-800/20" rounded-lg p-4>

$$w_{t+1}=w_t-\alpha X^\top(\hat p_t-y),\qquad \hat p_t=\sigma(Xw_t)$$

</div>

```python
def fit_logistic(X, y, alpha=.1, steps=1000):
    Xb = np.c_[np.ones(len(X)), X]
    w = np.zeros(Xb.shape[1])
    for _ in range(steps):
        p = sigmoid(Xb @ w)
        w -= alpha * Xb.T @ (p-y) / len(y)
    return w

w_fit = fit_logistic(X, y)
assert np.isfinite(w_fit).all()
```
</div>
<div>
<svg role="img" aria-label="Log loss decreases and levels off over gradient descent iterations" viewBox="0 0 470 300" class="w-full">
  <line x1="45" y1="260" x2="440" y2="260" stroke="#64748b"/><line x1="45" y1="260" x2="45" y2="25" stroke="#64748b"/>
  <path d="M55 45 C100 115 125 175 190 215 C260 250 345 252 430 252" fill="none" stroke="#2dd4bf" stroke-width="5"/>
  <text x="170" y="292" fill="#94a3b8">iteration</text><text x="8" y="30" fill="#94a3b8">loss</text>
</svg>
<div v-click border="2 solid amber-800" bg="amber-800/20" rounded-lg p-4 class="text-sm">No closed form: <code>p̂ = σ(Xw)</code> makes <code>Xᵀ(p̂−y)=0</code> nonlinear in <code>w</code>.</div>
</div>
</div>

<!--
Recall that ordinary linear regression has a closed-form solution because setting its gradient X^T(Xw-y) to zero produces the normal equations, a linear system in w that can be solved directly with linear algebra. Logistic regression has no such shortcut: setting X^T(p̂-y)=0 to zero is nonlinear in w, because p̂ = σ(Xw) buries w inside a sigmoid — there is no algebraic manipulation that isolates w on one side of the equation. Iterative optimization is therefore mandatory, not optional; the update rule w_{t+1} = w_t - α·X^T(p̂_t - y_t) is one gradient-descent step, repeated until the loss stops decreasing meaningfully.

Introduce the loss-vs-iteration training curve here as a diagnostic students will see constantly for the rest of the course, especially with neural networks: a healthy run shows loss decreasing quickly at first and leveling off as it approaches a minimum; a curve that increases, oscillates wildly, or plateaus too early signals a learning-rate or convergence problem. Compare the coefficients produced by the from-scratch `fit_logistic` function against scikit-learn's `LogisticRegression` fit on the same data live — they should closely agree (scikit-learn uses a more sophisticated solver like L-BFGS or Newton's method by default, but converges to essentially the same optimum for a convex loss like this one).
-->

---
glowSeed: 408
---

# Regularized Logistic Regression

<div class="grid grid-cols-2 gap-8 mt-3">
<div>
<div border="2 solid violet-800" bg="violet-800/20" rounded-lg p-4>

$$J_{L2}(w)=J(w)+\lambda\|w\|_2^2$$

</div>
<v-clicks>

- L2 or L1 controls overfitting exactly as in regression
- scikit-learn uses $C=1/\lambda$
- **Smaller `C` means stronger regularization**
- Same bias–variance tradeoff, new loss

</v-clicks>
</div>
<div>

```python
for C in [100., 1., .01]:
    model = LogisticRegression(C=C, max_iter=1000)
    model.fit(X, y)
    size = np.abs(model.coef_).max()
    print(f"C={C:6.2f}  max|w|={size:.3f}")
```

<div class="grid grid-cols-3 gap-2 mt-5 text-center text-sm">
<div border="2 solid orange-800" bg="orange-800/20" rounded p-3><strong>C=100</strong><br/>weak penalty<br/>larger weights</div>
<div border="2 solid teal-800" bg="teal-800/20" rounded p-3><strong>C=1</strong><br/>balanced</div>
<div border="2 solid blue-800" bg="blue-800/20" rounded p-3><strong>C=.01</strong><br/>strong penalty<br/>simpler fit</div>
</div>
</div>
</div>

<!--
Regularization works exactly as it did in linear regression: add a penalty term to the loss that discourages large weights, trading a small increase in training error for reduced variance and better generalization. L2 regularization adds λ‖w‖²₂ (the squared Euclidean norm of the weight vector) to encourage small, spread-out weights; L1 regularization adds λ‖w‖₁ and can drive individual weights to exactly zero, performing implicit feature selection — the same tradeoff studied for ridge and lasso regression, just applied on top of log loss instead of squared error.

Flag the inverse naming convention slowly and explicitly, since it is a genuine source of student errors: scikit-learn's `LogisticRegression` is parameterized by C, not λ directly, where C = 1/λ. This means smaller C corresponds to stronger regularization (a small λ⁻¹ means a large effective λ), and larger C corresponds to weaker regularization — the opposite intuition from Ridge and Lasso, which use `alpha` directly as λ, where larger alpha means stronger regularization. A student who assumes "bigger number, more regularization" for both APIs will silently regularize in the wrong direction with LogisticRegression. Connect the resulting weight-magnitude and decision-boundary changes across the three C values to the same underfitting-to-overfitting spectrum visualized with polynomial degree and ridge/lasso penalty strength earlier in the course.
-->

---
glowSeed: 409
---

# Beyond Two Classes: Softmax

<div class="grid grid-cols-2 gap-8 mt-3">
<div>
<div border="2 solid blue-800" bg="blue-800/20" rounded-lg p-4>

$$P(y=k\mid x)=\frac{e^{x^\top w_k}}{\sum_{j=1}^{K}e^{x^\top w_j}}$$
$$J(W)=-\sum_i\sum_k\mathbb 1[y_i=k]\log P(y_i=k\mid x_i)$$

</div>
<div class="grid grid-cols-2 gap-3 mt-5 text-center text-sm">
<div border="2 solid white/10" bg="white/5" rounded p-3><strong>scores</strong><br/><span class="text-orange-300">−1.2</span> · <span class="text-teal-300">0.7</span> · <span class="text-blue-300">2.1</span></div>
<div border="2 solid teal-800" bg="teal-800/20" rounded p-3><strong>probabilities</strong><br/>.03 · .19 · .78<br/>sum = 1</div>
</div>
</div>

```python
X3, y3 = make_classification(
    n_samples=300, n_features=4,
    n_classes=3, n_informative=3,
    n_redundant=0, random_state=0)

model = LogisticRegression(max_iter=1000)
model.fit(X3, y3)
probs = model.predict_proba(X3[:3])
assert np.allclose(probs.sum(axis=1), 1)
```
</div>

<!--
Treat softmax as a natural generalization of everything just derived, not a separate model to learn from scratch. With K classes, fit one weight vector w_k per class, compute a linear score x^T w_k for each, and convert the K scores into a probability distribution with the softmax function: exponentiate each score (guaranteeing positivity) and divide by the sum of all K exponentiated scores (guaranteeing the K probabilities sum to exactly 1). Larger scores map to proportionally larger probabilities, but softmax also has a translation-invariance property: adding the same constant to every score leaves the output probabilities unchanged, since it factors out of both numerator and denominator.

Verify as an exercise that with exactly K=2 classes, softmax reduces algebraically to the ordinary two-class sigmoid — parameterize with a single weight vector w = w_1 - w_0 and the softmax probability for class 1 becomes exactly σ(x^T w), so binary logistic regression is a special case of the multiclass model, not a fundamentally different one. The loss generalizes the same way: log loss for two classes becomes categorical cross-entropy for K classes, − Σ_i Σ_k 1[y_i=k] log P(y_i=k|x_i), which just sums the negative log-probability the model assigned to each example's true class across the whole training set. This combination — a linear score per class, softmax to convert to probabilities, categorical cross-entropy as the loss — is exactly the standard output layer and loss function used by neural network classifiers throughout the rest of the course, so nothing here is thrown away going forward.
-->

---
layout: center
class: text-center
glowSeed: 410
---

# Model → Loss → Gradient → Optimizer

<div class="flex items-stretch gap-3 mt-10 text-sm">
<div v-click class="flex-1 p-4 rounded-lg bg-blue-500/20 border-2 border-blue-700"><strong>Model</strong><br/><code>σ(Xw)</code></div>
<div class="text-2xl self-center">→</div>
<div v-click class="flex-1 p-4 rounded-lg bg-violet-500/20 border-2 border-violet-700"><strong>Loss</strong><br/>cross-entropy</div>
<div class="text-2xl self-center">→</div>
<div v-click class="flex-1 p-4 rounded-lg bg-teal-500/20 border-2 border-teal-700"><strong>Gradient</strong><br/><code>Xᵀ(p̂−y)</code></div>
<div class="text-2xl self-center">→</div>
<div v-click class="flex-1 p-4 rounded-lg bg-orange-500/20 border-2 border-orange-700"><strong>Optimizer</strong><br/>gradient descent</div>
</div>

<div v-click class="grid grid-cols-2 gap-4 mt-9 text-left">
<div border="2 solid white/10" bg="white/5" rounded-lg p-4>Regularization controls complexity; softmax handles multiple classes.</div>
<div border="2 solid teal-800" bg="teal-800/20" rounded-lg p-4><strong>Next:</strong> k-NN — classification with no loss, optimizer, or learned parameters.</div>
</div>

<!--
Summarize the complete template built across this deck: model (sigmoid applied to a linear score), loss (cross-entropy, derived from maximum likelihood under a Bernoulli label model), gradient (the clean features-times-error shape X^T(p̂-y)), and optimizer (gradient descent, mandatory since there is no closed form). Restate the maximum-likelihood interpretation of log loss one more time as the throughline: minimizing cross-entropy is identical to finding the weights that make the observed training labels most probable under the model.

Despite competition from more flexible models, logistic regression remains extremely widely used in practice for two concrete reasons worth naming explicitly: its weights are directly interpretable as changes in log-odds (a one-unit increase in feature j multiplies the odds of the positive class by exp(w_j), holding other features fixed), which matters in regulated domains like credit and healthcare; and its predicted probabilities are often well-calibrated out of the box, meaning a predicted probability of 0.7 really does correspond to roughly 70% of such predictions being correct, which is not automatically true of every classifier. Preview k-NN, the deliberate contrast for the next deck: no loss function, no gradient, no learned parameters at all — classification purely by geometric proximity to stored training examples. Take questions before moving on.
-->
