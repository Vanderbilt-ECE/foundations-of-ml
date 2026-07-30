---
theme: default
highlighter: shiki
css: unocss
colorSchema: dark
title: 'Gradient Descent Variants: SGD, Momentum, and Adam'
info: |
  ## Gradient Descent Variants: SGD, Momentum, and Adam
  Make descent faster, smoother, and adaptive
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
glowSeed: 910
---

# Gradient Descent Variants: SGD, Momentum, and Adam

### Make descent faster, smoother, and adaptive

<div class="pt-8 opacity-80 text-lg">Optimization in Practice · Foundations of Machine Learning</div>

<div class="mt-14 flex justify-center gap-4" aria-hidden="true">
<div class="w-28 h-3 rounded-full bg-teal-400/70"></div>
<div class="w-20 h-3 rounded-full bg-blue-400/60"></div>
<div class="w-14 h-3 rounded-full bg-violet-400/50"></div>
</div>

<!--
This deck sits inside the Optimization in Practice module, right after we established that training a model means minimizing a loss function J(θ) over parameters θ, and that gradient descent moves θ in the direction that decreases J fastest locally: θ ← θ − α∇J(θ). Everything up to this point has treated "gradient descent" as one algorithm. In practice it is a family, and the specific member you pick changes how fast training converges, how sensitive it is to the learning rate α, and even what solution you end up at.

Roadmap for today: we start with plain stochastic gradient descent (SGD) and see exactly why it zigzags on realistic loss surfaces. Then we fix that zigzag with momentum, and separately fix the "one learning rate for every parameter" problem with RMSProp. Adam is nothing mysterious once you've seen those two pieces — it is momentum and RMSProp combined, plus a bias-correction term for the first few steps. We close with a worked comparison of all four methods on the same loss surface, and an honest discussion of when Adam is not the right default.

Common misconception to defuse up front: "Adam is strictly better than SGD" is false. Adam converges faster and is more forgiving of a poorly tuned learning rate, but a carefully tuned SGD-with-momentum schedule frequently generalizes better, especially for image classification with convolutional networks. We will return to this at the end.
-->

---
glowSeed: 911
---

# Plain SGD Zigzags

<div class="grid grid-cols-2 gap-8 items-start">
<div>
<div class="space-y-3 mt-4">
<div v-click border="2 solid white/5" bg="white/5" rounded-lg px-4 py-3>
<span class="font-bold text-teal-300">Noisy gradient</span>
<span class="text-sm opacity-85"> — A mini-batch estimates the full-data direction.</span>
</div>
<div v-click border="2 solid white/5" bg="white/5" rounded-lg px-4 py-3>
<span class="font-bold text-blue-300">Ill-conditioned surface</span>
<span class="text-sm opacity-85"> — Steep and shallow axes need different effective step sizes.</span>
</div>
<div v-click border="2 solid white/5" bg="white/5" rounded-lg px-4 py-3>
<span class="font-bold text-amber-300">Result</span>
<span class="text-sm opacity-85"> — Oscillation across the steep axis and slow progress along the shallow one.</span>
</div>
</div>
</div>
<div>
<svg role="img" aria-label="Conceptual chart for Plain SGD Zigzags" viewBox="0 0 500 310" class="w-full max-w-xl mx-auto mt-7">
  <line x1="55" y1="260" x2="470" y2="260" stroke="#64748b" stroke-width="2"/><line x1="55" y1="35" x2="55" y2="260" stroke="#64748b" stroke-width="2"/>
  <path d="M60 235 C130 210,145 70,220 100 S320 210,465 55" fill="none" stroke="#2dd4bf" stroke-width="5"/>
  <path d="M60 245 C135 230,205 195,270 165 S385 110,465 95" fill="none" stroke="#60a5fa" stroke-width="4" stroke-dasharray="9 7"/>
  <g fill="#f59e0b"><circle cx="65" cy="230" r="6"/><circle cx="163" cy="185" r="6"/><circle cx="261" cy="110" r="6"/><circle cx="359" cy="150" r="6"/><circle cx="457" cy="65" r="6"/></g>
  <g fill="#cbd5e1" style="font-size: 12px" text-anchor="middle"><text x="65" y="285">0</text><text x="163" y="285">5</text><text x="261" y="285">10</text><text x="359" y="285">20</text><text x="457" y="285">30 steps</text></g>
  <g style="font-size: 12px"><text x="335" y="42" fill="#5eead4">primary signal</text><text x="335" y="82" fill="#93c5fd">comparison</text></g>
