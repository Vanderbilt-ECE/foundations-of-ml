---
theme: default
highlighter: shiki
css: unocss
colorSchema: dark
title: 'Neural Networks: From Perceptrons to Multilayer Networks'
info: |
  ## Neural Networks: From Perceptrons to Multilayer Networks
  What a neural network is, what it can solve, and how it learns
class: text-center
transition: fade-out
lineNumbers: false
drawings:
  persist: false
mdc: true
duration: 50min
vite:
  server:
    fs:
      strict: false
glowSeed: 410
---

# Neural Networks {.!text-5xl}

### From perceptrons to multilayer networks: what they are, what they solve, how they learn

<div class="mt-2 max-w-3xl mx-auto">
<NetFlow :layers="[3, 5, 5, 2]" mode="forward" :height="250" />
</div>

<div class="opacity-70 text-sm">Neural Networks and Deep Learning Basics · Foundations of Machine Learning</div>

<!--
Welcome to the first lecture of the neural networks unit. The animation is a real (randomly initialized) network: teal edges are positive weights, violet are negative, and the pulses are a signal flowing from the inputs on the left to the outputs on the right, one layer at a time. By the end of today, every part of this picture will have a name and a job.

Roadmap, about 50 minutes in four parts:
1. The perceptron (about 12 minutes): one artificial neuron, the line it draws, training it with the gradient descent students already know, and the problem it cannot solve, XOR.
2. Multilayer networks (about 13 minutes): how a hidden layer fixes XOR, why activation functions are essential, the common ones, and why "enough hidden units can approximate any curve."
3. What networks solve (about 15 minutes): regression, yes/no classification, and multiclass classification. Each one is live-trained in the browser on a realistic problem.
4. How they learn (about 10 minutes): the training loop, gradient descent, and backpropagation as an idea rather than a derivation.

The next deck, Training Neural Networks in Practice, picks up from there: initialization, optimizers, learning-rate schedules, and regularization.
-->

---
glowSeed: 411
---

# You Already Know One Neuron

<div class="grid grid-cols-3 gap-5 mt-8 text-left">

<div v-click border="2 solid blue-800" bg="blue-800/20" rounded-lg p-4>
<div class="font-bold text-blue-300 mb-2">Linear regression</div>

$$
\hat y = w^\top x + b
$$

<div class="text-sm opacity-85">A weighted sum. Output: any number.</div>
</div>

<div v-click border="2 solid violet-800" bg="violet-800/20" rounded-lg p-4>
<div class="font-bold text-violet-300 mb-2">Logistic regression</div>

$$
\hat y = \sigma(w^\top x + b)
$$

<div class="text-sm opacity-85">The same sum, squashed into (0, 1). Output: a probability.</div>
</div>

<div v-click border="2 solid teal-800" bg="teal-800/20" rounded-lg p-4>
<div class="font-bold text-teal-300 mb-2">An artificial neuron</div>

$$
\hat y = f(w^\top x + b)
$$

<div class="text-sm opacity-85">The same sum, through <b>some</b> function f, the <b>activation</b>.</div>
</div>

</div>

<div v-click class="mt-10 text-xl">A neural network is many of these, <span v-mark.underline.teal="4">wired together in layers</span>.</div>

<!--
Start from what students already have.

[click] Linear regression computes a weighted sum of the inputs plus a bias.

[click] Logistic regression computes the exact same weighted sum and passes it through the sigmoid so the output lands between 0 and 1.

[click] An artificial neuron is the same pattern with the squashing function left open: any function f applied to the weighted sum. We call f the activation function. Linear regression is a neuron whose f is the identity; logistic regression is a neuron whose f is the sigmoid.

[click] So there is nothing mysterious inside a neural network. Every unit computes something students have already computed in this course. The new ideas are only about how many of these units we use and how we connect them. Everything else today follows from that.
-->

---
glowSeed: 412
clicks: 3
---

# The Perceptron: Weigh, Sum, Decide

<NeuronAnim :step="$clicks" />

<div class="grid grid-cols-3 gap-4 text-sm text-left">
<div class="reveal" :class="{ shown: $clicks >= 1 }" border="2 solid white/5" bg="white/5" rounded-lg px-3 py-2><b class="text-teal-300">1 · Weigh</b>: each input is multiplied by its weight. Weights can be negative.</div>
<div class="reveal" :class="{ shown: $clicks >= 2 }" border="2 solid white/5" bg="white/5" rounded-lg px-3 py-2><b class="text-amber-300">2 · Sum</b>: add the products and the bias b to get z.</div>
<div class="reveal" :class="{ shown: $clicks >= 3 }" border="2 solid white/5" bg="white/5" rounded-lg px-3 py-2><b class="text-amber-300">3 · Decide</b>: output 1 if z &gt; 0, otherwise 0.</div>
</div>

<!--
Rosenblatt's perceptron (1958) is the oldest artificial neuron that learns, and it is a neuron whose activation is a hard step.

Walk the numbers. Three inputs: 0.8, 0.3, 0.6.

[click] Each input travels along its edge and gets multiplied by that edge's weight: 0.8 × 1.5 = 1.2, 0.3 × −2.0 = −0.6, 0.6 × 1.0 = 0.6. Point out that the weights are what the model learns. A big positive weight means "this input pushes toward yes," and a negative weight means "this input pushes toward no." Edge thickness shows weight size, and violet shows a negative weight.

[click] The products and the bias are summed: 1.2 − 0.6 + 0.6 − 0.5 = 0.7. The bias is a threshold that moves the cutoff: with b = −0.5, the weighted evidence has to exceed 0.5 before the perceptron says yes.

[click] The step function asks one question: is z above zero? It is, so the output is 1.

Ask the class: which single weight change would flip this output to 0? (Any change that drops z below zero, for example making w₃ = −0.5.)
-->

---
glowSeed: 438
---

# A Perceptron Is Logistic Regression

<div class="text-lg opacity-85 mt-1">Same weighted sum, same yes/no decision. Sigmoid or step on the output doesn't matter.</div>

<div class="grid grid-cols-2 gap-8 mt-4 items-center text-left">

<div border="2 solid white/5" bg="white/5" rounded-lg p-3>
<StepVsSigmoid />
</div>

<div class="flex flex-col gap-3 text-base">

<div v-click border="2 solid violet-800" bg="violet-800/20" rounded-lg px-4 py-2>
<div class="font-bold text-violet-300">Logistic regression</div>

$\hat y = \sigma(w^\top x + b)$, then predict 1 if $\hat y > 0.5$

</div>

<div v-click border="2 solid white/10" bg="white/5" rounded-lg px-4 py-2>
<div class="font-bold text-slate-300">Perceptron</div>

$\hat y = \text{step}(w^\top x + b)$: predict 1 if $z > 0$

</div>

<div v-click border="2 solid amber-800" bg="amber-800/20" rounded-lg px-4 py-2>

$\sigma(z) > 0.5 \iff z > 0$. Both say yes on the same side of the <b>same line</b>, $w^\top x + b = 0$.

</div>

</div>

</div>

<div v-click class="mt-4 text-xl text-center">You already know how to build and train this. <span v-mark.underline.teal="4">It's logistic regression.</span></div>

<!--
Pause here before going further, because this is the main reassurance of the lecture: a single perceptron is not a new model. It's the logistic regression students already built.

Point at the plot. The violet curve is the sigmoid from logistic regression and the gray curve is the perceptron's step. Both cross the amber 0.5 line at exactly z = 0. The sigmoid is just a smoothed-out step.

