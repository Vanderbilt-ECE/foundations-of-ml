---
theme: default
highlighter: shiki
css: unocss
colorSchema: dark
title: 'Probability and Statistics for Machine Learning'
info: |
  ## Probability and Statistics for Machine Learning
  Topic 1 of Mathematical Foundations — Foundations of Machine Learning.
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
glowSeed: 501
---

<div class="relative z-10">

# Probability and Statistics for Machine Learning

### Topic 1 of Mathematical Foundations

<div class="pt-6 opacity-80 text-lg">
Foundations of Machine Learning
</div>

<div class="pt-40 text-sm opacity-60">
Every loss function is, mechanically, a statement about probability
</div>

</div>

<!--
This is the middle lecture of the Mathematical Foundations unit: linear algebra gave us the objects, this lecture gives us the objective (what we're actually trying to maximize or minimize), and calculus will give us the mechanism for finding it.

Roadmap: random variables → distributions → expectation and variance → Bayes' theorem → maximum likelihood estimation → connecting MLE to loss functions like squared error and cross-entropy.
-->

---
glowSeed: 502
---

# Random Variables

<div class="grid grid-cols-2 gap-4 mt-4">

<div v-click>
<div class="p-4 text-sm [&>*]:my-1" border="2 solid teal-800" bg="teal-800/20" rounded-lg overflow-hidden>

**What it is**

A random variable assigns a number to the outcome of an uncertain process

</div>
</div>

<div v-click>
<div class="p-4 text-sm [&>*]:my-1" border="2 solid blue-800" bg="blue-800/20" rounded-lg overflow-hidden>

**Discrete**

Takes countable values (a coin flip, a class label)

</div>
</div>

<div v-click>
<div class="p-4 text-sm [&>*]:my-1" border="2 solid orange-800" bg="orange-800/20" rounded-lg overflow-hidden>

**Continuous**

Takes any value in a range (a sensor reading, a model's confidence score)

</div>
</div>

<div v-click>
<div class="p-4 text-sm [&>*]:my-1" border="2 solid violet-800" bg="violet-800/20" rounded-lg overflow-hidden>

**In ML**

Both the data and the model's predictions are usually treated as random variables

</div>
</div>

</div>

<div v-click class="mt-6 text-sm">

$$X: \Omega \to \mathbb{R}$$

</div>

<!--
Keep this concrete: in a classification problem, the true label y is a discrete random variable; in regression, the target y is continuous. The model itself defines a probability distribution over possible outputs — that's the bridge to everything that follows.
-->

---
glowSeed: 503
---

# Probability Distributions

<div class="grid grid-cols-2 gap-8 items-center mt-2">

<div>

<v-clicks>

- A **probability mass function (PMF)** gives $P(X=x)$ for discrete variables
- A **probability density function (PDF)** gives relative likelihood for continuous variables; probabilities come from area under the curve
- Must be non-negative and integrate (or sum) to 1
- The **Gaussian (normal) distribution** is the most common continuous distribution in ML

</v-clicks>

<div v-click class="mt-4 text-sm">

$$p(x) = \frac{1}{\sqrt{2\pi\sigma^2}} \exp\left(-\frac{(x-\mu)^2}{2\sigma^2}\right)$$

</div>

</div>

<div>
<svg viewBox="0 0 420 300" class="w-full">
  <line x1="30" y1="260" x2="400" y2="260" stroke="#475569" stroke-width="1.5" />
  <path d="M 40,255 C 100,255 130,60 210,60 C 290,60 320,255 380,255"
        fill="none" stroke="#38bdf8" stroke-width="3" />
  <line x1="210" y1="260" x2="210" y2="60" stroke="#94a3b8" stroke-width="1" stroke-dasharray="4 4" />
  <text x="195" y="280" fill="#94a3b8" style="font-size:13px">μ</text>
  <text x="20" y="20" fill="#94a3b8" style="font-size:14px">Gaussian density: bell curve centered at μ</text>
</svg>
</div>

</div>

<!--
Walk through the PMF/PDF distinction carefully: for a PDF, p(x) itself is not a probability and can exceed 1 — only the area under a stretch of the curve is a probability. This trips students up regularly.

The Gaussian earns special attention because squared-error loss in regression is a direct consequence of assuming Gaussian-distributed noise — a fact we'll derive explicitly a few slides from now. Point out the two parameters' roles: mu shifts the peak, sigma controls the spread.
-->

---
glowSeed: 504
---

# Distributions — Code

```python
import numpy as np

rng = np.random.default_rng(0)

samples = rng.normal(loc=0.0, scale=1.0, size=10000)   # standard Gaussian samples
print(samples.mean(), samples.std())                     # approx 0, 1

# evaluate the Gaussian PDF at a point
def gaussian_pdf(x, mu=0.0, sigma=1.0):
    return (1 / np.sqrt(2 * np.pi * sigma**2)) * np.exp(-0.5 * ((x - mu) / sigma) ** 2)

print(gaussian_pdf(0.0))   # peak density at the mean
print(gaussian_pdf(2.0))   # much lower density two standard deviations out
```

<!--
Run this live and show the sample mean/std converging to 0 and 1 as the sample size grows — a first taste of the law of large numbers, which underlies why we can estimate parameters from finite data at all.
-->

---
glowSeed: 520
---

# Expectation and Variance

<v-clicks>

- **Expectation** $\mathbb{E}[X]$ is the probability-weighted average value of a random variable
- **Variance** $\text{Var}(X) = \mathbb{E}[(X-\mathbb{E}[X])^2]$ measures spread around that average
- Expectation is linear: $\mathbb{E}[aX+b] = a\mathbb{E}[X]+b$, even when $X$ and other terms are dependent
- Every "average loss over a dataset" you compute is an empirical estimate of an expectation

</v-clicks>

<div v-click class="mt-6 text-sm">

$$\mathbb{E}[X] = \sum_x x\,P(X=x) \quad \text{or} \quad \int x\,p(x)\,dx$$
$$\text{Var}(X) = \mathbb{E}[X^2] - (\mathbb{E}[X])^2$$

</div>

<!--
This is the moment to say explicitly: when we write "loss = average of per-example losses over the training set," we are computing an empirical expectation, and the entire theory of why training on a finite dataset generalizes to new data rests on expectations and the law of large numbers.
-->

---
glowSeed: 521
---

# Expectation — Code

```python
import numpy as np

rng = np.random.default_rng(0)
X = rng.normal(loc=5.0, scale=2.0, size=100000)

print(X.mean())          # empirical estimate of E[X], approx 5.0
print(X.var())            # empirical estimate of Var(X), approx 4.0
print((X**2).mean() - X.mean()**2)   # same variance, computed via E[X^2] - E[X]^2
```

<!--
Point out that `.mean()` over a batch of per-example losses in any training loop is exactly this operation — an empirical expectation over a finite sample standing in for a true, unknown expectation over the full data distribution.
-->

---
glowSeed: 540
---

# Bayes' Theorem

<div class="grid grid-cols-2 gap-8 items-center mt-2">

<div>

<v-clicks>

- Bayes' theorem relates a **prior** belief to a **posterior** belief after seeing evidence
- $P(\theta \mid D)$: how likely are the parameters, given the data we observed?
- $P(D \mid \theta)$: the **likelihood** — how likely is this data, given these parameters?
- This single equation is the mathematical foundation of Bayesian machine learning

</v-clicks>

<div v-click class="mt-4 text-sm">

$$P(\theta \mid D) = \frac{P(D \mid \theta)\,P(\theta)}{P(D)}$$

</div>

</div>

<div>
<svg viewBox="0 0 400 260" class="w-full">
  <defs>
    <marker id="bayes-arrow" markerWidth="8" markerHeight="8" refX="4" refY="4" orient="auto">
      <path d="M0,0 L8,4 L0,8 Z" fill="#cbd5e1" />
    </marker>
  </defs>
  <rect x="10" y="85" width="95" height="70" rx="10" fill="#0b3550" stroke="#38bdf8" stroke-width="2" />
  <text x="57" y="112" text-anchor="middle" fill="#7dd3fc" style="font-size:14px">prior</text>
  <text x="57" y="137" text-anchor="middle" fill="#f8fafc" style="font-size:17px">P(θ)</text>
  <text x="119" y="128" text-anchor="middle" fill="#cbd5e1" style="font-size:22px">×</text>
  <rect x="135" y="85" width="120" height="70" rx="10" fill="#3f1e5f" stroke="#a78bfa" stroke-width="2" />
  <text x="195" y="112" text-anchor="middle" fill="#c4b5fd" style="font-size:14px">likelihood</text>
  <text x="195" y="137" text-anchor="middle" fill="#f8fafc" style="font-size:17px">P(D | θ)</text>
  <line x1="263" y1="120" x2="291" y2="120" stroke="#cbd5e1" stroke-width="2" marker-end="url(#bayes-arrow)" />
  <text x="278" y="105" text-anchor="middle" fill="#94a3b8" style="font-size:11px">normalize</text>
  <rect x="297" y="85" width="95" height="70" rx="10" fill="#173d35" stroke="#2dd4bf" stroke-width="2" />
  <text x="344" y="112" text-anchor="middle" fill="#5eead4" style="font-size:14px">posterior</text>
  <text x="344" y="137" text-anchor="middle" fill="#f8fafc" style="font-size:17px">P(θ | D)</text>
  <text x="200" y="205" text-anchor="middle" fill="#94a3b8" style="font-size:13px">evidence P(D) supplies the normalization</text>
</svg>
</div>

</div>

<!--
Frame the prior/posterior/likelihood vocabulary carefully since it recurs constantly: prior = what we believed before data, likelihood = how well parameters explain the data, posterior = updated belief after data. Explicitly preview that ridge regression's penalty term is exactly what falls out of putting a Gaussian prior on the weights and doing MAP estimation — full derivation two slides from now.
-->

---
glowSeed: 541
---

# Bayes' Theorem — Code

```python
# Classic example: a rare disease test
p_disease = 0.001                 # prior: P(disease)
p_pos_given_disease = 0.99        # sensitivity: P(positive | disease)
p_pos_given_healthy = 0.05        # false positive rate: P(positive | healthy)

p_positive = (p_pos_given_disease * p_disease
              + p_pos_given_healthy * (1 - p_disease))

p_disease_given_pos = (p_pos_given_disease * p_disease) / p_positive
print(p_disease_given_pos)   # roughly 0.02 -- surprisingly low despite 99% sensitivity
```

<!--
This example is deliberately counterintuitive: even a 99%-sensitive test gives only about a 2% chance of actually having the disease after one positive result, because the disease is so rare and the false-positive rate is 5%. This is the single best intuition-builder for why the prior term in Bayes' theorem matters as much as the likelihood.
-->

---
glowSeed: 560
---

# Maximum Likelihood Estimation

<div class="grid grid-cols-2 gap-4 mt-4">

<div v-click>
<div class="p-3 text-sm [&>*]:my-1" border="2 solid teal-800" bg="teal-800/20" rounded-lg overflow-hidden>

**MLE** picks the parameters $\theta$ that make the observed data most probable

</div>
</div>

<div v-click>
<div class="p-3 text-sm [&>*]:my-1" border="2 solid blue-800" bg="blue-800/20" rounded-lg overflow-hidden>

Formally: $\hat\theta_{MLE} = \arg\max_\theta P(D \mid \theta)$

</div>
</div>

<div v-click>
<div class="p-3 text-sm [&>*]:my-1" border="2 solid violet-800" bg="violet-800/20" rounded-lg overflow-hidden>

In practice we maximize the **log-likelihood** instead — same maximizer, but sums instead of products

</div>
</div>

<div v-click>
<div class="p-3 text-sm [&>*]:my-1" border="2 solid violet-800" bg="violet-800/20" rounded-lg overflow-hidden>

This is exactly the "objective" that calculus's gradient descent will later optimize

</div>
</div>

</div>

<div v-click class="mt-6 text-sm">

$$\hat\theta_{MLE} = \arg\max_\theta \sum_{i=1}^n \log P(x_i \mid \theta)$$

</div>

<!--
This slide is the hinge of the whole lecture: MLE is the general recipe, and the next slide shows that applying this recipe under a Gaussian noise assumption produces squared-error loss — the exact loss function used in linear regression, now derived from first principles rather than asserted.
-->

---
glowSeed: 561
---

# MLE Derives Squared-Error Loss

<v-clicks>

- Assume regression targets are the true function plus Gaussian noise: $y = f(x) + \varepsilon, \; \varepsilon \sim \mathcal{N}(0,\sigma^2)$
- Then $y$ given $x$ is Gaussian-distributed around the model's prediction $\hat y$
- Writing out the log-likelihood and dropping constants that don't depend on $\hat y$ leaves exactly the sum of squared errors
- **This is why "minimize squared error" is the standard regression loss** — it is MLE under a Gaussian noise assumption, not an arbitrary choice

</v-clicks>

<div v-click class="mt-4 text-sm">

$$\arg\max_{\hat y} \log \mathcal{N}(y; \hat y, \sigma^2) \;=\; \arg\min_{\hat y} (y - \hat y)^2$$

</div>

<!--
Walk through this derivation slowly since it is one of the most important connections in the entire course: MLE + Gaussian noise assumption = squared error loss. Every time a student writes `loss='mse'`, they are implicitly assuming Gaussian-distributed noise around the true function.
-->

---
glowSeed: 562
---

# MLE — Code

```python
import numpy as np
from scipy.optimize import minimize_scalar

rng = np.random.default_rng(0)
true_mu = 3.0
data = rng.normal(loc=true_mu, scale=1.0, size=200)

def negative_log_likelihood(mu):
    return -np.sum(-0.5 * (data - mu) ** 2)   # up to a constant, this is -log N(mu, 1)

result = minimize_scalar(negative_log_likelihood)
print(result.x)          # should be close to true_mu
print(data.mean())       # the MLE for a Gaussian's mean is just the sample mean
```

<!--
The punchline to run live: minimizing negative log-likelihood over mu lands exactly on the sample mean — showing that "the sample mean is the maximum likelihood estimate of a Gaussian's mean" isn't a coincidence, it's provable and this code proves it numerically.
-->

---
glowSeed: 580
---

# From MAP to Regularization

<div class="flex flex-col gap-2">

<div v-click>
<div class="px-3 py-2 text-sm [&>*]:my-1" border="2 solid teal-800" bg="teal-800/20" rounded-lg overflow-hidden>

**MAP (maximum a posteriori)** estimation adds a prior: $\hat\theta_{MAP} = \arg\max_\theta P(D\mid\theta)P(\theta)$

</div>
</div>

<div v-click>
<div class="px-3 py-2 text-sm [&>*]:my-1" border="2 solid blue-800" bg="blue-800/20" rounded-lg overflow-hidden>

Put a Gaussian prior on the weights ($\theta \sim \mathcal{N}(0,\tau^2)$) and take logs

</div>
</div>

<div v-click>
<div class="px-3 py-2 text-sm [&>*]:my-1" border="2 solid orange-800" bg="orange-800/20" rounded-lg overflow-hidden>

The prior term becomes an $L_2$ penalty on the weights — exactly the ridge regression penalty

</div>
</div>

<div v-click>
<div class="px-3 py-2 text-sm [&>*]:my-1" border="2 solid violet-800" bg="violet-800/20" rounded-lg overflow-hidden>

Regularization is not an ad-hoc trick; it is MAP estimation with a specific prior belief that weights should stay small

</div>
</div>

</div>

<div v-click class="mt-4 text-sm">

$$\hat\theta_{MAP} = \arg\min_\theta \underbrace{\sum_i (y_i - \hat y_i)^2}_{\text{data term (MLE)}} + \underbrace{\lambda\|\theta\|_2^2}_{\text{prior term}}$$

</div>

<!--
Close the loop explicitly: squared-error loss came from MLE under Gaussian noise (previous slides); the ridge penalty now comes from a Gaussian prior on the weights under MAP. Students should leave knowing that "loss function" and "regularizer" are not arbitrary engineering choices — they are statements about assumed noise and assumed prior belief, made precise through probability.
-->

---
layout: center
class: text-center
glowSeed: 600
---

# Summary and What's Next

<div class="grid grid-cols-3 gap-6 max-w-5xl mx-auto mt-8 text-left">

<div v-click>
<div class="px-6 py-5 [&>*]:my-1" border="2 solid teal-800" bg="teal-800/20" rounded-lg overflow-hidden>
<div class="text-3xl mb-2">📐</div>
<div class="font-bold mb-2">Linear Algebra</div>
Gave us the objects: vectors, matrices, weights.
</div>
</div>

<div v-click>
<div class="px-6 py-5 [&>*]:my-1" border="2 solid amber-800" bg="amber-800/20" rounded-lg overflow-hidden>
<div class="text-3xl mb-2">🎲</div>
<div class="font-bold mb-2">Probability</div>
Gives us the objective: maximize likelihood/posterior.
</div>
</div>

<div v-click>
<div class="px-6 py-5 [&>*]:my-1" border="2 solid violet-800" bg="violet-800/20" rounded-lg overflow-hidden>
<div class="text-3xl mb-2">📉</div>
<div class="font-bold mb-2">Calculus</div>
Gives us the mechanism: gradient descent finds the minimizer.
</div>
</div>

</div>

<div v-click class="mt-8 text-left max-w-3xl mx-auto">

- Random variables and distributions describe uncertainty in data and predictions
- Expectation and variance summarize a distribution; training loss is an empirical expectation
- Bayes' theorem combines a prior belief with observed data into a posterior belief
- MLE under a Gaussian noise assumption derives squared-error loss; MAP with a Gaussian prior derives ridge regularization

</div>

<div v-click class="mt-8 text-lg opacity-90">
Next: <strong>Calculus for Optimization</strong>
</div>

<!--
Use this slide to make the full arc of the Mathematical Foundations unit explicit: linear algebra's vectors and matrices are the objects being optimized; this lecture's likelihood and posterior are the objective being optimized; the calculus lecture's gradient descent — how it actually finds the parameters that maximize likelihood — is the mechanism that does the optimizing. Take questions before moving to Calculus for Optimization.
-->

---
layout: center
class: text-center
glowSeed: 229
---

# Thank You

### Questions &amp; Discussion

<div class="pt-6 opacity-80">
Probability and Statistics for Machine Learning · Mathematical Foundations
</div>

<!--
Take questions before moving to Calculus for Optimization.
-->
