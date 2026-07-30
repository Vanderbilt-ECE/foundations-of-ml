---
theme: default
highlighter: shiki
css: unocss
colorSchema: dark
title: 'Convolutional and Recurrent Networks'
info: |
  ## Convolutional and Recurrent Networks
  Specialized structure for images and sequences
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
glowSeed: 870
---

# Convolutional and Recurrent Networks

### Specialized structure for images and sequences

<div class="pt-8 opacity-80 text-lg">Neural Networks and Deep Learning Basics · Foundations of Machine Learning</div>

<div class="mt-14 flex justify-center gap-4" aria-hidden="true">
<div class="w-28 h-3 rounded-full bg-teal-400/70"></div>
<div class="w-20 h-3 rounded-full bg-blue-400/60"></div>
<div class="w-14 h-3 rounded-full bg-violet-400/50"></div>
</div>

<!--
This deck follows Backpropagation and Practical Training Issues in the Neural Networks and Deep Learning Basics unit. Those decks established the machinery every network uses: layers of weighted sums and nonlinearities, trained end to end by backpropagating gradients through the chain rule, with techniques like batch normalization and dropout keeping deep networks trainable. Everything in this deck reuses that machinery unchanged — nothing new is being trained differently.

What changes here is architecture, not mechanics. Dense (fully connected) layers, where every input connects to every unit, work fine for tabular data with no inherent structure. But images have spatial structure (nearby pixels are related) and sequences have temporal structure (nearby time steps are related). Convolutional neural networks (CNNs) and recurrent neural networks (RNNs) are two families of architectures that build that structure into the layer itself, rather than asking a dense layer to rediscover it from scratch.

Frame this explicitly as a light-touch overview: the goal is to recognize when each architecture applies and to understand its core operation at a conceptual level, not to derive backpropagation through a convolution or through time by hand. Two companion decks in this same folder — Convolutional Neural Networks and RNNs and LSTMs — go through those derivations and implementation details in full; point students there for depth. Roadmap: why dense layers fail on images, how convolution fixes that, a compact CNN example, why RNNs share weights across time, why long sequences reintroduce vanishing gradients, and a closing framework for choosing an architecture from data structure.
-->

---
glowSeed: 871
---

# Dense Layers Ignore Image Structure

<div class="grid grid-cols-3 gap-4 mt-6">
<div v-click border="2 solid teal-800" bg="teal-800/20" rounded-lg p-4>
<div class="font-bold text-teal-300 mb-2">Parameter explosion</div>
<div class="text-sm leading-relaxed opacity-90">224×224×3 pixels feeding 1,000 units means about 150 million weights.</div>
</div>
<div v-click border="2 solid blue-800" bg="blue-800/20" rounded-lg p-4>
<div class="font-bold text-blue-300 mb-2">Lost locality</div>
<div class="text-sm leading-relaxed opacity-90">Flattening does not tell a dense layer which pixels are neighbors.</div>
</div>
<div v-click border="2 solid amber-800" bg="amber-800/20" rounded-lg p-4>
<div class="font-bold text-amber-300 mb-2">CNN response</div>
<div class="text-sm leading-relaxed opacity-90">Share small filters across nearby spatial regions.</div>
</div>
</div>


<!--
Compute the parameter count explicitly, since the slide only asserts it. A 224×224 color image has 224 × 224 × 3 = 150,528 pixel values once flattened (3 channels for red, green, blue). Connecting every one of those inputs to a dense layer of 1,000 units requires 150,528 × 1,000 ≈ 150.5 million weights, for a single layer, before counting biases or any subsequent layer. That is already larger than many entire modern CNNs, and it scales linearly with image resolution — a 512×512 image would need roughly five times as many weights in that first layer alone.

Parameter count is only half the problem, and arguably the less important half. The deeper issue is lost locality: flattening an image into a single long vector destroys the information that pixel (i, j) is spatially adjacent to pixel (i, j+1). A dense layer treats every input as equally likely to interact with every other input, so it must independently relearn, from data, that nearby pixels tend to be correlated — a fact convolution builds in for free by only ever looking at local neighborhoods.

Convolutional layers respond to both problems with one idea: replace one giant fully-connected matrix with a small filter (kernel) that slides across the image and shares its weights at every spatial location. The next slide shows exactly how that works.
-->

---
glowSeed: 872
---

# Convolution Shares a Local Filter

