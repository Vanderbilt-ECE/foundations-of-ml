---
theme: default
highlighter: shiki
css: unocss
colorSchema: dark
title: 'Backpropagation'
info: |
  ## Backpropagation
  The chain rule, organized and reused at scale
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
glowSeed: 830
---

# Backpropagation

### The chain rule, organized and reused at scale

<div class="pt-8 opacity-80 text-lg">Neural Networks and Deep Learning Basics · Foundations of Machine Learning</div>

<div class="mt-14 flex justify-center gap-4" aria-hidden="true">
<div class="w-28 h-3 rounded-full bg-teal-400/70"></div>
<div class="w-20 h-3 rounded-full bg-blue-400/60"></div>
<div class="w-14 h-3 rounded-full bg-violet-400/50"></div>
</div>

<!--
Backpropagation is the algorithm that makes training neural networks computationally possible. The previous units built a forward-propagating network: inputs flow through layers of weighted sums and nonlinear activations to produce a prediction, and a loss function scores how wrong that prediction is. Training means adjusting every weight to reduce the loss, which requires the gradient of the loss with respect to every weight in the network — potentially millions of numbers.

Today's roadmap: first, why naively computing that gradient is too expensive to be practical. Second, the computational graph as the right mental model for any composed function. Third, a small concrete network — two inputs, two hidden neurons, two outputs — where we compute a full forward pass and a full backward pass by hand with real numbers, deriving every gradient from the chain rule rather than quoting a formula. Fourth, why this "reverse-mode" strategy is asymptotically cheaper than the naive alternative, and how it generalizes into the automatic differentiation engines inside PyTorch and TensorFlow. By the end, "backprop" should mean a specific, reproducible arithmetic procedure, not a magic phrase.
-->

---
glowSeed: 831
---

# Why Backpropagation? The Naive Alternative Is Too Slow

<div class="grid grid-cols-2 gap-8 items-start mt-4">
<div class="space-y-3">
<div v-click border="2 solid white/5" bg="white/5" rounded-lg px-4 py-3>
<span class="font-bold text-teal-300">The goal</span>
<span class="text-sm opacity-85"> — Compute $\partial L/\partial w$ for every weight $w$ in the network.</span>
</div>
<div v-click border="2 solid white/5" bg="white/5" rounded-lg px-4 py-3>
<span class="font-bold text-blue-300">Finite differences</span>
<span class="text-sm opacity-85"> — Perturb one weight, rerun the forward pass, measure the change in loss.</span>
</div>
<div v-click border="2 solid white/5" bg="white/5" rounded-lg px-4 py-3>
<span class="font-bold text-amber-300">The cost</span>
<span class="text-sm opacity-85"> — One extra forward pass <em>per weight</em>, every training step.</span>
</div>
</div>
<div v-click class="mt-2 text-sm" border="2 solid teal-800" bg="teal-800/20" rounded-lg px-4 py-3>

$$
\frac{\partial L}{\partial w_i} \approx \frac{L(w_i+\epsilon) - L(w_i)}{\epsilon}
$$

A network with a million weights needs roughly a million extra forward passes to estimate one gradient this way — for every single update step.

</div>
</div>

<!--
This slide motivates why backpropagation exists at all. A neural network with n weights, trained by gradient descent, needs the gradient of the loss with respect to every one of those n weights at every step. The most naive way to estimate a partial derivative numerically is finite differences: nudge one weight by a small epsilon, rerun the entire forward pass, see how much the loss changed, and divide. That single formula is correct, but doing it for every weight means rerunning the whole forward pass n times per gradient step — for a modern network with millions or billions of parameters, this is computationally impossible.

Backpropagation solves this by computing the gradient with respect to ALL weights using only one forward pass and one backward pass total, regardless of how many weights there are. That efficiency, not any new mathematics, is the entire point of the algorithm — the underlying calculus is just the chain rule you already know from single-variable calculus, applied systematically. Next, we set up the right mental model for organizing that computation: the computational graph.
-->

---
glowSeed: 832
---

# The Computational Graph

<div class="grid grid-cols-2 gap-8 items-center mt-2">
<div>
<v-clicks>

- Any composed function can be drawn as a **directed acyclic graph (DAG)**: each node is one elementary operation (add, multiply, sigmoid, ...)
- Edges carry values from one operation into the next
- The **forward pass** evaluates every node once, in topological order, from inputs to the final scalar loss
- Every node's inputs are simple enough that its local derivative is easy to write down — the graph does the bookkeeping for combining them

</v-clicks>
</div>
<div>
<svg role="img" aria-label="Computational graph: x and w feed a multiply node, then an add with bias, then a sigmoid, then a loss node" viewBox="0 0 420 260" class="w-full">
  <g stroke="#475569" stroke-width="2" fill="none">
    <line x1="55" y1="60" x2="140" y2="110"/>
    <line x1="55" y1="160" x2="140" y2="110"/>
    <line x1="140" y1="110" x2="230" y2="110"/>
    <line x1="180" y1="200" x2="230" y2="110"/>
    <line x1="230" y1="110" x2="320" y2="110"/>
    <line x1="320" y1="110" x2="390" y2="110"/>
  </g>
  <g fill="#0f172a" stroke-width="3">
    <circle cx="55" cy="60" r="20" stroke="#60a5fa"/>
    <circle cx="55" cy="160" r="20" stroke="#60a5fa"/>
    <circle cx="180" cy="200" r="20" stroke="#60a5fa"/>
    <circle cx="140" cy="110" r="24" stroke="#2dd4bf"/>
    <circle cx="230" cy="110" r="24" stroke="#2dd4bf"/>
    <circle cx="320" cy="110" r="24" stroke="#f59e0b"/>
  </g>
  <g fill="#cbd5e1" style="font-size: 13px" text-anchor="middle">
    <text x="55" y="65">x</text>
    <text x="55" y="165">w</text>
    <text x="180" y="205">b</text>
    <text x="140" y="115">×</text>
    <text x="230" y="115">+</text>
    <text x="320" y="115">σ</text>
    <text x="390" y="95">L</text>
  </g>
  <text x="10" y="20" fill="#94a3b8" style="font-size:13px">forward pass: evaluate left to right</text>
