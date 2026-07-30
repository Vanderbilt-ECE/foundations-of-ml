---
theme: default
highlighter: shiki
css: unocss
colorSchema: dark
title: 'RNNs and LSTMs'
info: |
  ## RNNs and LSTMs
  How networks gain memory over sequences, why plain recurrence breaks down, and how gated cell state fixes it.
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
glowSeed: 641
---

<div class="relative z-10">

# RNNs and LSTMs

### Giving Networks Memory Over Sequences

<div class="pt-6 opacity-80 text-lg">
Neural Networks and Deep Learning Basics · Foundations of Machine Learning
</div>

<div class="pt-40 text-sm opacity-60">
From a fixed-size perceptron to a network that reads one token at a time and remembers
</div>

</div>

<!--
Open this deck by connecting it to the MLP material students already have. So far, every network we have built takes one fixed-size input vector and produces one output — no notion of "before" or "after." Language, audio, and time series are fundamentally different: they are ordered sequences of variable length, and meaning depends on that order.

Today's roadmap: first we see precisely why a plain feedforward network cannot handle sequences. Then we build the recurrent neural network (RNN) as the natural fix — a neuron with a memory loop. We will then derive, mechanically, why plain RNNs fail on long sequences (the vanishing/exploding gradient problem), and finally build the LSTM cell that fixes it with a protected "cell state" highway and learned gates. We close with a preview of where the field goes next: attention and Transformers.
-->

---
glowSeed: 642
---

# Why Feedforward Networks Fail on Sequences

<v-clicks>

- A standard MLP takes one **fixed-size** input vector and applies the same weight matrix to it — there is no notion of "position 1" versus "position 2" built into the architecture
- Example: **"the cat sat"** vs. **"sat the cat"** — same three words, same bag of tokens, completely different meaning
- If we feed an MLP the tokens as an unordered set (or concatenate them in a way the network has no reason to treat consistently), it cannot naturally distinguish the two sentences
- Second problem: sequences have **variable length**. A review might be 10 words or 500 words. An MLP's input layer has a fixed number of slots — it cannot stretch or shrink

</v-clicks>

<div v-click class="grid grid-cols-2 gap-6 mt-6">

<div border="2 solid red-800" bg="red-800/20" rounded-lg p-4>
<div class="font-bold text-red-300 mb-1">Order blindness</div>
<div class="text-sm opacity-90">A bag of word-vectors looks identical whether it came from "the cat sat" or "sat the cat"</div>
</div>

<div border="2 solid orange-800" bg="orange-800/20" rounded-lg p-4>
<div class="font-bold text-orange-300 mb-1">Fixed-size input</div>
<div class="text-sm opacity-90">An MLP's input layer has a fixed width; it has no native way to accept 10 tokens today and 500 tomorrow</div>
</div>

</div>

<!--
Two independent failures here, and it is worth separating them clearly for students. The first is an architectural blindness to order: a dense layer computes a weighted sum of its inputs, and a weighted sum has no memory of which input arrived "first" unless we hand-engineer position information into the features ourselves. If "cat", "sat", and "the" each contribute a fixed feature slot regardless of position, permuting the words does not change the input vector the network sees, so it cannot possibly output different predictions for the two orderings without extra help.

The second failure is more mechanical: real sequences vary in length, but a feedforward network's input layer is a fixed number of neurons, wired to a fixed weight matrix shape. You cannot feed a 500-word review through a network built for 10 words without truncating, padding awkwardly, or redesigning the architecture per example.

Common misconception to flag: students sometimes think "we could just add a position feature to each word vector" and call it solved — that is actually part of how Transformers work later, but it does not fix the deeper issue that MLPs process the whole sequence in one shot rather than accumulating information step by step. The natural fix is a network that reads the sequence one token at a time and carries a running memory forward — that is exactly what we build starting next slide, but first we need to talk about how text becomes numbers at all.
-->

---
glowSeed: 643
---

# Turning Text Into Numbers: Tokenization

<v-clicks>

- Networks operate on numbers, not characters — text must be converted first
- **Tokenize:** split the text into pieces. Three common granularities:
  - **Word-level** — intuitive, but the vocabulary is huge and any unseen word breaks it
  - **Subword-level** (e.g. byte-pair encoding) — the modern default; splits rare words into common pieces
  - **Character-level** — tiny vocabulary, but sequences get much longer
- Each unique token is assigned an integer **ID** from a fixed vocabulary — a lookup table, nothing more. The IDs themselves carry no meaning

</v-clicks>

<div v-click class="flex justify-center mt-4">
<svg viewBox="0 0 560 170" class="w-full max-w-2xl" role="img" aria-label="The phrase the cat sat is tokenized into three word pieces and mapped to arbitrary integer IDs 4, 187, and 92">
  <text x="280" y="20" fill="#e2e8f0" style="font-size:15px;text-anchor:middle">"the cat sat"</text>
  <line x1="280" y1="28" x2="280" y2="46" stroke="#64748b" stroke-width="2" stroke-dasharray="3,3" />
  <polygon points="280,46 275,38 285,38" fill="#64748b" />
  <text x="360" y="42" fill="#64748b" style="font-size:10px">tokenize</text>

  <rect x="90" y="55" width="70" height="34" rx="6" fill="none" stroke="#2dd4bf" stroke-width="2" />
  <text x="125" y="77" fill="#5eead4" style="font-size:13px;text-anchor:middle">the</text>
  <rect x="245" y="55" width="70" height="34" rx="6" fill="none" stroke="#2dd4bf" stroke-width="2" />
  <text x="280" y="77" fill="#5eead4" style="font-size:13px;text-anchor:middle">cat</text>
  <rect x="400" y="55" width="70" height="34" rx="6" fill="none" stroke="#2dd4bf" stroke-width="2" />
  <text x="435" y="77" fill="#5eead4" style="font-size:13px;text-anchor:middle">sat</text>

  <line x1="125" y1="89" x2="125" y2="118" stroke="#5eead4" stroke-width="2" />
  <polygon points="125,118 120,110 130,110" fill="#5eead4" />
  <line x1="280" y1="89" x2="280" y2="118" stroke="#5eead4" stroke-width="2" />
  <polygon points="280,118 275,110 285,110" fill="#5eead4" />
  <line x1="435" y1="89" x2="435" y2="118" stroke="#5eead4" stroke-width="2" />
  <polygon points="435,118 430,110 440,110" fill="#5eead4" />

  <rect x="95" y="122" width="60" height="32" rx="6" fill="none" stroke="#f59e0b" stroke-width="2" />
  <text x="125" y="143" fill="#fbbf24" style="font-size:13px;text-anchor:middle">4</text>
  <rect x="250" y="122" width="60" height="32" rx="6" fill="none" stroke="#f59e0b" stroke-width="2" />
  <text x="280" y="143" fill="#fbbf24" style="font-size:13px;text-anchor:middle">187</text>
  <rect x="405" y="122" width="60" height="32" rx="6" fill="none" stroke="#f59e0b" stroke-width="2" />
  <text x="435" y="143" fill="#fbbf24" style="font-size:13px;text-anchor:middle">92</text>

  <text x="280" y="168" fill="#94a3b8" style="font-size:11px;text-anchor:middle">arbitrary vocabulary IDs — no meaning encoded yet</text>
