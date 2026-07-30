---
theme: default
highlighter: shiki
css: unocss
colorSchema: dark
title: 'Perceptrons and Multilayer Networks'
info: |
  ## Perceptrons and Multilayer Networks
  Familiar ingredients, composed into nonlinear models
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
glowSeed: 810
---

# Perceptrons and Multilayer Networks

### Familiar ingredients, composed into nonlinear models

<div class="pt-8 opacity-80 text-lg">Neural Networks and Deep Learning Basics · Foundations of Machine Learning</div>

<div class="mt-14 flex justify-center gap-4" aria-hidden="true">
<div class="w-28 h-3 rounded-full bg-teal-400/70"></div>
<div class="w-20 h-3 rounded-full bg-blue-400/60"></div>
<div class="w-14 h-3 rounded-full bg-violet-400/50"></div>
</div>

<!--
This unit follows directly from linear models and logistic regression: a perceptron reuses the exact same weighted sum z = w^T x + b that linear and logistic regression compute, but feeds it through a hard step function instead of leaving it linear or squashing it with a sigmoid. Today's roadmap builds from a single artificial neuron all the way to a network: (1) the biological and historical motivation for the perceptron, (2) the single perceptron as a linear classifier with a geometric decision boundary, (3) the perceptron learning rule, worked by hand on a tiny dataset until the weights converge, (4) the perceptron's fundamental limitation — it cannot solve XOR because XOR is not linearly separable, (5) how stacking a hidden layer with a nonlinearity fixes this, including an explicit set of weights that solves XOR and a hand-worked forward pass, (6) why the nonlinearity is not optional — without it, depth collapses back into one linear map, (7) the universal approximation theorem and its important caveats, and (8) architecture vocabulary that carries into every later lecture. By the end, students should be able to explain, from first principles, why deep learning needed both the perceptron's failure and the multilayer fix to become possible. Next class covers backpropagation, the algorithm that actually trains these networks.
-->

---
glowSeed: 811
---

# From Biological Neurons to an Artificial One

<div class="grid grid-cols-2 gap-8 items-start">
<div>
<div class="space-y-3 mt-4">
<div v-click border="2 solid white/5" bg="white/5" rounded-lg px-4 py-3>
<span class="font-bold text-teal-300">Biological inspiration</span>
<span class="text-sm opacity-85"> — Dendrites collect signals, the soma sums them, and the axon fires only past a threshold.</span>
</div>
<div v-click border="2 solid white/5" bg="white/5" rounded-lg px-4 py-3>
<span class="font-bold text-blue-300">McCulloch–Pitts (1943)</span>
<span class="text-sm opacity-85"> — First mathematical model: a binary threshold unit computing simple logical functions.</span>
</div>
<div v-click border="2 solid white/5" bg="white/5" rounded-lg px-4 py-3>
<span class="font-bold text-amber-300">Rosenblatt (1958)</span>
<span class="text-sm opacity-85"> — Added learnable weights and a training rule; built as the Mark I Perceptron hardware.</span>
</div>
<div v-click border="2 solid white/5" bg="white/5" rounded-lg px-4 py-3>
<span class="font-bold text-red-300">Minsky &amp; Papert (1969)</span>
<span class="text-sm opacity-85"> — Proved perceptrons cannot learn XOR, triggering the first "AI winter."</span>
</div>
</div>
</div>
<div>
<svg role="img" aria-label="Diagram of a biological neuron mapped to an artificial neuron" viewBox="0 0 400 300" class="w-full mt-4">
  <g stroke="#475569" stroke-width="2" fill="none">
    <path d="M30 90 C55 70, 60 60, 90 65" />
    <path d="M30 130 C55 130, 65 120, 90 110" />
    <path d="M30 170 C55 160, 65 150, 90 140" />
  </g>
  <text x="20" y="60" fill="#94a3b8" style="font-size:12px">dendrites</text>
  <circle cx="120" cy="120" r="34" fill="#0f172a" stroke="#2dd4bf" stroke-width="3" />
  <text x="120" y="125" fill="#5eead4" style="font-size:12px" text-anchor="middle">soma / Σ</text>
  <line x1="154" y1="120" x2="260" y2="120" stroke="#f59e0b" stroke-width="3" />
  <text x="160" y="105" fill="#f59e0b" style="font-size:12px">axon (fires if z ≥ 0)</text>
  <circle cx="270" cy="120" r="6" fill="#a78bfa" />
  <text x="285" y="125" fill="#a78bfa" style="font-size:12px">synapse to next unit</text>
  <text x="30" y="240" fill="#cbd5e1" style="font-size:13px">artificial analogue: inputs x → weighted sum z=w·x+b → step(z)</text>
</svg>
</div>
</div>

<!--
Define every term before moving on. A biological neuron receives electrical signals through dendrites, integrates them in the cell body (soma), and if the integrated signal crosses a threshold, fires a spike down its axon to downstream neurons via synapses. McCulloch and Pitts (1943) abstracted this into a binary threshold logic unit — no learning yet, just fixed logical functions like AND, OR, and NOT built from hand-chosen weights. Rosenblatt's 1958 perceptron was the first model that could adjust its own weights from data, and he built it as physical hardware (the Mark I Perceptron, using potentiometers as weights) rather than only as an equation. The story has a well-known plot twist: Minsky and Papert's 1969 book "Perceptrons" proved rigorously that a single perceptron cannot represent the XOR function, and their (widely over-read) conclusion that neural networks were a dead end contributed to a decade-plus funding drought known as the first AI winter — even though the fix (adding hidden layers) was already conceptually available. Keep this history in mind: it previews exactly the arc of today's lecture, from a single neuron's power to its limitation to the multilayer fix.
-->

---
glowSeed: 812
---

# The Single Perceptron: Weighted Sum + Threshold

<div class="grid grid-cols-2 gap-8 items-start">
<div>
<div class="space-y-3 mt-4">
<div v-click border="2 solid white/5" bg="white/5" rounded-lg px-4 py-3>
<span class="font-bold text-teal-300">Weighted sum</span>
<span class="text-sm opacity-85"> — Combine the inputs exactly as in a linear model.</span>
</div>
<div v-click border="2 solid white/5" bg="white/5" rounded-lg px-4 py-3>
<span class="font-bold text-blue-300">Hard decision</span>
<span class="text-sm opacity-85"> — A step function converts the score to 0 or 1.</span>
</div>
<div v-click border="2 solid white/5" bg="white/5" rounded-lg px-4 py-3>
<span class="font-bold text-amber-300">Close relative</span>
<span class="text-sm opacity-85"> — Logistic regression uses the same score with a smooth sigmoid.</span>
</div>
</div>
</div>
<div>
<div v-click class="mt-4" style="font-size: .9em" border="2 solid teal-800" bg="teal-800/20" rounded-lg px-4 py-3>

$$
z=w^\top x+b,\qquad \hat y=\mathbf1[z\ge0]
$$

</div>

