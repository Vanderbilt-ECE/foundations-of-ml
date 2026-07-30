---
theme: default
highlighter: shiki
css: unocss
colorSchema: dark
title: 'Activation Functions and Initialization'
info: |
  ## Activation Functions and Initialization
  Small choices that decide whether deep training succeeds
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
glowSeed: 850
---

# Activation Functions and Initialization

### Small choices that decide whether deep training succeeds

<div class="pt-8 opacity-80 text-lg">Neural Networks and Deep Learning Basics · Foundations of Machine Learning</div>

<div class="mt-14 flex justify-center gap-4" aria-hidden="true">
<div class="w-28 h-3 rounded-full bg-teal-400/70"></div>
<div class="w-20 h-3 rounded-full bg-blue-400/60"></div>
<div class="w-14 h-3 rounded-full bg-violet-400/50"></div>
</div>

<!--
Open by connecting this deck to the previous one: Perceptrons and Multilayer Networks introduced the architecture — layers of neurons computing z = Wx + b followed by a nonlinear activation f(z) — and showed that without f, depth is pointless because stacked linear maps collapse into one linear map. This deck asks two follow-up questions that decide whether a deep network actually trains. First, which nonlinearity f should each layer use, and what goes wrong with the classic choices (sigmoid, tanh)? Second, how should the weight matrices be initialized before training starts, since a bad starting scale can make even the right activation useless?

Roadmap for today: why nonlinearity matters at all → sigmoid and tanh saturation and the vanishing-gradient mechanism, walked through with an explicit numeric chain → ReLU and its dying-unit failure mode → a full worked example computing a forward and backward pass by hand through a tiny two-neuron network → why naive weight initialization fails → the variance-preservation argument behind Xavier/Glorot and He initialization, derived rather than just stated → practical pairings you will actually use. Next up after this deck is Backpropagation, which formalizes the chain-rule machinery this deck previews by hand.
-->

---
glowSeed: 851
---

# Why Nonlinearity Matters

<div class="grid grid-cols-2 gap-8 items-start mt-2">
<div>

<v-clicks>

- A layer computes $\mathbf{z} = W\mathbf{x}+\mathbf{b}$, then applies an **activation function** $f$ elementwise: $\mathbf{h}=f(\mathbf{z})$
- Stack two layers **without** an activation and the composition is still linear — depth buys nothing
- Only a **nonlinear** $f$ lets stacked layers draw curved decision boundaries and approximate complex functions
- This deck picks $f$ (activation) and the starting scale of $W$ (initialization) so that signal and gradient survive many layers

</v-clicks>

</div>
<div>

<div v-click border="2 solid teal-800" bg="teal-800/20" rounded-lg px-4 py-3 class="mt-4" style="font-size: .9em">

$$
\begin{aligned}
\mathbf{h} &= W_1\mathbf{x}+\mathbf{b}_1 \\
\mathbf{y} &= W_2\mathbf{h}+\mathbf{b}_2 = (W_2W_1)\mathbf{x} + (W_2\mathbf{b}_1+\mathbf{b}_2)
\end{aligned}
$$

</div>

<div v-click class="mt-4 text-sm opacity-85" border="2 solid white/5" bg="white/5" rounded-lg px-4 py-3>
The product $W_2W_1$ is just one matrix, and $W_2\mathbf{b}_1+\mathbf{b}_2$ is just one bias vector — two linear layers in a row are mathematically identical to a single linear layer. This is exactly why every hidden layer needs a nonlinear $f$ between the matrix multiplications.
</div>

</div>
</div>

<!--
Define terms first: an activation function f is a fixed, elementwise nonlinear function applied to a layer's pre-activation output z = Wx + b, producing the layer's output h = f(z). Walk the algebra in the card: if layer two is y = W2*h + b2 and h = W1*x + b1 with no activation in between, substituting gives y = (W2 W1)x + (W2 b1 + b2), which has the exact same form as a single linear layer z = W'x + b' with W' = W2 W1 and b' = W2 b1 + b2. This holds for any number of stacked linear layers — the whole network collapses to one matrix multiplication no matter how deep it is.

Common misconception: students often think "more layers always means more expressive power." That's only true once a nonlinearity separates the layers; without it, a 50-layer linear network is no more powerful than logistic regression on the raw inputs — it can only ever produce a linear function of x, so its decision boundary is always a straight line (or hyperplane). Sigmoid and tanh were the original nonlinear choices; the rest of this deck examines what breaks when you actually use them at depth, starting with sigmoid.
-->

---
glowSeed: 852
---

# Sigmoid Saturates

