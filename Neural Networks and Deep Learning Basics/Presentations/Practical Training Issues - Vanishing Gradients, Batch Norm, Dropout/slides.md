---
theme: default
highlighter: shiki
css: unocss
colorSchema: dark
title: 'Practical Training: Batch Normalization and Dropout'
info: |
  ## Practical Training: Batch Normalization and Dropout
  Stabilize gradient flow and regularize deep networks
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
glowSeed: 890
---

# Practical Training: Batch Normalization and Dropout

### Stabilize gradient flow and regularize deep networks

<div class="pt-8 opacity-80 text-lg">Neural Networks and Deep Learning Basics · Foundations of Machine Learning</div>

<div class="mt-14 flex justify-center gap-4" aria-hidden="true">
<div class="w-28 h-3 rounded-full bg-teal-400/70"></div>
<div class="w-20 h-3 rounded-full bg-blue-400/60"></div>
<div class="w-14 h-3 rounded-full bg-violet-400/50"></div>
</div>

<!--
This deck follows directly from the unit on building and training feedforward networks: once we know how to stack layers and run forward and backward propagation, two practical failure modes show up as soon as networks get deep. First, gradients computed by the chain rule can shrink toward zero or blow up toward infinity as they propagate backward through many layers, which stalls or destabilizes learning. Second, networks with enough capacity to fit deep, nonlinear functions can also memorize training data, which hurts generalization. Roadmap for today: derive why depth turns backpropagation into a long product of derivatives, see a concrete numeric illustration of vanishing and exploding values, cover standard mitigations (initialization, activation choice, gradient clipping), then study batch normalization and dropout in full mathematical and numeric detail, including their different behavior at train versus test time. We close by assembling everything into one modern dense network. Transition: start with the chain-rule mechanism that causes vanishing and exploding gradients.
-->

---
glowSeed: 891
---

# Backpropagation Multiplies Derivatives Through Depth

<div class="grid grid-cols-2 gap-8 items-start mt-2">
<div>

<v-clicks>

- Backpropagation computes $\partial L/\partial a_1$ by the **chain rule**, walking backward from the loss at layer $L$ to an early layer $1$
- Each step contributes one **local factor**: a layer's weight matrix combined with the derivative of its activation function
- With $L$ layers, that is $L-1$ factors **multiplied together**, not added
- A long product of numbers is exactly the setting where a value can shrink toward zero or grow without bound

</v-clicks>

</div>
<div>

<div v-click class="mt-6" style="font-size: .85em" border="2 solid teal-800" bg="teal-800/20" rounded-lg px-4 py-4>

