---
theme: default
highlighter: shiki
css: unocss
colorSchema: dark
title: 'Dimensionality Reduction: PCA, t-SNE, and UMAP'
info: |
  ## Dimensionality Reduction: PCA, t-SNE, and UMAP
  Fewer numbers per point, same structure
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
glowSeed: 740
---

# Dimensionality Reduction {.!text-5xl}

### PCA, t-SNE and UMAP: fewer numbers per point, same structure

<div class="mt-3">
<HeroMorph />
</div>

<div class="opacity-80 text-lg mt-2">Unsupervised Learning · Foundations of Machine Learning</div>

<!--
Every dot here is a handwritten digit: an 8 by 8 image, so 64 numbers. We've turned each one into just 2 numbers, a position on the slide. The color is the true label, which none of the methods ever saw.

The picture cycles through three ways of choosing those 2 numbers. PCA: a straight-on shadow of the 64-dimensional cloud; the classes overlap. Then t-SNE and UMAP: nonlinear maps that pull each digit's neighbors together, and the ten classes separate almost completely. You can click a method to jump to it.

Today is about how each of these works, what each one keeps and throws away, and how not to be fooled by the pretty pictures.

Every number on these slides comes from scripts/make_data.py in the deck folder, run with fixed seeds.
-->

---
glowSeed: 741
clicks: 2
---

# Where Gaussian Mixtures Left Off

<PlaneFit :step="$clicks" />

<div class="reveal text-sm mt-1" :class="{ shown: $clicks >= 2 }" border="2 solid teal-800" bg="teal-800/20" rounded-lg px-4 py-2>
Three numbers per point, but PC1 and PC2 hold <b>99.7%</b> of the variance. Two coordinates lose almost nothing.
</div>

<!--
This is the teaser from the end of the Gaussian Mixtures deck: the same 500 points we ran EM on, lifted into 3D. Three numbers per point. Rotate it, and you'll see they all sit close to one tilted plane.

[click] PCA finds that plane on its own. The amber and violet axes span it; the red one, PC3, points out of the plane and is tiny, because the points barely move in that direction. The arrows are two standard deviations long.

[click] So describe each point by its position on the plane: its coordinate along PC1 and along PC2. That's the 2D picture on the right, and it's the same three clusters we clustered last time. PC1 holds 71% of the variance, PC2 another 28.5%, PC3 only 0.3%. Two numbers per point instead of three, and we've lost almost nothing.

That's dimensionality reduction: find a few coordinates that capture the structure, drop the rest. Today we'll do it with 64 numbers per point instead of 3, and for curved structure that no plane can capture.
-->

---
glowSeed: 742
clicks: 5
---

# Today

<div class="grid grid-cols-2 gap-x-6 gap-y-3 mt-4 text-left">
<div border="2 solid teal-800" bg="teal-800/20" rounded-lg px-4 py-3>
<div class="font-bold text-teal-300">1 · Why fewer dimensions</div>
<div class="text-sm opacity-85 mt-1">Images as vectors, intrinsic dimension, the curse of dimensionality.</div>
</div>
<div class="reveal" :class="{ shown: $clicks >= 1 }" border="2 solid amber-800" bg="amber-800/20" rounded-lg px-4 py-3>
<div class="font-bold text-amber-300">2 · PCA: the best flat view</div>
<div class="text-sm opacity-85 mt-1">Max variance = min error = top eigenvectors. Power iteration, SVD, scaling.</div>
</div>
<div class="reveal" :class="{ shown: $clicks >= 2 }" border="2 solid violet-800" bg="violet-800/20" rounded-lg px-4 py-3>
<div class="font-bold text-violet-300">3 · PCA on real images</div>
<div class="text-sm opacity-85 mt-1">Eigendigits, reconstruction, choosing k, denoising, speeding up a model.</div>
</div>
<div class="reveal" :class="{ shown: $clicks >= 3 }" border="2 solid blue-800" bg="blue-800/20" rounded-lg px-4 py-3>
<div class="font-bold text-blue-300">4 · When flat is not enough</div>
<div class="text-sm opacity-85 mt-1">Manifolds, the Swiss roll, and why only small neighborhoods can be trusted.</div>
</div>
<div class="reveal" :class="{ shown: $clicks >= 4 }" border="2 solid orange-800" bg="orange-800/20" rounded-lg px-4 py-3>
<div class="font-bold text-orange-300">5 · t-SNE</div>
<div class="text-sm opacity-85 mt-1">Neighbor probabilities, heavy tails, KL divergence, live, and its pitfalls.</div>
</div>
<div class="reveal" :class="{ shown: $clicks >= 5 }" border="2 solid red-800" bg="red-800/20" rounded-lg px-4 py-3>
<div class="font-bold text-red-300">6 · UMAP, and putting it together</div>
<div class="text-sm opacity-85 mt-1">Fuzzy graphs, two knobs, comparisons, a practical pipeline.</div>
</div>
</div>

<!--
Six parts.

First, why we'd want fewer dimensions at all: what it means for an image to be a point in 64 dimensions, and what goes wrong in high dimensions.
[click] Second, PCA, derived properly: the direction of most variance, why it's also the direction of least reconstruction error, and why it's an eigenvector. How it's computed, and one trap.
[click] Third, PCA on real images: what the components look like, rebuilding digits, choosing how many to keep, and two practical uses.
[click] Fourth, where PCA fails: data on curved surfaces, and the key idea for fixing it.
[click] Fifth, t-SNE, step by step, with a version running live in the browser, and the ways its pictures mislead.
[click] Sixth, UMAP, then all three methods side by side and how they fit into a real workflow.
-->

---
layout: center
class: text-center
glowSeed: 743
---

# Part 1 · Why Fewer Dimensions?

<div class="text-lg opacity-80 mt-3">Data often has many columns but few real degrees of freedom.</div>

<!--
Part one: what high-dimensional data looks like, and why we'd want to describe it with fewer numbers.
-->

---
glowSeed: 744
clicks: 1
---

# An Image Is a Vector

<DigitUnroll :step="$clicks" />

<div class="grid grid-cols-3 gap-4 mt-1 text-left text-sm">
<div border="2 solid white/5" bg="white/5" rounded-lg px-4 py-2><b class="text-teal-300">1797</b> scanned digits, 8 × 8 pixels each</div>
<div border="2 solid white/5" bg="white/5" rounded-lg px-4 py-2><b class="text-amber-300">64</b> features: one per pixel, ink from 0 to 16</div>
<div border="2 solid white/5" bg="white/5" rounded-lg px-4 py-2>Each image is <b class="text-violet-300">one point</b> in ℝ⁶⁴</div>
</div>

<!--
Our running dataset: scikit-learn's handwritten digits. 1797 images, each 8 by 8 pixels, each pixel an ink level from 0 to 16. Here's one of them, a 3. Hover over a pixel to see its value.

[click] A model doesn't see a picture; it sees a list of numbers. Read the pixels row by row and you get a vector of 64 numbers. So every image is a single point in a 64-dimensional space, and the whole dataset is a cloud of 1797 points in that space.

Hover the row: each slot is one feature. Feature 1 is the top-left pixel, feature 64 the bottom-right. Nearby pixels end up far apart in this list, and the list knows nothing about the 2D layout. Keep that in mind; it's why the structure of the cloud, not the individual columns, carries the meaning.

We can't look at a 64-dimensional cloud. Today's methods find a handful of coordinates that describe it.
-->

---
glowSeed: 745
---

# Most of ℝ⁶⁴ Is Not Digits

<RandomVsReal />

<div class="grid grid-cols-2 gap-4 mt-5 text-left text-sm">
<div border="2 solid teal-800" bg="teal-800/20" rounded-lg px-4 py-2>
<b>Intrinsic dimension</b>: real images vary along a few directions: stroke thickness, slant, which digit. They fill a thin sliver of the space.
</div>
<div border="2 solid amber-800" bg="amber-800/20" rounded-lg px-4 py-2>
On digits, PCA needs <b>5</b> directions for 50% of the variance, <b>21</b> for 90%, <b>29</b> for 95%: not 64.
</div>
</div>

<!--
Left: twelve real digits. Right: twelve random points of the same 64-dimensional space, every pixel drawn uniformly from 0 to 16. Press "draw again" as often as you like. You will never draw a digit.

That's the key fact behind this whole lecture. The space has 64 dimensions, but real digits occupy a tiny, highly structured part of it. They vary in a few meaningful ways: which digit it is, how thick the stroke, how slanted, how big. Neighboring pixels move together. That small number of real degrees of freedom is called the intrinsic dimension.

We'll measure it in Part 3: PCA needs only 5 directions to capture half the variance of the digits, 21 for 90%, 29 for 95%. Dimensionality reduction tries to find coordinates for that sliver.
-->

---
glowSeed: 746
---

# The Curse of Dimensionality

<CurseDims />

<!--
Why bother reducing? One reason: high-dimensional space behaves strangely, and distance-based methods suffer.

Left: 150 random points in the unit cube in d dimensions. I compute all 11,000 pairwise distances, divide by the average, and histogram them. At d = 2 the histogram is wide: some pairs are close, some far. Drag the slider up, or press sweep. By d = 100 the histogram is a spike at 1: every point is about the same distance from every other point. The readout is the gap between the farthest pair and the nearest pair, relative to the nearest. It collapses toward zero.