</svg>
<div v-click class="mt-4" style="font-size: .9em" border="2 solid teal-800" bg="teal-800/20" rounded-lg px-4 py-3>

$$
\theta_{t+1}=\theta_t-\alpha\nabla J(\theta_t)
$$

</div>
</div>
</div>

<!--
Walk through the update rule term by term: θ_t is the parameter vector at step t (e.g., all the weights of a linear model or a neural network), α is the learning rate — a small positive scalar that controls how big a step we take — and ∇J(θ_t) is the gradient of the loss with respect to θ, evaluated using a mini-batch rather than the full dataset. That mini-batch estimate is why we call this "stochastic": g_t = ∇J(θ_t) is a noisy, unbiased estimate of the true full-batch gradient, and that noise is actually useful — it helps the optimizer escape shallow local minima and saddle points, at the cost of a jittery trajectory.

The zigzag in the plot is not a bug, it is a direct consequence of curvature. Picture a loss surface shaped like a narrow valley: steep walls on one axis, a gentle slope along the valley floor on the other. The gradient always points perpendicular to the local contour line, so on this elongated bowl the gradient has a large component across the steep axis and a small component along the shallow axis. A single learning rate α has to be small enough not to overshoot and oscillate on the steep axis, which makes progress along the shallow axis painfully slow. The dashed comparison curve shows a smoother, faster path — this is the target we are building toward across the rest of the deck.

Common misconception: students often think a smaller learning rate always fixes oscillation. It does reduce the zigzag amplitude, but at the direct cost of slower convergence along the shallow axis — you cannot fix an ill-conditioned surface with a scalar learning rate alone. That is exactly the motivation for momentum, which we introduce next.
-->

---
glowSeed: 912
---

# Momentum Accumulates a Useful Direction

<div class="grid grid-cols-2 gap-8 items-start">
<div>
<div class="space-y-3 mt-4">
<div v-click border="2 solid white/5" bg="white/5" rounded-lg px-4 py-3>
<span class="font-bold text-teal-300">Moving average</span>
<span class="text-sm opacity-85"> — Blend the current gradient with recent history.</span>
</div>
<div v-click border="2 solid white/5" bg="white/5" rounded-lg px-4 py-3>
<span class="font-bold text-blue-300">Cancel oscillation</span>
<span class="text-sm opacity-85"> — Alternating steep-axis gradients partially cancel.</span>
</div>
<div v-click border="2 solid white/5" bg="white/5" rounded-lg px-4 py-3>
<span class="font-bold text-amber-300">Reinforce progress</span>
<span class="text-sm opacity-85"> — Consistent shallow-axis gradients accumulate.</span>
</div>
</div>
</div>
<div>
<div v-click class="mt-4" style="font-size: .9em" border="2 solid teal-800" bg="teal-800/20" rounded-lg px-4 py-3>

$$
v_{t+1}=\beta v_t+(1-\beta)g_t,\qquad \theta_{t+1}=\theta_t-\alpha v_{t+1}
$$

</div>

</div>
</div>

<!--
Momentum keeps a running exponential moving average v_t of past gradients instead of using only the current gradient. Term by term: v_t is the "velocity" — a vector the same shape as θ, initialized to zero — β ∈ [0,1) is the momentum coefficient (commonly 0.9), g_t is the current mini-batch gradient, and α is still the learning rate. At each step we blend the old velocity with the new gradient, v_{t+1} = β v_t + (1−β) g_t, then move θ using the velocity instead of the raw gradient: θ_{t+1} = θ_t − α v_{t+1}.