</svg>
</div>
</div>

<!--
Define the computational graph precisely: it is a directed acyclic graph — "directed" meaning edges have a direction (data flows one way), "acyclic" meaning there are no loops, so evaluation order is well defined. Every node is one elementary operation: a multiplication, an addition, a sigmoid, a matrix product. Every edge carries a concrete numeric value once the forward pass runs.

The key insight the whole rest of the lecture builds on: because every node is a simple elementary operation, we know its local derivative in closed form — a multiply node's local derivative is the other input, a sigmoid node's local derivative is sigma(z)(1-sigma(z)), and so on. Backpropagation never needs a symbolic derivative of the entire, enormous composed function; it only ever needs these simple local derivatives, combined via the chain rule, one graph edge at a time. Transition: now we build a concrete graph — a tiny two-layer network — and evaluate it with real numbers so the abstract picture becomes arithmetic.
-->

---
glowSeed: 833
---

# A Concrete Tiny Network

<div class="grid grid-cols-2 gap-6 items-start mt-2">
<div>

<v-clicks>

- Architecture: 2 inputs $\to$ 2 hidden neurons $\to$ 2 output neurons, sigmoid activation everywhere
- Every hidden neuron connects to **both** output neurons — this fan-out is what will force a *sum* in the backward pass
- Loss: sum of squared errors over both outputs, $L=\tfrac12\sum_k (\hat y_k-y_k)^2$
- All weights and the input are fixed numbers below — we will compute every intermediate value by hand

</v-clicks>

</div>
<div v-click class="text-sm" border="2 solid teal-800" bg="teal-800/20" rounded-lg px-4 py-3>

$$
\begin{aligned}
x &= (1.0,\ 0.5) \qquad y = (1.0,\ 0.0) \\[4pt]
W^{(1)} &= \begin{bmatrix} 0.3 & -0.4 \\ 0.2 & 0.5 \end{bmatrix},\quad b^{(1)} = \begin{bmatrix} 0.1 \\ -0.2 \end{bmatrix} \\[4pt]
W^{(2)} &= \begin{bmatrix} 0.6 & -0.3 \\ 0.4 & 0.5 \end{bmatrix},\quad b^{(2)} = \begin{bmatrix} 0.05 \\ -0.1 \end{bmatrix}
\end{aligned}
$$

</div>
</div>

<!--
This is the worked example the rest of the lecture depends on, so define every symbol precisely. x is the input vector, two numbers. W^(1) and b^(1) are the hidden layer's weight matrix and bias — row i of W^(1) holds the weights feeding hidden neuron i, so z1 = 0.3·x1 − 0.4·x2 + 0.1 and z2 = 0.2·x1 + 0.5·x2 − 0.2. W^(2) and b^(2) play the same role for the output layer, mapping the two hidden activations to two output pre-activations. y is the target: we want output 1 to move toward 1.0 and output 2 toward 0.0 — this mimics a two-class one-hot target.

The critical structural feature: because there are two hidden neurons and two output neurons with a full connection between every hidden neuron and every output neuron, each hidden neuron's activation affects the loss through two separate downstream paths — one through each output neuron. That fan-out is deliberate: it is what forces the backward-pass derivation to include a genuine sum over paths, rather than a single term that could be mistaken for the whole story. Next slide: plug these numbers into the forward pass, one layer at a time.
-->

---
glowSeed: 834
---

# Forward Pass — Hidden Layer

<div class="grid grid-cols-2 gap-6 items-start mt-2">
<div class="text-sm" border="2 solid blue-800" bg="blue-800/20" rounded-lg px-4 py-3>

$$
\begin{aligned}
z_1 &= 0.3(1.0) + (-0.4)(0.5) + 0.1 = 0.2000 \\
z_2 &= 0.2(1.0) + 0.5(0.5) + (-0.2) = 0.2500
\end{aligned}
$$

</div>
<div class="text-sm" v-click border="2 solid teal-800" bg="teal-800/20" rounded-lg px-4 py-3>

$$
\begin{aligned}
a_1 &= \sigma(0.2000) = \frac{1}{1+e^{-0.2000}} = 0.5498 \\
a_2 &= \sigma(0.2500) = \frac{1}{1+e^{-0.2500}} = 0.5622
\end{aligned}
$$

</div>
</div>

<div v-click class="mt-6 text-sm opacity-85">
Each hidden pre-activation $z_j$ is a weighted sum of the inputs plus a bias; each activation $a_j=\sigma(z_j)$ squashes it into $(0,1)$. Both numbers are cached — the backward pass will need them again.
</div>

<!--
Walk through the arithmetic explicitly rather than just displaying it: z1 is the weighted sum feeding hidden neuron 1 — multiply each input by its corresponding weight from row 1 of W^(1), add the bias, and you get 0.3(1.0) + (−0.4)(0.5) + 0.1 = 0.3 − 0.2 + 0.1 = 0.2000. z2 uses row 2 of W^(1) the same way, giving 0.2500. These are called "pre-activations" because the nonlinearity has not been applied yet.