That's bad news for k-means, k-nearest neighbors, DBSCAN: anything that relies on "near" versus "far". When all distances are about equal, "nearest" stops meaning much.

Right, a related fact: the ball that just fits inside the cube. In 2D it's 78.5% of the square. In 10 dimensions it's a quarter of a percent; in 20 it's 2.5 × 10⁻⁸. Almost all the volume of a high-dimensional cube is in its corners, far from the center. Our low-dimensional intuition is simply wrong there.

Real data is less extreme than random noise, because of the intrinsic-dimension point from the last slide. But reducing to the dimensions that matter is often what makes distance-based methods work.
-->

---
glowSeed: 747
clicks: 4
---

# Four Reasons to Reduce

<div class="grid grid-cols-2 gap-4 mt-6 text-left">
<div border="2 solid teal-800" bg="teal-800/20" rounded-lg p-4>
<div class="font-bold text-teal-300 mb-1">👁 Visualize</div>
<div class="text-sm opacity-90">We can see 2 or 3 dimensions. Map the data there and look for clusters, outliers, trends.</div>
</div>
<div class="reveal" :class="{ shown: $clicks >= 1 }" border="2 solid blue-800" bg="blue-800/20" rounded-lg p-4>
<div class="font-bold text-blue-300 mb-1">🧹 Denoise</div>
<div class="text-sm opacity-90">Noise spreads over all directions; signal concentrates in a few. Keep those, drop the rest.</div>
</div>
<div class="reveal" :class="{ shown: $clicks >= 2 }" border="2 solid amber-800" bg="amber-800/20" rounded-lg p-4>
<div class="font-bold text-amber-300 mb-1">⚡ Accelerate</div>
<div class="text-sm opacity-90">Fewer features: faster training and neighbor search, fewer parameters to overfit.</div>
</div>
<div class="reveal" :class="{ shown: $clicks >= 3 }" border="2 solid violet-800" bg="violet-800/20" rounded-lg p-4>
<div class="font-bold text-violet-300 mb-1">🗜 Compress</div>
<div class="text-sm opacity-90">Store k numbers per item instead of d, and rebuild an approximation when needed.</div>
</div>
</div>

<div class="reveal mt-5 text-sm" :class="{ shown: $clicks >= 4 }" border="2 solid white/10" bg="white/5" rounded-lg px-4 py-2>
Different goals, different methods: <b class="text-amber-300">PCA</b> does all four. <b class="text-violet-300">t-SNE</b> and <b class="text-violet-300">UMAP</b> are for the first one.
</div>

<!--
Four distinct reasons, and it's worth keeping them apart because they lead to different methods.

Visualize: a human can look at 2 or 3 dimensions. Anything more needs a map.
[click] Denoise: measurement noise spreads out over every direction, while real structure lives in a few directions. Keep the few, and you keep most of the signal and lose most of the noise. We'll see this on noisy digits.
[click] Accelerate: fewer columns means faster training and faster nearest-neighbor search, and fewer parameters for a downstream model to overfit.
[click] Compress: store k numbers per item instead of d, and reconstruct an approximation when you need it.

[click] PCA serves all four: it gives you a projection, an inverse to rebuild from it, and a way to apply it to new data. t-SNE and UMAP are built for the first goal, looking, and are risky for the others. Keep that in mind for the second half.
-->

---
layout: center
class: text-center
glowSeed: 748
---

# Part 2 · PCA: The Best Flat View

<div class="text-lg opacity-80 mt-3">Which direction should we look along?</div>

<!--
Part two: principal component analysis, built from one question: if you can keep only one number per point, which direction should you project onto?
-->

---
glowSeed: 749
---

# Projecting onto a Direction

<ProjectDrag />

<div class="text-sm mt-1" border="2 solid teal-800" bg="teal-800/20" rounded-lg px-4>

$$
z_i = \mathbf v^\top \mathbf x_i \;\;(\lVert\mathbf v\rVert = 1,\ \text{data centered}),\qquad \operatorname{Var}(z)=\frac1{n-1}\sum_i (\mathbf v^\top\mathbf x_i)^2=\mathbf v^\top\Sigma\,\mathbf v
$$

</div>

<!--
48 points, already centered so the mean is at the origin. The amber line is a direction v, a unit vector. Projecting a point onto it gives one number, z = vᵀx: where the point lands along the line. Those are the amber dots. The red segments are what that one number fails to describe: the residual.

The line is turning slowly. Watch the bar on the right: amber is the variance of the projected values, red is the variance lost in the residuals. Grab the plot and turn it yourself.

Along the cloud's short axis, the projections bunch up: tiny variance, big residuals. Along the long axis, they spread out: big variance, small residuals. The curves below show both as functions of the angle, and they are mirror images.

The formula in the card: the variance of the projections is vᵀΣv, where Σ is the covariance matrix of the data. Same Σ as last deck. PCA's first component is the v that maximizes it. Press "snap to PC1": the variance there is 2.17, the largest eigenvalue of Σ. Next two slides: why the red and amber trade off exactly, and why the answer is an eigenvector.
-->

---
glowSeed: 750
---

# Two Views, One Answer

<Pythagoras />

<div class="text-sm mt-2" border="2 solid teal-800" bg="teal-800/20" rounded-lg px-4>

$$
\underbrace{\sum_i \lVert\mathbf x_i\rVert^2}_{\text{fixed}} \;=\; \underbrace{\sum_i (\mathbf v^\top\mathbf x_i)^2}_{\text{kept: maximize}} \;+\; \underbrace{\sum_i \lVert\mathbf x_i - (\mathbf v^\top\mathbf x_i)\mathbf v\rVert^2}_{\text{lost: minimize}}
$$

</div>

<!--
Why the amber and red curves on the last slide were mirror images. It's Pythagoras.

Take one point x. Its projection onto the line, the residual, and x itself form a right triangle: the residual is perpendicular to the line. So the square on x, the dashed teal one, equals the amber square plus the red square. As the line turns, the two smaller squares trade area, but their total stays fixed, because x doesn't move.

Sum over all the points, divide by n − 1: total variance, which doesn't depend on v, equals the variance we keep plus the squared reconstruction error we lose.

So "find the direction with the most projected variance" and "find the line closest to the data in squared distance" are the same problem. That's the second definition of PCA you'll see in books, and it's why PCA is a compression method: it's the best possible linear reconstruction. It's also the link to autoencoders at the end of today.

One contrast worth making: this is not linear regression. Regression minimizes vertical distances to predict one variable from another. PCA minimizes perpendicular distances, and treats all the variables the same.
-->

---
glowSeed: 751
clicks: 3
---

# The Optimizer Is an Eigenvector

<div class="grid grid-cols-2 gap-8 items-center mt-4 text-left">
<div class="space-y-3">
<div border="2 solid white/5" bg="white/5" rounded-lg px-4 py-3>
<span class="font-bold text-teal-300">Constrain</span> <span class="text-sm opacity-85">— without ‖v‖ = 1, making v longer would make vᵀΣv as big as we like.</span>
</div>
<div class="reveal" :class="{ shown: $clicks >= 1 }" border="2 solid white/5" bg="white/5" rounded-lg px-4 py-3>
<span class="font-bold text-blue-300">Set the gradient to zero</span> <span class="text-sm opacity-85">— ∇(vᵀΣv) = 2Σv, ∇(vᵀv) = 2v.</span>
</div>
<div class="reveal" :class="{ shown: $clicks >= 2 }" border="2 solid white/5" bg="white/5" rounded-lg px-4 py-3>
<span class="font-bold text-amber-300">Evaluate</span> <span class="text-sm opacity-85">— at an eigenvector, the variance is its eigenvalue. Take the largest.</span>
</div>
<div class="reveal" :class="{ shown: $clicks >= 3 }" border="2 solid white/5" bg="white/5" rounded-lg px-4 py-3>
<span class="font-bold text-violet-300">Repeat</span> <span class="text-sm opacity-85">— best direction orthogonal to v₁ is v₂, and so on: the eigenvectors in order of λ.</span>
</div>
</div>
<div class="space-y-3">
<div border="2 solid teal-800" bg="teal-800/20" rounded-lg px-4>

$$
\max_{\mathbf v}\ \mathbf v^\top\Sigma\mathbf v \quad\text{s.t.}\quad \mathbf v^\top\mathbf v=1
$$

</div>
<div class="reveal" :class="{ shown: $clicks >= 1 }" border="2 solid blue-800" bg="blue-800/20" rounded-lg px-4>

$$
\mathcal L=\mathbf v^\top\Sigma\mathbf v-\lambda(\mathbf v^\top\mathbf v-1)\;\Rightarrow\;\Sigma\mathbf v=\lambda\mathbf v
$$

</div>
<div class="reveal" :class="{ shown: $clicks >= 2 }" border="2 solid amber-800" bg="amber-800/20" rounded-lg px-4>

$$
\mathbf v^\top\Sigma\mathbf v=\mathbf v^\top(\lambda\mathbf v)=\lambda
$$

</div>
<div class="reveal" :class="{ shown: $clicks >= 3 }" border="2 solid violet-800" bg="violet-800/20" rounded-lg px-4>

$$
\Sigma = Q\Lambda Q^\top,\quad \lambda_1\ge\lambda_2\ge\dots\ge\lambda_d\ge 0
$$

</div>
</div>
</div>

