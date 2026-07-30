---
theme: default
highlighter: shiki
css: unocss
colorSchema: dark
title: 'Overfitting and Regularization'
info: |
  ## Overfitting and Regularization
  Controlling model complexity on purpose.
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
glowSeed: 261
---

# Overfitting and Regularization

### Controlling model complexity on purpose

<div class="pt-6 opacity-80 text-lg">Topic 4 of Core ML Concepts</div>

<div class="grid grid-cols-2 gap-8 mt-14 items-center">
<div border="2 solid orange-800" bg="orange-800/20" rounded-lg p-4><div class="text-4xl">〰️〰〰️</div><div class="font-bold mt-3">Fit every fluctuation</div></div>
<div border="2 solid teal-800" bg="teal-800/20" rounded-lg p-4><div class="text-4xl">⌒</div><div class="font-bold mt-3">Recover the pattern</div></div>
</div>

<!--
Set up the module arc explicitly: Bias-Variance gave the theory (why models err — a systematic bias piece and a sample-dependent variance piece), and Train/Validation/Test Splits gave the measurement (how to honestly observe that bias-variance behavior without fooling ourselves with training error). This deck supplies the *lever*: regularization is the deliberate, engineered mechanism by which we trade a small amount of additional bias for a often much larger reduction in variance, when a model's flexibility is producing more variance than the data can support.

The two icons on the title slide preview the whole deck's central image: "fit every fluctuation" (orange) is what an unregularized, highly flexible model does when it has more freedom than the signal-to-noise ratio of the data warrants — it treats noise as signal. "Recover the pattern" (teal) is the goal — capture the true underlying relationship and let regularization discourage the model from also memorizing noise. Roadmap: define overfitting concretely, formalize the regularized objective, connect it to Bayesian priors, work through L2 (ridge) and L1 (lasso) penalties with their geometric intuition, discuss how to *choose* the regularization strength honestly via cross-validation, and finish with the broader family of regularization strategies beyond an explicit penalty term.
-->

---
glowSeed: 262
---

# What Overfitting Looks Like

<div class="grid grid-cols-2 gap-7 mt-4 items-center">
<div>
<svg viewBox="0 0 430 310" class="w-full">
  <g fill="#f8fafc"><circle cx="30" cy="230" r="5"/><circle cx="75" cy="115" r="5"/><circle cx="120" cy="145" r="5"/><circle cx="165" cy="60" r="5"/><circle cx="210" cy="130" r="5"/><circle cx="255" cy="75" r="5"/><circle cx="300" cy="185" r="5"/><circle cx="350" cy="140" r="5"/><circle cx="400" cy="235" r="5"/></g>
  <path d="M25 235 C45 280,55 80,75 115 S100 180,120 145 S140 30,165 60 S190 175,210 130 S235 35,255 75 S280 235,300 185 S330 105,350 140 S380 270,405 230" fill="none" stroke="#fb923c" stroke-width="4" />
  <path d="M25 235 Q205 15 405 235" fill="none" stroke="#2dd4bf" stroke-width="3" stroke-dasharray="7 5" />
</svg>
</div>

<div>
<v-clicks>

- Very low training error
- Much larger validation error
- Erratic predictions between examples
- Large or finely balanced coefficients
- Common with too many features, too much flexibility, or too much training

</v-clicks>

<div v-click class="mt-5" border="2 solid orange-800" bg="orange-800/20" rounded-lg p-4>
The orange curve fits the sample. The dashed teal curve better captures the process.
</div>
</div>
</div>

<!--
Look closely at the picture: the white dots are a fixed training sample generated from some smooth underlying process plus noise. The dashed teal curve is a smooth, low-degree fit — it misses most individual points slightly but tracks the overall trend. The solid orange curve threads through nearly every single point, bending sharply between them.

Walk through the bulleted symptoms and explain the mechanism behind each, since "overfitting" should not be a vague adjective by the end of this slide. Very low training error: the orange curve was optimized to pass near the training points, so of course it scores well on exactly those points. Much larger validation error: on a fresh point not used for fitting, the wild oscillations of the orange curve are as likely to be badly wrong as right, because those oscillations were shaped by noise specific to the training sample, not by the true underlying pattern. Erratic predictions between examples: notice how the orange curve does something different, and often extreme, in between training points — a model with this much freedom is not being constrained by anything except the individual data points it happened to see. Large or finely balanced coefficients is the *mechanical* explanation for why the curve can bend so sharply: in polynomial regression, sharp local wiggles require large-magnitude coefficients on the higher-order terms, often nearly canceling each other (a large positive coefficient and a large negative coefficient sitting close in value) to create fine local structure while roughly preserving the overall level.

