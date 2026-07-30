---
theme: default
highlighter: shiki
css: unocss
colorSchema: dark
title: 'Convolutional Neural Networks'
info: |
  ## Convolutional Neural Networks
  Convolution, weight sharing, and the architecture that taught machines to see.
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
glowSeed: 512
---

<div class="relative z-10">

# Convolutional Neural Networks

### Convolution, Weight Sharing, and the Architecture That Taught Machines to See

<div class="pt-6 opacity-80 text-lg">
Neural Networks and Deep Learning Basics · Foundations of Machine Learning
</div>

<div class="pt-40 text-sm opacity-60">
Dense layers do not scale to images — today we derive, piece by piece, the architecture that does
</div>

</div>

<!--
Open by connecting this to the prior lecture on dense (fully-connected) feedforward networks and backpropagation. Everything students already know about layers, weights, activations, and gradient descent still applies here — what changes is the *shape* of the layer, not the training algorithm.

Roadmap for today: first we quantify exactly why a plain dense layer breaks down on a realistic image (a concrete parameter count, not just "it's bad"). Then we build the convolution operation from scratch with worked numeric arithmetic, show why weight sharing collapses the parameter count so dramatically, look at what a trained CNN's layers actually learn (citing the classic Zeiler & Fergus visualization work), walk a numeric max-pooling example, assemble a full architecture end to end, and finish by mapping every problem from the opening slide to the specific mechanism that fixes it. By the end, students should be able to compute the parameter count of a conv layer by hand and explain, in one sentence each, why convolution restores spatial structure and translation invariance that a flattened dense layer throws away.
-->

---
glowSeed: 513
---

# The Cost of Ignoring Image Structure

<div class="text-center text-lg my-3 text-teal-300 font-mono">
224 × 224 × 3 = 150,528 inputs
</div>

<div class="grid grid-cols-2 gap-6 mt-4">

<div v-click border="2 solid red-800" bg="red-800/20" rounded-lg p-4>
<div class="font-bold text-red-300 mb-2">A single dense hidden layer</div>
<div class="text-sm leading-relaxed opacity-90">
150,528 inputs fully connected to 1,000 hidden units:
</div>
<div class="text-center text-xl font-bold text-red-300 font-mono my-3">
150,528 × 1,000 = 150,528,000
</div>
<div class="text-sm opacity-80">weights, plus 1,000 biases — for one layer, before any output layer exists</div>
</div>

<div v-click border="2 solid red-800" bg="red-800/20" rounded-lg p-4>
<div class="font-bold text-red-300 mb-2">Four concrete failures</div>
<div class="text-sm leading-relaxed opacity-90 flex flex-col gap-2">
<div><strong>Compute:</strong> 150M multiply-adds per image, per forward pass</div>
<div><strong>Data hunger:</strong> that many free parameters need a comparably enormous labeled dataset to avoid overfitting</div>
<div><strong>No spatial structure:</strong> pixel (1,1) and pixel (224,224) are just two entries in a flat vector — "neighbor" has no meaning</div>
<div><strong>No translation invariance:</strong> a cat in the top-left and the same cat in the bottom-right activate completely different weights</div>
</div>
</div>

</div>

<div v-click class="mt-6 text-center text-lg opacity-90">
There has to be a better way.
</div>

<!--
Walk the arithmetic aloud, slowly: a 224×224 RGB image has 224 × 224 × 3 = 150,528 individual numbers once you count all three color channels. Flattening it into a single vector and fully connecting it to just 1,000 hidden units — a small hidden layer by modern standards — requires one weight per (input, hidden-unit) pair, so 150,528 × 1,000 = 150,528,000 weights. That is a single hidden layer, not the whole network, and does not yet include the output layer.

