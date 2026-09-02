---
theme: default
highlighter: shiki
css: unocss
colorSchema: dark
title: 'Loss Functions and Empirical Risk Minimization'
info: |
  ## Loss Functions and Empirical Risk Minimization
  What are we actually minimizing?
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
glowSeed: 281
---

# Loss Functions and ERM

### What are we actually minimizing?

<div class="pt-6 opacity-80 text-lg">Topic 5 of Core ML Concepts</div>

<div class="mt-12 rounded-xl border-2 border-teal-800 bg-teal-800/20 px-8 py-5 text-3xl">

$\displaystyle \arg\min_\theta\;\frac1n\sum_{i=1}^{n}\ell\big(f_\theta(x_i),y_i\big)$

</div>

<div class="mt-6 text-sm opacity-70">Zooming in on the symbol that tells a model what “better” means</div>

<!--
The goal of this lecture is to give formal definitions to loss, risk, and objective in the context of machine learning.

Every model-fitting procedure you will ever use — linear regression, logistic regression, decision trees, neural networks — reduces to choosing $\theta$ (the model's parameters) to make some quantity small.

The loss function is not a bookkeeping step computed after training finishes to report a number. It is the very definition of "better" that the entire fitting procedure — gradient descent, closed-form solving, whatever the algorithm — is built to pursue. Change the loss, and you change what "the best model" even means, even holding the model class and data fixed. 

Roadmap: we will formalize true risk versus empirical risk, examine the generalization gap this creates, survey concrete loss functions for regression and classification, derive where log loss comes from, and end by seeing how loss, ERM, and regularization combine into the single objective used in practice — tying together every earlier lecture in this module.
-->

---
glowSeed: 282
---

# True Risk vs. Empirical Risk

<div class="grid grid-cols-2 gap-6 mt-5">
<div v-click border="2 solid blue-800" bg="blue-800/20" rounded-lg p-5>
<div class="font-bold text-blue-300 text-xl">True risk · what we want</div>

$$R(\theta)=\mathbb E_{(x,y)\sim\mathcal D}[\ell(f_\theta(x),y)]$$

<div class="text-sm opacity-80">Average loss over the unknown population distribution.</div>
</div>
<div v-click border="2 solid teal-800" bg="teal-800/20" rounded-lg p-5>
<div class="font-bold text-teal-300 text-xl">Empirical risk · what we have</div>

$$\hat R(\theta)=\frac1n\sum_{i=1}^{n}\ell(f_\theta(x_i),y_i)$$

<div class="text-sm opacity-80">Average loss over one finite training sample.</div>
</div>
</div>

<div v-click mt-7 border="2 solid white/10" bg="white/5" rounded-lg p-5 text-center text-xl>

$$
\hat{\theta}_{\mathrm{ERM}} = \arg\min_{\theta} \hat{R}(\theta)
$$

<div class="text-sm opacity-75">Empirical Risk Minimization = “fit the model to the training data”</div>
</div>

<!--
 True risk $R(\theta)=\mathbb E_{(x,y)\sim\mathcal D}[\ell(f_\theta(x),y)]$ is the expected loss over $\mathcal D$, the true, unknown population distribution that generates every possible $(x,y)$ pair the model could ever encounter.
This is the quantity we actually care about: how will this model perform on data it has not seen. But $\mathcal D$ is never fully known or fully enumerable, so $R(\theta)$ cannot be computed exactly; it can only be estimated.

Empirical risk $\hat R(\theta)=\frac1n\sum_{i=1}^n\ell(f_\theta(x_i),y_i)$ replaces the true, unknown expectation with an average over the $n$ examples we actually have — the training sample.  

Empirical Risk Minimization (ERM), boxed at the bottom, is the strategy of choosing $\hat\theta$ to minimize $\hat R(\theta)$ instead of the true $R(\theta)$, simply because $\hat R$ is the only one we can actually compute.

The essential caveat, which the next slide builds on: minimizing $\hat R(\theta)$ does not automatically minimize $R(\theta)$. A model can drive empirical risk arbitrarily low — even to zero, by memorizing the training set — while true risk stays high. This is precisely the overfitting phenomenon from the Bias-Variance deck, now given a formal name: the empirical risk *underestimates* the true risk once the same data used to fit $\theta$ is also used to evaluate it, because the model has been explicitly optimized to look good on exactly those points.
-->

---
glowSeed: 283
---

# The Generalization Gap

<div class="grid grid-cols-2 gap-8 mt-3 items-center">
<div>
<svg viewBox="0 0 430 320" class="w-full">
  <ellipse cx="215" cy="160" rx="185" ry="120" fill="#2563eb22" stroke="#60a5fa" stroke-width="3"/>
  <text x="120" y="55" fill="#93c5fd" style="font-size: 17px">population 𝒟</text>
  <g fill="#94a3b8" opacity=".5"><circle cx="70" cy="150" r="4"/><circle cx="105" cy="80" r="4"/><circle cx="140" cy="245" r="4"/><circle cx="210" cy="65" r="4"/><circle cx="275" cy="230" r="4"/><circle cx="340" cy="105" r="4"/><circle cx="375" cy="180" r="4"/></g>
  <circle cx="215" cy="165" r="80" fill="#0f766e44" stroke="#2dd4bf" stroke-width="3"/>
  <g fill="#f8fafc"><circle cx="180" cy="135" r="6"/><circle cx="215" cy="110" r="6"/><circle cx="245" cy="145" r="6"/><circle cx="195" cy="195" r="6"/><circle cx="255" cy="205" r="6"/><circle cx="225" cy="175" r="6"/></g>
  <text x="168" y="260" fill="#5eead4" style="font-size: 15px">training sample</text>
</svg>
</div>

<div>
<div v-click border="2 solid teal-800" bg="teal-800/20" rounded-lg p-5 mb-5>
<div class="text-3xl font-bold text-teal-300">R̂(θ) low</div>
<div class="text-sm opacity-80 mt-2">The model fits observed examples.</div>
</div>
<div v-click border="2 solid orange-800" bg="orange-800/20" rounded-lg p-5>
<div class="text-3xl font-bold text-orange-300">R(θ) unknown</div>
<div class="text-sm opacity-80 mt-2">Future performance may still be poor.</div>
</div>
</div>
</div>

<div v-click class="mt-4 text-center text-xl">Overfitting means R̂(θ) falls while the gap R(θ) − R̂(θ) grows.</div>

<!--
 $\hat R(\theta)$, computed only over the teal points, can be pushed low by a flexible enough model, simply because there are only finitely many teal points to satisfy. $R(\theta)$, the average over the entire blue ellipse, is unaffected by how well the model does on those specific teal points — it depends on how well the model does everywhere.

Define "generalization gap" precisely: it is $R(\theta)-\hat R(\theta)$, the difference between true risk and empirical risk. 

A model that is well-behaved has a small gap — its training performance is a trustworthy preview of its future performance. Overfitting specifically means $\hat R(\theta)$ keeps falling while the gap $R(\theta)-\hat R(\theta)$ grows, i.e., the model is improving on the sample at the expense of the population.

This directly formalizes the diagnostic from the end of the Bias-Variance deck: what we called "comparing training error to validation error" is an *estimate* of the generalization gap, since we still cannot compute $R(\theta)$ exactly, but a large held-out validation set approximates $\mathcal D$ well enough to be a trustworthy stand-in. ERM by itself has no built-in defense against exploiting quirks of a finite sample — nothing in the ERM objective penalizes a model for behaving differently on unseen data, which is exactly why regularization (a later Core ML Concepts deck) and validation-based model selection exist: validation *measures* the gap, and regularization actively *constrains* it during fitting.
-->

---
glowSeed: 284
---

# What Makes a Useful Loss?

<div class="grid grid-cols-2 gap-4 mt-6">
<div v-click border="2 solid teal-800" bg="teal-800/20" rounded-lg p-5><div class="text-2xl">🧭</div><div class="font-bold mt-2">Aligned</div><div class="text-sm opacity-80 mt-2">low for predictions we value, high for costly mistakes</div></div>
<div v-click border="2 solid blue-800" bg="blue-800/20" rounded-lg p-5><div class="text-2xl">∇</div><div class="font-bold mt-2">Optimizable</div><div class="text-sm opacity-80 mt-2">differentiable or subdifferentiable enough to supply direction</div></div>
<div v-click border="2 solid violet-800" bg="violet-800/20" rounded-lg p-5><div class="text-2xl">⌣</div><div class="font-bold mt-2">Well-shaped</div><div class="text-sm opacity-80 mt-2">convex when possible, avoiding unnecessary local minima</div></div>
<div v-click border="2 solid orange-800" bg="orange-800/20" rounded-lg p-5><div class="text-2xl">⚖️</div><div class="font-bold mt-2">Task-aware</div><div class="text-sm opacity-80 mt-2">reflect target type, outliers, imbalance, and error costs</div></div>
</div>

<div v-click class="mt-8" border="2 solid amber-800" bg="amber-800/20" rounded-lg px-6 py-4 text-center text-lg>
The easiest loss to optimize is not always the metric stakeholders care about—so use a defensible surrogate.
</div>

<!--
Aligned: the loss must actually reflect what a wrong answer costs in the real application — predicting a house price $1,000 too low and predicting it $1,000 too high might not be equally bad in a lending context; a loss that is symmetric when the real costs are asymmetric is misaligned regardless of its mathematical elegance.

Optimizable: most training algorithms need a gradient or subgradient — a direction that tells the algorithm "make the parameters change this way to reduce loss." A loss that is flat almost everywhere provides no such direction.

Well-shaped: convexity means a loss function has a single global minimum with no separate local minima to get trapped in — for a convex loss, following the gradient downhill is guaranteed to eventually reach the best possible fit (subject to the model class). Non-convex losses (common in deep learning) do not offer this guarantee.

Task-aware: the same prediction task can call for different losses depending on context — 
- outlier-heavy data favors losses that don't let a few extreme points dominate  
- imbalanced classes may need per-class weighting 
- asymmetric error costs (a false negative in cancer screening is not equivalent to a false positive) may require a custom loss entirely. T
-->

---
glowSeed: 285
---

# Regression: Squared vs. Absolute Error

<div class="grid grid-cols-2 gap-7 mt-3 items-center">
<div>
<svg viewBox="0 0 440 310" class="w-full">
  <line x1="40" y1="260" x2="415" y2="260" stroke="#64748b" stroke-width="2"/><line x1="220" y1="285" x2="220" y2="20" stroke="#64748b" stroke-width="2"/>
  <path d="M65 35 Q220 485 375 35" fill="none" stroke="#60a5fa" stroke-width="4"/>
  <path d="M65 45 L220 260 L375 45" fill="none" stroke="#f59e0b" stroke-width="4"/>
  <text x="310" y="80" fill="#60a5fa" style="font-size: 14px">squared e²</text><text x="315" y="140" fill="#fbbf24" style="font-size: 14px">absolute |e|</text><text x="180" y="305" fill="#94a3b8" style="font-size: 14px">prediction error</text>
</svg>
</div>
<div>
<div v-click border="2 solid blue-800" bg="blue-800/20" rounded-lg p-4 mb-4>
<strong>Squared error · L2 loss</strong>
<div class="text-sm opacity-80 mt-2">smooth; large misses dominate; Gaussian noise model</div>

$$
\ell(y,\hat{y}) = (y-\hat{y})^2
$$

</div>
<div v-click border="2 solid orange-800" bg="orange-800/20" rounded-lg p-4>
<strong>Absolute error · L1 loss</strong>
<div class="text-sm opacity-80 mt-2">robust to outliers; corner at zero; Laplace noise model</div>

$$
\ell(y,\hat{y}) = \lvert y-\hat{y} \rvert
$$

</div>
</div>
</div>

<!--
Define the residual first: $e=y-\hat y$, 

Squared error, $\ell(y,\hat y)=(y-\hat y)^2$: because the error is squared, this means large errors are penalized disproportionately.

Absolute error, $\ell(y,\hat y)=|y-\hat y|$: the loss grows linearly with the size of the residual, this makes L1 loss far less sensitive to a small number of extreme outliers, since one huge residual cannot dominate the objective the way it can under squared error.  Note the visual "corner" at zero on the chart — |e| is not differentiable exactly at $e=0$, a minor complication for optimization that squared error does not have, since $e^2$ is smooth everywhere.

Common misconception: neither loss is "the correct one" in some absolute sense — the choice is a modeling decision about what kind of noise you believe is present and how much you want to penalize large mistakes.
-->

---
glowSeed: 286
---

# One Outlier, Two Very Different Objectives

```python {1|3-4|6-7|9-10|all}
import numpy as np

y_true = np.array([3., -.5, 2., 7., 50.])
y_pred = np.array([2.5, 0., 2., 8., 5.])

residuals = y_true - y_pred
squared = residuals ** 2
absolute = np.abs(residuals)

print(squared)  # [0.25, 0.25, 0, 1, 2025]
print(absolute) # [0.5, 0.5, 0, 1,   45]
```

<div class="grid grid-cols-2 gap-5 mt-6 text-center">
<div v-click border="2 solid blue-800" bg="blue-800/20" rounded-lg p-4><div class="text-4xl font-bold text-blue-300">2025</div><div class="text-sm opacity-75">squared contribution of the outlier</div></div>
<div v-click border="2 solid orange-800" bg="orange-800/20" rounded-lg p-4><div class="text-4xl font-bold text-orange-300">45</div><div class="text-sm opacity-75">absolute contribution of the outlier</div></div>
</div>

<!--
Walk the arithmetic explicitly, tying it to the previous slide's abstract shapes. Five true values `y_true` and five predictions `y_pred` give five residuals; the fourth point has residual $7-8=-1$ (a normal-sized miss), and the fifth point has residual $50-5=45$ — a genuine outlier, roughly 45 times larger than the other residuals.

Squared error for the outlier: $45^2=2025$. Summed across all five points, the total squared error is $0.25+0.25+0+1+2025=2026.5$ — the outlier alone accounts for over 99.9% of the total. If you were minimizing squared error by adjusting predictions, essentially all of the optimizer's "attention" (gradient signal) would be spent trying to reduce that one term, potentially at the cost of fit quality on the other four points.

Absolute error for the outlier: $|45|=45$. Summed, the total absolute error is $0.5+0.5+0+1+45=47$ — the outlier still dominates (about 96% of the total), but far less overwhelmingly than under squared error, and the other four points retain proportionally more influence on the total.

The concrete lesson: with just one bad data point (perhaps a data-entry error, or a genuine rare event), squared error and absolute error would push a model-fitting procedure toward meaningfully different solutions — squared error would sacrifice more accuracy on the "normal" points to accommodate the outlier; absolute error would largely ignore it. Neither choice is universally correct; it depends on whether that outlier represents a real, important pattern you want the model to respect, or noise/error you want the model to be robust against. Transition: an analogous choice — and an even sharper problem — comes up in classification.
-->

---
glowSeed: 287
---

# Classification: Why Not Optimize Accuracy?

<div class="grid grid-cols-2 gap-8 mt-4 items-center">
<div>
<svg viewBox="0 0 440 300" class="w-full">
  <line x1="35" y1="250" x2="415" y2="250" stroke="#64748b" stroke-width="2"/><line x1="220" y1="275" x2="220" y2="25" stroke="#64748b" stroke-width="2"/>
  <path d="M55 55 L218 55 L222 245 L400 245" fill="none" stroke="#f87171" stroke-width="5"/>
  <text x="60" y="42" fill="#fca5a5" style="font-size: 14px">wrong: loss 1</text><text x="315" y="235" fill="#fca5a5" style="font-size: 14px">correct: loss 0</text>
  <text x="172" y="292" fill="#94a3b8" style="font-size: 14px">decision margin</text>
</svg>
</div>
<div>
<div v-click border="2 solid red-800" bg="red-800/20" rounded-lg p-5>

$$\ell_{0\text{-}1}=\mathbb 1[\hat y\neq y]$$

</div>
<v-clicks>

- Flat almost everywhere
- Jumps at the decision boundary
- Gradient is zero or undefined
- Gives no signal about which direction improves the parameters

</v-clicks>
</div>
</div>

<div v-click class="mt-5" border="2 solid teal-800" bg="teal-800/20" rounded-lg p-4 text-center text-lg>
Train with a smooth <strong>surrogate loss</strong>; report accuracy when it suits the task.
</div>

<!--
Define $\ell_{0\text{-}1}$ precisely: $\mathbb 1[\hat y\neq y]$ is the indicator function, which equals 1 when the predicted label $\hat y$ disagrees with the true label $y$, and 0 when they agree. 

The problem is entirely about optimization mechanics, not about what the loss measures. This function has zero slope almost everywhere. Because the gradient is always zero or undefined, it gives no signal on how to reduce the lossl

Common misconception: this is not a claim that accuracy is a bad thing to *care about* — it remains the right thing to *report* to stakeholders in many tasks. It is specifically a poor training objective, because gradient-based optimizers cannot use it to find good parameters. Transition: the standard fix is to keep the same spirit — score correctness — with a smooth stand-in.
-->

---
glowSeed: 288
---

# Surrogate Losses Supply a Direction

<div class="grid grid-cols-2 gap-8 mt-3 items-center">
<div>
<svg viewBox="0 0 450 320" class="w-full">
  <line x1="45" y1="270" x2="420" y2="270" stroke="#64748b" stroke-width="2"/>
  <line x1="230" y1="290" x2="230" y2="18" stroke="#64748b" stroke-width="2"/>
  <g stroke="#64748b" stroke-width="1.5">
    <line x1="62" y1="266" x2="62" y2="274"/><line x1="146" y1="266" x2="146" y2="274"/>
    <line x1="272" y1="266" x2="272" y2="274"/><line x1="314" y1="266" x2="314" y2="274"/>
    <line x1="398" y1="266" x2="398" y2="274"/><line x1="226" y1="227" x2="234" y2="227"/>
  </g>
  <path d="M62 227 L230 227 L230 270 L398 270" fill="none" stroke="#f87171" stroke-width="3"/>
  <polyline points="62,20.7 72.5,35.9 83,51 93.5,66 104,80.9 114.5,95.6 125,110 135.5,124.2 146,138.1 156.5,151.5 167,164.5 177.5,176.8 188,188.5 198.5,199.5 209,209.6 219.5,218.8 230,227 240.5,234.3 251,240.6 261.5,246 272,250.6 282.5,254.4 293,257.5 303.5,260.1 314,262.1 324.5,263.8 335,265.1 345.5,266.2 356,267 366.5,267.6 377,268.2 387.5,268.6 398,268.9" fill="none" stroke="#2dd4bf" stroke-width="5" stroke-linejoin="round" stroke-linecap="round"/>
  <path d="M62 55 L272 270 L398 270" fill="none" stroke="#60a5fa" stroke-width="4" stroke-linejoin="round"/>
  <text x="78" y="216" fill="#fca5a5" style="font-size: 13px">0–1</text>
  <text x="82" y="38" fill="#5eead4" style="font-size: 13px">scaled logistic</text>
  <text x="92" y="92" fill="#93c5fd" style="font-size: 13px">hinge</text>
  <g fill="#94a3b8" style="font-size: 11px"><text x="54" y="288">−4</text><text x="225" y="288">0</text><text x="269" y="288">1</text><text x="394" y="288">4</text><text x="214" y="231">1</text></g>
  <text x="154" y="310" fill="#94a3b8" style="font-size: 14px">signed margin y × f(x)</text>
  <text x="20" y="155" fill="#94a3b8" style="font-size: 13px" transform="rotate(-90 20 155)">loss</text>
</svg>
</div>
<div>
<div v-click border="2 solid teal-800" bg="teal-800/20" rounded-lg p-4 mb-4><strong>Logistic loss</strong><div class="text-sm opacity-80 mt-2">smooth; rewards calibrated probabilities</div><div class="text-xs opacity-65 mt-1">curve scaled by 1/ln 2 to upper-bound 0–1 loss</div></div>
<div v-click border="2 solid blue-800" bg="blue-800/20" rounded-lg p-4><strong>Hinge loss</strong><div class="text-sm opacity-80 mt-2">penalizes points inside the margin; support vector machines</div></div>
<div v-click class="mt-5 text-sm opacity-80">Both provide useful upper bounds on the abrupt 0–1 objective.</div>
</div>
</div>

<!--
Define "signed margin," the x-axis of this chart: $yf(x)$, the true label (encoded as $\pm1$) multiplied by the model's raw, pre-threshold score $f(x)$. When the model's score has the same sign as the true label, $yf(x)>0$ and the prediction is correct; the larger $yf(x)$ is, the more confidently correct. When signs disagree, $yf(x)<0$ and the prediction is wrong, with more negative values meaning more confidently wrong. This single number generalizes "decision margin" from the previous slide into something continuous and signed.

Overlaid on the same axes: the red step function is 0-1 loss, flat and unhelpful as just discussed. The teal curve is the normalized logistic loss $\log(1+e^{-yf(x)})/\ln 2$. Dividing by $\ln 2$ scales its value at the decision boundary to 1, making the plotted curve an upper bound on 0-1 loss; this positive scaling does not change which model minimizes it. The standard natural-log version used on later slides has the same shape and optimizer, but different numerical units. The blue curve, hinge loss $\max(0,1-yf(x))$, decreases linearly until the margin reaches 1 (not just 0 — the model must be *confidently* correct, not merely correct), then flattens to exactly zero. Both plotted surrogates sit above the 0-1 loss everywhere, so minimizing them is a mathematically justified way to approximately minimize what we actually care about.

The two cards distinguish what each surrogate additionally rewards beyond bare correctness. Log loss, used in logistic regression and as the standard classification loss in neural networks, keeps decreasing as the predicted probability moves toward 1 for the correct class — it explicitly rewards *calibrated* probability estimates, not just correct hard labels, which the next slide quantifies. Hinge loss, the objective behind support vector machines, cares only about achieving a sufficient margin of confidence (margin $\geq 1$) and gives zero additional credit for probability beyond that — it optimizes for a robust separating boundary rather than well-calibrated probabilities. Transition: let's look closely at the log-loss numbers, and then derive where that formula actually comes from.
-->

---
glowSeed: 2885
---

# Where Log Loss Comes From: Bernoulli Likelihood

<div class="grid grid-cols-2 gap-8 mt-4 items-center">

<div>

<v-clicks>

- Model a binary label $y\in\{0,1\}$ as a coin flip with success probability $\hat p=f_\theta(x)$
- The Bernoulli probability mass function writes both cases in one formula: $P(y\mid \hat p)=\hat p^{\,y}(1-\hat p)^{1-y}$
- Assuming examples are drawn independently, the likelihood of the whole dataset is a product
- Maximizing likelihood is equivalent to minimizing its negative logarithm — logs turn products into sums

</v-clicks>

</div>

<div class="text-sm" border="2 solid white/10" bg="white/5" rounded-lg p-5>

$$
\begin{aligned}
\mathcal L(\theta) &= \prod_{i=1}^n \hat p_i^{\,y_i}(1-\hat p_i)^{1-y_i} \\
-\log \mathcal L(\theta) &= -\sum_{i=1}^n \big[y_i\log \hat p_i + (1-y_i)\log(1-\hat p_i)\big] \\
\tfrac1n\big(-\log \mathcal L(\theta)\big) &= \tfrac1n\sum_{i=1}^n \ell_{log}(y_i,\hat p_i)
\end{aligned}
$$

</div>

</div>

<div v-click class="mt-6 text-center text-lg" border="2 solid teal-800" bg="teal-800/20" rounded-lg p-4>
Cross-entropy loss <strong>is</strong> negative log-likelihood, averaged — ERM under log loss = maximum likelihood estimation.
</div>

<!--
Define:
  - $n$ is the number of training examples.
  - $y_i\in{0,1}$ is the observed label.
  - $\hat p_i=f_\theta(x_i)$ is the model’s predicted probability that (y_i=1).
  - $\mathcal L(\theta)$ measures how much probability the model assigns to all the labels that actually occurred.


  The exponents act like a switch:

  If $y_i=1$,

  $$
  \hat p_i^{1}(1-\hat p_i)^0=\hat p_i
  $$

  If $y_i=0$,

  $$
  \hat p_i^{0}(1-\hat p_i)^1=1-\hat p_i
  $$

**if $\hat p_i$ matches $y_i$, then the term $P(y\mid\hat p)=\hat p^y(1-\hat p)^{1-y}=1$**

  So each factor selects the probability the model assigned to the correct observed label. The product combines those probabilities across all examples, assuming the examples are independent.

  For instance, if the observed labels are (1,0,1) and the model predicts (0.9,0.2,0.7), then:

  $$
  \mathcal L(\theta)
  =0.9(1-0.2)(0.7)
  =0.504
  $$

  A larger likelihood means the model considered the observed dataset more probable. This is not yet a loss: training converts it into one by minimizing the negative log-likelihood shown on the next line.

**Maximizing how much they match is the same as minimizing the negative log because log is monotonic.**

  - Negative log-likelihood (NLL): “How improbable did the model consider the labels that actually occurred?”
  - Cross-entropy: “How different is the model’s predicted probability distribution from the target distribution?”

This slide answers the question the previous slide's speaker note only asserted: log loss is not an arbitrary smooth curve someone invented to replace 0-1 loss — it is derived from a specific probabilistic assumption about how labels are generated.

Step through the derivation left to right. We assume each label $y_i$ is generated by a Bernoulli (biased coin flip) random variable whose success probability is exactly the model's predicted probability $\hat p_i=f_\theta(x_i)$. The Bernoulli probability mass function $P(y\mid\hat p)=\hat p^y(1-\hat p)^{1-y}$ is a compact way to write two cases in one expression: plug in $y=1$ and the $(1-\hat p)^{1-y}$ factor becomes $(1-\hat p)^0=1$, leaving just $\hat p$; plug in $y=0$ and the $\hat p^y$ factor becomes $\hat p^0=1$, leaving just $1-\hat p$. So this one formula literally says "probability $\hat p$ if the label is 1, probability $1-\hat p$ if the label is 0" — exactly what you want a coin-flip model to say.

Assuming the training examples are drawn independently (the standard i.i.d. assumption underlying almost all of supervised learning), the probability of observing the entire dataset — the likelihood $\mathcal L(\theta)$ — is the product of each example's individual probability, by the definition of independence.

Products of many small probabilities are numerically painful (they underflow to zero) and analytically painful (products are hard to differentiate). Taking the negative logarithm converts the product into a sum via $\log(ab)=\log a+\log b$, and flips the maximization of likelihood into a minimization of negative log-likelihood, which is the conventional direction for a loss function. Dividing by $n$ turns the sum into an average — and that average is *exactly* $\ell_{log}$, the same log loss formula from the summary slide's boxed equation and the one used in the numeric example on the next slide.

The takeaway to state explicitly: minimizing empirical risk under log loss is mathematically identical to maximum likelihood estimation under a Bernoulli model. This is not a coincidence — most standard losses have exactly this kind of probabilistic derivation (squared error corresponds to a Gaussian noise assumption, absolute error to a Laplace noise assumption), which is why the earlier regression slide could say "Gaussian noise model" and "Laplace noise model" next to squared and absolute error. Transition: now that we know where the formula comes from, let's see it behave numerically on three concrete predictions.
-->

---
glowSeed: 289
---

# Cross-Entropy Punishes Confident Mistakes

<div border="2 solid teal-800" bg="teal-800/20" rounded-lg p-4>

$$\ell_{log}(y,\hat p)=-\left[y\log\hat p+(1-y)\log(1-\hat p)\right]$$

</div>

<div class="grid grid-cols-3 gap-4 mt-6 text-center">
<div v-click border="2 solid teal-800" bg="teal-800/20" rounded-lg p-5><div class="text-sm opacity-70">y = 1, p̂ = .99</div><div class="text-4xl font-bold text-teal-300 mt-2">0.01</div><div class="text-sm mt-2">confident + correct</div></div>
<div v-click border="2 solid amber-800" bg="amber-800/20" rounded-lg p-5><div class="text-sm opacity-70">y = 1, p̂ = .50</div><div class="text-4xl font-bold text-amber-300 mt-2">0.69</div><div class="text-sm mt-2">uncertain</div></div>
<div v-click border="2 solid red-800" bg="red-800/20" rounded-lg p-5><div class="text-sm opacity-70">y = 1, p̂ = .01</div><div class="text-4xl font-bold text-red-300 mt-2">4.61</div><div class="text-sm mt-2">confident + wrong</div></div>
</div>

```python
loss = -(y*np.log(p) + (1-y)*np.log(1-p))
```

<div v-click class="mt-4 text-center text-sm opacity-80">In code, clip probabilities away from exactly 0 and 1 for numerical stability.</div>

<!--
Read the formula symbol by symbol: $y\in\{0,1\}$ is the true label, $\hat p\in(0,1)$ is the model's predicted probability that $y=1$. When $y=1$, the second bracketed term vanishes ($1-y=0$) and the loss reduces to $-\log\hat p$; when $y=0$, the first term vanishes and the loss reduces to $-\log(1-\hat p)$ — exactly the "one formula, two cases" trick from the derivation slide two slides back, now with the negative sign and the log already applied.

Walk through the three numeric cards, all for a true label $y=1$. When $\hat p=.99$ (confident and correct), loss $=-\log(.99)\approx0.01$ — very small, since $\log$ of a number near 1 is near 0. When $\hat p=.50$ (maximally uncertain), loss $=-\log(.5)\approx0.69$ — a fixed, moderate penalty; note $\ln 2\approx0.693$ is a useful reference value, since it is the loss any model incurs by outputting pure 50/50 uncertainty. When $\hat p=.01$ (confident and *wrong*, since the true label is 1), loss $=-\log(.01)\approx4.61$ — over 400 times larger than the confident-correct case, because $-\log(x)\to\infty$ as $x\to0$.

This asymptotic blow-up as $\hat p\to0$ (when $y=1$) or $\hat p\to1$ (when $y=0$) is precisely why log loss is described as punishing confident mistakes severely: being wrong is bad, but being *confidently* wrong is disproportionately, unboundedly bad. This creates a strong incentive for a model to output calibrated, appropriately uncertain probabilities rather than overconfident ones — a real and desirable property in applications like medical risk scoring or fraud detection, where a model announcing 99% certainty and being wrong is far worse than a model that hedges.

Practical note on the code: because $\log(0)=-\infty$, if a model ever predicts exactly $\hat p=0$ or $\hat p=1$ and is wrong, the loss becomes infinite and training can crash with a NaN. The fix, mentioned in the caption, is to clip predicted probabilities into a safe range like $[10^{-7}, 1-10^{-7}]$ before taking the log — nearly every deep learning framework does this automatically inside its cross-entropy implementation. Transition: we have now seen loss functions for both regression and classification; the final piece is how loss combines with regularization into the objective actually solved in practice.
-->

---
glowSeed: 290
---

# The Objective Used in Practice

<div class="mt-8" border="2 solid white/10" bg="white/5" rounded-lg px-6 py-6>

$$
\hat\theta
=\arg\min_\theta
\underbrace{\frac1n\sum_{i=1}^{n}\ell(f_\theta(x_i),y_i)}_{\text{empirical risk}}
+\underbrace{\lambda R(\theta)}_{\text{regularization}}
$$

</div>

<div class="grid grid-cols-3 gap-4 mt-8 text-center">
<div v-click border="2 solid teal-800" bg="teal-800/20" rounded-lg p-4><strong>Loss</strong><div class="text-sm opacity-75 mt-2">defines each prediction's cost</div></div>
<div v-click border="2 solid blue-800" bg="blue-800/20" rounded-lg p-4><strong>Average</strong><div class="text-sm opacity-75 mt-2">turns examples into empirical risk</div></div>
<div v-click border="2 solid violet-800" bg="violet-800/20" rounded-lg p-4><strong>Penalty</strong><div class="text-sm opacity-75 mt-2">controls the generalization gap</div></div>
</div>

<div v-click class="mt-7 text-center text-lg">Optimization minimizes the objective; validation checks whether that objective transfers to unseen data.</div>

<!--
This single equation is the connective tissue for the entire Core ML Concepts module, so unpack every piece. $\hat\theta=\arg\min_\theta[\cdots]$ says we choose the parameter values $\hat\theta$ that minimize whatever follows in brackets. The first underbraced term, $\frac1n\sum_{i=1}^n\ell(f_\theta(x_i),y_i)$, is exactly the empirical risk $\hat R(\theta)$ from two slides back — it is the ERM part of the objective, built from whichever loss $\ell$ was chosen for the task (squared error, log loss, hinge loss, and so on, from earlier in this deck).

The second underbraced term, $\lambda R(\theta)$, is a regularization penalty (not to be confused with the true-risk $R(\theta)$ notation used earlier — here $R(\theta)$ denotes a complexity penalty on the parameters themselves, a slight notational overload students should be warned about explicitly, since the letter $R$ is doing double duty across this module's decks). $\lambda\geq0$ is a hyperparameter controlling how strongly that penalty is enforced: $\lambda=0$ recovers plain ERM with no regularization; larger $\lambda$ increasingly constrains the fit toward simpler parameter values, directly reducing variance at the cost of some bias — this is the mechanism, precisely stated, for what the upcoming Overfitting and Regularization deck explores at length.

Trace how every module topic appears in this one line: the model class $f_\theta$ and loss $\ell$ come from this deck; the averaging into empirical risk is ERM; the penalty term $\lambda R(\theta)$ is regularization; and — critically — *this equation alone cannot tell you if $\hat\theta$ is any good*, because it only measures fit to the training sample. Confirming that the fitted $\hat\theta$ actually generalizes requires evaluating it on a validation set never used in this minimization — the Train/Validation/Test Splits and Cross-Validation deck's entire subject. The closing sentence at the bottom draws this line explicitly: optimization (this equation) finds a good fit to training data; validation (a separate, later step) checks whether that fit transfers to new data.
-->

---
glowSeed: 291
---

# Core ML Concepts: One Connected Story

<div class="flex items-center gap-2 mt-14 text-center text-sm">
<div v-click class="flex-1 p-4 rounded-lg bg-teal-500/20 border-2 border-teal-700"><strong>Paradigms</strong><br><span class="opacity-70">what feedback?</span></div>
<div class="text-xl">→</div>
<div v-click class="flex-1 p-4 rounded-lg bg-blue-500/20 border-2 border-blue-700"><strong>Bias–variance</strong><br><span class="opacity-70">why errors?</span></div>
<div class="text-xl">→</div>
<div v-click class="flex-1 p-4 rounded-lg bg-orange-500/20 border-2 border-orange-700"><strong>Splits + CV</strong><br><span class="opacity-70">measure honestly</span></div>
<div class="text-xl">→</div>
<div v-click class="flex-1 p-4 rounded-lg bg-violet-500/20 border-2 border-violet-700"><strong>Regularization</strong><br><span class="opacity-70">control complexity</span></div>
<div class="text-xl">→</div>
<div v-click class="flex-1 p-4 rounded-lg bg-teal-500/20 border-2 border-teal-700"><strong>Loss + ERM</strong><br><span class="opacity-70">define fitting</span></div>
</div>

<div v-click class="mt-12" border="2 solid white/10" bg="white/5" rounded-lg px-6 py-5 text-center text-xl>
Next unit: <strong>Supervised Learning — Regression</strong>
<div class="text-sm opacity-75 mt-2">We now have the vocabulary to build and evaluate concrete models.</div>
</div>

<!--
Close the whole module by naming the throughline explicitly: these five decks are not independent topics that happen to be taught in sequence — they form one workflow, and each depends on the vocabulary of the one before it. Paradigms (supervised/unsupervised/reinforcement) established what kind of feedback a learning algorithm receives. Bias-variance explained, mechanically, why a fitted model makes errors — systematic (bias) versus sample-dependent (variance). Splits and cross-validation gave the honest measurement procedure needed to actually observe that bias-variance tradeoff instead of fooling ourselves with training error. Regularization gave a concrete lever to move along the tradeoff by constraining model complexity. And this deck, loss functions and ERM, gave the precise mathematical objective that ties all of it together: what a "fitted model" even means, why "empirical" risk is only an approximation of what we truly want, and how regularization plugs directly into that same objective as an extra penalty term.

Preview the transition explicitly: the next unit, Supervised Learning — Regression, is where all of this stops being abstract. Linear regression will be presented as a completely concrete instance of everything just covered: squared-error loss (from this deck), fit via ERM (this deck), optionally regularized as ridge or lasso regression (previous deck), evaluated honestly with train/validation/test splits (two decks back), and diagnosed for underfitting versus overfitting using the bias-variance framework (three decks back). Every subsequent model in this course — regression, classification, ensembles, neural networks — will be introduced as a new choice of $f_\theta$ and $\ell$ plugged into this same objective equation. Take questions before moving on.
-->