<div v-click class="mt-4 text-sm opacity-85">
Here $x\in\mathbb{R}^n$ is the input vector, $w\in\mathbb{R}^n$ is a learned weight vector, $b\in\mathbb{R}$ is a learned bias (threshold), and $\mathbf1[\cdot]$ is the indicator function: 1 if the condition holds, 0 otherwise.
</div>
</div>
</div>

<!--
Walk the formula term by term. z = w^T x + b is a scalar "score," computed identically to ordinary linear regression: each input feature x_i is multiplied by a learned weight w_i, the products are summed, and a bias b is added (the bias shifts the threshold and is equivalent to an extra input fixed at 1 with weight b). What makes this a perceptron rather than a linear regressor is the second step: y-hat = 1[z ≥ 0], a hard step function that outputs exactly 0 or 1 with nothing in between. Contrast this immediately with logistic regression, which computes the identical score z but passes it through a smooth sigmoid σ(z) = 1/(1+e^{-z}) to get a probability in (0,1) — the perceptron is what you get if you replace that smooth squashing with an all-or-nothing threshold. A common misconception is that perceptrons and logistic regression are unrelated models; they are the same linear score with two different output nonlinearities, which is why both produce a linear decision boundary. Next, we make that boundary geometric.
-->

---
glowSeed: 813
---

# Geometric Interpretation: A Linear Boundary

<div class="grid grid-cols-2 gap-8 items-center">
<div>
<v-clicks>

- Setting $z=0$ traces the **decision boundary**: a line in 2D, a plane in 3D, a hyperplane in general
- $w$ is the **normal vector** to that boundary — it points in the direction $z$ increases fastest
- $b$ shifts the boundary away from the origin without changing its orientation
- Points with $z\ge0$ (same side as $w$) are classified 1; the other side is classified 0

</v-clicks>
</div>
<div>
<svg role="img" aria-label="2D plot showing a separating line with a normal vector" viewBox="0 0 400 300" class="w-full">
  <line x1="40" y1="260" x2="380" y2="260" stroke="#475569" stroke-width="1.5" />
  <line x1="40" y1="260" x2="40" y2="20" stroke="#475569" stroke-width="1.5" />
  <text x="10" y="20" fill="#94a3b8" style="font-size:13px">w·x + b = 0 separates the classes</text>

  <line x1="90" y1="240" x2="330" y2="60" stroke="#2dd4bf" stroke-width="3" />
  <text x="335" y="55" fill="#2dd4bf" style="font-size:13px">boundary</text>

  <g fill="#60a5fa"><circle cx="120" cy="220" r="8" /><circle cx="160" cy="230" r="8" /><circle cx="90" cy="180" r="8" /></g>
  <text x="80" y="255" fill="#60a5fa" style="font-size:12px">class 0</text>

  <g fill="#f59e0b"><circle cx="280" cy="120" r="8" /><circle cx="310" cy="90" r="8" /><circle cx="250" cy="150" r="8" /></g>
  <text x="290" y="70" fill="#f59e0b" style="font-size:12px">class 1</text>

  <defs>
    <marker id="nv" markerWidth="8" markerHeight="8" refX="4" refY="4" orient="auto">
      <path d="M0,0 L8,4 L0,8 Z" fill="#f472b6" />
    </marker>
  </defs>
  <line x1="210" y1="150" x2="270" y2="95" stroke="#f472b6" stroke-width="3" marker-end="url(#nv)" />
  <text x="275" y="100" fill="#f472b6" style="font-size:13px">w (normal)</text>
</svg>
</div>
</div>

<!--
This is the geometric picture every student should be able to draw from memory. In n dimensions, the set of points satisfying w^T x + b = 0 is a hyperplane — a line when n=2, a flat plane when n=3, and a generalized flat "cut" through space for higher n. The weight vector w is perpendicular (normal) to this hyperplane and points toward the region classified as 1; this follows because z = w^T x + b changes fastest when you move along w, and z=0 exactly on the boundary. The bias b controls how far the hyperplane sits from the origin without rotating it — increasing b shifts the boundary in the -w direction, admitting more points into the positive class. A perceptron can therefore only ever produce decision boundaries that are straight lines (or flat hyperplanes) — no curves, no closed regions. Flag the misconception directly: students sometimes think the "line" is drawn by the data; it is entirely determined by w and b, and different (w,b) pairs give different lines. This limitation is exactly what will make XOR impossible for a single perceptron later in this deck.
-->

---
glowSeed: 814
---

# The Perceptron Learning Rule

<div class="grid grid-cols-2 gap-8 items-start">
<div>
<div v-click style="font-size: .95em" border="2 solid teal-800" bg="teal-800/20" rounded-lg px-4 py-3>

$$
w \leftarrow w + \eta\,(y-\hat y)\,x, \qquad b \leftarrow b + \eta\,(y-\hat y)
$$

</div>
<div class="space-y-3 mt-4">
<div v-click border="2 solid white/5" bg="white/5" rounded-lg px-4 py-3>
<span class="font-bold text-teal-300">No error, no update</span>
<span class="text-sm opacity-85"> — If $\hat y=y$, then $(y-\hat y)=0$ and nothing changes.</span>
</div>
<div v-click border="2 solid white/5" bg="white/5" rounded-lg px-4 py-3>
<span class="font-bold text-blue-300">Error nudges the boundary</span>
<span class="text-sm opacity-85"> — A false negative ($y{=}1,\hat y{=}0$) adds $\eta x$ to $w$, rotating the boundary toward $x$.</span>
</div>
<div v-click border="2 solid white/5" bg="white/5" rounded-lg px-4 py-3>
<span class="font-bold text-amber-300">Convergence theorem</span>
<span class="text-sm opacity-85"> — If the classes are linearly separable, this rule finds a separating hyperplane in finitely many updates.</span>
</div>
</div>
</div>
<div class="text-sm opacity-85 mt-6">
Here $\eta>0$ is the <strong>learning rate</strong> (step size), $y\in\{0,1\}$ is the true label, and $\hat y=\mathbf1[z\ge0]$ is the current prediction. The update runs one training example at a time — this is <em>online</em> learning, the ancestor of stochastic gradient descent.
</div>
</div>

<!--
Walk through why this rule makes sense. The error term (y - ŷ) can only take three values: 0 (correct prediction, no update at all), +1 (a false negative: true label 1 but predicted 0), or -1 (a false positive: true label 0 but predicted 1). When there's a false negative, w ← w + ηx rotates the weight vector toward x, increasing w^T x for that point and making the model more likely to predict 1 next time it sees something like x; a false positive does the opposite, rotating w away from x. The learning rate η controls how large each nudge is — too large and the boundary oscillates, too small and convergence is slow, though for the classic perceptron rule any positive η works eventually. State the convergence theorem precisely and flag the common misconception around it: the Perceptron Convergence Theorem (Rosenblatt/Novikoff) guarantees this rule finds a perfectly separating hyperplane in a finite number of steps if and only if the data is linearly separable — it says nothing about non-separable data, where the weights can cycle forever without settling. This is one of the most common student errors: assuming the rule "eventually works" on any dataset. It does not — XOR, coming up shortly, is the canonical counterexample. Next we work this rule by hand on a tiny dataset.
-->

