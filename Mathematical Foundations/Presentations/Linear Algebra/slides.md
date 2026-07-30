---
theme: default
highlighter: shiki
css: unocss
colorSchema: dark
title: 'Linear Algebra for Machine Learning'
info: |
  ## Linear Algebra for Machine Learning
  Topic 0 of Mathematical Foundations — Foundations of Machine Learning.
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
glowSeed: 11
---

<div class="relative z-10">

# Linear Algebra for Machine Learning

### Topic 0 of Mathematical Foundations

<div class="pt-6 opacity-80 text-lg">
Foundations of Machine Learning
</div>

<div class="pt-40 text-sm opacity-60">
Every dataset, weight, and model is, mechanically, a collection of vectors and matrices
</div>

</div>

<!--
Open the Mathematical Foundations unit here: linear algebra gives us the objects (vectors, matrices, weights), probability will give us the objective, and calculus will give us the mechanism.

Roadmap for today: vectors → matrices and matrix multiplication → linear transformations → eigenvalues/eigenvectors → positive definiteness. This vocabulary shows up in every subsequent lecture — a feature row is a vector, a dataset is a matrix, a layer of a neural network is a matrix multiplication.
-->

---
glowSeed: 12
---

# Vectors — What They Are

<div class="grid grid-cols-2 gap-3 mt-3">

<div v-click>
<div class="p-3 text-sm" border="2 solid teal-800" bg="teal-800/20" rounded-lg overflow-hidden>
<div class="flex flex-col gap-2">
<div class="font-bold">What it is</div>
<div>A vector is an ordered list of numbers — geometrically, a point or an arrow in space</div>
</div>

</div>
</div>

<div v-click>
<div class="p-3 text-sm" border="2 solid blue-800" bg="blue-800/20" rounded-lg overflow-hidden>
<div class="flex flex-col gap-2">
<div class="font-bold">In ML</div>
<div>Almost always a <strong>feature representation</strong>: one row of a dataset, one set of model weights, one embedding</div>
</div>

</div>
</div>

<div v-click>
<div class="p-3 text-sm" border="2 solid orange-800" bg="orange-800/20" rounded-lg overflow-hidden>
<div class="flex flex-col gap-2">
<div class="font-bold">Operations</div>
<div>Vectors support two core operations: addition and scalar multiplication</div>
</div>

</div>
</div>

<div v-click>
<div class="p-3 text-sm" border="2 solid violet-800" bg="violet-800/20" rounded-lg overflow-hidden>
<div class="flex flex-col gap-2">
<div class="font-bold">Dimensionality</div>
<div>Number of entries; a "high-dimensional" model just means a long vector</div>
</div>

</div>
</div>

</div>

<div v-click class="mt-3 text-sm">

$$\mathbf{x} = \begin{bmatrix} x_1 \\ x_2 \\ \vdots \\ x_n \end{bmatrix} \in \mathbb{R}^n$$

</div>

<!--
Ground this immediately in ML terms: a single row of a spreadsheet-style dataset (age, income, height) is literally a vector in R^3. A grayscale image flattened to a list of pixel intensities is a vector in a very high-dimensional space.
-->

---
glowSeed: 13
---

# Vectors — Geometry

<div class="grid grid-cols-2 gap-8 items-center mt-2">

<div>

<v-clicks>

- Vector addition: place arrows tip-to-tail, or add componentwise
- Scalar multiplication stretches, shrinks, or flips a vector's direction
- The **norm** $\|\mathbf{x}\|$ measures a vector's length
- The **dot product** measures alignment between two vectors

</v-clicks>

<div v-click class="mt-4 text-sm">

$$\|\mathbf{x}\|_2 = \sqrt{x_1^2 + x_2^2 + \cdots + x_n^2}$$
$$\mathbf{a}\cdot\mathbf{b} = \sum_i a_i b_i = \|\mathbf{a}\|\|\mathbf{b}\|\cos\theta$$

</div>

</div>

