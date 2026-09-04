---
theme: default
highlighter: shiki
css: unocss
colorSchema: dark
title: 'Introduction to Gradient Descent'
info: |
  ## Introduction to Gradient Descent
  From "what to minimize" to how we actually minimize it.
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
glowSeed: 330
---

# Introduction to Gradient Descent

### From “what to minimize” to *how* to minimize it

<div class="pt-6 opacity-80 text-lg">Topic 6 of Core ML Concepts</div>

<div class="mt-10 flex items-center justify-center gap-6">
<div class="rounded-xl border-2 border-blue-800 bg-blue-800/20 px-7 py-4 text-2xl">

$\displaystyle \arg\min_\theta\;\hat R(\theta)$

</div>
<div class="text-3xl opacity-60">→</div>
<div class="rounded-xl border-2 border-teal-800 bg-teal-800/20 px-7 py-4 text-2xl">

$\displaystyle \theta \leftarrow \theta - \eta\,\nabla_\theta \ell(\theta)$

</div>
</div>

<div class="mt-8 text-sm opacity-70">The algorithm behind nearly every model in this course</div>

<!--
Open by directly bridging from the last lecture: we spent a whole lecture being careful about what "loss" and "empirical risk" mean, and arrived at $\arg\min_\theta \hat R(\theta)$ — but never actually said how to *do* the minimizing. Today's lecture is that missing piece, and it's the piece that turns every loss function from the previous lecture into something a computer can actually run.

Roadmap for the hour: what a gradient is, the update rule itself, then derive it concretely for MSE, MAE, and logistic loss.

Tell students this is the last purely conceptual lecture of the unit — starting next lecture (Regression), everything from here on is applying this exact algorithm to real models.

Visual to hold in mind for the whole lecture: a 3D bowl-shaped loss surface with a small ball rolling down toward the minimum, leaving dotted footprints rather than a smooth trail — the path is a sequence of discrete steps, not a continuous slide. That discreteness is the whole algorithm.
-->

---
glowSeed: 331
---

# The Gradient — Direction of Steepest Change

<div class="grid grid-cols-2 gap-7 mt-2 items-center">
<div>
<svg viewBox="0 0 420 320" class="w-full" role="img" aria-label="Contour plot of a two-parameter loss surface with elliptical rings around a minimum. An arrow at a point on an outer ring points outward and uphill, labelled as the gradient; a second arrow at the same point points inward and downhill, labelled as the direction we actually move.">
  <defs>
    <marker id="gdArrowUp" viewBox="0 0 10 10" refX="9" refY="5" markerWidth="6" markerHeight="6" orient="auto-start-reverse"><path d="M0 0 L10 5 L0 10 z" fill="#fb923c"/></marker>
    <marker id="gdArrowDown" viewBox="0 0 10 10" refX="9" refY="5" markerWidth="6" markerHeight="6" orient="auto-start-reverse"><path d="M0 0 L10 5 L0 10 z" fill="#2dd4bf"/></marker>
  </defs>
  <ellipse cx="210" cy="165" rx="160" ry="112" fill="none" stroke="#3b82f6" stroke-width="2" opacity=".35"/>
  <ellipse cx="210" cy="165" rx="120" ry="84" fill="none" stroke="#3b82f6" stroke-width="2" opacity=".5"/>
  <ellipse cx="210" cy="165" rx="80" ry="56" fill="none" stroke="#3b82f6" stroke-width="2" opacity=".65"/>
  <ellipse cx="210" cy="165" rx="40" ry="28" fill="none" stroke="#3b82f6" stroke-width="2" opacity=".8"/>
  <circle cx="210" cy="165" r="5" fill="#93c5fd"/>
  <text x="196" y="150" fill="#93c5fd" style="font-size: 14px">min</text>
  <line x1="302" y1="111" x2="347" y2="57" stroke="#fb923c" stroke-width="3.5" marker-end="url(#gdArrowUp)"/>
  <line x1="302" y1="111" x2="257" y2="165" stroke="#2dd4bf" stroke-width="3.5" marker-end="url(#gdArrowDown)"/>
  <circle cx="302" cy="111" r="6" fill="#f8fafc"/>
  <text x="320" y="42" fill="#fdba74" style="font-size: 15px">∇L(θ) · uphill</text>
  <text x="60" y="205" fill="#5eead4" style="font-size: 15px">−∇L(θ) · the direction</text>
  <text x="60" y="224" fill="#5eead4" style="font-size: 15px">we actually move</text>
  <text x="140" y="308" fill="#94a3b8" style="font-size: 14px">contours of L(θ₁, θ₂)</text>
</svg>
</div>

<div>
<div border="2 solid white/10" bg="white/5" rounded-lg p-4>

$$\nabla_\theta \ell(\theta) = \left[\frac{\partial \ell}{\partial \theta_1},\ \frac{\partial \ell}{\partial \theta_2},\ \dots,\ \frac{\partial \ell}{\partial \theta_k}\right]^{\!\top}$$

</div>

<div class="mt-4 space-y-3">
<div v-click border="2 solid blue-800" bg="blue-800/20" rounded-lg p-3 text-sm>
One partial derivative per parameter, collected into a single vector — loss as a function of θ = (θ₁, …, θ<sub>k</sub>).
</div>
<div v-click border="2 solid orange-800" bg="orange-800/20" rounded-lg p-3 text-sm>
The gradient points in the direction of steepest <strong>increase</strong> at that point.
</div>
<div v-click border="2 solid teal-800" bg="teal-800/20" rounded-lg p-3 text-sm>
So its negative decreases the loss fastest, locally. That single fact is the whole algorithm.
</div>
</div>
</div>
</div>

<div v-click class="mt-4 text-center text-sm opacity-75">This is the calculus lecture from Unit 1 (Mathematical Foundations) put directly to work.</div>

<!--
Keep this slide grounded in the multivariable calculus students already saw in Unit 1 — the gradient is nothing new mathematically, just a vector of partial derivatives, one per parameter. Each entry answers a narrow question: "if I nudge *this one* parameter up slightly and hold all the others fixed, does the loss go up or down, and how fast?"

The contour plot is worth lingering on. Point out that the gradient at any point is always perpendicular to the contour line through that point. That is exactly why it is the direction of steepest ascent rather than some arbitrary uphill direction: moving *along* a contour changes the loss not at all, so all of the change must be in the perpendicular direction.

The orange arrow is $\nabla_\theta\ell$, pointing outward toward higher contours. The teal arrow is $-\nabla_\theta\ell$, pointing inward toward the minimum — that is the direction gradient descent will step in.

Everything in the rest of the lecture is a single exercise repeated three times: "compute this vector for a specific loss function."
-->

---
glowSeed: 332
---

# One Parameter: the Gradient Is Just the Slope

<div class="text-center text-sm opacity-80 mb-1">One parameter ⇒ the gradient is a single number, the slope. Positive slope ⇒ decrease θ.</div>