[click] Logistic regression: compute the weighted sum z, squash it with the sigmoid to get a probability, and to make a yes/no call, predict 1 when that probability is above 0.5.

[click] Perceptron: compute the same weighted sum z, and predict 1 when z is above 0. There's no probability in between.

[click] These are the same rule. The sigmoid is above 0.5 exactly when z is above 0 (σ(0) = 0.5 and σ always increases). So for the same weights, both models give the same answer for every input, and they share the decision boundary w·x + b = 0. Whether you put a sigmoid or a step on the output makes no difference to the classification. The only thing the sigmoid adds is a confidence level: how far from 0.5 you are.

[click] So students already know how to do this. Everything they learned about logistic regression (weights, bias, a linear boundary, training by gradient descent) carries over. The next slide shows the line this draws, and the one after shows that training it is the same gradient descent.

If someone asks why we ever bother with the sigmoid: it gives a smooth loss with a useful gradient everywhere. The step is flat almost everywhere, which is why the perceptron's training rule (in two slides) looks at z directly instead of the step output. That comes up again on the activation-functions slide.
-->

---
glowSeed: 413
---

# A Perceptron Draws a Line

<PerceptronPlay />

<div class="mt-3 text-sm" border="2 solid teal-800" bg="teal-800/20" rounded-lg px-4 py-2>
<b class="text-teal-300">The boundary is where z = 0:</b> w₁x₁ + w₂x₂ + b = 0, a straight line. The weights set its tilt, the bias slides it, and w points toward the "yes" side.
</div>

<!--
This slide is interactive: drag the sliders live.

The data is an admissions problem: two standardized scores per applicant (exam on x₁, interview on x₂), teal circles admitted and violet squares not. The perceptron says "admit" when w₁x₁ + w₂x₂ + b > 0, so the boundary between its two answers is the set of points where that sum is exactly zero. In two dimensions that's a line. In three it's a plane, and in general a hyperplane.

Things to demonstrate by dragging:
- Change b only: the line slides without rotating.
- Change w₁ and w₂: the line rotates. The amber arrow (the weight vector) always stays perpendicular to the line and points into the "+1" region.
- Doubling all three numbers leaves the line in the same place. Only the direction matters for the decision.

Red rings mark misclassified points. Ask a student to call out slider moves until the count reaches 0 (around w₁ ≈ 0.9, w₂ ≈ 0.6, b ≈ −0.1 works). The point to land: whatever the weights, a single perceptron can only ever draw a straight boundary. Hold onto that; it's about to matter.
-->

---
glowSeed: 439
clicks: 6
---

# Why "Neuron"? The Biology Behind the Perceptron

<div class="grid grid-cols-5 gap-6 mt-4 items-center text-left">

<div class="col-span-2" border="2 solid white/5" bg="white/5" rounded-lg p-3>
<BioNeuron :step="$clicks" />
</div>

<div class="col-span-3 flex flex-col gap-2 text-sm">

<div class="reveal grid grid-cols-2 gap-3" :class="{ shown: $clicks >= 1 }" border="2 solid white/5" bg="white/5" rounded-lg px-3 py-1.5>
<div><b class="text-blue-300">Dendrites</b> receive signals from other neurons</div>
<div>→ the <b>inputs</b> x₁, …, xₙ</div>
</div>

<div class="reveal grid grid-cols-2 gap-3" :class="{ shown: $clicks >= 2 }" border="2 solid white/5" bg="white/5" rounded-lg px-3 py-1.5>
<div><b class="text-teal-300">Synapses</b> are strong or weak, exciting or inhibiting</div>
<div>→ the <b>weights</b> w, positive or negative</div>
</div>

<div class="reveal grid grid-cols-2 gap-3" :class="{ shown: $clicks >= 3 }" border="2 solid white/5" bg="white/5" rounded-lg px-3 py-1.5>
<div><b class="text-amber-300">Cell body</b> adds up all incoming charge</div>
<div>→ the <b>sum</b> z = wᵀx + b</div>
</div>

<div class="reveal grid grid-cols-2 gap-3" :class="{ shown: $clicks >= 4 }" border="2 solid white/5" bg="white/5" rounded-lg px-3 py-1.5>
<div><b class="text-amber-300">Fires</b> only past a threshold, all or nothing</div>
<div>→ the <b>step</b>: output 1 if z &gt; 0 (bias = −threshold)</div>
</div>

<div class="reveal grid grid-cols-2 gap-3" :class="{ shown: $clicks >= 5 }" border="2 solid white/5" bg="white/5" rounded-lg px-3 py-1.5>
<div><b class="text-violet-300">Axon</b> carries the spike to the next neurons</div>
<div>→ the <b>output</b>, which can feed other units</div>
</div>

</div>

</div>

<div class="reveal mt-5 text-base" :class="{ shown: $clicks >= 6 }" border="2 solid teal-800" bg="teal-800/20" rounded-lg px-4 py-2>
<b class="text-teal-300">The brain learns by changing synapse strengths. A perceptron learns by changing w.</b> <span class="opacity-75">It's a loose sketch, not a brain model: real neurons spike over time and are far messier. But the idea stuck.</span>
</div>

<!--
Now that students have seen what a perceptron computes, give them the "why it looks like this." The design is a deliberately simplified copy of a biological neuron. McCulloch and Pitts proposed the threshold-neuron model in 1943; Rosenblatt's 1958 perceptron added the part that learns the weights.

The picture lights up one part per click, matching the row on the right.

[click] Dendrites. The branching fibers on the left receive signals from many other neurons. Those incoming signals are the perceptron's inputs.

[click] Synapses. Each connection has its own strength, which is why the dots at the tips are different sizes. Some connections excite the neuron (push it toward firing) and some inhibit it (push it away). That's exactly a weight: big or small, positive or negative. Point back to the violet negative-weight edges on the earlier perceptron slide.

[click] Cell body. All the incoming charge accumulates here. Excitatory inputs add, inhibitory inputs subtract. That's the weighted sum z.

[click] Threshold and firing. At the axon hillock, if the total charge crosses a threshold, the neuron fires a spike, and that spike is always the same size. It either fires or it doesn't, which biologists call "all or nothing." That's the step function. The threshold becomes the bias: "fire if w·x > θ" is the same as "fire if w·x − θ > 0", so b = −θ.

[click] Axon. The spike travels down the axon to the terminals, which form synapses on other neurons' dendrites. One neuron's output becomes another's input. That's the seed of the idea that the next section builds on: wire these into layers.

[click] Learning. In the brain, learning is largely changing synapse strengths (Hebb, 1949: "cells that fire together wire together"). In a perceptron, learning is changing the weights, which is exactly what the next slide does with gradient descent.

Be honest about the limits: real neurons communicate with timed spike trains, have complex dendritic processing, and don't learn by gradient descent. Modern neural networks have drifted far from biology (ReLU, softmax, and backprop have no clean biological counterpart). The analogy explains the name and the original design, not how modern networks work.
-->

---
glowSeed: 414
---

# Training a Perceptron Is Gradient Descent

<div class="text-lg opacity-85 mt-2">The recipe you already know: pick a loss, step against its gradient, one example at a time.</div>

<div class="gd-cards grid grid-cols-3 gap-5 mt-6 text-left">

<div v-click border="2 solid red-800" bg="red-800/20" rounded-lg p-4>
<div class="font-bold text-red-300 text-lg mb-2">1 · Loss</div>