Applying the sigmoid function sigma(z) = 1/(1+e^{-z}) turns each pre-activation into an activation between 0 and 1: sigma(0.2000) ≈ 0.5498 and sigma(0.2500) ≈ 0.5622. Common misconception to flag here: students often forget that z and a are different numbers that both need to be stored — the backward pass needs the raw z (or equivalently a) to compute sigma'(z) = a(1−a), and it needs a itself as the "input" to the next layer's weighted sum. This caching is exactly why training uses more memory than pure inference, which can discard z and a as soon as they are no longer needed for a subsequent layer. Next: push a1 and a2 through the output layer to get the network's predictions and the loss.
-->

---
glowSeed: 835
---

# Forward Pass — Output Layer and Loss

<div class="grid grid-cols-2 gap-6 items-start mt-2">
<div class="text-sm" border="2 solid blue-800" bg="blue-800/20" rounded-lg px-4 py-3>

$$
\begin{aligned}
z^{out}_1 &= 0.6(0.5498) + (-0.3)(0.5622) + 0.05 = 0.2112 \\
z^{out}_2 &= 0.4(0.5498) + 0.5(0.5622) + (-0.1) = 0.4010
\end{aligned}
$$

</div>
<div class="text-sm" v-click border="2 solid teal-800" bg="teal-800/20" rounded-lg px-4 py-3>

$$
\begin{aligned}
\hat y_1 &= \sigma(0.2112) = 0.5526 \\
\hat y_2 &= \sigma(0.4010) = 0.5989
\end{aligned}
$$

</div>
</div>

<div v-click class="mt-6 text-sm" border="2 solid amber-800" bg="amber-800/20" rounded-lg px-4 py-3>

$$
L = \tfrac12(\hat y_1-y_1)^2 + \tfrac12(\hat y_2-y_2)^2 = \tfrac12(0.5526-1.0)^2+\tfrac12(0.5989-0.0)^2 = 0.2794
$$

</div>

<!--
Same mechanics as the hidden layer, one level up: z^out_1 is the weighted sum of the hidden activations (not the raw inputs) using row 1 of W^(2), plus its bias — 0.6(0.5498) + (−0.3)(0.5622) + 0.05 = 0.3299 − 0.1687 + 0.05 = 0.2112. z^out_2 uses row 2 of W^(2), giving 0.4010. Applying sigma again gives the network's two predictions: y-hat_1 = 0.5526 and y-hat_2 = 0.5989.

The loss compares each prediction to its target with squared error and sums across outputs: L = 0.5(0.5526−1.0)^2 + 0.5(0.5989−0.0)^2 = 0.5(0.2001) + 0.5(0.3587) = 0.1001 + 0.1794 = 0.2794. The one-half factor is a convention that cancels the 2 produced when we differentiate the square, making the derivative exactly (y-hat − y) rather than 2(y-hat − y) — purely a bookkeeping convenience, not a different loss function. We now have every forward-pass number cached: x, z1, a1, z2, a2, z^out_1, y-hat_1, z^out_2, y-hat_2, and L. The next three slides derive, from the chain rule alone, how to turn this cache into every gradient the network needs.
-->

---
glowSeed: 836
---

# The Chain Rule, Reviewed

<div class="grid grid-cols-2 gap-8 items-start mt-2">
<div>
<v-clicks>

- Single-variable chain rule: if $L$ depends on $g$ which depends on $x$, then $\dfrac{dL}{dx}=\dfrac{dL}{dg}\cdot\dfrac{dg}{dx}$ — derivatives along a chain **multiply**
- If $x$ influences $L$ through **two** separate downstream quantities $g_1, g_2$, their contributions **add**
- This additive rule is the multivariate chain rule, and it is exactly what a fan-out node in a computational graph requires

</v-clicks>
</div>
<div v-click class="text-sm" border="2 solid violet-800" bg="violet-800/20" rounded-lg px-4 py-3>

$$
\frac{\partial L}{\partial x} = \sum_{k} \frac{\partial L}{\partial g_k}\cdot\frac{\partial g_k}{\partial x}
$$

<div class="mt-2 text-xs opacity-80">Sum over every downstream path from $x$ to $L$</div>
</div>
</div>

<!--
This slide is the single most important piece of calculus in the whole lecture, so state it carefully. The single-variable chain rule says derivatives along a chain multiply: if L is a function of g, and g is a function of x, then dL/dx = (dL/dg)(dg/dx). A very common misconception is to add these two factors instead of multiplying them — multiplication is correct because it is a rate-of-change-of-a-rate-of-change: a small change in x causes a proportional change in g, which causes a proportional change in L, and the two proportionality constants compose by multiplying.

The multivariate extension handles the case where x affects L through more than one route. If x feeds into g1 and separately into g2, and both g1 and g2 feed into L, then a small perturbation of x changes L along both paths simultaneously, and the total effect is the sum of each path's contribution: partial L/partial x = sum over k of (partial L/partial g_k)(partial g_k/partial x). This is exactly the situation for a hidden neuron in our tiny network — its activation a1 feeds both output neurons, so its gradient will be a sum of two terms, not one. Next: apply the single-path version of this rule first, to the output layer, where each output neuron has only one path to the loss.
-->

---
glowSeed: 837
---

# Backward Pass — Output Layer, Deriving δ

