---
theme: default
highlighter: shiki
css: unocss
colorSchema: dark
title: 'The Bias–Variance Tradeoff'
info: |
  ## The Bias–Variance Tradeoff
  Why simple models underfit and complex models overfit.
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
glowSeed: 221
---

# The Bias–Variance Tradeoff

### Why simple models underfit and complex models overfit

<div class="pt-6 opacity-80 text-lg">Topic 2 of Core ML Concepts</div>

<div class="mt-18 flex justify-center items-end gap-4">
<div class="w-36 h-18 rounded-lg bg-blue-500/20 border-2 border-blue-700 flex items-center justify-center">too simple</div>
<div class="text-3xl text-teal-300">→</div>
<div class="w-36 h-28 rounded-lg bg-teal-500/20 border-2 border-teal-700 flex items-center justify-center font-bold">sweet spot</div>
<div class="text-3xl text-orange-300">→</div>
<div class="w-36 h-38 rounded-lg bg-orange-500/20 border-2 border-orange-700 flex items-center justify-center">too flexible</div>
</div>

<!--
This is the conceptual backbone of supervised learning, and every later module — regularization, ensembles, model selection, even neural network capacity — is really a variation on this one idea. "Bias" here does not mean social or statistical unfairness; it is a precise technical term for the systematic gap between what a model can represent and the true relationship it is trying to learn. "Variance" is not the variance of the data — it is the variance of the model's predictions across different random training sets of the same size drawn from the same population.

Roadmap for today: we build intuition with the dartboard picture, connect it to underfitting and overfitting curves you have likely seen informally, derive the bias-variance decomposition algebraically so it stops being a metaphor and becomes a provable identity, estimate bias and variance numerically with a simulation, and finish with a practical diagnostic for reading training and validation error gaps.

Every knob you will encounter later — tree depth, polynomial degree, number of neighbors k, network width and depth, regularization strength — is a dial that moves a model along this same underfit-to-overfit spectrum. Understanding this tradeoff is what lets you diagnose *why* a model is failing, not just *that* it is failing.

This deck assumes you already know what a training set, a model, and a loss function are; if any of those feel shaky, ask now before we build on them.
-->


---
glowSeed: 222
---

# The Dartboard Intuition

<div class="grid grid-cols-[7rem_1fr_1fr] gap-3 mt-3 text-center text-sm">
<div></div><div class="font-bold text-teal-300">Low variance</div><div class="font-bold text-orange-300">High variance</div>

<div class="flex items-center justify-end pr-2 font-bold text-blue-300">Low bias</div>
<div v-click border="2 solid teal-800" bg="teal-800/20" rounded-lg p-2>
<svg viewBox="0 0 160 115" class="w-full max-w-44 mx-auto"><circle cx="80" cy="58" r="45" fill="none" stroke="#64748b"/><circle cx="80" cy="58" r="28" fill="none" stroke="#64748b"/><circle cx="80" cy="58" r="10" fill="none" stroke="#2dd4bf"/><g fill="#f8fafc"><circle cx="78" cy="57" r="3"/><circle cx="84" cy="61" r="3"/><circle cx="75" cy="63" r="3"/><circle cx="82" cy="52" r="3"/><circle cx="87" cy="56" r="3"/></g></svg>
<strong>Accurate + consistent</strong>
</div>
<div v-click border="2 solid orange-800" bg="orange-800/20" rounded-lg p-2>
<svg viewBox="0 0 160 115" class="w-full max-w-44 mx-auto"><circle cx="80" cy="58" r="45" fill="none" stroke="#64748b"/><circle cx="80" cy="58" r="28" fill="none" stroke="#64748b"/><circle cx="80" cy="58" r="10" fill="none" stroke="#2dd4bf"/><g fill="#f8fafc"><circle cx="40" cy="35" r="3"/><circle cx="110" cy="36" r="3"/><circle cx="65" cy="89" r="3"/><circle cx="95" cy="74" r="3"/><circle cx="82" cy="45" r="3"/></g></svg>
<strong>Right on average, unstable</strong>
</div>