<div>
<svg viewBox="0 0 400 320" class="w-full">
  <line x1="40" y1="280" x2="380" y2="280" stroke="#475569" stroke-width="1.5" />
  <line x1="40" y1="280" x2="40" y2="20" stroke="#475569" stroke-width="1.5" />

  <defs>
    <marker id="av1" markerWidth="8" markerHeight="8" refX="4" refY="4" orient="auto">
      <path d="M0,0 L8,4 L0,8 Z" fill="#38bdf8" />
    </marker>
    <marker id="av2" markerWidth="8" markerHeight="8" refX="4" refY="4" orient="auto">
      <path d="M0,0 L8,4 L0,8 Z" fill="#fbbf24" />
    </marker>
    <marker id="av3" markerWidth="8" markerHeight="8" refX="4" refY="4" orient="auto">
      <path d="M0,0 L8,4 L0,8 Z" fill="#f472b6" />
    </marker>
  </defs>

  <line x1="40" y1="280" x2="220" y2="140" stroke="#38bdf8" stroke-width="3" marker-end="url(#av1)" />
  <text x="225" y="135" fill="#38bdf8" style="font-size:14px">a</text>

  <line x1="220" y1="140" x2="340" y2="60" stroke="#fbbf24" stroke-width="3" marker-end="url(#av2)" />
  <text x="345" y="55" fill="#fbbf24" style="font-size:14px">b</text>

  <line x1="40" y1="280" x2="340" y2="60" stroke="#f472b6" stroke-width="3" stroke-dasharray="6 4" marker-end="url(#av3)" />
  <text x="250" y="200" fill="#f472b6" style="font-size:14px">a + b</text>

  <text x="20" y="15" fill="#94a3b8" style="font-size:14px">tip-to-tail vector addition</text>
</svg>
</div>

</div>

<!--
Draw this on the board too. Emphasize the dot product's role: it's how "similarity" gets computed everywhere in ML — cosine similarity for embeddings, attention scores in transformers, and the weighted sum inside every neuron are all dot products.
-->

---
glowSeed: 14
---

# Vectors — Code

```python
import numpy as np

a = np.array([2.0, 1.0, 3.0])
b = np.array([1.0, 4.0, 0.0])

print(a + b)              # elementwise addition
print(2.5 * a)             # scalar multiplication
print(np.linalg.norm(a))   # L2 norm (length)
print(np.dot(a, b))        # dot product

cos_theta = np.dot(a, b) / (np.linalg.norm(a) * np.linalg.norm(b))
print(cos_theta)           # cosine similarity between a and b
```

<!--
Run this live. Point out that `np.dot` is the same operation used millions of times per second inside a neural network's forward pass — nothing more exotic is happening under the hood.
-->

---
glowSeed: 30
---

# Matrices — What They Are

<div class="grid grid-cols-2 gap-4 mt-4">

<div v-click>
<div class="p-4 text-sm [&>*]:my-1" border="2 solid teal-800" bg="teal-800/20" rounded-lg overflow-hidden>

A matrix is a rectangular grid of numbers — a collection of vectors, or a transformation

</div>
</div>

<div v-click>
<div class="p-4 text-sm [&>*]:my-1" border="2 solid blue-800" bg="blue-800/20" rounded-lg overflow-hidden>

An $m \times n$ matrix has $m$ rows and $n$ columns

</div>
</div>

<div v-click>
<div class="p-4 text-sm [&>*]:my-1" border="2 solid violet-800" bg="violet-800/20" rounded-lg overflow-hidden>

In ML, a matrix is usually a **dataset** (rows = examples, columns = features) or a **layer's weights**

</div>
</div>

<div v-click>
<div class="p-4 text-sm [&>*]:my-1" border="2 solid violet-800" bg="violet-800/20" rounded-lg overflow-hidden>

Matrices support addition, scalar multiplication, and — most importantly — matrix multiplication

</div>
</div>

</div>

<div v-click class="mt-6 text-sm">

$$A \in \mathbb{R}^{m\times n} = \begin{bmatrix} a_{11} & a_{12} & \cdots & a_{1n} \\ a_{21} & a_{22} & \cdots & a_{2n} \\ \vdots & \vdots & \ddots & \vdots \\ a_{m1} & a_{m2} & \cdots & a_{mn} \end{bmatrix}$$