Why this fixes the zigzag: on the steep axis, consecutive gradients alternate in sign as the parameter overshoots back and forth across the valley, so their exponential average partially cancels — the oscillation is damped. On the shallow axis, consecutive gradients point in roughly the same direction step after step, so they accumulate and the effective step size along that axis grows. Net effect: less wasted motion across the valley, more consistent motion along it.

On the β = 0.9 figure: think of v_t as remembering roughly the last 1/(1−β) = 10 gradients, with exponentially decaying weight — the most recent gradient matters most, a gradient from 10 steps ago has decayed to about 1/e of its original weight, and gradients much further back are negligible.

Common misconception to flag explicitly: this is "classical" or "heavy-ball" momentum, which evaluates the gradient at the current position θ_t. It is not the same as Nesterov accelerated gradient, which evaluates the gradient at a look-ahead position θ_t − αβv_t — a small but important difference we cover on the next slide. Students often use the two names interchangeably; they are different update rules with different convergence guarantees.
-->

---
glowSeed: 9125
---

# Nesterov Momentum Looks Ahead First

<div class="grid grid-cols-2 gap-8 items-start">
<div>
<div class="space-y-3 mt-4">
<div v-click border="2 solid white/5" bg="white/5" rounded-lg px-4 py-3>
<span class="font-bold text-teal-300">Look-ahead point</span>
<span class="text-sm opacity-85"> — Peek at where momentum is already about to carry θ.</span>
</div>
<div v-click border="2 solid white/5" bg="white/5" rounded-lg px-4 py-3>
<span class="font-bold text-blue-300">Gradient there, not here</span>
<span class="text-sm opacity-85"> — Evaluate ∇J at the look-ahead point instead of the current θ.</span>
</div>
<div v-click border="2 solid white/5" bg="white/5" rounded-lg px-4 py-3>
<span class="font-bold text-amber-300">Effect</span>
<span class="text-sm opacity-85"> — Corrects course earlier, reducing overshoot near the minimum.</span>
</div>
</div>
</div>
<div>
<div v-click class="mt-4" style="font-size: .85em" border="2 solid teal-800" bg="teal-800/20" rounded-lg px-4 py-3>

$$
\begin{aligned}
\tilde\theta_t &= \theta_t - \alpha\beta v_t \\
g_t &= \nabla J(\tilde\theta_t) \\
v_{t+1} &= \beta v_t + (1-\beta) g_t \\
\theta_{t+1} &= \theta_t - \alpha v_{t+1}
\end{aligned}
$$

</div>
</div>
</div>

<!--
Classical (heavy-ball) momentum from the previous slide computes the gradient g_t = ∇J(θ_t) at the current position, then updates velocity and position. Nesterov accelerated gradient (NAG) reorders this: it first takes a provisional step in the direction momentum is already carrying us, θ̃_t = θ_t − αβv_t, and evaluates the gradient at that look-ahead point instead. Intuitively, if momentum is about to carry the parameters over the minimum and up the far wall of the valley, evaluating the gradient there detects the "you're about to overshoot" signal one step earlier than evaluating it at θ_t, so the correction arrives sooner.