<div class="max-w-[780px] mx-auto">
<svg viewBox="0 14 900 456" class="w-full" role="img" aria-label="A loss curve L of theta plotted against theta, bowl shaped with its minimum marked theta star. A point theta t sits on the right arm of the bowl with a dashed line dropping to the axis. The tangent line at that point is drawn, with an arrow pointing up and to the right along it labelled gradient greater than zero. A separate arrow on the theta axis points left, labelled step theta becomes theta minus eta times the gradient.">
  <defs>
    <marker id="gdTanArrow" viewBox="0 0 10 10" refX="9" refY="5" markerWidth="6" markerHeight="6" orient="auto-start-reverse"><path d="M0 0 L10 5 L0 10 z" fill="#fb923c"/></marker>
    <marker id="gdStepArrow" viewBox="0 0 10 10" refX="9" refY="5" markerWidth="7" markerHeight="7" orient="auto-start-reverse"><path d="M0 0 L10 5 L0 10 z" fill="#2dd4bf"/></marker>
  </defs>

  <line x1="80" y1="420" x2="878" y2="420" stroke="#64748b" stroke-width="2"/>
  <line x1="80" y1="30" x2="80" y2="424" stroke="#64748b" stroke-width="2"/>
  <text x="884" y="416" fill="#94a3b8" style="font-size: 22px">θ</text>
  <text x="26" y="36" fill="#94a3b8" style="font-size: 22px">L(θ)</text>

  <polyline points="140,60.0 160,92.8 180,123.8 200,153.1 220,180.6 240,206.3 260,230.2 280,252.4 300,272.7 320,291.4 340,308.2 360,323.3 380,336.6 400,348.1 420,357.8 440,365.8 460,372.0 480,376.5 500,379.1 520,380.0 540,379.1 560,376.5 580,372.0 600,365.8 620,357.8 640,348.1 660,336.6 680,323.3 700,308.2 720,291.4 740,272.7 760,252.4 780,230.2 800,206.3 820,180.6 840,153.1 860,123.8"
    fill="none" stroke="#60a5fa" stroke-width="4" stroke-linejoin="round" stroke-linecap="round"/>

  <circle cx="520" cy="380" r="6" fill="#93c5fd" opacity=".75"/>
  <line x1="520" y1="386" x2="520" y2="420" stroke="#93c5fd" stroke-width="1.5" stroke-dasharray="4 4" opacity=".6"/>
  <text x="508" y="446" fill="#93c5fd" style="font-size: 19px" opacity=".85">θ*</text>

  <line x1="760" y1="252" x2="760" y2="420" stroke="#f8fafc" stroke-width="1.5" stroke-dasharray="5 5" opacity=".55"/>
  <circle cx="760" cy="252" r="8" fill="#f8fafc"/>
  <text x="748" y="446" fill="#f8fafc" style="font-size: 19px">θₜ</text>

  <g v-click>
    <line x1="660" y1="359" x2="862" y2="144" stroke="#fbbf24" stroke-width="2.5" stroke-dasharray="7 5" opacity=".8"/>
    <text x="596" y="300" fill="#fbbf24" style="font-size: 17px">tangent at θₜ</text>
  </g>

  <g v-click>
    <line x1="766" y1="246" x2="848" y2="159" stroke="#fb923c" stroke-width="4.5" marker-end="url(#gdTanArrow)"/>
    <text x="556" y="180" fill="#fdba74" style="font-size: 20px">∇L(θₜ) &gt; 0 · uphill</text>
  </g>

  <g v-click>
    <line x1="756" y1="458" x2="618" y2="458" stroke="#2dd4bf" stroke-width="4.5" marker-end="url(#gdStepArrow)"/>
    <text x="600" y="465" fill="#5eead4" style="font-size: 19px" text-anchor="end">step: θ ← θ − η∇L(θ)</text>
  </g>
</svg>
</div>

<div class="text-center text-sm opacity-80 mt-1">Same rule runs per-coordinate when θ is a vector.</div>

<!--
This is the one-dimensional companion to the previous slide. Contour plots are the honest picture for two parameters, but they hide the thing students most need to see: the *sign* bookkeeping. With a single parameter there is no vector at all — the gradient is one number, the slope of the tangent line.

Walk the picture left to right. The blue curve is the loss as a function of a single parameter θ. The faint point at the bottom is $\theta^*$, the minimizer we are trying to reach. The white point is $\theta_t$, wherever the algorithm currently sits — here, to the right of the minimum.

Click through the stages. First the tangent: the amber dashed line touching the curve at $\theta_t$. Its slope *is* $\nabla L(\theta_t)$. Second, the orange arrow along that tangent: the slope is positive, so the gradient points up and to the right — increasing θ from here would increase the loss. Third, the teal arrow on the axis: because the update subtracts $\eta\nabla L$, and $\nabla L>0$, the new θ moves *left* — toward the minimum. The minus sign in the update rule is doing exactly one job, and this is it.

Ask the class the mirror question before moving on: if $\theta_t$ had landed on the *left* arm of the bowl, the slope would be negative, $-\eta\nabla L$ would be positive, and the step would move right. Either way the step heads downhill. That is the whole guarantee, and it is local — nothing here promises the step is not too large, which is the learning-rate discussion two slides from now.

Finally, connect back: for a vector θ this exact reasoning runs independently in every coordinate, which is precisely what "the gradient is the vector of partial derivatives" means.
-->

---
glowSeed: 333
---

# The Gradient Descent Update Rule

<div border="2 solid teal-800" bg="teal-800/20" rounded-lg px-6 py-4 text-center text-2xl>

$$\theta^{(t+1)} = \theta^{(t)} - \eta\,\nabla_\theta \ell\big(\theta^{(t)}\big)$$

</div>

<div class="grid grid-cols-2 gap-7 mt-5 items-center">
<div class="space-y-3">
<div v-click border="2 solid blue-800" bg="blue-800/20" rounded-lg p-3 text-sm>
<strong>Initialize.</strong> Start from some θ₀ — often random, often just zeros.
</div>
<div v-click border="2 solid teal-800" bg="teal-800/20" rounded-lg p-3 text-sm>
<strong>Step.</strong> Repeatedly move in the negative gradient direction.
</div>
<div v-click border="2 solid amber-800" bg="amber-800/20" rounded-lg p-3 text-sm>
<strong>Learning rate η.</strong> Controls step size. A <em>hyperparameter</em> chosen by the practitioner, not learned from data.
</div>
<div v-click border="2 solid violet-800" bg="violet-800/20" rounded-lg p-3 text-sm>
<strong>Stop.</strong> When the loss stops decreasing meaningfully, or after a fixed number of iterations.
</div>
</div>

<div>
<svg viewBox="0 0 420 300" class="w-full" role="img" aria-label="Contour rings of a loss surface seen from above, with a dotted zig-zag path of discrete steps starting near the outer ring and converging on the central minimum, each step shorter than the last.">
  <ellipse cx="210" cy="155" rx="175" ry="120" fill="none" stroke="#3b82f6" stroke-width="2" opacity=".3"/>
  <ellipse cx="210" cy="155" rx="130" ry="89" fill="none" stroke="#3b82f6" stroke-width="2" opacity=".45"/>
  <ellipse cx="210" cy="155" rx="86" ry="59" fill="none" stroke="#3b82f6" stroke-width="2" opacity=".6"/>
  <ellipse cx="210" cy="155" rx="42" ry="29" fill="none" stroke="#3b82f6" stroke-width="2" opacity=".75"/>
  <polyline points="55,45 300,95 120,132 268,150 176,158 230,157 205,155" fill="none" stroke="#2dd4bf" stroke-width="3" stroke-dasharray="6 5" stroke-linejoin="round"/>
  <g fill="#5eead4"><circle cx="55" cy="45" r="6"/><circle cx="300" cy="95" r="5.5"/><circle cx="120" cy="132" r="5"/><circle cx="268" cy="150" r="4.5"/><circle cx="176" cy="158" r="4"/><circle cx="230" cy="157" r="3.5"/></g>
  <circle cx="210" cy="155" r="6" fill="#f8fafc"/>
  <text x="20" y="30" fill="#5eead4" style="font-size: 14px">θ₀</text>
  <text x="222" y="140" fill="#f8fafc" style="font-size: 14px">θ*</text>
  <text x="118" y="292" fill="#94a3b8" style="font-size: 14px">steps shrink as the gradient shrinks</text>
</svg>
</div>
</div>

<!--
Emphasize that this update rule is the single most-used line of math in all of machine learning — nearly every model trained in this course, and the vast majority of models trained in industry, boil down to running some variant of this loop.

Read the equation aloud as an instruction rather than an identity: "the new parameters are the old parameters, minus a small multiple of the gradient at the old parameters." The superscript $(t)$ is an iteration counter, not an exponent — worth saying explicitly, because students confuse it with a power every year.