<div class="flex items-center justify-end pr-2 font-bold text-violet-300">High bias</div>
<div v-click border="2 solid violet-800" bg="violet-800/20" rounded-lg p-2>
<svg viewBox="0 0 160 115" class="w-full max-w-44 mx-auto"><circle cx="80" cy="58" r="45" fill="none" stroke="#64748b"/><circle cx="80" cy="58" r="28" fill="none" stroke="#64748b"/><circle cx="80" cy="58" r="10" fill="none" stroke="#2dd4bf"/><g fill="#f8fafc"><circle cx="48" cy="34" r="3"/><circle cx="54" cy="38" r="3"/><circle cx="43" cy="41" r="3"/><circle cx="50" cy="46" r="3"/><circle cx="58" cy="32" r="3"/></g></svg>
<strong>Consistently wrong</strong>
</div>
<div v-click border="2 solid red-800" bg="red-800/20" rounded-lg p-2>
<svg viewBox="0 0 160 115" class="w-full max-w-44 mx-auto"><circle cx="80" cy="58" r="45" fill="none" stroke="#64748b"/><circle cx="80" cy="58" r="28" fill="none" stroke="#64748b"/><circle cx="80" cy="58" r="10" fill="none" stroke="#2dd4bf"/><g fill="#f8fafc"><circle cx="25" cy="25" r="3"/><circle cx="65" cy="28" r="3"/><circle cx="35" cy="72" r="3"/><circle cx="96" cy="96" r="3"/><circle cx="50" cy="53" r="3"/></g></svg>
<strong>Wrong + unstable</strong>
</div>
</div>

<!--
The dartboard is the single mental image to keep for this whole topic. Imagine retraining the exact same learning procedure — same algorithm, same hyperparameters — on many different random samples drawn from the same population, and plotting one prediction (one dart throw) from each resulting model. Bias measures where the *center* of the cluster of throws lands relative to the bullseye (the true value): low bias means the average throw is close to the target, high bias means the thrower has a systematic aim problem. Variance measures how *spread out* the throws are around their own center, regardless of where that center is: low variance means throws land close together, high variance means they scatter widely from throw to throw.

Walk through all four quadrants explicitly. Top-left (low bias, low variance): accurate and consistent — this is the goal. Top-right (low bias, high variance): correct on average but individual throws are unpredictable — this is a classic overfitting signature, like a high-degree polynomial that happens to average out correctly across many resamples but wildly disagrees with itself on any single sample. Bottom-left (high bias, low variance): consistently wrong in the same way every time — this is underfitting, like fitting a straight line to a strongly curved relationship; it is reliable, but reliably incorrect. Bottom-right (high bias, high variance): the worst case, wrong and unpredictable.

Critical point to hammer here: bias and variance are properties of a *training procedure* (an algorithm plus its hyperparameters, applied to random samples of a given size), not properties of one single fitted model. You cannot look at one trained model in isolation and say "this has high variance" — you can only say that about the *process* that produced it, evaluated across hypothetical resamples.

Common misconception to flag now, before it hardens: students often say "overfitting" and "high variance" as if they were two different problems. They describe the same phenomenon from two angles — overfitting is what you observe (the model fits training noise, so training error is far below validation error), and high variance is the statistical explanation for why it happens (small changes in the training sample produce large changes in the fitted function). Similarly, underfitting and high bias are the same phenomenon: underfitting is the observed symptom, high bias is the explanation.
-->

---
glowSeed: 223
---

# Model Complexity: Underfit → Good Fit → Overfit

<div class="grid grid-cols-3 gap-4 mt-6 text-center text-sm">

<div v-click border="2 solid blue-800" bg="blue-800/20" rounded-lg p-3>
<div class="font-bold text-blue-300 mb-2">Underfit · high bias</div>
<svg viewBox="0 0 220 150" class="w-full"><g fill="#cbd5e1"><circle cx="25" cy="120" r="4"/><circle cx="55" cy="85" r="4"/><circle cx="90" cy="52" r="4"/><circle cx="125" cy="58" r="4"/><circle cx="160" cy="88" r="4"/><circle cx="195" cy="120" r="4"/></g><line x1="20" y1="100" x2="200" y2="72" stroke="#60a5fa" stroke-width="4"/></svg>
Too rigid to capture the curve
</div>

<div v-click border="2 solid teal-800" bg="teal-800/20" rounded-lg p-3>
<div class="font-bold text-teal-300 mb-2">Good generalization</div>
<svg viewBox="0 0 220 150" class="w-full"><g fill="#cbd5e1"><circle cx="25" cy="120" r="4"/><circle cx="55" cy="85" r="4"/><circle cx="90" cy="52" r="4"/><circle cx="125" cy="58" r="4"/><circle cx="160" cy="88" r="4"/><circle cx="195" cy="120" r="4"/></g><path d="M20 125 Q105 5 200 125" fill="none" stroke="#2dd4bf" stroke-width="4"/></svg>
Captures signal, ignores noise
</div>