<div class="grid grid-cols-2 gap-6 items-start mt-2">
<div class="space-y-3">
<div v-click border="2 solid white/5" bg="white/5" rounded-lg px-4 py-3>
<span class="font-bold text-teal-300">Step 1 — loss to prediction</span>
<span class="text-sm opacity-85"> — $\partial L/\partial \hat y_k = \hat y_k - y_k$</span>
</div>
<div v-click border="2 solid white/5" bg="white/5" rounded-lg px-4 py-3>
<span class="font-bold text-blue-300">Step 2 — prediction to pre-activation</span>
<span class="text-sm opacity-85"> — $\partial \hat y_k/\partial z^{out}_k = \hat y_k(1-\hat y_k)$</span>
</div>
<div v-click border="2 solid white/5" bg="white/5" rounded-lg px-4 py-3>
<span class="font-bold text-amber-300">Step 3 — multiply (chain rule, single path)</span>
<span class="text-sm opacity-85"> — $\delta^{out}_k := \partial L/\partial z^{out}_k$</span>
</div>
</div>
<div v-click class="text-sm" border="2 solid teal-800" bg="teal-800/20" rounded-lg px-4 py-3>

$$
\begin{aligned}
\delta^{out}_k &= \frac{\partial L}{\partial \hat y_k}\cdot\frac{\partial \hat y_k}{\partial z^{out}_k} = (\hat y_k-y_k)\,\hat y_k(1-\hat y_k) \\[6pt]
\frac{\partial L}{\partial v_{kj}} &= \delta^{out}_k \cdot \frac{\partial z^{out}_k}{\partial v_{kj}} = \delta^{out}_k \, a_j
\end{aligned}
$$

</div>
</div>

<!--
Derive this step by step rather than presenting it as a formula to memorize. Each output neuron k has exactly one path to the loss, so the ordinary single-variable chain rule applies. Step 1: L depends on y-hat_k through the squared-error term 0.5(y-hat_k − y_k)^2, whose derivative with respect to y-hat_k is (y-hat_k − y_k) — the 0.5 and the 2 from the power rule cancel, which is exactly why that 0.5 was included in the loss definition. Step 2: y-hat_k = sigma(z^out_k), and the derivative of the sigmoid function has the well-known closed form sigma'(z) = sigma(z)(1−sigma(z)) = y-hat_k(1−y-hat_k) — this is worth deriving once on the board from the quotient rule, since students will reuse it constantly.

Step 3 multiplies these two factors together, by the chain rule, to get delta^out_k := partial L/partial z^out_k — this quantity is often called the "error signal" or "delta" at that neuron, and it is the single number that captures how sensitive the loss is to that neuron's pre-activation. Once we have delta^out_k, the gradient with respect to any weight feeding into that neuron is just delta^out_k times whatever value flowed into that weight — here, the hidden activation a_j — because z^out_k = sum_j v_kj a_j + c_k is linear in v_kj, making partial z^out_k/partial v_kj = a_j. Next slide: substitute this network's actual cached numbers.
-->

---
glowSeed: 838
---

# Backward Pass — Output Layer, Numeric Gradients

<div class="grid grid-cols-2 gap-6 items-start mt-2">
<div class="text-sm" border="2 solid teal-800" bg="teal-800/20" rounded-lg px-4 py-3>

$$
\begin{aligned}
\delta^{out}_1 &= (0.5526-1.0)(0.2472) = -0.1106 \\
\delta^{out}_2 &= (0.5989-0.0)(0.2402) = 0.1439
\end{aligned}
$$

</div>
<div class="text-sm" v-click border="2 solid amber-800" bg="amber-800/20" rounded-lg px-4 py-3>

$$
\begin{aligned}
\partial L/\partial v_{11} &= \delta^{out}_1 a_1 = -0.0608, &
\partial L/\partial v_{12} &= \delta^{out}_1 a_2 = -0.0622 \\
\partial L/\partial v_{21} &= \delta^{out}_2 a_1 = 0.0791, &
\partial L/\partial v_{22} &= \delta^{out}_2 a_2 = 0.0809 \\
\partial L/\partial c_1 &= \delta^{out}_1 = -0.1106, &
\partial L/\partial c_2 &= \delta^{out}_2 = 0.1439
\end{aligned}
$$

</div>
</div>

<div v-click class="mt-6 text-sm opacity-85">
Every output-layer gradient is now known — six numbers, computed from cached forward-pass values with no new forward passes required.
</div>

<!--
Substitute the cached numbers from three slides ago directly into the delta formula. For output 1: y-hat_1 = 0.5526, y_1 = 1.0, and the local sigmoid derivative y-hat_1(1−y-hat_1) = 0.5526(0.4474) = 0.2472, giving delta^out_1 = (0.5526−1.0)(0.2472) = (−0.4474)(0.2472) = −0.1106. The negative sign has a concrete meaning: increasing z^out_1 would increase y-hat_1 toward the target 1.0, which would decrease the loss — so the loss is decreasing in z^out_1, hence a negative partial derivative. For output 2, y_2 = 0.0 is the target, so delta^out_2 = (0.5989−0.0)(0.2402) = 0.1439, positive because y-hat_2 is already too large relative to its target of 0.

Every weight gradient is now just delta times the corresponding hidden activation: partial L/partial v_11 = delta^out_1 · a_1 = (−0.1106)(0.5498) = −0.0608, and so on for all six output-layer parameters (four weights and two biases) shown above. This is the first fully numeric gradient computed by hand in this lecture — pause and let students verify one entry themselves. Transition: the hidden layer is next, and it is qualitatively different, because each hidden neuron has two downstream paths rather than one.
-->

---
glowSeed: 839
---

# Backward Pass — Hidden Layer: Summing Over Paths