</svg>
</div>

<!--
Tokenization is a purely mechanical preprocessing step, and it is worth walking through why each granularity exists. Word-level tokenization is the most intuitive but produces enormous vocabularies (every inflection, typo, and proper noun needs its own slot) and completely fails on words never seen during training. Character-level tokenization has a tiny, closed vocabulary (26 letters plus punctuation) but turns every sentence into a much longer sequence of tokens, which is harder for the network to model. Subword tokenization, such as byte-pair encoding, is the modern default in large language models: common words stay as one token, rare words get split into frequent sub-pieces, striking a balance between vocabulary size and sequence length.

The key thing to emphasize with the diagram: at this stage we have only produced arbitrary integer IDs via a dictionary lookup. Token ID 187 is not "closer" in meaning to ID 188 than it is to ID 4 — the numbers are just index positions into a vocabulary table, assigned in whatever order the vocabulary was built. Common misconception: students sometimes assume the ID itself is a meaningful numeric feature the network can use directly. It is not — feeding raw IDs into a network would imply a false ordinal relationship between unrelated words. That gap between "arbitrary ID" and "meaningful numeric vector" is exactly what the embedding layer, next, is built to close.
-->

---
glowSeed: 644
---

# Embeddings: From IDs to Meaningful Vectors

<v-clicks>

- An **embedding layer** is a learned lookup table: it maps each token ID to a dense real-valued vector, typically 100–1000 numbers long
- Unlike the token IDs, embedding vectors are **learned** during training via backpropagation, exactly like any other weight matrix
- Words used in similar contexts end up with similar vectors after training — meaning becomes geometry (distance and direction in vector space)
- This embedding vector is exactly what we call $x_t$: the input fed into the RNN or LSTM at time step $t$

</v-clicks>

<div v-click class="mt-4 text-sm" border="2 solid violet-800" bg="violet-800/20" rounded-lg p-4>

A sentence with $T$ tokens becomes a sequence of embedding vectors $x_1, x_2, \ldots, x_T$ — this sequence is what the recurrent network reads, one vector per time step.

</div>

<!--
Two mental pictures are worth giving students. First, mechanically: the embedding layer is literally a big matrix E of shape (vocabulary size × embedding dimension); looking up token ID 187 just means reading row 187 of that matrix. That row is a normal weight vector, updated by gradient descent just like the weights in a dense layer — nothing exotic is happening.

Second, geometrically: once trained on enough text, that vector space acquires structure. Words that tend to appear in similar contexts (say, "cat", "dog", "kitten") end up clustered near each other, while unrelated words end up far apart. This is why "meaning becomes geometry" — semantic similarity gets approximated by vector distance or cosine similarity, concepts already covered in the linear algebra unit.

The critical takeaway to carry into the rest of this lecture: from this point forward, "the input at time t" always means this learned embedding vector x_t, not the raw text and not the raw integer ID. A sentence of length T becomes a sequence x_1 through x_T, each one a vector in R^d. This is precisely the object the RNN is built to consume one step at a time — which is the next slide.
-->

---
glowSeed: 645
---

# What Is an RNN? A Neuron With a Memory Loop

<v-clicks>

- A **recurrent neural network** reuses the *same* weight matrices at every time step — it is not a different neuron per token, it is one set of weights called in a loop
- At each step $t$, it combines the current input $x_t$ with a **hidden state** $h_{t-1}$ carried over from the previous step
- The hidden state $h_t$ is a fixed-size vector summarizing everything the network has read so far
- Because $h_{t-1}$ feeds back in, the output at step $t$ depends on the entire history of tokens, not just $x_t$ alone

</v-clicks>

<div v-click class="mt-4 text-sm" border="2 solid blue-800" bg="blue-800/20" rounded-lg p-4>

$$h_t = f\big(W_{xh}\, x_t + W_{hh}\, h_{t-1} + b\big)$$

$f$ is typically $\tanh$. $W_{xh}$, $W_{hh}$, and $b$ are the **same** matrices/vector at every single time step.

</div>

<!--
Define every symbol explicitly. x_t is the embedding vector for the token at position t, from the previous slide. h_{t-1} is the hidden state produced at the previous step — a fixed-size vector (say, 128 numbers) that is meant to summarize "everything relevant from tokens 1 through t-1." W_xh is the weight matrix that projects the current input into the hidden space; W_hh is the weight matrix that projects the previous hidden state into the new hidden state; b is a bias vector. f is a nonlinearity, usually tanh, squashing the combined signal into a bounded range.

The single most important structural fact, and the one that makes this "recurrent": W_xh, W_hh, and b are the exact same matrices reused at every time step, from t=1 to t=T. This is weight sharing across time, analogous to how a convolutional filter shares weights across space. It is what lets an RNN handle sequences of any length with a fixed number of parameters — solving the variable-length problem from two slides ago directly.

Common misconception to flag here: students often picture h_t as "the output," full stop. It is better described as a compressed memory or running summary — at each step, the network must decide what to keep, overwrite, or discard from h_{t-1} to make room for information from x_t, because h_t has the same fixed size no matter how long the sequence has been so far. That compression is exactly what will cause problems in a few slides. Next we make the recurrence explicit by "unrolling" this loop in time so the repeated structure is visible.
-->