</div>

<!--
Concrete framing: if you have 1000 training examples each with 20 features, your dataset is a 1000×20 matrix. If a neural network layer maps a 784-dimensional input (a flattened MNIST image) to a 128-dimensional hidden representation, that layer's weights are a 128×784 matrix.
-->

---
glowSeed: 31
---

# Matrix Multiplication

<div class="grid grid-cols-2 gap-8 items-center mt-2">

<div>

<v-clicks>

- $(AB)_{ij}$ = dot product of row $i$ of $A$ with column $j$ of $B$
- Requires inner dimensions to match: $(m\times n)(n\times p) = (m\times p)$
- Not commutative: $AB \neq BA$ in general
- This single operation **is** a neural network layer: weights times inputs, plus a bias

</v-clicks>

<div v-click class="mt-4 text-sm">

$$\mathbf{z} = W\mathbf{x} + \mathbf{b}$$

</div>

</div>

<div>
<svg viewBox="0 0 440 320" class="w-full">
  <text x="10" y="20" fill="#94a3b8" style="font-size:14px">row i of A · column j of B → entry (i,j)</text>

  <g>
    <text x="20" y="60" fill="#38bdf8" style="font-size:13px">A</text>
    <rect x="20" y="70" width="120" height="180" fill="none" stroke="#475569" stroke-width="1.5" />
    <rect x="20" y="70" width="120" height="60" fill="#38bdf8" opacity="0.35">
      <animate attributeName="y" values="70;130;190;70" keyTimes="0;0.333;0.667;1" calcMode="discrete" dur="6s" repeatCount="indefinite" />
    </rect>
    <line x1="80" y1="70" x2="80" y2="250" stroke="#475569" stroke-width="1" />
    <line x1="20" y1="130" x2="140" y2="130" stroke="#475569" stroke-width="1" />
    <line x1="20" y1="190" x2="140" y2="190" stroke="#475569" stroke-width="1" />
  </g>

  <g>
    <text x="200" y="60" fill="#fbbf24" style="font-size:13px">B</text>
    <rect x="200" y="70" width="180" height="120" fill="none" stroke="#475569" stroke-width="1.5" />
    <rect x="200" y="70" width="60" height="120" fill="#fbbf24" opacity="0.35">
      <animate attributeName="x" values="200;260;320;200" keyTimes="0;0.333;0.667;1" calcMode="discrete" dur="6s" repeatCount="indefinite" />
    </rect>
    <line x1="260" y1="70" x2="260" y2="190" stroke="#475569" stroke-width="1" />
    <line x1="320" y1="70" x2="320" y2="190" stroke="#475569" stroke-width="1" />
    <line x1="200" y1="130" x2="380" y2="130" stroke="#475569" stroke-width="1" />
  </g>

  <g>
    <text x="200" y="215" fill="#f472b6" style="font-size:13px">AB</text>
    <rect x="200" y="225" width="180" height="90" fill="none" stroke="#475569" stroke-width="1.5" />
    <rect x="200" y="225" width="60" height="30" fill="#f472b6" opacity="0.5">
      <animate attributeName="x" values="200;260;320;200" keyTimes="0;0.333;0.667;1" calcMode="discrete" dur="6s" repeatCount="indefinite" />
      <animate attributeName="y" values="225;255;285;225" keyTimes="0;0.333;0.667;1" calcMode="discrete" dur="6s" repeatCount="indefinite" />
    </rect>
    <line x1="260" y1="225" x2="260" y2="315" stroke="#475569" stroke-width="1" />
    <line x1="320" y1="225" x2="320" y2="315" stroke="#475569" stroke-width="1" />
    <line x1="200" y1="255" x2="380" y2="255" stroke="#475569" stroke-width="1" />
    <line x1="200" y1="285" x2="380" y2="285" stroke="#475569" stroke-width="1" />
  </g>
</svg>
</div>

</div>

<!--
Walk through the picture: the highlighted row of A and highlighted column of B combine (via dot product) into the single highlighted entry of AB. Every entry of the output is one dot product like this.