---
glowSeed: 815
---

# Worked Example — Setup

<div class="grid grid-cols-2 gap-8 items-start">
<div>
<div class="text-sm opacity-85 mb-2">Training the AND gate: 2 inputs, 4 examples, one perceptron.</div>
<table class="text-sm w-full text-center border-separate" style="border-spacing: 4px">
<thead><tr class="opacity-70"><th>$x_1$</th><th>$x_2$</th><th>$y$</th></tr></thead>
<tbody>
<tr v-click><td border="1 solid white/10" p-2>0</td><td border="1 solid white/10" p-2>0</td><td border="1 solid white/10" p-2>0</td></tr>
<tr v-click><td border="1 solid white/10" p-2>0</td><td border="1 solid white/10" p-2>1</td><td border="1 solid white/10" p-2>0</td></tr>
<tr v-click><td border="1 solid white/10" p-2>1</td><td border="1 solid white/10" p-2>0</td><td border="1 solid white/10" p-2>0</td></tr>
<tr v-click><td border="1 solid white/10" p-2>1</td><td border="1 solid white/10" p-2>1</td><td border="1 solid white/10" p-2 class="text-teal-300 font-bold">1</td></tr>
</tbody>
</table>
</div>
<div>
<div v-click border="2 solid white/5" bg="white/5" rounded-lg px-4 py-3 class="mb-3">
<span class="font-bold text-blue-300">Initialization</span>
<span class="text-sm opacity-85 block mt-1">$w=(0,0)$, $b=0$, learning rate $\eta=1$</span>
</div>
<div v-click border="2 solid white/5" bg="white/5" rounded-lg px-4 py-3>
<span class="font-bold text-amber-300">Process</span>
<span class="text-sm opacity-85 block mt-1">Visit each row in order; update on every misclassification; repeat until a full pass makes zero errors.</span>
</div>
</div>
</div>

<!--
Set up the concrete example we'll hand-trace. The AND gate is the simplest nontrivial linearly separable dataset: it outputs 1 only when both inputs are 1, and 0 otherwise, and a single line easily separates the lone positive point (1,1) from the three negative points. We initialize the weights and bias to zero — a common, if arbitrary, starting point — and set the learning rate η=1 for simplicity so every update is an easy integer computation. The training procedure is: sweep through the four rows in order, and for each row compute z = w·x + b, then ŷ = 1[z≥0]; if ŷ differs from the true y, apply the update rule from the previous slide immediately (this is "online" perceptron training, not a batch average). A full pass through all four examples is called an epoch. We stop once an entire epoch produces zero updates, meaning every example is already correctly classified. On the next slide we trace the first epoch by hand, updating weights exactly twice.
-->

---
glowSeed: 816
---

# Worked Example — Updates by Hand

<div class="text-sm">
<table class="w-full text-center border-separate" style="border-spacing: 6px">
<thead class="opacity-70"><tr><th>$x$</th><th>$y$</th><th>$z=w{\cdot}x+b$</th><th>$\hat y$</th><th>update?</th><th>new $(w,b)$</th></tr></thead>
<tbody>
<tr v-click><td border="1 solid white/10" p-2>(0,0)</td><td border="1 solid white/10" p-2>0</td><td border="1 solid white/10" p-2>0</td><td border="1 solid white/10" p-2>1</td><td border="1 solid white/10" p-2 class="text-amber-300">yes, err = -1</td><td border="1 solid white/10" p-2>(0,0), $-1$</td></tr>
<tr v-click><td border="1 solid white/10" p-2>(0,1)</td><td border="1 solid white/10" p-2>0</td><td border="1 solid white/10" p-2>$-1$</td><td border="1 solid white/10" p-2>0</td><td border="1 solid white/10" p-2 class="opacity-60">no</td><td border="1 solid white/10" p-2>unchanged</td></tr>
<tr v-click><td border="1 solid white/10" p-2>(1,0)</td><td border="1 solid white/10" p-2>0</td><td border="1 solid white/10" p-2>$-1$</td><td border="1 solid white/10" p-2>0</td><td border="1 solid white/10" p-2 class="opacity-60">no</td><td border="1 solid white/10" p-2>unchanged</td></tr>
<tr v-click><td border="1 solid white/10" p-2>(1,1)</td><td border="1 solid white/10" p-2>1</td><td border="1 solid white/10" p-2>$-1$</td><td border="1 solid white/10" p-2>0</td><td border="1 solid white/10" p-2 class="text-amber-300">yes, err = +1</td><td border="1 solid white/10" p-2>(1,1), $0$</td></tr>
</tbody>
</table>
</div>

<div v-click class="mt-6 text-center" border="2 solid teal-800" bg="teal-800/20" rounded-lg px-4 py-3>
End of epoch 1: $w=(1,1)$, $b=0$ — closer, but $(0,0)$ still misclassifies. Training continues.
</div>

<!--
Trace every row aloud. Row 1, x=(0,0): z = 0·0+0·0+0 = 0, and since the rule is ŷ=1[z≥0], z=0 counts as class 1 — but the true label is 0, so this is a false positive (error = y-ŷ = 0-1 = -1). Applying the update: w ← w + 1·(-1)·(0,0) = (0,0) (unchanged, because the input itself is the zero vector — multiplying an error by a zero input contributes nothing), and b ← b + 1·(-1) = -1. Row 2, x=(0,1): z = 0·0+0·1+(-1) = -1 < 0, ŷ=0, matches y=0, no update. Row 3, x=(1,0): z = 0·1+0·0-1 = -1 < 0, ŷ=0, matches y=0, no update. Row 4, x=(1,1): z = 0·1+0·1-1 = -1 < 0, ŷ=0, but true y=1 — a false negative (error=+1). Update: w ← (0,0)+1·(1,1) = (1,1), b ← -1+1 = 0. After one epoch we've moved from the useless all-zero weights to w=(1,1), b=0 — progress, but not yet a solution, since (0,0) now gives z=0 ≥0, still misclassified as 1. This is completely normal: perceptron convergence is not guaranteed in one pass. The next slide shows the fully converged result.
-->

---
glowSeed: 817
---

# Worked Example — Convergence

<div class="grid grid-cols-2 gap-8 items-center">
<div>
<v-clicks>

- Continuing the same process for **4 more epochs**, the weights evolve: $(1,1),0 \to (1,0),{-2} \to (2,1),{-2} \to \ldots \to (2,1),{-3}$
- Final weights: $w=(2,1)$, $b=-3$ — every example now classified correctly
- Decision boundary: $2x_1+x_2-3=0$, cleanly separating $(1,1)$ from the rest