<div class="grid grid-cols-2 gap-8 items-start">
<div>
<div class="space-y-3 mt-4">
<div v-click border="2 solid white/5" bg="white/5" rounded-lg px-4 py-3>
<span class="font-bold text-teal-300">Small kernel</span>
<span class="text-sm opacity-85"> — A learned 3×3 grid slides across the image.</span>
</div>
<div v-click border="2 solid white/5" bg="white/5" rounded-lg px-4 py-3>
<span class="font-bold text-blue-300">Weight sharing</span>
<span class="text-sm opacity-85"> — The same nine weights detect a pattern everywhere.</span>
</div>
<div v-click border="2 solid white/5" bg="white/5" rounded-lg px-4 py-3>
<span class="font-bold text-amber-300">Feature maps</span>
<span class="text-sm opacity-85"> — Different filters learn edges, textures, and shapes.</span>
</div>
</div>
</div>
<div>
<svg role="img" aria-label="A 3 by 3 kernel slides over a patch of the input grid and produces one output cell via a weighted sum" viewBox="0 0 420 260" class="w-full max-w-lg mx-auto mt-6">
  <text x="10" y="18" fill="#94a3b8" style="font-size:12px">input</text>
  <g stroke="#475569" stroke-width="1">
    <rect x="10" y="26" width="180" height="180" fill="none" />
    <line x1="10" y1="86" x2="190" y2="86" /><line x1="10" y1="146" x2="190" y2="146" />
    <line x1="70" y1="26" x2="70" y2="206" /><line x1="130" y1="26" x2="130" y2="206" />
  </g>
  <rect x="10" y="26" width="60" height="60" fill="none" stroke="#2dd4bf" stroke-width="3" />
  <text x="15" y="20" fill="#2dd4bf" style="font-size:11px">3×3 kernel K</text>

  <defs>
    <marker id="cvarrow" markerWidth="8" markerHeight="8" refX="4" refY="4" orient="auto">
      <path d="M0,0 L8,4 L0,8 Z" fill="#fbbf24" />
    </marker>
  </defs>
  <line x1="200" y1="56" x2="250" y2="56" stroke="#fbbf24" stroke-width="2" marker-end="url(#cvarrow)" />
  <text x="195" y="44" fill="#fbbf24" style="font-size:11px">weighted sum</text>

  <text x="270" y="18" fill="#94a3b8" style="font-size:12px">output feature map</text>
  <g stroke="#475569" stroke-width="1">
    <rect x="270" y="26" width="120" height="120" fill="none" />
    <line x1="270" y1="66" x2="390" y2="66" /><line x1="270" y1="106" x2="390" y2="106" />
    <line x1="310" y1="26" x2="310" y2="146" /><line x1="350" y1="26" x2="350" y2="146" />
  </g>
  <rect x="270" y="26" width="40" height="40" fill="#f472b6" opacity="0.5" />
  <text x="270" y="200" fill="#f472b6" style="font-size:10px">one kernel pos → one output cell</text>
</svg>
<div v-click class="mt-4" style="font-size: .9em" border="2 solid teal-800" bg="teal-800/20" rounded-lg px-4 py-3>

$$
Y_{ij}=\sum_{u,v}K_{uv}X_{i+u,j+v}
$$

</div>
</div>
</div>

<div v-click class="mt-2 text-xs opacity-80" border="2 solid white/5" bg="white/5" rounded-lg px-3 py-1>
For the full convolution derivation, padding/stride arithmetic, and multi-channel filters, see the <strong>Convolutional Neural Networks</strong> deck.
</div>

<!--
Weight sharing is the key idea: instead of one weight per (input pixel, output unit) pair, the same small kernel K — here 3×3, so nine weights plus one bias — is applied at every spatial position in the image. That single kernel produces one entry of the output feature map per position it slides to, as the diagram shows: the highlighted 3×3 patch of the input combines with K to produce the highlighted cell of the output.

Two things follow immediately. First, the parameter count no longer depends on image size — a 3×3 kernel has 9 weights whether the image is 28×28 or 4K resolution, versus the 150-million-weight dense layer from the previous slide. Second, because the same weights are reused everywhere, a kernel that learns to detect a vertical edge in the top-left corner will also detect it in the bottom-right corner; the network doesn't need separate training examples for every location.