This is the moment to say explicitly: forward propagation through a neural network layer is nothing but z = Wx + b, a matrix-vector product plus a bias vector, followed by a nonlinearity. Everything about "deep learning" sits on top of this one operation applied repeatedly.
-->

---
glowSeed: 32
---

# Matrix Multiplication — Code

```python
import numpy as np

W = np.array([[0.2, -0.5, 0.1],
              [0.8,  0.3, -0.4]])   # a "layer": maps R^3 -> R^2
x = np.array([1.0, 2.0, 3.0])
b = np.array([0.1, -0.2])

z = W @ x + b
print(z)   # the layer's pre-activation output

A = np.random.randn(4, 3)
B = np.random.randn(3, 5)
print((A @ B).shape)   # (4, 5) -- inner dimensions (3) must match
```

<!--
Emphasize the shape-checking habit: whenever a matrix multiplication throws a shape error in practice, it means the inner dimensions don't line up — this is one of the most common bugs when building neural network architectures by hand.
-->

---
glowSeed: 45
---

# Linear Transformations

<div class="grid grid-cols-2 gap-8 items-center mt-2">

<div>

<v-clicks>

- Multiplying a vector by a matrix is a **linear transformation**: rotation, scaling, shearing, or projection
- Linear means it preserves addition and scalar multiplication: $A(\mathbf{u}+\mathbf{v}) = A\mathbf{u}+A\mathbf{v}$
- The **identity matrix** $I$ leaves every vector unchanged
- The **inverse** $A^{-1}$ undoes the transformation, when it exists

</v-clicks>

<div v-click class="mt-4 text-sm">

$$AA^{-1} = A^{-1}A = I$$

</div>

</div>

<div>
<svg viewBox="0 0 400 300" class="w-full">
  <line x1="30" y1="260" x2="380" y2="260" stroke="#475569" stroke-width="1.5" />
  <line x1="30" y1="260" x2="30" y2="20" stroke="#475569" stroke-width="1.5" />

  <polygon points="30,260 130,260 130,200 30,200" fill="#38bdf8" opacity="0.3" stroke="#38bdf8" />
  <text x="45" y="235" fill="#38bdf8" style="font-size:13px">unit square</text>

  <defs>
    <marker id="tf" markerWidth="8" markerHeight="8" refX="4" refY="4" orient="auto">
      <path d="M0,0 L8,4 L0,8 Z" fill="#fbbf24" />
    </marker>
  </defs>
  <line x1="160" y1="150" x2="220" y2="150" stroke="#fbbf24" stroke-width="2" marker-end="url(#tf)" />
  <text x="165" y="140" fill="#fbbf24" style="font-size:13px">apply A</text>

  <polygon points="240,260 340,260 380,180 280,180" fill="#f472b6" opacity="0.3" stroke="#f472b6" />
  <text x="270" y="235" fill="#f472b6" style="font-size:13px">sheared &amp; scaled</text>
</svg>
</div>

</div>

<!--
The picture to leave students with: a matrix is a machine that takes every point in space and moves it somewhere else, consistently. A unit square becomes a parallelogram. Rotation matrices, scaling matrices, and projection matrices are all just different choices of A.
-->

---
glowSeed: 46
---

# Eigenvalues and Eigenvectors

<div class="grid grid-cols-2 gap-8 items-center mt-2">

<div>

<div class="flex flex-col gap-1.5 mt-1">

<div v-click>
<div class="px-3 py-1.5 text-sm" border="2 solid teal-800" bg="teal-800/20" rounded-lg overflow-hidden>

An eigenvector of $A$ lies on a direction that $A$ only **scales** (and may flip), never turns off that line

</div>
</div>

<div v-click>
<div class="px-3 py-1.5 text-sm" border="2 solid blue-800" bg="blue-800/20" rounded-lg overflow-hidden>

The amount of stretch is the corresponding eigenvalue $\lambda$

</div>
</div>

<div v-click>
<div class="px-3 py-1.5 text-sm" border="2 solid orange-800" bg="orange-800/20" rounded-lg overflow-hidden>

Found by solving $\det(A - \lambda I) = 0$

</div>
</div>

<div v-click>
<div class="px-3 py-1.5 text-sm" border="2 solid violet-800" bg="violet-800/20" rounded-lg overflow-hidden>