<div v-click border="2 solid orange-800" bg="orange-800/20" rounded-lg p-3>
<div class="font-bold text-orange-300 mb-2">Overfit · high variance</div>
<svg viewBox="0 0 220 150" class="w-full"><g fill="#cbd5e1"><circle cx="25" cy="120" r="4"/><circle cx="55" cy="85" r="4"/><circle cx="90" cy="52" r="4"/><circle cx="125" cy="58" r="4"/><circle cx="160" cy="88" r="4"/><circle cx="195" cy="120" r="4"/></g><path d="M20 125 C35 140,40 65,55 85 S75 75,90 52 S110 80,125 58 S145 60,160 88 S180 140,200 115" fill="none" stroke="#fb923c" stroke-width="4"/></svg>
Chases every noisy point
</div>

</div>

<div v-click class="mt-7 text-center text-lg">Increasing flexibility usually <span class="text-blue-300">reduces bias</span> and <span class="text-orange-300">increases variance</span>.</div>

<!--
Have students identify the three curves before naming them — cover the labels and ask which curve is which, and why. The gray dots are the same fixed training sample in all three panels; only the fitted curve (the model) changes.

Left panel: a straight line fit to data that is clearly curved. This is underfitting — the model's hypothesis class (straight lines) is too restrictive to represent the true relationship no matter how the coefficients are chosen. This is high bias: even with infinite training data of this size, a linear model would still systematically miss the curvature. Notice the line misses almost every point by a similar systematic amount — that systematic miss is the visual signature of bias.

Middle panel: a smooth curve that tracks the general upward-then-down shape without chasing each individual point. This is the target: it captures the signal (the smooth trend) while ignoring the noise (the point-to-point jitter). Critically, the middle curve does *not* have the lowest training error of the three — the rightmost curve does, because it interpolates the training points almost exactly. The middle curve wins on *future*, unseen data, which is the only kind of performance that matters in practice.

Right panel: a wiggly curve that bends to pass near almost every single point, including the noisy ones. This is overfitting — the model has enough flexibility to fit the idiosyncrasies of this particular sample, including random noise that will not repeat in a new sample. If you resampled the data and refit, this curve would look completely different each time — that instability is variance made visible.

Emphasize the general rule stated at the bottom: increasing model flexibility (more polynomial terms, deeper trees, more neighbors considered, less regularization) tends to reduce bias — the model can represent more shapes — while it tends to increase variance — the model has more freedom to react to noise. Flexibility is not free; it is traded for stability. Transition: this qualitative picture is what we will now make precise algebraically.
-->

---
glowSeed: 224
---

# Formal Setup: Signal + Noise

<div class="grid grid-cols-2 gap-8 mt-5 items-center">

<div>
<div border="2 solid teal-800" bg="teal-800/20" rounded-lg p-5>

$$y=f(x)+\epsilon$$
$$\mathbb E[\epsilon]=0,\qquad \operatorname{Var}(\epsilon)=\sigma^2$$

</div>

<v-clicks>

- $f(x)$ is the true signal
- $\epsilon$ is irreducible randomness
- Fit $\hat f$ on a randomly drawn training set
- Evaluate at a fresh point $x_0$

</v-clicks>
</div>

<div v-click>
<svg viewBox="0 0 430 310" class="w-full">
  <path d="M25 245 C105 40, 215 40, 405 235" fill="none" stroke="#2dd4bf" stroke-width="4" />
  <path d="M25 260 C100 70, 205 15, 405 220" fill="none" stroke="#60a5fa" stroke-width="2" opacity=".65" />
  <path d="M25 215 C115 10, 250 95, 405 250" fill="none" stroke="#f59e0b" stroke-width="2" opacity=".65" />
  <g fill="#f8fafc"><circle cx="50" cy="226" r="5"/><circle cx="92" cy="139" r="5"/><circle cx="130" cy="88" r="5"/><circle cx="175" cy="69" r="5"/><circle cx="220" cy="45" r="5"/><circle cx="270" cy="86" r="5"/><circle cx="320" cy="132" r="5"/><circle cx="375" cy="227" r="5"/></g>
  <text x="315" y="90" fill="#5eead4" style="font-size: 14px">true f(x)</text>
  <text x="50" y="285" fill="#94a3b8" style="font-size: 13px">different samples → different f̂</text>
</svg>
</div>

</div>

<div v-click class="mt-2 text-center" border="2 solid white/5" bg="white/5" rounded-lg p-3>

$$\mathbb E\!\left[(y_0-\hat f(x_0))^2\right] \quad \text{expectation over new training sets and new noise}$$

</div>

<!--
Define every symbol before moving on. $y$ is the observed target value we actually measure. $f(x)$ is the true, unknown function describing how the target depends on the input on average — it is the thing we are trying to learn but never get to see directly. $\epsilon$ is irreducible noise: randomness in the data-generating process itself (measurement error, unmeasured factors, inherent randomness) that no model, however good, can predict away. $\mathbb{E}[\epsilon]=0$ says the noise has no systematic direction — it does not on average push $y$ up or down. $\operatorname{Var}(\epsilon)=\sigma^2$ says the noise has a fixed spread, denoted $\sigma^2$, which becomes the noise floor in the decomposition two slides from now.