<!--
Now the algebra. We want the unit vector v that maximizes vᵀΣv. The constraint matters: vᵀΣv is quadratic in v, so without it we'd just make v longer forever. We want a direction, not a length.

[click] Constrained optimization, so a Lagrange multiplier, from the calculus lecture. The Lagrangian is vᵀΣv − λ(vᵀv − 1). The gradient of vᵀΣv is 2Σv because Σ is symmetric; the gradient of vᵀv is 2v. Set the gradient to zero, divide by 2: Σv = λv. That's the eigenvector equation. The best direction must be an eigenvector of the covariance matrix. Not an analogy: it falls straight out.

[click] Which eigenvector? Plug the condition back into the objective: vᵀΣv = vᵀ(λv) = λ, because v has length 1. The variance along an eigenvector is its eigenvalue. So take the eigenvector with the largest eigenvalue. That's PC1, and λ₁ is the variance it captures.

[click] For PC2, maximize again, now also requiring v to be orthogonal to v₁; the answer is the eigenvector with the second-largest eigenvalue, and so on. Σ is symmetric, so by the spectral theorem it has d orthogonal eigenvectors and real eigenvalues, and since it's a covariance they're all non-negative. PCA is the eigendecomposition of Σ, sorted by eigenvalue. Next slide: what that equation looks like.
-->

---
glowSeed: 752
---

# Seeing Σv = λv

<EigenDrag />

<!--
Same covariance matrix as the projection slide. The teal arrow is a unit vector v; drag it around the circle. The amber arrow is Σv, what the matrix does to it.

Generally Σv points somewhere else: Σ stretches and turns. The faint arrows show what Σ does to 24 unit vectors around the circle, and the dashed ellipse is where the whole circle goes. Look at the pattern: Σ pulls every direction toward the long axis.

Now drag v until it lines up with Σv: the panel lights up. That happens in exactly two directions, plus their opposites: along the ellipse's long axis and short axis. Those are the eigenvectors, and the stretch factor there is the eigenvalue: 2.17 along the long axis, 0.22 along the short one.

Also watch the readout vᵀΣv: it's the projected variance from two slides ago. It's largest exactly at the long-axis eigenvector, smallest at the short one. Everything we derived, in one picture: the ellipse of the data is the ellipse of Σ, its axes are the eigenvectors, and the variance along each axis is the eigenvalue. The covariance ellipses of last deck's Gaussians were exactly this.
-->

---
glowSeed: 753
---

# Finding v₁: Power Iteration

<PowerIter />

<div class="text-sm mt-2" border="2 solid teal-800" bg="teal-800/20" rounded-lg px-4>

$$
\mathbf v \leftarrow \frac{\Sigma\mathbf v}{\lVert\Sigma\mathbf v\rVert}\qquad\text{error shrinks by about } \lambda_2/\lambda_1 \text{ per step}
$$

</div>

<!--
How do you actually compute an eigenvector? We just saw that Σ pulls every direction toward the long axis. So apply it again and again.

Power iteration: start with any v, multiply by Σ, rescale to length 1, repeat. Write v as a mix of the eigenvectors. Multiplying by Σ multiplies the v₁ part by λ₁ and the v₂ part by λ₂. After many steps the ratio of the two parts has been multiplied by (λ₂/λ₁) to the power of the number of steps, so the v₁ part wins.

The plot starts almost perpendicular to v₁, a bad start on purpose. With close eigenvalues, ratio 0.85, the arrow creeps over; the error on the right falls in a straight line on the log scale, a factor 0.85 per step. Click "our cloud": ratio 0.10, and it's done in about three steps.

This is the core idea of the iterative solvers inside numerical libraries, and of Google's original PageRank. It also shows when PCA's answer is unstable: if two eigenvalues are nearly equal, the data is nearly round in that plane, and the direction of the top component is barely determined.
-->

---
glowSeed: 754
clicks: 4
---

# PCA Is a Change of Basis

<PcaSteps :step="$clicks" />

<div class="grid grid-cols-4 gap-3 text-xs text-left mt-1">
<div class="reveal" :class="{ shown: $clicks >= 1 }" border="2 solid white/5" bg="white/5" rounded-lg px-3 py-2><b class="text-teal-300">1 · Center</b><br>subtract the mean μ</div>
<div class="reveal" :class="{ shown: $clicks >= 2 }" border="2 solid white/5" bg="white/5" rounded-lg px-3 py-2><b class="text-blue-300">2 · Rotate</b><br>Z = (X − μ)Q: eigenvectors become the axes</div>
<div class="reveal" :class="{ shown: $clicks >= 3 }" border="2 solid white/5" bg="white/5" rounded-lg px-3 py-2><b class="text-amber-300">3 · Truncate</b><br>keep the first k columns of Z</div>
<div class="reveal" :class="{ shown: $clicks >= 4 }" border="2 solid white/5" bg="white/5" rounded-lg px-3 py-2><b class="text-red-300">4 · Reconstruct</b><br>X̂ = μ + Z_k Q_kᵀ, error = dropped variance</div>
</div>

<!--
The whole algorithm, as motion. Raw data, somewhere off in feature space. The amber and violet lines are its principal axes, through its mean.

[click] Step one, center: subtract the mean. The cloud slides to the origin. PCA describes spread around the mean, not location.

[click] Step two, rotate. Multiply by Q, the matrix whose columns are the eigenvectors. That's a rotation, so no distances change. Now PC1 is the horizontal axis and PC2 the vertical. The new coordinates, Z, are called the scores. Notice the cloud is no longer tilted: in the new coordinates the features are uncorrelated, the covariance of Z is diagonal, with the eigenvalues on the diagonal.

[click] Step three, the actual reduction: keep only the first k columns of Z. Here k = 1, so every point drops onto the PC1 axis. Each point is now one number.

[click] Step four, go back: rotate the 1D scores back to the original axes and add the mean. That's the reconstruction X̂. The red segments are the errors, and their mean squared length is the sum of the eigenvalues we dropped. In sklearn, these steps are fit, transform, and inverse_transform.
-->

---
glowSeed: 755
clicks: 3
---

# Worked Example: PCA by Hand

<div class="grid grid-cols-[1fr_1.1fr] gap-6 items-center mt-1">
<div>
<WorkedPlot :step="$clicks" />
<div class="text-xs opacity-60 text-center">10 points (Smith, 2002) · hover a point</div>
</div>
<div class="space-y-3 text-left text-sm">
<div border="2 solid white/5" bg="white/5" rounded-lg px-4 py-2>

Mean $\bar{\mathbf x}=(1.81,\ 1.91)$, so center first.

</div>
<div class="reveal" :class="{ shown: $clicks >= 1 }" border="2 solid teal-800" bg="teal-800/20" rounded-lg px-4>

$$
\Sigma=\begin{bmatrix}0.617&0.615\\0.615&0.717\end{bmatrix}
$$

</div>
<div class="reveal" :class="{ shown: $clicks >= 2 }" border="2 solid amber-800" bg="amber-800/20" rounded-lg px-4>

$$
\det(\Sigma-\lambda I)=0\ \Rightarrow\ \lambda_1=1.284,\ \lambda_2=0.049,\quad \mathbf v_1=(0.678,\ 0.735)
$$

</div>
<div class="reveal" :class="{ shown: $clicks >= 3 }" border="2 solid white/5" bg="white/5" rounded-lg px-4 py-2>

PC1 keeps $\lambda_1/(\lambda_1+\lambda_2)=$ **96.3%** of the variance. Each point's score: $z_i=\mathbf v_1^\top(\mathbf x_i-\bar{\mathbf x})$.

</div>
</div>
</div>

<!--
Ten points, small enough to do by hand; this example is from Lindsay Smith's PCA tutorial, and the numbers are recomputed in make_data.py.

Step zero: the mean is (1.81, 1.91); subtract it.

[click] The covariance matrix. The off-diagonal, 0.615, is almost as big as the diagonal entries: the two features are strongly correlated. On the plot: the mean, and the 1- and 2-standard-deviation ellipses of Σ, a thin tilted cigar.

[click] Eigenvalues from the 2 by 2 characteristic equation: λ² − 1.334λ + 0.064 = 0, giving 1.284 and 0.049. The top eigenvector is (0.678, 0.735), roughly the 45-degree diagonal. Those are the amber and violet axes on the plot, each drawn 2 standard deviations, 2√λ, from the mean.

[click] The share of variance on PC1: 1.284 over 1.333, 96.3%. Project each centered point onto v₁ to get its score: the amber dots on the line. Hover a point to see it. Dropping the second coordinate loses only 3.7% of the variance: the red segments are short.
-->

---
glowSeed: 756
---

# The SVD Route, and What sklearn Does

<SvdBlocks />

<div class="grid grid-cols-2 gap-4 mt-3 text-left text-sm">
<div border="2 solid teal-800" bg="teal-800/20" rounded-lg px-4 style="font-size: .9em">

$$
\begin{aligned}X_c&=UDV^\top\\ \Sigma=\tfrac{1}{n-1}X_c^\top X_c&=V\,\tfrac{D^2}{n-1}\,V^\top,\quad \lambda_j=\tfrac{d_j^2}{n-1}\end{aligned}
$$