<div class="grid grid-cols-2 gap-8 items-start">
<div>
<div class="space-y-3 mt-4">
<div v-click border="2 solid white/5" bg="white/5" rounded-lg px-4 py-3>
<span class="font-bold text-teal-300">Derivative ceiling</span>
<span class="text-sm opacity-85"> — σ′(z) ≤ 0.25 everywhere.</span>
</div>
<div v-click border="2 solid white/5" bg="white/5" rounded-lg px-4 py-3>
<span class="font-bold text-blue-300">Flat tails</span>
<span class="text-sm opacity-85"> — Large |z| produces a derivative near zero.</span>
</div>
<div v-click border="2 solid white/5" bg="white/5" rounded-lg px-4 py-3>
<span class="font-bold text-amber-300">Deep product</span>
<span class="text-sm opacity-85"> — Repeated small derivatives shrink early-layer gradients exponentially.</span>
</div>
</div>
</div>
<div>
<svg role="img" aria-label="Conceptual chart for Sigmoid Saturates" viewBox="0 0 500 310" class="w-full max-w-xl mx-auto mt-7">
  <line x1="55" y1="260" x2="470" y2="260" stroke="#64748b" stroke-width="2"/><line x1="55" y1="35" x2="55" y2="260" stroke="#64748b" stroke-width="2"/>
  <path d="M60 235 C130 210,145 70,220 100 S320 210,465 55" fill="none" stroke="#2dd4bf" stroke-width="5"/>
  <path d="M60 245 C135 230,205 195,270 165 S385 110,465 95" fill="none" stroke="#60a5fa" stroke-width="4" stroke-dasharray="9 7"/>
  <g fill="#f59e0b"><circle cx="65" cy="230" r="6"/><circle cx="163" cy="185" r="6"/><circle cx="261" cy="110" r="6"/><circle cx="359" cy="150" r="6"/><circle cx="457" cy="65" r="6"/></g>
  <g fill="#cbd5e1" style="font-size: 12px" text-anchor="middle"><text x="65" y="285">−6</text><text x="163" y="285">−3</text><text x="261" y="285">0</text><text x="359" y="285">3</text><text x="457" y="285">6</text></g>
  <g style="font-size: 12px"><text x="335" y="42" fill="#5eead4">primary signal</text><text x="335" y="82" fill="#93c5fd">comparison</text></g>
</svg>
<div v-click class="mt-4" style="font-size: .9em" border="2 solid teal-800" bg="teal-800/20" rounded-lg px-4 py-3>

$$
\sigma(z)=\frac{1}{1+e^{-z}},\qquad \sigma'(z)=\sigma(z)(1-\sigma(z))
$$

</div>
</div>
</div>

<!--
Define sigmoid: σ(z) = 1/(1+e^{-z}) squashes any real number into (0, 1), which made it the natural choice for outputs interpreted as probabilities. Its derivative has a clean closed form, σ'(z) = σ(z)(1-σ(z)) — walk this: since σ(z) is between 0 and 1, the product σ(z)(1-σ(z)) is maximized when σ(z) = 0.5, i.e. at z = 0, giving σ'(0) = 0.5 × 0.5 = 0.25. That 0.25 is the ceiling — the derivative is never larger than 0.25 anywhere, and as |z| grows in either direction σ(z) approaches 0 or 1, so (1-σ(z)) or σ(z) approaches 0 and the derivative collapses toward zero. This flattening is called saturation: the curve on the right goes nearly flat for large |z|, so a neuron sitting in that regime gets almost no gradient signal no matter how wrong its output is.

Common misconception: students conflate "sigmoid saturates" with "sigmoid vanishes" — the function's *output* stays bounded in (0,1) and never vanishes; it is the *derivative* that shrinks toward zero in the tails, which is what actually damages learning. The 0.25 ceiling matters even more once you chain many layers together, because backpropagation multiplies these small derivatives layer after layer — the next slide makes that chain concrete with real numbers.
-->

---
glowSeed: 853
---

# The Vanishing Gradient Chain, Numerically

<div class="grid grid-cols-2 gap-8 items-start mt-2">
<div>

<v-clicks>

- Backprop through $L$ sigmoid layers multiplies $L-1$ derivative terms together
- Even at the **best case**, every factor is capped at $\sigma'(z)=0.25$
- Five layers of best-case multiplication already shrinks the gradient roughly a thousandfold
- Real networks rarely sit exactly at $z=0$, so the true shrinkage is usually worse than this best case

</v-clicks>

<div v-click border="2 solid teal-800" bg="teal-800/20" rounded-lg px-4 py-3 class="mt-4" style="font-size: .9em">

$$
\frac{\partial L}{\partial z^{(1)}} = \frac{\partial L}{\partial z^{(L)}}\prod_{l=2}^{L}\sigma'\!\left(z^{(l)}\right)
$$

</div>

</div>
<div class="flex flex-col gap-2 mt-4">

<div v-click border="2 solid teal-800" bg="teal-800/20" rounded-lg px-4 py-2 class="text-sm font-mono">0.25¹ = 0.25</div>
<div v-click border="2 solid blue-800" bg="blue-800/20" rounded-lg px-4 py-2 class="text-sm font-mono">0.25² = 0.0625</div>
<div v-click border="2 solid amber-800" bg="amber-800/20" rounded-lg px-4 py-2 class="text-sm font-mono">0.25³ = 0.015625</div>
<div v-click border="2 solid orange-800" bg="orange-800/20" rounded-lg px-4 py-2 class="text-sm font-mono">0.25⁴ ≈ 0.0039</div>
<div v-click border="2 solid red-800" bg="red-800/20" rounded-lg px-4 py-2 class="text-sm font-mono">0.25⁵ ≈ 0.001</div>