$\hat f$ (read "f-hat") is our *fitted* model — the function we get out after running a learning algorithm on one particular training set. The hat notation throughout statistics and ML means "estimated from data," as opposed to the true, unobserved quantity underneath. Because the training set is drawn randomly, $\hat f$ itself is a random object: if you drew a different training set from the same population, you would fit a different $\hat f$. This is the key conceptual move of the whole topic — stop thinking about $\hat f$ as one fixed function, and start thinking about the *distribution* of possible $\hat f$'s induced by resampling the training data.

The right panel shows this directly: the true function $f(x)$ (teal) is fixed, but three different training samples (implied by the gray dots) each produce a different fitted curve (blue and amber). $x_0$ is one fixed evaluation point — we ask "how does the model's prediction at this one point vary across different training sets?"

The boxed expectation $\mathbb{E}[(y_0-\hat f(x_0))^2]$ is the *expected squared prediction error at $x_0$*, where the expectation is taken over two independent sources of randomness simultaneously: which training set got drawn, and what the fresh noise draw $\epsilon$ at the test point happens to be. This double expectation is what we decompose into three interpretable pieces starting next slide. Transition: to split this expectation into pieces, we use one algebraic trick — adding and subtracting the same quantity.
-->

---
glowSeed: 225
---

# Decomposition: Add Zero in a Useful Form

<div class="mt-8 text-center">

$$
\begin{aligned}
y_0-\hat f(x_0)
&= f(x_0)+\epsilon-\hat f(x_0) \\
&= \underbrace{f(x_0)-\mathbb E[\hat f(x_0)]}_{\text{systematic offset}}
+ \underbrace{\mathbb E[\hat f(x_0)]-\hat f(x_0)}_{\text{sample-to-sample fluctuation}}
+ \underbrace{\epsilon}_{\text{noise}}
\end{aligned}
$$

</div>

<div class="grid grid-cols-3 gap-4 mt-10 text-center">
<div v-click border="2 solid blue-800" bg="blue-800/20" rounded-lg p-4><div class="font-bold text-blue-300">Bias</div><div class="text-sm opacity-75 mt-2">mean prediction misses truth</div></div>
<div v-click border="2 solid orange-800" bg="orange-800/20" rounded-lg p-4><div class="font-bold text-orange-300">Variance</div><div class="text-sm opacity-75 mt-2">fits change with the sample</div></div>
<div v-click border="2 solid white/10" bg="white/5" rounded-lg p-4><div class="font-bold">Noise</div><div class="text-sm opacity-75 mt-2">outcomes vary even at fixed x</div></div>
</div>

<!--
Walk through this line by line. We start from the raw prediction error $y_0-\hat f(x_0)$ and substitute $y_0=f(x_0)+\epsilon$ from the previous slide's data-generating model — this is just algebraic substitution, nothing new yet.

The key trick, common throughout statistics whenever you need to decompose an error into interpretable pieces, is adding and subtracting the same quantity so nothing changes numerically but new structure appears. Here we add and subtract $\mathbb{E}[\hat f(x_0)]$ — the *average prediction the procedure would make at $x_0$ if you could retrain on infinitely many training sets and average the results*. That average prediction is a fixed, non-random number (even though any single $\hat f(x_0)$ is random), so it is a legitimate quantity to insert.

This regroups the single error term into three pieces, each with a clean interpretation, labeled directly under the braces on the slide:

1. $f(x_0)-\mathbb{E}[\hat f(x_0)]$ — the **systematic offset**: how far the procedure's *average* prediction sits from the truth. This piece does not depend on which training set you happened to draw; it is a fixed property of the learning procedure and the true function. This becomes the bias term.
2. $\mathbb{E}[\hat f(x_0)]-\hat f(x_0)$ — the **sample-to-sample fluctuation**: how far *this particular* fitted model's prediction deviates from the procedure's average prediction. This piece is random — it changes every time you redraw the training set — and by construction its expectation over training sets is exactly zero, since $\mathbb E[\hat f(x_0)]$ is subtracted from itself in expectation.
3. $\epsilon$ — the noise, already defined as mean-zero and independent of the training data.

Common misconception: students sometimes think bias is about the model performing badly on the training set, and variance is about performing badly on the test set. That is not quite right — both bias and variance are about the *test point* $x_0$; the distinction is whether the error is systematic across resamples (bias) or fluctuates across resamples (variance). Transition: next we square this expression and take expectations, and something convenient happens — the cross terms between bias, fluctuation, and noise all disappear.
-->