That last point is the hinge to the rest of the deck: if large, finely-balanced coefficients are the *mechanism* that lets a model overfit, then a policy that makes large coefficients expensive should directly counteract overfitting — which is exactly what a regularization penalty does. Transition: the next slide writes that policy down as an explicit modified objective.
-->

---
glowSeed: 263
---

# Regularization: Fit Well, but Stay Simple

<div class="mt-8" border="2 solid white/10" bg="white/5" backdrop-blur-sm rounded-lg px-6 py-6>

$$
\hat\theta = \arg\min_\theta
\underbrace{\sum_{i=1}^{n}\ell(f_\theta(x_i),y_i)}_{\text{fit the data}}
+ \underbrace{\lambda R(\theta)}_{\text{penalize complexity}}
$$

</div>

<div class="grid grid-cols-3 gap-4 mt-8 text-center">
<div v-click border="2 solid teal-800" bg="teal-800/20" rounded-lg p-5><div class="text-3xl">🎯</div><div class="font-bold mt-2">Data fit</div><div class="text-sm opacity-75 mt-2">reduce training mistakes</div></div>
<div v-click border="2 solid blue-800" bg="blue-800/20" rounded-lg p-5><div class="text-3xl">🎚️</div><div class="font-bold mt-2">λ</div><div class="text-sm opacity-75 mt-2">controls the compromise</div></div>
<div v-click border="2 solid orange-800" bg="orange-800/20" rounded-lg p-5><div class="text-3xl">🪶</div><div class="font-bold mt-2">Penalty</div><div class="text-sm opacity-75 mt-2">prefer simpler parameters</div></div>
</div>

<div v-click class="mt-7 text-center text-lg">Accept a little more bias to gain a lot less variance.</div>

<!--
Define every piece. The first underbraced term $\sum_i\ell(f_\theta(x_i),y_i)$ is the same data-fit term from the Loss Functions deck (unnormalized here, but equivalent up to a constant factor of $n$ to the empirical risk $\hat R(\theta)$) — it wants $\theta$ to explain the training data well. The second term, $\lambda R(\theta)$, is new: $R(\theta)$ (careful — this reuses the letter $R$ but now means a complexity penalty on the parameters, not true risk) measures how "large" or "complex" the parameters are, and $\lambda\geq0$ is a scalar that controls how heavily that complexity is penalized relative to fitting the data.

Critical distinction to state explicitly: $\lambda$ is a *hyperparameter*, not a parameter. It is not learned by minimizing this same training objective — if it were, the optimizer would simply set $\lambda=0$ to remove the penalty and fit the training data as closely as possible, defeating the purpose. Instead $\lambda$ must be chosen by a separate procedure that can detect overfitting, namely evaluating candidate values of $\lambda$ on a validation set or via cross-validation (the subject two slides ahead) — this is a direct callback to the diagnostic built in the Bias-Variance and Splits/CV decks.

Two boundary cases worth stating explicitly: at $\lambda=0$, the penalty vanishes entirely and this objective reduces exactly to plain ERM from the Loss Functions deck — no regularization at all. As $\lambda\to\infty$, the penalty term dominates so completely that the optimizer is forced toward the simplest possible parameters (often all zeros), regardless of data fit — severe underfitting. The bottom banner states the core tradeoff in one sentence: we deliberately accept slightly worse fit to the training data (more bias) in exchange for a fitted model that is less sensitive to which particular training sample we happened to draw (less variance) — precisely the bias-variance tradeoff, now with an explicit knob to move along it.
-->

---
glowSeed: 264
---

# Regularization Is Also a Prior

<div class="grid grid-cols-2 gap-7 mt-5">
<div v-click border="2 solid blue-800" bg="blue-800/20" rounded-lg p-5>
<div class="font-bold text-blue-300 text-xl">Optimization view</div>
<div class="mt-4">Add a penalty to the empirical loss.</div>

$$-\log p(y\mid X,\theta)+\lambda R(\theta)$$

</div>
<div v-click border="2 solid violet-800" bg="violet-800/20" rounded-lg p-5>
<div class="font-bold text-violet-300 text-xl">Bayesian view</div>
<div class="mt-4">Place a prior on plausible parameters.</div>

$$-\log p(y\mid X,\theta)-\log p(\theta)$$

</div>
</div>

<div v-click class="mt-8" border="2 solid teal-800" bg="teal-800/20" rounded-lg px-6 py-5 text-center text-xl>
When $\lambda R(\theta)=-\log p(\theta)$, regularized fitting is <strong>MAP estimation</strong>.
</div>

<div v-click class="mt-5 grid grid-cols-2 gap-4 text-center text-sm">
<div bg="white/5" rounded-lg p-3>Gaussian prior ↔ L2 penalty</div><div bg="white/5" rounded-lg p-3>Laplace prior ↔ L1 penalty</div>
</div>