</div>
</div>

<!--
Walk the mechanism explicitly. The chain rule says the gradient reaching an early layer's pre-activation z^(1) equals the gradient at the last layer times the product of every intervening layer's local derivative — for a sigmoid network, each of those local factors is σ'(z^(l)), the same quantity from the previous slide, capped at 0.25. The right-hand list makes this concrete for a 6-layer network (5 multiplications between layer 1 and layer 6): even if every single layer happens to sit exactly at z=0 — the *most favorable* case, where the derivative is at its maximum of 0.25 — multiplying five of these together gives 0.25^5 = 0.0009765625, roughly one one-thousandth of the original gradient. That is the mathematical definition of a vanishing gradient: the update signal reaching early layers is thousands of times smaller than the signal reaching late layers, so early layers learn extremely slowly or appear to stop learning entirely.

Common misconception: students sometimes think vanishing gradients are a bug or an implementation error. They are not — they are the exact, correct output of the chain rule applied to a function whose derivative is bounded well below 1. This slide simplified by ignoring the weight-matrix factors that also appear in the true chain rule (∂z^(l)/∂z^(l-1) includes a weight matrix, not just σ'); those can partially offset or worsen the shrinkage, but the σ' factor alone is enough to explain why sigmoid and tanh networks historically struggled past a handful of layers. This single fact — bounded, sub-1 derivatives compounding through depth — is the entire motivation for ReRU-style activations, coming up in two slides. First, tanh, sigmoid's zero-centered cousin, which improves one problem but not this one.
-->

---
glowSeed: 854
---

# Tanh Helps, But Still Saturates

<div class="grid grid-cols-2 gap-8 items-start">
<div>
<div class="space-y-3 mt-4">
<div v-click border="2 solid white/5" bg="white/5" rounded-lg px-4 py-3>
<span class="font-bold text-teal-300">Zero-centered</span>
<span class="text-sm opacity-85"> — Outputs range from −1 to 1.</span>
</div>
<div v-click border="2 solid white/5" bg="white/5" rounded-lg px-4 py-3>
<span class="font-bold text-blue-300">Larger peak slope</span>
<span class="text-sm opacity-85"> — The derivative reaches 1 near zero.</span>
</div>
<div v-click border="2 solid white/5" bg="white/5" rounded-lg px-4 py-3>
<span class="font-bold text-amber-300">Same tail problem</span>
<span class="text-sm opacity-85"> — Large magnitudes still flatten the function.</span>
</div>
</div>
</div>
<div>
<div v-click class="mt-4" style="font-size: .9em" border="2 solid teal-800" bg="teal-800/20" rounded-lg px-4 py-3>

$$
\begin{aligned}\tanh(z)&=2\sigma(2z)-1\\\tanh'(z)&=1-\tanh^2(z)\end{aligned}
$$

</div>

<div v-click class="mt-4 text-sm opacity-85" border="2 solid white/5" bg="white/5" rounded-lg px-4 py-3>
At $z=0$: $\tanh'(0)=1-0^2=1$, four times sigmoid's ceiling of $0.25$ — a real improvement, but a chain of $\tanh'$ factors below 1 still shrinks toward zero as depth grows.
</div>

</div>
</div>

<!--
Define tanh as a rescaled, shifted sigmoid: tanh(z) = 2σ(2z) - 1, which maps any real z into (-1, 1) instead of (0, 1). Zero-centered means the average output across many inputs tends toward zero rather than always being positive like sigmoid's — this matters because when a layer's outputs are all positive, the gradient updates to that layer's incoming weights are constrained to move in a consistent direction on every dimension (a "zig-zagging" convergence pattern), which tanh avoids. Its derivative, tanh'(z) = 1 - tanh(z)^2, peaks at z=0 where tanh(0)=0, giving tanh'(0) = 1, four times sigmoid's peak of 0.25 — this genuinely slows down vanishing gradients relative to sigmoid.

Common misconception: "tanh solves vanishing gradients" — it does not, it only postpones the problem. As |z| grows, tanh(z) approaches ±1 just as sigmoid approaches 0 or 1, so tanh'(z) approaches 1 - 1 = 0 in exactly the same saturating way. Chain five tanh layers all sitting away from zero and the gradient still shrinks toward zero, just more slowly than the sigmoid case. Because both classic S-shaped activations saturate in their tails, the field moved toward activations with a derivative that never decays at all on one side — ReLU, next.
-->

---
glowSeed: 855
---

# ReLU Is the Modern Default

<div class="grid grid-cols-2 gap-8 items-start">
<div>
<div class="space-y-3 mt-4">
<div v-click border="2 solid white/5" bg="white/5" rounded-lg px-4 py-3>
<span class="font-bold text-teal-300">Simple</span>
<span class="text-sm opacity-85"> — One max operation.</span>
</div>
<div v-click border="2 solid white/5" bg="white/5" rounded-lg px-4 py-3>
<span class="font-bold text-blue-300">Positive side</span>
<span class="text-sm opacity-85"> — Derivative is exactly 1, so it does not saturate there.</span>
</div>
<div v-click border="2 solid white/5" bg="white/5" rounded-lg px-4 py-3>
<span class="font-bold text-amber-300">Scale</span>
<span class="text-sm opacity-85"> — Cheap enough for enormous numbers of activations.</span>
</div>
</div>
</div>
<div>
<div v-click class="mt-4" style="font-size: .9em" border="2 solid teal-800" bg="teal-800/20" rounded-lg px-4 py-3>

$$
\mathrm{ReLU}(z)=\max(0,z),\qquad \mathrm{ReLU}'(z)=\mathbf1[z>0]
$$

</div>

</div>
</div>

<!--
Define ReLU (Rectified Linear Unit): ReLU(z) = max(0, z), which simply passes positive inputs through unchanged and zeroes out negative inputs. Its derivative is a step function, ReLU'(z) = 1 if z>0 and 0 if z<0 (undefined exactly at z=0, conventionally taken as 0 or 1 in practice — it rarely matters). Compare this to the previous two slides: for any z>0, no matter how large, the derivative is exactly 1, not a shrinking fraction. Chain five ReLU layers together where every unit is active (z>0) and the product of derivatives is 1×1×1×1×1=1 — the gradient passes through completely undiminished, which is precisely what sigmoid and tanh could never do.

Also worth naming: ReLU is cheap to compute (one comparison, no exponential), which matters when a layer has thousands of units and a network has many layers — this computational simplicity, on top of solving the positive-side vanishing-gradient problem, is why ReLU became the default hidden-layer activation soon after AlexNet (2012) demonstrated it at scale. Common misconception: students sometimes think ReLU "fixes" vanishing gradients everywhere. It only fixes the positive side. For z<0, ReLU'(z)=0 exactly — not small, but zero — which creates its own, different failure mode: a unit that always outputs zero receives zero gradient forever and cannot recover through gradient descent alone. That "dying ReLU" problem, and its fix, is next.
-->

---
glowSeed: 856
---

# Dying ReLU and Leaky ReLU

<div class="grid grid-cols-3 gap-4 mt-6">
<div v-click border="2 solid teal-800" bg="teal-800/20" rounded-lg p-4>
<div class="font-bold text-teal-300 mb-2">Dying ReLU</div>
<div class="text-sm leading-relaxed opacity-90">A unit that stays negative outputs zero and receives zero gradient forever — no update can ever revive it.</div>
</div>
<div v-click border="2 solid blue-800" bg="blue-800/20" rounded-lg p-4>
<div class="font-bold text-blue-300 mb-2">Leaky ReLU</div>
<div class="text-sm leading-relaxed opacity-90">A small negative-side slope keeps a nonzero gradient, so the unit can still update.</div>
</div>
<div v-click border="2 solid amber-800" bg="amber-800/20" rounded-lg p-4>
<div class="font-bold text-amber-300 mb-2">Minimal fix</div>
<div class="text-sm leading-relaxed opacity-90">The tiny slope 0.01 is enough to let a "dead" unit recover, at almost no extra compute.</div>
</div>
</div>
<div v-click class="mt-4" style="font-size: .9em" border="2 solid teal-800" bg="teal-800/20" rounded-lg px-4 py-3>

$$
f(z)=\begin{cases}z&z>0\\0.01z&z\le0\end{cases}
$$

</div>

<!--
Walk the failure mode precisely: because ReLU'(z)=0 for every z<0, if a training step ever pushes a unit's incoming weights and bias so that its pre-activation z is negative for every example in the training set, that unit outputs zero for every input, its gradient with respect to its own weights is zero for every input (since the chain rule multiplies by ReLU'(z)=0), and no future gradient step can ever change its weights again — it has permanently "died." This is not a hypothetical: large learning rates and unlucky initialization can silently kill a meaningful fraction of a network's ReLU units, wasting capacity without any visible error.

Leaky ReLU's fix is the smallest possible change: replace the flat zero on the negative side with a very small nonzero slope, conventionally 0.01, so f(z)=z for z>0 and f(z)=0.01z for z≤0. Now the derivative on the negative side is 0.01, not 0 — tiny, but nonzero — so gradient still flows back through a "leaky" unit and its weights can keep updating, giving it a path back to positive territory. Common misconception: Leaky ReLU does not eliminate small gradients, it eliminates permanently zero gradients — the tradeoff is a small, controlled shrinkage (like sigmoid's, but a fixed 0.01 rather than something that varies with z) in exchange for units that can never fully die. Having covered how the choice of f shapes gradient flow, make it concrete: the next two slides compute an actual forward and backward pass, by hand, through a tiny sigmoid network.
-->

---
glowSeed: 857
---

# Worked Example — Forward Pass by Hand

<div class="text-sm opacity-85 mt-2">Two inputs, two sigmoid hidden units, one sigmoid output unit, target $y=1$.</div>

<div class="grid grid-cols-2 gap-8 items-start mt-4">
<div>

| Quantity | Value |
|---|---|
| $x_1,\ x_2$ | $1.0,\ 0.5$ |
| $W^{(1)}$ row 1 (to $h_1$) | $0.5,\ {-0.3}$, bias $0.1$ |
| $W^{(1)}$ row 2 (to $h_2$) | $0.2,\ 0.4$, bias $-0.1$ |
| $W^{(2)}$ (to output) | $0.6,\ {-0.5}$, bias $0.2$ |

</div>
<div>

<v-clicks>

- $z_1 = 0.5(1.0)-0.3(0.5)+0.1 = 0.45 \Rightarrow h_1=\sigma(0.45)\approx0.611$
- $z_2 = 0.2(1.0)+0.4(0.5)-0.1 = 0.30 \Rightarrow h_2=\sigma(0.30)\approx0.574$
- $z_{out}=0.6(0.611)-0.5(0.574)+0.2\approx0.279 \Rightarrow \hat y=\sigma(0.279)\approx0.569$
- Loss (binary cross-entropy, $y=1$): $L=-\ln(0.569)\approx0.563$

</v-clicks>

</div>
</div>

<!--
This example makes every abstract formula from the last five slides concrete with real numbers, so nothing about sigmoid or the chain rule remains hypothetical. Setup: two inputs x1=1.0, x2=0.5 feed a hidden layer of two sigmoid neurons, whose outputs h1, h2 feed a single sigmoid output neuron producing a predicted probability ŷ, compared against a true binary label y=1 via binary cross-entropy loss L=-ln(ŷ) (the standard loss for a single-probability target of 1).

Walk each line. For h1: z1 = W1_11·x1 + W1_12·x2 + b1_1 = 0.5(1.0) + (-0.3)(0.5) + 0.1 = 0.5 - 0.15 + 0.1 = 0.45, then h1 = σ(0.45) = 1/(1+e^{-0.45}) ≈ 0.611 using the sigmoid definition from three slides ago. For h2: z2 = 0.2(1.0) + 0.4(0.5) - 0.1 = 0.2+0.2-0.1 = 0.30, h2 = σ(0.30) ≈ 0.574. The output combines both hidden activations: z_out = 0.6(0.611) - 0.5(0.574) + 0.2 ≈ 0.366 - 0.287 + 0.2 = 0.279, ŷ = σ(0.279) ≈ 0.569. Finally the loss for a target of 1 is simply -ln(ŷ) ≈ 0.563 — a moderate loss, since the network predicted 0.569 when it should have predicted close to 1.

Every number here will be reused on the next slide to compute the gradient by hand, so keep them visible. That backward pass is where the σ'(z)≤0.25 ceiling from the sigmoid derivation shows up as an actual multiplier on real numbers, not just an abstract bound.
-->

---
glowSeed: 858
---

# Worked Example — Backward Pass by Hand

<div class="text-sm opacity-85 mt-2">Same network, same numbers. Watch the sigmoid derivative shrink the signal at each step.</div>

<div class="grid grid-cols-2 gap-8 items-start mt-4">
<div>

<v-clicks>

- Output error: $\dfrac{\partial L}{\partial z_{out}}=\hat y-y = 0.569-1=-0.431$
- Weight gradients: $\dfrac{\partial L}{\partial W^{(2)}_1}=-0.431(0.611)\approx-0.263$, $\dfrac{\partial L}{\partial W^{(2)}_2}=-0.431(0.574)\approx-0.247$
- Back to $h_1$: $\dfrac{\partial L}{\partial h_1}=-0.431(0.6)=-0.258$
- Through $\sigma'$: $\sigma'(0.45)=0.611(0.389)\approx0.238$, so $\dfrac{\partial L}{\partial z_1}=-0.258(0.238)\approx-0.061$

</v-clicks>

</div>
<div>

<div v-click border="2 solid amber-800" bg="amber-800/20" rounded-lg px-4 py-3 class="text-sm">
Only one sigmoid layer separates $z_1$ from the output, and the signal already shrank from $-0.431$ to $-0.061$ — a factor of about $0.238$, right at the $\sigma'\le0.25$ ceiling from two slides ago. Stack a few more sigmoid layers and this compounds toward zero exactly as the numeric chain predicted.
</div>

</div>
</div>

<!--
Continue directly from the forward pass. The output layer uses sigmoid activation with cross-entropy loss, which has a famously clean combined derivative: ∂L/∂z_out = ŷ - y = 0.569 - 1 = -0.431 (this shortcut — output-minus-target — only holds for this exact sigmoid+cross-entropy pairing, worth flagging so students don't assume it generalizes to other loss/activation combinations). The gradient with respect to each output weight is this error times the corresponding hidden activation: ∂L/∂W2_1 = -0.431 × h1 = -0.431×0.611 ≈ -0.263, and ∂L/∂W2_2 = -0.431×0.574 ≈ -0.247 — these are the numbers a gradient-descent step would actually subtract (times a learning rate) from W2.

Now propagate backward into the hidden layer, which is where the vanishing-gradient mechanism becomes visible in real numbers rather than abstract bounds. First take ∂L/∂h1 = (∂L/∂z_out)×W2_1 = -0.431×0.6 = -0.258 (the chain rule through the linear combination). Then multiply by the local sigmoid derivative at h1's own pre-activation: σ'(0.45) = h1(1-h1) = 0.611×0.389 ≈ 0.238 — notice this sits close to, but below, the theoretical ceiling of 0.25 established earlier, because z1=0.45 is close to but not exactly 0. Multiplying gives ∂L/∂z1 = -0.258×0.238 ≈ -0.061: the gradient shrank by roughly a factor of 4 crossing just one sigmoid layer. This is the exact mechanism from the numeric-chain slide, now applied to a real network instead of an idealized 0.25 constant.

Common misconception: students sometimes think backprop is a separate algorithm from calculus. It is not — every line above is a direct application of the multivariable chain rule; the Backpropagation deck that follows this one names and systematizes exactly this bookkeeping across arbitrarily many layers. Having seen sigmoid's gradient shrinkage in concrete numbers, the deck now turns to the other half of the training-success problem: even with a good activation function, a bad starting weight scale can sabotage training before it begins.
-->

---
glowSeed: 859
---

# Naive Initialization Fails Two Ways

<div class="grid grid-cols-2 gap-8 items-start">
<div>
<div class="space-y-3 mt-4">
<div v-click border="2 solid white/5" bg="white/5" rounded-lg px-4 py-3>
<span class="font-bold text-teal-300">All zeros</span>
<span class="text-sm opacity-85"> — Every unit in a layer computes the same output and receives the same gradient forever.</span>
</div>
<div v-click border="2 solid white/5" bg="white/5" rounded-lg px-4 py-3>
<span class="font-bold text-blue-300">No specialization</span>
<span class="text-sm opacity-85"> — Symmetric units stay symmetric across every update; many neurons behave as one.</span>
</div>
<div v-click border="2 solid amber-800" bg="amber-800/20" rounded-lg px-4 py-3>
<span class="font-bold text-amber-300">Too-large random</span>
<span class="text-sm opacity-85"> — Large weights push $z$ into sigmoid/tanh's flat tails immediately, saturating before training starts.</span>
</div>
<div v-click border="2 solid red-800" bg="red-800/20" rounded-lg px-4 py-3>
<span class="font-bold text-red-300">Too-small random</span>
<span class="text-sm opacity-85"> — Tiny weights shrink activations toward zero at every layer, vanishing before any signal reaches the output.</span>
</div>
</div>
</div>
<div>
<svg role="img" aria-label="Network diagram for Naive Initialization Fails" viewBox="0 0 440 290" class="w-full max-w-xl mx-auto mt-8">
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
Two separate failure modes live under "bad initialization." First, initializing every weight to zero (or any single constant): every hidden unit in a layer receives the same weighted sum of inputs, so every unit outputs an identical value; by the chain rule, every unit's gradient during backprop is then also identical, so a gradient-descent update changes every unit's weights by the exact same amount — the layer stays perfectly symmetric forever, so a "hidden layer" of 100 identical units has the actual representational capacity of one unit. This is why random initialization exists at all: randomness breaks the symmetry so different units can drift apart and specialize, which is the diverse-hidden-layer picture in the diagram (teal circles ending up different, not identical).

Second, and this is the failure mode naive *random* init still has: the *scale* of the random weights matters enormously, independent of symmetry-breaking. Draw weights from, say, a standard normal N(0,1) with many inputs summed together, and the pre-activation z = Σ w_i x_i can easily land far from zero — with a sigmoid or tanh activation, that pushes many units straight into the flat, saturating tails from three slides ago, killing gradient flow from the very first forward pass. Draw weights that are too small instead, and z stays near zero at every layer, so the layer's output variance shrinks each time it passes through — after enough layers the signal itself is indistinguishable from zero. Common misconception: "just use small random numbers" is not a complete answer — too small has its own vanishing problem, symmetrically opposite to too large. The right scale is not arbitrary; it can be derived from a variance-preservation argument, which is exactly what the next slide works out.
-->

---
glowSeed: 860
---

# Why Preserve Variance Across Layers

<div class="mt-2">

Consider one linear neuron summing $n$ inputs with independent, zero-mean weights and inputs: $y=\sum_{i=1}^n w_i x_i$.

</div>

<div v-click border="2 solid teal-800" bg="teal-800/20" rounded-lg px-4 py-3 class="mt-4" style="font-size: .95em">

$$
\begin{aligned}
\operatorname{Var}(y) &= \sum_{i=1}^n \operatorname{Var}(w_i x_i) = \sum_{i=1}^n \operatorname{Var}(w_i)\operatorname{Var}(x_i) \\
&= n\,\operatorname{Var}(w)\operatorname{Var}(x)
\end{aligned}
$$

</div>

<div v-click class="mt-4 grid grid-cols-2 gap-6">
<div border="2 solid blue-800" bg="blue-800/20" rounded-lg px-4 py-3 class="text-sm">
<span class="font-bold text-blue-300">Preserve signal:</span> require $\operatorname{Var}(y)=\operatorname{Var}(x)$, so $n\operatorname{Var}(w)=1 \Rightarrow \operatorname{Var}(w)=\dfrac{1}{n}$
</div>
<div border="2 solid amber-800" bg="amber-800/20" rounded-lg px-4 py-3 class="text-sm">
<span class="font-bold text-amber-300">Too big or small:</span> $\operatorname{Var}(w)>1/n$ grows layer to layer; $\operatorname{Var}(w)<1/n$ shrinks it — both compound with depth
</div>
</div>

<!--
This derivation is the mathematical justification behind Xavier and He initialization — not a formula to memorize, but a consequence of one clean assumption. Model one neuron's pre-activation as y = Σ w_i x_i, a sum of n independent products, where each weight w_i and input x_i are independent of each other and have zero mean (a reasonable idealization at initialization, before training has correlated anything). For two independent, zero-mean random variables, Var(w_i x_i) = E[w_i²x_i²] - (E[w_i x_i])² = E[w_i²]E[x_i²] - 0 = Var(w_i)Var(x_i) — this is the key algebraic step, using independence to factor the expectation of the product into a product of expectations, and zero mean to make the E[w_i x_i] term vanish. Summing n such independent, identically-distributed terms gives Var(y) = n·Var(w)·Var(x), because variances of independent variables add.

Now the design decision: we want each layer to neither amplify nor shrink the signal's spread as it passes through, i.e. Var(y) = Var(x), so that after many layers the activations stay in a sane numeric range rather than exploding or collapsing to zero — exactly the failure modes named on the previous slide. Setting n·Var(w) = 1 gives Var(w) = 1/n: the variance each weight is drawn from should scale inversely with the number of inputs it sums over. This single equation, Var(w)=1/n, is the entire idea behind "principled" initialization — it is not a magic constant, it is the unique choice that keeps variance constant layer over layer under this model. The next slide turns this one condition into the two named schemes — Xavier/Glorot and He — that practitioners actually use, adapting the fan-in count n and adding a correction for ReLU's asymmetry.
-->

---
glowSeed: 861
---

# Xavier and He Initialization

<div class="grid grid-cols-2 gap-8 items-start">
<div>
<div class="space-y-3 mt-4">
<div v-click border="2 solid white/5" bg="white/5" rounded-lg px-4 py-3>
<span class="font-bold text-teal-300">Xavier / Glorot</span>
<span class="text-sm opacity-85"> — Averages fan-in $n_{in}$ and fan-out $n_{out}$; matched to tanh/sigmoid-like activations.</span>
</div>
<div v-click border="2 solid white/5" bg="white/5" rounded-lg px-4 py-3>
<span class="font-bold text-blue-300">He</span>
<span class="text-sm opacity-85"> — Uses $2/n_{in}$: ReLU zeroes about half its inputs, so the surviving half needs twice the variance to compensate.</span>
</div>
<div v-click border="2 solid amber-800" bg="amber-800/20" rounded-lg px-4 py-3>
<span class="font-bold text-amber-300">Goal</span>
<span class="text-sm opacity-85"> — Both satisfy the $\operatorname{Var}(w)\approx1/n$ condition derived on the previous slide, adapted per activation.</span>
</div>
</div>
</div>
<div>
<div v-click class="mt-4" style="font-size: .9em" border="2 solid teal-800" bg="teal-800/20" rounded-lg px-4 py-3>

$$
\operatorname{Var}(W_{\mathrm{Xavier}})\approx\frac{2}{n_{in}+n_{out}},\qquad \operatorname{Var}(W_{\mathrm{He}})=\frac{2}{n_{in}}
$$

</div>

</div>
</div>

<!--
Connect directly back to the derivation: the previous slide showed Var(w)=1/n keeps a linear neuron's output variance equal to its input variance, where n is the number of inputs it sums (the fan-in). Xavier/Glorot initialization (Glorot & Bengio, 2010) refines this for a full network by requiring variance preservation in *both* directions — forward through the layer (which depends on fan-in n_in) and backward through the gradient (which depends on fan-out n_out, the number of units the next layer feeds into) — and uses the harmonic-style average Var(W) ≈ 2/(n_in+n_out) as a compromise satisfying both approximately. It is matched to sigmoid and tanh because those activations are roughly linear (derivative near 1) close to z=0, which is exactly where the variance argument's linear-neuron assumption is most accurate.

He initialization (He et al., 2015) adapts the same 1/n idea for ReLU. Walk why the factor becomes 2/n_in rather than 1/n_in: ReLU zeroes out roughly half of its inputs (every unit with z<0 becomes exactly 0), so on average only about half the variance computed by the plain linear-neuron argument actually survives into the next layer's inputs. To compensate for this halving, He initialization doubles the variance the weights are drawn from, giving Var(W) = 2/n_in — the derivation is the same variance-preservation logic as Xavier, just with a correction for ReLU's asymmetric zeroing. Common misconception: these are not competing "tricks" to try at random; the choice is dictated by which activation the layer uses — the derivation on the previous slide is a general principle, and Xavier vs. He is just which activation-specific correction to apply to it. With activation and initialization both chosen correctly, the next slide turns this into concrete pairings for real network layers.
-->

---
glowSeed: 862
---

# Practical Pairings

<div class="grid grid-cols-2 gap-4 mt-6">
<div v-click border="2 solid teal-800" bg="teal-800/20" rounded-lg p-4>
<div class="font-bold text-teal-300 mb-2">Hidden layers</div>
<div class="text-sm leading-relaxed opacity-90">ReLU or Leaky ReLU with He initialization.</div>
</div>
<div v-click border="2 solid blue-800" bg="blue-800/20" rounded-lg p-4>
<div class="font-bold text-blue-300 mb-2">Binary output</div>
<div class="text-sm leading-relaxed opacity-90">Sigmoid.</div>
</div>
<div v-click border="2 solid amber-800" bg="amber-800/20" rounded-lg p-4>
<div class="font-bold text-amber-300 mb-2">Multiclass output</div>
<div class="text-sm leading-relaxed opacity-90">Softmax.</div>
</div>
<div v-click border="2 solid violet-800" bg="violet-800/20" rounded-lg p-4>
<div class="font-bold text-violet-300 mb-2">Regression output</div>
<div class="text-sm leading-relaxed opacity-90">Linear activation.</div>
</div>
</div>


<!--
Turn the last six slides into a decision rule practitioners actually use. Hidden layers: default to ReLU (or Leaky ReLU if dead units are observed in practice) paired with He initialization, because the derivative-1 positive side avoids the sigmoid/tanh vanishing-gradient chain from earlier, and He's Var(W)=2/n_in keeps the resulting activations from exploding or collapsing across many stacked layers. Output layers are chosen by the *task*, not by the vanishing-gradient concern that drove the hidden-layer choice, because there is only one output layer — saturation risk there matters far less than getting the right output range: sigmoid squashes to (0,1) for a single probability (binary classification), softmax generalizes this to a probability distribution over multiple mutually exclusive classes (multiclass classification), and a plain linear activation (no squashing at all) is used for regression, where the target is an unbounded real number and forcing it through a bounded activation would make certain target values unreachable.

Common misconception: students sometimes assume ReLU should be used everywhere, including the output layer. That would be wrong for classification — ReLU's unbounded positive range does not represent a probability, so cross-entropy loss requires sigmoid or softmax specifically at the output. Keras/PyTorch defaults follow exactly this table, and now the reasoning behind each choice — saturation, dead units, and variance-preserving initialization — is visible rather than memorized. Having covered the individual pieces, the closing slide ties activation choice and initialization together as one coupled design decision, not two separate ones.
-->

---
glowSeed: 863
---

# Make Gradients Flow

<div class="mt-8"><div class="grid grid-cols-3 gap-4 mt-6">
<div v-click border="2 solid teal-800" bg="teal-800/20" rounded-lg p-4>
<div class="font-bold text-teal-300 mb-2">Avoid saturation</div>
<div class="text-sm leading-relaxed opacity-90">Prefer ReLU-family hidden units — derivative is 1 on the active side, not a shrinking fraction.</div>
</div>
<div v-click border="2 solid blue-800" bg="blue-800/20" rounded-lg p-4>
<div class="font-bold text-blue-300 mb-2">Break symmetry</div>
<div class="text-sm leading-relaxed opacity-90">Never initialize all weights equally — random draws let units specialize.</div>
</div>
<div v-click border="2 solid amber-800" bg="amber-800/20" rounded-lg p-4>
<div class="font-bold text-amber-300 mb-2">Control scale</div>
<div class="text-sm leading-relaxed opacity-90">Use Xavier or He so signal variance survives, layer after layer.</div>
</div>
</div></div>

<div v-click class="mt-10 text-center text-lg" border="2 solid white/10" bg="white/5" rounded-lg px-6 py-4>Next: Backpropagation formalizes the by-hand gradient chain from this deck into one general algorithm.</div>

<!--
Close by tying the three pillars together as one coupled decision, not three independent ones: the activation function determines whether the derivative multiplied at every layer during backprop stays near 1 (ReLU-family, avoiding saturation) or shrinks toward 0 (sigmoid/tanh in their tails); initialization determines two separate things — random values break the symmetry that would otherwise make an entire layer of units behave as one, and the *variance* of those random values, set by Xavier or He, determines whether activations and gradients stay at a stable scale across many layers rather than exploding or vanishing before training even gets going. Get any one of these three wrong and the other two cannot compensate: perfect initialization cannot fix a saturating activation, and the best activation cannot fix symmetric zero weights.

Recap the throughline of the whole deck: sigmoid's derivative is capped at 0.25 and multiplying several such factors compounds toward zero (shown numerically as 0.25^5 ≈ 0.001, then again on real numbers in the worked backward pass); ReLU fixes the positive side by making the derivative exactly 1, at the cost of units that can die permanently on the negative side, which Leaky ReLU patches with a small nonzero slope; and initialization scale is not arbitrary but follows directly from requiring Var(w)=1/n so that a layer's output variance matches its input variance, adapted into Xavier for tanh/sigmoid and He for ReLU. The next deck, Backpropagation, takes the by-hand chain-rule bookkeeping from the worked example in this deck and generalizes it into the single recursive algorithm used to train networks of any depth — take questions before moving on.
-->

---
layout: center
class: text-center
glowSeed: 864
---

# Thank You

### Questions &amp; Discussion

<div class="pt-6 opacity-80">
Activation Functions and Initialization · Neural Networks and Deep Learning Basics
</div>

<!--
Take questions before moving to Backpropagation, which formalizes the by-hand forward and backward pass computed earlier in this deck into a single recursive algorithm that scales to networks of arbitrary depth and width.
-->