Used throughout ML: PCA finds the eigenvectors of a covariance matrix; they reveal a dataset's dominant directions of variance

</div>
</div>

</div>

<div v-click class="mt-2 text-sm">

$$A\mathbf{v} = \lambda\mathbf{v}$$

</div>

</div>

<div>
<svg viewBox="0 0 480 300" class="w-full">
  <circle cx="200" cy="150" r="4" fill="#94a3b8" />
  <ellipse cx="200" cy="150" rx="140" ry="70" fill="none" stroke="#475569" stroke-width="1.5" />

  <defs>
    <marker id="ev" markerWidth="8" markerHeight="8" refX="4" refY="4" orient="auto">
      <path d="M0,0 L8,4 L0,8 Z" fill="#38bdf8" />
    </marker>
    <marker id="ev2" markerWidth="8" markerHeight="8" refX="4" refY="4" orient="auto">
      <path d="M0,0 L8,4 L0,8 Z" fill="#f472b6" />
    </marker>
  </defs>

  <line x1="200" y1="150" x2="340" y2="150" stroke="#38bdf8" stroke-width="3" marker-end="url(#ev)" />
  <text x="345" y="145" fill="#38bdf8" style="font-size:14px">v₁ (λ₁ = 2)</text>

  <line x1="200" y1="150" x2="200" y2="80" stroke="#f472b6" stroke-width="3" marker-end="url(#ev2)" />
  <text x="205" y="75" fill="#f472b6" style="font-size:14px">v₂ (λ₂ = 0.7)</text>

  <text x="10" y="20" fill="#94a3b8" style="font-size:14px">eigenvectors point along the ellipse's axes</text>
</svg>
</div>

</div>