<!--
Two ways to arrive at the exact same optimization problem. The optimization view treats regularization as engineering: start from $-\log p(y\mid X,\theta)$, the negative log-likelihood (this is the same quantity as the empirical risk under a probabilistic loss — the log-loss derivation from the previous deck showed $-\log p(y\mid X,\theta)$ for a Bernoulli model is exactly $n$ times the average log loss), and simply bolt on a penalty term $\lambda R(\theta)$ because large weights seem undesirable.

The Bayesian view treats regularization as a modeling choice made *before* seeing any data: place a prior distribution $p(\theta)$ over plausible parameter values, encoding a belief such as "weights are probably small and near zero," then combine that prior with the data via Bayes' rule. The quantity we then maximize is the posterior $p(\theta\mid y,X)\propto p(y\mid X,\theta)p(\theta)$; taking the negative log of both sides (using $\log(ab)=\log a+\log b$) gives $-\log p(y\mid X,\theta)-\log p(\theta)$ — matching the optimization view's objective term for term, with $\lambda R(\theta)$ playing the exact role of $-\log p(\theta)$.

This equivalence is not a loose metaphor for intuition — it is an exact algebraic identity whenever $\lambda R(\theta)=-\log p(\theta)$, and the estimator that results, $\hat\theta=\arg\max_\theta p(\theta\mid y,X)$, is called MAP (Maximum A Posteriori) estimation: the single most probable parameter setting given both the data and the prior belief. The bottom row previews next slide's payoff and the slide after: a Gaussian prior's negative log is quadratic in $\theta$, producing the L2 penalty (ridge); a Laplace prior's negative log is linear in $|\theta|$, producing the L1 penalty (lasso) — the next inserted slide proves both of these explicitly with the actual algebra. Transition: let's see the L2 case worked out in full, starting with ridge regression.
-->

---
glowSeed: 2645
---

# Deriving L2 and L1 from Priors

<div class="grid grid-cols-2 gap-6 mt-4 text-sm">

<div v-click border="2 solid blue-800" bg="blue-800/20" rounded-lg p-4>
<div class="font-bold text-blue-300 mb-2">Gaussian prior → L2</div>

$$p(\theta_j)=\frac1{\sqrt{2\pi\tau^2}}\exp\!\left(-\frac{\theta_j^2}{2\tau^2}\right)$$
$$-\log p(\theta_j)=\frac{\theta_j^2}{2\tau^2}+\text{const}$$

Summing over $j$: $-\log p(\theta)=\tfrac1{2\tau^2}\|\theta\|_2^2+\text{const}$

</div>

<div v-click border="2 solid violet-800" bg="violet-800/20" rounded-lg p-4>
<div class="font-bold text-violet-300 mb-2">Laplace prior → L1</div>

$$p(\theta_j)=\frac1{2b}\exp\!\left(-\frac{|\theta_j|}{b}\right)$$
$$-\log p(\theta_j)=\frac{|\theta_j|}{b}+\text{const}$$

Summing over $j$: $-\log p(\theta)=\tfrac1b\|\theta\|_1+\text{const}$

</div>

</div>

<div v-click class="mt-6 text-center text-lg" border="2 solid teal-800" bg="teal-800/20" rounded-lg p-4>
Small prior variance $\tau^2$ (or scale $b$) ⇔ large $\lambda$ — a tighter prior belief in small weights is a stronger penalty.
</div>

<!--
This slide proves the claim the previous slide only stated: "Gaussian prior ↔ L2 penalty" and "Laplace prior ↔ L1 penalty" are not loose analogies, they are the same equation.

Left side: assume each parameter $\theta_j$ is drawn independently from a Gaussian (normal) distribution centered at zero with variance $\tau^2$ — the prior belief, before seeing data, that weights are probably small and symmetric around zero. Take the negative log of the Gaussian density; the normalizing constant $\frac1{\sqrt{2\pi\tau^2}}$ becomes an additive constant that does not depend on $\theta_j$ (so it does not affect where the minimum is), and $\exp(-\theta_j^2/2\tau^2)$ becomes $\theta_j^2/2\tau^2$ after the log cancels the exponential. Summing this over all parameters $j$ gives $\frac1{2\tau^2}\|\theta\|_2^2$ plus a constant — exactly proportional to the L2 penalty $\|\theta\|_2^2$ from the ridge slide, with $\lambda=\frac1{2\tau^2}$.

Right side: the same derivation with a Laplace (double-exponential) prior instead of Gaussian. Its density involves $|\theta_j|$ rather than $\theta_j^2$ inside the exponential, so taking the negative log produces $|\theta_j|/b$ instead of $\theta_j^2/(2\tau^2)$. Summing over $j$ gives exactly $\frac1b\|\theta\|_1$ — the L1 penalty from the lasso slide, with $\lambda=\frac1b$.