On initialization: zeros are fine for the convex losses in this lecture; random initialization matters much more for neural networks later, where symmetric zero weights would keep every unit computing the same thing.

On the diagram: point out that the steps get shorter near the minimum *automatically*, with no change to η. That is because the gradient itself shrinks as the surface flattens out. Students often assume you have to decay the learning rate to converge; the gradient's own magnitude does much of that work for free on a well-behaved surface.

Briefly flag the learning-rate tradeoff — too small and convergence is painfully slow, too large and the steps overshoot and can diverge — but hold the detail for the dedicated slide two slides on. Tell students the Optimization in Practice unit later in the course covers learning rate schedules, momentum, and adaptive methods such as Adam; today is deliberately the minimal, clean version of the idea.
-->

---
glowSeed: 334
---

# The Loop, in Code

```python
import numpy as np

def gradient_descent(grad_fn, theta_init, lr=0.01, n_steps=1000):
    theta = theta_init.copy()
    for _ in range(n_steps):
        grad = grad_fn(theta)
        theta = theta - lr * grad
    return theta
```

<div class="grid grid-cols-2 gap-5 mt-5">
<div v-click border="2 solid teal-800" bg="teal-800/20" rounded-lg p-4 text-sm>
<div class="font-bold text-teal-300">The loop is loss-agnostic</div>
<div class="opacity-80 mt-2">
<code>grad_fn</code> is the only thing that knows which loss is being minimized. Swap it and you have a different model — the loop never changes.
</div>
</div>
<div v-click border="2 solid amber-800" bg="amber-800/20" rounded-lg p-4 text-sm>
<div class="font-bold text-amber-300">Everything else is a hyperparameter</div>
<div class="opacity-80 mt-2">
<code>lr</code> and <code>n_steps</code> are chosen, not fitted. No amount of training data will tell you what they should be.
</div>
</div>
</div>

<div v-click class="mt-5 text-center text-sm opacity-80">The rest of this lecture writes one <code>grad_fn</code> for each of three loss functions.</div>

<!--
This is the entire algorithm, in seven lines, and it is worth saying out loud that there is nothing hidden. Students often expect optimizers to be complicated; the complexity in real frameworks is all in variants and bookkeeping, not in this core.

Note the deliberate design of the signature. `grad_fn` is passed in rather than hard-coded, which makes the point the lecture is building toward structurally visible: the loop is universal, and the *only* thing that distinguishes training a linear regression from training a logistic regression is which gradient function gets handed to it.

Two implementation details worth a sentence each. First, `theta_init.copy()` — without it the function mutates the caller's array, a classic NumPy footgun students will hit in the assignment. Second, `theta = theta - lr * grad` rather than `theta -= lr * grad`: the former allocates a fresh array, which is safer here for the same aliasing reason.

The fixed `n_steps` stopping rule is the simplest possible one, and it is what we will use today. A real implementation usually also stops early when the change in loss (or the gradient norm) falls below a tolerance — mention it, but do not implement it now.

Set up the next slide: `lr=0.01` is a default, not a truth. Ask the class what they think happens if it were 0.0000001, or 10.
-->

---
glowSeed: 335
---

# Choosing the Learning Rate

<div class="text-center text-sm opacity-80 mb-2">Same loss surface, same starting point, same update rule — only η changes.</div>

<svg viewBox="0 0 840 260" class="w-full max-w-[860px] mx-auto" role="img" aria-label="Three panels showing descent on the same one dimensional bowl. With a learning rate that is too small the iterates crawl and barely leave the starting point. With a good learning rate they reach the minimum in a few steps. With a learning rate that is too large the iterates jump across the bowl and climb higher on each side.">
  <g>
    <path d="M20 40 Q130 300 240 40" fill="none" stroke="#60a5fa" stroke-width="3" opacity=".55"/>
    <polyline points="42,87 53,106 64,123 75,138" fill="none" stroke="#fbbf24" stroke-width="2.5" stroke-dasharray="5 4"/>
    <g fill="#fbbf24"><circle cx="42" cy="87" r="5"/><circle cx="53" cy="106" r="5"/><circle cx="64" cy="123" r="5"/><circle cx="75" cy="138" r="5"/></g>
    <text x="130" y="228" fill="#fbbf24" style="font-size: 17px" text-anchor="middle">η too small</text>
    <text x="130" y="250" fill="#94a3b8" style="font-size: 14px" text-anchor="middle">correct direction, glacial progress</text>
  </g>
  <g transform="translate(280,0)">
    <path d="M20 40 Q130 300 240 40" fill="none" stroke="#60a5fa" stroke-width="3" opacity=".55"/>
    <polyline points="42,87 75,138 108,165 130,170" fill="none" stroke="#2dd4bf" stroke-width="2.5" stroke-dasharray="5 4"/>
    <g fill="#2dd4bf"><circle cx="42" cy="87" r="5"/><circle cx="75" cy="138" r="5"/><circle cx="108" cy="165" r="5"/><circle cx="130" cy="170" r="6"/></g>
    <text x="130" y="228" fill="#5eead4" style="font-size: 17px" text-anchor="middle">η just right</text>
    <text x="130" y="250" fill="#94a3b8" style="font-size: 14px" text-anchor="middle">converges in a few steps</text>
  </g>
  <g transform="translate(560,0)">
    <path d="M20 40 Q130 300 240 40" fill="none" stroke="#60a5fa" stroke-width="3" opacity=".55"/>
    <polyline points="97,158 185,138 47,95 222,78" fill="none" stroke="#f87171" stroke-width="2.5" stroke-dasharray="5 4"/>
    <g fill="#f87171"><circle cx="97" cy="158" r="5"/><circle cx="185" cy="138" r="5"/><circle cx="47" cy="95" r="5"/><circle cx="222" cy="78" r="5"/></g>
    <text x="130" y="228" fill="#f87171" style="font-size: 17px" text-anchor="middle">η too large</text>
    <text x="130" y="250" fill="#94a3b8" style="font-size: 14px" text-anchor="middle">overshoots, then diverges</text>
  </g>
</svg>

<div v-click class="mt-3 mx-auto max-w-[720px]" border="2 solid white/10" bg="white/5" rounded-lg px-5 py-3 text-center text-sm>
The gradient supplies the <strong>direction</strong>; η alone decides <strong>how far</strong> to trust it. Nothing in the data picks η for you.
</div>

<!--
This slide exists because the learning rate is the first hyperparameter most students ever tune, and the failure modes are far easier to recognize as pictures than as symptoms in a log file.

Left panel: η far too small. Notice the direction is perfectly correct at every step — the algorithm is not wrong, just slow. In practice this shows up as a training loss that decreases monotonically but is nowhere near converged when the iteration budget runs out. Students usually misdiagnose this as "the model can't fit the data."

Middle panel: a well-chosen η. The steps are large where the surface is steep and shorten on their own near the bottom, exactly as on the previous slide.

Right panel: η too large. Each step lands on the far side of the valley, at a point *higher* than where it started, so the next gradient is larger still, and the iterates walk outward. The tell-tale symptom in code is a loss that increases and then becomes `nan` or `inf` within a handful of iterations. When a student reports NaN losses, an overlarge learning rate is the first thing to check.

The practical advice to give: start around 0.01 to 0.1 on standardized features, watch the loss curve for the first few dozen iterations, and multiply or divide by ten. Also note the connection to feature scaling — wildly different feature scales make the loss surface a long narrow ravine rather than a round bowl, and then no single η works well for all coordinates. That is a direct argument for `StandardScaler`, and part of why adaptive methods like Adam exist.
-->

---
glowSeed: 336
---

# Deriving the Gradient of MSE · Scalar Form

<div class="grid grid-cols-2 gap-6 mt-3">
<div>
<div border="2 solid blue-800" bg="blue-800/20" rounded-lg p-4>
<div class="text-sm font-bold text-blue-300 mb-1">Model and loss</div>