Flag a common misconception: the formula shown, Y_ij = sum over u,v of K_uv X_(i+u,j+v), is technically cross-correlation, not true mathematical convolution — true convolution flips the kernel before sliding it. Every deep learning framework (PyTorch, TensorFlow/Keras) implements cross-correlation and simply calls it "convolution"; the distinction almost never matters in practice because the kernel weights are learned either way. Also note this formula is the single-channel simplification — a real conv layer sums this expression over all input channels (e.g., red, green, blue) and adds a learned bias term before the layer's activation function is applied.

A real CNN stacks many such kernels (a "bank" of filters) per layer, each learning to detect a different pattern — edges, corners, textures — producing multiple output feature maps stacked into a 3D volume. Next slide shows how these layers compose into a full compact network.
-->

---
glowSeed: 873
---

# A Compact CNN

<div class="grid grid-cols-2 gap-4 mt-6">
<div v-click border="2 solid teal-800" bg="teal-800/20" rounded-lg p-4>
<div class="font-bold text-teal-300 mb-2">Convolve + pool</div>
<div class="text-sm leading-relaxed opacity-90">Extract and downsample spatial features.</div>
</div>
<div v-click border="2 solid blue-800" bg="blue-800/20" rounded-lg p-4>
<div class="font-bold text-blue-300 mb-2">Flatten late</div>
<div class="text-sm leading-relaxed opacity-90">Preserve structure until learned features exist.</div>
</div>
</div>

```python
cnn = keras.Sequential([
    layers.Input(shape=(28, 28, 1)),
    layers.Conv2D(32, 3, activation="relu"),
    layers.MaxPooling2D(2),
    layers.Conv2D(64, 3, activation="relu"),
    layers.MaxPooling2D(2),
    layers.Flatten(),
    layers.Dense(10, activation="softmax"),
])
```

<!--
Trace the shape (height × width × channels) through every layer, since that bookkeeping is exactly what trips people up when building CNNs by hand. Input: 28×28×1 (a grayscale MNIST digit). Conv2D(32, 3) applies 32 different 3×3 kernels with no padding, so each spatial dimension shrinks by 2 (3 - 1): output is 26×26×32 — 32 feature maps, one per kernel. MaxPooling2D(2) takes the max over non-overlapping 2×2 blocks, halving each spatial dimension without changing channel count: 26×26×32 becomes 13×13×32.

Second Conv2D(64, 3) again shrinks each spatial dimension by 2 and changes the channel count to 64 (one map per kernel, now operating on the 32 incoming channels): 13×13×32 becomes 11×11×64. The second MaxPooling2D(2) halves again: 11×11×64 becomes 5×5×64 (11 is odd, so this floors to 5). Flatten collapses everything into a single vector of length 5×5×64 = 1,600. The final Dense(10, activation="softmax") layer maps that 1,600-dimensional vector to 10 class probabilities — one per digit 0 through 9 — exactly the kind of dense layer from two slides ago, but now applied only after convolution has already extracted compact, spatially-aware features.

The "flatten late" principle: convolutional and pooling layers preserve spatial structure and progressively compress it; only once the representation is small and feature-rich does the network flatten it into a vector for a dense classification head. Flattening at the very start (as in slide 2) is what throws away the spatial information convolution is built to exploit.
-->

---
glowSeed: 874
---

# RNNs Share Weights Across Time