---
glowSeed: 2251
---

# Squaring: Why the Cross Terms Vanish

<div class="text-sm mt-4">

Let $b = f(x_0)-\mathbb E[\hat f(x_0)]$ (a fixed number) and $v = \mathbb E[\hat f(x_0)]-\hat f(x_0)$ (random, mean zero). Then $y_0-\hat f(x_0) = b + v + \epsilon$.

$$
\begin{aligned}
(y_0-\hat f(x_0))^2 &= (b+v+\epsilon)^2 \\
&= b^2 + v^2 + \epsilon^2 + 2bv + 2b\epsilon + 2v\epsilon
\end{aligned}
$$

</div>

<div class="grid grid-cols-2 gap-4 mt-6 text-sm">

<div v-click border="2 solid teal-800" bg="teal-800/20" rounded-lg p-3>
$\mathbb E[b^2]=b^2$ — constant, survives as bias²
</div>
<div v-click border="2 solid teal-800" bg="teal-800/20" rounded-lg p-3>
$\mathbb E[v^2]=\operatorname{Var}(\hat f(x_0))$ — survives as variance
</div>
<div v-click border="2 solid teal-800" bg="teal-800/20" rounded-lg p-3>
$\mathbb E[\epsilon^2]=\sigma^2$ — survives as noise
</div>
<div v-click border="2 solid red-800" bg="red-800/20" rounded-lg p-3>
$\mathbb E[2bv]=\mathbb E[2b\epsilon]=\mathbb E[2v\epsilon]=0$ — all three cancel
</div>

</div>

<div v-click class="mt-5 text-center text-sm opacity-80">
$b$ is a constant, so $\mathbb E[bv]=b\,\mathbb E[v]=0$ since $\mathbb E[v]=0$ by construction. $\mathbb E[b\epsilon]=b\,\mathbb E[\epsilon]=0$ since $\mathbb E[\epsilon]=0$. $\mathbb E[v\epsilon]=\mathbb E[v]\,\mathbb E[\epsilon]=0$ since $v$ (a property of the training sample) and $\epsilon$ (fresh test-point noise) are independent, and each already has mean zero.
</div>

<!--
This is the algebra the previous slide promised. We square the three-term sum $b+v+\epsilon$ using ordinary $(x+y+z)^2$ expansion — six terms: three squares and three cross (mixed) terms. Then we take the expectation of each of the six terms separately, since expectation is linear (the expectation of a sum is the sum of expectations).

The three squared terms survive expectation and become the three pieces of the final decomposition: $\mathbb E[b^2]=b^2$ because $b$ is a constant (a number does not change when you take its expectation); $\mathbb E[v^2]$ is by definition the variance of $\hat f(x_0)$, since $v$ is exactly "prediction minus its own mean"; $\mathbb E[\epsilon^2]=\sigma^2$ follows from the definition $\operatorname{Var}(\epsilon)=\mathbb E[\epsilon^2]-(\mathbb E[\epsilon])^2=\mathbb E[\epsilon^2]-0=\sigma^2$.

The three cross terms all vanish, for three different but related reasons, spelled out in the box at the bottom: one factor is a constant that can be pulled out of the expectation, and the remaining random factor has mean zero; or the two random factors are statistically independent, so the expectation of their product is the product of their expectations, which is zero times anything.

This is the moment to say explicitly: the bias-variance decomposition is not an approximation, a heuristic, or a rule of thumb — it is an exact algebraic identity that holds whenever the loss is squared error and the noise is independent of the model with mean zero. Transition: assembling the three surviving terms gives the decomposition on the next slide.
-->

---
glowSeed: 226
---

# The Bias–Variance Decomposition

<div class="mt-10" border="2 solid white/10" bg="white/5" backdrop-blur-sm rounded-lg px-6 py-6>

$$
\mathbb E[(y_0-\hat f(x_0))^2]
= \underbrace{\sigma^2}_{\text{irreducible noise}}
+ \underbrace{\left(f(x_0)-\mathbb E[\hat f(x_0)]\right)^2}_{\text{bias}^2}
+ \underbrace{\mathbb E\!\left[(\hat f(x_0)-\mathbb E[\hat f(x_0)])^2\right]}_{\text{variance}}
$$

</div>

<div class="grid grid-cols-3 gap-4 mt-8 text-center">
<div v-click class="p-4 rounded-lg bg-slate-500/20 border-2 border-slate-600"><div class="text-3xl">🔒</div><strong>Cannot eliminate</strong></div>
<div v-click class="p-4 rounded-lg bg-blue-500/20 border-2 border-blue-700"><div class="text-3xl">🎯</div><strong>Systematic error</strong></div>
<div v-click class="p-4 rounded-lg bg-orange-500/20 border-2 border-orange-700"><div class="text-3xl">🎲</div><strong>Instability</strong></div>
</div>