$$f_\theta(x) = x^\top\theta, \qquad \ell(\theta) = \frac{1}{n}\sum_{i=1}^n \big(y_i - x_i^\top\theta\big)^2$$

</div>

<div v-click class="mt-4 text-sm opacity-80">Differentiate with respect to one parameter θ<sub>j</sub>, using the chain rule twice: the square, then the residual.</div>
</div>

<div v-click>
<div border="2 solid teal-800" bg="teal-800/20" rounded-lg p-4>
<div class="text-sm font-bold text-teal-300 mb-1">Per-parameter partial derivative</div>

$$
\begin{aligned}
\frac{\partial \ell}{\partial \theta_j}
&= \frac{1}{n}\sum_{i=1}^n 2\big(y_i - x_i^\top\theta\big)\cdot(-x_{ij}) \\[4pt]
&= -\frac{2}{n}\sum_{i=1}^n \big(y_i - x_i^\top\theta\big)\,x_{ij}
\end{aligned}
$$

</div>
</div>
</div>

<div v-click class="mt-5 mx-auto max-w-[760px]" border="2 solid amber-800" bg="amber-800/20" rounded-lg px-5 py-3 text-center>

The step everyone drops: $\dfrac{\partial}{\partial \theta_j}\big(y_i - x_i^\top\theta\big) = -x_{ij}$ — the **minus sign** comes from the residual, not the square.

</div>

<!--
Walk through the chain rule step by step on the board rather than jumping straight to the vectorized form.

Set it up carefully. The loss is a sum over data points of a squared residual, so differentiating term by term: the outer function is $u^2$ with $u = y_i - x_i^\top\theta$, giving $2u$; the inner derivative is $\partial u/\partial\theta_j$.

That inner derivative is the step students most often get wrong. Since $x_i^\top\theta = \sum_j x_{ij}\theta_j$, the only term involving $\theta_j$ is $x_{ij}\theta_j$, whose derivative is $x_{ij}$. But it enters the residual with a minus sign, so $\partial u/\partial\theta_j = -x_{ij}$. Write that on the board separately and box it. Every sign error later in the course traces back to this line.

Two sanity checks worth stating. First, dimensional: the partial derivative is a scalar, and indeed the right-hand side is a sum of scalars. Second, directional: if the residual $y_i - x_i^\top\theta$ is positive (we under-predicted) and $x_{ij}$ is positive, the partial derivative is negative — so the update $\theta_j \leftarrow \theta_j - \eta\cdot(\text{negative})$ increases $\theta_j$, raising the prediction. Exactly what should happen.

Note also that the factor of 2 is an artifact of squaring, and many textbooks define MSE with a $\frac{1}{2n}$ out front purely to cancel it. Either convention is fine; it rescales the gradient by a constant, which the learning rate absorbs. Say this explicitly, because students will meet both conventions and assume one of them is a typo.

Next slide stacks all $k$ of these partials into a vector.
-->

---
glowSeed: 337
---

# MSE Gradient · Vectorized and in Code

<div class="grid grid-cols-2 gap-6 mt-3 items-start">
<div>
<div border="2 solid teal-800" bg="teal-800/20" rounded-lg px-4 py-3 text-center>

$$\nabla_\theta \ell(\theta) = \frac{2}{n}X^\top\big(X\theta - y\big)$$

</div>

```python
import numpy as np

def mse_grad(theta, X, y):
    n = X.shape[0]
    residual = X @ theta - y
    return (2 / n) * X.T @ residual
```

<div v-click class="mt-3 text-sm opacity-80">Note the residual is written <code>X @ theta - y</code>, which absorbs the minus sign from the scalar form.</div>
</div>

<div>
<svg viewBox="0 0 420 320" class="w-full" role="img" aria-label="A mapping between the scalar and vectorized forms of the mean squared error gradient. The sum over i corresponds to the transpose of X times a vector, the residual y minus x transpose theta corresponds to X theta minus y, and the single feature x i j corresponds to column j of X.">
  <defs>
    <marker id="gdMapArrow" viewBox="0 0 10 10" refX="9" refY="5" markerWidth="6" markerHeight="6" orient="auto-start-reverse"><path d="M0 0 L10 5 L0 10 z" fill="#94a3b8"/></marker>
  </defs>
  <text x="66" y="28" fill="#93c5fd" style="font-size: 16px" text-anchor="middle">scalar form</text>
  <text x="330" y="28" fill="#5eead4" style="font-size: 16px" text-anchor="middle">vectorized</text>

  <rect x="14" y="50" width="150" height="56" rx="9" fill="#2563eb22" stroke="#60a5fa" stroke-width="2"/>
  <text x="89" y="84" fill="#dbeafe" style="font-size: 20px" text-anchor="middle">Σᵢ over n rows</text>
  <rect x="256" y="50" width="150" height="56" rx="9" fill="#0f766e33" stroke="#2dd4bf" stroke-width="2"/>
  <text x="331" y="84" fill="#ccfbf1" style="font-size: 20px" text-anchor="middle">Xᵀ ( · )</text>
  <line x1="172" y1="78" x2="248" y2="78" stroke="#94a3b8" stroke-width="2" marker-end="url(#gdMapArrow)"/>

  <rect x="14" y="130" width="150" height="56" rx="9" fill="#2563eb22" stroke="#60a5fa" stroke-width="2"/>
  <text x="89" y="164" fill="#dbeafe" style="font-size: 18px" text-anchor="middle">−(yᵢ − xᵢᵀθ)</text>
  <rect x="256" y="130" width="150" height="56" rx="9" fill="#0f766e33" stroke="#2dd4bf" stroke-width="2"/>
  <text x="331" y="164" fill="#ccfbf1" style="font-size: 18px" text-anchor="middle">Xθ − y</text>
  <line x1="172" y1="158" x2="248" y2="158" stroke="#94a3b8" stroke-width="2" marker-end="url(#gdMapArrow)"/>

  <rect x="14" y="210" width="150" height="56" rx="9" fill="#2563eb22" stroke="#60a5fa" stroke-width="2"/>
  <text x="89" y="244" fill="#dbeafe" style="font-size: 20px" text-anchor="middle">xᵢⱼ</text>
  <rect x="256" y="210" width="150" height="56" rx="9" fill="#0f766e33" stroke="#2dd4bf" stroke-width="2"/>
  <text x="331" y="244" fill="#ccfbf1" style="font-size: 18px" text-anchor="middle">column j of X</text>
  <line x1="172" y1="238" x2="248" y2="238" stroke="#94a3b8" stroke-width="2" marker-end="url(#gdMapArrow)"/>

  <text x="210" y="298" fill="#94a3b8" style="font-size: 15px" text-anchor="middle">k scalars stacked = one gradient vector</text>
</svg>
</div>
</div>

<!--
Once the scalar per-parameter form is on the board, show that stacking all $k$ partial derivatives into a vector and rewriting the sum as a matrix product gives exactly $\frac{2}{n}X^\top(X\theta-y)$. This is the same design-matrix trick used when MSE was first introduced in the Loss Functions lecture.

Take the mapping diagram row by row, because it is the actual content of the slide. The sum over data points $i$ becomes a multiplication by $X^\top$ — that is what a matrix transpose product *is*, a sum over rows. The residual, with its leading minus sign absorbed, becomes $X\theta - y$ rather than $y - X\theta$. And the single feature value $x_{ij}$ becomes column $j$ of the design matrix, which is precisely why row $j$ of $X^\top$ is what multiplies the residual vector to produce entry $j$ of the gradient.

Do the shape check aloud, every time: $X$ is $n\times k$, so $X\theta$ is $n\times 1$, $X\theta - y$ is $n\times 1$, $X^\top$ is $k\times n$, and the product is $k\times 1$ — the same shape as $\theta$. It has to be, since we subtract the gradient from $\theta$. Tell students that this shape check catches the overwhelming majority of gradient bugs before a single line runs.