</div>
<div border="2 solid white/5" bg="white/5" rounded-lg px-4 py-2>
<code>svd_solver="auto"</code>: tall data (n ≥ 10d, d ≤ 1000, like digits) → form Σ and eigendecompose it (<code>covariance_eigh</code>). Otherwise → SVD of X_c, full or randomized.
</div>
</div>

<!--
A second route to the same answer: the singular value decomposition. Any matrix factors as U D Vᵀ: U and V have orthonormal columns, D is diagonal with the singular values, largest first.

Substitute into the covariance formula: XᵀX = V D Uᵀ U D Vᵀ = V D² Vᵀ, since UᵀU is the identity. Compare with Σ = QΛQᵀ: same thing. So the rows of Vᵀ are the principal directions, and each eigenvalue is a squared singular value over n − 1. And U D, the first factors, are exactly the scores Z.

The slider: keep the first k columns of U, values of D and rows of Vᵀ, and multiply back. That's the best rank-k approximation of the data matrix in squared error, the Eckart–Young theorem, and it's the same thing as PCA with k components. On digits, k = 3 already keeps 40% of the variance.

What does scikit-learn actually do? It depends on the shape. For tall, narrow data, at least ten times as many rows as columns and at most a thousand columns, it forms the small d by d covariance matrix and eigendecomposes it; I checked: on digits, sklearn 1.9 picks this "covariance_eigh" solver. Otherwise it takes the SVD of the centered data directly, which is more accurate because it never squares the numbers, and for big data with few components it uses a randomized SVD. Same answer either way, up to the sign of each component.
-->

---
glowSeed: 757
clicks: 1
---

# Scale Before PCA

<WineScale :std="$clicks >= 1" />

<div class="text-sm mt-1" border="2 solid amber-800" bg="amber-800/20" rounded-lg px-4 py-2>
{{ $clicks >= 1 ? 'Standardized: every feature has variance 1, so PC1 mixes many of them, and the three cultivars separate.' : 'Raw: proline varies in the hundreds, hue in tenths. PC1 is just proline, and calls it 99.8% of the variance.' }}
</div>

<!--
One trap. The wine dataset: 178 wines, 13 chemical measurements, 3 grape cultivars, the colors, which PCA never sees.

On the raw numbers, PC1 is all proline: weight 1.00, everything else zero. And it "explains" 99.8% of the variance. Why? Look at the standard deviations next to the feature names: proline is measured in the hundreds, sd 315; hue has sd 0.23. Variance depends on units. PCA chases whatever has the biggest numbers. Measuring proline in different units would give a completely different PC1.

[click] Standardize first, every feature to mean 0 and variance 1, and run PCA again. Now PC1 has substantial weights on many features, flavanoids, phenols, OD280, and explains 36%. That's a much smaller number, and much more meaningful: it's a combination of chemistry, not an artifact of units. And on the left, the three cultivars now separate along PC1.

The rule: if your features are in different units, standardize before PCA. If they share a unit and their sizes are comparable on purpose, like pixel intensities, you may leave them raw. That's why we don't scale the digits.
-->

---
layout: center
class: text-center
glowSeed: 758
---

# Part 3 · PCA on Real Images

<div class="text-lg opacity-80 mt-3">64 pixels, 1797 digits: what do the components look like?</div>

<!--
Part three: PCA on the digits. Now each principal component is a direction in 64-dimensional pixel space, which means each one is itself an 8 by 8 image.
-->

---
glowSeed: 759
---

# Eigendigits

<Eigendigits />

<!--
Each principal direction has 64 entries, one per pixel, so we can draw it as an image. Teal pixels have positive weight, violet negative.

Top left, the mean digit: a blurry average of all 1797. Below, the first ten components, with the share of variance each explains: 14.9%, 13.6%, 11.8%, and decreasing.

They don't look like digits; they're contrasts. Look at PC1: positive in some regions, negative in others. A digit gets a high PC1 score if its ink lands on the teal parts and not the violet parts.

The big panel is the best way to read a component. It shows the mean plus c times the component, with c sweeping between −2 and +2 standard deviations. Hover over different components. Moving along a component morphs the average digit in one specific way: watch which strokes appear at one end and fade at the other, and ask which digits that pulls toward. Each component is a "direction of variation" among digits. The later components describe finer and finer details.
-->

---
glowSeed: 760
---

# Rebuilding a Digit

<Rebuild />

<div class="text-sm mt-2" border="2 solid teal-800" bg="teal-800/20" rounded-lg px-4>

$$
\hat{\mathbf x}=\boldsymbol\mu+\sum_{j=1}^{k} z_j\,\mathbf v_j,\qquad z_j=\mathbf v_j^\top(\mathbf x-\boldsymbol\mu)
$$

</div>

<!--
Any digit can be rebuilt as the mean plus a weighted sum of components. The weights, the z's, are its PCA scores, and they're just dot products.

The strip shows the sum: the mean digit, plus z₁ times PC1, plus z₂ times PC2, and so on, with this digit's actual coefficients. Press "build": we add one component at a time. At k = 0 it's just the mean. By 5 or so the digit is recognizable; by 20 it's sharp. The bars are the size of every coefficient: the early ones are big and the late ones small, which is why truncating loses little.

Click the other digits on top to switch. The readouts: the share of variance kept by k components, over all digits; and this digit's own error. At k = 64 the error is zero: with all 64 components it's just a rotation, nothing is lost.

So a digit can be stored as, say, 20 numbers instead of 64, plus the shared mean and components. That's PCA as compression.
-->

---
glowSeed: 761
---

# How Many Components?

<ScreeLinked />

<!--
The practical question: how many components to keep. The scree plot answers it.

The orange bars: each component's share of the variance, in decreasing order by construction. The teal line: the running total. Move the mouse across the chart to choose k, and the row of digits below shows eight digits rebuilt from that many components.

The dashed lines mark common targets: 80% of the variance at k = 13, 90% at 21, 95% at 29. That's what PCA(n_components=0.95) does: it picks the smallest k whose cumulative share reaches 95%.

Notice there's no sharp elbow here; real data rarely has one. So how to choose? It depends on the goal. For plotting, k is 2 or 3, whatever it explains. For compression or denoising, look at the reconstructions and the downstream error, as on the next slides. For a model, treat k as a hyperparameter and pick it by cross-validation. The cumulative-variance rule is a reasonable default, not a law.
-->

---
glowSeed: 762
---

# The Digits on Two Components

<div class="grid grid-cols-[auto_1fr] gap-6 items-center">
<DigitMap by="pca" />
<div class="text-left space-y-3 text-sm">
<div border="2 solid white/5" bg="white/5" rounded-lg px-4 py-3>
PC1 + PC2 hold only <b class="text-amber-300">28.5%</b> of the variance.
</div>
<div border="2 solid white/5" bg="white/5" rounded-lg px-4 py-3>
0, 4, 6 and 2 sit apart; <b>1, 5, 8, 9</b> pile up in the middle.
</div>
<div border="2 solid white/5" bg="white/5" rounded-lg px-4 py-3>
Hover a point to see its image. Hover a digit in the legend to pick out its class.
</div>
</div>
</div>

<!--
All 1797 digits, placed by their first two PCA scores, colored by the true label, which PCA didn't use.

It's the best two-dimensional shadow in the variance sense, and it shows real structure: zeros on one side, fours and sixes elsewhere, twos and threes in their own areas. But the middle is a pile-up of 1s, 5s, 8s and 9s. That's not because those digits are similar in 64 dimensions; it's because two directions hold only 28.5% of the variance, and a straight projection squashes the rest on top of each other.

Hover over points in the overlap to see what's there. Hover the legend to isolate one class; look at how spread out the 1s are.

Keep this picture in mind. In Part 5, t-SNE and UMAP will produce maps where these classes separate cleanly, from the same 64 numbers.
-->

---
glowSeed: 763
---

# PCA Denoises

<Denoise />

<div class="text-sm mt-3" border="2 solid teal-800" bg="teal-800/20" rounded-lg px-4 py-2>
Signal lives in the first components; noise is spread evenly over all 64. Keeping k ≈ 21 cuts the error from <b>9.3</b> to <b>5.6</b>.
</div>

<!--
Denoising, measured. PCA was fit on clean training digits. Then I took 300 held-out digits and added random noise to every pixel, standard deviation 4 on a 0-to-16 scale. Top row clean, middle row noisy.

The bottom row: each noisy digit projected onto the first k components and mapped back. Drag the slider. The curve on the right is the error against the clean digits, averaged over all 300, for every k.

At k = 0 every digit becomes the mean: error 19, worse than the noisy input. As k grows, the digits come back and the error drops below the noise level, the red dashed line. It bottoms out at k = 21, error 5.6, down from 9.3. Then it rises again, and at k = 64 it's exactly the noisy input: projecting on every direction keeps everything, including the noise.

Why it works: real digits live near a low-dimensional subspace, so their signal is in the top components. Noise is spread evenly in all 64 directions. Keeping 21 directions keeps nearly all the signal but only about a third of the noise. And the U-shape is the bias–variance trade-off again: too few components, bias; too many, noise.
-->

---
glowSeed: 764
---

# PCA Before a Classifier