<div class="grid grid-cols-2 gap-6 items-start mt-2">
<div class="space-y-3">
<div v-click border="2 solid white/5" bg="white/5" rounded-lg px-4 py-3>
<span class="font-bold text-teal-300">Two downstream paths</span>
<span class="text-sm opacity-85"> — $a_1$ feeds both $z^{out}_1$ and $z^{out}_2$, so its gradient sums both contributions.</span>
</div>
<div v-click border="2 solid white/5" bg="white/5" rounded-lg px-4 py-3>
<span class="font-bold text-blue-300">Multivariate chain rule</span>
<span class="text-sm opacity-85"> — This is precisely the summed rule from two slides back, applied concretely.</span>
</div>
<div v-click border="2 solid white/5" bg="white/5" rounded-lg px-4 py-3>
<span class="font-bold text-amber-300">Then the local sigmoid step</span>
<span class="text-sm opacity-85"> — Multiply the summed upstream signal by this layer's own activation slope.</span>
</div>
</div>
<div v-click class="text-sm" border="2 solid violet-800" bg="violet-800/20" rounded-lg px-4 py-3>

$$
\begin{aligned}
\frac{\partial L}{\partial a_j} &= \sum_k \delta^{out}_k\, v_{kj} \\[6pt]
\delta_j &:= \frac{\partial L}{\partial z_j} = \frac{\partial L}{\partial a_j}\cdot\sigma'(z_j) = \Big(\sum_k \delta^{out}_k v_{kj}\Big)a_j(1-a_j) \\[6pt]
\frac{\partial L}{\partial w_{ji}} &= \delta_j \, x_i
\end{aligned}
$$

</div>
</div>

<!--
This is the derivation the entire lecture has been building toward, so slow down here. Hidden activation a1 does not connect directly to the loss — it connects to z^out_1 and z^out_2, each of which connects to the loss. By the multivariate chain rule from two slides ago, the total sensitivity of L to a1 is the sum of its sensitivity through each path: partial L/partial a_j = sum_k delta^out_k · v_kj, where v_kj is the weight carrying a_j into output k's pre-activation, and delta^out_k is the error signal at output k that we already computed. In matrix form for the whole hidden layer at once, this sum is exactly the matrix-vector product (W^(2))^T delta^out — the transpose appears because we are now going backward, from outputs to hidden units, whereas W^(2) itself was defined for the forward direction.

Once we have partial L/partial a_j, one more chain-rule step converts it into delta_j = partial L/partial z_j, by multiplying by the local sigmoid derivative a_j(1−a_j), exactly as in the output layer. And once we have delta_j, the gradient with respect to any weight w_ji feeding into hidden neuron j is delta_j times whatever fed that weight — here, the raw input x_i, since z_j = sum_i w_ji x_i + b_j is linear in w_ji. Common misconception to name explicitly: students often write delta_j as a single term (as if a1 had only one downstream path), forgetting the sum — that error silently drops information whenever a layer's output fans out to more than one downstream unit, which is the normal case in real networks. Next: substitute this network's numbers.
-->

---
glowSeed: 840
---

# Backward Pass — Hidden Layer, Numeric Gradients

<div class="grid grid-cols-2 gap-6 items-start mt-2">
<div class="text-sm" border="2 solid violet-800" bg="violet-800/20" rounded-lg px-4 py-3>

$$
\begin{aligned}
\partial L/\partial a_1 &= (-0.1106)(0.6)+(0.1439)(0.4) = -0.0088 \\
\partial L/\partial a_2 &= (-0.1106)(-0.3)+(0.1439)(0.5) = 0.1051
\end{aligned}
$$

</div>
<div class="text-sm" v-click border="2 solid teal-800" bg="teal-800/20" rounded-lg px-4 py-3>

$$
\begin{aligned}
\delta_1 &= (-0.0088)(0.2475) = -0.0022 \\
\delta_2 &= (0.1051)(0.2461) = 0.0259
\end{aligned}
$$

</div>
</div>

<div v-click class="mt-4 text-sm" border="2 solid amber-800" bg="amber-800/20" rounded-lg px-4 py-3>

$$
\begin{aligned}
\partial L/\partial w_{11} &= \delta_1 x_1 = -0.0022, &
\partial L/\partial w_{12} &= \delta_1 x_2 = -0.0011, &
\partial L/\partial b_1 &= \delta_1 = -0.0022 \\
\partial L/\partial w_{21} &= \delta_2 x_1 = 0.0259, &
\partial L/\partial w_{22} &= \delta_2 x_2 = 0.0129, &
\partial L/\partial b_2 &= \delta_2 = 0.0259
\end{aligned}
$$

</div>

<!--
Substitute the numbers. For a1: delta^out_1 v_11 + delta^out_2 v_21 = (−0.1106)(0.6) + (0.1439)(0.4) = −0.0664 + 0.0576 = −0.0088. Notice the two terms nearly cancel — output 1 pulls a1's gradient negative while output 2 pulls it positive, because a1 helps output 1 (good, target 1.0) while also incorrectly pushing output 2 upward (bad, target 0.0). This near-cancellation is a direct, numeric illustration of why omitting one of the two sum terms would give a badly wrong answer — the misconception flagged on the previous slide is not a minor rounding issue, it can flip the sign of the gradient entirely.

For a2: (−0.1106)(−0.3) + (0.1439)(0.5) = 0.0332 + 0.0719 = 0.1051. Multiplying each by its local sigmoid slope gives delta_1 = −0.0088 × 0.2475 = −0.0022 and delta_2 = 0.1051 × 0.2461 = 0.0259. Finally, each hidden weight's gradient is its neuron's delta times the corresponding input: partial L/partial w_11 = delta_1 · x_1 = −0.0022, and so on for all six hidden-layer parameters shown above. We have now computed the complete gradient of L with respect to all twelve weights and four biases in this network, using exactly one forward pass and one backward pass — not twelve or sixteen separate reruns. That efficiency claim is the subject of the next two slides.
-->

---
glowSeed: 841
---

# One Gradient Descent Step

<div class="grid grid-cols-2 gap-6 items-start mt-2">
<div class="text-sm opacity-90">