Run the code live on a toy `X, y`: initialize theta at zeros, call `gradient_descent(lambda t: mse_grad(t, X, y), np.zeros(k), lr=0.05, n_steps=2000)`, and compare against `np.linalg.lstsq(X, y, rcond=None)[0]`. Confirm the gradient norm shrinks toward zero as theta approaches the least-squares solution — that is the numerical statement of "we have reached the minimum."
-->

---
glowSeed: 338
---

# Deriving the Gradient of MAE

<div class="grid grid-cols-2 gap-6 mt-3 items-start">
<div>
<div border="2 solid orange-800" bg="orange-800/20" rounded-lg p-4>

$$
\begin{aligned}
\ell(\theta) &= \frac{1}{n}\sum_{i=1}^n \big|y_i - x_i^\top\theta\big| \\[4pt]
\frac{\partial \ell}{\partial \theta_j} &= -\frac{1}{n}\sum_{i=1}^n \operatorname{sign}\big(y_i - x_i^\top\theta\big)\,x_{ij}
\end{aligned}
$$

</div>

```python
import numpy as np

def mae_grad(theta, X, y):
    n = X.shape[0]
    residual = y - X @ theta
    # sign(0) is a subgradient choice; np.sign returns 0 there, a common convention
    return -(1 / n) * X.T @ np.sign(residual)
```
</div>

<div>
<svg viewBox="0 0 420 322" class="w-full" role="img" aria-label="A zoomed plot of the absolute value function near zero. The sharp corner at the origin is circled and annotated as not differentiable. A fan of faint lines at the corner shows the subgradient, any slope between minus one and one, while a single tangent line is drawn on the right branch where the derivative is well defined.">
  <line x1="30" y1="240" x2="392" y2="240" stroke="#64748b" stroke-width="2"/>
  <text x="398" y="236" fill="#94a3b8" style="font-size: 16px">z</text>
  <text x="24" y="46" fill="#94a3b8" style="font-size: 16px">|z|</text>
  <path d="M60 60 L210 240 L360 60" fill="none" stroke="#fb923c" stroke-width="4" stroke-linejoin="round"/>
  <g stroke="#a78bfa" stroke-width="2" opacity=".65">
    <line x1="210" y1="240" x2="256" y2="201"/>
    <line x1="210" y1="240" x2="235" y2="186"/>
    <line x1="210" y1="240" x2="210" y2="180"/>
    <line x1="210" y1="240" x2="185" y2="186"/>
    <line x1="210" y1="240" x2="164" y2="201"/>
  </g>
  <circle cx="210" cy="240" r="17" fill="none" stroke="#f87171" stroke-width="2.5" stroke-dasharray="5 4"/>
  <line x1="266" y1="180" x2="342" y2="88" stroke="#5eead4" stroke-width="2.5" stroke-dasharray="6 4"/>
  <circle cx="304" cy="134" r="5" fill="#f8fafc"/>
  <text x="326" y="148" fill="#5eead4" style="font-size: 15px">slope +1</text>
  <text x="46" y="148" fill="#5eead4" style="font-size: 15px">slope −1</text>
  <text x="210" y="276" fill="#f87171" style="font-size: 15px" text-anchor="middle">not differentiable here</text>
  <text x="210" y="302" fill="#c4b5fd" style="font-size: 14px" text-anchor="middle">subgradient: any slope in [−1, 1]</text>
</svg>
</div>
</div>

<!--
Same setup as MSE — same model, same data, same residuals — but a different penalty shape, and the gradient that falls out behaves completely differently.

The derivative of $|u|$ is $\operatorname{sign}(u)$, which is $+1$ for positive $u$ and $-1$ for negative $u$. Chaining with the same $\partial u/\partial\theta_j = -x_{ij}$ from two slides ago gives the formula shown. Point out what is *missing* compared to MSE: the residual's magnitude has vanished entirely. Only its sign survives.

Do not rush past the non-differentiability at zero. Name it explicitly as a **subgradient** situation. At the corner there is no single tangent line — the violet fan in the diagram shows that every slope between $-1$ and $+1$ is a legitimate local linear under-approximation, and any of them may be used as a descent direction. Explain the practical convention, using 0 (which is what `np.sign` returns), without needing the full formal subgradient theory. In practice a residual is almost never exactly zero in floating point, so this case is a formality far more often than a real event.

Then land the qualitative comparison, which is the point of the slide. MAE's gradient cares only about *which side* of the true value the prediction landed on, not by how much. A point that is off by 1000 and a point that is off by 0.001 pull the parameters with exactly the same force. Under MSE the first would pull a million times harder.

Tie this back to the Loss Functions lecture: this is the same robustness-to-outliers property, now seen from the optimization side rather than the penalty-shape side. It also explains the cost — because every point pulls equally, MAE gives the optimizer much less signal about how close it is, and convergence is typically slower and jumpier than for MSE.
-->

---
glowSeed: 339
---

# Logistic Loss · Setup and the Key Building Block

<div class="mt-4" border="2 solid orange-800" bg="orange-800/20" rounded-lg px-5 py-3>
<div class="text-sm font-bold text-orange-300">Loss: log loss / cross-entropy</div>

$$\ell(\theta) = -\frac{1}{n}\sum_{i=1}^n \Big[y_i \log \hat p_i + (1-y_i)\log(1-\hat p_i)\Big]$$

</div>

<div class="grid grid-cols-2 gap-5 mt-4">
<div border="2 solid blue-800" bg="blue-800/20" rounded-lg px-5 py-3>
<div class="text-sm font-bold text-blue-300">Model: sigmoid of a linear score</div>

$$\hat p_i = \sigma\big(x_i^\top\theta\big) = \frac{1}{1+e^{-x_i^\top\theta}}$$

</div>
<div v-click border="2 solid violet-800" bg="violet-800/20" rounded-lg px-5 py-3>
<div class="text-sm font-bold text-violet-300">The building block that makes it all work</div>

$$\sigma'(z) = \sigma(z)\big(1-\sigma(z)\big)$$

</div>
</div>

<div v-click class="mt-4" border="2 solid white/10" bg="white/5" rounded-lg px-5 py-3 text-sm>
The sigmoid's derivative is expressible in terms of the sigmoid itself. Chaining it through the log terms causes almost everything to cancel — which is why a loss this messy-looking produces a gradient as clean as MSE's.
</div>

<div v-click class="mt-3 text-center text-sm opacity-75">Two very different-looking losses. Watch what happens to their gradients.</div>

<!--
Split into two slides deliberately: the setup here, the payoff next. Resist the urge to show the destination early.

Start by reminding students where both pieces came from. The sigmoid appeared as the standard way to turn an unbounded linear score $x_i^\top\theta$ into a probability in $(0,1)$; log loss appeared in the previous lecture, where it was derived from a Bernoulli maximum-likelihood argument rather than invented.

Then dwell on the derivative identity, because it is genuinely the crux. Derive it quickly if time allows: writing $\sigma(z) = (1+e^{-z})^{-1}$ and differentiating gives $e^{-z}/(1+e^{-z})^2$, which factors as $\frac{1}{1+e^{-z}}\cdot\frac{e^{-z}}{1+e^{-z}} = \sigma(z)(1-\sigma(z))$. It is one of the small number of functions whose derivative is a polynomial in itself, and that self-referential structure is exactly what makes the cancellation on the next slide happen.

Ask the class to predict, before the reveal, what the gradient will look like. Most will expect something with $\sigma$ terms scattered through it, extra products, maybe a quotient — because the loss has logarithms and the model has an exponential. Getting them to commit to a wrong guess makes the next slide land much harder.

One practical aside if a student asks: $\sigma(z)(1-\sigma(z))$ is at most $1/4$, and it collapses toward zero when the score is large in magnitude. That is the vanishing-gradient phenomenon in miniature — a confidently saturated sigmoid learns very slowly — and it returns in force in the Neural Networks unit.
-->