</v-clicks>
<div v-click class="mt-4 text-sm opacity-85">
Verify: $(0,0)\to z=-3$, $(0,1)\to z=-2$, $(1,0)\to z=-1$ — all $<0\Rightarrow \hat y=0$. $(1,1)\to z=0 \Rightarrow \hat y=1$. All four match $y$.
</div>
</div>
<div>
<svg role="img" aria-label="Final decision boundary separating the AND gate" viewBox="0 0 400 300" class="w-full">
  <line x1="40" y1="260" x2="380" y2="260" stroke="#475569" stroke-width="1.5" />
  <line x1="40" y1="260" x2="40" y2="20" stroke="#475569" stroke-width="1.5" />
  <text x="30" y="280" fill="#94a3b8" style="font-size:12px">0</text>
  <text x="190" y="280" fill="#94a3b8" style="font-size:12px">1</text>
  <text x="15" y="130" fill="#94a3b8" style="font-size:12px">1</text>

  <line x1="165" y1="50" x2="270" y2="260" stroke="#2dd4bf" stroke-width="3" />
  <text x="275" y="240" fill="#2dd4bf" style="font-size:13px">2x₁+x₂-3=0</text>

  <g fill="#60a5fa">
    <circle cx="60" cy="260" r="9" /><circle cx="60" cy="120" r="9" /><circle cx="200" cy="260" r="9" />
  </g>
  <g fill="#f59e0b"><circle cx="200" cy="120" r="9" /></g>
  <text x="205" y="105" fill="#f59e0b" style="font-size:12px">(1,1) → 1</text>
  <text x="20" y="35" fill="#cbd5e1" style="font-size:12px">all other points → 0</text>
</svg>
</div>
</div>

<!--
Give students the final answer without re-deriving every intermediate epoch on the slide (do that at the board if time allows, or leave it as a take-home check). After a total of five epochs, the perceptron rule settles at w=(2,1), b=-3, and a quick check confirms every example is now correctly classified: the three negative examples give z values of -3, -2, and -1 (all comfortably negative, so ŷ=0), while (1,1) gives z=2+1-3=0, which is ≥0 so ŷ=1, matching the true label. The corresponding boundary line is 2x₁+x₂-3=0, which passes just below the point (1,1), isolating it in its own half-plane from the other three corners of the unit square. This is the Perceptron Convergence Theorem from the earlier slide made concrete: because AND is linearly separable, the online update rule was guaranteed to find some separating line, though not necessarily this exact one — a different example order or a different learning rate would generally converge to a different (but still valid) separating line, since infinitely many lines separate this dataset. Flag this explicitly: the perceptron finds *a* solution, not *the* solution — there is no notion of a maximum-margin "best" line the way there is with a support vector machine.
-->

---
glowSeed: 818
---

# Worked Example — Verifying with Code

```python
import numpy as np

X = np.array([[0, 0], [0, 1], [1, 0], [1, 1]])
y = np.array([0, 0, 0, 1])          # AND gate

w = np.zeros(2)
b = 0.0
eta = 1.0

for epoch in range(10):
    errors = 0
    for xi, yi in zip(X, y):
        z = w @ xi + b
        y_hat = 1 if z >= 0 else 0
        update = eta * (yi - y_hat)
        w += update * xi
        b += update
        errors += int(update != 0)
    if errors == 0:
        break

print(epoch + 1, w, b)   # 5 [2. 1.] -3.0
```

<!--
Run this live to confirm the hand computation. The code implements exactly the rule from the last three slides: an outer loop over epochs, an inner loop over the four training examples, computing z, thresholding it into ŷ, and applying the update only when ŷ differs from y. The `errors` counter tracks how many updates happened in a given epoch; when it hits zero, every example is correctly classified and we break out early. Running this prints epoch 5 and weights [2. 1.] with bias -3.0, exactly matching the by-hand result. This is a good moment to note the connection to modern deep learning: this loop — compute prediction, compute error, nudge parameters — is the direct ancestor of the training loops used for every neural network today; only the error signal (a hard 0/1 mismatch here) and the update rule (plain addition here, versus a gradient computed via backpropagation later) will change. Transition: now that we've seen what a perceptron *can* learn, we turn to what it fundamentally *cannot*.
-->

---
glowSeed: 819
---

# XOR: A Deceptively Simple Problem

<div class="grid grid-cols-2 gap-8 items-start">
<div>
<div class="space-y-3 mt-4">
<div v-click border="2 solid white/5" bg="white/5" rounded-lg px-4 py-3>
<span class="font-bold text-teal-300">Inputs</span>
<span class="text-sm opacity-85"> — 00 and 11 map to 0; 01 and 10 map to 1.</span>
</div>
<div v-click border="2 solid white/5" bg="white/5" rounded-lg px-4 py-3>
<span class="font-bold text-blue-300">Geometry</span>
<span class="text-sm opacity-85"> — The positive points occupy opposite corners.</span>
</div>
<div v-click border="2 solid white/5" bg="white/5" rounded-lg px-4 py-3>
<span class="font-bold text-amber-300">Limitation</span>
<span class="text-sm opacity-85"> — No single line separates the two labels.</span>
</div>
</div>
</div>
<div>
<div role="img" aria-label="Two by two matrix for One Linear Boundary Cannot Solve XOR" class="mt-8 max-w-lg mx-auto">
<div class="grid grid-cols-[6rem_1fr_1fr] gap-2 text-center text-sm">
<div></div><div class="font-bold text-blue-300">$x_2=0$</div><div class="font-bold text-blue-300">$x_2=1$</div>
<div class="flex items-center justify-end pr-2 font-bold text-teal-300">$x_1=0$</div><div border="2 solid teal-800" bg="teal-800/20" rounded-lg p-5 class="text-2xl font-bold">0</div><div border="2 solid red-800" bg="red-800/20" rounded-lg p-5 class="text-2xl font-bold">1</div>
<div class="flex items-center justify-end pr-2 font-bold text-teal-300">$x_1=1$</div><div border="2 solid red-800" bg="red-800/20" rounded-lg p-5 class="text-2xl font-bold">1</div><div border="2 solid teal-800" bg="teal-800/20" rounded-lg p-5 class="text-2xl font-bold">0</div>
</div>
</div>

</div>
</div>

<!--
XOR (exclusive or) outputs 1 exactly when its two binary inputs differ, and 0 when they agree: (0,0)→0, (0,1)→1, (1,0)→1, (1,1)→0. It looks like a trivial four-row truth table, barely more complex than AND or OR, which is exactly why Minsky and Papert's 1969 proof that a perceptron cannot learn it was so consequential — it showed that "looks simple" and "is linearly separable" are not the same thing. Notice the geometry described in the cards: plotted on the unit square, the two positive examples (0,1) and (1,0) sit on opposite corners, and the two negative examples (0,0) and (1,1) sit on the other pair of opposite corners — a checkerboard pattern. Invite students to actually try drawing a single straight line on the unit square that puts (0,1) and (1,0) on one side and (0,0) and (1,1) on the other before revealing that it's provably impossible; this hands-on failure makes the next slide's geometric argument land harder. Transition: we now prove rigorously why no line can work.
-->

---
glowSeed: 820
---

# XOR: Why No Line Works

<div class="grid grid-cols-2 gap-8 items-center">
<div>
<v-clicks>

- The positive class $\{(0,1),(1,0)\}$ and negative class $\{(0,0),(1,1)\}$ each have a midpoint at $(0.5,0.5)$
- Any line separating them would have to separate two point sets whose **convex hulls overlap** at that shared midpoint
- A hyperplane can never separate two sets whose convex hulls intersect — this is the formal definition of "not linearly separable"
- The perceptron learning rule would cycle forever here, never converging (it is only guaranteed to converge when the data *is* separable)