<v-clicks>

- Gradient descent moves every weight a small step **opposite** its gradient — the gradient points toward steeper loss, so we subtract it
- Learning rate $\eta$ controls the step size; here $\eta=0.5$ purely to make the change visible
- This single update uses every number computed on the last four slides — nothing is recomputed

</v-clicks>

</div>
<div v-click class="text-sm" border="2 solid teal-800" bg="teal-800/20" rounded-lg px-4 py-3>

$$
\begin{aligned}
w_{11}^{new} &= w_{11} - \eta\,\frac{\partial L}{\partial w_{11}} = 0.3000 - 0.5(-0.0022) = 0.3011 \\
v_{11}^{new} &= v_{11} - \eta\,\frac{\partial L}{\partial v_{11}} = 0.6000 - 0.5(-0.0608) = 0.6304
\end{aligned}
$$

</div>
</div>

<!--
Connect the gradient we just derived to what it is actually used for: gradient descent updates every parameter as w_new = w − eta · (partial L/partial w), where eta is the learning rate, a small positive number chosen before training. The gradient partial L/partial w points in the direction that would most increase the loss if we moved w that way — this is a common misconception to name directly: the gradient is the direction of steepest ascent, not descent, which is exactly why the update subtracts it rather than adds it.

Using our computed gradients with an illustrative eta = 0.5: w_11 moves from 0.3000 to 0.3000 − 0.5(−0.0022) = 0.3011, a small increase, because its gradient was negative (increasing w_11 would decrease the loss). v_11 moves from 0.6000 to 0.6000 − 0.5(−0.0608) = 0.6304, a larger increase, because output-layer gradients were larger in magnitude than hidden-layer gradients here — this is a preview of the vanishing-gradient phenomenon covered in a later lecture, where gradients shrink as they propagate backward through many sigmoid layers. In practice eta is far smaller, often 0.01 to 0.001, and a single step like this is repeated thousands of times over many training examples; we used an exaggerated eta only so the arithmetic change is visible on one slide. Next: why was this entire gradient computable in one backward pass, when the naive method from the start of the lecture needed sixteen?
-->

---
glowSeed: 842
---

# Forward-Mode vs. Reverse-Mode Differentiation

<div class="grid grid-cols-2 gap-4 mt-6">
<div v-click border="2 solid teal-800" bg="teal-800/20" rounded-lg p-4>
<div class="font-bold text-teal-300 mb-2">Forward mode</div>
<div class="text-sm leading-relaxed opacity-90">Propagate $\partial(\text{everything})/\partial w_i$ forward, one input weight at a time. Cost scales with the number of <strong>inputs</strong> — here, 16 weights means 16 forward sweeps.</div>
</div>
<div v-click border="2 solid blue-800" bg="blue-800/20" rounded-lg p-4>
<div class="font-bold text-blue-300 mb-2">Reverse mode (backprop)</div>
<div class="text-sm leading-relaxed opacity-90">Propagate $\partial L/\partial(\text{everything})$ backward from the single scalar loss. Cost scales with the number of <strong>outputs</strong> — here, 1 loss means exactly 1 backward sweep.</div>
</div>
<div v-click border="2 solid amber-800" bg="amber-800/20" rounded-lg p-4>
<div class="font-bold text-amber-300 mb-2">Why training uses reverse mode</div>
<div class="text-sm leading-relaxed opacity-90">Loss functions have <em>one</em> scalar output and potentially <em>millions</em> of weight-inputs — the exact regime where reverse mode wins by orders of magnitude.</div>
</div>
</div>

<!--
Generalize the efficiency argument beyond finite differences. Automatic differentiation has two dual strategies. Forward mode fixes one input variable, sets its "seed" derivative to 1 and every other input's seed to 0, and propagates derivatives forward through the graph alongside the ordinary values — this computes one full column of the Jacobian (the derivative of every output with respect to that one input) per sweep. To get the gradient of a scalar loss with respect to n weights, forward mode needs n separate sweeps, one per weight — this is structurally the same cost as the finite-difference approach from the start of the lecture, just computed exactly instead of approximately.

Reverse mode does the opposite: it fixes one output, seeds its upstream derivative to 1, and propagates backward through the graph, accumulating partial L/partial(each intermediate) as it goes — exactly what we did by hand for our tiny network. This computes one full row of the Jacobian per sweep — the derivative of that one output with respect to every input — in a single pass. Since a loss function is a single scalar (one output) and a network can have millions of weights (many inputs), reverse mode needs exactly one backward sweep regardless of parameter count, while forward mode would need one sweep per parameter. This asymmetry between "few outputs, many inputs" is precisely the situation neural network training sits in, which is why every deep learning framework implements reverse-mode automatic differentiation as backpropagation.
-->

---
glowSeed: 843
---

# Backpropagation Is Reverse-Mode Autodiff

<div class="grid grid-cols-2 gap-8 items-start mt-2">
<div class="space-y-3">
<div v-click border="2 solid white/5" bg="white/5" rounded-lg px-4 py-3>
<span class="font-bold text-teal-300">Topological order</span>
<span class="text-sm opacity-85"> — Forward pass visits every graph node once, inputs to loss.</span>
</div>
<div v-click border="2 solid white/5" bg="white/5" rounded-lg px-4 py-3>
<span class="font-bold text-blue-300">Reverse order</span>
<span class="text-sm opacity-85"> — Backward pass revisits the same nodes in reverse, accumulating $\partial L/\partial(\text{node})$.</span>
</div>
<div v-click border="2 solid white/5" bg="white/5" rounded-lg px-4 py-3>
<span class="font-bold text-amber-300">Dynamic programming</span>
<span class="text-sm opacity-85"> — Each node's upstream gradient is computed exactly once and reused by every earlier node that needs it.</span>
</div>
</div>
<div>
<div v-click class="text-sm" border="2 solid violet-800" bg="violet-800/20" rounded-lg px-4 py-3>
The quantity carried backward along each edge — $\delta^{out}_k$, $\delta_j$ in our example — is often called the node's <strong>adjoint</strong> or <strong>upstream gradient</strong>: how sensitive the final loss is to that one intermediate value.
</div>
</div>
</div>