---
glowSeed: 646
---

# The RNN Unrolled in Time

<div class="text-sm opacity-80 mb-2">The loop on the previous slide is the same cell, drawn once per time step — same weights every time</div>

<div class="flex justify-center mt-2">
<svg viewBox="0 0 760 260" class="w-full max-w-4xl" role="img" aria-label="An RNN cell unrolled across four time steps, showing hidden state h passed from each step to the next, with inputs x1 through x4 feeding in from below and outputs y1 through y4 emitted from above">
  <defs>
    <marker id="rnnA" markerWidth="8" markerHeight="8" refX="6" refY="3" orient="auto">
      <path d="M0,0 L6,3 L0,6 Z" fill="#38bdf8" />
    </marker>
  </defs>

  <!-- cell 1 -->
  <rect x="60" y="90" width="90" height="70" rx="10" fill="#0d9488" fill-opacity="0.25" stroke="#2dd4bf" stroke-width="2" />
  <text x="105" y="130" fill="#5eead4" style="font-size:14px;text-anchor:middle">RNN</text>
  <text x="105" y="66" fill="#94a3b8" style="font-size:11px;text-anchor:middle">t = 1</text>
  <line x1="105" y1="230" x2="105" y2="162" stroke="#5eead4" stroke-width="2" marker-end="url(#rnnA)" />
  <text x="105" y="248" fill="#5eead4" style="font-size:12px;text-anchor:middle">x₁</text>
  <line x1="105" y1="88" x2="105" y2="30" stroke="#93c5fd" stroke-width="2" marker-end="url(#rnnA)" />
  <text x="105" y="20" fill="#93c5fd" style="font-size:12px;text-anchor:middle">y₁</text>

  <!-- cell 2 -->
  <rect x="255" y="90" width="90" height="70" rx="10" fill="#0d9488" fill-opacity="0.25" stroke="#2dd4bf" stroke-width="2" />
  <text x="300" y="130" fill="#5eead4" style="font-size:14px;text-anchor:middle">RNN</text>
  <text x="300" y="66" fill="#94a3b8" style="font-size:11px;text-anchor:middle">t = 2</text>
  <line x1="300" y1="230" x2="300" y2="162" stroke="#5eead4" stroke-width="2" marker-end="url(#rnnA)" />
  <text x="300" y="248" fill="#5eead4" style="font-size:12px;text-anchor:middle">x₂</text>
  <line x1="300" y1="88" x2="300" y2="30" stroke="#93c5fd" stroke-width="2" marker-end="url(#rnnA)" />
  <text x="300" y="20" fill="#93c5fd" style="font-size:12px;text-anchor:middle">y₂</text>

  <!-- cell 3 -->
  <rect x="450" y="90" width="90" height="70" rx="10" fill="#0d9488" fill-opacity="0.25" stroke="#2dd4bf" stroke-width="2" />
  <text x="495" y="130" fill="#5eead4" style="font-size:14px;text-anchor:middle">RNN</text>
  <text x="495" y="66" fill="#94a3b8" style="font-size:11px;text-anchor:middle">t = 3</text>
  <line x1="495" y1="230" x2="495" y2="162" stroke="#5eead4" stroke-width="2" marker-end="url(#rnnA)" />
  <text x="495" y="248" fill="#5eead4" style="font-size:12px;text-anchor:middle">x₃</text>
  <line x1="495" y1="88" x2="495" y2="30" stroke="#93c5fd" stroke-width="2" marker-end="url(#rnnA)" />
  <text x="495" y="20" fill="#93c5fd" style="font-size:12px;text-anchor:middle">y₃</text>

  <!-- cell 4 -->
  <rect x="620" y="90" width="90" height="70" rx="10" fill="#0d9488" fill-opacity="0.25" stroke="#2dd4bf" stroke-width="2" />
  <text x="665" y="130" fill="#5eead4" style="font-size:14px;text-anchor:middle">RNN</text>
  <text x="665" y="66" fill="#94a3b8" style="font-size:11px;text-anchor:middle">t = T</text>
  <line x1="665" y1="230" x2="665" y2="162" stroke="#5eead4" stroke-width="2" marker-end="url(#rnnA)" />
  <text x="665" y="248" fill="#5eead4" style="font-size:12px;text-anchor:middle">x_T</text>
  <line x1="665" y1="88" x2="665" y2="30" stroke="#93c5fd" stroke-width="2" marker-end="url(#rnnA)" />
  <text x="665" y="20" fill="#93c5fd" style="font-size:12px;text-anchor:middle">y_T</text>

  <!-- hidden state arrows between cells, same weights -->
  <line x1="150" y1="125" x2="253" y2="125" stroke="#fbbf24" stroke-width="2.5" marker-end="url(#rnnA)" />
  <text x="200" y="112" fill="#fde68a" style="font-size:12px;text-anchor:middle">h₁</text>
  <line x1="345" y1="125" x2="448" y2="125" stroke="#fbbf24" stroke-width="2.5" marker-end="url(#rnnA)" />
  <text x="395" y="112" fill="#fde68a" style="font-size:12px;text-anchor:middle">h₂</text>
  <line x1="540" y1="125" x2="618" y2="125" stroke="#fbbf24" stroke-width="2.5" marker-end="url(#rnnA)" />
  <text x="575" y="112" fill="#fde68a" style="font-size:12px;text-anchor:middle">h₃</text>
  <text x="560" y="152" fill="#94a3b8" style="font-size:14px;text-anchor:middle">···</text>

  <text x="380" y="255" fill="#64748b" style="font-size:11px;text-anchor:middle">every box is literally the same cell — same W_xh, W_hh, b</text>
</svg>
</div>

<!--
This is the standard "unrolled" diagram, and it is worth being explicit that it is a drawing convention, not a different network. There is only one RNN cell and one set of weights (W_xh, W_hh, b); this picture draws it once per time step purely to visualize the computation graph that backpropagation will operate on. Each box receives the current input x_t from below and the hidden state h_{t-1} from its left neighbor, and produces the new hidden state h_t, which becomes the input to the box on its right, as well as (optionally) an output y_t used for a prediction at that time step.