Four distinct problems follow from this, and it is worth separating them because CNNs fix them with different mechanisms later in the lecture. (1) Computational cost: 150M multiply-add operations per image, repeated over every training image and every epoch, is expensive. (2) Data hunger: a rule of thumb in statistical learning is that you need training examples on the same order as your free parameters to avoid severe overfitting — 150M parameters implies needing datasets far larger than anything feasible to collect and label. (3) No spatial structure: flattening destroys the 2D grid layout; the network has no built-in notion that pixel (5,5) is close to pixel (5,6) and far from pixel (200,200) — it has to relearn locality from scratch, wasting capacity. (4) No translation invariance: because every input pixel connects to every hidden unit with an independent weight, a pattern (like a cat's ear) appearing in a different location must be learned as if it were a completely different pattern, multiplying the amount of data and capacity needed by roughly the number of possible pattern locations.

Common misconception to flag: this is not saying dense layers are "bad" in general — they work fine on tabular data with no spatial or ordering structure. The failure is specific to inputs like images where nearby values are correlated and patterns can appear anywhere.

Next: we fix all four problems with one operation — convolution. Let's build it from the ground up.
-->

---
glowSeed: 514
---

# The Convolution Operation

<div class="text-sm opacity-80 mb-3">A small filter (kernel) slides across the input, computing a dot product at every position</div>

<div class="grid grid-cols-2 gap-6 items-start">

<div>

<v-clicks>

- Place the kernel at the top-left corner of the input
- Multiply each kernel weight by the pixel value underneath it
- Sum the products into a single output value
- Slide the kernel one step (the **stride**) and repeat across the whole input

</v-clicks>

<div v-click class="mt-4 text-sm" border="2 solid teal-800" bg="teal-800/20" rounded-lg px-4 py-3>

$$
Y_{i,j} = \sum_{u=0}^{2}\sum_{v=0}^{2} K_{u,v}\, X_{i+u,\,j+v}
$$

</div>

</div>

<div>
<svg viewBox="0 0 340 170" class="w-full max-w-md mx-auto" role="img" aria-label="A 3 by 3 kernel positioned over the top-left corner of a 5 by 5 input grid, with an arrow pointing to a smaller output feature map">
  <g stroke="#475569" stroke-width="1" fill="none">
    <rect x="16" y="20" width="120" height="120"/>
    <line x1="40" y1="20" x2="40" y2="140"/><line x1="64" y1="20" x2="64" y2="140"/><line x1="88" y1="20" x2="88" y2="140"/><line x1="112" y1="20" x2="112" y2="140"/>
    <line x1="16" y1="44" x2="136" y2="44"/><line x1="16" y1="68" x2="136" y2="68"/><line x1="16" y1="92" x2="136" y2="92"/><line x1="16" y1="116" x2="136" y2="116"/>
  </g>
  <rect x="16" y="20" width="72" height="72" fill="#2dd4bf" fill-opacity="0.25" stroke="#2dd4bf" stroke-width="2.5"/>
  <text x="76" y="156" fill="#94a3b8" style="font-size:11px" text-anchor="middle">5×5 input · 3×3 kernel</text>

  <line x1="150" y1="80" x2="212" y2="80" stroke="#94a3b8" stroke-width="2" marker-end="url(#arrCNN)"/>
  <defs><marker id="arrCNN" markerWidth="9" markerHeight="9" refX="6" refY="3" orient="auto"><path d="M0,0 L6,3 L0,6 Z" fill="#94a3b8"/></marker></defs>

  <g stroke="#475569" stroke-width="1" fill="none">
    <rect x="230" y="35" width="90" height="90"/>
    <line x1="260" y1="35" x2="260" y2="125"/><line x1="290" y1="35" x2="290" y2="125"/>
    <line x1="230" y1="65" x2="320" y2="65"/><line x1="230" y1="95" x2="320" y2="95"/>
  </g>
  <rect x="230" y="35" width="30" height="30" fill="#2dd4bf" fill-opacity="0.5"/>
  <text x="275" y="156" fill="#94a3b8" style="font-size:11px" text-anchor="middle">3×3 output feature map</text>
</svg>
</div>

</div>

<!--
Define terms precisely before the arithmetic example on the next slide. A kernel (also called a filter) is a small grid of learnable numbers — commonly 3×3 for images. The input here is shown as a 5×5 grid for illustration (a real image channel would be much larger, e.g. 224×224). At each position, we overlay the kernel on a patch of the input the same size as the kernel, multiply each kernel weight by the input value directly beneath it, and sum all the products into one number — that is a dot product between the flattened kernel and the flattened patch. That single number becomes one entry of the output, called a feature map. The kernel then slides over by the stride (1 pixel here) and the process repeats, producing one output value per position. With a 5×5 input, a 3×3 kernel, and stride 1, the kernel fits in 3×3 = 9 positions, so the output feature map is 3×3.

Common misconception: students often think the filter is "applied once" to the image, like a single dot product for the whole thing. It is not — the same 9 weights are applied repeatedly, once per spatial position, producing many outputs, not one. That repetition is the seed of weight sharing, which we quantify two slides from now.

Next: let's make this concrete with real numbers — an edge-detecting kernel applied to an actual numeric grid, worked out arithmetic and all.
-->

---
glowSeed: 515
---

# Convolution, Worked in Numbers

<div class="grid grid-cols-2 gap-6 items-start">

<div>

<div class="text-sm mb-2 opacity-80">A 4×4 input patch and a Sobel-style vertical edge kernel:</div>

<div class="grid grid-cols-2 gap-3">
<div border="2 solid blue-800" bg="blue-800/20" rounded-lg p-3 class="font-mono text-sm text-center">
<div class="font-bold text-blue-300 mb-1 font-sans">Input X</div>
<div>2  4  1  3</div>
<div>1  5  2  0</div>
<div>3  6  2  1</div>
<div>0  1  4  2</div>
</div>
<div border="2 solid violet-800" bg="violet-800/20" rounded-lg p-3 class="font-mono text-sm text-center">
<div class="font-bold text-violet-300 mb-1 font-sans">Kernel K</div>
<div>-1&nbsp; 0&nbsp; 1</div>
<div>-2&nbsp; 0&nbsp; 2</div>
<div>-1&nbsp; 0&nbsp; 1</div>
</div>
</div>

<div v-click class="mt-4 text-sm" border="2 solid teal-800" bg="teal-800/20" rounded-lg p-3>
<div class="font-bold text-teal-300 mb-1">Top-left 3×3 patch, position (0,0)</div>
<div class="font-mono text-xs leading-relaxed">
(2)(-1)+(4)(0)+(1)(1)<br/>
+(1)(-2)+(5)(0)+(2)(2)<br/>
+(3)(-1)+(6)(0)+(2)(1)
</div>
<div class="mt-2">= -2 + 0 + 1 - 2 + 0 + 4 - 3 + 0 + 2 = <strong class="text-teal-300">0</strong></div>
</div>

</div>

<div>
<svg viewBox="0 0 260 220" class="w-full max-w-sm mx-auto" role="img" aria-label="4 by 4 numeric grid with the top-left 3 by 3 patch highlighted, feeding into a single output value of zero">
  <g stroke="#475569" stroke-width="1" fill="none">
    <rect x="10" y="10" width="160" height="160"/>
    <line x1="50" y1="10" x2="50" y2="170"/><line x1="90" y1="10" x2="90" y2="170"/><line x1="130" y1="10" x2="130" y2="170"/>
    <line x1="10" y1="50" x2="170" y2="50"/><line x1="10" y1="90" x2="170" y2="90"/><line x1="10" y1="130" x2="170" y2="130"/>
  </g>
  <rect x="10" y="10" width="120" height="120" fill="#2dd4bf" fill-opacity="0.2" stroke="#2dd4bf" stroke-width="2.5"/>
  <g fill="#e2e8f0" style="font-size:15px" text-anchor="middle" font-family="monospace">
    <text x="30" y="35">2</text><text x="70" y="35">4</text><text x="110" y="35">1</text><text x="150" y="35">3</text>
    <text x="30" y="75">1</text><text x="70" y="75">5</text><text x="110" y="75">2</text><text x="150" y="75">0</text>
    <text x="30" y="115">3</text><text x="70" y="115">6</text><text x="110" y="115">2</text><text x="150" y="115">1</text>
    <text x="30" y="155">0</text><text x="70" y="155">1</text><text x="110" y="155">4</text><text x="150" y="155">2</text>
  </g>
  <line x1="180" y1="90" x2="212" y2="90" stroke="#94a3b8" stroke-width="2" marker-end="url(#arrW)"/>
  <defs><marker id="arrW" markerWidth="9" markerHeight="9" refX="6" refY="3" orient="auto"><path d="M0,0 L6,3 L0,6 Z" fill="#94a3b8"/></marker></defs>
  <rect x="220" y="70" width="40" height="40" fill="#2dd4bf" fill-opacity="0.35" stroke="#2dd4bf" stroke-width="2"/>
  <text x="240" y="95" fill="#5eead4" style="font-size:18px;font-weight:700" text-anchor="middle" font-family="monospace">0</text>
  <text x="240" y="130" fill="#94a3b8" style="font-size:10px" text-anchor="middle">output (0,0)</text>
</svg>
</div>

</div>

<!--
This is a Sobel-style vertical-edge kernel: negative weights on the left column, zero weights in the middle, positive weights on the right column. Its effect is to respond strongly wherever pixel intensity changes sharply from left to right (a vertical edge) and to output near zero over flat, unchanging regions.

Walk the arithmetic exactly as shown: overlay the kernel on the top-left 3×3 patch of X — rows [2,4,1 / 1,5,2 / 3,6,2] — and multiply elementwise with K's [-1,0,1 / -2,0,2 / -1,0,1], then sum all nine products: (2)(-1) + (4)(0) + (1)(1) + (1)(-2) + (5)(0) + (2)(2) + (3)(-1) + (6)(0) + (2)(1) = -2 + 0 + 1 - 2 + 0 + 4 - 3 + 0 + 2 = 0. That single number becomes entry (0,0) of the output feature map. To get entry (0,1), you would slide the kernel one column right — onto columns 2-4 of the top three rows — and repeat the same nine multiplications and sum. A real forward pass does this at every valid position, producing a full feature map, then typically adds a bias and applies ReLU.

Common misconception: students sometimes flip the sign convention or forget that the middle column contributes zero regardless of pixel value — check that arithmetic on the board if anyone looks uncertain, since forgetting a zero-weight column is a common error when computing by hand.

Next: this same 9-weight kernel is reused at every single position across the entire image — that reuse is called weight sharing, and it is the single idea that collapses the 150-million-parameter dense layer down to a few hundred parameters.
-->

---
glowSeed: 516
---

# Weight Sharing — The Same Filter, Everywhere

<div class="grid grid-cols-2 gap-6 mt-2">

<div v-click border="2 solid red-800" bg="red-800/20" rounded-lg p-4>
<div class="font-bold text-red-300 mb-2">Dense layer</div>
<div class="text-sm mb-2 opacity-90">224×224×3 image → 1,000 hidden units</div>
<div class="text-center text-2xl font-bold text-red-300 font-mono my-2">150,528,000</div>
<div class="text-sm opacity-70">independent weights — a fresh weight for every (pixel, unit) pair</div>
</div>

<div v-click border="2 solid teal-800" bg="teal-800/20" rounded-lg p-4>
<div class="font-bold text-teal-300 mb-2">Conv layer: 32 filters, 3×3, 3 input channels</div>
<div class="text-sm mb-2 opacity-90 font-mono">3 × 3 × 3 × 32 + 32 = 896</div>
<div class="text-center text-2xl font-bold text-teal-300 font-mono my-2">896</div>
<div class="text-sm opacity-70">total learnable parameters — every filter is reused at every spatial location</div>
</div>

</div>

<div v-click class="text-center text-lg my-4 text-amber-300 font-mono">
150,528,000 / 896 ≈ 168,000× fewer parameters
</div>

<div class="grid grid-cols-2 gap-6 mt-2">

<div v-click border="2 solid blue-800" bg="blue-800/20" rounded-lg p-4>
<div class="font-bold text-blue-300 mb-2">Why fewer parameters is possible</div>
<div class="text-sm opacity-90">An edge is worth detecting anywhere in the image, not only in the top-left corner — so one small set of weights, reused, does the job of millions of independent ones.</div>
</div>

<div v-click border="2 solid blue-800" bg="blue-800/20" rounded-lg p-4>
<div class="font-bold text-blue-300 mb-2">Why it gives translation invariance</div>
<div class="text-sm opacity-90">Because the identical filter slides over every position, the same feature detector fires wherever the pattern appears — a cat's ear in the corner produces the same response as a cat's ear in the center.</div>
</div>

</div>

<!--
Do the parameter count carefully, because the arithmetic differs from the earlier 3×3 example: a real conv layer's kernel spans the full depth of its input, not just one channel. A 224×224×3 RGB image has 3 input channels, so each 3×3 filter is actually 3×3×3 = 27 weights (one 3×3 patch per channel, summed together), plus 1 bias, giving 28 parameters per filter. With 32 independent filters, that is 32 × 28 = 3 × 3 × 3 × 32 + 32 = 864 + 32 = 896 parameters total for the whole conv layer — regardless of whether the image is 224×224 or 4,000×4,000, because the same 896 numbers are reused at every spatial location. Compare that to the 150,528,000 weights the dense layer needed for just 1,000 hidden units, and the ratio is roughly 168,000-fold fewer parameters for a comparable amount of visual processing power (32 learned feature detectors instead of 1,000 unstructured ones — not a perfectly apples-to-apples comparison, but the order-of-magnitude gap is the point).

Two distinct benefits follow from reuse, and it's worth keeping them conceptually separate. First, drastically fewer parameters means less compute and — per the data-hunger problem from two slides ago — far less training data is needed to fit them reliably. Second, translation invariance: because the exact same 27 weights plus bias are applied at every (i, j) position, a pattern that the filter has learned to detect produces the same activation magnitude no matter where in the image it appears. This is fundamentally different from the dense layer, where "cat in the top-left" and "cat in the bottom-right" would need to be learned as two unrelated patterns using two disjoint sets of weights.

Common misconception: weight sharing does not mean the network only detects one feature. Each of the 32 filters has its own independently-learned 27+1 parameters and produces its own feature map — 32 different learned pattern detectors, each individually shared across all spatial positions.

Next: what do these filters actually learn to detect once training is complete? The answer forms a hierarchy, from simple edges in the first layer to whole objects many layers deep — this was empirically visualized by Zeiler and Fergus in 2014.
-->

---
glowSeed: 517
---

# The Feature Hierarchy

<div class="text-sm opacity-80 mb-3">Nobody hand-designs these detectors — they emerge from backpropagation</div>

<div class="grid grid-cols-2 gap-6 items-start">

<div>

| Depth | What it detects |
|-------|---------|
| **Layer 1** | Edges, oriented gradients, color blobs |
| **Layer 2–3** | Textures, corners, simple curves |
| **Layer 4–5** | Object parts — eyes, wheels, fur patterns |
| **Deep layers** | Whole objects, in context |

<div v-click class="mt-3 text-xs opacity-60 italic">Zeiler & Fergus, "Visualizing and Understanding Convolutional Networks" (2014) — reconstructed what each layer responds to using a "deconvnet"</div>

</div>

<div class="flex flex-col gap-3">

<div v-click border="2 solid teal-800" bg="teal-800/20" rounded-lg p-3>
<div class="font-bold text-teal-300 mb-1">Emergence, not design</div>
<div class="text-sm opacity-90">This hierarchy was never specified by engineers. It falls out automatically from training on labeled images with backpropagation and gradient descent.</div>
</div>

<div v-click border="2 solid violet-800" bg="violet-800/20" rounded-lg p-3>
<div class="font-bold text-violet-300 mb-1">Reusable low-level features</div>
<div class="text-sm opacity-90">Edges and curves are useful for recognizing cats, cars, and buildings alike — the reason pretrained CNNs transfer well to new tasks.</div>
</div>

<div v-click border="2 solid amber-800" bg="amber-800/20" rounded-lg p-3>
<div class="font-bold text-amber-300 mb-1">Receptive field grows with depth</div>
<div class="text-sm opacity-90">A single 3×3 kernel only sees a 3×3 patch, but stacking layers lets deeper units respond to much larger regions of the original input.</div>
</div>

</div>

</div>

<!--
Name the source explicitly: Zeiler and Fergus, "Visualizing and Understanding Convolutional Networks," 2014. They built a "deconvnet" — a mechanism to run activations from a given layer backward through approximate inverse operations (unpooling, un-ReLU, and transposed convolution) and reconstruct which pixels in the original image caused a given unit to activate strongly. Doing this layer by layer across a trained network revealed a clean progressive hierarchy: layer 1 units respond to simple oriented edges and color contrasts (visually similar to classical Gabor filters), layer 2–3 units respond to textures, corners, and simple curves built by combining edge responses, layer 4–5 units respond to recognizable object parts such as eyes, wheels, or fur texture, and the deepest layers respond to whole objects in their typical context. This paper, along with AlexNet the year before, was pivotal in convincing the field that CNNs were not just accurate but interpretable — you could literally see what a layer had learned.

Explain the mechanism behind the hierarchy, not just the empirical result: a layer-1 unit's receptive field is exactly the kernel size (e.g. 3×3 pixels of the raw input). A layer-2 unit that itself uses a 3×3 kernel over layer-1's feature maps indirectly "sees" a larger patch of the original image, because each of those 9 inputs was already a summary of a 3×3 patch one layer back. Stack enough layers and the receptive field of a deep unit can cover the entire image, which is exactly what lets deep units respond to whole objects rather than small textures.

Common misconception to flag directly: students often confuse kernel size with receptive field. A 3×3 kernel does NOT mean a deep layer only ever sees a 3×3 patch of the original image — receptive field grows with network depth, even though every individual kernel stays small. Also worth noting: because reusable low-level features (edges, curves) generalize across very different object categories, pretrained CNN weights transfer well to new tasks — this is the basis of transfer learning, covered later in the course.

Next: before assembling the full architecture, we need one more building block — max pooling, which shrinks the spatial size of feature maps and adds a bit of robustness to small shifts.
-->

---
glowSeed: 518
---

# Max Pooling — A Worked Example

<div class="text-sm opacity-80 mb-2">Divide into 2×2 regions; keep only the maximum from each — no weights to learn</div>

<div class="grid grid-cols-3 gap-4 items-center">

<div border="2 solid blue-800" bg="blue-800/20" rounded-lg p-2>
<div class="font-bold text-blue-300 mb-1 text-sm">Input (4×4)</div>
<svg viewBox="0 0 140 140" class="w-full max-w-[9rem] mx-auto" role="img" aria-label="4 by 4 grid of numbers divided into four 2 by 2 quadrants, with the maximum of each quadrant circled">
  <rect x="10" y="10" width="60" height="60" fill="#2dd4bf" fill-opacity="0.12"/>
  <rect x="70" y="10" width="60" height="60" fill="#60a5fa" fill-opacity="0.12"/>
  <rect x="10" y="70" width="60" height="60" fill="#fbbf24" fill-opacity="0.12"/>
  <rect x="70" y="70" width="60" height="60" fill="#c084fc" fill-opacity="0.12"/>
  <g stroke="#475569" stroke-width="1" fill="none">
    <rect x="10" y="10" width="120" height="120"/>
    <line x1="40" y1="10" x2="40" y2="130"/><line x1="70" y1="10" x2="70" y2="130"/><line x1="100" y1="10" x2="100" y2="130"/>
    <line x1="10" y1="40" x2="130" y2="40"/><line x1="10" y1="70" x2="130" y2="70"/><line x1="10" y1="100" x2="130" y2="100"/>
  </g>
  <g fill="#94a3b8" style="font-size:14px" text-anchor="middle" font-family="monospace">
    <text x="25" y="30">1</text><text x="55" y="30">3</text><text x="85" y="30">2</text><text x="115" y="30">4</text>
    <text x="25" y="60">5</text><text x="85" y="60">1</text><text x="115" y="60">2</text>
    <text x="55" y="90">1</text><text x="115" y="90">3</text>
    <text x="25" y="120">2</text><text x="55" y="120">2</text><text x="85" y="120">1</text><text x="115" y="120">0</text>
  </g>
  <g fill="#e2e8f0" style="font-size:14px;font-weight:700" text-anchor="middle" font-family="monospace">
    <text x="55" y="60">6</text><text x="115" y="30">4</text><text x="25" y="90">3</text><text x="85" y="90">4</text>
  </g>
  <g fill="none" stroke="#f8fafc" stroke-width="2">
    <circle cx="55" cy="55" r="11"/><circle cx="115" cy="25" r="11"/><circle cx="25" cy="85" r="11"/><circle cx="85" cy="85" r="11"/>
  </g>
</svg>
</div>

<div v-click border="2 solid amber-800" bg="amber-800/20" rounded-lg p-2 style="font-size:.8em">
<div class="font-bold text-amber-300 mb-1 text-sm">2×2 max pool, stride 2</div>
<div class="opacity-90">Top-left: {1,3,5,6} → <strong>6</strong></div>
<div class="opacity-90">Top-right: {2,4,1,2} → <strong>4</strong></div>
<div class="opacity-90">Bottom-left: {2,2,1,3} → <strong>3</strong></div>
<div class="opacity-90">Bottom-right: {1,0,4,3} → <strong>4</strong></div>
</div>

<div v-click border="2 solid teal-800" bg="teal-800/20" rounded-lg p-2>
<div class="font-bold text-teal-300 mb-1 text-sm">Output (2×2)</div>
<div class="text-center font-mono text-xl font-bold text-teal-300 leading-tight">
<div>6&nbsp;&nbsp;4</div>
<div>3&nbsp;&nbsp;4</div>
</div>
</div>

</div>

<div class="grid grid-cols-3 gap-4 mt-3">
<div v-click border="2 solid violet-800" bg="violet-800/20" rounded-lg p-2 style="font-size:.85em">
<div class="font-bold text-violet-300 mb-1 text-sm">Downsampling</div>
<div class="opacity-90">16 values become 4 — a 4× reduction in compute and memory downstream.</div>
</div>
<div v-click border="2 solid violet-800" bg="violet-800/20" rounded-lg p-2 style="font-size:.85em">
<div class="font-bold text-violet-300 mb-1 text-sm">Local translation invariance</div>
<div class="opacity-90">A small shift of the strongest activation within a 2×2 window still gives the same max.</div>
</div>
<div v-click border="2 solid violet-800" bg="violet-800/20" rounded-lg p-2 style="font-size:.85em">
<div class="font-bold text-violet-300 mb-1 text-sm">Growing abstraction</div>
<div class="opacity-90">Each pooled unit now summarizes a larger patch, enlarging the effective receptive field.</div>
</div>
</div>

<!--
Walk the numbers exactly as displayed. The 4×4 input is split into four non-overlapping 2×2 windows (top-left, top-right, bottom-left, bottom-right — matching the four quadrant colors in the SVG). Top-left window contains {1,3,5,6}; its maximum is 6. Top-right window contains {2,4,1,2}; its maximum is 4. Bottom-left window contains {2,2,1,3}; its maximum is 3. Bottom-right window contains {1,0,4,3}; its maximum is 4. Collecting these four maxima into a 2×2 grid in the same spatial arrangement gives the output [[6,4],[3,4]]. Stride 2 here means the window jumps by 2 each time, so windows never overlap — this is the standard configuration for max pooling.

Three distinct benefits, and it's worth having students name all three rather than just "it shrinks the image." (1) Downsampling: going from 16 numbers to 4 is a 4× reduction, and every convolution and pooling layer applied afterward now operates on a smaller tensor, directly cutting compute and memory cost through the rest of the network. (2) Local translation invariance: if the "6" in the top-left window had instead been at a different position within that same 2×2 window, the max would still be 6 — small shifts in exactly where a feature activated don't change the pooled output, adding robustness on top of the translation invariance convolution already provides. (3) Increasing abstraction / receptive field: because pooling merges a small neighborhood into one value, a unit downstream of a pooling layer effectively "sees" a larger patch of the original input than a unit at the same depth without pooling — this compounds with the receptive-field growth from stacking conv layers, discussed on the previous slide.

Common misconception: max pooling has zero learnable parameters — it is a fixed, deterministic operation, not a trainable layer. Students sometimes assume every layer in a CNN has weights; pooling is the counterexample.

Next: assemble convolution, ReLU, and pooling into the standard repeating block, and see how a complete CNN architecture goes from raw pixels to a class prediction.
-->

---
glowSeed: 519
---

# The Full CNN Architecture

<div class="text-sm opacity-80 mb-2 text-center">Raw pixels in, class probabilities out</div>

<div class="text-center text-lg my-2 text-teal-300 font-mono">
Input → [Conv + ReLU + Pool] × n → Flatten → FC → Softmax
</div>

<div class="grid grid-cols-2 gap-6 items-start mt-4">

<div class="flex flex-col gap-2">
<v-clicks>

<div border="2 solid teal-800" bg="teal-800/20" rounded-lg px-4 py-2 class="text-sm">
<strong>Input:</strong> 32×32×3 image (height × width × RGB channels)
</div>
<div border="2 solid teal-800" bg="teal-800/20" rounded-lg px-4 py-2 class="text-sm">
<strong>Block 1:</strong> Conv(16 filters, 3×3) + ReLU → 32×32×16, then 2×2 MaxPool → 16×16×16
</div>
<div border="2 solid teal-800" bg="teal-800/20" rounded-lg px-4 py-2 class="text-sm">
<strong>Block 2:</strong> Conv(32 filters, 3×3) + ReLU → 16×16×32, then 2×2 MaxPool → 8×8×32
</div>
<div border="2 solid teal-800" bg="teal-800/20" rounded-lg px-4 py-2 class="text-sm">
<strong>Block 3:</strong> Conv(64 filters, 3×3) + ReLU → 8×8×64, then 2×2 MaxPool → 4×4×64
</div>
<div border="2 solid blue-800" bg="blue-800/20" rounded-lg px-4 py-2 class="text-sm">
<strong>Flatten:</strong> 4×4×64 → vector of 1,024 values
</div>
<div border="2 solid blue-800" bg="blue-800/20" rounded-lg px-4 py-2 class="text-sm">
<strong>Dense(128) + ReLU → Dense(10) + Softmax</strong> — probability over 10 classes
</div>

</v-clicks>
</div>

<div>
<svg viewBox="0 0 300 260" class="w-full max-w-sm mx-auto" role="img" aria-label="Diagram of a small CNN: an input cube shrinking in width and height but growing in depth through three convolution and pooling blocks, then flattening into a vector and two dense layers ending in a softmax output">
  <g font-family="monospace" style="font-size:9px" fill="#94a3b8" text-anchor="middle">
    <rect x="10" y="60" width="34" height="110" fill="#2dd4bf" fill-opacity="0.3" stroke="#2dd4bf"/>
    <text x="27" y="185">32×32×3</text>

    <rect x="60" y="70" width="28" height="90" fill="#60a5fa" fill-opacity="0.3" stroke="#60a5fa"/>
    <text x="74" y="185">16×16×16</text>

    <rect x="105" y="80" width="22" height="70" fill="#fbbf24" fill-opacity="0.3" stroke="#fbbf24"/>
    <text x="116" y="185">8×8×32</text>

    <rect x="145" y="95" width="16" height="45" fill="#f472b6" fill-opacity="0.3" stroke="#f472b6"/>
    <text x="153" y="185">4×4×64</text>

    <line x1="170" y1="115" x2="195" y2="115" stroke="#94a3b8" stroke-width="2" marker-end="url(#arrArch)"/>
    <defs><marker id="arrArch" markerWidth="8" markerHeight="8" refX="5" refY="2.5" orient="auto"><path d="M0,0 L5,2.5 L0,5 Z" fill="#94a3b8"/></marker></defs>

    <rect x="200" y="60" width="10" height="110" fill="#c084fc" fill-opacity="0.35" stroke="#c084fc"/>
    <text x="205" y="185">flat 1024</text>

    <rect x="225" y="90" width="10" height="50" fill="#34d399" fill-opacity="0.35" stroke="#34d399"/>
    <text x="230" y="185">FC 128</text>

    <rect x="248" y="100" width="10" height="30" fill="#fb923c" fill-opacity="0.35" stroke="#fb923c"/>
    <text x="253" y="185">FC 10</text>

    <rect x="270" y="108" width="10" height="14" fill="#e2e8f0" fill-opacity="0.5" stroke="#e2e8f0"/>
    <text x="275" y="185">softmax</text>
  </g>
  <text x="150" y="20" fill="#cbd5e1" style="font-size:12px" text-anchor="middle">spatial size shrinks, channel depth grows</text>
</svg>
</div>

</div>

<!--
Walk the diagram block by block, tracing the tensor's shape at every stage — this is the habit students need for reading any CNN architecture. Start with a 32×32×3 input image. Block 1 applies 16 filters of size 3×3 (each spanning all 3 input channels), producing a 32×32×16 feature map — spatial size unchanged because of zero-padding, channel depth now 16 because there are 16 independent filters. ReLU is applied elementwise immediately after the convolution, zeroing out every negative activation — this nonlinearity is what lets the network represent non-linear decision boundaries; without it, stacking conv layers would collapse into one big linear operation. Then 2×2 max pooling with stride 2 halves the spatial dimensions to 16×16, leaving channels at 16. Block 2 and Block 3 repeat this pattern — convolution increases channel depth (16→32→64) while pooling keeps shrinking height and width (16×16→8×8→4×4). After three blocks the tensor is 4×4×64. Flatten reshapes this 3D tensor into a single vector by concatenating all values: 4×4×64 = 1,024. That vector feeds a dense layer of 128 units with ReLU, then a final dense layer of 10 units (one per class in this example), followed by softmax, which converts the 10 raw scores into a probability distribution that sums to 1.

Common misconception to flag explicitly: ReLU is applied after every single convolution, not just once at the end of the network — students sometimes forget it belongs inside each conv block rather than being a single global step. Also flag: "flatten" happens once, near the end, after most of the spatial processing is already done — flattening at the very start (as a plain dense network would) is exactly the mistake CNNs are designed to avoid.

For scale, mention VGG16 (Simonyan & Zisserman, 2014) as a real reference point: 13 convolutional layers plus 3 fully-connected layers, totaling about 138 million parameters — still less than the 150 million a single naive dense layer needed on raw pixels in our opening slide, despite VGG16 being a genuinely deep, high-performing network.

Next: let's close the loop and map every one of the four problems from the opening slide to the specific mechanism that solves it.
-->

---
glowSeed: 520
---

# Recap — Every Problem, Solved by a Named Mechanism

<div class="text-sm opacity-80 mb-4 text-center">Each CNN design choice traces directly back to a failure of dense networks</div>

<div class="grid grid-cols-2 gap-4">

<div v-click border="2 solid red-800" bg="red-800/20" rounded-lg p-4>
<div class="font-bold text-red-300 mb-1">Problem: parameter explosion</div>
<div class="text-sm opacity-80 mb-2">150,528,000 weights for one dense layer</div>
<div class="text-sm">→ solved by <strong class="text-teal-300">weight sharing</strong>: 896 parameters for a 32-filter conv layer, reused at every position</div>
</div>

<div v-click border="2 solid red-800" bg="red-800/20" rounded-lg p-4>
<div class="font-bold text-red-300 mb-1">Problem: no spatial structure</div>
<div class="text-sm opacity-80 mb-2">Flattening destroys pixel neighborhoods</div>
<div class="text-sm">→ solved by <strong class="text-teal-300">local receptive fields</strong>: each kernel only ever looks at a small spatial patch</div>
</div>

<div v-click border="2 solid red-800" bg="red-800/20" rounded-lg p-4>
<div class="font-bold text-red-300 mb-1">Problem: no translation invariance</div>
<div class="text-sm opacity-80 mb-2">A shifted cat looks like an unrelated pattern</div>
<div class="text-sm">→ solved by <strong class="text-teal-300">shift-equivariant convolution + pooling</strong>: the same filter fires wherever the pattern appears</div>
</div>

<div v-click border="2 solid red-800" bg="red-800/20" rounded-lg p-4>
<div class="font-bold text-red-300 mb-1">Problem: data hunger</div>
<div class="text-sm opacity-80 mb-2">Millions of free parameters need proportionally more labeled data</div>
<div class="text-sm">→ solved by <strong class="text-teal-300">far fewer parameters</strong>: dramatically less data required to fit the same model reliably</div>
</div>

</div>

<div v-click class="mt-6 text-center text-lg opacity-90">
CNNs are not just more accurate on images — they are structurally matched to what images are.
</div>

<!--
Walk this table as a direct callback to the opening problem slide, closing the loop the lecture opened with. Parameter explosion (150,528,000 weights for one dense layer) is solved by weight sharing: the same 3×3×3 kernel, reused at every spatial position, needs only 9×3+1 = 28 parameters per filter — 896 total across 32 filters, independent of image size. No spatial structure (flattening treats pixel (1,1) and (224,224) as unrelated) is solved by local receptive fields: a convolutional unit only ever reads a small spatial neighborhood of its input, so locality is built into the architecture rather than something the network must discover from data. No translation invariance (a shifted cat needs to be relearned) is solved by the combination of convolution's shift-equivariance — sliding the same filter means a shifted input produces a correspondingly shifted output, not an unrelated one — and max pooling's added local invariance, which further blurs out exactly where within a small window a feature fired. Data hunger follows automatically once parameter count drops by roughly five orders of magnitude: far fewer parameters means far less training data is needed to fit them without overfitting.

Emphasize the throughline for the whole lecture in one sentence: every one of these fixes traces back to a single idea — reusing a small set of local weights across every spatial position, instead of learning an independent weight for every (pixel, unit) pair. That's convolution.

This is a natural stopping point for questions. Next lecture in this unit moves to techniques that make deep CNN training more reliable — batch normalization and dropout — and later units cover transfer learning, where the reusable low-level features from this lecture's Zeiler & Fergus discussion get reused directly on new tasks.
-->

---
layout: center
class: text-center
glowSeed: 229
---

# Thank You

### Questions &amp; Discussion

<div class="pt-6 opacity-80">
Convolutional Neural Networks · Neural Networks and Deep Learning Basics
</div>

<!--
Take questions before moving to the next lecture in this unit — batch normalization and dropout for more reliable deep training. Encourage students to try computing a conv layer's parameter count by hand for a different configuration (e.g. 64 filters, 5×5, on a 64-channel input) as a self-check that the 3×3×3×32+32 formula generalizes.
-->