<!--
Tie the concrete derivation back to the general algorithm. Backpropagation is nothing but reverse-mode automatic differentiation applied to the specific computational graph of a layered neural network. The forward pass visits every node in topological order (an order respecting all the dependency arrows) and computes its numeric value — this is the caching step from the very first content slide. The backward pass then visits the same nodes in the reverse order, and at each node computes that node's "adjoint" — the partial derivative of the final scalar loss with respect to that node's value — by combining the adjoints of the nodes it feeds into (summing when there is fan-out, exactly as derived for the hidden layer) with that node's own local derivative.

This is precisely a dynamic programming algorithm: without caching, the gradient with respect to an early node would require re-deriving its effect on the loss through every downstream path from scratch, an amount of work that grows exponentially with graph depth for a naive recursive implementation. By storing each node's adjoint exactly once and reusing it, the total work of the backward pass is proportional to the total work of the forward pass — a small constant multiple, not a blow-up. This is exactly why delta^out_1 and delta^out_2, computed once, were directly reused (multiplied by weights, summed) to get the hidden-layer deltas, rather than being rederived. Next: this general algorithm is what deep learning frameworks implement automatically, so practitioners rarely hand-derive these formulas.
-->

---
glowSeed: 844
---

# Automatic Differentiation in Practice

<div class="grid grid-cols-2 gap-8 items-start">
<div>
<div class="space-y-3 mt-4">
<div v-click border="2 solid white/5" bg="white/5" rounded-lg px-4 py-3>
<span class="font-bold text-teal-300">Record operations</span>
<span class="text-sm opacity-85"> — Libraries build the computation graph automatically during the forward pass.</span>
</div>
<div v-click border="2 solid white/5" bg="white/5" rounded-lg px-4 py-3>
<span class="font-bold text-blue-300">Call one function</span>
<span class="text-sm opacity-85"> — <code>loss.backward()</code> triggers the entire reverse-mode traversal.</span>
</div>
<div v-click border="2 solid white/5" bg="white/5" rounded-lg px-4 py-3>
<span class="font-bold text-amber-300">Same math, hidden</span>
<span class="text-sm opacity-85"> — <code>model.fit</code> and <code>loss.backward()</code> execute the exact derivation from this lecture, at scale.</span>
</div>
</div>
</div>
<div class="text-xs">

```python
import torch

x = torch.tensor([1.0, 0.5])
y = torch.tensor([1.0, 0.0])

W1 = torch.tensor([[0.3, -0.4], [0.2, 0.5]],
                   requires_grad=True)
b1 = torch.tensor([0.1, -0.2], requires_grad=True)
W2 = torch.tensor([[0.6, -0.3], [0.4, 0.5]],
                   requires_grad=True)
b2 = torch.tensor([0.05, -0.1], requires_grad=True)

a1 = torch.sigmoid(W1 @ x + b1)
y_hat = torch.sigmoid(W2 @ a1 + b2)
loss = 0.5 * ((y_hat - y) ** 2).sum()

loss.backward()  # reverse-mode sweep
print(W1.grad, b1.grad)  # matches hand-derived grads
```

</div>
</div>

<!--
This is the same network, same numbers, expressed in PyTorch — running it should reproduce the exact gradients derived by hand on the previous slides, up to rounding. requires_grad=True tells PyTorch to record every operation touching that tensor into a computation graph as the forward pass executes; this recording is the "record operations" step. loss.backward() then triggers a full reverse-mode sweep over that recorded graph: it computes the adjoint of every intermediate tensor exactly as we did by hand, and the leaf tensors' .grad attributes end up holding partial L/partial W1, partial L/partial b1, and so on.

The point of showing this code is not the syntax — it is to demystify the phrase "the library computes the gradients." There is no separate, more powerful algorithm running inside PyTorch; loss.backward() is executing precisely the chain-rule bookkeeping this lecture just derived by hand, generalized to work automatically on any composed differentiable function, not just this one small network. When later lectures say "the optimizer updates the weights using the gradients," those gradients are backpropagation's output, cached exactly as described here. Next: before moving on, name a short list of the most common ways students misapply this material.
-->

---
glowSeed: 845
---

# Common Misconceptions

<div class="grid grid-cols-2 gap-4 mt-6">
<div v-click border="2 solid red-800" bg="red-800/20" rounded-lg p-4>
<div class="font-bold text-red-300 mb-2">"Chain rule adds, not multiplies"</div>
<div class="text-sm leading-relaxed opacity-90">Along one path, factors <strong>multiply</strong>: $dL/dx=(dL/dg)(dg/dx)$. Sums appear only across <em>separate</em> paths.</div>
</div>
<div v-click border="2 solid red-800" bg="red-800/20" rounded-lg p-4>
<div class="font-bold text-red-300 mb-2">"Gradient points toward the minimum"</div>
<div class="text-sm leading-relaxed opacity-90">The gradient points toward <strong>steepest increase</strong>. Descent requires subtracting it, not following it.</div>
</div>
<div v-click border="2 solid red-800" bg="red-800/20" rounded-lg p-4>
<div class="font-bold text-red-300 mb-2">"Zero gradient means global minimum"</div>
<div class="text-sm leading-relaxed opacity-90">A zero gradient marks any critical point — local minimum, local maximum, or saddle. Loss surfaces of real networks are highly non-convex.</div>
</div>
<div v-click border="2 solid red-800" bg="red-800/20" rounded-lg p-4>
<div class="font-bold text-red-300 mb-2">"Fan-out doesn't matter"</div>
<div class="text-sm leading-relaxed opacity-90">Dropping one term of a fan-out sum (as in our hidden layer) can flip a gradient's sign, as the near-cancellation in $\partial L/\partial a_1$ showed directly.</div>
</div>
</div>