Common misconception to preempt directly: students often think each box in this diagram represents a separate neuron or a separate layer with its own trained weights, similar to how depth works in a deep MLP. That is wrong — depth in an RNN diagram like this represents time, not distinct layers, and every box shares identical parameters. This is why RNNs can process arbitrarily long sequences with a fixed parameter count: we simply unroll the same cell for however many time steps the input sequence has.

This unrolled picture is also exactly what backpropagation through time (BPTT) operates on: gradients get computed by treating the unrolled graph like a very deep feedforward network and applying the chain rule backward through every one of these arrows. That mechanism, and why it breaks down for long sequences, is the subject of the next few slides.
-->

---
glowSeed: 647
---

# The Problem: Backpropagation Through Time

<v-clicks>

- Training an RNN means unrolling it (previous slide) and running ordinary backpropagation on the unrolled graph — this is called **backpropagation through time (BPTT)**
- To get the gradient of the loss at step $T$ with respect to an *early* hidden state $h_k$, the chain rule forces us to multiply together the Jacobian of every step in between
- Roughly, after linearizing the activation function, each factor is proportional to $W_{hh}$, so the gradient contains something like $W_{hh}^{\,T-k}$ — the same matrix multiplied by itself $T-k$ times

</v-clicks>

<div v-click class="mt-4 text-sm" border="2 solid red-800" bg="red-800/20" rounded-lg p-4>