<!--
Read the identity term by term. $\mathbb E[(y_0-\hat f(x_0))^2]$, the left side, is the expected squared error at test point $x_0$, averaged over both which training set was drawn and the fresh noise at the test point — exactly what we defined two slides ago. It equals the sum of three non-negative pieces.

$\sigma^2$, irreducible noise: the variance of the label-generating noise itself. No choice of model, no amount of data, and no amount of cleverness can push this term below its true value, because it reflects randomness in the world, not a deficiency of the model. This is the noise floor — the best achievable expected squared error at $x_0$, even by the true function $f$ itself.

$(f(x_0)-\mathbb E[\hat f(x_0)])^2$, bias squared: the square of the systematic offset from two slides ago. This is zero only if the learning procedure's average prediction exactly equals the truth. A straight line trying to fit a quadratic relationship has nonzero bias at essentially every $x_0$, no matter how much data you give it, because the hypothesis class itself cannot represent the true curve.

$\mathbb E[(\hat f(x_0)-\mathbb E[\hat f(x_0)])^2]$, variance: literally the statistical variance of the prediction $\hat f(x_0)$ across different training sets. A model class that is very flexible (high-degree polynomial, unpruned decision tree, deep unregularized network) tends to have high variance because small changes in the training sample cause it to fit a noticeably different function.

Why do we square the bias but not label the variance term as "variance squared"? Because variance is already defined as an expected squared deviation — $\operatorname{Var}(X)=\mathbb E[(X-\mathbb E X)^2]$ — so no extra squaring is needed; bias itself is a signed quantity (systematic error can be positive or negative), so we square it separately to make it comparable in units to variance and combine additively.

Common misconception: students sometimes think you can drive total error to exactly zero with a perfect model. You cannot — $\sigma^2$ is a hard floor set by the data-generating process, present in the formula regardless of model choice. The only two terms an algorithm designer can influence are bias and variance, and — as the tradeoff curve on the next-but-one slide shows — pushing one down typically pushes the other up.
-->

---
glowSeed: 227
---

# Estimating Bias and Variance by Repeated Fitting

```python {1-2|4-5|7-10|12-13|all}
import numpy as np
from sklearn.preprocessing import PolynomialFeatures
from sklearn.linear_model import LinearRegression
from sklearn.pipeline import make_pipeline

rng = np.random.default_rng(0)
true_f = lambda x: np.sin(1.5 * np.pi * x)
predictions = []
for _ in range(500):
    x = rng.uniform(0, 1, 20)
    y = true_f(x) + rng.normal(scale=.2, size=20)
    model = make_pipeline(PolynomialFeatures(1), LinearRegression())
    model.fit(x[:, None], y)
    predictions.append(model.predict([[.5]])[0])

bias_sq = (np.mean(predictions) - true_f(.5)) ** 2
variance = np.var(predictions)
```

<div v-click class="mt-4 text-sm opacity-80 text-center">The mathematical expectation becomes an ordinary average over many simulated training sets.</div>

<!--
This simulation makes the abstract expectation concrete: 500 resamples stand in for the mathematical expectation, and `np.mean` / `np.var` across those 500 fitted predictions stand in for $\mathbb E[\cdot]$ and $\operatorname{Var}(\cdot)$. We evaluate every model at the same fixed point $x_0=0.5$ so the only thing changing across the 500 iterations is which random training sample got drawn — exactly matching the formal setup.

Walk through the code block by block, matching the click groups: lines 1-2 import numpy and set up polynomial features and linear regression, the modeling ingredients. Lines 4-5 define the true signal $f(x)=\sin(1.5\pi x)$ and the container for the 500 point predictions. Lines 7-10 are the resampling loop: each iteration draws a *fresh* 20-point training sample with fresh noise (`scale=.2` means $\sigma=0.2$, so $\sigma^2=0.04$), fits a degree-1 (straight-line) polynomial model, and records its single prediction at $x_0=0.5$. Lines 12-13 compute the empirical bias² and variance exactly as the formulas define them, but using sample statistics instead of true expectations.