$$
L(w,b) = \textstyle\sum_i \max(0,\, -y_i z_i)
$$

<div class="text-sm opacity-85">

with $z_i = w^\top x_i + b$ and labels $y_i = \pm 1$. Zero for a correct point; grows the further a point sits on the wrong side.

</div>
</div>

<div v-click border="2 solid amber-800" bg="amber-800/20" rounded-lg p-4>
<div class="font-bold text-amber-300 text-lg mb-2">2 · Gradient = derivative</div>

$$
\nabla_w = -y\,x, \qquad \nabla_b = -y
$$

<div class="text-sm opacity-85">of one misclassified point's loss term, with respect to w and b. A correct point's term is flat at zero, so its gradient is 0 and nothing happens.</div>
</div>

<div v-click border="2 solid teal-800" bg="teal-800/20" rounded-lg p-4>
<div class="font-bold text-teal-300 text-lg mb-2">3 · SGD step</div>

$$
w \leftarrow w - \eta\nabla_w = w + \eta\,y\,x
$$

$$
b \leftarrow b + \eta\,y
$$

<div class="text-sm opacity-85">Exactly Rosenblatt's 1958 perceptron rule.</div>
</div>

</div>

<div v-click class="mt-6 text-base opacity-90">

Compare logistic regression's SGD step, $\theta \leftarrow \theta - \eta\,(\sigma(z) - y)\,x$: the same <b>error × input</b> shape. The perceptron uses a hard yes/no instead of a probability, and only wrong points contribute.

</div>

<style>
/* keep the three cards' display equations inside their boxes */
.gd-cards .katex-display { font-size: 0.92em; margin: 0.6em 0; }
</style>

<!--
Students have already seen gradient descent in the Core ML Concepts unit: choose a loss, compute its gradient, and step the parameters against it, w ← w − η∇L. They also saw the stochastic version, which uses one example per step. Training a perceptron is exactly that, with one particular loss. So rather than presenting the perceptron rule as a separate trick, frame it as gradient descent they already know. The next slide compares the full-batch and stochastic versions side by side; the one after steps through SGD one click at a time.

[click] The loss. Use labels +1 and −1, so y·z is positive exactly when a point is on the correct side. max(0, −y·z) is zero for every correct point and, for a wrong one, measures how far it sits on the wrong side. Summing over all points gives the total loss.
Why not just count mistakes? A count is flat almost everywhere, so its gradient is zero and gives gradient descent nothing to follow. This loss uses the raw score z instead of the step output, so it has a slope wherever a point is wrong. (The same reason comes up again on the activation-functions slide.)

[click] The gradient of one point's term. For a correct point the term is flat at zero, so its gradient is zero and nothing happens. For a wrong point, the term is −y(w·x + b), with gradient −y·x for w and −y for b.
Remind students what "gradient" means here: the derivative of the loss with respect to each parameter, collected into a vector. ∂/∂wⱼ of −y(w·x + b) is −y·xⱼ, so stacking those gives −y·x.
The corner: right at y·z = 0, max(0, ·) has a kink, so strictly there's no derivative there. Any slope between the two sides is a valid choice (a subgradient). The perceptron rule picks the "wrong" side, updating whenever y·z ≤ 0, so a point exactly on the line counts as a mistake. ReLU has the same kink at 0, and frameworks like PyTorch simply pick a value there; it's the same convention.

[click] Plug that into the stochastic gradient descent step: w ← w − η(−y·x) = w + η·y·x, and b ← b + η·y. That's the perceptron learning rule.
Intuition: for a +1 point predicted −1, adding η·x to w raises that point's score by η‖x‖², pushing it toward the correct side.
History: Rosenblatt introduced this rule in 1958 as a mistake-driven update; reading it as SGD on the perceptron loss is the modern view.

[click] Make the connection out loud: logistic regression's SGD step was θ ← θ − η(σ(z) − y)x. The perceptron step has the same shape, error times input, but with a hard yes/no instead of a probability, and only misclassified points contribute.

If a sharp student asks: the loss is also exactly zero at w = 0, b = 0, where every score is 0 and there's no line at all. That's why the rule counts z = 0 as a mistake (it updates when y·z ≤ 0), and it's one reason this loss is a teaching device rather than what modern networks use.
-->

---
glowSeed: 437
clicks: 5
---

# Full Batch vs. Stochastic

<div class="mt-3">
<BatchVsSgd :step="$clicks" />
</div>

<div v-click="5" class="mt-3 text-base">
<span class="text-blue-300">Full batch</span>: each step uses every wrong point, so it's smooth, but you read all the data before moving once.
<span class="text-red-300">Stochastic</span>: noisy, cheap steps that often get there first. <span class="opacity-80">Mini-batches, used in practice, sit in between.</span>
</div>

<!--
Every wrong point counts in the loss; the question is how many of them you use per step. Same data, same starting line, same loss L = Σ max(0, −y·z) on both sides. Red outlines mark the points that are wrong right now: those are exactly the points that contribute to L. At the start there are 12, adding up to L = 4.90.

The two recipes:
Full batch: add up the gradients of ALL wrong points and take one step, w ← w + η·Σ yᵢxᵢ. That's the true gradient of L. Its step size is smaller (η = 0.05 vs 0.5) because it adds up about a dozen points' worth of gradient at once.
Stochastic: walk through the points one at a time. Each wrong point you meet triggers its own step using just its term, w ← w + η·y·x. That's what the next slide steps through.
The x-axis of the chart is the fair comparison: how many points each method has had to look at.

[click] Pass 1. Watch the right panel first: SGD takes 8 small steps as it walks the data, the amber ring marking the point behind each one. Its loss zigzags down, including the small rise. The batch panel doesn't move until it has examined all 40 points, then it takes one big step: L falls from 4.90 to 1.29.

[click] Pass 2. SGD hits L = 0 about nine points in and then stops moving: every gradient is zero. Batch takes its second step, to 0.26.

[click] Pass 3: batch, 0.11.

[click] Pass 4: batch reaches 0 too. Both found a separating line, and a different one: there are many lines with zero loss.

[click] The trade-off. Full batch follows the true gradient, so its loss curve only goes down (with a small enough η), but every step costs a full pass over the data. SGD's steps are noisy and can go uphill, but each one costs a single point, so it makes progress immediately. With millions of training examples, waiting for a full pass before each step is far too slow, which is why neural networks are trained with mini-batches: average the gradient over, say, 32 or 256 examples per step. Students saw this in the gradient descent unit; it comes back in the next deck.
-->

---
glowSeed: 433
clicks: 9
---

# Gradient Descent on a Perceptron, Step by Step

<div class="mt-4">
<PerceptronTrain data="sep" :step="$clicks" />
</div>

<!--
Same data as the slider slide: admitted (teal circles, y = +1) or not (violet squares, y = −1). Left: the current line. Right: the total perceptron loss after every gradient step. Each click takes one SGD step.

Start: the initial line misclassifies several points, and together they add up to L = 4.90. Explain the routine once: we walk through the points in order. Every correct point has zero gradient and is skipped. The first wrong point we reach triggers a step.