$$
\frac{\partial h_T}{\partial h_k} = \prod_{i=k+1}^{T} \frac{\partial h_i}{\partial h_{i-1}} \approx \prod_{i=k+1}^{T} \text{diag}\big(f'(\cdot)\big)\, W_{hh}
$$

</div>

<!--
Walk through the chain rule mechanics carefully, since this course's math bar requires the real mechanism rather than a hand-wave. h_T depends on h_{T-1}, which depends on h_{T-2}, and so on back to h_k. By the multivariate chain rule, the Jacobian of h_T with respect to h_k is the product of the Jacobians of each consecutive pair, dh_i/dh_{i-1}, for i running from k+1 to T. Each of those individual Jacobians works out to (approximately, after differentiating h_i = f(W_xh x_i + W_hh h_{i-1} + b)) a diagonal matrix of activation-function derivatives f'(·) multiplied by W_hh itself — because h_{i-1} enters the formula for h_i only through the term W_hh h_{i-1}.

The key structural fact: this is the *same* W_hh at every factor, because RNN weights are shared across time (previous two slides). So this product behaves, to a first approximation, like W_hh raised to the power (T - k). That is the mechanical root cause of vanishing and exploding gradients, which the next slide makes concrete with actual numbers and eigenvalues.

Common misconception: students often treat "vanishing gradients" as a vague catchphrase without connecting it to this literal repeated-multiplication structure. Make sure they can state precisely: it is a product of T-k Jacobians, each proportional to the same recurrent weight matrix, and repeated multiplication by the same matrix is what shrinks or grows the result geometrically in the number of time steps.
-->

---
glowSeed: 648
---

# Why Gradients Vanish or Explode

<v-clicks>

- Think of $W_{hh}$ through its eigenvalues. If $v$ is an eigenvector with eigenvalue $\lambda$, then $W_{hh}^n v = \lambda^n v$
- If the **dominant eigenvalue** has $|\lambda| < 1$, then $\lambda^n \to 0$ as $n$ grows — the gradient **vanishes** exponentially in the number of steps
- If $|\lambda| > 1$, then $\lambda^n \to \infty$ — the gradient **explodes** exponentially
- Only the razor's-edge case $|\lambda| \approx 1$ keeps gradients from shrinking or blowing up over long sequences, and training rarely holds a network there on its own

</v-clicks>

<div v-click class="grid grid-cols-2 gap-6 mt-4 text-sm">

<div border="2 solid blue-800" bg="blue-800/20" rounded-lg p-4>
<div class="font-bold text-blue-300 mb-1">Vanishing: scalar weight 0.5</div>
<div class="font-mono text-xs opacity-90">
0.5¹⁰ ≈ 0.00098<br/>
0.5²⁰ ≈ 0.00000095<br/>
0.5⁵⁰ ≈ 8.9 × 10⁻¹⁶
</div>
</div>

<div border="2 solid amber-800" bg="amber-800/20" rounded-lg p-4>
<div class="font-bold text-amber-300 mb-1">Exploding: scalar weight 1.5</div>
<div class="font-mono text-xs opacity-90">
1.5¹⁰ ≈ 57.7<br/>
1.5²⁰ ≈ 3,325<br/>
1.5⁵⁰ ≈ 6.4 × 10⁸
</div>
</div>

</div>

<div v-click class="mt-4" border="2 solid violet-800" bg="violet-800/20" rounded-lg p-4>

<div class="font-bold text-violet-300 mb-1">Telephone-game intuition</div>
<div class="text-sm opacity-90">50 people whisper a message down a line. By the last person, the original signal has been diluted past recognition — this is the intuitive picture for vanishing gradients; the eigenvalue argument above is the actual mechanism producing it.</div>

</div>

<!--
This slide gives both required layers: the real mathematical mechanism and the intuitive analogy, with the math doing the actual explanatory work. Recall from the eigenvalue slide in the linear algebra unit: if v is an eigenvector of W_hh with eigenvalue lambda, applying W_hh repeatedly to v just rescales it by lambda each time, so after n applications we get lambda^n v. Since the BPTT gradient from two slides ago is approximately a product of n copies of W_hh (composed with activation derivatives), its behavior along the dominant eigen-direction is governed by lambda^n, where lambda is the largest-magnitude eigenvalue of W_hh.

Walk through the numeric illustration explicitly: with a scalar recurrent weight of 0.5, repeated multiplication shrinks the value geometrically — by 10 steps it's already under a tenth of a percent of its starting value, and by 50 steps it is smaller than floating-point precision can meaningfully represent, i.e., the gradient signal for anything more than a few dozen steps back is numerically zero. With a scalar weight of 1.5, the opposite happens: the value grows without bound, reaching hundreds of millions by 50 steps — gradients this large make weight updates wildly unstable and can produce NaNs.

Common misconception to correct directly: students often think vanishing/exploding gradients is only an intuitive metaphor about "information getting lost," similar to the telephone game. It is that, but it is caused by something precise and provable: repeated multiplication by the same matrix (or scalar), whose eigenvalues determine geometric growth or decay. The telephone game is a good intuition pump for *why it feels like forgetting*, but the reason it is mathematically inevitable is this eigenvalue argument. Activation functions like tanh compound the problem further, since their derivative is at most 1 and typically much smaller away from zero, pushing the effective eigenvalues of the combined Jacobian below 1 in most regimes — which is part of why vanishing is empirically more common than exploding in practice, though exploding does happen and is usually controlled with gradient clipping.

This is exactly the problem LSTMs were designed to fix. Next we introduce the LSTM cell and its protected cell-state highway.
-->

---
glowSeed: 649
---

# Enter the LSTM: A Protected Memory Highway

<div class="text-sm opacity-80 mb-1">A separate <strong class="text-teal-300">cell state</strong> $C_t$ runs alongside the hidden state — <strong class="text-orange-300">gates</strong> control what flows in, out, and through</div>

<div class="flex justify-center mt-1">
<svg viewBox="0 0 720 380" class="w-full max-w-3xl" role="img" aria-label="Anatomy of one LSTM cell: a cell state line runs left to right through a forget gate multiplication and an input gate addition; a hidden state line runs below through the same gates and an output gate; the current input feeds all three gates from below">
  <defs>
    <marker id="lA" markerWidth="9" markerHeight="9" refX="7" refY="3.5" orient="auto"><path d="M0,0 L8,3.5 L0,7 Z" fill="#e2e8f0" /></marker>
    <marker id="lAT" markerWidth="9" markerHeight="9" refX="7" refY="3.5" orient="auto"><path d="M0,0 L8,3.5 L0,7 Z" fill="#2dd4bf" /></marker>
    <marker id="lAB" markerWidth="9" markerHeight="9" refX="7" refY="3.5" orient="auto"><path d="M0,0 L8,3.5 L0,7 Z" fill="#60a5fa" /></marker>
  </defs>

  <rect x="135" y="72" width="120" height="230" fill="#f97316" fill-opacity="0.06" />
  <rect x="255" y="72" width="170" height="230" fill="#f59e0b" fill-opacity="0.06" />
  <rect x="425" y="72" width="165" height="230" fill="#8b5cf6" fill-opacity="0.06" />

  <rect x="120" y="60" width="485" height="245" rx="26" fill="none" stroke="#94a3b8" stroke-width="2" stroke-dasharray="7,5" />
  <text x="362" y="82" fill="#e2e8f0" style="font-size:13px;text-anchor:middle;font-weight:bold">LSTM Cell</text>

  <text x="195" y="100" fill="#fdba74" style="font-size:11px;text-anchor:middle;font-style:italic">Forget gate</text>
  <text x="340" y="100" fill="#fde68a" style="font-size:11px;text-anchor:middle;font-style:italic">Input gate</text>
  <text x="508" y="100" fill="#c4b5fd" style="font-size:11px;text-anchor:middle;font-style:italic">Output gate</text>

  <!-- cell state line -->
  <line x1="78" y1="125" x2="640" y2="125" stroke="#2dd4bf" stroke-width="3" marker-end="url(#lAT)" />
  <rect x="18" y="108" width="60" height="34" rx="4" fill="#0d9488" fill-opacity="0.2" stroke="#2dd4bf" stroke-width="1.5" />
  <text x="48" y="130" fill="#5eead4" style="font-size:14px;text-anchor:middle;font-style:italic">C_{t-1}</text>
  <rect x="644" y="108" width="60" height="34" rx="4" fill="#0d9488" fill-opacity="0.2" stroke="#2dd4bf" stroke-width="1.5" />
  <text x="674" y="130" fill="#5eead4" style="font-size:14px;text-anchor:middle;font-style:italic">C_t</text>

  <!-- hidden state line -->
  <line x1="78" y1="275" x2="640" y2="275" stroke="#60a5fa" stroke-width="2.5" marker-end="url(#lAB)" />
  <rect x="18" y="258" width="60" height="34" rx="4" fill="#1d4ed8" fill-opacity="0.2" stroke="#60a5fa" stroke-width="1.5" />
  <text x="48" y="280" fill="#93c5fd" style="font-size:14px;text-anchor:middle;font-style:italic">h_{t-1}</text>
  <rect x="644" y="258" width="60" height="34" rx="4" fill="#1d4ed8" fill-opacity="0.2" stroke="#60a5fa" stroke-width="1.5" />
  <text x="674" y="280" fill="#93c5fd" style="font-size:14px;text-anchor:middle;font-style:italic">h_t</text>

  <!-- x_t input -->
  <circle cx="150" cy="345" r="16" fill="#2dd4bf" fill-opacity="0.25" stroke="#5eead4" stroke-width="1.5" />
  <text x="150" y="350" fill="#ccfbf1" style="font-size:13px;text-anchor:middle;font-style:italic">x_t</text>
  <line x1="150" y1="329" x2="150" y2="279" stroke="#5eead4" stroke-width="2" marker-end="url(#lA)" />

  <!-- forget gate -->
  <rect x="172" y="200" width="46" height="28" rx="6" fill="#f97316" fill-opacity="0.25" stroke="#fb923c" stroke-width="1.8" />
  <text x="195" y="219" fill="#fed7aa" style="font-size:13px;text-anchor:middle">σ</text>
  <line x1="195" y1="275" x2="195" y2="228" stroke="#e2e8f0" stroke-width="1.8" marker-end="url(#lA)" />
  <line x1="195" y1="200" x2="195" y2="139" stroke="#e2e8f0" stroke-width="1.8" marker-end="url(#lA)" />
  <circle cx="195" cy="125" r="13" fill="#0f172a" stroke="#f472b6" stroke-width="2" />
  <text x="195" y="130" fill="#f472b6" style="font-size:15px;text-anchor:middle;font-weight:bold">×</text>

  <!-- input gate -->
  <rect x="262" y="200" width="46" height="28" rx="6" fill="#f59e0b" fill-opacity="0.25" stroke="#fbbf24" stroke-width="1.8" />
  <text x="285" y="219" fill="#fde68a" style="font-size:13px;text-anchor:middle">σ</text>
  <line x1="285" y1="275" x2="285" y2="228" stroke="#e2e8f0" stroke-width="1.8" marker-end="url(#lA)" />

  <rect x="337" y="200" width="52" height="28" rx="6" fill="#f59e0b" fill-opacity="0.25" stroke="#fbbf24" stroke-width="1.8" />
  <text x="363" y="219" fill="#fde68a" style="font-size:12px;text-anchor:middle">tanh</text>
  <line x1="363" y1="275" x2="363" y2="228" stroke="#e2e8f0" stroke-width="1.8" marker-end="url(#lA)" />

  <path d="M 285,200 L 285,168 L 344,168" fill="none" stroke="#e2e8f0" stroke-width="1.8" marker-end="url(#lA)" />
  <circle cx="363" cy="168" r="13" fill="#0f172a" stroke="#f472b6" stroke-width="2" />
  <text x="363" y="173" fill="#f472b6" style="font-size:15px;text-anchor:middle;font-weight:bold">×</text>
  <line x1="363" y1="200" x2="363" y2="184" stroke="#e2e8f0" stroke-width="1.8" marker-end="url(#lA)" />
  <line x1="363" y1="155" x2="363" y2="142" stroke="#e2e8f0" stroke-width="1.8" marker-end="url(#lA)" />
  <circle cx="363" cy="125" r="13" fill="#0f172a" stroke="#f472b6" stroke-width="2" />
  <text x="363" y="130" fill="#f472b6" style="font-size:15px;text-anchor:middle;font-weight:bold">+</text>

  <!-- output gate -->
  <line x1="520" y1="125" x2="520" y2="150" stroke="#2dd4bf" stroke-width="2" marker-end="url(#lAT)" />
  <rect x="494" y="154" width="52" height="28" rx="6" fill="#8b5cf6" fill-opacity="0.25" stroke="#a78bfa" stroke-width="1.8" />
  <text x="520" y="173" fill="#ddd6fe" style="font-size:12px;text-anchor:middle">tanh</text>

  <rect x="437" y="208" width="46" height="28" rx="6" fill="#8b5cf6" fill-opacity="0.25" stroke="#a78bfa" stroke-width="1.8" />
  <text x="460" y="227" fill="#ddd6fe" style="font-size:13px;text-anchor:middle">σ</text>
  <line x1="460" y1="275" x2="460" y2="236" stroke="#e2e8f0" stroke-width="1.8" marker-end="url(#lA)" />
  <line x1="483" y1="222" x2="503" y2="222" stroke="#e2e8f0" stroke-width="1.8" marker-end="url(#lA)" />

  <line x1="520" y1="182" x2="520" y2="205" stroke="#e2e8f0" stroke-width="1.8" marker-end="url(#lA)" />
  <circle cx="520" cy="222" r="13" fill="#0f172a" stroke="#f472b6" stroke-width="2" />
  <text x="520" y="227" fill="#f472b6" style="font-size:15px;text-anchor:middle;font-weight:bold">×</text>

  <path d="M 533,222 L 570,222 L 570,271" fill="none" stroke="#60a5fa" stroke-width="2" marker-end="url(#lAB)" />

  <text x="362" y="330" fill="#64748b" style="font-size:11px;text-anchor:middle">x_t and h_{t-1} feed every gate — only the learned weights differ per gate</text>
</svg>
</div>

<!--
This is the anatomical diagram of one LSTM cell — take time to trace each rail with the class. Two lines run through the cell: the cell state C, along the top, and the hidden state h, along the bottom. Both x_t (current input) and h_{t-1} (previous hidden state) feed into all three gates from below; only the learned weight matrices differ between gates.

Follow the cell-state rail left to right: C_{t-1} enters, gets multiplied elementwise by the forget gate's output (the leftmost × — this is "erase old memory"), then has the input gate's contribution added to it (the + in the middle — "write new memory"), producing C_t on the right. Note there is no matrix multiplication anywhere along this top rail — only elementwise multiplication and addition. That absence is the entire point, and the next slide makes precise why it matters for gradients.

The hidden state rail is where the actual gating decisions get computed: h_{t-1} and x_t combine (via ordinary weighted sums, exactly like a plain RNN) inside each sigma or tanh box to produce the gate values, which then reach up to interact with the cell-state rail. The rightmost region, the output gate, reads the freshly updated C_t, squashes it with tanh, and multiplies by a sigmoid-gated fraction to produce the new hidden state h_t, which both exits the cell and feeds into the next time step alongside C_t.

Common misconception to flag immediately: students often think each gate is itself a full separate neural network. It is not — each gate (forget, input, output) is a single sigmoid layer, i.e., one weighted sum followed by a sigmoid nonlinearity, producing a vector of values between 0 and 1 that elementwise-gates another vector. Also flag: the cell state C_t and the hidden state h_t are NOT the same object — C_t is the protected long-term memory, h_t is the (bounded, tanh-squashed) working output derived from it at this instant. We define each gate's exact equation on the next slide.
-->

---
glowSeed: 650
---

# The Forget and Input Gates

<v-clicks>

- **Forget gate** $f_t$: how much of the old cell state to keep (1 = keep everything, 0 = erase completely)

$$f_t = \sigma\big(W_f \cdot [h_{t-1}, x_t] + b_f\big)$$

- **Input gate** $i_t$: how much of the new candidate information to write in
- **Candidate cell state** $\tilde{C}_t$: the new information *proposed* for the cell state, before gating

$$
\begin{aligned}
i_t &= \sigma\big(W_i \cdot [h_{t-1}, x_t] + b_i\big) \\
\tilde{C}_t &= \tanh\big(W_C \cdot [h_{t-1}, x_t] + b_C\big)
\end{aligned}
$$

</v-clicks>

<div v-click class="mt-4 text-sm" border="2 solid amber-800" bg="amber-800/20" rounded-lg p-4>

Why $\sigma$ for the gates but $\tanh$ for the candidate? Sigmoid squashes to $[0,1]$ — perfect for "what fraction to let through." Tanh squashes to $[-1,1]$ — appropriate for a signed value that can add to or subtract from memory.

</div>

<!--
Define every symbol. $[h_{t-1}, x_t]$ denotes concatenating the previous hidden state and the current input into one longer vector; W_f, W_i, W_C are learned weight matrices (one set per gate/candidate), and b_f, b_i, b_C are learned biases. sigma is the logistic sigmoid function, squashing any real number to the open interval (0,1).

Walk through what each equation computes. The forget gate f_t looks at "what just happened" (h_{t-1} and x_t) and outputs, for every entry of the cell state vector, a number between 0 and 1 saying how much of that entry to retain. An entry near 1 means "keep this piece of memory," near 0 means "erase it" — for example, an LSTM tracking grammatical gender in a sentence might learn to zero out that memory entry once a new subject with a different gender appears. The input gate i_t similarly outputs a number in [0,1] per entry, but this time it gates how much of a *proposed new value* gets written in. The candidate C̃_t is that proposed new value itself — computed with tanh rather than sigmoid because it is meant to represent a genuine value that could be added to or subtracted from the running memory, not a 0-to-1 "how much" fraction. This sigmoid-vs-tanh distinction is worth drilling: sigmoid answers "how much," tanh answers "what value."

Common misconception to correct explicitly here, since it is one of the most frequent errors: each gate is a vector of numbers in [0,1], one number per dimension of the cell state — it is NOT a separate neural network making an independent yes/no decision. A "gate" elementwise-multiplies another vector; think of it as a set of dials, each one independently turned somewhere between fully closed and fully open, not as a switch or a classifier. Next slide combines these two gates into the actual cell-state update equation, and introduces the output gate.
-->

---
glowSeed: 651
---

# Updating the Cell State and Producing the Output

<v-clicks>

- **Cell state update:** combine what survives from before with what's newly written in

$$C_t = f_t * C_{t-1} + i_t * \tilde{C}_t$$

- **Output gate** $o_t$: how much of the (now updated) cell state to expose as the hidden state

$$
\begin{aligned}
o_t &= \sigma\big(W_o \cdot [h_{t-1}, x_t] + b_o\big) \\
h_t &= o_t * \tanh(C_t)
\end{aligned}
$$

</v-clicks>

<div v-click class="mt-4 text-sm" border="2 solid teal-800" bg="teal-800/20" rounded-lg p-4>

Every $*$ above is elementwise multiplication — a Hadamard product, not a matrix multiplication. This is the mechanical detail that will matter enormously on the next slide.

</div>

<!--
Walk through the cell-state update line by line. C_t = f_t * C_{t-1} + i_t * C̃_t says: take the old cell state, keep only the fraction of each entry that the forget gate says to keep (elementwise multiplication by f_t), then add in the fraction of the new candidate values that the input gate says to admit (elementwise multiplication of i_t and C̃_t). The asterisk here denotes the Hadamard product — elementwise multiplication of same-shaped vectors — not a matrix multiplication. This is a crucial distinction to make explicit, because the next slide's entire argument about why gradients survive rests on this being elementwise rather than a matrix product.

Then the output gate: o_t is computed exactly like the forget and input gates, a sigmoid over a weighted combination of h_{t-1} and x_t. The hidden state h_t is produced by squashing the freshly updated cell state with tanh (bounding it to [-1, 1] for use as an output/working representation) and then gating it elementwise with o_t — deciding how much of that squashed memory to actually expose at this time step versus keep hidden internally in C_t for later use.

Common misconception to flag again, because it recurs constantly: C_t and h_t are different objects with different roles. C_t is the long-term, largely unconstrained memory (it can grow in magnitude over many steps since it is only ever multiplied/added elementwise, never squashed on the main path). h_t is a bounded, immediately-usable summary derived from C_t at this instant via tanh and the output gate — it's what gets passed to any output layer and what feeds into the next time step's gate computations. Students who conflate these two will misread every diagram of an LSTM. Next we make explicit why routing memory through C_t this way — rather than through a repeatedly matrix-multiplied hidden state, as in a plain RNN — solves the vanishing gradient problem from a few slides ago.
-->

---
glowSeed: 652
---

# Why the Cell State Fixes Vanishing Gradients

<v-clicks>

- Recall the vanilla RNN's problem: $h_t$ is produced by repeated **matrix multiplication** by $W_{hh}$ *and* squashed through a nonlinearity at *every single step* — the source of the $W_{hh}^n$ term that vanishes or explodes
- The LSTM's cell-state update, $C_t = f_t * C_{t-1} + i_t * \tilde{C}_t$, involves only **elementwise** multiplication and addition — no matrix multiply, no repeated squashing nonlinearity on this path
- When $f_t \approx 1$, the gradient of the loss with respect to $C_{t-1}$ passing through this update is multiplied by approximately 1 — a **near-identity mapping**
- This is the exact same intuition as a **residual / skip connection**: an unimpeded path lets gradient flow backward across many steps largely unchanged

</v-clicks>

<div v-click class="mt-4" border="2 solid red-800" bg="red-800/20" rounded-lg p-4>

<div class="font-bold text-red-300 mb-1">Important: mitigates, does not eliminate</div>
<div class="text-sm opacity-90">The cell state highway substantially reduces vanishing gradients, but $f_t$ is learned and rarely sits at exactly 1 for every dimension over arbitrarily long spans — very long sequences can still degrade LSTM memory, just far less severely than a plain RNN.</div>

</div>

<!--
This is the core mechanical payoff of the whole lecture, so connect it explicitly back to the BPTT derivation from earlier. Recall: for the plain RNN, dh_T/dh_k was approximately a product of T-k copies of W_hh (times activation derivatives), and that repeated matrix multiplication is what produces exponential vanishing or explosion via the dominant eigenvalue.

Now look at the cell-state path in the LSTM. Taking the derivative of C_t with respect to C_{t-1} in the update C_t = f_t * C_{t-1} + i_t * C̃_t: since this is elementwise multiplication (not a matrix product), the derivative along this path is just f_t itself (a vector of gate values, applied elementwise), plus additional terms from how f_t, i_t, and C̃_t themselves depend on C_{t-1} indirectly through h_{t-1} — which are typically small compared to the direct f_t term. If the forget gate has learned to hold a particular memory entry open (f_t close to 1 for that entry), then propagating the gradient of the loss backward through that entry across many time steps multiplies by approximately 1 repeatedly, rather than by a shrinking or exploding factor of W_hh each time. That is a near-identity mapping, structurally identical in spirit to the residual/skip connections used in very deep feedforward and convolutional networks (a preview of terminology from other units): an unobstructed additive path that lets gradient information travel across depth (or here, time) with far less decay.

Critical caveat, and a very common misconception among students first learning LSTMs: this does NOT mean LSTMs are immune to vanishing gradients. f_t is itself a learned, input-dependent vector of numbers in [0,1] — it is not fixed at exactly 1, and different entries of the cell state may have forget gates that are well below 1 for long stretches, especially early in training before the network has learned to protect the memory it needs. LSTMs substantially mitigate the vanishing gradient problem relative to plain RNNs — they can learn dependencies spanning hundreds of steps rather than a handful — but they do not eliminate the problem outright, and extremely long sequences (thousands of steps) can still degrade performance. This nuance is exactly why the field eventually moved toward attention-based architectures that avoid the sequential bottleneck altogether, which we preview on the closing slide.
-->

---
layout: center
class: text-center
glowSeed: 653
---

# Wrap-Up: RNN vs. LSTM, and What's Next

<div class="grid grid-cols-2 gap-8 mt-6 text-left">

<div v-click border="2 solid blue-800" bg="blue-800/20" rounded-lg p-4>
<div class="font-bold text-blue-300 mb-2">RNN chain</div>
<svg viewBox="0 0 220 60" class="w-full" role="img" aria-label="RNN chain: hidden state passed sequentially between three cells with no protected highway">
  <rect x="10" y="12" width="40" height="34" rx="6" fill="none" stroke="#60a5fa" stroke-width="2" />
  <rect x="90" y="12" width="40" height="34" rx="6" fill="none" stroke="#60a5fa" stroke-width="2" />
  <rect x="170" y="12" width="40" height="34" rx="6" fill="none" stroke="#60a5fa" stroke-width="2" />
  <line x1="50" y1="29" x2="88" y2="29" stroke="#93c5fd" stroke-width="2" />
  <polygon points="88,29 80,24 80,34" fill="#93c5fd" />
  <line x1="130" y1="29" x2="168" y2="29" stroke="#93c5fd" stroke-width="2" />
  <polygon points="168,29 160,24 160,34" fill="#93c5fd" />
</svg>
<div class="text-sm mt-2 opacity-90">One shared weight matrix multiplied repeatedly — memory decays geometrically with $|\lambda(W_{hh})|$</div>
</div>

<div v-click border="2 solid teal-800" bg="teal-800/20" rounded-lg p-4>
<div class="font-bold text-teal-300 mb-2">LSTM chain</div>
<svg viewBox="0 0 220 60" class="w-full" role="img" aria-label="LSTM chain: a protected cell-state highway runs straight through three cells above the gated hidden-state path">
  <line x1="6" y1="16" x2="214" y2="16" stroke="#2dd4bf" stroke-width="3" />
  <rect x="10" y="26" width="40" height="20" rx="5" fill="none" stroke="#2dd4bf" stroke-width="2" />
  <rect x="90" y="26" width="40" height="20" rx="5" fill="none" stroke="#2dd4bf" stroke-width="2" />
  <rect x="170" y="26" width="40" height="20" rx="5" fill="none" stroke="#2dd4bf" stroke-width="2" />
</svg>
<div class="text-sm mt-2 opacity-90">A protected, mostly-elementwise cell-state highway + learned gates — memory survives far longer</div>
</div>

</div>

<div v-click class="mt-8 max-w-3xl mx-auto text-left text-sm" border="2 solid violet-800" bg="violet-800/20" rounded-lg p-4>

**Looking ahead:** Hochreiter & Schmidhuber introduced the LSTM in 1997, and it remained the dominant sequence architecture for two decades. LSTMs are still sequential — step $t$ must finish before step $t+1$ can start, which limits training speed. Modern large-scale models mostly replace recurrence with **attention** (Transformers), letting every position look directly at every other position with no step-by-step bottleneck. That mechanism is its own lecture — out of scope here, but this is where the story goes next.

</div>

<!--
Close by putting the two architectures side by side using the diagrams: the plain RNN chain has hidden state passed cell to cell with no protected path, so its effective memory decays at a rate governed by the eigenvalues of W_hh, exactly as derived earlier. The LSTM chain adds the cell-state highway running above the hidden-state path, giving gradients (and hence long-range dependencies) a much more direct route backward through time, subject to the caveat from the previous slide that this mitigates rather than eliminates the problem.

Cite Hochreiter & Schmidhuber (1997) explicitly as the origin of the LSTM architecture — it predates most of modern deep learning and was designed specifically to solve the vanishing gradient problem we derived mathematically earlier in this lecture. Note for students: LSTMs (and GRUs, a simplified cousin) dominated sequence modeling in NLP, speech, and time series from the mid-2000s through the mid-2010s.

Preview the next chapter of the story without teaching it: the fundamental limitation LSTMs never solved is that recurrence is inherently sequential — you cannot compute h_t before h_{t-1} is done, which prevents parallelizing computation across the time dimension during training. "Attention Is All You Need" (Vaswani et al., 2017) replaced recurrence entirely with attention, letting every position attend directly to every other position in parallel, removing the sequential bottleneck altogether. Make clear this is a forward pointer only — the mechanics of attention and Transformers are a separate lecture, not something to derive here. Take questions before closing.
-->

---
layout: center
class: text-center
glowSeed: 654
---

# Thank You

### Questions &amp; Discussion

<div class="pt-6 opacity-80">
RNNs and LSTMs · Neural Networks and Deep Learning Basics
</div>

<!--
Open the floor for questions. Good prompts if the room is quiet: ask a student to state, in their own words, the difference between the cell state and the hidden state; ask another to explain why a forget gate is a vector of values in [0,1] rather than a separate network; ask whether LSTMs fully solve vanishing gradients (they do not — they mitigate it). Close by reminding students that the next unit builds on the "memory bottleneck" theme raised here, moving toward attention and Transformers.
-->