</v-clicks>
</div>
<div>
<svg role="img" aria-label="Plot showing no line separates the XOR classes" viewBox="0 0 400 300" class="w-full">
  <line x1="40" y1="260" x2="380" y2="260" stroke="#475569" stroke-width="1.5" />
  <line x1="40" y1="260" x2="40" y2="20" stroke="#475569" stroke-width="1.5" />

  <line x1="60" y1="120" x2="200" y2="260" stroke="#60a5fa" stroke-width="2" stroke-dasharray="5 4" opacity="0.6" />
  <line x1="140" y1="240" x2="120" y2="40" stroke="#60a5fa" stroke-width="2" stroke-dasharray="5 4" opacity="0.6" />
  <text x="150" y="30" fill="#60a5fa" style="font-size:12px">every candidate line fails ✗</text>

  <g fill="#f59e0b"><circle cx="60" cy="120" r="9" /><circle cx="200" cy="260" r="9" /></g>
  <text x="30" y="105" fill="#f59e0b" style="font-size:12px">1 (diff.)</text>

  <g fill="#60a5fa"><circle cx="60" cy="260" r="9" /><circle cx="200" cy="120" r="9" /></g>
  <text x="205" y="105" fill="#60a5fa" style="font-size:12px">0 (same)</text>

  <circle cx="130" cy="190" r="4" fill="#f472b6" />
  <text x="140" y="195" fill="#f472b6" style="font-size:12px">shared midpoint (0.5, 0.5)</text>
</svg>
</div>
</div>

<!--
Give the rigorous version of the impossibility argument, not just "it looks hard." Take the convex hull of the positive class {(0,1),(1,0)} — since there are only two points, the hull is the line segment between them, whose midpoint is (0.5,0.5). Do the same for the negative class {(0,0),(1,1)}: its hull is the segment between them, and that segment's midpoint is also exactly (0.5,0.5). Because both convex hulls pass through the same point, they overlap, and a fundamental theorem of linear separability (a consequence of the separating hyperplane theorem) states that two sets can be separated by a hyperplane if and only if their convex hulls are disjoint. Since these hulls share a point, no hyperplane — no line, in 2D — can separate them, period; this is not a limitation of one particular training algorithm, it is a mathematical fact about the dataset. Consequently, if you ran the perceptron learning rule from two slides ago on this data, it would never terminate: the weights would update forever, chasing an update that always fixes one misclassified point while breaking another, because the "no errors" state is unreachable. This is precisely the boundary of the Perceptron Convergence Theorem's guarantee: it promises convergence if and only if the data is linearly separable, and XOR is the textbook example where that hypothesis fails. Transition: the fix is not a better learning rule — it's a more expressive model.
-->

---
glowSeed: 821
---

# Hidden Layers Combine Several Boundaries

<div class="grid grid-cols-2 gap-8 items-start">
<div>
<div class="space-y-3 mt-4">
<div v-click border="2 solid white/5" bg="white/5" rounded-lg px-4 py-3>
<span class="font-bold text-teal-300">Hidden units</span>
<span class="text-sm opacity-85"> — Each learns its own linear score and nonlinearity.</span>
</div>
<div v-click border="2 solid white/5" bg="white/5" rounded-lg px-4 py-3>
<span class="font-bold text-blue-300">Output unit</span>
<span class="text-sm opacity-85"> — Combines learned intermediate features.</span>
</div>
<div v-click border="2 solid white/5" bg="white/5" rounded-lg px-4 py-3>
<span class="font-bold text-amber-300">Result</span>
<span class="text-sm opacity-85"> — Even one hidden layer can carve out a nonlinear XOR region.</span>
</div>
</div>
</div>
<div>
<svg role="img" aria-label="Network diagram for Hidden Layers Combine Several Boundaries" viewBox="0 0 440 290" class="w-full max-w-xl mx-auto mt-8">
  <g stroke="#475569" stroke-width="2" opacity=".75">
    <line x1="70" y1="75" x2="190" y2="55"/><line x1="70" y1="75" x2="190" y2="145"/><line x1="70" y1="215" x2="190" y2="145"/><line x1="70" y1="215" x2="190" y2="235"/>
    <line x1="190" y1="55" x2="315" y2="95"/><line x1="190" y1="145" x2="315" y2="95"/><line x1="190" y1="145" x2="315" y2="195"/><line x1="190" y1="235" x2="315" y2="195"/>
    <line x1="315" y1="95" x2="405" y2="145"/><line x1="315" y1="195" x2="405" y2="145"/>
  </g>
  <g fill="#0f172a" stroke-width="4"><circle cx="70" cy="75" r="22" stroke="#60a5fa"/><circle cx="70" cy="215" r="22" stroke="#60a5fa"/><circle cx="190" cy="55" r="22" stroke="#2dd4bf"/><circle cx="190" cy="145" r="22" stroke="#2dd4bf"/><circle cx="190" cy="235" r="22" stroke="#2dd4bf"/><circle cx="315" cy="95" r="22" stroke="#f59e0b"/><circle cx="315" cy="195" r="22" stroke="#f59e0b"/><circle cx="405" cy="145" r="24" stroke="#a78bfa"/></g>
  <g fill="#cbd5e1" style="font-size: 13px" text-anchor="middle"><text x="70" y="265">input</text><text x="190" y="275">hidden / diverse</text><text x="315" y="245">combine</text><text x="405" y="185">output</text></g>
</svg>
<div v-click class="mt-4" style="font-size: .9em" border="2 solid teal-800" bg="teal-800/20" rounded-lg px-4 py-3>

$$
h=\sigma(W_1x+b_1),\qquad \hat y=\sigma(W_2h+b_2)
$$

</div>
</div>
</div>

<!--
This is the resolution to XOR's impossibility. A multilayer perceptron (MLP) stacks a hidden layer between the input and the output: instead of one weighted sum, we compute several — h = σ(W₁x+b₁) produces a vector of "hidden unit" activations, where W₁ is now a matrix (one row of weights per hidden unit) and σ is a nonlinear activation function applied elementwise. Each hidden unit is itself a perceptron-like linear-plus-nonlinearity computing its own straight-line decision boundary in the input space, but a different one for each unit (different rows of W₁ give different lines). The output layer then computes ŷ = σ(W₂h+b₂), a second weighted sum that combines these hidden features — geometrically, it takes the hidden units' individual half-plane decisions and combines them into a nonlinear, non-convex decision region in the original input space, something no single line could ever represent. This is the key conceptual leap: depth does not add power by making the *same* kind of computation repeatedly, it adds power by letting each layer's output become the *input features* for the next layer, so the final boundary is built from combinations of simpler boundaries. Two slides from now we will write down the exact numeric weights that make this work for XOR specifically.
-->

---
glowSeed: 822
---

# Concrete Weights Solve XOR