<div class="grid grid-cols-2 gap-8 items-start">
<div>
<div class="space-y-3 mt-4">
<div v-click border="2 solid white/5" bg="white/5" rounded-lg px-4 py-3>
<span class="font-bold text-teal-300">Ordered input</span>
<span class="text-sm opacity-85"> — Text, time series, and audio depend on sequence.</span>
</div>
<div v-click border="2 solid white/5" bg="white/5" rounded-lg px-4 py-3>
<span class="font-bold text-blue-300">Hidden state</span>
<span class="text-sm opacity-85"> — Carry a learned summary from earlier steps.</span>
</div>
<div v-click border="2 solid white/5" bg="white/5" rounded-lg px-4 py-3>
<span class="font-bold text-amber-300">Time sharing</span>
<span class="text-sm opacity-85"> — Reuse the same transition weights at every position.</span>
</div>
</div>
</div>
<div>
<div class="mt-5" role="img" aria-label="x₁ → h₁ then x₂ → h₂ then x₃ → h₃ then output">
<div v-click class="flex items-center gap-3">
<div class="w-8 h-8 rounded-full bg-teal-500/20 border-2 border-teal-700 flex items-center justify-center text-sm font-bold">1</div>
<div class="flex-1 rounded-lg border-2 border-white/10 bg-white/5 px-3 py-2 text-sm font-bold">x₁ → h₁</div>
</div>
<div class="ml-4 h-1 border-l-2 border-teal-400/50"></div>
<div v-click class="flex items-center gap-3">
<div class="w-8 h-8 rounded-full bg-blue-500/20 border-2 border-blue-700 flex items-center justify-center text-sm font-bold">2</div>
<div class="flex-1 rounded-lg border-2 border-white/10 bg-white/5 px-3 py-2 text-sm font-bold">x₂ → h₂</div>
</div>
<div class="ml-4 h-1 border-l-2 border-teal-400/50"></div>
<div v-click class="flex items-center gap-3">
<div class="w-8 h-8 rounded-full bg-amber-500/20 border-2 border-amber-700 flex items-center justify-center text-sm font-bold">3</div>
<div class="flex-1 rounded-lg border-2 border-white/10 bg-white/5 px-3 py-2 text-sm font-bold">x₃ → h₃</div>
</div>
<div class="ml-4 h-1 border-l-2 border-teal-400/50"></div>
<div v-click class="flex items-center gap-3">
<div class="w-8 h-8 rounded-full bg-violet-500/20 border-2 border-violet-700 flex items-center justify-center text-sm font-bold">4</div>
<div class="flex-1 rounded-lg border-2 border-white/10 bg-white/5 px-3 py-2 text-sm font-bold">output</div>
</div>
</div>
<div v-click class="mt-4" style="font-size: .9em" border="2 solid teal-800" bg="teal-800/20" rounded-lg px-4 py-3>

$$
h_t=\sigma(W_{hh}h_{t-1}+W_{xh}x_t+b_h)
$$

</div>

<div v-click class="mt-2 text-xs opacity-80" border="2 solid white/5" bg="white/5" rounded-lg px-3 py-1>
For the LSTM cell's gates and the full backpropagation-through-time walkthrough, see the <strong>RNNs and LSTMs</strong> deck.
</div>

</div>
</div>

<!--
Unroll the recurrent cell so the repeated structure becomes concrete: the diagram shows the same transition applied at each time step, x1 feeding in to produce hidden state h1, then x2 combining with h1 to produce h2, then x3 combining with h2 to produce h3, before a final output is read off. Each arrow represents one application of the same formula, h_t = sigma(W_hh h_(t-1) + W_xh x_t + b_h): the new hidden state h_t is a nonlinear function of the previous hidden state h_(t-1) (weighted by W_hh) plus the current input x_t (weighted by W_xh), plus a bias b_h.

Define every symbol: h_t is the hidden state at time t — a learned vector summary of everything the network has seen up through step t. W_hh is the recurrent weight matrix (hidden-to-hidden), W_xh is the input weight matrix (input-to-hidden), and b_h is a bias vector. Critically, W_hh, W_xh, and b_h are the same three parameters reused at every time step — this is weight sharing across time, directly analogous to a convolutional kernel's weight sharing across space from the CNN slides.

Flag a common misconception: the sigma in this formula is very often read as the logistic sigmoid because of the symbol, but vanilla (Elman) RNNs conventionally use tanh here, not sigmoid — tanh's output range of (-1, 1) and steeper gradient near zero make it the standard choice for the hidden-state update, while sigmoid (range (0,1)) is reserved for gating mechanisms in LSTMs and GRUs. See the Activation Functions and Initialization deck in this unit for why the choice of squashing function affects gradient flow.

Next slide: this same weight-sharing-through-time mechanism is also the source of a familiar training problem.
-->

---
glowSeed: 875
---

# Long Sequences Recreate Vanishing Gradients