The bottom callout draws the practical conclusion: the regularization strength $\lambda$ is, under this Bayesian interpretation, literally a statement about how confident you are, a priori, that weights should be small. A very small prior variance $\tau^2$ (a strong, confident belief that weights are near zero) corresponds to a large $\lambda$ (a strong penalty); a large, diffuse prior variance corresponds to a small $\lambda$ (a weak penalty, close to plain unregularized ERM). This is the precise mathematical content behind the earlier claim "regularized fitting is MAP estimation" — MAP means Maximum A Posteriori, choosing $\theta$ to maximize the posterior probability $p(\theta\mid y,X)\propto p(y\mid X,\theta)p(\theta)$, and by Bayes' rule the negative log posterior is exactly $-\log p(y\mid X,\theta)-\log p(\theta)$, i.e. data-fit loss plus prior penalty — the same additive structure as the regularized objective. Transition: with the probabilistic justification established, let's look at *why* L1's geometry specifically produces exact zeros while L2's does not.
-->

---
glowSeed: 265
---

# L2 Regularization · Ridge

<div class="grid grid-cols-2 gap-8 mt-3">
<div>
<div border="2 solid blue-800" bg="blue-800/20" rounded-lg p-4>

$$R(\theta)=\|\theta\|_2^2=\sum_j\theta_j^2$$
$$\hat\theta_{ridge}=\arg\min_\theta\sum_i(y_i-x_i^\top\theta)^2+\lambda\|\theta\|_2^2$$

</div>

<v-clicks>

- Smoothly shrinks every weight toward zero
- Usually does not make weights exactly zero
- Gaussian prior under MAP
- “Weight decay” is the same idea in neural networks

</v-clicks>
</div>

<div>

```python
from sklearn.linear_model import Ridge

for alpha in [0., 1., 100.]:
    model = Ridge(alpha=alpha).fit(X, y)
    largest = abs(model.coef_).max()
    print(alpha, largest)
```

<div v-click class="mt-5 text-sm" border="2 solid teal-800" bg="teal-800/20" rounded-lg p-4>
Larger α makes extreme weights increasingly expensive.
</div>
</div>
</div>

<!--
Read the objective: $\hat\theta_{ridge}=\arg\min_\theta\sum_i(y_i-x_i^\top\theta)^2+\lambda\|\theta\|_2^2$ combines ordinary squared-error loss (from the Loss Functions deck) with the L2 penalty $\|\theta\|_2^2=\sum_j\theta_j^2$, the sum of squared coefficients, weighted by $\lambda$. Unlike the squared-error *loss*, which measures prediction error, this penalty measures parameter *magnitude* — it does not look at $x_i$ or $y_i$ at all, only at how large the fitted weights themselves are.