<div class="grid grid-cols-2 gap-8 items-start">
<div>
<div class="text-sm opacity-85 mb-3">Two hidden units, each its own linear boundary, combined by the output unit:</div>
<div v-click border="2 solid teal-800" bg="teal-800/20" rounded-lg px-4 py-3 class="mb-2">
<span class="font-bold text-teal-300">$h_1 = \mathrm{OR}(x_1,x_2)$</span>
<span class="text-sm opacity-85 block mt-1">$h_1=\mathbf1[\,x_1+x_2-0.5\ge0\,]$</span>
</div>
<div v-click border="2 solid blue-800" bg="blue-800/20" rounded-lg px-4 py-3 class="mb-2">
<span class="font-bold text-blue-300">$h_2 = \mathrm{NAND}(x_1,x_2)$</span>
<span class="text-sm opacity-85 block mt-1">$h_2=\mathbf1[\,{-x_1-x_2}+1.5\ge0\,]$</span>
</div>
<div v-click border="2 solid amber-800" bg="amber-800/20" rounded-lg px-4 py-3>
<span class="font-bold text-amber-300">$\hat y = \mathrm{AND}(h_1,h_2)$</span>
<span class="text-sm opacity-85 block mt-1">$\hat y=\mathbf1[\,h_1+h_2-1.5\ge0\,]$</span>
</div>
</div>
<div class="text-sm opacity-85 mt-4">
<v-click>

Intuition: XOR is true exactly when "at least one input is on" ($h_1$) **and** "not both are on" ($h_2$). Neither $h_1$ nor $h_2$ alone solves XOR, but their conjunction does — this conjunction is precisely the nonlinear combining step the output unit performs.

</v-click>
</div>
</div>

<!--
Derive this rather than just presenting it. Notice that XOR(x1,x2) is logically equivalent to (x1 OR x2) AND NOT(x1 AND x2), i.e., "at least one is true, but not both." Define h1 as OR(x1,x2): it fires (outputs 1) whenever x1+x2 ≥ 1, which the threshold x1+x2-0.5≥0 captures (0.5 sits strictly between 0 and 1). Define h2 as NAND(x1,x2), the negation of AND: it fires whenever it is NOT the case that both inputs are 1, captured by -x1-x2+1.5≥0, which is only violated when x1=x2=1. Both h1 and h2 are individually linear boundaries — each is a valid perceptron — but neither alone solves XOR (OR is 1 on three of the four corners, NAND is 1 on three of the four corners). The output combines them with AND(h1,h2): fires only when both hidden units fire, using threshold h1+h2-1.5≥0, which needs h1=h2=1 exactly. Walk students through why this combination is exactly XOR: h1=1 and h2=1 together means "at least one input is on" and "not both are on," which is precisely the XOR condition. The next slide verifies this numerically, input by input.
-->

---
glowSeed: 823
---

# Forward Pass Verification

<div class="grid grid-cols-2 gap-8 items-start">
<div>
<div class="text-sm opacity-85 mb-2">Full forward pass for $x=(1,0)$, expected $y=1$:</div>
<div class="space-y-2 text-sm">
<div v-click border="2 solid white/5" bg="white/5" rounded-lg px-3 py-2>$z_{h_1}=1{+}0{-}0.5=0.5\ge0 \Rightarrow h_1=1$</div>
<div v-click border="2 solid white/5" bg="white/5" rounded-lg px-3 py-2>$z_{h_2}={-}1{-}0{+}1.5=0.5\ge0 \Rightarrow h_2=1$</div>
<div v-click border="2 solid white/5" bg="white/5" rounded-lg px-3 py-2>$z_{\hat y}=1{+}1{-}1.5=0.5\ge0 \Rightarrow \hat y=1$ ✓</div>
</div>
</div>
<div>
<table v-click class="text-sm w-full text-center border-separate mt-4" style="border-spacing: 4px">
<thead class="opacity-70"><tr><th>$x_1$</th><th>$x_2$</th><th>$h_1$</th><th>$h_2$</th><th>$\hat y$</th><th>$y$</th></tr></thead>
<tbody>
<tr><td border="1 solid white/10" p-1>0</td><td border="1 solid white/10" p-1>0</td><td border="1 solid white/10" p-1>0</td><td border="1 solid white/10" p-1>1</td><td border="1 solid white/10" p-1>0</td><td border="1 solid white/10" p-1>0</td></tr>
<tr><td border="1 solid white/10" p-1>0</td><td border="1 solid white/10" p-1>1</td><td border="1 solid white/10" p-1>1</td><td border="1 solid white/10" p-1>1</td><td border="1 solid white/10" p-1 class="text-teal-300 font-bold">1</td><td border="1 solid white/10" p-1>1</td></tr>
<tr><td border="1 solid white/10" p-1>1</td><td border="1 solid white/10" p-1>0</td><td border="1 solid white/10" p-1>1</td><td border="1 solid white/10" p-1>1</td><td border="1 solid white/10" p-1 class="text-teal-300 font-bold">1</td><td border="1 solid white/10" p-1>1</td></tr>
<tr><td border="1 solid white/10" p-1>1</td><td border="1 solid white/10" p-1>1</td><td border="1 solid white/10" p-1>1</td><td border="1 solid white/10" p-1>0</td><td border="1 solid white/10" p-1>0</td><td border="1 solid white/10" p-1>0</td></tr>
</tbody>
</table>
</div>
</div>

<!--
Walk the left-hand arithmetic slowly, since this is the deck's canonical worked forward pass. For x=(1,0): the first hidden unit computes z_h1 = 1·1 + 1·0 - 0.5 = 0.5, which is ≥0, so h1=1 (OR correctly fires since at least one input is on). The second hidden unit computes z_h2 = -1·1 + -1·0 + 1.5 = 0.5, also ≥0, so h2=1 (NAND correctly fires since not both inputs are on). The output layer then treats (h1,h2)=(1,1) as its own input: z_ŷ = 1·1 + 1·1 - 1.5 = 0.5 ≥ 0, so ŷ=1 — matching the expected XOR(1,0)=1. The right-hand table repeats this same three-line computation for all four inputs and confirms every prediction matches the true label; work through at least the (1,1) row aloud, since it's the one where h1=1 but h2=0, so the output computes 1+0-1.5=-0.5<0, giving ŷ=0, correctly matching XOR(1,1)=0. This concrete example is the existence proof that a two-layer network with step activations solves what a single perceptron provably cannot — the extra hidden layer is not a minor tweak, it is a qualitatively different, more expressive hypothesis class. A common misconception to correct here: students sometimes think you could train these exact weights with the plain perceptron learning rule applied end-to-end; you cannot, because that rule only knows how to update weights that connect directly to a unit with a known target, and the hidden units here have no directly observed target — computing appropriate hidden-layer updates is exactly the problem backpropagation solves, in our next lecture.
-->

---
glowSeed: 824
---

# Without Activations, Depth Collapses