<div class="grid grid-cols-2 gap-8 items-start">
<div>
<div class="space-y-3 mt-4">
<div v-click border="2 solid white/5" bg="white/5" rounded-lg px-4 py-3>
<span class="font-bold text-teal-300">Backpropagation through time</span>
<span class="text-sm opacity-85"> — The chain rule multiplies through many recurrent steps.</span>
</div>
<div v-click border="2 solid white/5" bg="white/5" rounded-lg px-4 py-3>
<span class="font-bold text-blue-300">Plain RNN</span>
<span class="text-sm opacity-85"> — Long-range dependencies become hard to learn.</span>
</div>
<div v-click border="2 solid white/5" bg="white/5" rounded-lg px-4 py-3>
<span class="font-bold text-amber-300">LSTM / GRU</span>
<span class="text-sm opacity-85"> — Gates create paths that preserve information and gradient flow.</span>
</div>
</div>
</div>
<div>
<svg role="img" aria-label="Conceptual chart for Long Sequences Recreate Vanishing Gradients" viewBox="0 0 500 310" class="w-full max-w-xl mx-auto mt-7">
  <line x1="55" y1="260" x2="470" y2="260" stroke="#64748b" stroke-width="2"/><line x1="55" y1="35" x2="55" y2="260" stroke="#64748b" stroke-width="2"/>
  <path d="M60 235 C130 210,145 70,220 100 S320 210,465 55" fill="none" stroke="#2dd4bf" stroke-width="5"/>
  <path d="M60 245 C135 230,205 195,270 165 S385 110,465 95" fill="none" stroke="#60a5fa" stroke-width="4" stroke-dasharray="9 7"/>
  <g fill="#f59e0b"><circle cx="65" cy="230" r="6"/><circle cx="163" cy="185" r="6"/><circle cx="261" cy="110" r="6"/><circle cx="359" cy="150" r="6"/><circle cx="457" cy="65" r="6"/></g>
  <g fill="#cbd5e1" style="font-size: 12px" text-anchor="middle"><text x="65" y="285">t</text><text x="163" y="285">t−5</text><text x="261" y="285">t−10</text><text x="359" y="285">t−25</text><text x="457" y="285">t−50</text></g>
  <g style="font-size: 12px"><text x="335" y="42" fill="#5eead4">primary signal</text><text x="335" y="82" fill="#93c5fd">comparison</text></g>
</svg>

</div>
</div>

<!--
The previous slide's recurrence h_t = sigma(W_hh h_(t-1) + W_xh x_t + b_h) is applied once per time step, and computing a gradient with respect to an early hidden state requires backpropagating through every step in between — this process has a name, backpropagation through time (BPTT), and it is structurally identical to backpropagating through the layers of a deep feedforward network, just walking backward through time steps instead of layers. Because the same W_hh is reused at every step (weight sharing across time, established on the previous slide), the chain rule multiplies the same Jacobian-like factor by itself once per time step separating the early and late positions — exactly the repeated-multiplication mechanism from the Practical Training Issues deck, only the "depth" being multiplied through is now sequence length rather than layer count.