[click] Step 1: the red ring marks the point that was wrong. The line moves toward it (w ← w + η·y·x) and the loss drops to 2.94.
[click] Step 2: 1.65.
[click] Step 3: 0.97.
[click] Step 4: 0.90.
[click] Step 5: 0.76.
[click] Step 6: the loss goes UP, to 0.86. Pause here. Each step looks at only one point; fixing it nudged the line in a way that made other points slightly worse. That's the "stochastic" in stochastic gradient descent, exactly as students saw in the gradient descent unit. On average the steps still go downhill.
[click] Step 7: 0.39.
[click] Step 8: 0.22. That ends the first pass through the data: 8 points were wrong along the way.
[click] Step 9, early in the second pass: L = 0. Every point is on the correct side, so every gradient is zero: the next pass takes no steps and training stops.

The perceptron convergence theorem (Novikoff, 1962) guarantees this: whenever a separating line exists, this procedure reaches zero loss after a finite number of steps. The next slide shows what happens when no such line exists.
-->

---
glowSeed: 415
---

# XOR: The Problem a Line Can't Solve

<div class="grid grid-cols-[1fr_2fr] gap-6 items-center text-left">
<div class="xor-table">

| x₁ | x₂ | XOR |
|:-:|:-:|:-:|
| 0 | 0 | <span class="text-violet-300">0</span> |
| 0 | 1 | <span class="text-teal-300">1</span> |
| 1 | 0 | <span class="text-teal-300">1</span> |
| 1 | 1 | <span class="text-violet-300">0</span> |

<div v-click class="mt-3">The teal points sit on <b>opposite corners</b>. Any line that puts both on one side also takes a violet point with them.</div>

<div v-click class="mt-2 text-sm opacity-80">Minsky &amp; Papert (1969) made this limit famous, and neural network research stalled for over a decade.</div>

</div>
<div>

<PerceptronTrain data="xor" :clicks="$clicks" :finish-at="2" />

</div>
</div>

<style>
.xor-table table { font-size: 0.9rem; margin: 0; }
.xor-table td, .xor-table th { padding: 0.2rem 0.8rem; }
</style>

<!--
XOR outputs 1 when exactly one input is on. It's tiny (four points), and it's the classic case where a single perceptron fails.

The same gradient descent runs here, unchanged: same loss, same step. Watch the line: every step fixes one point and breaks another, so the line keeps jumping, and the loss chart bounces between about 0.3 and 1.8 without ever reaching zero. (The run plays in three chunks: steps 1–7 on arrival, 8–13 after the first click, and the last 7 quickly on the second click, where it stops on step 20.) There is no bug. Gradient descent can only reach zero loss if some line gets every point right, and for this data no line does.

[click] Why: the two teal points are on opposite corners of the square, and so are the two violet points. A line splits the plane into two half-planes. If both teal corners are in one half-plane, the segment joining them is too, and that segment passes through the center of the square. Any half-plane containing the center contains at least one of the violet corners as well.

[click] History, briefly: Minsky and Papert's 1969 book Perceptrons proved limits like this rigorously for single-layer networks. It contributed to the first "AI winter" of the 1970s. The fix, adding layers, was known in principle, but nobody had a practical way to train hidden layers until backpropagation became widely used in the 1980s. That's the subject of the end of today's lecture.
-->

---
glowSeed: 416
clicks: 4
---

# A Hidden Layer Moves the Points

<XorWarp :step="$clicks" />

<!--
This is the most important idea of the lecture, so go slowly and let the animation carry it.

Start: the four XOR points in the input space, impossible for one line.

[click] Add a hidden layer of two perceptrons, each drawing its own line. h₁ fires when x₁ + x₂ > 0.5, which is OR (at least one input on). h₂ fires when x₁ + x₂ > 1.5, which is AND (both inputs on). The table on the right fills in each point's hidden values.

[click] Now the key move. Stop thinking of the points as living at (x₁, x₂), and plot them at their hidden values (h₁, h₂) instead. (0,0) stays at (0,0). (1,1) goes to (1,1). And both teal points, (0,1) and (1,0), land on the same spot, (1,0). We nudged them apart slightly so both stay visible.

[click] In this new space, one ordinary line separates teal from violet: the output perceptron fires when h₁ − h₂ > 0.5, which means "OR but not AND." That is exactly XOR.

[click] Back in the original space, the whole network's decision region is the band between the two hidden lines. The network didn't find a magic curved line. It combined two straight lines into a region no single line could make.

The general lesson: each layer transforms the data into a new representation, and the next layer's job gets easier. In deep learning, "learning features" means learning these transformations instead of hand-designing them.
-->

---
glowSeed: 440
clicks: 3
---

# You've Seen This Before: The Kernel Trick

<div class="grid grid-cols-5 gap-6 mt-2 items-center text-left">

<div class="col-span-3" border="2 solid white/5" bg="white/5" rounded-lg p-2>
<XorLift3D :step="$clicks" />
</div>

<div class="col-span-2 flex flex-col gap-3 text-sm">

<div border="2 solid blue-800" bg="blue-800/20" rounded-lg px-3 py-2>
<b class="text-blue-300">SVMs:</b> a ring can't be split by a line, so you <b>added a feature</b>, z = x₁² + x₂², and a <b>plane</b> split it in 3D.
</div>

<div class="reveal" :class="{ shown: $clicks >= 1 }" border="2 solid amber-800" bg="amber-800/20" rounded-lg px-3 py-2>
<b class="text-amber-300">Here:</b> one hidden neuron adds the feature <b>h = AND(x₁, x₂)</b>. Only (1, 1) turns it on, so only (1, 1) rises.
</div>

<div class="reveal" :class="{ shown: $clicks >= 2 }" border="2 solid teal-800" bg="teal-800/20" rounded-lg px-3 py-2>
<b class="text-teal-300">Now a plane works:</b> x₁ + x₂ − 2h = 0.5. Teal below, violet above. XOR is solved.
</div>

</div>

</div>

<div class="reveal mt-4 text-base text-center" :class="{ shown: $clicks >= 3 }" border="2 solid violet-800" bg="violet-800/20" rounded-lg px-4 py-2>
<b class="text-blue-300">SVM:</b> you choose the new features. &nbsp;·&nbsp; <b class="text-teal-300">Neural network:</b> the hidden layer <span v-mark.underline.teal="3">learns them</span>.
<div class="text-xs opacity-75 mt-1">Either way, the last step is linear: a hyperplane in the new space.</div>
</div>

<!--
This slide connects the hidden layer to something students already understand from the SVM unit.

Start: remind them of "Lifting a Ring into Three Dimensions." The orange and blue rings couldn't be separated by a line in the plane. Adding a third coordinate, z = x₁² + x₂², raised the outer ring higher than the inner one, and a flat plane slid between them. The boundary was linear in the lifted space and a circle back in the original space.

The picture shows XOR in 3D, but for now every point sits on the floor: the third coordinate is 0 for all of them, so this is still the unsolvable XOR square.

[click] Add one hidden neuron that computes AND(x₁, x₂). It's a perceptron that fires only when both inputs are on, so on these 0/1 inputs it equals x₁·x₂. Use its output as a third coordinate, h. Three points have h = 0 and stay on the floor. Only (1, 1) has h = 1, so it rises.

[click] Now one flat plane separates the classes: x₁ + x₂ − 2h = 0.5. Check a couple out loud. (0, 1, 0): 1 − 0 = 1 > 0.5, teal side. (1, 1, 1): 2 − 2 = 0 < 0.5, violet side. (0, 0, 0): 0 < 0.5, violet side. So the output neuron is just a perceptron with three inputs, x₁, x₂, and h. This is exactly the ring trick: add a nonlinear feature, then cut with a plane.