---
glowSeed: 340
---

# Logistic Gradient · The Clean Result

<div class="grid grid-cols-2 gap-6 mt-3 items-start">
<div>
<div border="2 solid teal-800" bg="teal-800/20" rounded-lg px-4 py-3 text-center>

$$\nabla_\theta \ell(\theta) = \frac{1}{n}X^\top\big(\hat p - y\big)$$

</div>

```python
import numpy as np

def sigmoid(z):
    return 1 / (1 + np.exp(-z))

def log_loss_grad(theta, X, y):
    n = X.shape[0]
    p_hat = sigmoid(X @ theta)
    return (1 / n) * X.T @ (p_hat - y)
```
</div>

<div>
<svg viewBox="0 0 420 250" class="w-full" role="img" aria-label="The mean squared error gradient and the logistic loss gradient stacked for comparison. Both share the highlighted structure X transpose of prediction minus target; only the prediction term differs, linear for MSE and sigmoid squashed for logistic.">
  <rect x="126" y="34" width="246" height="42" rx="8" fill="#0f766e33" stroke="#2dd4bf" stroke-width="2"/>
  <rect x="126" y="118" width="246" height="42" rx="8" fill="#0f766e33" stroke="#2dd4bf" stroke-width="2"/>

  <text x="14" y="62" fill="#93c5fd" style="font-size: 16px">MSE</text>
  <text x="118" y="62" fill="#e2e8f0" style="font-size: 16px" text-anchor="end">(2/n) ·</text>
  <text x="140" y="62" fill="#ccfbf1" style="font-size: 19px">Xᵀ (</text>
  <text x="196" y="62" fill="#fdba74" style="font-size: 19px">Xθ</text>
  <text x="238" y="62" fill="#ccfbf1" style="font-size: 19px">−  y  )</text>

  <text x="14" y="146" fill="#93c5fd" style="font-size: 16px">Log</text>
  <text x="118" y="146" fill="#e2e8f0" style="font-size: 16px" text-anchor="end">(1/n) ·</text>
  <text x="140" y="146" fill="#ccfbf1" style="font-size: 19px">Xᵀ (</text>
  <text x="196" y="146" fill="#fdba74" style="font-size: 19px">p̂</text>
  <text x="238" y="146" fill="#ccfbf1" style="font-size: 19px">−  y  )</text>

  <line x1="249" y1="82" x2="249" y2="112" stroke="#2dd4bf" stroke-width="2" stroke-dasharray="4 4"/>
  <text x="210" y="196" fill="#5eead4" style="font-size: 16px" text-anchor="middle">Xᵀ ( prediction − target )</text>
  <text x="210" y="222" fill="#fdba74" style="font-size: 15px" text-anchor="middle">only the prediction term differs</text>
</svg>
</div>
</div>

<!--
This is the payoff slide of the lecture. Most students expect log loss to produce something much messier than MSE given how different the two loss formulas look, so the clean matching structure is genuinely surprising and worth pausing on.

Show the derivation briefly — chain rule through the sigmoid derivative from the previous slide, then through the log terms, with several intermediate terms cancelling — but do not feel obligated to grind through every algebraic step on the board. The destination is the point, not each intermediate line. The single sentence version: $\frac{\partial}{\partial\hat p}$ of the log loss contributes a $\frac{\hat p - y}{\hat p(1-\hat p)}$ factor, the sigmoid derivative contributes $\hat p(1-\hat p)$, and those cancel exactly, leaving $\hat p - y$.

Then state the takeaway explicitly, and slowly, because it is the sentence students should leave with: for both models, the gradient is "how wrong the prediction was, weighted by the inputs." The *only* thing that changed between MSE and logistic regression is what "prediction" means — the raw linear output $X\theta$ versus the sigmoid-squashed output $\hat p$.

Point at the diagram: the teal boxes are identical between the two rows. The orange terms are the only difference. There is even a leftover factor-of-2 difference from the squaring convention, which the learning rate absorbs and which nobody should read anything into.

If a student asks whether this is a coincidence: it is not. Both losses are the negative log-likelihood of a generalized linear model with a canonical link, and this cancellation is a general theorem for that family. That is well beyond scope today, but naming it is worthwhile for the students who will meet it later.

Practical note for the assignment: `np.exp(-z)` overflows for very negative `z`. Production implementations use a numerically stable sigmoid; the plain version here is fine for well-scaled toy data.
-->

---
glowSeed: 341
---

# The Three Gradients Share One Skeleton

<div class="mt-4 mx-auto max-w-[820px]" border="2 solid white/10" bg="white/5" rounded-lg px-6 py-5 text-center>

$$\nabla_\theta \ell(\theta) \;\propto\; \sum_{i=1}^n \underbrace{g\big(\text{residual}_i\big)}_{\text{what changes}}\;\cdot\;\underbrace{x_i}_{\text{always}}$$

</div>

<div class="grid grid-cols-3 gap-4 mt-6 text-center">
<v-clicks>
<div border="2 solid blue-800" bg="blue-800/20" rounded-lg p-4>
<div class="font-bold text-blue-300 text-lg">MSE</div>
<div class="text-sm opacity-80 mt-2">weights by the <strong>size</strong> of the residual</div>
<div class="text-xs opacity-70 mt-2">large errors pull hardest</div>
</div>
<div border="2 solid orange-800" bg="orange-800/20" rounded-lg p-4>
<div class="font-bold text-orange-300 text-lg">MAE</div>
<div class="text-sm opacity-80 mt-2">weights by the <strong>direction</strong> only</div>
<div class="text-xs opacity-70 mt-2">every error pulls equally</div>
</div>
<div border="2 solid violet-800" bg="violet-800/20" rounded-lg p-4>
<div class="font-bold text-violet-300 text-lg">Logistic</div>
<div class="text-sm opacity-80 mt-2">weights by <strong>how wrong</strong> the probability was</div>
<div class="text-xs opacity-70 mt-2">confidently wrong pulls hardest</div>
</div>
</v-clicks>
</div>

<div v-click class="mt-6 text-center text-lg">Choosing a loss <em>is</em> choosing how errors get weighted in every single gradient step.</div>

<!--
Use this as a consolidation slide. Ideally let students fill in the comparison themselves from the previous three slides before revealing the cards, since reconstructing it is far more durable than reading it passively.

Read the skeleton equation carefully. Every gradient derived today has the same three-part shape: some function of the residual, multiplied by the input vector $x_i$, summed (or matrix-multiplied) across the data. The $x_i$ factor is universal and comes from the model being linear in its parameters — it is the chain rule's $\partial(x_i^\top\theta)/\partial\theta$ and nothing more. It is the function $g$ applied to the residual that differs between losses, and $g$ is where all the behavioral difference lives.

Name each $g$ concretely as you reveal the cards. For MSE, $g(r) = -2r$ — proportional to the residual, so a point off by 10 pulls ten times harder than a point off by 1. For MAE, $g(r) = -\operatorname{sign}(r)$ — a constant magnitude, so a point off by 10 and a point off by 1 pull identically. For logistic loss, $g$ is $\hat p - y$, which is bounded in $(-1,1)$ and largest precisely when the model assigned high probability to the wrong label.

The core message to land: choosing a loss function is not just choosing a penalty shape in the abstract, as it was framed in the previous lecture. It is choosing exactly how errors get weighted during every single gradient step of training — a very concrete, mechanical consequence of an otherwise abstract-feeling choice. Outlier robustness is not a property someone asserted about MAE; it is a direct, visible consequence of $g$ being bounded.
-->

---
glowSeed: 342
---

# Comparison Table