$$
\begin{aligned}
\frac{\partial L}{\partial a_1} &= \frac{\partial L}{\partial a_L}\prod_{k=1}^{L-1}\frac{\partial a_{k+1}}{\partial a_k} \\
\frac{\partial a_{k+1}}{\partial a_k} &= (W^{(k+1)})^\top\,\mathrm{diag}\big(\sigma'(z^{(k+1)})\big)
\end{aligned}
$$

</div>

<div v-click class="mt-6 text-sm opacity-90">
$a_k$: activation vector at layer $k$. $W^{(k+1)}$: weight matrix mapping layer $k$ into layer $k+1$. $z^{(k+1)}$: pre-activation at layer $k+1$. $\sigma'$: derivative of the activation function, applied elementwise and placed on the diagonal.
</div>

</div>
</div>

<!--
Define every symbol before moving on. L is the number of layers, a_k is the vector of activations coming out of layer k, W^(k+1) is the weight matrix of the next layer, z^(k+1) = W^(k+1) a_k + b^(k+1) is that layer's pre-activation, and sigma-prime is the derivative of whatever nonlinearity is used, evaluated at that layer's pre-activation and placed on the diagonal of a matrix because each output unit's derivative only depends on its own pre-activation. The chain rule says the gradient of the loss with respect to an early activation is the gradient at the last layer times the product of all these intermediate local-derivative matrices, one per layer in between. This is the single most important fact in this deck: depth does not add error, it multiplies it, because differentiating a composition of functions multiplies derivatives rather than summing them. Misconception to flag: students often assume more layers only add more terms to a sum, the way adding more features adds more terms to a linear model; backpropagation through depth is fundamentally multiplicative, not additive. Transition: next we make this product concrete and see exactly how it can vanish or explode.
-->

---
glowSeed: 892
---

# Vanishing and Exploding Are One Product Problem

<div class="grid grid-cols-2 gap-8 items-start">
<div>
<div class="space-y-3 mt-4">
<div v-click border="2 solid white/5" bg="white/5" rounded-lg px-4 py-3>
<span class="font-bold text-teal-300">Factors below one</span>
<span class="text-sm opacity-85"> — If each local factor has magnitude less than 1 on average, the product shrinks geometrically with depth: early-layer gradients vanish.</span>
</div>
<div v-click border="2 solid white/5" bg="white/5" rounded-lg px-4 py-3>
<span class="font-bold text-blue-300">Factors above one</span>
<span class="text-sm opacity-85"> — If each local factor has magnitude greater than 1 on average, the product grows geometrically: gradients explode and training diverges.</span>
</div>
<div v-click border="2 solid white/5" bg="white/5" rounded-lg px-4 py-3>
<span class="font-bold text-amber-300">Across depth or time</span>
<span class="text-sm opacity-85"> — The same repeated-multiplication mechanism affects deep dense nets, deep CNNs, and RNNs unrolled over many time steps.</span>
</div>
</div>
</div>
<div>
<svg role="img" aria-label="Conceptual chart for Vanishing and Exploding Are One Product Problem" viewBox="0 0 500 310" class="w-full max-w-xl mx-auto mt-7">
  <line x1="55" y1="260" x2="470" y2="260" stroke="#64748b" stroke-width="2"/><line x1="55" y1="35" x2="55" y2="260" stroke="#64748b" stroke-width="2"/>
  <path d="M60 235 C130 210,145 70,220 100 S320 210,465 55" fill="none" stroke="#2dd4bf" stroke-width="5"/>
  <path d="M60 245 C135 230,205 195,270 165 S385 110,465 95" fill="none" stroke="#60a5fa" stroke-width="4" stroke-dasharray="9 7"/>
  <g fill="#f59e0b"><circle cx="65" cy="230" r="6"/><circle cx="163" cy="185" r="6"/><circle cx="261" cy="110" r="6"/><circle cx="359" cy="150" r="6"/><circle cx="457" cy="65" r="6"/></g>
  <g fill="#cbd5e1" style="font-size: 12px" text-anchor="middle"><text x="65" y="285">1</text><text x="163" y="285">5</text><text x="261" y="285">10</text><text x="359" y="285">15</text><text x="457" y="285">20 layers</text></g>
  <g style="font-size: 12px"><text x="335" y="42" fill="#5eead4">primary signal</text><text x="335" y="82" fill="#93c5fd">comparison</text></g>
</svg>
<div v-click class="mt-4" style="font-size: .9em" border="2 solid teal-800" bg="teal-800/20" rounded-lg px-4 py-3>

$$
\delta^{(1)}\propto\prod_{l=2}^L (W^{(l)})^\top\sigma'(z^{(l)})
$$

</div>
</div>
</div>

<!--
Here delta^(1) denotes the error signal (gradient of the loss with respect to the pre-activation) at layer 1, and the formula restates the previous slide's chain rule specifically for that quantity: it is proportional to a product over every layer from 2 to L of that layer's weight matrix transposed times the diagonal of its activation derivative. Whether this product shrinks or grows is governed by the typical magnitude of each factor, which depends on two things multiplying together: the scale of the weights (controlled by how they are initialized) and the scale of sigma-prime (controlled by the activation function). Saturating activations like sigmoid and tanh have derivatives bounded well below 1 almost everywhere, which pushes the product toward vanishing; poorly scaled weight initialization can push it toward exploding instead. Both failure modes are the same underlying phenomenon — repeated multiplication of numbers whose average magnitude is not close to 1 — just in opposite directions, and the same mechanism explains why very deep CNNs and RNNs unrolled over many time steps face the identical issue. Transition: let's make "repeated multiplication of numbers near 1" completely concrete with actual arithmetic.
-->

---
glowSeed: 893
---

# A Numeric Illustration: 0.9 and 1.1 to the Power of Depth

<div class="grid grid-cols-2 gap-6 mt-4 text-sm">

<div v-click border="2 solid teal-800" bg="teal-800/20" rounded-lg p-4>
<div class="font-bold text-teal-300 mb-2">Factors of 0.9 (vanishing)</div>
<table class="w-full text-left">
<tr class="opacity-70"><th class="pr-4">Layers</th><th>$0.9^L$</th></tr>
<tr><td class="pr-4">5</td><td>0.590</td></tr>
<tr><td class="pr-4">10</td><td>0.349</td></tr>
<tr><td class="pr-4">20</td><td>0.122</td></tr>
<tr><td class="pr-4">50</td><td>0.0052</td></tr>
<tr><td class="pr-4">100</td><td>0.0000266</td></tr>
</table>
</div>

<div v-click border="2 solid blue-800" bg="blue-800/20" rounded-lg p-4>
<div class="font-bold text-blue-300 mb-2">Factors of 1.1 (exploding)</div>
<table class="w-full text-left">
<tr class="opacity-70"><th class="pr-4">Layers</th><th>$1.1^L$</th></tr>
<tr><td class="pr-4">5</td><td>1.61</td></tr>
<tr><td class="pr-4">10</td><td>2.59</td></tr>
<tr><td class="pr-4">20</td><td>6.73</td></tr>
<tr><td class="pr-4">50</td><td>117.4</td></tr>
<tr><td class="pr-4">100</td><td>13,780</td></tr>
</table>
</div>

</div>

<div v-click class="mt-2 text-xs" border="2 solid amber-800" bg="amber-800/20" rounded-lg px-4 py-2>
Sigmoid's derivative is at most 0.25. Twenty layers of sigmoid units, each contributing a factor of at most 0.25, multiply to at most $0.25^{20}\approx 8.9\times10^{-13}$ — a gradient that is numerically indistinguishable from zero.
</div>

<!--
This slide replaces abstraction with arithmetic. A single number slightly less than 1, raised to a power equal to the network's depth, shrinks geometrically: 0.9 multiplied by itself 5 times is about 0.59, but by 100 times it is 0.0000266, essentially zero for any practical gradient update. The identical mechanism in reverse produces explosion: 1.1 raised to the 100th power is over 13,000, a gradient so large it will overflow numerically or cause the optimizer to take a destructively large step. The sigmoid example makes this concrete for a real activation function: sigmoid's derivative sigma(z)(1-sigma(z)) has a maximum value of exactly 0.25, achieved only at z=0, so a chain of twenty sigmoid layers multiplies at most twenty factors of 0.25, giving 0.25 to the 20th power, roughly 9 times 10 to the -13 power — a number so small it underflows to effectively zero in floating point and stops learning dead in early layers. This is precisely why sigmoid and tanh fell out of favor as the default hidden-layer activation for deep networks, and why ReLU, whose derivative is exactly 1 for all positive inputs, became standard. Transition: given this failure mode, what do practitioners actually do about it?
-->

---
glowSeed: 894
---

# Mitigating Vanishing and Exploding Gradients

<div class="grid grid-cols-2 gap-4 mt-4">

<div v-click border="2 solid teal-800" bg="teal-800/20" rounded-lg p-4>
<div class="font-bold text-teal-300 mb-2">Careful initialization</div>
<div class="text-sm leading-relaxed opacity-90">He or Xavier initialization scales initial weight variance by fan-in (and fan-out) so that the product of factors starts near magnitude 1.</div>
</div>

<div v-click border="2 solid blue-800" bg="blue-800/20" rounded-lg p-4>
<div class="font-bold text-blue-300 mb-2">Non-saturating activations</div>
<div class="text-sm leading-relaxed opacity-90">ReLU has derivative exactly 1 for positive inputs, avoiding the small-derivative problem of sigmoid/tanh.</div>
</div>

<div v-click border="2 solid violet-800" bg="violet-800/20" rounded-lg p-4>
<div class="font-bold text-violet-300 mb-2">Residual (skip) connections</div>
<div class="text-sm leading-relaxed opacity-90">Adding an identity path around a block gives the gradient an additive route that bypasses the multiplicative chain.</div>
</div>

<div v-click border="2 solid amber-800" bg="amber-800/20" rounded-lg p-4>
<div class="font-bold text-amber-300 mb-2">Gradient clipping</div>
<div class="text-sm leading-relaxed opacity-90">Rescale the gradient vector if its norm exceeds a threshold, capping how large one update step can be.</div>
</div>

</div>

<div v-click class="mt-4 text-sm" border="2 solid white/10" bg="white/5" rounded-lg px-4 py-3>

$$
\text{if } \|\mathbf g\| > \tau: \quad \mathbf g \leftarrow \tau \cdot \frac{\mathbf g}{\|\mathbf g\|}
$$

</div>

<!--
Four standard tools, each attacking the product-of-factors problem from a different angle. He initialization (for ReLU) and Xavier/Glorot initialization (for tanh) choose the initial weight variance as a function of the number of incoming (and sometimes outgoing) connections specifically so that the variance of activations and gradients stays roughly constant layer to layer at the start of training, rather than compounding a systematic shrink or growth. Swapping sigmoid or tanh for ReLU removes the built-in derivative ceiling of 0.25 discussed on the previous slide, since ReLU's derivative is exactly 1 wherever the input is positive. Residual connections, introduced in ResNet, add the block's input directly to its output (a = F(x) + x), which means the gradient has a path with a local derivative of exactly 1 that skips the multiplicative chain entirely, letting gradients reach early layers largely undiminished even in networks hundreds of layers deep. Gradient clipping is different in kind: it does not prevent large gradients from occurring, it caps their effect after the fact by rescaling the entire gradient vector g so its Euclidean norm never exceeds a chosen threshold tau, which is especially common in RNN training where explosion is frequent. Misconception to flag: clipping fixes exploding gradients but does nothing for vanishing gradients, since it only ever shrinks gradients, never grows them. Transition: batch normalization is the next major tool, and it works by controlling activation scale directly rather than relying on initialization alone.
-->

---
glowSeed: 895
---

# Batch Normalization Stabilizes Layer Inputs

<div class="grid grid-cols-2 gap-8 items-start">
<div>
<div class="space-y-3 mt-4">
<div v-click border="2 solid white/5" bg="white/5" rounded-lg px-4 py-3>
<span class="font-bold text-teal-300">Normalize</span>
<span class="text-sm opacity-85"> — For each unit, subtract the mini-batch mean and divide by the mini-batch standard deviation, so pre-activations have mean 0 and variance 1 within the batch.</span>
</div>
<div v-click border="2 solid white/5" bg="white/5" rounded-lg px-4 py-3>
<span class="font-bold text-blue-300">Restore flexibility</span>
<span class="text-sm opacity-85"> — A fixed mean-0, variance-1 distribution can limit what the layer can represent, so learn a scale $\gamma$ and shift $\beta$ per unit to undo normalization if that helps.</span>
</div>
<div v-click border="2 solid amber-800" bg="amber-800/20" rounded-lg px-4 py-3>
<span class="font-bold text-amber-300">Why it helps</span>
<span class="text-sm opacity-85"> — It reduces internal covariate shift (each layer's input distribution drifting as earlier weights update) and empirically smooths the loss landscape, permitting larger, more stable learning rates.</span>
</div>
</div>
</div>
<div>
<div v-click class="mt-4" style="font-size: .9em" border="2 solid teal-800" bg="teal-800/20" rounded-lg px-4 py-3>

$$
\mu_B=\frac1m\sum_{i=1}^m z_i,\qquad \sigma_B^2=\frac1m\sum_{i=1}^m(z_i-\mu_B)^2
$$

$$
\hat z_i=\frac{z_i-\mu_B}{\sqrt{\sigma_B^2+\epsilon}},\qquad y_i=\gamma\hat z_i+\beta
$$

</div>

<div v-click class="mt-4 text-sm opacity-90">
$z_i$: pre-activation of one unit for example $i$ in the batch. $m$: batch size. $\epsilon$: tiny constant (e.g. $10^{-5}$) preventing division by zero. $\gamma,\beta$: learned per-unit parameters, updated by gradient descent like any weight.
</div>

</div>
</div>

<!--
Walk the formula left to right. mu_B and sigma_B squared are the mean and variance of one unit's pre-activation z, computed across the m examples currently in the mini-batch — not across the whole dataset, and not across other units. z-hat-sub-i is the normalized value: subtract the batch mean, divide by the batch standard deviation (with epsilon added under the square root purely to avoid dividing by zero when a batch happens to have near-zero variance). If training stopped there, every unit would be forced into a mean-0, variance-1 distribution at every layer, which can actually remove representational power the network needs — for example a sigmoid unit restricted to its near-linear region around 0 cannot express strong saturation even when that is useful. So batch norm adds two more learnable parameters per unit, gamma and beta, which linearly rescale and shift the normalized value; gamma and beta are trained by backpropagation exactly like any other weight, and if the optimal choice is to undo normalization entirely, the network can learn gamma equal to the batch standard deviation and beta equal to the batch mean, recovering the original z. The stated benefit is reducing internal covariate shift — the tendency for a layer's input distribution to keep shifting as every earlier layer's weights update during training — and more recent analysis shows batch norm also smooths the loss surface (reduces the Lipschitz constant of the loss and its gradient), which is why it tolerates noticeably larger learning rates. Transition: let's normalize an actual small batch of numbers by hand to see this is genuinely simple arithmetic.
-->

---
glowSeed: 896
---

# Batch Norm — A Worked Numeric Example

<div class="grid grid-cols-2 gap-8 items-start mt-2">
<div>

<v-clicks>

- One unit's pre-activations across a batch of 4 examples: $z = [2,\,4,\,4,\,6]$
- Batch mean: $\mu_B = (2+4+4+6)/4 = 4$
- Batch variance: $\sigma_B^2 = \big[(2{-}4)^2+(4{-}4)^2+(4{-}4)^2+(6{-}4)^2\big]/4 = 8/4 = 2$
- Batch std: $\sqrt{\sigma_B^2+\epsilon}\approx\sqrt{2}\approx 1.414$

</v-clicks>

</div>
<div>

<div v-click border="2 solid teal-800" bg="teal-800/20" rounded-lg p-4 style="font-size:.9em">
Normalized: $\hat z = \dfrac{z-4}{1.414} = [-1.414,\ 0,\ 0,\ 1.414]$
</div>

<div v-click class="mt-3" border="2 solid blue-800" bg="blue-800/20" rounded-lg p-4 style="font-size:.9em">
With learned $\gamma=2,\ \beta=1$: $y = 2\hat z + 1 = [-1.83,\ 1,\ 1,\ 3.83]$
</div>

<div v-click class="mt-3 text-sm opacity-85">
Check: the normalized values $\hat z$ have mean 0 and variance 1 by construction — verify $(-1.414+0+0+1.414)/4=0$.
</div>

</div>
</div>

<!--
Every number here can be checked by hand. The raw pre-activations for one unit across a batch of four examples are 2, 4, 4, and 6; their mean is (2+4+4+6)/4 = 4. The variance is the average squared deviation from that mean: (2-4) squared is 4, (4-4) squared is 0 twice, and (6-4) squared is 4, giving (4+0+0+4)/4 = 2, so the standard deviation is the square root of 2, about 1.414 (epsilon is negligible here and omitted from the arithmetic). Subtracting the mean and dividing by the standard deviation turns [2,4,4,6] into [-1.414, 0, 0, 1.414] — notice this new list has mean exactly 0 and variance exactly 1, which is the entire point of the normalization step and is worth verifying by summing the four values. Finally applying a learned scale gamma=2 and shift beta=1 (arbitrary example values a network might learn) gives y = 2*z-hat + 1 = [-1.83, 1, 1, 3.83], which no longer has mean 0 or variance 1, because gamma and beta are free to move the distribution wherever training finds useful. Common student error: forgetting that the mean and variance used here are computed only over the current mini-batch and only for this one unit — every unit in a batch-normalized layer has its own independent mu_B, sigma_B, gamma, and beta. Transition: this batch-based statistic works fine during training, but it creates a subtlety at test time.
-->

---
glowSeed: 897
---

# Batch Norm — Training Versus Inference

<div class="grid grid-cols-2 gap-4 mt-6">

<div v-click border="2 solid teal-800" bg="teal-800/20" rounded-lg p-4>
<div class="font-bold text-teal-300 mb-2">Training</div>
<div class="text-sm leading-relaxed opacity-90">Normalize using the current mini-batch's own $\mu_B,\sigma_B^2$. Also update running (exponential moving average) estimates of the mean and variance across all batches seen so far.</div>
</div>

<div v-click border="2 solid blue-800" bg="blue-800/20" rounded-lg p-4>
<div class="font-bold text-blue-300 mb-2">Inference</div>
<div class="text-sm leading-relaxed opacity-90">Use the stored running mean and running variance instead of any batch statistic, so a single test example (batch size 1) still gets a well-defined, deterministic normalization.</div>
</div>

</div>

<div v-click class="mt-4 text-sm" border="2 solid amber-800" bg="amber-800/20" rounded-lg px-4 py-3>
Common bug: forgetting to switch a framework's batch norm layer into evaluation mode (<code>model.eval()</code> in PyTorch, <code>training=False</code> in Keras) — the model then keeps using per-batch statistics at test time, giving inconsistent, batch-size-dependent predictions.
</div>

<!--
Batch normalization behaves differently depending on whether the network is training or being evaluated, and this is one of the most common sources of subtle bugs in practice. During training, each forward pass normalizes using that specific mini-batch's own mean and variance — batch statistics that change from step to step — and simultaneously updates a running mean and running variance, typically via an exponential moving average with some momentum term (for example running_mean = 0.9*running_mean + 0.1*batch_mean), that accumulate an estimate of the statistics over the whole training distribution. At inference time we generally do not have a meaningful "batch" — we might be scoring one example at a time — so batch norm switches to using the stored running mean and running variance instead of recomputing statistics from whatever examples happen to be present, which makes predictions deterministic and independent of what else is in the batch. The flagged misconception is exactly the bug that trips up most practitioners: PyTorch's batch norm module and Keras's BatchNormalization layer both have a training/inference mode flag, and if you forget to set it correctly (calling model.eval() in PyTorch, or passing training=False in Keras) at test time, the layer keeps computing statistics from whatever batch you pass it, which for a batch of size 1 is division by a variance of zero (or near it), producing garbage or wildly inconsistent outputs depending on batch composition. Transition: batch norm addresses training instability; the next tool, dropout, addresses overfitting.
-->

---
glowSeed: 898
---

# Batch Norm in a Network

<div class="grid grid-cols-2 gap-4 mt-6">
<div v-click border="2 solid teal-800" bg="teal-800/20" rounded-lg p-4>
<div class="font-bold text-teal-300 mb-2">Order</div>
<div class="text-sm leading-relaxed opacity-90">Dense → BatchNormalization → Activation, so the nonlinearity sees a stabilized, unit-scale input.</div>
</div>
<div v-click border="2 solid blue-800" bg="blue-800/20" rounded-lg p-4>
<div class="font-bold text-blue-300 mb-2">Benefit</div>
<div class="text-sm leading-relaxed opacity-90">More stable activations often permit larger learning rates and faster, more reliable convergence.</div>
</div>
</div>

```python
model = keras.Sequential([
    layers.Input(shape=(20,)),
    layers.Dense(64),
    layers.BatchNormalization(),
    layers.Activation("relu"),
    layers.Dense(32),
    layers.BatchNormalization(),
    layers.Activation("relu"),
    layers.Dense(1, activation="sigmoid"),
])
```

<!--
This code shows the standard placement: a Dense (fully connected) layer computes the linear pre-activation z = Wx + b, BatchNormalization normalizes and rescales that z per the two-step formula from earlier slides, and only then does the Activation layer (ReLU here) apply the nonlinearity — so ReLU always receives an input that has been recentered and rescaled to a controlled range rather than whatever raw, potentially drifting scale the previous layer's weights happen to produce. Keras's BatchNormalization layer automatically tracks the running mean and variance during training and switches to them during inference, handling the train/eval distinction from the previous slide without extra code, as long as the model is called in the correct mode (model(x, training=True/False) or via model.fit/model.predict, which set this automatically). The practical benefit repeatedly observed is that because batch norm keeps each layer's input distribution roughly stable regardless of how earlier weights have moved, gradients behave more predictably, which tolerates noticeably larger learning rates than an equivalent unnormalized network and generally speeds up convergence. A batch-dependent amount of noise in the batch statistics also acts as a mild, incidental regularizer, but this is a side effect — stabilizing training is the primary purpose, and dropout (next) is the tool purpose-built for regularization. Transition: now let's look at dropout, the standard regularization technique for reducing overfitting in deep networks.
-->

---
glowSeed: 899
---

# Dropout Trains Randomly Thinned Networks

<div class="grid grid-cols-2 gap-8 items-start">
<div>
<div class="space-y-3 mt-4">
<div v-click border="2 solid white/5" bg="white/5" rounded-lg px-4 py-3>
<span class="font-bold text-teal-300">Training</span>
<span class="text-sm opacity-85"> — Randomly zero out each unit's activation with probability $p$ (independently, every forward pass), forcing the network to route information through many different subsets of units.</span>
</div>
<div v-click border="2 solid white/5" bg="white/5" rounded-lg px-4 py-3>
<span class="font-bold text-blue-300">Pressure</span>
<span class="text-sm opacity-85"> — Because any unit may vanish at any step, no small set of neurons can become individually indispensable; the network is pushed toward redundant, distributed representations.</span>
</div>
<div v-click border="2 solid amber-800" bg="amber-800/20" rounded-lg px-4 py-3>
<span class="font-bold text-amber-300">Inference</span>
<span class="text-sm opacity-85"> — Use the full, un-thinned network with no masking; inverted dropout already rescaled activations during training so no further adjustment is needed at test time.</span>
</div>
</div>
</div>
<div>
<svg role="img" aria-label="Network diagram for Dropout Trains Randomly Thinned Networks" viewBox="0 0 440 290" class="w-full max-w-xl mx-auto mt-8">
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
\tilde a_j=\frac{m_j}{1-p}a_j,\qquad m_j\sim\mathrm{Bernoulli}(1-p)
$$

</div>
</div>
</div>

<!--
Define the formula precisely. a_j is unit j's activation before dropout, p is the drop probability (a hyperparameter, commonly 0.2 to 0.5), and m_j is a Bernoulli random variable equal to 1 with probability (1-p) — i.e. m_j indicates whether unit j survives this forward pass — and equal to 0 with probability p, meaning the unit is zeroed. The tilde-a_j on the left is the actual activation used going forward: if the unit is dropped (m_j=0), tilde-a_j is 0; if it survives (m_j=1), tilde-a_j is a_j divided by (1-p), i.e. scaled up. This division by (1-p) during training is called "inverted dropout" and is the modern standard implementation (as opposed to older dropout, which left training activations unscaled and instead multiplied everything by (1-p) at test time) — inverted dropout is preferred specifically because it keeps the test-time forward pass identical to a network with no dropout at all, simplifying deployment code. Each of the m_j values is resampled independently for every unit on every single forward pass (not once per epoch), so a network with dropout is effectively training an enormous ensemble of different thinned sub-networks that share weights. Misconception to flag directly: dropout is active ONLY during training; at test time the model must run in evaluation mode with dropout disabled and use every unit at full strength — leaving dropout active at inference (or, under the old non-inverted convention, forgetting to rescale) is a common and consequential bug that silently degrades predictions. Transition: let's trace one small dropout mask through actual numbers to see the scaling arithmetic explicitly.
-->

---
glowSeed: 900
---

# Dropout — A Worked Numeric Example

<div class="grid grid-cols-2 gap-8 items-start mt-2">
<div>

<v-clicks>

- Activations before dropout: $a = [1,\ 2,\ 3,\ 4]$, with $p = 0.5$
- One sampled mask (unit survives if $m_j=1$): $m = [1,\ 0,\ 1,\ 0]$
- Scale factor for surviving units: $1/(1-p) = 1/0.5 = 2$
- Applied: $\tilde a = [1\cdot2\cdot1,\ 0,\ 3\cdot2\cdot1,\ 0] = [2,\ 0,\ 6,\ 0]$

</v-clicks>

</div>
<div>

<div v-click border="2 solid teal-800" bg="teal-800/20" rounded-lg p-4 style="font-size:.9em">
$E[\tilde a_j] = (1-p)\cdot\dfrac{1}{1-p}\cdot a_j = a_j$
</div>

<div v-click class="mt-3 text-sm opacity-85">
The scaling makes each unit's expected activation under dropout equal to its original, un-dropped value — this is exactly why no rescaling is needed at test time.
</div>

</div>
</div>

<!--
Trace the arithmetic directly. We start with activations 1, 2, 3, and 4 for four units, and a drop probability p=0.5, so the survival probability (1-p) is also 0.5 and the inverted-dropout scale factor 1/(1-p) is 2. A concrete sampled mask [1,0,1,0] means unit 1 survives, unit 2 is dropped, unit 3 survives, unit 4 is dropped; applying tilde-a_j = m_j/(1-p) times a_j gives unit 1 as 1 times 2 times 1 = 2, unit 2 as 0 (dropped), unit 3 as 3 times 2 times 1 = 6, and unit 4 as 0 (dropped), producing tilde-a = [2, 0, 6, 0]. The expected-value calculation at the bottom is the theoretical justification for the whole scheme: E[tilde a_j] = (1-p) times (1/(1-p)) times a_j, and the (1-p) and 1/(1-p) cancel exactly, leaving a_j — so averaged over many random masks, the dropout-scaled activation has exactly the same expectation as the original un-dropped activation. That is precisely why, at test time, we can simply turn dropout off and use the raw activations directly: the training-time scaling already matched the expected magnitude, so no further adjustment is needed, which is the practical payoff of the "inverted" convention over the older approach. Transition: with the mechanism concrete, let's connect dropout to two different theoretical explanations for why it improves generalization.
-->

---
glowSeed: 901
---

# Dropout Connects Regularization and Ensembling

<div class="grid grid-cols-3 gap-4 mt-6">
<div v-click border="2 solid teal-800" bg="teal-800/20" rounded-lg p-4>
<div class="font-bold text-teal-300 mb-2">Regularization view</div>
<div class="text-sm leading-relaxed opacity-90">Random removal prevents brittle co-adaptation — units can no longer rely on one specific partner always being present, so each must learn features that are useful on their own.</div>
</div>
<div v-click border="2 solid blue-800" bg="blue-800/20" rounded-lg p-4>
<div class="font-bold text-blue-300 mb-2">Ensemble view</div>
<div class="text-sm leading-relaxed opacity-90">Each random mask defines a different "thinned" sub-network; training with dropout approximates training and then averaging an exponential number of such sub-networks.</div>
</div>
<div v-click border="2 solid amber-800" bg="amber-800/20" rounded-lg p-4>
<div class="font-bold text-amber-300 mb-2">Important caveat</div>
<div class="text-sm leading-relaxed opacity-90">Unlike true bagging, the sub-networks are not independent — they share the same underlying weights, so this is an approximation, not literal ensemble training.</div>
</div>
</div>

<!--
Two complementary stories explain why dropout works, and both are worth holding onto. The regularization story: co-adaptation means one unit's usefulness comes to depend on a specific other unit always firing alongside it, a fragile, overly specific joint representation; because dropout can silence any unit at any training step, no unit can safely assume any particular neighbor will be present, which pressures every unit toward learning features that are independently useful, producing a more robust, redundant representation. The ensembling story: sampling a different Bernoulli mask on every forward pass is mathematically like training a different, smaller sub-network (formed by only the surviving units) on each mini-batch, and since there are 2 to the power of (number of units) possible masks, dropout is training an enormous, exponentially large collection of overlapping sub-networks; using the full network at test time is understood as an efficient approximation to averaging the predictions of all those sub-networks. The caveat is essential for accuracy: in a genuine ensemble (e.g. bagging in the ensemble-methods unit), each model has its own independently trained parameters, whereas here every sub-network shares the exact same weight tensor — only which units are active differs — so dropout is best described as an efficient, weight-sharing approximation to ensembling, not literal bagging. Transition: beyond batch norm and dropout, a few more standard levers round out practical training.
-->

---
glowSeed: 902
---

# Other Practical Levers: Schedules and Weight Decay

<div class="grid grid-cols-2 gap-4 mt-4">

<div v-click border="2 solid teal-800" bg="teal-800/20" rounded-lg p-4>
<div class="font-bold text-teal-300 mb-2">Learning rate schedules</div>
<div class="text-sm leading-relaxed opacity-90">Decay $\eta_t$ over training (step decay, cosine annealing) or warm it up first, so early steps are cautious, middle steps are fast, and late steps fine-tune with small, precise updates.</div>
</div>

<div v-click border="2 solid blue-800" bg="blue-800/20" rounded-lg p-4>
<div class="font-bold text-blue-300 mb-2">Weight decay (L2 regularization)</div>
<div class="text-sm leading-relaxed opacity-90">Shrink weights toward zero every step, penalizing large weights that tend to overfit and improving generalization, much like ridge regression's penalty.</div>
</div>

</div>

<div v-click class="mt-4 text-sm" border="2 solid white/10" bg="white/5" rounded-lg px-4 py-3>

$$
\theta \leftarrow \theta - \eta\big(\nabla L(\theta) + \lambda\theta\big)
$$

</div>

<div v-click class="mt-3 text-sm opacity-80">
$\eta$: learning rate (possibly scheduled, $\eta_t$). $\lambda$: weight decay coefficient. $\nabla L(\theta)$: gradient of the data loss with respect to the weights $\theta$.
</div>

<!--
Two more standard tools that round out a practitioner's toolkit alongside gradient control, batch norm, and dropout. Learning rate schedules change eta, the step size in gradient descent, as a function of training progress rather than holding it fixed: step decay drops eta by a fixed factor every so many epochs, cosine annealing smoothly decreases it following a cosine curve down to near zero, and warmup starts eta small and ramps it up over the first few hundred steps before decaying, which helps avoid instability during the very first updates when weights (and, relatedly, batch norm's running statistics) are still far from a good region. Weight decay adds a penalty term lambda times theta to the update, where lambda is a small positive coefficient and theta is the current weight vector; this is mathematically the gradient of an added L2 penalty (lambda/2) times the squared norm of theta on the loss function, so it continuously pulls every weight toward zero at each step, in direct analogy to the ridge regression penalty covered in the regularization unit — smaller weights generally correspond to smoother, less extreme functions that overfit less. One subtlety worth flagging for adaptive optimizers like Adam: naively adding the L2 penalty to the gradient before Adam's per-parameter scaling is not equivalent to true weight decay, which is why AdamW decouples weight decay from the gradient-based update, applying the theta-shrinking step directly rather than through the adaptive gradient computation. Transition: let's assemble every tool covered today into one complete, modern dense network.
-->

---
glowSeed: 903
---

# A Complete Modern Dense Network

<div class="grid grid-cols-2 gap-4 mt-6">
<div v-click border="2 solid teal-800" bg="teal-800/20" rounded-lg p-4>
<div class="font-bold text-teal-300 mb-2">Stability</div>
<div class="text-sm leading-relaxed opacity-90">Batch normalization plus ReLU keeps each layer's inputs well-scaled and avoids the vanishing-derivative problem of saturating activations.</div>
</div>
<div v-click border="2 solid blue-800" bg="blue-800/20" rounded-lg p-4>
<div class="font-bold text-blue-300 mb-2">Generalization</div>
<div class="text-sm leading-relaxed opacity-90">Dropout between learned blocks prevents co-adaptation and approximates averaging many sub-networks, reducing overfitting.</div>
</div>
</div>

```python
model = keras.Sequential([
    layers.Input(shape=(20,)),
    layers.Dense(128), layers.BatchNormalization(),
    layers.Activation("relu"), layers.Dropout(0.3),
    layers.Dense(64), layers.BatchNormalization(),
    layers.Activation("relu"), layers.Dropout(0.3),
    layers.Dense(1, activation="sigmoid"),
])
```

<!--
Read this architecture as a checklist of everything covered today. Each block is Dense (the linear map z = Wx+b, initialized with a scheme like He initialization to start the vanishing/exploding product near magnitude 1), BatchNormalization (normalize by the current batch's mean/variance during training, then scale and shift by learned gamma and beta, switching to running statistics at inference), Activation with ReLU (avoiding the small-derivative problem of sigmoid/tanh), and finally Dropout(0.3) (randomly zeroing 30% of units per forward pass during training only, using inverted dropout so no rescaling is needed at test time). The final Dense(1, activation="sigmoid") layer is the output for binary classification and deliberately has no batch norm or dropout after it, since we want a clean, deterministic probability estimate, not a regularized or batch-dependent one. Ask students to identify which earlier lecture supplied each component: weight initialization and the Dense layer come from the forward/backward propagation unit, ReLU and gradient clipping come from the vanishing/exploding gradient discussion, BatchNormalization comes from the batch-norm slides, and Dropout comes from the dropout slides — this is the moment the whole unit's separate pieces visibly compose into one working recipe. Misconception to flag one more time: both BatchNormalization and Dropout behave differently in training versus inference mode, and Keras handles this automatically via model.fit versus model.predict, but a custom training loop must set the mode explicitly or these layers will silently misbehave. Transition: close by summarizing the three big ideas and previewing what comes next.
-->

---
glowSeed: 904
---

# Make Deep Networks Train and Generalize

<div class="mt-8"><div class="grid grid-cols-3 gap-4 mt-6">
<div v-click border="2 solid teal-800" bg="teal-800/20" rounded-lg p-4>
<div class="font-bold text-teal-300 mb-2">Scale</div>
<div class="text-sm leading-relaxed opacity-90">Control the product of derivatives through depth: good initialization, non-saturating activations, skip connections, and gradient clipping.</div>
</div>
<div v-click border="2 solid blue-800" bg="blue-800/20" rounded-lg p-4>
<div class="font-bold text-blue-300 mb-2">Batch norm</div>
<div class="text-sm leading-relaxed opacity-90">Stabilize each layer's input distribution using batch statistics at train time, running statistics at test time.</div>
</div>
<div v-click border="2 solid amber-800" bg="amber-800/20" rounded-lg p-4>
<div class="font-bold text-amber-300 mb-2">Dropout</div>
<div class="text-sm leading-relaxed opacity-90">Regularize with random masks during training only, approximating an ensemble of shared-weight sub-networks.</div>
</div>
</div></div>

<div v-click class="mt-10 text-center text-lg" border="2 solid white/10" bg="white/5" rounded-lg px-6 py-4>Next: open the optimizer black box — SGD, momentum, RMSProp, and Adam.</div>

<!--
Close the neural-networks unit by restating it as architecture plus gradients plus practical stabilization. First, depth turns backpropagation into a long product of derivatives (the chain rule applied layer after layer), and that product can shrink toward zero or blow up toward infinity depending on the typical magnitude of each factor — mitigated by careful initialization, ReLU-style activations, residual connections, and gradient clipping. Second, batch normalization stabilizes each layer's input distribution by subtracting the batch mean, dividing by the batch standard deviation, then applying a learned scale gamma and shift beta, using batch statistics during training and accumulated running statistics during inference — remember the common bug of leaving a model in the wrong train/eval mode. Third, dropout regularizes by randomly zeroing units during training with probability p, scaling survivors by 1/(1-p) so expected activation magnitude is preserved (inverted dropout), and using the full network at test time; this approximates training and averaging many weight-sharing sub-networks and prevents brittle co-adaptation between units. Together with learning rate schedules and weight decay, these are the standard levers that turn a network that merely runs into one that reliably trains and generalizes. Transition: everything so far has assumed we already have a working weight-update rule; next we open that black box and compare SGD, momentum, RMSProp, and Adam.
-->

---
layout: center
class: text-center
glowSeed: 905
---

# Thank You

### Questions &amp; Discussion

<div class="pt-6 opacity-80">
Practical Training: Batch Normalization and Dropout · Neural Networks and Deep Learning Basics
</div>

<!--
Take questions before moving to the optimizers lecture (SGD, momentum, RMSProp, and Adam). Good questions to prompt if the room is quiet: why does batch norm need different behavior at train versus test time, why does inverted dropout scale during training rather than at test time, and how does gradient clipping differ from the other three mitigations for exploding gradients covered today. Confirm students can state, without notes, the two formulas from this deck: batch norm's z-hat = (z - mu_B)/sqrt(sigma_B^2 + epsilon) followed by y = gamma*z-hat + beta, and dropout's tilde-a_j = (m_j/(1-p))*a_j with m_j ~ Bernoulli(1-p).
-->