The practical consequence for a plain (vanilla) RNN: if that repeated factor has typical magnitude below 1 (common with tanh's bounded derivative), the gradient signal connecting a late time step back to an early one shrinks geometrically with the gap between them, exactly as the conceptual chart shows — a token from 50 steps ago contributes almost nothing to the gradient used to update the weights, so the network effectively cannot learn dependencies that span long distances, even though the architecture in principle has access to the entire history through h_(t-1). This is precisely why vanilla RNNs struggle with tasks like carrying subject-verb agreement across a long clause, or remembering an early plot detail in a long passage.

LSTMs and GRUs (introduced by name only here) fix this with gated paths that let information and gradient flow through many time steps largely unchanged, rather than being repeatedly multiplied down. The full gate equations, the cell-state mechanism, and a worked numeric BPTT derivation are covered in depth in the companion RNNs and LSTMs deck — this slide's job is only to establish that the vanishing-gradient problem is not unique to deep feedforward networks, it recurs (pun intended) wherever weights are shared and repeatedly applied, whether across depth or across time.
-->

---
glowSeed: 876
---

# Choose Architecture From Data Structure

<div class="grid grid-cols-2 gap-4 mt-6">
<div v-click border="2 solid teal-800" bg="teal-800/20" rounded-lg p-4>
<div class="font-bold text-teal-300 mb-2">Dense</div>
<div class="text-sm leading-relaxed opacity-90">Tabular data with no special spatial or sequential structure.</div>
</div>
<div v-click border="2 solid blue-800" bg="blue-800/20" rounded-lg p-4>
<div class="font-bold text-blue-300 mb-2">CNN</div>
<div class="text-sm leading-relaxed opacity-90">Grid-like local structure: images and spectrograms.</div>
</div>
<div v-click border="2 solid amber-800" bg="amber-800/20" rounded-lg p-4>
<div class="font-bold text-amber-300 mb-2">RNN / LSTM</div>
<div class="text-sm leading-relaxed opacity-90">Ordered, variable-length sequences.</div>
</div>
<div v-click border="2 solid violet-800" bg="violet-800/20" rounded-lg p-4>
<div class="font-bold text-violet-300 mb-2">Beyond</div>
<div class="text-sm leading-relaxed opacity-90">Transformers increasingly dominate many sequence tasks.</div>
</div>
</div>


<!--
This slide converts everything covered today into a practical decision rule, since that is this light-touch deck's actual goal: recognizing which architecture fits a given problem, not deriving one from scratch. Dense (fully connected) layers are the right default when the input is tabular — a fixed-length vector of features with no inherent spatial or temporal relationship between them, such as a row of a spreadsheet where reordering the columns wouldn't change what the data means. CNNs are the right choice for grid-like data with local structure, where nearby entries are meaningfully related: images are the canonical example, but the same idea extends to spectrograms (audio represented as a 2D time-frequency grid) and any other data with a consistent spatial layout.

RNN/LSTM architectures fit ordered, variable-length sequences, where the order of the data carries information a dense layer would discard on flattening — text, time series, sensor streams, or any data where "what came before" matters for interpreting "what comes now," and where different examples may have different lengths (unlike a fixed-size image or feature vector). The "Beyond" card is an intentional, honest caveat: Transformers, which use an attention mechanism rather than either convolution or recurrence, have become the dominant architecture for many sequence tasks (especially in natural language) precisely because they avoid the sequential bottleneck of RNNs while still modeling long-range dependencies — this course does not cover Transformers in depth, but students should know the architectural landscape did not stop at RNNs and LSTMs.

The unifying test to leave students with: look at the data's structure before choosing an architecture — ask whether nearby entries in space are related (favor CNN), whether nearby entries in time/order are related (favor RNN/LSTM or, increasingly, attention-based models), or neither (dense is often sufficient and simpler). Transition: the final slide closes the loop by naming what stayed the same underneath all this architectural variety.
-->

---
glowSeed: 877
---

# Same Machinery, Specialized Layout

<div class="mt-8"><div class="grid grid-cols-3 gap-4 mt-6">
<div v-click border="2 solid teal-800" bg="teal-800/20" rounded-lg p-4>
<div class="font-bold text-teal-300 mb-2">CNN</div>
<div class="text-sm leading-relaxed opacity-90">Share across space.</div>
</div>
<div v-click border="2 solid blue-800" bg="blue-800/20" rounded-lg p-4>
<div class="font-bold text-blue-300 mb-2">RNN</div>
<div class="text-sm leading-relaxed opacity-90">Share across time.</div>
</div>
<div v-click border="2 solid amber-800" bg="amber-800/20" rounded-lg p-4>
<div class="font-bold text-amber-300 mb-2">Both</div>
<div class="text-sm leading-relaxed opacity-90">Train with backpropagation.</div>
</div>
</div></div>

<div v-click class="mt-10 text-center text-lg" border="2 solid white/10" bg="white/5" rounded-lg px-6 py-4>Next: batch normalization and dropout make deep training more reliable.</div>

<!--
Close by making explicit what this deck deliberately did and did not change, since that framing is the entire point of a "light touch" survey. CNNs share one small kernel's weights across every spatial position; RNNs share one set of transition weights across every time step; both are trained by exactly the same backpropagation machinery covered in the Backpropagation deck — computing a loss, applying the chain rule backward through every operation (whether that operation is a convolution, a recurrence, or an ordinary dense layer), and updating weights with gradient descent. Nothing about the training algorithm itself changed; what changed is which structure the architecture builds in before training even starts, which determines what kind of data the network can exploit efficiently and how quickly it can learn a good solution from a limited number of examples.

Tie this explicitly back to the vanishing-gradient discussion two slides ago and forward to the Practical Training Issues deck: because both CNNs and RNNs are still trained by backpropagation, they remain susceptible to the same depth-driven (or time-driven, for RNNs) gradient problems, and the same toolkit — careful initialization, non-saturating activations, batch normalization, gradient clipping, and (for RNNs specifically) gated architectures like LSTMs — applies to keep them trainable. This is the bridge to the next deck: Practical Training Issues covers those stabilization techniques in full mathematical and numeric detail, and the two companion decks in this folder, Convolutional Neural Networks and RNNs and LSTMs, cover each specialized architecture's mechanics far more rigorously than this survey attempted to. Encourage students who want depth on either architecture to go there next.
-->