<div class="grid grid-cols-[auto_1fr] gap-6 items-center mt-2">
<ClfCurve />
<div class="text-left space-y-3 text-sm">
<div border="2 solid white/5" bg="white/5" rounded-lg px-4 py-3>
<code>StandardScaler → PCA(k) → LogisticRegression</code>, 5-fold CV on digits.
</div>
<div border="2 solid teal-800" bg="teal-800/20" rounded-lg px-4 py-3>
k = 2: <b>53%</b>. k = 15: <b>89%</b>. k = 30: <b>91%</b>. All 64: <b>92%</b>.
</div>
<div border="2 solid amber-800" bg="amber-800/20" rounded-lg px-4 py-3>
PCA ignores the labels: the directions of most variance need not be the directions that separate the classes.
</div>
</div>
</div>

<!--
PCA as a preprocessing step for a supervised model. The pipeline: standardize, reduce to k components, logistic regression. Five-fold cross-validated accuracy on digits as a function of k; hover for exact numbers.

Two components give 53%: much better than the 10% of guessing, but the overlap we saw two slides ago costs a lot. Fifteen components already reach 89%, and thirty get within a point of using all 64.

On a dataset this small the speed-up hardly matters. On a dataset with thousands of features it can matter a great deal, and fewer inputs can also mean less overfitting.

The amber card is the caveat. PCA is unsupervised: it finds directions of large variance, not directions that predict the label. A small-variance direction can be the one that separates the classes, and PCA will throw it away first. So treat k as a hyperparameter and tune it by cross-validation, inside the pipeline.
-->

---
glowSeed: 765
---

# PCA in scikit-learn

<div class="grid grid-cols-[1.25fr_1fr] gap-6 items-start mt-2">

```python
from sklearn.decomposition import PCA

pca = PCA(n_components=0.95)          # keep 95% of variance
Z_train = pca.fit_transform(X_train)  # learn μ and directions
Z_test = pca.transform(X_test)        # reuse them: no leakage

pca.n_components_                # 29 on digits
pca.explained_variance_ratio_    # the scree plot
pca.components_                  # rows: eigendigits
X_back = pca.inverse_transform(Z_test)  # μ + Z Qₖᵀ
```

<div class="space-y-3 text-left text-sm">
<div border="2 solid white/5" bg="white/5" rounded-lg px-4 py-3>
<b class="text-teal-300">Integer or fraction</b>: <code>n_components=10</code> keeps 10; <code>0.95</code> keeps enough for 95%.
</div>
<div border="2 solid white/5" bg="white/5" rounded-lg px-4 py-3>
<b class="text-amber-300">Fit on training data only</b>: in a <code>Pipeline</code>, cross-validation refits PCA inside each fold.
</div>
<div border="2 solid white/5" bg="white/5" rounded-lg px-4 py-3>
<b class="text-violet-300">Different units?</b> Put a <code>StandardScaler</code> in front.
</div>
</div>
</div>

<!--
The API. n_components can be an integer, the number to keep, or a fraction, the share of variance to keep; 0.95 keeps 29 components on digits.

fit learns the mean and the directions from the training data; transform projects onto them. Use the same fitted PCA on the test set. Fitting PCA on all the data before splitting is leakage, exactly like fitting a scaler on everything: the test set would have shaped the directions. In practice, put it in a Pipeline so cross-validation refits it inside each fold.

The attributes: explained_variance_ratio_ is the scree plot. components_ holds the directions as rows: on digits, these are the eigendigits we drew. inverse_transform maps scores back to feature space, the reconstruction.

And from the wine slide: if features are in different units, standardize first.
-->

---
layout: center
class: text-center
glowSeed: 766
---

# Part 4 · When Flat Is Not Enough

<div class="text-lg opacity-80 mt-3">Data can be low-dimensional and still not lie near any plane.</div>

<!--
Part four. PCA finds the best flat subspace. But low-dimensional structure doesn't have to be flat.
-->

---
glowSeed: 767
clicks: 2
---

# The Swiss Roll

<SwissRoll :view="$clicks === 0 ? null : $clicks === 1 ? 'pca' : 'truth'" />

<div class="reveal text-sm mt-1" :class="{ shown: $clicks >= 2 }" border="2 solid teal-800" bg="teal-800/20" rounded-lg px-4 py-2>
A <b>manifold</b>: a surface that is 2D up close, curled up in 3D. Its natural coordinates are not any linear projection.
</div>

<!--
The classic example: the Swiss roll. 900 points on a sheet of paper that's been rolled up in 3D. The color is the position along the sheet, from the inside of the roll to the outside. The data is 3D, but it's intrinsically 2D: two numbers, how far along the sheet and how high up, describe each point.

[click] PCA's best flat view. It looks at the roll from the side, and the layers land on top of each other: the violet inner layer overlaps the amber and red outer layers. Points that are far apart on the sheet end up next to each other. No linear projection can fix this; whichever way you look, some layers overlap.

[click] What we'd like instead: unroll the sheet. That's the true 2D structure, with colors in order. A surface like this, flat up close but curved overall, is called a manifold. Nonlinear dimensionality reduction tries to find these unrolled coordinates.
-->

---
glowSeed: 768
---

# Straight Lines Cut Through Empty Space

<SpiralGeo />

<!--
The problem in one picture. A spiral: a one-dimensional curve in 2D. The color shows distance along the curve from the amber point.

The circle captures every point within a straight-line radius. Small radius: everything inside is a genuine neighbor, teal, near along the curve too. Drag the radius up. At some point the circle reaches the next arm, and red points appear: close in a straight line, but far along the curve. The dashed line is the closest such point: from the starting source, the straight-line distance is 0.71, but the distance along the curve is 8.7, twelve times as far.

Click anywhere to move the source; the same thing happens everywhere.

So straight-line distance is trustworthy only at short range. For close points, it agrees with distance along the manifold. For far points, it cuts through empty space and lies. PCA uses all distances, so it's fooled. The nonlinear methods use only the small ones.
-->

---
glowSeed: 769
---

# Trust Only Small Neighborhoods

<KnnGraph />

<!--
The fix shared by all the nonlinear methods: keep only local distances, as a graph. Connect each point to its k nearest neighbors.

With k = 6 the graph follows the spiral: a chain. Distances through the graph, hopping along edges, approximate distances along the curve. That's exactly the idea of Isomap, an early method: compute shortest paths through this graph, then find a layout that preserves them.

Press play to grow k. At k = 1 the graph is 74 separate pieces, at k = 2 still 15; from k = 3 it's one connected chain. From k = 11 the first red edges appear: short circuits between arms. By k = 20 there are about a hundred, and a path can jump straight across: the graph has lost the shape.

Keep this picture. t-SNE's perplexity and UMAP's n_neighbors are this same k: how big a neighborhood to trust. Both build something like this graph, then look for a 2D layout that keeps graph neighbors close.
-->

---
layout: center
class: text-center
glowSeed: 770
---

# Part 5 · t-SNE

<div class="text-lg opacity-80 mt-3">t-distributed Stochastic Neighbor Embedding (van der Maaten & Hinton, 2008)</div>

<!--
Part five: t-SNE, the method that made nonlinear maps of high-dimensional data a standard tool. The name is a mouthful: t-distributed stochastic neighbor embedding. We'll take it in three steps.
-->

---
glowSeed: 771
---

# t-SNE in One Picture

<TsneIdea />

<div class="grid grid-cols-3 gap-3 mt-3 text-left text-sm">
<div border="2 solid teal-800" bg="teal-800/20" rounded-lg px-3 py-2><b class="text-teal-300">1 · pᵢⱼ</b>: how strongly i and j are neighbors in the data (Gaussian)</div>
<div border="2 solid amber-800" bg="amber-800/20" rounded-lg px-3 py-2><b class="text-amber-300">2 · qᵢⱼ</b>: the same, between their positions in the 2D map (Student-t)</div>
<div border="2 solid violet-800" bg="violet-800/20" rounded-lg px-3 py-2><b class="text-violet-300">3 · Move the map</b> points until q matches p (KL divergence)</div>
</div>

<!--
The whole idea before the details. Left: points in the original space, with links between neighbors; thicker means closer. Those link strengths are p_ij.

Right: the 2D map. We start with the points in random positions, and compute the same kind of link strengths between their map positions, q_ij. Red links are stretched: the two points are neighbors in the data but far apart in the map. Then we move the map points, by gradient descent, until the links match, and the colors go teal.

Notice what is not in the picture: there's no formula from x to its map position. t-SNE doesn't learn a function; it just optimizes the 1797 or so positions directly. That will matter later.

Three ingredients, one per slide: how p is defined, how q is defined, and how we measure the mismatch.
-->

---
glowSeed: 772
---

# Step 1: Neighbor Probabilities

<Affinity />

<div class="text-sm mt-1" border="2 solid teal-800" bg="teal-800/20" rounded-lg px-4>

$$
p_{j\mid i}=\frac{\exp(-\lVert\mathbf x_i-\mathbf x_j\rVert^2/2\sigma_i^2)}{\sum_{k\ne i}\exp(-\lVert\mathbf x_i-\mathbf x_k\rVert^2/2\sigma_i^2)},\qquad 2^{H(P_i)}=\text{perplexity},\qquad p_{ij}=\frac{p_{j\mid i}+p_{i\mid j}}{2n}
$$

</div>

<!--
Step one. For each point i, put a Gaussian around it and turn distances into probabilities: p_{j|i} is the probability that i would pick j as its neighbor. Closer points get more probability. On the plot, each point's size and brightness is its probability.