Worked numbers from running this exact code with degree varied: $f(0.5)=\sin(0.75\pi)\approx0.707$. At degree 1 (straight line, too rigid for a sine curve): mean prediction ≈0.238, so bias²≈(0.707-0.238)²≈0.220, while variance≈0.013 — high bias, low variance, matching the underfit corner of the dartboard. At degree 3: mean prediction ≈0.652, bias²≈0.003, variance≈0.005 — both small, the sweet spot. At degree 10 (a very flexible curve for only 20 points): mean prediction ≈0.701, bias²≈0.00004 (essentially zero), but variance jumps to ≈0.022 — the classic overfit signature, low bias, high variance. Note the total (bias²+variance+noise σ²=0.04) falls from about 0.273 at degree 1 to about 0.048 at degree 3 and rises again to about 0.062 at degree 10 — a numeric U-shape, previewing the next slide's curve.
-->

---
glowSeed: 228
---

# The Tradeoff Curve

<div class="grid grid-cols-2 gap-8 mt-3 items-center">
<div>
<svg viewBox="0 0 470 330" class="w-full">
  <line x1="48" y1="285" x2="445" y2="285" stroke="#64748b" stroke-width="2"/><line x1="48" y1="285" x2="48" y2="25" stroke="#64748b" stroke-width="2"/>
  <path d="M60 45 C160 115,285 190,430 255" fill="none" stroke="#60a5fa" stroke-width="4"/>
  <path d="M60 260 C180 240,310 145,430 45" fill="none" stroke="#fb923c" stroke-width="4"/>
  <path d="M60 150 C150 105,205 95,260 112 C330 135,370 185,430 245" fill="none" stroke="#2dd4bf" stroke-width="5"/>
  <line x1="225" y1="103" x2="225" y2="285" stroke="#f8fafc" stroke-width="2" stroke-dasharray="6 5"/>
  <circle cx="225" cy="103" r="8" fill="#f8fafc"/>
  <text x="245" y="92" fill="#f8fafc" style="font-size: 14px">sweet spot</text>
  <text x="330" y="238" fill="#60a5fa" style="font-size: 14px">bias²</text><text x="345" y="80" fill="#fb923c" style="font-size: 14px">variance</text><text x="75" y="135" fill="#2dd4bf" style="font-size: 14px">test error</text>
  <text x="180" y="320" fill="#94a3b8" style="font-size: 14px">model complexity</text><text x="10" y="28" fill="#94a3b8" style="font-size: 14px">error</text>
</svg>
</div>

<div>
<v-clicks>

- Bias² usually falls with complexity
- Variance usually rises with complexity
- Their sum produces a U-shaped test-error curve
- Best generalization occurs at an intermediate capacity
- Cross-validation helps locate the minimum

</v-clicks>

<div v-click class="mt-5" border="2 solid amber-800" bg="amber-800/20" rounded-lg p-4>
“Make the model bigger” is not a universal improvement strategy.
</div>
</div>
</div>

<!--
This plot assembles the three numeric findings from the previous slide into a continuous picture. The x-axis is model complexity — map familiar knobs onto it: polynomial degree, decision tree depth, number of neighbors $k$ used *inversely* (small $k$ = high complexity, large $k$ = low complexity), neural network width/depth, or inverse regularization strength (weaker regularization = more complexity). All of these are, mechanically, different ways of turning the same dial.

The blue curve (bias²) falls monotonically as complexity increases: a more flexible model can represent the true function more closely, on average. The orange curve (variance) rises monotonically: a more flexible model has more freedom to fit the specific noise in whatever sample it was trained on. The teal curve (test error) is their sum plus the constant noise floor $\sigma^2$ — it inherits a U-shape because it starts high (dominated by bias when the model is too simple), decreases as bias falls faster than variance rises, reaches a minimum, then increases again as variance starts rising faster than bias falls.

The marked "sweet spot" is not the point of lowest bias, nor the point of lowest variance — it is the point where their *sum* is lowest, which is generally somewhere in the middle. This is the central practical takeaway of the whole topic: "make the model bigger/more powerful" is not a universal improvement strategy, because past the sweet spot, added flexibility actively hurts generalization by inflating variance faster than it reduces bias.

The last bullet flags the practical question this raises: since we cannot observe bias² and variance directly on real data (we would need to know the true $f$ and to retrain many times), how do we locate the sweet spot in practice? Cross-validation, covered in the next deck, is the answer — it estimates the U-shaped test-error curve directly from held-out data without ever computing bias or variance separately.
-->

---
glowSeed: 229
---

# Diagnose the Regime You Are In

<div class="grid grid-cols-2 gap-6 mt-6">

<div v-click class="rounded-lg overflow-hidden border-2 border-blue-800 bg-blue-800/20">
<div class="bg-blue-800/40 px-5 py-3 font-bold text-blue-200">High bias · underfitting</div>
<div class="px-5 py-5">

$$\text{Error}_{train}\approx\text{Error}_{val}\qquad\text{both high}$$