<!--
The stretched-ellipse picture is the one to remember for a symmetric positive-definite A: apply A to a circle of vectors, and it deforms into an ellipse whose axes point along A's eigenvectors, with axis scales equal to the positive eigenvalues. This is exactly the geometric picture behind PCA and behind understanding the "shape" of a loss landscape's curvature (the Hessian's eigenvectors/eigenvalues) — a preview for the calculus lecture.
-->

---
glowSeed: 47
---

# Eigenvalues — Code

```python
import numpy as np

A = np.array([[2.0, 0.4],
              [0.4, 1.7]])

eigenvalues, eigenvectors = np.linalg.eig(A)
print(eigenvalues)    # the two lambda values
print(eigenvectors)   # columns are the corresponding eigenvectors

# verify: A @ v should equal lambda * v
v = eigenvectors[:, 0]
lam = eigenvalues[0]
print(np.allclose(A @ v, lam * v))   # True
```

<!--
Run this live and verify the defining property A @ v == lambda * v numerically — it demystifies eigenvalues as "just a number and a direction satisfying one equation," rather than abstract machinery.
-->

---
glowSeed: 60
---

# Positive Definite Matrices

<div class="grid grid-cols-2 gap-8 items-center mt-2">

<div>

<v-clicks>

- A symmetric matrix $A$ is **positive definite** if $\mathbf{x}^\top A \mathbf{x} > 0$ for every nonzero $\mathbf{x}$
- Equivalently: all of its eigenvalues are positive
- Geometrically: the "bowl" always curves upward, in every direction — no flat or downward directions
- This is exactly the condition for a quadratic function to have a unique minimum — the calculus lecture will lean on this directly

</v-clicks>

<div v-click class="mt-4 text-sm">

$$A \succ 0 \iff \mathbf{x}^\top A \mathbf{x} > 0 \; \forall \mathbf{x} \neq 0 \iff \text{all } \lambda_i > 0$$

</div>

</div>

<div>
<svg viewBox="0 0 400 300" class="w-full">
  <ellipse cx="130" cy="150" rx="90" ry="60" fill="none" stroke="#2dd4bf" stroke-width="2" />
  <ellipse cx="130" cy="150" rx="60" ry="40" fill="none" stroke="#2dd4bf" stroke-width="2" />
  <ellipse cx="130" cy="150" rx="30" ry="20" fill="none" stroke="#2dd4bf" stroke-width="2" />
  <circle cx="130" cy="150" r="4" fill="#2dd4bf" />
  <text x="45" y="230" fill="#2dd4bf" style="font-size:13px">positive definite (bowl)</text>

  <path d="M 260,120 C 300,90 340,90 380,120" fill="none" stroke="#f472b6" stroke-width="2" />
  <path d="M 260,180 C 300,210 340,210 380,180" fill="none" stroke="#f472b6" stroke-width="2" />
  <circle cx="320" cy="150" r="4" fill="#f472b6" />
  <text x="255" y="230" fill="#f472b6" style="font-size:13px">indefinite (saddle)</text>
</svg>
</div>

</div>

<!--
Plant this seed explicitly for later: when the calculus lecture introduces the Hessian and says "H ≻ 0 implies local minimum," this slide is the entire content of that condition, just applied to second derivatives instead of an arbitrary matrix. Also mention that ridge regression's penalty term and covariance matrices are always positive semi-definite by construction.
-->

---
glowSeed: 61
---

# Positive Definite — Code

```python
import numpy as np

def is_positive_definite(A):
    eigenvalues = np.linalg.eigvalsh(A)   # symmetric matrices have real eigenvalues
    return np.all(eigenvalues > 0)

bowl = np.array([[2.0, 0.4], [0.4, 1.7]])
saddle = np.array([[1.0, 0.0], [0.0, -1.0]])

print(is_positive_definite(bowl))     # True
print(is_positive_definite(saddle))   # False
```

<!--
This tiny function is literally the test used to check whether a quadratic loss (or a Hessian at a critical point) describes a genuine minimum. Worth having students internalize this exact three-line pattern.
-->

---
layout: center
class: text-center
glowSeed: 300
---

# Summary and What's Next

<div class="grid grid-cols-3 gap-6 max-w-5xl mx-auto mt-8 text-left">

<div v-click>
<div class="px-6 py-5 [&>*]:my-1" border="2 solid teal-800" bg="teal-800/20" rounded-lg overflow-hidden>
<div class="text-3xl mb-2">📐</div>
<div class="font-bold mb-2">Linear Algebra</div>
Gives us the objects: vectors, matrices, weights.
</div>
</div>

<div v-click>
<div class="px-6 py-5 [&>*]:my-1" border="2 solid amber-800" bg="amber-800/20" rounded-lg overflow-hidden>
<div class="text-3xl mb-2">🎲</div>
<div class="font-bold mb-2">Probability</div>
Next up: the objective — maximize likelihood/posterior.
</div>
</div>

<div v-click>
<div class="px-6 py-5 [&>*]:my-1" border="2 solid violet-800" bg="violet-800/20" rounded-lg overflow-hidden>
<div class="text-3xl mb-2">📉</div>
<div class="font-bold mb-2">Calculus</div>
Later: the mechanism — gradient descent finds the minimizer.
</div>
</div>

</div>

<div v-click class="mt-8 text-left max-w-3xl mx-auto">

- Vectors are feature rows, weights, and embeddings; dot products measure alignment
- Matrix multiplication is the core operation of every neural network layer: $W\mathbf{x}+\mathbf{b}$
- Eigenvalues and eigenvectors reveal a matrix's stretching directions — the basis of PCA
- Positive definiteness is exactly the condition for a "bowl-shaped" loss with a unique minimum

</div>

<div v-click class="mt-8 text-lg opacity-90">
Next: <strong>Probability and Statistics</strong>
</div>

<!--
Close by reminding students this is genuinely the vocabulary for the rest of the course: every time we write W @ x, that's matrix multiplication; every time we normalize a vector, that's the L2 norm; every time PCA or a covariance matrix comes up, that's eigenvalues. Random variables, distributions, and where loss functions come from is next. Take questions before moving to Probability and Statistics.
-->

---
layout: center
class: text-center
glowSeed: 229
---

# Thank You

### Questions &amp; Discussion

<div class="pt-6 opacity-80">
Linear Algebra for Machine Learning · Mathematical Foundations
</div>

<!--
Take questions before moving to Probability and Statistics.
-->