The key question is the width σᵢ of each Gaussian, and the answer is: different for every point. Click a point in the tight cluster on the left: the rings, σ and 2σ, are small. Now click one in the diffuse cluster on the right: much bigger. t-SNE picks each σᵢ by bisection so that the distribution has a fixed perplexity, which is 2 to the entropy. Think of it as the effective number of neighbors. Same perplexity, same number of effective neighbors, whether the region is dense or sparse.

Drag the perplexity slider: more effective neighbors, bigger σ. Typical values are 5 to 50; the default is 30. The readout shows 2^H matching the slider.

Finally, symmetrize: average p_{j|i} and p_{i|j}, divide by 2n, so the p_ij's add to 1 over all pairs.

A consequence to remember: because σ adapts to density, t-SNE throws away information about density. A tight cluster and a loose one look alike after this step.
-->

---
glowSeed: 773
---

# Step 2: A Heavy-Tailed Map

<HeavyTails />

<div class="grid grid-cols-[1.2fr_1fr] gap-4 mt-2 text-left text-sm">
<div border="2 solid violet-800" bg="violet-800/20" rounded-lg px-4>

$$
q_{ij}=\frac{(1+\lVert\mathbf y_i-\mathbf y_j\rVert^2)^{-1}}{\sum_{k\ne l}(1+\lVert\mathbf y_k-\mathbf y_l\rVert^2)^{-1}}
$$

</div>
<div border="2 solid white/5" bg="white/5" rounded-lg px-4 py-2>
<b>Crowding problem</b>: in 64-D a point can have many equidistant neighbors; in 2D there isn't room. Heavy tails let moderately distant points move further out.
</div>
</div>

<!--
Step two: similarities in the map. Same idea, a kernel of the distance between map points y_i and y_j, but a different kernel: Student-t with one degree of freedom, 1 over 1 plus distance squared. That's the "t" in t-SNE.

Why not a Gaussian again? The crowding problem. In 64 dimensions a point can have dozens of neighbors all at about the same distance; we saw distances concentrate. In 2D there's no room to place dozens of points all at the same distance from a center. Something has to give.

The plot shows the fix. Teal: the Gaussian of the original space. Violet: the Student-t of the map. Drag the amber marker along the distance axis. For a pair at that distance in the original space, the horizontal line finds the map distance with the same similarity. For close pairs, the two distances are about equal: local structure is kept. For moderately distant pairs, the t-curve needs a much larger distance: at 1.5 it's about twice as far, at 2 almost four times. So pairs that are moderately far apart get pushed further apart in the map. That relieves the crowding, and it's why t-SNE clusters come out with clear gaps between them.
-->

---
glowSeed: 774
clicks: 2
---

# Step 3: Match with KL Divergence

<div class="grid grid-cols-2 gap-8 items-start mt-4 text-left">
<div class="space-y-3">
<div border="2 solid teal-800" bg="teal-800/20" rounded-lg px-4>

$$
C=\mathrm{KL}(P\,\Vert\,Q)=\sum_{i\ne j}p_{ij}\log\frac{p_{ij}}{q_{ij}}
$$

</div>
<div class="reveal" :class="{ shown: $clicks >= 2 }" border="2 solid violet-800" bg="violet-800/20" rounded-lg px-4>

$$
\frac{\partial C}{\partial\mathbf y_i}=4\sum_j\underbrace{(p_{ij}-q_{ij})}_{\text{spring}}\frac{\mathbf y_i-\mathbf y_j}{1+\lVert\mathbf y_i-\mathbf y_j\rVert^2}
$$

</div>
</div>
<div class="space-y-3">
<table class="kl reveal" :class="{ shown: $clicks >= 1 }">
<thead><tr><th>in the data</th><th>in the map</th><th>cost</th></tr></thead>
<tbody>
<tr><td>neighbors (p large)</td><td>far (q small)</td><td class="text-red-300 font-bold">large</td></tr>
<tr><td>far (p small)</td><td>close (q large)</td><td class="text-teal-300 font-bold">small</td></tr>
</tbody>
</table>
<div class="reveal text-sm" :class="{ shown: $clicks >= 1 }" border="2 solid white/5" bg="white/5" rounded-lg px-4 py-2>
Tearing neighbors apart is punished; putting strangers together is barely noticed. t-SNE keeps <b>local</b> structure, not global.
</div>
<div class="reveal text-sm" :class="{ shown: $clicks >= 2 }" border="2 solid white/5" bg="white/5" rounded-lg px-4 py-2>
Gradient descent with momentum, and <b>early exaggeration</b> (p × 12 for the first 250 steps) so clusters form first.
</div>
</div>
</div>

<style>
.kl { width: 100%; border-collapse: separate; border-spacing: 0 4px; font-size: 0.85rem; }
.kl th { font-size: 0.72rem; text-transform: uppercase; letter-spacing: 0.05em; opacity: 0.6; text-align: left; padding: 2px 8px; }
.kl td { background: rgba(255, 255, 255, 0.05); padding: 8px; }
</style>

<!--
Step three: measure how badly the map's q's match the data's p's, and minimize it. The measure is the Kullback–Leibler divergence of P from Q, the sum of p log p over q. It's zero when they match exactly.

[click] KL is asymmetric, and that asymmetry is the whole personality of t-SNE. If two points are neighbors in the data, p large, and the map puts them far apart, q small, the log ratio is big and it's weighted by the big p: a large cost. If two points are far apart in the data, p tiny, and the map puts them close, the term is weighted by that tiny p: almost no cost. So t-SNE works hard to keep neighbors together and hardly cares where non-neighbors end up. It preserves local structure, not global structure. Distances between clusters in a t-SNE map are not reliable.

[click] The gradient has a nice physical reading: each pair is connected by a spring whose strength is p − q. If the map has them too far apart, q < p, the spring pulls them together; too close, it pushes them apart. Minimize with gradient descent and momentum. One trick: early exaggeration. For the first 250 iterations, multiply all p's by 12, so the attractions dominate and clusters form tight and early, with room to move around each other. Let's watch it.
-->

---
glowSeed: 775
---

# Watch t-SNE Run

<TsneLive />

<!--
This is t-SNE running live, in the browser, on 400 of the digits: the exact algorithm from the last three slides, about 100 lines of code. It's the same as the Python version in make_data.py, which ends at almost the same KL as scikit-learn's.

The points start in a tiny random blob. During early exaggeration, the amber part of the progress bar, clusters form quickly and pull tight. After iteration 250 the exaggeration switches off and the map relaxes and spreads out, and the KL divergence keeps falling.

Things to try: hover points to see the digits; notice the odd ones sitting in the wrong cluster are often genuinely ambiguous handwriting. Press restart: a different random start gives a differently arranged map, with the same clusters. Then try perplexity 5: more fragmented, many small clumps. Perplexity 100: rounder and more connected.

The next slide does the same on all 1797 digits, precomputed.
-->

---
glowSeed: 776
---

# Perplexity and Seeds Change the Picture

<PerplexityMorph />

<!--
All 1797 digits, t-SNE at six perplexities. Every map is aligned to the perplexity-30 map, so switching morphs the points rather than spinning everything.

Perplexity 2: each point considers only its two closest neighbors. The map shatters into many small fragments: lots of fake sub-clusters. 5 and 15: clean clusters, still with some internal splitting. 30, the default: ten clean clusters. 100: the clusters get rounder and start pulling toward each other, as each point now considers a hundred neighbors.

Then the three seeds, all at perplexity 30 from different random starting positions. The same clusters, with the same digits in them, but their arrangement on the page changes: which cluster is next to which, and where. That's the KL asymmetry again: the cost barely cares where non-neighbors go, so the global layout is partly arbitrary.

So: never trust a single t-SNE run. Try a few perplexities and seeds; believe what stays the same.
-->

---
glowSeed: 777
clicks: 1
---

# How Not to Read a t-SNE Plot

<div class="grid grid-cols-3 gap-3 mt-1">
<div class="text-center">
<Pitfall which="size" :emb="$clicks >= 1" />
<div class="text-sm font-bold text-teal-300 mt-1">Cluster sizes mean nothing</div>
<div class="text-xs opacity-75">sd 1 vs sd 10: drawn the same size</div>
</div>
<div class="text-center">
<Pitfall which="gap" :emb="$clicks >= 1" />
<div class="text-sm font-bold text-amber-300 mt-1">Gaps may mean nothing</div>
<div class="text-xs opacity-75">gaps of 10 and 50: drawn about equal</div>
</div>
<div class="text-center">
<Pitfall which="noise" :emb="$clicks >= 1" />
<div class="text-sm font-bold text-red-300 mt-1">Noise can look clumpy</div>
<div class="text-xs opacity-75">pure 30-D noise, perplexity 3</div>
</div>
</div>

<div class="text-center text-sm font-mono mt-2">{{ $clicks >= 1 ? 't-SNE maps' : 'the original data' }}</div>

<div class="text-sm mt-2" border="2 solid white/5" bg="white/5" rounded-lg px-4 py-2>
After Wattenberg, Viégas & Johnson, <i>How to Use t-SNE Effectively</i> (Distill, 2016). Use t-SNE to look and form hypotheses; confirm in the original space.
</div>

<!--
Three ways to misread t-SNE, from the excellent Distill article by Wattenberg, Viégas and Johnson. Each panel shows the original data first.