<div class="grid grid-cols-2 gap-8 items-start">
<div>
<div class="space-y-3 mt-4">
<div v-click border="2 solid white/5" bg="white/5" rounded-lg px-4 py-3>
<span class="font-bold text-teal-300">Composition</span>
<span class="text-sm opacity-85"> — A stack of linear maps is still one linear map.</span>
</div>
<div v-click border="2 solid white/5" bg="white/5" rounded-lg px-4 py-3>
<span class="font-bold text-blue-300">No extra capacity</span>
<span class="text-sm opacity-85"> — More matrices alone cannot solve XOR.</span>
</div>
<div v-click border="2 solid white/5" bg="white/5" rounded-lg px-4 py-3>
<span class="font-bold text-amber-300">Essential ingredient</span>
<span class="text-sm opacity-85"> — A nonlinearity between layers prevents collapse.</span>
</div>
</div>
</div>
<div>
<div v-click class="mt-4" style="font-size: .9em" border="2 solid teal-800" bg="teal-800/20" rounded-lg px-4 py-3>

$$
W_2(W_1x)=(W_2W_1)x=W_{\mathrm{effective}}x
$$

</div>

</div>
</div>

<!--
Prove this algebraically before moving on, since it's the reason activation functions are non-negotiable. If a hidden layer had no nonlinearity — h = W₁x+b₁ with no σ — then the output would be ŷ = W₂h+b₂ = W₂(W₁x+b₁)+b₂ = (W₂W₁)x + (W₂b₁+b₂). Define W_effective = W₂W₁ and b_effective = W₂b₁+b₂: the whole two-layer computation reduces algebraically to a single matrix W_effective and a single bias b_effective, i.e., exactly one linear map, no matter how many layers you stack. This means an all-linear "deep" network has exactly the same representational power as a single-layer linear model — it can only ever produce a linear decision boundary, so it inherits the perceptron's XOR failure regardless of depth. The nonlinearity σ (step, sigmoid, ReLU, tanh — any of them) is what breaks this collapse: because σ(W₁x+b₁) cannot be rewritten as a single linear function of x, each additional nonlinear layer genuinely adds new representational capacity rather than just more parameters. Suggest verifying this numerically: pick random W₁, W₂, b₁, b₂, compute h=W₁x+b₁ and ŷ=W₂h+b₂ two ways (layer by layer, and via the collapsed W_effective, b_effective) and confirm np.allclose holds. Transition: given that nonlinear depth genuinely adds power, how much can it represent?
-->

---
glowSeed: 825
---

# Universal Approximation—with Important Caveats

<div class="grid grid-cols-2 gap-8 items-start">
<div>
<div class="space-y-3 mt-4">
<div v-click border="2 solid white/5" bg="white/5" rounded-lg px-4 py-3>
<span class="font-bold text-teal-300">Existence</span>
<span class="text-sm opacity-85"> — A wide enough hidden layer can approximate any continuous function on a bounded domain.</span>
</div>
<div v-click border="2 solid white/5" bg="white/5" rounded-lg px-4 py-3>
<span class="font-bold text-blue-300">Not a training guarantee</span>
<span class="text-sm opacity-85"> — The theorem does not say gradient descent will find those weights.</span>
</div>
<div v-click border="2 solid white/5" bg="white/5" rounded-lg px-4 py-3>
<span class="font-bold text-amber-300">Not a generalization guarantee</span>
<span class="text-sm opacity-85"> — Representing a function is not the same as learning it from finite data.</span>
</div>
</div>
</div>
<div>
<svg role="img" aria-label="Conceptual chart for Universal Approximation—with Important Caveats" viewBox="0 0 500 310" class="w-full max-w-xl mx-auto mt-7">
  <line x1="55" y1="260" x2="470" y2="260" stroke="#64748b" stroke-width="2"/><line x1="55" y1="35" x2="55" y2="260" stroke="#64748b" stroke-width="2"/>
  <path d="M60 235 C130 210,145 70,220 100 S320 210,465 55" fill="none" stroke="#2dd4bf" stroke-width="5"/>
  <path d="M60 245 C135 230,205 195,270 165 S385 110,465 95" fill="none" stroke="#60a5fa" stroke-width="4" stroke-dasharray="9 7"/>
  <g fill="#f59e0b"><circle cx="65" cy="230" r="6"/><circle cx="163" cy="185" r="6"/><circle cx="261" cy="110" r="6"/><circle cx="359" cy="150" r="6"/><circle cx="457" cy="65" r="6"/></g>
  <g fill="#cbd5e1" style="font-size: 12px" text-anchor="middle"><text x="65" y="285">2</text><text x="163" y="285">4</text><text x="261" y="285">8</text><text x="359" y="285">16</text><text x="457" y="285">32</text></g>
  <g style="font-size: 12px"><text x="335" y="42" fill="#5eead4">primary signal</text><text x="335" y="82" fill="#93c5fd">comparison</text></g>
</svg>

</div>
</div>

<!--
State the theorem precisely, then immediately undercut the popular oversimplification. The Universal Approximation Theorem (Cybenko 1989, Hornik 1991) says: a feedforward network with a single hidden layer, a nonlinear activation, and enough hidden units can approximate any continuous function on a compact (closed and bounded) domain to arbitrary accuracy. This is an existence result — it proves such weights exist, saying nothing about how many hidden units are "enough" (it can be astronomically large for complicated functions) and nothing about how to find them. Do not summarize this theorem as "networks can learn anything," which is the single most common misreading students bring into this course. Two caveats must be stated explicitly: first, the theorem says nothing about trainability — gradient descent (or the plain perceptron rule) is not guaranteed to discover the approximating weights even though they exist, and in practice optimization can get stuck or fail to find them; second, the theorem is about function representation on data you already have infinite access to, not about generalization — a network can perfectly represent a function and still generalize badly if trained on finite, noisy, or unrepresentative data (this is the overfitting problem from an earlier unit). The x-axis on the plot conceptually represents hidden-layer width; wider networks approximate the target function more closely, but width is not a free lunch — it also increases the risk of overfitting and the cost of training. Next, precise vocabulary for describing these architectures.
-->

---
glowSeed: 826
---

# Architecture Vocabulary