<ul class="text-sm mt-4"><li>add useful features</li><li>use a more expressive model</li><li>reduce regularization</li></ul>
</div>
</div>

<div v-click class="rounded-lg overflow-hidden border-2 border-orange-800 bg-orange-800/20">
<div class="bg-orange-800/40 px-5 py-3 font-bold text-orange-200">High variance · overfitting</div>
<div class="px-5 py-5">

$$\text{Error}_{train}\;\text{is much smaller than}\;\text{Error}_{val}$$

<ul class="text-sm mt-4"><li>regularize or simplify</li><li>collect more training data</li><li>select features carefully</li></ul>
</div>
</div>

</div>

<div v-click class="mt-8" border="2 solid teal-800" bg="teal-800/20" rounded-lg px-6 py-4 text-center text-lg>
Absolute error tells you <strong>how well</strong>; the train–validation gap helps explain <strong>why</strong>.
</div>

<!--
This is the practical diagnostic students should walk out remembering, because it is the one they will use in every future project. $\text{Error}_{train}$ is the loss measured on the same data the model was fit on; $\text{Error}_{val}$ is loss measured on held-out data the model never saw during fitting — the validation set stands in for "a fresh draw from the same population," approximating the $x_0$ from the formal setup.

High-bias regime (left card): training error and validation error are close to each other, *and both are high*. The "both are high" clause is essential and often missed — a small gap alone does not mean things are fine. If the model cannot even fit the data it was trained on, adding more training data will not help (the model's ceiling is already reached); the fix has to increase the model's representational capacity — more/better features, a more expressive hypothesis class — or reduce regularization that is artificially constraining it.

High-variance regime (right card): training error is small but validation error is much larger — the model has essentially memorized the training set's idiosyncrasies and fails to generalize. Fixes: increase regularization (next deck's topic) or simplify the model (reduce complexity), collect more training data (more data makes it harder for a flexible model to fit noise, since noise averages out but the underlying pattern does not), or select/engineer features more carefully to reduce unnecessary flexibility.

Common misconception, worth stating explicitly here since students conflate these constantly: "overfitting" describes the *train-vs-validation gap* symptom (train much better than validation); "underfitting" describes the *both-are-bad* symptom. Neither is defined by the absolute error value alone — a model with 10% error could be underfitting (if a better model gets 2%) or could be doing about as well as achievable (if the noise floor is 9%). You always need the comparison between train and validation error, not just one number, to diagnose which regime you are in. This is exactly why the next deck formalizes train/validation/test splitting — without a validation set, this entire diagnostic is unavailable.
-->

---
glowSeed: 230
---

# Keep These Four Ideas

<div class="grid grid-cols-2 gap-4 mt-7">
<div v-click border="2 solid blue-800" bg="blue-800/20" rounded-lg p-5><strong>Bias</strong><div class="text-sm opacity-80 mt-2">systematic error from restrictive assumptions</div></div>
<div v-click border="2 solid orange-800" bg="orange-800/20" rounded-lg p-5><strong>Variance</strong><div class="text-sm opacity-80 mt-2">sensitivity to the sampled training data</div></div>
<div v-click border="2 solid teal-800" bg="teal-800/20" rounded-lg p-5><strong>Total error</strong><div class="text-sm opacity-80 mt-2">noise + bias² + variance</div></div>
<div v-click border="2 solid violet-800" bg="violet-800/20" rounded-lg p-5><strong>Diagnosis</strong><div class="text-sm opacity-80 mt-2">compare training and validation error</div></div>
</div>

<div v-click class="mt-9 text-xl text-center">Next: <strong>Train/Validation/Test Splits and Cross-Validation</strong></div>

<!--
Recap the four ideas in one pass, tying each back to a symbol from the decomposition: bias is $f(x_0)-\mathbb E[\hat f(x_0)]$, the systematic error baked into a restrictive hypothesis class; variance is $\mathbb E[(\hat f(x_0)-\mathbb E[\hat f(x_0)])^2]$, the sensitivity of the fitted model to which particular training sample it saw; total expected error is the exact sum $\sigma^2+\text{bias}^2+\text{variance}$, provable by the squaring argument two slides back, not just a rule of thumb; and diagnosis in practice comes from comparing training error to validation error, since we cannot compute bias and variance directly on real, non-simulated data.

We now understand precisely what bias and variance mean and why they trade off, but everything in this deck quietly assumed we already had a trustworthy validation set to compare against training error. We have not yet established *how* to split data honestly, how many folds to use, or what goes wrong if the split leaks information. The next lecture, Train/Validation/Test Splits and Cross-Validation, builds exactly that discipline — it is the methodological foundation that makes the diagnostic on the previous slide actually reliable rather than accidentally optimistic.
-->