<!--
Four misconceptions worth naming explicitly and correcting on the board, because each one produces a specific, diagnosable bug. First: the chain rule multiplies local derivatives along a single path — dL/dx = (dL/dg)(dg/dx) — students who instead add these factors will get gradients with wrong units and wrong magnitude; sums only ever appear when combining contributions from genuinely separate downstream paths, as derived for the hidden layer.

Second: the gradient partial L/partial w points in the direction of steepest increase of L, not decrease — gradient descent explicitly subtracts eta times the gradient for exactly this reason, and forgetting the minus sign is one of the most common bugs when implementing an optimizer from scratch, causing the loss to increase every step instead of decrease. Third: a zero gradient identifies a critical point, not necessarily a minimum, let alone the global minimum — it could be a local minimum, a local maximum, or (very commonly in high-dimensional networks) a saddle point where the surface curves up in some directions and down in others; real network loss surfaces are non-convex, with many such points, and gradient descent gives no formal guarantee of reaching the global optimum. Fourth: our own numeric example showed that omitting one term of a fan-out sum is not a negligible rounding error — for partial L/partial a_1, the two path contributions (−0.0664 and +0.0576) nearly canceled, so dropping either one would have flipped the sign of the resulting gradient entirely, an easy and consequential bug when implementing backprop by hand or debugging a custom autodiff graph.
-->

---
glowSeed: 846
---

# Backpropagation

<div class="mt-8"><div class="grid grid-cols-3 gap-4 mt-6">
<div v-click border="2 solid teal-800" bg="teal-800/20" rounded-lg p-4>
<div class="font-bold text-teal-300 mb-2">Forward</div>
<div class="text-sm leading-relaxed opacity-90">Compute and cache every $z$ and $a$, in topological order.</div>
</div>
<div v-click border="2 solid blue-800" bg="blue-800/20" rounded-lg p-4>
<div class="font-bold text-blue-300 mb-2">Backward</div>
<div class="text-sm leading-relaxed opacity-90">Propagate $\delta$ recursively, summing over every fan-out path.</div>
</div>
<div v-click border="2 solid amber-800" bg="amber-800/20" rounded-lg p-4>
<div class="font-bold text-amber-300 mb-2">Autodiff</div>
<div class="text-sm leading-relaxed opacity-90">Frameworks automate this exact graph traversal at any scale.</div>
</div>
</div></div>

<div v-click class="mt-8 text-sm max-w-3xl mx-auto text-left" border="2 solid white/10" bg="white/5" rounded-lg px-6 py-4>

- Every gradient in this lecture came from one forward pass and one backward pass through a small worked example — twelve weights and four biases, computed by hand from the chain rule
- Reverse mode wins because networks have many weight-inputs but one scalar loss-output
- The four misconceptions on the previous slide are the most common sources of bugs in a from-scratch backprop implementation

</div>

<div v-click class="mt-6 text-center text-lg" border="2 solid white/10" bg="white/5" rounded-lg px-6 py-4>Next: activation and initialization choices determine whether gradients flow well — sigmoid saturation and vanishing gradients.</div>

<!--
Recap the arc of the lecture concretely rather than abstractly. We started by showing the naive alternative — finite differences, one extra forward pass per weight — is too slow to train real networks. We then built a small but structurally complete network (fan-out included) and computed a full forward pass by hand, then derived the backward pass from first principles: the single-variable chain rule for the output layer's single-path deltas, and the multivariate chain rule's summed version for the hidden layer's fan-out. We verified the efficiency claim by contrasting forward-mode and reverse-mode automatic differentiation, and connected the by-hand derivation to loss.backward() in PyTorch.

Preview for next time: this lecture assumed sigmoid activations throughout and never asked whether the gradients we computed were large or small in absolute terms. Notice that a1(1−a1) and a2(1−a2), the local sigmoid derivatives, were both close to 0.25 — this is sigmoid's maximum possible slope, and it only shrinks further as z moves away from 0. Stacking many sigmoid layers multiplies many such factors below 0.25 together, and the product shrinks toward zero exponentially with depth — this is the vanishing gradient problem, and it is why modern deep networks favor ReLU-family activations and careful weight initialization. That is exactly where the next lecture picks up. Take questions before moving on.
-->

---
layout: center
class: text-center
glowSeed: 847
---

# Thank You

### Questions &amp; Discussion

<div class="pt-6 opacity-80">
Backpropagation · Neural Networks and Deep Learning Basics
</div>

<!--
Open the floor for questions before the next lecture. Good prompts if the room is quiet: ask a student to recompute delta_2 for the hidden layer from scratch on the board, using only the cached forward-pass numbers, to confirm the arithmetic is reproducible and not just something that appeared on a slide. Or ask what would change in the derivation if the network had three output neurons instead of two — the answer is that the sum defining partial L/partial a_j would simply have three terms instead of two, with no other change to the method, reinforcing that the fan-out sum generalizes cleanly to any width. Transition to the next lecture: activation functions, gradient saturation, and weight initialization strategies that keep gradients from vanishing or exploding as networks get deeper.
-->