[click] The difference, and it's the whole reason deep learning exists: with the SVM, YOU chose the feature map (the squared radius, or a kernel like the RBF). Here the hidden neuron's weights are learned by gradient descent, so the network finds its own features. For XOR we wrote h by hand to make the point, but training would discover something equivalent.

Two cautions, if there's time or someone asks:
1. The extra dimension only helps because h is nonlinear (a threshold). If h were a plain weighted sum like x₁ + x₂, the four points would still lie on a flat sheet in 3D, and a plane cutting a flat sheet is just a line on it, so nothing is gained. That's the next slide: without activations, depth collapses.
2. More dimensions isn't the point in itself. On the previous slide, the hidden layer had 2 units, so 2D went to 2D, and it still worked because the threshold moved the points. The number of hidden units sets the dimension of the new space; it can be smaller, equal, or larger than the input.

On the RBF kernel: it puts a fixed Gaussian bump around every training point, an effectively infinite-dimensional feature space that is never built explicitly. A hidden layer is the opposite trade: a small number of features, but learned. (RBF networks, whose hidden units are Gaussian bumps with learned centers, sit in between.)
-->

---
glowSeed: 417
clicks: 4
---

# Without Activations, Depth Collapses

<div class="text-lg opacity-85 mt-1">Two neurons in a row, no activation: each neuron is a weighted sum <span class="text-orange-400">plus a bias</span>.</div>

<div class="mt-1">
<TwoNeuronCollapse :step="$clicks" />
</div>

<div class="grid grid-cols-2 gap-6 mt-1 text-left items-start">

<div class="collapse-math text-base">
<div class="reveal" :class="{ shown: $clicks >= 1 }">