Left: two clusters, one tight, standard deviation 1, and one ten times more spread out. Middle: three tight clusters along a line, with a gap of 10 between the first two and 50 between the second two. Right: 300 points of pure Gaussian noise in 30 dimensions; I'm showing the first two coordinates. No structure at all.

[click] Now t-SNE. Left: the two clusters come out about the same size. That's the adaptive σ from step one: density is normalized away. Middle: the big gap and the small gap come out roughly the same. The cost doesn't care about far-apart pairs, so distances between clusters aren't preserved. Right: at low perplexity, pure noise breaks into little clumps of a few points: apparent structure that isn't there. With real data, small clumps at low perplexity can be exactly this.

The lesson: t-SNE is a tool for looking and forming hypotheses. Size, density and distance between clusters in the map are not evidence. Check anything interesting in the original data or with PCA.
-->

---
layout: center
class: text-center
glowSeed: 778
---

# Part 6 · UMAP

<div class="text-lg opacity-80 mt-3">Uniform Manifold Approximation and Projection (McInnes, Healy & Melville, 2018)</div>

<!--
Part six: UMAP. Same goal as t-SNE: a 2D map that keeps neighbors together. Different construction, rooted in topology, but we'll stick to what it does: build a weighted graph, then lay it out. It's usually faster, keeps somewhat more global structure, and can place new points.
-->

---
glowSeed: 779
---

# UMAP Step 1: A Fuzzy Neighbor Graph

<FuzzyGraph />

<div class="text-sm mt-1" border="2 solid teal-800" bg="teal-800/20" rounded-lg px-4>

$$
w_{j\mid i}=\exp\!\Big(-\frac{d(\mathbf x_i,\mathbf x_j)-\rho_i}{\sigma_i}\Big)\ \ (j\text{ among the }k\text{ nearest}),\qquad w_{ij}=w_{j\mid i}+w_{i\mid j}-w_{j\mid i}\,w_{i\mid j}
$$

</div>

<!--
Step one: a weighted k-nearest-neighbor graph, like Part 4's, with two twists.

For each point i, find its k nearest neighbors. ρᵢ is the distance to the very nearest one. Each neighbor gets weight exp of minus (distance − ρ) over σ. Subtracting ρ means every point's nearest neighbor gets weight exactly 1, however sparse its region: every point is connected to something. Hover a point to see its ρ, the dashed ring, and its own edges. σᵢ plays the same role as in t-SNE: it's chosen per point so the weights add up to log₂ k, adapting to the local density.

The two directions, i to j and j to i, can disagree. UMAP combines them as a fuzzy union, a + b − ab: the probability that at least one of the two edges exists.

The slider is n_neighbors, the k. Small: a sparse chain that follows the spiral. Larger: more edges, a smoother graph that reaches further, eventually across arms. It's the same trade-off as before: local detail versus global connectivity.
-->

---
glowSeed: 780
---

# UMAP Step 2: Lay Out the Graph

<div class="grid grid-cols-[auto_1fr] gap-6 items-center">
<UmapEpochs />
<div class="text-left space-y-3 text-sm">
<div border="2 solid white/5" bg="white/5" rounded-lg px-4 py-3>
<b class="text-teal-300">Start</b>: a spectral layout of the graph, not random.
</div>
<div border="2 solid white/5" bg="white/5" rounded-lg px-4 py-3>
<b class="text-amber-300">Attract</b> along edges; <b class="text-red-300">repel</b> a few random non-neighbors (negative sampling).
</div>
<div style="font-size: .8em" border="2 solid violet-800" bg="violet-800/20" rounded-lg px-3>

$$
\sum_{ij} w_{ij}\log\frac{w_{ij}}{v_{ij}}+(1-w_{ij})\log\frac{1-w_{ij}}{1-v_{ij}}
$$

</div>
<div class="text-xs opacity-75">v<sub>ij</sub> = (1 + a‖yᵢ − yⱼ‖<sup>2b</sup>)⁻¹, with a, b set by <code>min_dist</code>.</div>
</div>
</div>

<!--
Step two: find a 2D layout whose own fuzzy graph matches the first one.

The cost is a cross-entropy, in the purple card. The first term is like t-SNE's: an edge with weight w in the data but a weak link v in the map costs a lot, so neighbors attract. The second term is what t-SNE lacks: if a pair has weight near 0 in the data but the map puts them close, so v is large, that's penalized too. Non-neighbors repel. That's one reason UMAP tends to keep more of the global arrangement.

The map similarity v is a heavy-tailed curve like t-SNE's, with a shape set by min_dist.

Two practical differences. UMAP starts from a spectral layout, a smart initial arrangement computed from the graph, rather than random noise; that's "start" in the animation. And instead of computing every pairwise repulsion, it samples a few random non-neighbors per step. That's why it scales to millions of points.

The animation: the digits after 0, 5, 15, 40, 100 and 200 epochs of optimization. The spectral start already has the coarse layout; the epochs tighten the clusters.
-->

---
glowSeed: 781
---

# UMAP's Two Knobs

<UmapKnobs />

<!--
UMAP's two main hyperparameters, on the digits. 16 precomputed maps, all aligned, so switching morphs.

n_neighbors, the k of the graph. 5: very local, clusters break into pieces and their relative positions are arbitrary. 15 is the default. 50, 200: each point considers a much larger neighborhood; clusters become smoother and the overall arrangement reflects more global structure, at the cost of fine detail.

min_dist: how tightly points may pack in the map. It doesn't change the graph at all, only the layout. 0: points collapse into dense clumps, good for clustering. 0.99: points spread evenly, good for seeing the internal structure of a cluster.

Same lesson as with perplexity: try a few settings. Features that survive every setting are real.
-->

---
glowSeed: 782
---

# The Swiss Roll, Three Ways

<SwissThree />

<div class="text-sm mt-3" border="2 solid white/5" bg="white/5" rounded-lg px-4 py-2>
<b>Trustworthiness</b>: are each point's 10 nearest neighbors in the map also near it in the original space? 1 = all of them.
</div>

<!--
Back to the Swiss roll, through all three methods. Same coloring: position along the roll.

PCA: the side view. Layers overlap; colors mixed.

t-SNE: neighbors are kept, so locally the colors are smooth. But the sheet may come out torn into pieces, folded, or with its ends rearranged: the global shape isn't something t-SNE tries to preserve.

UMAP: also keeps neighbors, and often keeps more of the sheet's continuity.

Hover a point in one map and it's ringed in all three, so you can see where the same piece of the roll ends up.

The number under each is trustworthiness: for each point, are its 10 nearest neighbors in the map really near it in 3D? PCA scores 0.90: the overlap brings strangers together. t-SNE and UMAP both score 0.999. That's the measure they're good at. Note what it doesn't measure: whether the global shape is right.
-->

---
glowSeed: 783
---

# Same Digits, Three Maps

<LinkedMaps />

<div class="text-sm mt-3" border="2 solid white/5" bg="white/5" rounded-lg px-4 py-2>
Hover any point: the same digit is ringed in all three maps. Trust = trustworthiness with 10 neighbors.
</div>

<!--
The full digits through all three. Hover over any point in any map: the same digit gets a ring in all three, and its image pops up.

PCA: overlapping classes, trustworthiness 0.83. t-SNE: ten clean islands, 0.993. UMAP: ten islands, tighter and with more space between them, 0.988. Try hovering in PCA's crowded middle and watch where those points land in the other two: they're scattered among different, well-separated clusters.

Hover some points sitting in the "wrong" cluster in t-SNE or UMAP: they're usually badly written digits, a 9 that really does look like a 3.

Fit times from my run: PCA, a fraction of a millisecond. t-SNE about a second; UMAP a few seconds here, with its one-time compilation; on big datasets UMAP is usually much faster than t-SNE. And remember: PCA's axes mean something, variance directions you can inspect. In t-SNE and UMAP, the x and y axes mean nothing at all.
-->

---
glowSeed: 784
---

# A Practical Pipeline

<PipelineFlow />

<div class="text-xs text-center opacity-70 mt-1">Adjusted Rand index between 10 clusters and the true digits (1 = perfect, 0 = chance)</div>

<!--
How these fit together in practice.

Start with the raw features. Run PCA first, often down to about 50 components or a fixed share of the variance: here, 29 components for 95%. That removes noise and makes everything after it faster. Then two separate branches.

To look: run t-SNE or UMAP on the PCA scores and make a picture.
To group: cluster, but on the PCA scores, not the 2D map. Then go back and color the map by your clusters to check them visually.

The bars: how well 10-cluster k-means matches the true digits on different representations, by adjusted Rand index. Raw 64-D: 0.67. Two PCA components: 0.39, the overlap hurts. 29 PCA components: 0.67, same as raw, with half the features. A GMM on those 29: 0.71.

And k-means on the t-SNE map gets 0.89, UMAP 0.83. Tempting! It's done on digits sometimes, and with UMAP it's a known workflow. But be careful: the map distorts densities and distances, it depends on perplexity and seed, and t-SNE can't place new points. If you cluster on a map, check that the clusters are stable across settings and that they mean something in the original data.
-->

---
glowSeed: 785
---

# t-SNE and UMAP in Code

<div class="grid grid-cols-[1.3fr_1fr] gap-6 items-start mt-2">