Walk through the bullet points with the mechanism behind each. "Smoothly shrinks every weight toward zero": because the penalty is quadratic and differentiable everywhere, its gradient $2\lambda\theta_j$ is proportional to the current weight — larger weights get pulled down harder, but the pull never becomes infinitely strong or discontinuous, so weights shrink gradually rather than snapping to zero. "Usually does not make weights exactly zero": since the quadratic penalty's gradient at $\theta_j=0$ is itself zero, there is no persistent pressure pushing a weight that's already near zero the rest of the way to exactly zero — it is shrunk, not eliminated (the next slide's L1 case behaves differently for exactly this reason). "Gaussian prior under MAP" ties directly to the new derivation slide two slides back. "Weight decay" is the name this exact same L2 penalty goes by in neural network training — the terminology differs across subfields, but the mathematics is identical.

The code demonstrates this concretely: as `alpha` (scikit-learn's name for $\lambda$) increases from 0 to 1 to 100, the magnitude of the largest fitted coefficient should shrink monotonically — run it live and confirm. Practical note worth stating explicitly, since it is a common source of bugs: ridge penalizes raw coefficient magnitude, so if features are on very different scales (e.g., "age in years" versus "income in dollars"), the penalty will unfairly suppress coefficients on large-scale features relative to small-scale ones. Standardizing features (subtracting the mean, dividing by the standard deviation) before fitting ridge — inside a pipeline, so it happens correctly within each cross-validation fold — makes every coefficient's scale comparable, so the shared penalty $\lambda$ treats all features fairly. Ridge also has a useful property with correlated features: rather than arbitrarily favoring one of two highly correlated predictors, it tends to *share* the coefficient weight between them roughly evenly.
-->

---
glowSeed: 266
---

# L1 Regularization · Lasso

<div class="grid grid-cols-2 gap-8 mt-3">
<div>
<div border="2 solid violet-800" bg="violet-800/20" rounded-lg p-4>

$$R(\theta)=\|\theta\|_1=\sum_j|\theta_j|$$
$$\hat\theta_{lasso}=\arg\min_\theta\sum_i(y_i-x_i^\top\theta)^2+\lambda\|\theta\|_1$$

</div>

<v-clicks>

- Encourages **sparse** parameter vectors
- Many coefficients become exactly zero
- Laplace prior under MAP
- Can perform rough feature selection

</v-clicks>
</div>

<div>

```python
from sklearn.linear_model import Lasso

for alpha in [.001, .1, 1.]:
    model = Lasso(
        alpha=alpha, max_iter=10_000
    ).fit(X, y)
    zeros = np.isclose(model.coef_, 0).sum()
    print(alpha, zeros)
```

<div v-click class="mt-4 text-sm" border="2 solid amber-800" bg="amber-800/20" rounded-lg p-4>
Sparsity helps interpretation, but correlated features can make the selection unstable.
</div>
</div>
</div>

<!--
Read the objective: identical to ridge except the penalty is $\|\theta\|_1=\sum_j|\theta_j|$, the sum of absolute values, instead of the sum of squares. This single change in exponent (1 instead of 2) has a qualitatively different effect, which the geometric slide two ahead explains visually.

"Encourages sparse parameter vectors" and "many coefficients become exactly zero": unlike ridge's quadratic penalty, whose gradient vanishes at $\theta_j=0$, the L1 penalty's (sub)gradient has constant magnitude $\lambda$ regardless of how small $\theta_j$ already is (except exactly at zero, where the penalty is non-differentiable and technically has a whole range of valid subgradients) — this means there is *always* a constant-strength pull toward zero, strong enough to push small, unimportant coefficients all the way to exactly zero rather than merely shrinking them. The practical consequence: a lasso-fitted model often has many coefficients that are exactly 0.0, effectively deleting those features from the model, which is why lasso is described as performing automatic feature selection.

"Laplace prior under MAP" is the exact derivation from two slides back. The code shows this directly: as `alpha` increases, `zeros` (the count of near-zero coefficients) should increase — smaller alpha values like 0.001 might zero out none, while alpha=1.0 might zero out most of the feature set; run it live to see the count grow.

Critical caveat, worth emphasizing since it is commonly misunderstood: a coefficient being exactly zero under lasso does *not* prove that feature is scientifically or causally unimportant. If two features are highly correlated (e.g., two near-duplicate sensor readings), lasso will often arbitrarily keep one and zero out the other — the selection can be unstable across resampled datasets, and the surviving feature is not necessarily more "true" or "important" than the discarded one, just the one the optimizer happened to favor. Interpret lasso sparsity as a useful practical simplification, not as a scientific claim about which features causally matter. Transition: why does this qualitative difference — smooth shrinkage versus hard zeroing — arise from what looks like a small change in the exponent? The geometry of the two penalty regions explains it directly.
-->

---
glowSeed: 267
---

# Why L1 Creates Zeros and L2 Usually Does Not

<div class="grid grid-cols-2 gap-8 mt-4 text-center">
<div v-click border="2 solid violet-800" bg="violet-800/20" rounded-lg p-4>
<div class="font-bold text-violet-300">L1 constraint</div>
<svg viewBox="0 0 300 230" class="w-full max-w-80 mx-auto">
  <line x1="25" y1="115" x2="275" y2="115" stroke="#64748b"/><line x1="150" y1="15" x2="150" y2="215" stroke="#64748b"/>
  <path d="M150 35 L240 115 L150 195 L60 115 Z" fill="#7c3aed33" stroke="#c084fc" stroke-width="3"/>
  <ellipse cx="245" cy="45" rx="105" ry="65" fill="none" stroke="#f8fafc" stroke-width="2" transform="rotate(-25 245 45)"/>
  <circle cx="150" cy="35" r="7" fill="#f59e0b"/><text x="162" y="31" fill="#fbbf24" style="font-size: 13px">axis corner</text>
</svg>
Corners lie on axes → exact zeros
</div>

<div v-click border="2 solid blue-800" bg="blue-800/20" rounded-lg p-4>
<div class="font-bold text-blue-300">L2 constraint</div>
<svg viewBox="0 0 300 230" class="w-full max-w-80 mx-auto">
  <line x1="25" y1="115" x2="275" y2="115" stroke="#64748b"/><line x1="150" y1="15" x2="150" y2="215" stroke="#64748b"/>
  <circle cx="150" cy="115" r="82" fill="#2563eb33" stroke="#60a5fa" stroke-width="3"/>
  <ellipse cx="245" cy="45" rx="105" ry="65" fill="none" stroke="#f8fafc" stroke-width="2" transform="rotate(-25 245 45)"/>
  <circle cx="205" cy="54" r="7" fill="#f59e0b"/><text x="215" y="49" fill="#fbbf24" style="font-size: 13px">generic tangent</text>
</svg>
Smooth boundary → small nonzero weights
</div>
</div>

<!--
This is the standard geometric picture for why L1 and L2 behave so differently, and it is worth building up slowly on the board if students have not seen constrained-optimization contour pictures before. Regularized least squares can be equivalently written as: minimize the squared-error loss $\sum_i(y_i-x_i^\top\theta)^2$ subject to a hard constraint that $\theta$ lies inside some allowed region — a diamond of "radius" determined by $\lambda$ for L1, a circle (ball) of radius determined by $\lambda$ for L2. (This equivalence between the penalized form and the constrained form is a standard Lagrangian-duality fact, worth mentioning even without full derivation.)

The white ellipses in each panel are contour lines of the squared-error loss — each ellipse is a set of $\theta$ values giving the same training error, with error decreasing toward the ellipse's center (the unconstrained least-squares solution, off to the side, outside the allowed region in this picture). Imagine inflating these ellipses outward from the unconstrained optimum until the smallest one just barely touches the allowed region (diamond or circle) — that first point of contact is the regularized solution, since it is the lowest-loss point that still satisfies the constraint.

Left panel, L1 (diamond): the diamond has sharp corners that sit exactly on the coordinate axes (where one coordinate of $\theta$ is exactly zero). Because corners are "pointy," an expanding ellipse is disproportionately likely to first touch the diamond exactly at one of those corners rather than along a flat edge — and touching at a corner means one parameter is exactly zero. This is the precise geometric reason lasso produces sparse solutions.

Right panel, L2 (circle): a circle has no corners and no preferred points — every point on its boundary looks locally the same. An expanding ellipse will generically touch the circle at some "generic" point, tangent to the boundary, which is essentially never exactly on a coordinate axis. This is why ridge shrinks weights smoothly toward zero without typically hitting exactly zero. Transition: given this precise mechanism, the strength $\lambda$ of either penalty still has to be chosen — the next slide addresses how.
-->

---
glowSeed: 268
---

# Choosing the Strength

<div class="grid grid-cols-2 gap-8 mt-3 items-center">
<div>
<svg viewBox="0 0 450 310" class="w-full">
  <line x1="45" y1="270" x2="420" y2="270" stroke="#64748b" stroke-width="2"/><line x1="45" y1="270" x2="45" y2="25" stroke="#64748b" stroke-width="2"/>
  <path d="M55 55 C155 100,260 180,410 245" fill="none" stroke="#fb923c" stroke-width="4"/>
  <path d="M55 230 C170 205,290 125,410 55" fill="none" stroke="#60a5fa" stroke-width="4"/>
  <path d="M55 150 C145 105,205 95,255 110 C325 132,365 185,410 238" fill="none" stroke="#2dd4bf" stroke-width="5"/>
  <circle cx="220" cy="102" r="7" fill="#f8fafc"/><line x1="220" y1="102" x2="220" y2="270" stroke="#f8fafc" stroke-dasharray="6 5"/>
  <text x="150" y="300" fill="#94a3b8" style="font-size: 14px">regularization strength λ</text><text x="62" y="138" fill="#2dd4bf" style="font-size: 14px">validation</text><text x="320" y="230" fill="#fb923c" style="font-size: 14px">variance</text><text x="320" y="80" fill="#60a5fa" style="font-size: 14px">bias²</text>
</svg>
</div>
<div>
<div v-click border="2 solid orange-800" bg="orange-800/20" rounded-lg p-4 mb-4><strong>Too small</strong><div class="text-sm opacity-80 mt-2">weak constraint → overfit</div></div>
<div v-click border="2 solid teal-800" bg="teal-800/20" rounded-lg p-4 mb-4><strong>Intermediate</strong><div class="text-sm opacity-80 mt-2">best validation performance</div></div>
<div v-click border="2 solid blue-800" bg="blue-800/20" rounded-lg p-4><strong>Too large</strong><div class="text-sm opacity-80 mt-2">strong constraint → underfit</div></div>
</div>
</div>

<!--
Point out explicitly that this chart is the exact same U-shaped picture from the Bias-Variance deck's tradeoff-curve slide, just with the x-axis relabeled from "model complexity" to "regularization strength λ" — and, crucially, the direction is *reversed*: increasing λ makes the model simpler (more constrained), so it moves *left* on the original complexity axis. Small λ (weak constraint) behaves like high complexity: low bias, high variance, risk of overfitting. Large λ (strong constraint) behaves like low complexity: high bias, low variance, risk of underfitting. This mapping — "λ is an inverse complexity dial" — is worth stating explicitly since students sometimes assume larger λ means "more model," which is backwards.

Walk through the three regime cards, which are literally the same three regimes from the earlier diagnostic slide, expressed now in terms of λ instead of raw model capacity: too small λ under-constrains the model, so it can still fit noise — overfitting. Too large λ over-constrains it, forcing coefficients toward zero regardless of what the data says — underfitting. The intermediate λ, marked with the dot, is where validation error (the teal curve — an *estimate* of true risk $R(\theta)$, not training error) is lowest.

Critical methodological point, worth stating as its own sentence: λ must be chosen using validation performance (or cross-validation, next slide), never training performance and never test-set performance. Training error is monotonically non-decreasing in λ (more constraint can only hurt training fit), so choosing λ by training error would always select λ=0 and defeat the purpose. Choosing λ by looking at test-set performance would contaminate the test set's whole purpose — the test set is reserved as a final, one-time-only measure of true risk, a discipline the next deck (Splits and Cross-Validation, chronologically the deck right before this one) establishes in detail; using it to tune λ turns it into a second validation set and invalidates any later claim about the deployed model's expected performance.
-->

---
glowSeed: 269
---

# Let Cross-Validation Choose

```python {1-2|4|5-6|8|all}
import numpy as np
from sklearn.linear_model import RidgeCV
from sklearn.pipeline import make_pipeline
from sklearn.preprocessing import StandardScaler

alphas = np.logspace(-3, 3, 20)
model = make_pipeline(
    StandardScaler(),
    RidgeCV(alphas=alphas, cv=5)
).fit(X, y)

print(model[-1].alpha_)
```

<div class="grid grid-cols-3 gap-4 mt-6 text-center text-sm">
<div v-click border="2 solid blue-800" bg="blue-800/20" rounded-lg p-4>Search orders of magnitude</div>
<div v-click border="2 solid teal-800" bg="teal-800/20" rounded-lg p-4>Average held-out performance</div>
<div v-click border="2 solid orange-800" bg="orange-800/20" rounded-lg p-4>Keep the test set locked</div>
</div>

<!--
Walk through the code, matching the click groups. Lines 1-2 import numpy and `RidgeCV`, a version of ridge regression that automatically searches over a list of candidate α (λ) values and picks the best one by internal cross-validation. Line 4, `np.logspace(-3, 3, 20)`, generates 20 candidate values spaced evenly on a *logarithmic* scale from $10^{-3}$ to $10^3$ — not a linear scale, because regularization strength is scale-sensitive: the difference between λ=0.001 and λ=0.01 can matter as much as the difference between λ=10 and λ=100, so an evenly-spaced linear grid would waste most of its resolution on uninteresting large values.

Lines 5-6 build a `Pipeline` combining `StandardScaler` (feature standardization, motivated on the ridge slide) with `RidgeCV(alphas=alphas, cv=5)` — 5-fold cross-validation internally tries each of the 20 candidate α values, fits on 4 folds, evaluates on the held-out fold, repeats across all 5 folds, and picks the α with the best average held-out performance. Line 8 prints `model[-1].alpha_`, the selected best value (using pipeline indexing to reach the last step, the `RidgeCV` object, whose fitted `alpha_` attribute holds the winner).

Emphasize the "inside a pipeline" detail specifically, since it prevents a subtle but common data leakage bug: if you standardized the *entire* dataset once before cross-validating, information about the validation fold's mean and variance would leak into the "training" computation for each fold, producing an overoptimistic λ choice. Wrapping `StandardScaler` inside the same `Pipeline` that gets cross-validated ensures the scaler is refit on only the training portion of each fold — this exact leakage issue is explored in depth in the Train/Validation/Test Splits and Cross-Validation deck. The three summary cards restate the workflow: search a wide, log-spaced range of strengths, average performance across held-out folds rather than trusting any single split, and never touch the final test set during this search — it is reserved for one honest evaluation at the very end.
-->

---
glowSeed: 270
---

# Regularization Is a Family of Strategies

<div class="grid grid-cols-3 gap-4 mt-6">
<div v-click border="2 solid teal-800" bg="teal-800/20" rounded-lg p-5><div class="text-2xl">➕</div><div class="font-bold mt-2">Penalty terms</div><div class="text-sm opacity-80 mt-2">L1, L2, elastic net, weight decay</div></div>
<div v-click border="2 solid blue-800" bg="blue-800/20" rounded-lg p-5><div class="text-2xl">⏹️</div><div class="font-bold mt-2">Early stopping</div><div class="text-sm opacity-80 mt-2">stop when validation error begins rising</div></div>
<div v-click border="2 solid violet-800" bg="violet-800/20" rounded-lg p-5><div class="text-2xl">🎭</div><div class="font-bold mt-2">Dropout</div><div class="text-sm opacity-80 mt-2">prevent brittle co-adaptation in networks</div></div>
<div v-click border="2 solid amber-800" bg="amber-800/20" rounded-lg p-5><div class="text-2xl">✂️</div><div class="font-bold mt-2">Simpler model</div><div class="text-sm opacity-80 mt-2">limit depth, degree, features, or width</div></div>
<div v-click border="2 solid orange-800" bg="orange-800/20" rounded-lg p-5><div class="text-2xl">📚</div><div class="font-bold mt-2">More data</div><div class="text-sm opacity-80 mt-2">constrain what patterns survive resampling</div></div>
<div v-click border="2 solid red-800" bg="red-800/20" rounded-lg p-5><div class="text-2xl">🧪</div><div class="font-bold mt-2">Augmentation</div><div class="text-sm opacity-80 mt-2">encode invariances with plausible examples</div></div>
</div>

<!--
The deck has focused on L1/L2 penalty terms because they are the cleanest to formalize mathematically, but the underlying goal — reduce variance by limiting how much a fitted model can react to the specific training sample it saw — is achieved by many different mechanisms, and this slide surveys them so students recognize regularization "in the wild" even when it does not look like an explicit $\lambda R(\theta)$ term.

Penalty terms: L1, L2 (just covered), elastic net (a weighted combination of both, getting some sparsity from L1 and some of L2's stability with correlated features), and weight decay (the neural-network name for L2, already noted). Early stopping: rather than adding a penalty, simply monitor validation error during iterative training (gradient descent, boosting) and halt once it stops improving or starts rising — this directly prevents the model from continuing to fit noise in later iterations, achieving a similar effect to a penalty without one being explicitly written down. Dropout: specific to neural networks, randomly disables a fraction of neurons on each training step, preventing units from co-adapting into brittle, overly specific joint representations — this will be covered in depth in the Neural Networks module.

Simpler model: directly limiting a model's capacity — maximum tree depth, polynomial degree, number of features, network width — has the same variance-reducing effect as a penalty, just enforced structurally rather than through an added loss term; this is literally "move left on the complexity axis" from the Bias-Variance deck's tradeoff curve. More data: increasing $n$ does not change the model, but it constrains which patterns can survive across resampled training sets — spurious noise patterns that happened to fit one small sample are increasingly unlikely to also fit a much larger sample, so variance falls simply from having more data, independent of any explicit regularization. Augmentation: generating additional, plausible training examples (rotated/cropped images, paraphrased text) encodes real-world invariances the model should respect, functionally enlarging the effective training set in a targeted way. Common thread across all six: none of these requires believing overfitting is caused by "large weights" specifically — any of them reduces the sensitivity of the fitted model to which particular sample it was trained on, which is the actual definition of reducing variance.
-->

---
glowSeed: 271
---

# The Practical Takeaway

<div class="grid grid-cols-2 gap-4 mt-7">
<div v-click border="2 solid orange-800" bg="orange-800/20" rounded-lg p-5><strong>Detect</strong><div class="text-sm opacity-80 mt-2">look for a train–validation gap</div></div>
<div v-click border="2 solid teal-800" bg="teal-800/20" rounded-lg p-5><strong>Constrain</strong><div class="text-sm opacity-80 mt-2">penalize or reduce effective complexity</div></div>
<div v-click border="2 solid blue-800" bg="blue-800/20" rounded-lg p-5><strong>Validate</strong><div class="text-sm opacity-80 mt-2">choose strength with cross-validation</div></div>
<div v-click border="2 solid violet-800" bg="violet-800/20" rounded-lg p-5><strong>Interpret</strong><div class="text-sm opacity-80 mt-2">L2 shrinks; L1 creates sparsity</div></div>
</div>

<div v-click class="mt-9 text-xl text-center">Next: <strong>Loss Functions and Empirical Risk Minimization</strong></div>

<!--
Recap the four-step workflow, each tied to a specific earlier slide: Detect — look for a gap between training and validation error, the same diagnostic introduced at the end of the Bias-Variance deck and formalized as the generalization gap in the next deck. Constrain — add an explicit penalty (L1/L2/elastic net) or reduce effective capacity through one of the six mechanisms just surveyed. Validate — never guess at λ; select it via cross-validation, keeping the test set untouched until final evaluation. Interpret — remember the geometric distinction: L2 shrinks all weights smoothly and shares credit across correlated features; L1 can zero weights out entirely, useful for sparsity and rough feature selection but not a proof of scientific irrelevance.

Throughout this deck we have focused entirely on the *penalty* term, $\lambda R(\theta)$ — how to constrain a model once we already know how to score its fit to data. We have been quietly borrowing the data-fit term $\sum_i\ell(f_\theta(x_i),y_i)$ from the Loss Functions deck without formalizing it ourselves. The final Core ML Concepts lecture, Loss Functions and Empirical Risk Minimization, is where that data-fit term gets its full formal treatment: precisely what a loss function is, how empirical risk (the sample average) approximates true risk (the population average) and why that approximation can fail, and why different tasks — regression, classification, ranking — call for structurally different losses. Combined, these two decks give the complete objective every model in this course optimizes: fit the data (Loss Functions) while staying appropriately simple (this deck).
-->