<div class="mt-6" border="2 solid white/5" bg="white/5" backdrop-blur-sm rounded-lg p-5>
<table class="w-full text-sm">
<thead>
<tr class="text-left opacity-70 border-b border-white/15">
<th class="py-2 pr-3">Loss</th>
<th class="py-2 pr-3">Formula</th>
<th class="py-2 pr-3">Gradient</th>
<th class="py-2 pr-3">Differentiable everywhere?</th>
<th class="py-2">Weights errors by</th>
</tr>
</thead>
<tbody>
<tr class="border-b border-white/10">
<td class="py-3 pr-3 font-bold text-blue-300">MSE</td>
<td class="py-3 pr-3">(1/n) Σ (yᵢ − xᵢᵀθ)²</td>
<td class="py-3 pr-3 text-teal-200">(2/n) Xᵀ(Xθ − y)</td>
<td class="py-3 pr-3 text-teal-300">Yes — smooth</td>
<td class="py-3">residual <strong>magnitude</strong></td>
</tr>
<tr class="border-b border-white/10">
<td class="py-3 pr-3 font-bold text-orange-300">MAE</td>
<td class="py-3 pr-3">(1/n) Σ |yᵢ − xᵢᵀθ|</td>
<td class="py-3 pr-3 text-teal-200">−(1/n) Xᵀ sign(y − Xθ)</td>
<td class="py-3 pr-3 text-red-300">No — corner at 0</td>
<td class="py-3">residual <strong>sign</strong> only</td>
</tr>
<tr>
<td class="py-3 pr-3 font-bold text-violet-300">Logistic</td>
<td class="py-3 pr-3">−(1/n) Σ [y log p̂ + (1−y) log(1−p̂)]</td>
<td class="py-3 pr-3 text-teal-200">(1/n) Xᵀ(p̂ − y)</td>
<td class="py-3 pr-3 text-teal-300">Yes — smooth</td>
<td class="py-3">probability <strong>error</strong></td>
</tr>
</tbody>
</table>
</div>

<div v-click class="mt-6 text-center text-sm opacity-80">Same update rule in all three rows. Only the third column ever changes.</div>

<!--
This is the consolidation artifact students should photograph, and the one to reproduce on the assignment sheet.

Walk the columns rather than the rows, so the comparison is structural rather than a list of three facts. Column two shows three losses that look nothing alike — a square, an absolute value, a pair of logarithms. Column three shows three gradients that look almost identical, all of the form "X transpose times something minus something." That contrast between column two and column three *is* the lecture.

Column four is the only place MAE stands apart, and the practical consequence is worth naming: because of the corner at zero, MAE cannot be minimized by the clean closed-form or smooth-optimizer machinery that MSE admits, and subgradient descent converges more slowly. That is the price paid for the robustness in column five.

Column five is the behavioral summary and the thing to remember when choosing a loss for a real problem. Ask the class to apply it: with a handful of data-entry errors producing wild target values, which column-five behavior do you want? With a medical risk model where overconfidence is dangerous, which one?

Point out one deliberate notational detail: the MAE gradient keeps the residual as $y - X\theta$ with a leading minus sign, matching the code from that slide, while MSE flips to $X\theta - y$ and absorbs it. Both conventions appear in the wild. Students should get in the habit of checking which one a given formula uses rather than pattern-matching on the sign.
-->

---
glowSeed: 343
---

# Batch, Stochastic, and Mini-Batch

<div class="text-center text-sm opacity-80 mb-1">Same update rule. Only <em>how much data</em> goes into each gradient estimate changes.</div>

<svg viewBox="0 0 840 210" class="w-full max-w-[860px] mx-auto" role="img" aria-label="Three contour plots of the same loss surface. Batch gradient descent traces a smooth direct path to the minimum, stochastic gradient descent traces a jagged noisy path that still trends toward the minimum, and mini-batch gradient descent traces a path of intermediate smoothness.">
  <g>
    <ellipse cx="140" cy="105" rx="118" ry="82" fill="none" stroke="#3b82f6" stroke-width="2" opacity=".3"/>
    <ellipse cx="140" cy="105" rx="78" ry="54" fill="none" stroke="#3b82f6" stroke-width="2" opacity=".45"/>
    <ellipse cx="140" cy="105" rx="38" ry="26" fill="none" stroke="#3b82f6" stroke-width="2" opacity=".6"/>
    <polyline points="34,38 78,66 108,86 128,98 138,104" fill="none" stroke="#2dd4bf" stroke-width="3" stroke-linejoin="round"/>
    <circle cx="140" cy="105" r="5" fill="#f8fafc"/>
    <text x="140" y="200" fill="#5eead4" style="font-size: 16px" text-anchor="middle">Batch · all n points</text>
  </g>
  <g transform="translate(280,0)">
    <ellipse cx="140" cy="105" rx="118" ry="82" fill="none" stroke="#3b82f6" stroke-width="2" opacity=".3"/>
    <ellipse cx="140" cy="105" rx="78" ry="54" fill="none" stroke="#3b82f6" stroke-width="2" opacity=".45"/>
    <ellipse cx="140" cy="105" rx="38" ry="26" fill="none" stroke="#3b82f6" stroke-width="2" opacity=".6"/>
    <polyline points="34,38 92,42 62,84 122,66 88,112 146,88 118,124 152,102 138,112" fill="none" stroke="#f87171" stroke-width="3" stroke-linejoin="round"/>
    <circle cx="140" cy="105" r="5" fill="#f8fafc"/>
    <text x="140" y="200" fill="#f87171" style="font-size: 16px" text-anchor="middle">SGD · one point</text>
  </g>
  <g transform="translate(560,0)">
    <ellipse cx="140" cy="105" rx="118" ry="82" fill="none" stroke="#3b82f6" stroke-width="2" opacity=".3"/>
    <ellipse cx="140" cy="105" rx="78" ry="54" fill="none" stroke="#3b82f6" stroke-width="2" opacity=".45"/>
    <ellipse cx="140" cy="105" rx="38" ry="26" fill="none" stroke="#3b82f6" stroke-width="2" opacity=".6"/>
    <polyline points="34,38 84,54 74,88 124,80 106,110 144,96 138,106" fill="none" stroke="#fbbf24" stroke-width="3" stroke-linejoin="round"/>
    <circle cx="140" cy="105" r="5" fill="#f8fafc"/>
    <text x="140" y="200" fill="#fbbf24" style="font-size: 16px" text-anchor="middle">Mini-batch · a subset</text>
  </g>
</svg>

<div class="grid grid-cols-3 gap-4 mt-3 text-sm">
<div v-click border="2 solid teal-800" bg="teal-800/20" rounded-lg p-3>Exact gradient, smooth path, most expensive step.</div>
<div v-click border="2 solid red-800" bg="red-800/20" rounded-lg p-3>Noisy estimate, jagged path, cheapest possible step.</div>
<div v-click border="2 solid amber-800" bg="amber-800/20" rounded-lg p-3>The practical middle ground, used almost universally at scale.</div>
</div>

<!--
Keep this slide short and forward-looking. The goal is just to make sure students have heard these terms, since they will see `batch_size` as a parameter in essentially every neural network training call later in the course, particularly once Keras is introduced.

Make the framing precise: every gradient derived so far sums over the *entire* dataset at each step. That is batch gradient descent, and it is what the formulas on the previous slides literally say. Stochastic gradient descent uses just one data point per step. Mini-batch uses a small random subset — typically 32 to 256 points.

Note briefly that with datasets of realistic size, computing the full gradient over every point at every step is often too expensive, which is precisely why SGD and mini-batching exist. If a dataset has ten million rows, one batch step costs ten million residual computations; a mini-batch step costs 128.

The essential invariant, and the reason this slide belongs in this lecture at all: the underlying update rule $\theta \leftarrow \theta - \eta\nabla_\theta\ell$ is *identical* in all three variants. Nothing about the derivations changes. Only the estimate of $\nabla_\theta\ell$ changes — from exact, to a one-sample estimate, to a small-sample average. Each is an unbiased estimate of the same quantity; they differ only in variance, which is exactly what the three path pictures show.