```python
from sklearn.decomposition import PCA
from sklearn.manifold import TSNE
import umap                                # pip install umap-learn

pca = PCA(n_components=50).fit(X_train)
Z = pca.transform(X_train)                 # denoise and speed up first

E = TSNE(perplexity=30, init="pca",
         random_state=0).fit_transform(Z)  # no .transform() for new data

reducer = umap.UMAP(n_neighbors=15, min_dist=0.1, random_state=0)
E = reducer.fit_transform(Z)
E_new = reducer.transform(pca.transform(X_new))  # UMAP can embed new points
```

<div class="space-y-3 text-left text-sm">
<div border="2 solid white/5" bg="white/5" rounded-lg px-4 py-3>
<b class="text-teal-300">init="pca"</b> (the default now): a more stable, more global starting layout than random.
</div>
<div border="2 solid white/5" bg="white/5" rounded-lg px-4 py-3>
<b class="text-amber-300">Fix random_state</b> to reproduce a map, then <b>vary</b> it to see what is stable.
</div>
<div border="2 solid white/5" bg="white/5" rounded-lg px-4 py-3>
<b class="text-violet-300">Scale</b>: t-SNE uses Barnes–Hut, O(n log n); UMAP handles millions.
</div>
</div>
</div>

<!--
The code. Reduce with PCA first, to around 50 components; both methods are faster and often cleaner on the PCA scores than on raw features.

t-SNE in scikit-learn. Perplexity 30 is the default. init="pca" starts from the PCA layout instead of random noise, which gives more stable maps and keeps more global structure; it's the default in recent versions. Note there's no transform method: t-SNE optimizes positions for the points it was given and has no function to apply to new points. To add points you rerun the whole thing.

UMAP lives in its own package, umap-learn, with a scikit-learn-style API. n_neighbors and min_dist, defaults 15 and 0.1. Unlike t-SNE it has a transform method: new points are placed into the existing map, using their neighbors among the training points.

Both are random: fix random_state to reproduce a figure, and vary it to see what's stable. For scale: sklearn's t-SNE uses the Barnes–Hut approximation, n log n per iteration, fine for tens of thousands of points; UMAP routinely handles millions.
-->

---
glowSeed: 786
---

# Choosing a Method

<table class="choose">
<thead><tr><th /><th>Map</th><th>Keeps</th><th>New points</th><th>Axes mean</th><th>Repeatable</th><th>Use it to</th></tr></thead>
<tbody>
<tr class="hl"><td class="text-amber-300">PCA</td><td>linear</td><td>global variance</td><td>yes, exact</td><td>variance directions</td><td>yes</td><td>compress, denoise, preprocess, a first look</td></tr>
<tr><td class="text-violet-300">t-SNE</td><td>nonlinear</td><td>local neighbors</td><td>no</td><td>nothing</td><td>varies with seed</td><td>look at cluster structure</td></tr>
<tr><td class="text-blue-300">UMAP</td><td>nonlinear</td><td>local + some global</td><td>yes, approx.</td><td>nothing</td><td>varies with seed</td><td>look at large data; preprocessing with care</td></tr>
</tbody>
</table>

<div class="grid grid-cols-2 gap-4 mt-5 text-left text-sm">
<div border="2 solid white/5" bg="white/5" rounded-lg px-4 py-2>
Never read <b>sizes, densities or distances between clusters</b> off a t-SNE or UMAP map.
</div>
<div border="2 solid white/5" bg="white/5" rounded-lg px-4 py-2>
Also worth knowing: <b>kernel PCA</b>, <b>Isomap</b>, <b>autoencoders</b> (next module).
</div>
</div>

<style>
.choose { width: 100%; border-collapse: separate; border-spacing: 0 4px; font-size: 0.85rem; margin-top: 0.5rem; }
.choose th { font-size: 0.72rem; text-transform: uppercase; letter-spacing: 0.05em; opacity: 0.6; text-align: left; padding: 2px 8px; }
.choose td { background: rgba(255, 255, 255, 0.05); padding: 8px; text-align: left; }
.choose td:first-child { font-weight: 700; border-radius: 6px 0 0 6px; white-space: nowrap; }
.choose td:last-child { border-radius: 0 6px 6px 0; }
.choose tr.hl td { background: rgba(251, 191, 36, 0.1); }
</style>

<!--
The comparison.

PCA: linear, so it can only find flat structure. It keeps global variance, applies exactly to new points, its axes mean something you can inspect, and it gives the same answer every time. It's what you use for compression, denoising and preprocessing, and it's always worth a first look.

t-SNE: nonlinear, keeps local neighborhoods, can't embed new points, axes mean nothing, and the layout changes with the seed. Use it to look at cluster structure.

UMAP: similar, keeps somewhat more global structure, can embed new points approximately, scales better. Use it to look at large data, and sometimes as preprocessing for clustering, carefully.

The rule from the pitfalls slide applies to both nonlinear methods. And a few names for further reading: kernel PCA, which does PCA in an implicit feature space like the kernel trick in SVMs; Isomap, the shortest-paths-on-a-graph method from Part 4; and autoencoders, which are next.
-->

---
glowSeed: 787
clicks: 6
---

# Summary

<div class="grid grid-cols-3 gap-4 mt-6 text-left">
<div class="reveal" :class="{ shown: $clicks >= 1 }" border="2 solid teal-800" bg="teal-800/20" rounded-lg px-4 py-3>
<div class="font-bold text-teal-300">Few real dimensions</div>
<div class="text-sm opacity-85 mt-1">Data with many columns often varies along a few directions; distances degrade in high d.</div>
</div>
<div class="reveal" :class="{ shown: $clicks >= 2 }" border="2 solid amber-800" bg="amber-800/20" rounded-lg px-4 py-3>
<div class="font-bold text-amber-300">PCA = eigenvectors of Σ</div>
<div class="text-sm opacity-85 mt-1">Max variance = min reconstruction error. λⱼ = variance kept by component j.</div>
</div>
<div class="reveal" :class="{ shown: $clicks >= 3 }" border="2 solid violet-800" bg="violet-800/20" rounded-lg px-4 py-3>
<div class="font-bold text-violet-300">Use it well</div>
<div class="text-sm opacity-85 mt-1">Center (and scale); choose k by variance or CV; fit on training data only.</div>
</div>
<div class="reveal" :class="{ shown: $clicks >= 4 }" border="2 solid blue-800" bg="blue-800/20" rounded-lg px-4 py-3>
<div class="font-bold text-blue-300">Manifolds need local views</div>
<div class="text-sm opacity-85 mt-1">Straight-line distance is only trustworthy between near neighbors: build a neighbor graph.</div>
</div>
<div class="reveal" :class="{ shown: $clicks >= 5 }" border="2 solid orange-800" bg="orange-800/20" rounded-lg px-4 py-3>
<div class="font-bold text-orange-300">t-SNE &amp; UMAP</div>
<div class="text-sm opacity-85 mt-1">Match neighbor probabilities between data and map. Perplexity / n_neighbors set the scale.</div>
</div>
<div class="reveal" :class="{ shown: $clicks >= 6 }" border="2 solid red-800" bg="red-800/20" rounded-lg px-4 py-3>
<div class="font-bold text-red-300">Read maps carefully</div>
<div class="text-sm opacity-85 mt-1">Sizes, gaps, and seeds can mislead. Confirm in the original space.</div>
</div>
</div>

<!--
Six things to take away.

[click] High-dimensional data usually has far fewer real degrees of freedom than columns, and high dimensions break our intuition about distance.
[click] PCA finds the directions of largest variance, which are also the best linear reconstruction, and they're the eigenvectors of the covariance matrix, with the eigenvalues as the variance each keeps.
[click] Using PCA well: center always, standardize when units differ, choose k by the variance curve or by cross-validation, and fit it on training data only.
[click] When data lies on a curved manifold, straight-line distances are only trustworthy between close neighbors, so the nonlinear methods build a neighbor graph.
[click] t-SNE and UMAP find 2D layouts whose neighbor probabilities match the data's; perplexity and n_neighbors set how big a neighborhood counts.
[click] And their maps need careful reading: cluster sizes, gaps and arrangements can be artifacts. Use them to look, then confirm.
-->

---
glowSeed: 788
---

# Next: Neural Networks

<div class="mt-6">
<AutoencoderTeaser />
</div>

<div class="text-sm mt-6 text-left" border="2 solid teal-800" bg="teal-800/20" rounded-lg px-4 py-3>
<b class="text-teal-300">Next module:</b> networks of simple units, trained by gradient descent. One of them, the <b>autoencoder</b>, squeezes data through a narrow middle layer and rebuilds it. With linear layers and squared error it learns <b>PCA's subspace</b>; with nonlinear layers it can follow curved manifolds.
</div>

<!--
This closes the unsupervised learning unit: k-means, hierarchical and density-based clustering, Gaussian mixtures, and now dimensionality reduction.

And it points to the next module, neural networks. Here's one: an autoencoder. A digit goes in, 64 numbers. The network narrows to a bottleneck of just 2 numbers, and then widens again and tries to rebuild the digit. Trained to minimize squared reconstruction error.

Remember "maximize variance equals minimize reconstruction error"? If the layers are linear, the best possible autoencoder spans exactly PCA's subspace. The output on the right is PCA's own 2-component reconstruction of the digit: that's what the linear version would produce. Blurry, because 2 linear components aren't enough. Make the layers nonlinear and the network can learn curved coordinates, a learned, invertible cousin of the manifold methods we saw today.

How to build and train networks like that is the next module.
-->