This is a genuine algorithmic difference with a real consequence: NAG has a provably better convergence rate than classical momentum for convex smooth objectives (O(1/t²) instead of O(1/t) for the function-value gap in the deterministic case), and empirically it reduces the overshoot-and-correct oscillation you sometimes see with heavy-ball momentum near a minimum. In deep learning frameworks this appears as `nesterov=True` in SGD optimizers (e.g. PyTorch's `torch.optim.SGD(..., momentum=0.9, nesterov=True)`).

Address the misconception directly: many practitioners say "momentum" when they mean either variant interchangeably, and many tutorials present Nesterov's update algebraically rearranged in a way that obscures the look-ahead idea. The concrete distinguishing question to ask on an exam or in an interview: "where is the gradient evaluated — at θ_t or at a point shifted by the current velocity?" That answer tells you which momentum variant you are looking at.
-->

---
glowSeed: 913
---

# One Global Learning Rate Is a Compromise

<div class="grid grid-cols-3 gap-4 mt-6">
<div v-click border="2 solid teal-800" bg="teal-800/20" rounded-lg p-4>
<div class="font-bold text-teal-300 mb-2">Large-gradient parameters</div>
<div class="text-sm leading-relaxed opacity-90">Need smaller effective steps to remain stable.</div>
</div>
<div v-click border="2 solid blue-800" bg="blue-800/20" rounded-lg p-4>
<div class="font-bold text-blue-300 mb-2">Small-gradient parameters</div>
<div class="text-sm leading-relaxed opacity-90">Need larger effective steps to make progress.</div>
</div>
<div v-click border="2 solid amber-800" bg="amber-800/20" rounded-lg p-4>
<div class="font-bold text-amber-300 mb-2">Adaptive goal</div>
<div class="text-sm leading-relaxed opacity-90">Learn a separate scale for every parameter from gradient history.</div>
</div>
</div>


<!--
Momentum solves the "wasted oscillation" problem, but it still leaves one scalar α shared by every parameter in θ. In a real model, different parameters can have wildly different gradient magnitudes and curvatures — a weight feeding a frequently activated neuron might receive large, consistent gradients every step, while a weight touched only by rare features gets small, sparse gradients. An α tuned to be safe for the large-gradient parameters is too small to make timely progress on the small-gradient ones, and an α large enough to move the small-gradient parameters quickly will make the large-gradient parameters diverge or oscillate.

This is exactly the setup for adaptive learning-rate methods: instead of one α for the whole parameter vector, learn a separate effective step size per parameter, based on that parameter's own gradient history. RMSProp, introduced next, is the simplest widely used way to do this — it tracks the recent typical magnitude of each parameter's gradient and divides the step by it.
-->

---
glowSeed: 914
---

# RMSProp Rescales by Squared Gradients

<div class="grid grid-cols-2 gap-8 items-start">
<div>
<div class="space-y-3 mt-4">
<div v-click border="2 solid white/5" bg="white/5" rounded-lg px-4 py-3>
<span class="font-bold text-teal-300">Second moment</span>
<span class="text-sm opacity-85"> — Track an exponential average of g² per parameter.</span>
</div>
<div v-click border="2 solid white/5" bg="white/5" rounded-lg px-4 py-3>
<span class="font-bold text-blue-300">Automatic scale</span>
<span class="text-sm opacity-85"> — Large typical gradients get smaller steps; tiny ones get larger steps.</span>
</div>
<div v-click border="2 solid white/5" bg="white/5" rounded-lg px-4 py-3>
<span class="font-bold text-amber-300">Numerical guard</span>
<span class="text-sm opacity-85"> — ε prevents division by zero.</span>
</div>
</div>
</div>
<div>
<div v-click class="mt-4" style="font-size: .9em" border="2 solid teal-800" bg="teal-800/20" rounded-lg px-4 py-3>

$$
\begin{aligned}s_{t+1}&=\beta_2s_t+(1-\beta_2)g_t^2\\\theta_{t+1}&=\theta_t-\frac{\alpha g_t}{\sqrt{s_{t+1}}+\epsilon}\end{aligned}
$$

</div>

</div>
</div>

<!--
RMSProp keeps a second exponential moving average, s_t, but of the squared gradient rather than the gradient itself: s_{t+1} = β₂ s_t + (1−β₂) g_t². Note this is elementwise squaring — s_t has the same shape as θ, one entry per parameter — so it tracks each parameter's own recent typical gradient magnitude independently. β₂ plays the same role β played for momentum, a decay coefficient close to 1 (commonly 0.999); it is subscripted "2" here to distinguish it from momentum's coefficient once we combine both ideas in Adam.

The update divides the learning rate by the square root of that running average: θ_{t+1} = θ_t − α g_t / (√s_{t+1} + ε). Read this as a per-parameter effective learning rate α / (√s_{t+1} + ε): a parameter whose gradients have been consistently large gets a small effective step (dividing by a large √s shrinks the step), and a parameter whose gradients have been small and infrequent gets a larger effective step. This directly fixes the problem from the previous slide.

ε (typically 1e-8) is a small constant purely for numerical safety — without it, a parameter that has seen zero gradient so far (s_t = 0) would cause division by zero. Common misconception: ε is not a hyperparameter you tune for performance; it exists only to prevent a numerical error, and its exact value rarely matters as long as it is small relative to typical √s values.

Transition: RMSProp adapts step size per parameter but, like plain SGD, uses only the instantaneous gradient direction — it has no memory of direction the way momentum does. The natural next question, which Adam answers, is: why not track both a first moment (direction, like momentum) and a second moment (scale, like RMSProp) at once?
-->

---
glowSeed: 915
---

# Adam Combines Both Ideas

<div class="grid grid-cols-2 gap-8 items-start">
<div>
<div class="space-y-3 mt-4">
<div v-click border="2 solid white/5" bg="white/5" rounded-lg px-4 py-3>
<span class="font-bold text-teal-300">First moment m</span>
<span class="text-sm opacity-85"> — Momentum-style average of gradients.</span>
</div>
<div v-click border="2 solid white/5" bg="white/5" rounded-lg px-4 py-3>
<span class="font-bold text-blue-300">Second moment v</span>
<span class="text-sm opacity-85"> — RMSProp-style average of squared gradients.</span>
</div>
<div v-click border="2 solid white/5" bg="white/5" rounded-lg px-4 py-3>
<span class="font-bold text-amber-300">Bias correction</span>
<span class="text-sm opacity-85"> — Compensate for both estimates starting at zero.</span>
</div>
</div>
</div>
<div>
<div v-click class="mt-4" style="font-size: .9em" border="2 solid teal-800" bg="teal-800/20" rounded-lg px-4 py-3>

$$
\begin{aligned}\hat m_t&=m_t/(1-\beta_1^t),\quad \hat v_t=v_t/(1-\beta_2^t)\\\theta_{t+1}&=\theta_t-\alpha\frac{\hat m_t}{\sqrt{\hat v_t}+\epsilon}\end{aligned}
$$

</div>

</div>
</div>

<!--
Adam (Adaptive Moment Estimation) keeps both moving averages we just built separately: m_t, the first moment (a momentum-style average of the raw gradient, exactly like v_t before but renamed), and v_t, the second moment (an RMSProp-style average of squared gradients — careful, the slide reuses v as Adam's standard notation for the second moment, which is a different symbol than the momentum velocity two slides ago). Their update equations are literally the momentum and RMSProp updates run side by side: m_t = β₁ m_{t-1} + (1−β₁) g_t and v_t = β₂ v_{t-1} + (1−β₂) g_t², with typical defaults β₁ = 0.9, β₂ = 0.999.

The bias-correction step is the one genuinely new idea. Because m_0 and v_0 are initialized to zero, the early estimates m_t and v_t are biased toward zero — badly so in the first few steps, since a moving average that starts at zero and gets only a (1−β) fraction of new information per step takes many steps to "warm up" to the true magnitude. Adam corrects this explicitly by dividing out the accumulated decay: m̂_t = m_t / (1 − β₁ᵗ) and v̂_t = v_t / (1 − β₂ᵗ). At t = 1, 1 − β₁¹ = 0.1, so m̂_1 = m_1 / 0.1 = 10·m_1 — a large correction. As t grows, β₁ᵗ → 0, so the denominator → 1 and the correction fades to nothing; by t ≈ 100 with β₂ = 0.999 the correction is already negligible.

Finally θ_{t+1} = θ_t − α m̂_t / (√v̂_t + ε) — momentum's smoothed direction, scaled by RMSProp's per-parameter adaptive step size, with the early-step bias removed. Without bias correction, Adam would take artificially tiny, overly cautious steps for the first several dozen iterations, exactly when the optimizer most needs to move.
-->

---
glowSeed: 916
---

# Adam Update in Code

<div class="grid grid-cols-2 gap-4 mt-6">
<div v-click border="2 solid teal-800" bg="teal-800/20" rounded-lg p-4>
<div class="font-bold text-teal-300 mb-2">Smooth</div>
<div class="text-sm leading-relaxed opacity-90">m carries direction.</div>
</div>
<div v-click border="2 solid blue-800" bg="blue-800/20" rounded-lg p-4>
<div class="font-bold text-blue-300 mb-2">Adapt</div>
<div class="text-sm leading-relaxed opacity-90">v scales each coordinate.</div>
</div>
</div>

```python
m = np.zeros_like(theta)
v = np.zeros_like(theta)
for t in range(1, steps + 1):
    g = grad(theta)
    m = beta1 * m + (1 - beta1) * g
    v = beta2 * v + (1 - beta2) * g**2
    m_hat = m / (1 - beta1**t)
    v_hat = v / (1 - beta2**t)
    theta -= alpha * m_hat / (np.sqrt(v_hat) + eps)
```

<!--
Walk the loop line by line: `m` and `v` start as zero arrays shaped like `theta` — this is the "cold start" that makes bias correction necessary. Inside the loop, `g = grad(theta)` is a single mini-batch gradient evaluation. The next two lines are the exponential moving averages we derived: `m` blends toward the new gradient at rate `(1 - beta1)`, `v` blends toward the new squared gradient at rate `(1 - beta2)`. `m_hat` and `v_hat` apply bias correction using the current step count `t`, which is why the loop is written as `range(1, steps + 1)` rather than starting at zero — bias correction's denominator `1 - beta1**t` would be zero at t = 0. The final line is the parameter update: note the elementwise division by `np.sqrt(v_hat) + eps`, which is what makes the effective step size different for every entry of `theta`.

This is genuinely the entire algorithm — production implementations (PyTorch's `torch.optim.Adam`, TensorFlow's `tf.keras.optimizers.Adam`) add engineering details like weight decay decoupling (AdamW) or mixed-precision safeguards, but the mathematical core is these eight lines.

Transition: we have now built SGD, momentum, RMSProp, and Adam as four points on one family tree. The next slide puts all four on the same loss surface so you can see the qualitative difference in their paths, not just compare their formulas.
-->

---
glowSeed: 9165
---

# Four Optimizers, One Loss Surface

<svg role="img" aria-label="Elliptical loss contours with four optimizer trajectories: SGD zigzags, momentum overshoots and settles, RMSProp adapts per axis, Adam converges most directly" viewBox="0 0 620 320" class="w-full max-w-2xl mx-auto">
  <g fill="none" stroke="#334155" stroke-width="1.5">
    <ellipse cx="310" cy="160" rx="270" ry="78"/>
    <ellipse cx="310" cy="160" rx="200" ry="57"/>
    <ellipse cx="310" cy="160" rx="130" ry="37"/>
    <ellipse cx="310" cy="160" rx="65" ry="18"/>
  </g>
  <circle cx="310" cy="160" r="4" fill="#e2e8f0"/>
  <text x="310" y="146" fill="#e2e8f0" text-anchor="middle" style="font-size:12px">minimum</text>

  <path d="M55 50 L120 260 L180 78 L235 235 L275 113 L300 172 L308 158 L310 161" fill="none" stroke="#2dd4bf" stroke-width="3"/>
  <circle cx="55" cy="50" r="5" fill="#2dd4bf"/>
  <text x="30" y="35" fill="#5eead4" style="font-size:13px">SGD</text>

  <path d="M55 50 C 130 113, 150 225, 220 217 S 300 168, 309 161" fill="none" stroke="#60a5fa" stroke-width="3"/>
  <text x="150" y="248" fill="#93c5fd" style="font-size:13px">Momentum (overshoots once)</text>

  <path d="M55 50 C 110 65, 200 138, 260 154 S 305 159, 310 160" fill="none" stroke="#f59e0b" stroke-width="3"/>
  <text x="90" y="82" fill="#fbbf24" style="font-size:13px">RMSProp</text>

  <path d="M55 50 C 95 87, 220 150, 280 158 S 308 160, 310 160" fill="none" stroke="#a78bfa" stroke-width="3.5"/>
  <text x="330" y="95" fill="#c4b5fd" style="font-size:13px">Adam (smooth + adaptive)</text>
</svg>

<div class="grid grid-cols-4 gap-2 mt-3 text-xs">
<div v-click border="2 solid teal-800" bg="teal-800/20" rounded-lg px-2 py-1.5><span class="font-bold text-teal-300">SGD</span> — zigzags across the steep axis every step.</div>
<div v-click border="2 solid blue-800" bg="blue-800/20" rounded-lg px-2 py-1.5><span class="font-bold text-blue-300">Momentum</span> — one large overshoot, then settles.</div>
<div v-click border="2 solid amber-800" bg="amber-800/20" rounded-lg px-2 py-1.5><span class="font-bold text-amber-300">RMSProp</span> — bends toward the minimum, per-axis scaling.</div>
<div v-click border="2 solid violet-800" bg="violet-800/20" rounded-lg px-2 py-1.5><span class="font-bold text-violet-300">Adam</span> — combines both; usually the shortest path here.</div>
</div>

<!--
All four optimizers start at the same point on the same elongated elliptical loss surface — the ellipses are level sets of J(θ), so the tight spacing on the vertical axis versus the loose spacing on the horizontal axis is exactly the ill-conditioning that caused the zigzag on the first slide of this deck.

Plain SGD (teal) takes the sharpest possible step each time, so it bounces back and forth across the steep axis while creeping along the shallow one — the same zigzag we saw earlier, now drawn on a 2D bowl instead of a 1D trace. Momentum (blue) smooths this into a single sweeping overshoot: it builds enough velocity along the shallow axis that it flies somewhat past the minimum before curving back, trading the many-small-oscillations failure mode for a single-large-oscillation failure mode. RMSProp (amber) does not overshoot the same way, because it rescales each axis by its own recent gradient magnitude — it bends toward the minimum more directly because the steep axis gets automatically shrunk steps. Adam (violet) combines momentum's smoothing with RMSProp's per-axis scaling, and in this illustration takes the most direct path of the four.

Important caveat to state explicitly: this is a stylized, convex, noise-free illustration meant to build intuition about the mechanism. Real loss surfaces for neural networks are extremely high-dimensional, non-convex, and full of saddle points, so "which optimizer wins" in practice depends heavily on the specific architecture, data, batch size, and learning-rate schedule — there is no proof that Adam's path is always shortest on real problems. Treat this figure as showing *why* each mechanism behaves differently, not as a guarantee of *which one wins* on your dataset.
-->

---
glowSeed: 917
---

# Practical Optimizer Choice

<div class="grid grid-cols-2 gap-4 mt-6">
<div v-click border="2 solid teal-800" bg="teal-800/20" rounded-lg p-4>
<div class="font-bold text-teal-300 mb-2">Adam</div>
<div class="text-sm leading-relaxed opacity-90">Strong low-effort default for most neural-network training.</div>
</div>
<div v-click border="2 solid blue-800" bg="blue-800/20" rounded-lg p-4>
<div class="font-bold text-blue-300 mb-2">SGD + momentum</div>
<div class="text-sm leading-relaxed opacity-90">Can generalize better on some well-studied tasks with careful schedules.</div>
</div>
<div v-click border="2 solid amber-800" bg="amber-800/20" rounded-lg p-4>
<div class="font-bold text-amber-300 mb-2">Classical models</div>
<div class="text-sm leading-relaxed opacity-90">Prefer closed-form or specialized convex solvers when available.</div>
</div>
<div v-click border="2 solid violet-800" bg="violet-800/20" rounded-lg p-4>
<div class="font-bold text-violet-300 mb-2">No universal winner</div>
<div class="text-sm leading-relaxed opacity-90">Optimizer performance remains problem dependent.</div>
</div>
</div>


<!--
Adam's practical strength is robustness: it typically converges quickly with default hyperparameters (α = 1e-3, β₁ = 0.9, β₂ = 0.999) across a wide range of architectures, so it is the standard first choice when prototyping a new model — you spend less time tuning the learning rate because the per-parameter adaptive scaling partly compensates for a suboptimal global α.

The counterpoint, which is the misconception this slide exists to correct: several well-studied results (particularly in image classification with convolutional networks, e.g. ResNets on ImageNet) show that SGD with momentum, given a carefully tuned learning-rate schedule, reaches a solution that generalizes measurably better than Adam's solution — even though Adam often gets to a low training loss faster. One hypothesis is that Adam's adaptive per-parameter scaling can converge to sharper minima that generalize worse; this remains an active research question, not settled textbook fact, so we state it as an empirically observed tendency, not a proof.

For classical, convex models — linear regression, logistic regression, SVMs — prefer closed-form solutions (normal equations) or specialized convex solvers (L-BFGS, coordinate descent) over any gradient-descent variant when they are available and the problem is small enough: they are exact or near-exact, and gradient descent is solving a problem that already has a better tool. The unifying lesson for the whole slide: "optimizer performance is problem dependent" is not a hedge, it is the actual empirical finding — treat Adam as a strong, low-effort default, not a proof of universal superiority, and be willing to try SGD+momentum with a schedule when final generalization quality matters more than prototyping speed.
-->

---
glowSeed: 918
---

# From SGD to Adam

<div class="mt-8"><div class="grid grid-cols-3 gap-4 mt-6">
<div v-click border="2 solid teal-800" bg="teal-800/20" rounded-lg p-4>
<div class="font-bold text-teal-300 mb-2">Momentum</div>
<div class="text-sm leading-relaxed opacity-90">Smooth direction.</div>
</div>
<div v-click border="2 solid blue-800" bg="blue-800/20" rounded-lg p-4>
<div class="font-bold text-blue-300 mb-2">RMSProp</div>
<div class="text-sm leading-relaxed opacity-90">Adapt coordinate scale.</div>
</div>
<div v-click border="2 solid amber-800" bg="amber-800/20" rounded-lg p-4>
<div class="font-bold text-amber-300 mb-2">Adam</div>
<div class="text-sm leading-relaxed opacity-90">Combine and correct bias.</div>
</div>
</div></div>

<div v-click class="mt-10 text-center text-lg" border="2 solid white/10" bg="white/5" rounded-lg px-6 py-4>Next: tune every model hyperparameter systematically.</div>

<!--
Summarize the deck as a chain of fixes, each motivated by a concrete failure of the previous method: plain SGD zigzags on ill-conditioned surfaces because it uses only the instantaneous gradient with one global learning rate; momentum fixes the zigzag by averaging gradient direction over time, and Nesterov momentum sharpens this further by evaluating the gradient at a look-ahead point; RMSProp fixes the "one learning rate for every parameter" problem by rescaling each parameter's step by its own recent gradient magnitude; Adam fixes nothing new mechanically — it simply combines momentum's direction-smoothing with RMSProp's per-parameter scaling and adds bias correction so both moving averages are trustworthy from step one.

The exam-relevant skill from this deck is not memorizing four formulas — it is being able to look at any new optimizer and ask "which specific failure mode of a simpler method is this trying to fix, and what does it cost?" Every method here trades some simplicity or some generalization robustness for faster or smoother convergence; none of them are free.

Transition to next topic: choosing an optimizer is only one hyperparameter among many — learning rate, momentum coefficients, batch size, regularization strength, network width and depth all interact. The next deck covers how to search that hyperparameter space systematically rather than by hand-tuning one setting at a time.
-->