<div class="grid grid-cols-2 gap-8 items-start">
<div>
<div class="space-y-3 mt-4">
<div v-click border="2 solid white/5" bg="white/5" rounded-lg px-4 py-3>
<span class="font-bold text-teal-300">Input</span>
<span class="text-sm opacity-85"> — Raw features; no learned transformation.</span>
</div>
<div v-click border="2 solid white/5" bg="white/5" rounded-lg px-4 py-3>
<span class="font-bold text-blue-300">Hidden layers</span>
<span class="text-sm opacity-85"> — Linear maps plus nonlinear activations.</span>
</div>
<div v-click border="2 solid white/5" bg="white/5" rounded-lg px-4 py-3>
<span class="font-bold text-amber-300">Output</span>
<span class="text-sm opacity-85"> — Sigmoid, softmax, or linear activation matched to the task.</span>
</div>
<div v-click border="2 solid white/5" bg="white/5" rounded-lg px-4 py-3>
<span class="font-bold text-violet-300">Capacity</span>
<span class="text-sm opacity-85"> — Width counts units; depth counts learned layers.</span>
</div>
</div>
</div>
<div>
<svg role="img" aria-label="Network diagram for Architecture Vocabulary" viewBox="0 0 440 290" class="w-full max-w-xl mx-auto mt-8">
  <g stroke="#475569" stroke-width="2" opacity=".75">
    <line x1="70" y1="75" x2="190" y2="55"/><line x1="70" y1="75" x2="190" y2="145"/><line x1="70" y1="215" x2="190" y2="145"/><line x1="70" y1="215" x2="190" y2="235"/>
    <line x1="190" y1="55" x2="315" y2="95"/><line x1="190" y1="145" x2="315" y2="95"/><line x1="190" y1="145" x2="315" y2="195"/><line x1="190" y1="235" x2="315" y2="195"/>
    <line x1="315" y1="95" x2="405" y2="145"/><line x1="315" y1="195" x2="405" y2="145"/>
  </g>
  <g fill="#0f172a" stroke-width="4"><circle cx="70" cy="75" r="22" stroke="#60a5fa"/><circle cx="70" cy="215" r="22" stroke="#60a5fa"/><circle cx="190" cy="55" r="22" stroke="#2dd4bf"/><circle cx="190" cy="145" r="22" stroke="#2dd4bf"/><circle cx="190" cy="235" r="22" stroke="#2dd4bf"/><circle cx="315" cy="95" r="22" stroke="#f59e0b"/><circle cx="315" cy="195" r="22" stroke="#f59e0b"/><circle cx="405" cy="145" r="24" stroke="#a78bfa"/></g>
  <g fill="#cbd5e1" style="font-size: 13px" text-anchor="middle"><text x="70" y="265">input</text><text x="190" y="275">hidden / diverse</text><text x="315" y="245">combine</text><text x="405" y="185">output</text></g>
</svg>

</div>
</div>

<!--
Define every term precisely, since this vocabulary is used without re-explanation for the rest of the course. The input layer holds the raw feature vector — it performs no computation and has no learned weights of its own. Hidden layers sit between input and output; each is a linear map (a weight matrix and bias vector) followed elementwise by a nonlinear activation function, and "hidden" simply means we never directly observe or supervise their values during training — we only see the final output. The output layer's activation is chosen to match the task: sigmoid for binary classification (squashing to a single probability in (0,1)), softmax for multi-class classification (a vector of probabilities summing to 1), or no activation (linear) for regression, where unbounded real-valued outputs are needed. Capacity has two independent knobs: width, the number of units in a given layer (more units per layer means more distinct linear boundaries combined at that layer), and depth, the number of learned layers stacked (more layers means more stages of combining and recombining features). Work the arithmetic on the board: a dense layer mapping 20 input features to 64 hidden units has 20×64=1280 weights plus 64 biases, for 1344 learned parameters in that layer alone — this is exactly the parameter count Keras' model.summary() will report on the next slide's code. Next: turning this vocabulary into a runnable model.
-->

---
glowSeed: 827
---

# Build the Network

<div class="grid grid-cols-2 gap-4 mt-6">
<div v-click border="2 solid teal-800" bg="teal-800/20" rounded-lg p-4>
<div class="font-bold text-teal-300 mb-2">Two hidden layers</div>
<div class="text-sm leading-relaxed opacity-90">ReLU creates nonlinear features.</div>
</div>
<div v-click border="2 solid blue-800" bg="blue-800/20" rounded-lg p-4>
<div class="font-bold text-blue-300 mb-2">Binary output</div>
<div class="text-sm leading-relaxed opacity-90">Sigmoid returns a score in (0, 1).</div>
</div>
</div>

```python
import keras
from keras import layers

model = keras.Sequential([
    layers.Input(shape=(20,)),
    layers.Dense(64, activation="relu"),
    layers.Dense(32, activation="relu"),
    layers.Dense(1, activation="sigmoid"),
])
model.summary()
```

<!--
Map every line of this code to the diagram from the previous two slides. layers.Input(shape=(20,)) declares the input layer: 20 raw features, no computation. The first layers.Dense(64, activation="relu") is a hidden layer with 64 units, each computing a weighted sum of the 20 inputs (that's 20×64 weights plus 64 biases, 1344 parameters, matching the arithmetic from the last slide) followed by the ReLU nonlinearity, defined as ReLU(z)=max(0,z) — it zeroes out negative pre-activations and passes positive ones through unchanged, which is why it counts as the "nonlinearity" that prevents the depth-collapse from two slides ago despite being piecewise linear. The second Dense(32, activation="relu") is a second hidden layer, taking the 64 outputs of the first as its own 64 input features and producing 32 new features — this is depth, stacking learned representations on top of each other. The final Dense(1, activation="sigmoid") is the output layer: one unit, squashed to (0,1) with the sigmoid, appropriate for binary classification exactly as in logistic regression. Running model.summary() will print each layer's output shape and parameter count, letting students verify the 20×64+64=1344 figure directly against Keras' own accounting. Next: what happens once we call model.fit and need to update every one of these weights.
-->

---
glowSeed: 828
---

# From Architecture to Training

<div class="mt-8"><div class="grid grid-cols-3 gap-4 mt-6">
<div v-click border="2 solid teal-800" bg="teal-800/20" rounded-lg p-4>
<div class="font-bold text-teal-300 mb-2">Perceptron</div>
<div class="text-sm leading-relaxed opacity-90">One linear boundary.</div>
</div>
<div v-click border="2 solid blue-800" bg="blue-800/20" rounded-lg p-4>
<div class="font-bold text-blue-300 mb-2">MLP</div>
<div class="text-sm leading-relaxed opacity-90">Compose nonlinear layers.</div>
</div>
<div v-click border="2 solid amber-800" bg="amber-800/20" rounded-lg p-4>
<div class="font-bold text-amber-300 mb-2">Capacity</div>
<div class="text-sm leading-relaxed opacity-90">Width and depth matter.</div>
</div>
</div></div>

<div v-click class="mt-10 text-center text-lg" border="2 solid white/10" bg="white/5" rounded-lg px-6 py-4>Next: backpropagation computes every network gradient efficiently.</div>

<!--
Close by tying the whole deck together in one arc. We started with a single perceptron: one weighted sum, one hard threshold, one linear decision boundary, trainable by a simple online update rule that provably converges only when the data is linearly separable. We then hit a wall with XOR — a rigorous, geometric proof that no single linear boundary can separate its classes, regardless of how the perceptron rule is tuned. The fix was architectural, not algorithmic: stacking a hidden layer with a nonlinear activation between input and output, which we verified concretely by writing down exact weights that solve XOR and hand-tracing a forward pass through them. We confirmed the nonlinearity is essential (without it, any depth collapses algebraically to one linear map) and situated this in the Universal Approximation Theorem, with its important caveats about trainability and generalization that a single existence proof does not address. Architecture vocabulary — input, hidden, output, width, depth — gives us the language to describe any network we build going forward. What remains completely unanswered is *how* to find good weights for a network with hidden layers, since the plain perceptron rule has no way to assign credit or blame to units it cannot directly observe. That gap is exactly what backpropagation closes, and it's the subject of our next lecture. Take questions before moving on.
-->