Full treatment — including the genuinely surprising result that noisier updates can help rather than hurt, by escaping poor regions of non-convex surfaces — is out of scope here and belongs to the Optimization in Practice unit. Do not get drawn into it if asked; just promise it.
-->

---
glowSeed: 344
---

# Summary

<div class="grid grid-cols-2 gap-5 mt-6">
<div v-click border="2 solid teal-800" bg="teal-800/20" rounded-lg p-5>
<div class="font-bold text-teal-300 text-lg">Minimization became an algorithm</div>
<div class="text-sm opacity-80 mt-2">Gradient descent turns “minimize the loss” into something concrete, iterative, and implementable in seven lines.</div>
</div>
<div v-click border="2 solid blue-800" bg="blue-800/20" rounded-lg p-5>
<div class="font-bold text-blue-300 text-lg">One update rule for every model</div>
<div class="text-sm opacity-80 mt-2">θ ← θ − η∇L(θ) is the same for every model in this course. Only the gradient formula changes.</div>
</div>
<div v-click border="2 solid orange-800" bg="orange-800/20" rounded-lg p-5>
<div class="font-bold text-orange-300 text-lg">Three losses, three code-ready gradients</div>
<div class="text-sm opacity-80 mt-2">MSE, MAE, and logistic loss each reduce to a clean formula — and each weights errors differently.</div>
</div>
<div v-click border="2 solid violet-800" bg="violet-800/20" rounded-lg p-5>
<div class="font-bold text-violet-300 text-lg">The unit is complete</div>
<div class="text-sm opacity-80 mt-2">Every foundational concept needed to understand <em>any</em> supervised learning algorithm is now in place.</div>
</div>
</div>

<!--
Close by tying this lecture explicitly back to the whole arc of the unit. We now have every piece needed to actually train a model: a way to define the problem (loss and ERM), a way to measure honestly (train/validation/test splits), a way to control complexity (regularization), and now a way to actually find good parameters (gradient descent).

Restate the central claim once more, because it is the load-bearing idea of the entire course and students should be able to say it back: the update rule does not change. Not for linear regression, not for logistic regression, not for a fifty-layer neural network. What changes is the function you hand to `grad_fn`. Everything students learn about models from here on can be organized as answers to two questions — what is $f_\theta$, and what is $\ell$.

If time permits, invite a prediction: given how MSE and logistic gradients turned out, what do students expect the gradient of a neural network to look like? The honest answer — the same "prediction minus target, weighted by inputs" shape at the output layer, with the chain rule propagating it backward through the layers — is exactly backpropagation, and previewing it here makes that later lecture feel inevitable rather than novel.
-->

---
glowSeed: 345
---

# Core ML Concepts, Complete

<svg viewBox="0 0 900 290" class="w-full max-w-[900px] mx-auto" role="img" aria-label="A map of the six Core ML Concepts lectures as connected boxes: Types of Learning, Bias-Variance Tradeoff, Train Validation Test and CV, then Overfitting and Regularization, Loss Functions and ERM, and Gradient Descent, which is highlighted as the current lecture. An arrow leads from Gradient Descent down to a box labelled Supervised Learning Regression as the next unit.">
  <defs>
    <marker id="gdMapEnd" viewBox="0 0 10 10" refX="9" refY="5" markerWidth="6" markerHeight="6" orient="auto-start-reverse"><path d="M0 0 L10 5 L0 10 z" fill="#94a3b8"/></marker>
  </defs>

  <rect x="20" y="24" width="270" height="54" rx="10" fill="#0f766e26" stroke="#14b8a6" stroke-width="2"/>
  <text x="155" y="57" fill="#ccfbf1" style="font-size: 16px" text-anchor="middle">Types of Learning</text>
  <rect x="315" y="24" width="270" height="54" rx="10" fill="#2563eb26" stroke="#3b82f6" stroke-width="2"/>
  <text x="450" y="57" fill="#dbeafe" style="font-size: 16px" text-anchor="middle">Bias–Variance Tradeoff</text>
  <rect x="610" y="24" width="270" height="54" rx="10" fill="#c2410c26" stroke="#f97316" stroke-width="2"/>
  <text x="745" y="57" fill="#fed7aa" style="font-size: 16px" text-anchor="middle">Train / Val / Test + CV</text>
  <line x1="292" y1="51" x2="311" y2="51" stroke="#94a3b8" stroke-width="2" marker-end="url(#gdMapEnd)"/>
  <line x1="587" y1="51" x2="606" y2="51" stroke="#94a3b8" stroke-width="2" marker-end="url(#gdMapEnd)"/>

  <line x1="745" y1="80" x2="745" y2="122" stroke="#94a3b8" stroke-width="2" marker-end="url(#gdMapEnd)"/>

  <rect x="610" y="126" width="270" height="54" rx="10" fill="#6d28d926" stroke="#8b5cf6" stroke-width="2"/>
  <text x="745" y="159" fill="#ddd6fe" style="font-size: 16px" text-anchor="middle">Overfitting + Regularization</text>
  <rect x="315" y="126" width="270" height="54" rx="10" fill="#0f766e26" stroke="#14b8a6" stroke-width="2"/>
  <text x="450" y="159" fill="#ccfbf1" style="font-size: 16px" text-anchor="middle">Loss Functions + ERM</text>
  <rect x="20" y="126" width="270" height="54" rx="10" fill="#0f766e55" stroke="#2dd4bf" stroke-width="3"/>
  <text x="155" y="153" fill="#f0fdfa" style="font-size: 16px" text-anchor="middle">Gradient Descent</text>
  <text x="155" y="171" fill="#5eead4" style="font-size: 13px" text-anchor="middle">you are here</text>
  <line x1="608" y1="153" x2="589" y2="153" stroke="#94a3b8" stroke-width="2" marker-end="url(#gdMapEnd)"/>
  <line x1="313" y1="153" x2="294" y2="153" stroke="#94a3b8" stroke-width="2" marker-end="url(#gdMapEnd)"/>

  <line x1="155" y1="182" x2="155" y2="216" stroke="#94a3b8" stroke-width="2" marker-end="url(#gdMapEnd)"/>
  <rect x="20" y="220" width="270" height="54" rx="10" fill="#c2410c33" stroke="#fb923c" stroke-width="2.5"/>
  <text x="155" y="253" fill="#ffedd5" style="font-size: 16px" text-anchor="middle">Next: Regression</text>
</svg>

<div v-click class="mt-2 mx-auto max-w-[760px]" border="2 solid white/10" bg="white/5" rounded-lg px-6 py-4 text-center text-lg>
Next unit: <strong>Supervised Learning — Regression</strong>
<div class="text-sm opacity-75 mt-2">The MSE gradient derived today reappears verbatim as the training loop.</div>
</div>

<!--
This is the closing map for the whole unit, so read it as a story rather than a list.

Types of Learning established what kind of feedback a learning algorithm receives. Bias-variance explained mechanically why a fitted model makes errors — systematic versus sample-dependent. Splits and cross-validation gave the honest measurement procedure needed to actually observe that tradeoff instead of fooling ourselves with training error. Overfitting and regularization gave a concrete lever for moving along it. Loss functions and ERM gave the precise mathematical objective. And today's lecture supplied the missing verb: how to actually *find* the parameters that objective asks for.

Tell students that starting next lecture, all of this machinery stops being abstract and gets applied directly to linear regression, where the MSE gradient derived earlier in this deck will reappear verbatim as the training loop — the same $\frac{2}{n}X^\top(X\theta-y)$, in the same shape, doing the same job. Linear regression will also be shown to have a closed-form solution, which makes it an unusually good first case study: students can watch gradient descent converge to an answer they can verify exactly.

After that, every subsequent model in the course — regression, classification, ensembles, neural networks — is introduced as a new choice of $f_\theta$ and $\ell$ dropped into this same loop.

Take questions before moving on to the Regression unit.
-->