$h = w_1x + \textcolor{#fb923c}{b_1} = 2x + \textcolor{#fb923c}{1}$

</div>
<div class="reveal" :class="{ shown: $clicks >= 2 }">

$y = w_2h + \textcolor{#fb923c}{b_2} = 3h \mathbin{\textcolor{#fb923c}{-}} \textcolor{#fb923c}{4}$

</div>
<div class="reveal" :class="{ shown: $clicks >= 3 }">

$y = 3(2x + \textcolor{#fb923c}{1}) \mathbin{\textcolor{#fb923c}{-}} \textcolor{#fb923c}{4} = \boldsymbol{6x} \mathbin{\textcolor{#fb923c}{\boldsymbol{-}}} \textcolor{#fb923c}{\boldsymbol{1}}$

</div>
</div>

<div class="reveal text-sm collapse-box" :class="{ shown: $clicks >= 4 }" border="2 solid violet-800" bg="violet-800/20" rounded-lg px-4 py-1>

$W_2(W_1x + \textcolor{#fb923c}{b_1}) + \textcolor{#fb923c}{b_2} = (W_2W_1)\,x + \textcolor{#fb923c}{(W_2b_1 + b_2)}$

<b class="text-violet-300">Any number of layers, any width:</b> still one linear layer. No new features, so no lift like the AND neuron.

</div>

</div>

<style>
.collapse-math .katex { font-size: 1.15em; }
.collapse-math p { margin: 0.35em 0; }
.collapse-box p { margin: 0.4em 0; }
</style>

<!--
The previous slide's lift only worked because the hidden neuron, AND, thresholds its input. This slide shows what happens if we drop that and let neurons output their weighted sum directly, with no activation function.

Setup: one input x, two neurons in a chain. Neuron 1 has weight 2 and bias 1; neuron 2 has weight 3 and bias −4. No activation anywhere: each neuron just outputs its sum. The orange boxes are the biases: a constant that gets added into the neuron's sum no matter what comes in on the weighted edge. Biases are orange everywhere on this slide, including the equations, so you can follow them through.

[click] Neuron 1 computes h = 2x + 1. That's a line.

[click] Neuron 2 takes h as its input and computes y = 3h − 4. Also a line.

[click] Substitute the first into the second: y = 3(2x + 1) − 4 = 6x + 3 − 4 = 6x − 1. The picture collapses to a single neuron with weight 3·2 = 6 and bias 3·1 − 4 = −1. Check with x = 1: h = 3, y = 9 − 4 = 5, and 6·1 − 1 = 5. Same answer. Point at the orange: the first bias, 1, gets multiplied by the second weight (it passes through neuron 2 like everything else), and then the second bias, −4, is added. 3·1 − 4 = −1, the single orange box on the bottom row. In general, y = (w₂w₁)x + (w₂b₁ + b₂): the weights multiply and the biases combine, and the result is still one weighted sum plus one bias.

[click] The same algebra holds with many inputs and many neurons per layer: the weights become matrices, and multiplying two matrices gives one matrix. So a hundred stacked linear layers can always be replaced by one, and the network can still only draw straight boundaries, exactly like a single perceptron.

Tie it back to the previous slide: the hidden neuron there created a genuinely new feature, AND(x₁, x₂), that lifted (1, 1) out of the plane. A linear neuron can't do that. Its output, like x₁ + x₂, is just a combination of features we already had, so the points stay on a flat sheet and nothing new becomes separable.

Takeaway: the nonlinear activation is what makes extra layers worth having. That's why the activation function is never optional in hidden layers, and the next slide looks at the common choices.
-->

---
glowSeed: 418
---

# Activation Functions

<ActivationGallery />

<div v-click class="mt-4 text-sm" border="2 solid teal-800" bg="teal-800/20" rounded-lg px-4 py-2>
<b class="text-teal-300">Rule of thumb:</b> ReLU in hidden layers. The output layer's activation depends on the problem, coming up next.
</div>

<!--
The amber dot is one input z sweeping back and forth through all four functions at once. Read off how each one responds to the same z.

- Step: the perceptron's original choice. Its problem for learning is that it's flat everywhere except at the jump, so a tiny change in a weight almost never changes the output. Gradient descent follows the slope, so it gets no signal. That's why the perceptron loss on slide 5 used the score z, not the step output.
- Sigmoid: a smooth version of the step. Output in (0, 1), so it reads as a probability. That's the logistic regression function.
- Tanh: the same S-shape stretched to (−1, 1) and centered at zero.
- ReLU: max(0, z). Zero for negative inputs, the identity for positive ones. It's cheap to compute, and it doesn't flatten out for large z, which turns out to matter a lot when training deep networks.

[click] Practical default: ReLU (or a close cousin) in the hidden layers. The output layer is different: its activation is chosen to match the kind of answer we want, which is the next section.

Keep this brief. Why sigmoid and tanh make deep networks hard to train (saturation and vanishing gradients) is covered properly next lecture, once we've seen gradients.
-->

---
glowSeed: 419
clicks: 4
---

# More Hidden Units, More Bends

<ReluSum :step="$clicks" />

<div class="mt-2 text-sm reveal" :class="{ shown: $clicks >= 4 }" border="2 solid amber-800" bg="amber-800/20" rounded-lg px-4 py-2>
<b class="text-amber-300">Universal approximation:</b> one hidden layer with enough units can approximate any continuous function as closely as you like. It does <b>not</b> say how many units, or that training will find them.
</div>

<!--
This makes "neural networks can fit anything" concrete. Each hidden ReLU unit computes a hinge, ReLU(x − xₖ): zero until x reaches xₖ, then a straight ramp. The output adds the hinges together with weights aₖ. Before xₖ a unit contributes nothing; after it, the unit adds aₖ to the slope. So each dot on the curve is one hidden unit switching on and bending the output there, and the weight aₖ is how sharply it bends.

This network is built by hand, not trained: the hinge positions are evenly spaced, and the weights are chosen so the curve passes through the target at each hinge.

[click] 2 units: two bends, a crude zigzag.
[click] 4 units.
[click] 8 units: it's starting to follow the shape.
[click] 20 units: the worst-case error is small. With more units it keeps shrinking.

That is the universal approximation theorem (Cybenko 1989; Hornik 1991) in one picture. Two caveats matter as much as the theorem itself:
1. It guarantees that a good network exists, not how big it needs to be. For complicated functions, one hidden layer may need an impractically huge number of units. Deeper networks often do the same job with far fewer.
2. It says nothing about whether training will find those weights, or whether the result will generalize to new data. Those are the subject of the next lecture.
-->

---
glowSeed: 420
---

# Anatomy of a Network

<div class="grid grid-cols-[1.3fr_1fr] gap-6 items-center text-left">
<div>

<NetFlow :layers="[4, 6, 6, 3]" mode="forward" :labels="['input', 'hidden 1', 'hidden 2', 'output']" :height="280" />

</div>
<div class="text-base">

<v-clicks>

- **Input layer**: one node per feature
- **Hidden layers**: each computes $h = f(Wh_{\text{prev}} + b)$
- **Output layer**: one node per answer
- **Width**: units per layer · **Depth**: number of layers
- **Fully connected (dense)**: every unit feeds every unit in the next layer

</v-clicks>

<div v-click border="2 solid white/5" bg="white/5" rounded-lg px-3 py-2 mt-3 text-sm>
<b class="text-amber-300">Count the parameters</b> of 64 → 32 → 10:<br>
<span class="font-mono">64·32 + 32 = 2,080</span> and <span class="font-mono">32·10 + 10 = 330</span><br>
<span class="font-mono text-amber-300">2,410 weights and biases</span>
</div>

</div>
</div>

<!--
Now the vocabulary that every later lecture uses.

[click] Input layer: just the features. One node per number we feed in. It doesn't compute anything; it's drawn as a layer by convention.
[click] Hidden layers: called hidden because we never see their target values in the data. Each one is a matrix multiply, a bias, and an activation: h = f(W h_prev + b). One matrix multiplication per layer is why GPUs are so good at this.
[click] Output layer: one node per number we want out. Its size and activation depend on the problem type, coming up next.
[click] Width and depth are the two knobs of architecture. "Deep learning" just means many hidden layers.
[click] Fully connected: every unit connects to every unit in the next layer. Convolutional and recurrent networks, later in this unit, connect more selectively.

[click] Parameter counting, a skill students should practice: each layer has (inputs × outputs) weights plus one bias per output. For the 64 → 32 → 10 digit network we'll train in a few minutes: 64·32 + 32 = 2,080, and 32·10 + 10 = 330, for 2,410 parameters. For comparison, a modern language model has billions. The arithmetic is the same.
-->

---
glowSeed: 421
---

# Three Problem Types, One Network

<div class="grid grid-cols-3 gap-5 mt-6 text-left">

<div v-click border="2 solid blue-800" bg="blue-800/20" rounded-lg p-4>
<div class="font-bold text-blue-300 text-lg">Regression</div>
<div class="text-sm opacity-80 mb-3">predict a number</div>
<div class="text-sm"><b>Output:</b> 1 unit, no activation</div>
<div class="text-sm"><b>Loss:</b> mean squared error</div>
<div class="text-sm mt-3 opacity-85">house price · energy demand · delivery time</div>
</div>

<div v-click border="2 solid teal-800" bg="teal-800/20" rounded-lg p-4>
<div class="font-bold text-teal-300 text-lg">Binary classification</div>
<div class="text-sm opacity-80 mb-3">yes or no</div>
<div class="text-sm"><b>Output:</b> 1 unit, sigmoid → P(yes)</div>
<div class="text-sm"><b>Loss:</b> binary cross-entropy</div>
<div class="text-sm mt-3 opacity-85">spam · fraud · machine fault</div>
</div>

<div v-click border="2 solid violet-800" bg="violet-800/20" rounded-lg p-4>
<div class="font-bold text-violet-300 text-lg">Multiclass classification</div>
<div class="text-sm opacity-80 mb-3">one of K classes</div>
<div class="text-sm"><b>Output:</b> K units, softmax → K probabilities</div>
<div class="text-sm"><b>Loss:</b> cross-entropy</div>
<div class="text-sm mt-3 opacity-85">digit 0–9 · product category · species</div>
</div>

</div>

<div v-click class="mt-8 text-lg">The hidden layers stay the same. <span class="text-amber-300">Only the output layer and the loss change.</span></div>

<!--
This is the most practically useful slide in the deck: it's the decision students will make every time they build a network.

[click] Regression: we want any real number, so the output unit has no activation (it can be any value), and the loss is mean squared error, exactly as in linear regression.
[click] Binary classification: one output unit with a sigmoid gives a probability, and the loss is binary cross-entropy, the same loss as logistic regression.
[click] Multiclass: K output units, one per class, with a softmax that turns K scores into K probabilities that sum to one. The loss is cross-entropy.

[click] The key message: the body of the network, its hidden layers, doesn't care what kind of problem this is. Only the head (the output layer plus its matching loss) changes. These pairings also aren't arbitrary: each output activation is paired with the loss that makes the gradient at the output come out as simply (prediction − target), which keeps training well-behaved.

Next, one live example of each, trained in the browser right now.
-->

---
glowSeed: 422
---

# Regression: Energy Use vs. Temperature

<RegressionLive />

<!--
This is live training, not a recording. Each frame runs a few gradient steps. Click the plot to restart.

Problem: predict a building's daily electricity use from the outdoor temperature. Real energy data looks like this: high on cold days (heating), lowest in mild weather, high again on hot days (air conditioning). It's a U shape. (This data is synthetic but shaped like real load curves.)

Two networks train on the same data with the same loss:
- No hidden layer: that's exactly linear regression. It quickly settles on the best straight line, and the best straight line is nearly flat, because the U has no overall slope. Its typical error stays around 6 kWh no matter how long it trains.
- Two hidden layers of 16 tanh units: watch the amber curve bend into the U. Its typical error drops to about the noise level of the data, around 1.5 kWh.

Ask: how would you have fit this with classical tools? (Add a temperature² feature by hand, then use linear regression.) The network found the curve's shape itself, which is exactly the "learned features" point from the XOR slide.

Output layer: one unit, no activation. Loss: mean squared error.
-->

---
glowSeed: 423
---

# Binary Classification: Is the Machine OK?

<ClassifyLive />

<!--
Live training again; click either plot to restart.

Problem: a sensor reports a machine's temperature and pressure (standardized). It runs OK when both are near their nominal values. Too hot, too cold, too high, or too low all mean a fault. So the OK region is a disc in the middle (teal circles), with faults all around it (violet squares).

Background color is the model's predicted probability of OK: teal where it says OK, violet where it says fault, brighter when it's more confident.

- Left, no hidden layer: that's logistic regression, which can only draw one straight boundary. It gets stuck at about 77% accuracy. Since 77% of the readings are faults, that's no better than answering "fault" every time: a straight line simply has nothing useful to offer here. This is a good moment to remind students that accuracy needs a baseline.
- Right, one hidden layer of 8 units: the boundary closes into a loop around the OK region, reaching about 97% accuracy. Each hidden unit contributes one straight edge, and the output combines them, just like XOR's band, only with more lines.

Output layer: one sigmoid unit, read as P(OK). Loss: binary cross-entropy.
-->

---
glowSeed: 424
clicks: 2
---

# Softmax: From Scores to Probabilities

<SoftmaxBars :step="$clicks" />

<div class="text-center mt-1">

$$
p_k = \frac{e^{z_k}}{\sum_{j=1}^{K} e^{z_j}}
$$

</div>

<!--
For multiclass problems the network outputs one raw score per class, called a logit. Here: 10 scores for an image of a handwritten 3.

Step 0: raw scores can be any real number, including negative ones. They aren't probabilities yet. Class 3 has the highest score, 8 is second, and 5 third. Those are the digits that look like a 3.

[click] Exponentiate every score. Now they're all positive. Exponentiating also stretches the gaps: a score that's 1.2 higher becomes about 3.3 times larger.

[click] Divide each one by the total, so they sum to 1. The stacked bar shows the result as a pie: 62% "3", 19% "8", 10% "5". The prediction is the largest probability, and the probabilities also tell us how confident the network is.

Connection: with two classes, softmax reduces to the sigmoid. So multiclass logistic regression is a neural network with no hidden layer and a softmax output.
-->

---
glowSeed: 425
---

# Multiclass: Reading Handwritten Digits

<DigitsLive />

<!--
Live training on real data: 1,797 handwritten digit scans at 8×8 pixels (the UCI digits set, which some students have seen in the dimensionality-reduction unit). 1,500 are used for training and 297 are held out as a test set the network never trains on.

The network is the one we counted parameters for: 64 pixel inputs → 32 ReLU units → 10 softmax outputs, for 2,410 parameters. It trains on mini-batches of 32 images at a time.

Watch three things:
1. Left: 24 test digits with the network's current guess under each. At the start the guesses are random and mostly red. Within a few seconds most turn teal.
2. Top right: test accuracy climbs from about 10% (chance for 10 classes) to about 97%.
3. Bottom right: the softmax output for the highlighted digit, which cycles. Early on the probabilities are spread out. Once trained, almost all the mass sits on the correct digit.

Point out what the network was not told: nothing about strokes, loops, or edges. It was given 64 pixel brightnesses and the right answers, and it worked out useful features itself. The CNN lecture later in this unit shows how to do much better on bigger images by building in the fact that pixels have neighbors.
-->

---
glowSeed: 426
---

# Three Demos, Three Heads

````md magic-move {lines: false}
```python
# Regression: energy use from temperature
model = nn.Sequential(
    nn.Linear(1, 16), nn.Tanh(),
    nn.Linear(16, 16), nn.Tanh(),
    nn.Linear(16, 1),                 # one number, no activation
)
loss_fn = nn.MSELoss()
```
```python
# Binary classification: machine OK or fault
model = nn.Sequential(
    nn.Linear(2, 8), nn.Tanh(),
    nn.Linear(8, 1),                  # one score → sigmoid inside the loss
)
loss_fn = nn.BCEWithLogitsLoss()
```
```python
# Multiclass: which digit, 0–9
model = nn.Sequential(
    nn.Linear(64, 32), nn.ReLU(),
    nn.Linear(32, 10),                # ten scores → softmax inside the loss
)
loss_fn = nn.CrossEntropyLoss()
```
````

<div v-click="3" class="mt-4 text-sm opacity-85">PyTorch folds the sigmoid and softmax into the loss for numerical stability. Apply them yourself only to read off probabilities.</div>

<!--
The three demos you just watched, in PyTorch. Click to morph between them. The hidden layers differ a little because the demos have different inputs (1 temperature, 2 sensor readings, 64 pixels), but the pattern is the same each time: Linear, activation, Linear, activation. Focus on the last Linear and the loss line, since those are what the problem type decides.

Regression: the last layer outputs one number, there's no activation, and the loss is MSELoss.

[click] Binary: the last layer outputs one score, and the loss is BCEWithLogitsLoss.

[click] Multiclass: the last layer outputs ten scores, and the loss is CrossEntropyLoss.

[click] A detail that trips students up: in PyTorch the sigmoid and softmax are not in the model. BCEWithLogitsLoss and CrossEntropyLoss take the raw scores (logits) and apply the activation internally, because computing log(softmax(z)) in one step avoids overflow and underflow. To get probabilities for display, apply torch.sigmoid or torch.softmax to the model's output yourself. A common bug is adding a softmax layer to the model AND using CrossEntropyLoss, which applies softmax twice. It still trains, but worse.

Everything above the last Linear is the same kind of layer stack each time, sized to the data. The head and the loss are what change with the problem type.
-->

---
glowSeed: 427
---

# Training Is a Loop

<TrainLoop />

<!--
Now, how did those demos actually learn? Every network you'll ever train runs this same four-step loop, thousands of times.

1. Forward: push a batch of inputs through the network to get predictions. That's the part we've been animating all lecture.
2. Loss: one number measuring how wrong the predictions were, using the loss that matches the head.
3. Backward: for every single weight, work out which direction to nudge it to make the loss smaller, and how strongly. That's the gradient, and computing it efficiently is what backpropagation does.
4. Update: nudge every weight a small step in that direction.

Then repeat with the next batch. The loss curve on the right (illustrative) falls quickly at first, then levels off.

This is the loop the perceptron already ran on slides 5 and 6: the perceptron loss, its gradient, and an SGD step. Two things change for a multilayer network. The losses are the smooth ones from the problem-types section, so every example contributes, not just the misclassified ones. And the weights are spread across several layers, so computing the gradient takes more work. That second part is what backpropagation solves, two slides from now.
-->

---
glowSeed: 428
---

# Gradient Descent, Revisited

<Descent />

<!--
This is review: the same gradient descent students learned in Core ML Concepts and watched train a perceptron on slide 6. The only point to add is that nothing about it changes for a neural network. There are just more weights.

Picture the loss as a landscape over the weights. Here there are only two weights so we can see it from above: contour lines connect weight settings with equal loss, and the minimum is the teal dot. A real network has thousands or billions of weights, but the idea is the same.

The gradient ∇L points uphill, in the direction where loss increases fastest. So we step the opposite way: w ← w − η∇L. The red arrow is −∇L at the current point.

Watch the walk:
- Steps are big where the slope is steep and shrink near the bottom, automatically, because the gradient gets smaller.
- The bowl is steep in one direction and shallow in the other, so the path zigzags a little across the steep direction while it slides along the shallow one.
- The loss bars on the right fall step by step.

The walk restarts from a new starting point each time. All of them reach the same minimum here because this bowl has only one. Real loss landscapes are bumpier.

η, the learning rate, is the step size. Too small and training crawls; too big and the steps overshoot and bounce out of the valley. Choosing it, and smarter ways to step (momentum, Adam), are the heart of next lecture. Today, just hold onto the picture: a ball rolling downhill, one step per iteration.
-->

---
glowSeed: 429
clicks: 4
---

# Backpropagation: Passing Blame Backward

<div class="grid grid-cols-[1.4fr_1fr] gap-6 items-center text-left">
<div>

<NetFlow :layers="[3, 5, 5, 2]" :mode="['none', 'forward', 'loss', 'backward', 'update'][$clicks]" :height="290" />

</div>
<div class="text-base">

<div class="reveal" :class="{ shown: $clicks >= 1 }"><b class="text-teal-300">1 · Forward:</b> compute and save every unit's output</div>
<div class="reveal mt-3" :class="{ shown: $clicks >= 2 }"><b class="text-red-300">2 · Loss:</b> compare the output with the target</div>
<div class="reveal mt-3" :class="{ shown: $clicks >= 3 }"><b class="text-amber-300">3 · Backward:</b> send the error back layer by layer. Each weight's share of blame = how much it changed the loss</div>
<div class="reveal mt-3" :class="{ shown: $clicks >= 4 }">

<b class="text-violet-300">4 · Update:</b> every weight moves at once: $w \leftarrow w - \eta\,\partial L/\partial w$

</div>

<div class="reveal mt-5 text-sm" :class="{ shown: $clicks >= 3 }" border="2 solid amber-800" bg="amber-800/20" rounded-lg px-3 py-2>
<b class="text-amber-300">The chain rule, reused:</b> a weight's blame = (blame arriving at its unit) × (how much the weight affected that unit). One backward pass gets <b>every</b> gradient.
</div>

</div>
</div>

<!--
Backpropagation is how step 3 of the loop is done efficiently. The goal is intuition, not a derivation.

[click] Forward: the signal flows left to right, and every unit's output is saved, because the backward pass will need it.

[click] Loss: the output is compared with the target, and the error shows up at the output units.

[click] Backward: the error flows right to left, the same edges in reverse. These edge widths are real: they're the actual gradient sizes for this network on one example. An output unit's blame is how wrong it was. A hidden unit's blame is the sum of the blame of every unit it feeds, each weighted by the connecting weight. That's the chain rule from calculus, applied layer by layer and reusing what the layer above already computed. Thick amber edges are the weights that most affected the error; those will change most.

Why it matters: the naive way to find each weight's gradient is to wiggle that one weight and rerun the network, once per weight. With a million weights, that's a million forward passes per step. Backprop gets all the gradients in one backward pass, at about the cost of one forward pass. That efficiency is why deep learning is possible at all.

[click] Update: every weight steps downhill at once. Notice the edges change. (The step here is deliberately exaggerated so the change is visible.)

You will almost never write backprop by hand. Frameworks record the forward pass and run the backward pass for you, which is the next slide.
-->

---
glowSeed: 430
---

# The Whole Loop in PyTorch

<div class="grid grid-cols-[1.4fr_1fr] gap-6 items-center text-left">
<div>

```python {all|3|4|5-6|7|all}
optimizer = torch.optim.Adam(model.parameters(), lr=1e-3)
for X, y in loader:              # one mini-batch at a time
    y_hat = model(X)             # 1 forward
    loss = loss_fn(y_hat, y)     # 2 loss
    optimizer.zero_grad()        #   clear last step's gradients
    loss.backward()              # 3 backward: backprop, automatically
    optimizer.step()             # 4 update every weight
```

</div>
<div class="text-base">

<div v-click="1" class="mb-3"><b class="text-teal-300">Forward</b>: call the model like a function</div>
<div v-click="2" class="mb-3"><b class="text-red-300">Loss</b>: one number</div>
<div v-click="3" class="mb-3"><b class="text-amber-300">Backward</b>: <code>.backward()</code> fills in ∂L/∂w for every weight</div>
<div v-click="4" class="mb-3"><b class="text-violet-300">Update</b>: the optimizer takes one downhill step</div>

</div>
</div>

<!--
The four-step loop from two slides ago, in seven lines. This exact shape trains everything from the tiny digit network to large language models.

[click] Forward: calling model(X) runs the forward pass. PyTorch quietly records every operation as it goes.
[click] Loss: the head-matched loss reduces everything to one number.
[click] Backward: zero_grad clears the previous step's gradients (PyTorch adds gradients up by default, which is a classic bug source if forgotten). Then loss.backward() runs backpropagation through the recorded operations and stores ∂L/∂w in each weight's .grad field. This is automatic differentiation, and it's why nobody writes backprop by hand anymore.
[click] Update: optimizer.step() moves each weight using its gradient.

[click] Note the optimizer is Adam rather than plain gradient descent, and lr is the learning rate η. What Adam does and how to choose lr are where next lecture starts.
-->

---
glowSeed: 431
---

# Recap

<div class="grid grid-cols-2 gap-5 mt-6 text-left">

<div v-click border="2 solid blue-800" bg="blue-800/20" rounded-lg p-4>
<div class="font-bold text-blue-300 mb-1">One neuron draws a line</div>
<div class="text-sm opacity-90">A perceptron is a weighted sum and a threshold. Gradient descent on its mistakes trains it, but it can't solve XOR.</div>
</div>

<div v-click border="2 solid teal-800" bg="teal-800/20" rounded-lg p-4>
<div class="font-bold text-teal-300 mb-1">Hidden layers move the data</div>
<div class="text-sm opacity-90">Each layer re-represents the inputs until a simple boundary works. Nonlinear activations are what make depth count.</div>
</div>

<div v-click border="2 solid violet-800" bg="violet-800/20" rounded-lg p-4>
<div class="font-bold text-violet-300 mb-1">The head sets the problem</div>
<div class="text-sm opacity-90">Linear + MSE for numbers · sigmoid + BCE for yes/no · softmax + cross-entropy for K classes.</div>
</div>

<div v-click border="2 solid amber-800" bg="amber-800/20" rounded-lg p-4>
<div class="font-bold text-amber-300 mb-1">Training walks downhill</div>
<div class="text-sm opacity-90">Forward, loss, backward, update. Backprop gets every gradient in one backward pass.</div>
</div>

</div>

<div v-click class="mt-8 opacity-85"><b>Next:</b> Training Neural Networks in Practice: initialization, optimizers, learning-rate schedules, and regularization</div>

<!--
Four ideas to take away. Reveal one at a time and ask a student to restate each in their own words before moving on.

[click] The perceptron: a weighted sum plus a threshold, which geometrically is a line. Training it is gradient descent on the perceptron loss. That reaches zero loss when a line can separate the data, and fails on XOR, where none can.
[click] Hidden layers transform the data into a representation where a simple boundary works. Activation functions are essential, because without them all the layers collapse into one linear map.
[click] The problem type determines only the output layer and the loss: regression, binary, or multiclass.
[click] Training is a loop of forward, loss, backward, update. Gradient descent walks downhill on the loss, and backpropagation computes all the gradients in one backward pass.

[click] Next lecture, Training Neural Networks in Practice, picks up exactly where the demos left off. They all trained smoothly because the settings were chosen carefully. Next time we look at what goes wrong without that care, and the tools for fixing it: how to initialize the weights, which optimizer to use, how to schedule the learning rate, and how to regularize so the network generalizes instead of memorizing.
-->

---
layout: center
class: text-center
glowSeed: 432
---

# Thank You

### Questions &amp; Discussion

<div class="mt-6 max-w-xl mx-auto">
<NetFlow :layers="[3, 4, 4, 1]" mode="forward" :height="170" :seed="12" />
</div>

<div class="pt-4 opacity-80">
Neural Networks: From Perceptrons to Multilayer Networks · Neural Networks and Deep Learning Basics
</div>

<!--
Good prompts if the room is quiet:
- How many hidden perceptrons would you need to carve out a triangle-shaped region? (Three, one per edge.)
- If you removed every activation function from the digit network, what kind of model would it become? (Multiclass logistic regression on the raw pixels: one linear layer plus a softmax.)
- In the regression demo, why did the no-hidden-layer model draw an almost flat line? (The best straight line through a symmetric U has nearly zero slope.)

Next lecture: Training Neural Networks in Practice.
-->
