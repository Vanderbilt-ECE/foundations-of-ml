---
theme: default
highlighter: shiki
css: unocss
colorSchema: dark
title: 'Calculus for Optimization'
info: |
  ## Calculus for Optimization
  Topic 2 of Mathematical Foundations — Foundations of Machine Learning.
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
glowSeed: 229
---

<div class="absolute inset-0 flex items-center justify-center opacity-90">
<img src="/title-bowl.png" alt="Bowl-shaped optimization surface" class="h-105 object-contain" style="filter: invert(1) hue-rotate(180deg)" />
</div>

<div class="relative z-10">

# Calculus for Optimization

### Topic 2 of Mathematical Foundations

<div class="pt-6 opacity-80 text-lg">
Foundations of Machine Learning
</div>

<div class="pt-40 text-sm opacity-60">
Every model we train is, mechanically, an optimization problem
</div>

</div>

<!--
Frame this as the payoff lecture of the Mathematical Foundations unit: linear algebra gave us the objects (vectors, matrices, weights), probability gave us the objective (maximize likelihood/posterior), and calculus now gives us the mechanism — how a computer actually finds the parameter values that maximize or minimize that objective when there's no clean closed-form solution.

Roadmap for today: derivatives → gradients → chain rule → gradient descent.

Tell students that literally every "training" step they'll see for the rest of the semester, from linear regression to deep neural networks, is some variant of the algorithm we derive today: gradient descent.
-->

---
glowSeed: 14
---

# Derivatives — Definition and Intuition

<div class="grid grid-cols-2 gap-8 items-center mt-2">

<div>

<div class="flex flex-col gap-1.5">

<div v-click>
<div class="min-h-10 px-3 py-1.5 text-xs leading-snug [&>*]:my-0" border="2 solid teal-800" bg="teal-800/20" rounded-lg overflow-hidden>

The derivative $f'(x)$ measures the **instantaneous rate of change** of $f$ at $x$

</div>
</div>

<div v-click>
<div class="min-h-10 px-3 py-1.5 text-xs leading-snug [&>*]:my-0" border="2 solid blue-800" bg="blue-800/20" rounded-lg overflow-hidden>

Formally: the limit of the slope of secant lines as they shrink to a point

</div>
</div>

<div v-click>
<div class="min-h-10 px-3 py-1.5 text-xs leading-snug [&>*]:my-0" border="2 solid orange-800" bg="orange-800/20" rounded-lg overflow-hidden>

Geometric meaning: slope of the **tangent line**

</div>
</div>

<div v-click>
<div class="min-h-10 px-3 py-1.5 text-xs leading-snug [&>*]:my-0" border="2 solid violet-800" bg="violet-800/20" rounded-lg overflow-hidden>

Sign tells direction of steepest local increase; magnitude tells how steep

</div>
</div>

<div class="px-3 py-2 text-sm" border="2 solid teal-800" bg="teal-800/20" rounded-lg overflow-hidden>

<div class="[&>*]:my-0">

$$f'(x) = \lim_{h\to 0} \frac{f(x+h)-f(x)}{h}$$

</div>

</div>

</div>

</div>

<div>
<svg viewBox="0 0 500 340" class="w-full">
  <path d="M 40.0,308.0 L 47.1,310.3 L 54.2,312.4 L 61.4,314.2 L 68.5,315.8 L 75.6,317.1 L 82.7,318.2 L 89.8,319.0 L 96.9,319.6 L 104.1,319.9 L 111.2,320.0 L 118.3,319.8 L 125.4,319.4 L 132.5,318.8 L 139.7,317.8 L 146.8,316.7 L 153.9,315.3 L 161.0,313.6 L 168.1,311.7 L 175.3,309.6 L 182.4,307.2 L 189.5,304.5 L 196.6,301.6 L 203.7,298.5 L 210.8,295.1 L 218.0,291.5 L 225.1,287.6 L 232.2,283.4 L 239.3,279.0 L 246.4,274.4 L 253.6,269.5 L 260.7,264.4 L 267.8,259.0 L 274.9,253.4 L 282.0,247.5 L 289.2,241.4 L 296.3,235.0 L 303.4,228.4 L 310.5,221.5 L 317.6,214.4 L 324.7,207.1 L 331.9,199.5 L 339.0,191.6 L 346.1,183.5 L 353.2,175.1 L 360.3,166.5 L 367.5,157.7 L 374.6,148.6 L 381.7,139.2 L 388.8,129.6 L 395.9,119.8 L 403.1,109.7 L 410.2,99.3 L 417.3,88.8 L 424.4,77.9 L 431.5,66.8 L 438.6,55.5 L 445.8,43.9 L 452.9,32.1 L 460.0,20.0"
        fill="none" stroke="#7dd3fc" stroke-width="3" />

  <!-- secant line, animates from x=4.5 down toward x=3 (tangent) and back -->
  <line x1="320" y1="212" stroke="#fbbf24" stroke-width="2.5">
    <animate attributeName="x2" values="425;390;355;334;323.5;334;355;390;425" dur="4s" repeatCount="indefinite" />
    <animate attributeName="y2" values="77;128;173;197.1;208.4;197.1;173;128;77" dur="4s" repeatCount="indefinite" />
  </line>

  <!-- moving point -->
  <circle r="6" fill="#fbbf24">
    <animate attributeName="cx" values="425;390;355;334;323.5;334;355;390;425" dur="4s" repeatCount="indefinite" />
    <animate attributeName="cy" values="77;128;173;197.1;208.4;197.1;173;128;77" dur="4s" repeatCount="indefinite" />
  </circle>

  <!-- fixed point at x=3 -->
  <circle cx="320" cy="212" r="6" fill="#f472b6" />
  <text x="330" y="235" fill="#f8fafc" style="font-size:16px">x = 3</text>
  <text x="60" y="30" fill="#94a3b8" style="font-size:16px">f(x) = x²</text>
</svg>
<div class="text-sm opacity-70 text-center mt-2">Secant line collapsing into the tangent line at x = 3</div>
</div>

</div>

<!--
Don't rush the limit definition even if it's review — the "secant line collapsing to a tangent line" picture is exactly the mental model students need later for understanding numerical vs. analytical gradients. Very small finite-difference steps can suffer floating-point cancellation; gradient descent's learning-rate tradeoff is a separate issue covered later.
-->

---
glowSeed: 15
---

# Derivatives — Numerical Approximation

```python
import numpy as np

def f(x):
    return x**2

def numerical_derivative(f, x, h=1e-6):
    return (f(x + h) - f(x)) / h

print(numerical_derivative(f, 3.0))  # ~6.0, matches f'(x) = 2x at x=3
```

<!--
Show the numerical derivative code computing an increasingly accurate approximation as `h` shrinks, then show what happens when `h` becomes too small (floating-point cancellation error) — a nice practical preview of why we prefer analytical gradients (autodiff) over finite differences in real ML systems.
-->

---
glowSeed: 55
---

# Common Derivative Rules

<div class="text-sm opacity-70 mb-4">A quick reference, not a derivation — the toolkit for differentiating anything built from these pieces.</div>

<div class="grid grid-cols-2 gap-4">

<div v-click>
<div class="p-4 text-sm" border="2 solid teal-800" bg="teal-800/20" rounded-lg overflow-hidden>
<div class="flex flex-col gap-2">
<div class="font-bold text-base">Power rule</div>
<div class="text-lg [&>*]:my-0">

$\frac{d}{dx}x^n = nx^{n-1}$

</div>
<div class="opacity-80">Used for: squared-error loss derivatives</div>
</div>

</div>
</div>

<div v-click>
<div class="p-4 text-sm" border="2 solid blue-800" bg="blue-800/20" rounded-lg overflow-hidden>
<div class="flex flex-col gap-2">
<div class="font-bold text-base">Sum rule</div>
<div class="text-lg [&>*]:my-0">

$\frac{d}{dx}[f+g] = f'+g'$

</div>
<div class="opacity-80">Used for: differentiating multi-term losses</div>
</div>

</div>
</div>

<div v-click>
<div class="p-4 text-sm" border="2 solid orange-800" bg="orange-800/20" rounded-lg overflow-hidden>
<div class="flex flex-col gap-2">
<div class="font-bold text-base">Product rule</div>
<div class="text-lg [&>*]:my-0">

$\frac{d}{dx}[fg] = f'g + fg'$

</div>
<div class="opacity-80">Used for: sigmoid's derivative in logistic regression</div>
</div>

</div>
</div>

<div v-click>
<div class="p-4 text-sm" border="2 solid violet-800" bg="violet-800/20" rounded-lg overflow-hidden>
<div class="flex flex-col gap-2">
<div class="font-bold text-base">Exp &amp; log</div>
<div class="text-lg [&>*]:my-0">

$\frac{d}{dx}e^x = e^x, \quad \frac{d}{dx}\ln x = \frac{1}{x}$

</div>
<div class="opacity-80">Used for: log-likelihoods, softmax, cross-entropy</div>
</div>

</div>
</div>

</div>

<!--
Move through this quickly as a reference slide rather than a derivation slide — most students have seen these rules before.

The pedagogically useful move is pairing each abstract rule with the specific place it will be used later this semester (power rule for squared-error loss derivatives, log rule for log-likelihood and cross-entropy derivatives, product/quotient rule for the sigmoid function's derivative in logistic regression), so the rules feel anchored to upcoming material rather than free-floating.
-->

---
glowSeed: 56
---

# Common Derivative Rules — Symbolic Check

```python
import sympy as sp

x = sp.symbols('x')
expr = x**3 + sp.exp(x) * sp.log(x)
derivative = sp.diff(expr, x)
print(derivative)   # symbolic verification of product + power + log/exp rules
```

---
glowSeed: 88
---

# Partial Derivatives

<div class="grid grid-cols-2 gap-8 items-center mt-2">

<div>

<v-clicks>

- For functions of multiple variables, a partial derivative measures the rate of change with respect to **one** variable, holding all others fixed
- Notation: $\frac{\partial f}{\partial x}$ (curly d) instead of $\frac{df}{dx}$
- Essential for ML: models have many parameters, and we need the sensitivity of the loss to each one individually

</v-clicks>

<div v-click class="mt-6 text-sm">

$$f(x,y) = x^2 y + y^3$$
$$\frac{\partial f}{\partial x} = 2xy \quad (\text{treat } y \text{ as constant})$$
$$\frac{\partial f}{\partial y} = x^2 + 3y^2 \quad (\text{treat } x \text{ as constant})$$

</div>

</div>

<div>
<img src="/partial-derivatives-surface.png" alt="Surface with slices showing partial derivatives in the x and y directions" class="w-full" style="filter: invert(1) hue-rotate(180deg)" />
<div class="text-sm opacity-70 text-center mt-1">
<span style="color:#ff6b6b">red</span>: slice with y fixed (∂f/∂x) &nbsp;·&nbsp;
<span style="color:#4dd4ff">blue</span>: slice with x fixed (∂f/∂y)
</div>
</div>

</div>

<!--
The "freeze all other variables" framing is the key idea — walk through the worked example treating y as if it were literally a number like 5 while differentiating with respect to x, then repeat the other way.

This directly sets up the next slide (the gradient), since a gradient is nothing more than the collection of all partial derivatives, one per parameter. Emphasize that in a model with a million parameters, we compute a million partial derivatives — but the rule for each one individually is exactly this simple "freeze everything else" idea; the complexity is just in bookkeeping, which is why we let software (autodiff) handle it.
-->

---
glowSeed: 89
---

# Partial Derivatives — Symbolic Check

```python
import sympy as sp

x, y = sp.symbols('x y')
f = x**2 * y + y**3

df_dx = sp.diff(f, x)
df_dy = sp.diff(f, y)
print(df_dx)   # 2*x*y
print(df_dy)   # x**2 + 3*y**2
```

---
glowSeed: 121
---

# The Gradient

<div class="grid grid-cols-2 gap-8 items-center mt-2">

<div>

<v-clicks>

- The gradient $\nabla f$ collects all partial derivatives into a single vector
- Points in the direction of steepest **ascent** of $f$ at that point
- Its negative, $-\nabla f$, points in the direction of steepest **descent** — the basis of gradient descent
- Magnitude of the gradient indicates how steep the function is at that point

</v-clicks>

<div class="p-5 mt-6 text-sm [&>*]:my-1" border="2 solid violet-800" bg="violet-800/20" rounded-lg overflow-hidden>

$$\nabla f(x,y) = \begin{bmatrix} \partial f/\partial x \\ \partial f/\partial y \end{bmatrix}
\qquad
\nabla_\theta f(\theta) = \begin{bmatrix} \partial f/\partial \theta_1 \\ \vdots \\ \partial f/\partial \theta_d \end{bmatrix}$$

</div>

</div>

<div>
<svg viewBox="0 0 500 400" class="w-full">
  <defs>
    <marker id="arrowhead" markerWidth="8" markerHeight="8" refX="4" refY="4" orient="auto">
      <path d="M0,0 L8,4 L0,8 Z" fill="#fbbf24" />
    </marker>
  </defs>
  <circle cx="250" cy="210" r="32" fill="none" stroke="#475569" stroke-width="1.5" />
  <circle cx="250" cy="210" r="64" fill="none" stroke="#475569" stroke-width="1.5" />
  <circle cx="250" cy="210" r="96" fill="none" stroke="#475569" stroke-width="1.5" />
  <circle cx="250" cy="210" r="128" fill="none" stroke="#475569" stroke-width="1.5" />
  <circle cx="250" cy="210" r="5" fill="#38bdf8" />
  <text x="258" y="205" fill="#38bdf8" style="font-size:14px">min</text>

  <line x1="311" y1="174.8" x2="358.6" y2="147.3" stroke="#fbbf24" stroke-width="3" marker-end="url(#arrowhead)" />
  <line x1="225.9" y1="143.8" x2="207.1" y2="92.2" stroke="#fbbf24" stroke-width="3" marker-end="url(#arrowhead)" />
  <line x1="183.8" y1="234.1" x2="132.2" y2="252.9" stroke="#fbbf24" stroke-width="3" marker-end="url(#arrowhead)" />
  <line x1="262.2" y1="279.3" x2="271.8" y2="333.5" stroke="#fbbf24" stroke-width="3" marker-end="url(#arrowhead)" />

  <text x="20" y="30" fill="#94a3b8" style="font-size:15px">f(x,y) = x² + y² (contours), arrows = ∇f (uphill)</text>
</svg>
</div>

</div>

<!--
This is the pivotal slide of the lecture — the entire optimization story for the rest of the semester rests on "gradient points uphill, so we step in the opposite direction."

Make sure students can read the contour plot fluently: closer-together contour lines mean steeper regions (bigger gradient magnitude), and the gradient arrow at any point is always perpendicular to the contour line through that point.

If time allows, connect back to the linear algebra lecture: the gradient is literally a vector living in the same space as the parameters, and everything learned about vectors (direction, magnitude, dot products for measuring alignment between successive gradient steps) applies directly.
-->

---
glowSeed: 122
---

# The Gradient — Computing It

```python
import numpy as np

def f(xy):
    x, y = xy
    return x**2 + y**2

def grad_f(xy):
    x, y = xy
    return np.array([2*x, 2*y])

point = np.array([3.0, 4.0])
print(grad_f(point))   # [6. 8.], points away from the minimum at (0,0)
print(-grad_f(point))  # [-6. -8.], direction of steepest descent, toward (0,0)
```

---
glowSeed: 63
---

# The Chain Rule

<div class="grid grid-cols-3 gap-4">

<div v-click>
<div class="p-4 text-sm [&>*]:my-1" border="2 solid teal-800" bg="teal-800/20" rounded-lg overflow-hidden>

**What it governs**

Differentiating a composition of functions: an "outer" function applied to an "inner" function

</div>
</div>

<div v-click>
<div class="p-4 text-sm [&>*]:my-1" border="2 solid blue-800" bg="blue-800/20" rounded-lg overflow-hidden>

**Single-variable form**

Multiply the derivative of the outer function by the derivative of the inner function

</div>
</div>

<div v-click>
<div class="p-4 text-sm [&>*]:my-1" border="2 solid orange-800" bg="orange-800/20" rounded-lg overflow-hidden>

**Why it matters**

Without exaggeration, **the single most important rule in all of deep learning** — the basis of backpropagation

</div>
</div>

</div>

<div class="p-5 my-5 text-center [&>*]:my-1" border="2 solid violet-800" bg="violet-800/20" rounded-lg overflow-hidden>

$$h(x) = f(g(x)) \implies h'(x) = f'(g(x))\cdot g'(x)$$
$$\text{Example: } h(x) = \sin(x^2) \implies h'(x) = \cos(x^2)\cdot 2x$$

</div>

<!--
Do the h(x)=sin(x^2) derivation by hand on the board, narrating explicitly: "derivative of the outside, evaluated at the inside, times derivative of the inside." Point out that "outer" and "inner" is a labeling choice, not a property of the function — the same expression can be decomposed different ways, but the chain rule gives the same answer regardless.

This is the moment to name the destination explicitly: every layer of a neural network is another composed function, so a network with many layers is one long composition, and differentiating it means chaining this exact rule once per layer.
-->

---
glowSeed: 64
---

# The Chain Rule — Visualized

<div class="flex justify-center mt-8">
<svg viewBox="0 0 700 200" class="w-full max-w-2xl">
  <defs>
    <marker id="arrow2" markerWidth="8" markerHeight="8" refX="4" refY="4" orient="auto">
      <path d="M0,0 L8,4 L0,8 Z" fill="#cbd5e1" />
    </marker>
  </defs>
  <text x="20" y="65" fill="#f8fafc" style="font-size:24px">x</text>
  <line x1="45" y1="60" x2="95" y2="60" stroke="#cbd5e1" stroke-width="2" marker-end="url(#arrow2)" />

  <rect x="100" y="30" width="70" height="60" rx="10" fill="#1e3a5f" stroke="#38bdf8" stroke-width="2" />
  <text x="122" y="67" fill="#7dd3fc" style="font-size:26px">g</text>

  <line x1="170" y1="60" x2="220" y2="60" stroke="#cbd5e1" stroke-width="2" marker-end="url(#arrow2)" />
  <text x="185" y="45" fill="#94a3b8" style="font-size:13px">g(x)</text>

  <rect x="225" y="30" width="70" height="60" rx="10" fill="#3f1e5f" stroke="#a78bfa" stroke-width="2" />
  <text x="248" y="67" fill="#c4b5fd" style="font-size:26px">f</text>

  <line x1="295" y1="60" x2="345" y2="60" stroke="#cbd5e1" stroke-width="2" marker-end="url(#arrow2)" />
  <text x="350" y="65" fill="#f8fafc" style="font-size:20px">h(x) = f(g(x))</text>

  <path d="M 100,100 C 100,150 340,150 340,100" fill="none" stroke="#fbbf24" stroke-width="2.5" marker-end="url(#arrow2)" />
  <text x="90" y="175" fill="#fbbf24" style="font-size:15px">chain rule: multiply the local derivatives along the path</text>
</svg>
</div>

<!--
Then immediately do the single-neuron example (z=wx+b, a=σ(z)) since it's the exact three-function composition (linear transform → nonlinearity) that appears in every layer of a neural network.

Explicitly tell students: "when we reach the neural networks unit and I say 'backpropagation is just the chain rule applied repeatedly through the layers of the network,' I mean that completely literally, not as a loose analogy — today's slide is the entire mathematical content of that algorithm; the rest is bookkeeping and efficient computation."
-->

---
glowSeed: 65
---

# The Chain Rule — Symbolic Check

```python
import sympy as sp

x = sp.symbols('x')
h = sp.sin(x**2)
print(sp.diff(h, x))   # 2*x*cos(x**2), matches chain rule by hand

# a small composed-function example resembling a single neuron:
# z = w*x + b,  a = sigmoid(z)
w, b = sp.symbols('w b')
z = w*x + b
a = 1 / (1 + sp.exp(-z))
da_dw = sp.diff(a, w)
print(sp.simplify(da_dw))
```

---
glowSeed: 140
---

# Chain Rule Worked Example — Setup &amp; Forward Pass

<v-clicks>

- Realistic ML functions are compositions of several stages: linear transform → nonlinearity → loss

</v-clicks>

<div v-click class="mt-2">

$$z = wx+b, \qquad a = \sigma(z) = \frac{1}{1+e^{-z}}, \qquad L = (a-y)^2$$

</div>

```python
import numpy as np

def sigmoid(z):
    return 1.0 / (1.0 + np.exp(-z))

x, y = 2.0, 1.0
w, b = 0.5, 0.1

z = w*x + b
a = sigmoid(z)
L = (a - y)**2
print(f"z={z:.4f}  a={a:.4f}  L={L:.4f}")
```

<!--
This worked example mirrors, in miniature, exactly what backpropagation computes for a single neuron and a single training example.

Walk through the forward pass first (compute z, then a, then L, plugging in actual numbers) before touching any derivatives — this mirrors exactly how a neural network's forward pass works and makes the backward pass feel like a natural next step rather than a separate topic.

Run this code live: z = 1.1, a ≈ 0.7503, L ≈ 0.0624. Keep these numbers on the board — the next slide reuses them for the backward pass.
-->

---
glowSeed: 141
---

# Chain Rule Worked Example — Backward Pass

<div class="p-4 mb-3 text-center [&>*]:my-1" border="2 solid violet-800" bg="violet-800/20" rounded-lg overflow-hidden>

$$\frac{\partial L}{\partial w} = \frac{\partial L}{\partial a}\cdot\frac{\partial a}{\partial z}\cdot\frac{\partial z}{\partial w}$$

$$= \underbrace{2(a-y)}_{\partial L/\partial a} \cdot \underbrace{\sigma(z)(1-\sigma(z))}_{\partial a/\partial z} \cdot \underbrace{x}_{\partial z/\partial w}$$

</div>

<div class="flex justify-center">
<svg viewBox="0 0 760 260" class="w-full max-w-2xl">
  <defs>
    <marker id="fwd" markerWidth="8" markerHeight="8" refX="4" refY="4" orient="auto">
      <path d="M0,0 L8,4 L0,8 Z" fill="#7dd3fc" />
    </marker>
    <marker id="bwd" markerWidth="8" markerHeight="8" refX="4" refY="4" orient="auto">
      <path d="M0,0 L8,4 L0,8 Z" fill="#fbbf24" />
    </marker>
  </defs>

  <!-- forward row -->
  <text x="20" y="75" fill="#f8fafc" style="font-size:18px">x,w,b</text>
  <line x1="75" y1="70" x2="150" y2="70" stroke="#7dd3fc" stroke-width="2" marker-end="url(#fwd)" />
  <text x="90" y="55" fill="#7dd3fc" style="font-size:13px">z=1.10</text>

  <circle cx="180" cy="70" r="28" fill="#0b3550" stroke="#7dd3fc" stroke-width="2" />
  <text x="168" y="76" fill="#e0f2fe" style="font-size:16px">z</text>
  <line x1="208" y1="70" x2="290" y2="70" stroke="#7dd3fc" stroke-width="2" marker-end="url(#fwd)" />
  <text x="215" y="55" fill="#7dd3fc" style="font-size:13px">a=0.750</text>

  <circle cx="320" cy="70" r="28" fill="#0b3550" stroke="#7dd3fc" stroke-width="2" />
  <text x="308" y="76" fill="#e0f2fe" style="font-size:16px">a</text>
  <line x1="348" y1="70" x2="430" y2="70" stroke="#7dd3fc" stroke-width="2" marker-end="url(#fwd)" />
  <text x="355" y="55" fill="#7dd3fc" style="font-size:13px">L=0.062</text>

  <circle cx="460" cy="70" r="28" fill="#0b3550" stroke="#7dd3fc" stroke-width="2" />
  <text x="448" y="76" fill="#e0f2fe" style="font-size:16px">L</text>

  <text x="560" y="75" fill="#94a3b8" style="font-size:14px">forward pass →</text>

  <!-- backward row -->
  <line x1="430" y1="150" x2="348" y2="150" stroke="#fbbf24" stroke-width="2.5" marker-end="url(#bwd)" />
  <text x="358" y="140" fill="#fbbf24" style="font-size:13px">∂L/∂a = −0.500</text>

  <line x1="290" y1="150" x2="208" y2="150" stroke="#fbbf24" stroke-width="2.5" marker-end="url(#bwd)" />
  <text x="212" y="140" fill="#fbbf24" style="font-size:13px">∂a/∂z = 0.187</text>

  <line x1="150" y1="150" x2="75" y2="150" stroke="#fbbf24" stroke-width="2.5" marker-end="url(#bwd)" />
  <text x="78" y="140" fill="#fbbf24" style="font-size:13px">∂z/∂w = x</text>

  <text x="560" y="155" fill="#fbbf24" style="font-size:14px">← backward pass (chain rule)</text>

  <text x="20" y="230" fill="#f8fafc" style="font-size:16px">∂L/∂w = −0.500 × 0.187 × 2.0 ≈ −0.188</text>
</svg>
</div>

<!--
Compute each local derivative one at a time and multiply them together, explicitly narrating that this chained multiplication of local derivatives, applied automatically across every parameter in a large network, is literally what backpropagation is.
-->

---
glowSeed: 142
---

# Chain Rule Worked Example — Code

```python
dL_da = 2*(a - y)
da_dz = a * (1 - a)
dz_dw = x

dL_dw = dL_da * da_dz * dz_dw
print(f"dL/dw = {dL_dw:.5f}")

# sanity check against numerical gradient
def loss(w):
    z = w*x + b
    a = sigmoid(z)
    return (a - y)**2

h = 1e-6
numerical = (loss(w + h) - loss(w - h)) / (2*h)
print(f"numerical dL/dw = {numerical:.5f}")   # should match closely
```

<!--
The numerical-gradient sanity check in the code is worth running live if possible — showing the analytical and numerical gradients match builds real confidence that the chain rule "actually works" rather than being taken on faith.
-->

---
glowSeed: 172
---

# Critical Points and Second Derivatives

<div class="grid grid-cols-2 gap-8 items-center mt-2">

<div>

<div class="flex flex-col gap-2">

<div v-click>
<div class="p-3 text-sm [&>*]:my-1" border="2 solid teal-800" bg="teal-800/20" rounded-lg overflow-hidden>

A critical point occurs where $\nabla f = 0$ — a candidate minimum, maximum, or saddle point

</div>
</div>

<div v-click>
<div class="p-3 text-sm [&>*]:my-1" border="2 solid blue-800" bg="blue-800/20" rounded-lg overflow-hidden>

The second derivative (or Hessian, in multiple dimensions) tells us which one it is

</div>
</div>

<div v-click>
<div class="p-3 text-sm [&>*]:my-1" border="2 solid violet-800" bg="violet-800/20" rounded-lg overflow-hidden>

Connects directly back to positive definiteness from the linear algebra lecture

</div>
</div>

</div>

<div v-click class="mt-4 text-sm">

$$f'(x^*)=0:\quad f''(x^*) > 0 \implies \text{local min}, \quad f''(x^*) < 0 \implies \text{local max}$$
$$\nabla f(\mathbf{x}^*)=0,\ H(\mathbf{x}^*) \succ 0 \implies \text{strict local minimum}$$

</div>

</div>

<div>
<svg viewBox="0 0 500 340" class="w-full">
  <path d="M 89.0,347.5 L 94.5,320.5 L 99.9,295.9 L 105.4,273.4 L 110.8,253.0 L 116.3,234.7 L 121.7,218.3 L 127.2,203.8 L 132.7,191.1 L 138.1,180.1 L 143.6,170.7 L 149.0,162.9 L 154.5,156.5 L 159.9,151.6 L 165.4,147.9 L 170.9,145.5 L 176.3,144.2 L 181.8,144.1 L 187.2,144.9 L 192.7,146.6 L 198.2,149.2 L 203.6,152.5 L 209.1,156.5 L 214.5,161.1 L 220.0,166.2 L 225.4,171.7 L 230.9,177.6 L 236.4,183.8 L 241.8,190.2 L 247.3,196.7 L 252.7,203.3 L 258.2,209.8 L 263.6,216.2 L 269.1,222.4 L 274.6,228.3 L 280.0,233.8 L 285.5,238.9 L 290.9,243.5 L 296.4,247.5 L 301.8,250.8 L 307.3,253.4 L 312.8,255.1 L 318.2,255.9 L 323.7,255.8 L 329.1,254.5 L 334.6,252.1 L 340.1,248.4 L 345.5,243.5 L 351.0,237.1 L 356.4,229.3 L 361.9,219.9 L 367.3,208.9 L 372.8,196.2 L 378.3,181.7 L 383.7,165.3 L 389.2,147.0 L 394.6,126.6 L 400.1,104.1 L 405.5,79.5 L 411.0,52.5"
        fill="none" stroke="#7dd3fc" stroke-width="3" />
  <circle cx="180" cy="144" r="6" fill="#fbbf24" />
  <text x="140" y="130" fill="#fbbf24" style="font-size:14px">local max (x=-1)</text>
  <circle cx="320" cy="256" r="6" fill="#f472b6" />
  <text x="290" y="285" fill="#f472b6" style="font-size:14px">local min (x=1)</text>
  <text x="20" y="30" fill="#94a3b8" style="font-size:15px">f(x) = x³ - 3x</text>
</svg>
</div>

</div>

<!--
Explicitly reconnect to the positive-definite-matrices slide from the linear algebra lecture: the Hessian condition H ≻ 0 for a local minimum is exactly the positive-definiteness condition covered there, now applied to the matrix of second partial derivatives instead of an arbitrary matrix.
-->

---
glowSeed: 174
---

# Critical Points — Saddle Points

<div class="flex items-center gap-8" style="min-height: 70%">
<img src="/saddle-point.png" alt="Saddle-shaped surface" class="h-72" style="filter: invert(1) hue-rotate(180deg)" />
<div class="text-lg opacity-80 max-w-lg">
A saddle point: the Hessian <em>H</em> is indefinite (positive in one direction, negative in another) — the "Pringle chip" shape. In high-dimensional neural network loss landscapes, these are far more common than true local minima.
</div>
</div>

<!--
This is a good moment to be honest about a real limitation students should carry forward: in high-dimensional neural network loss landscapes, saddle points (not local minima) are actually the far more common type of critical point, and a large part of why modern optimizers use momentum and adaptive step sizes is specifically to escape saddle points and flat regions — plant this as a preview for the "Optimization in Practice" unit later in the semester.
-->

---
glowSeed: 173
---

# Critical Points — Symbolic Check

```python
import sympy as sp

x = sp.symbols('x')
f = x**3 - 3*x

critical_points = sp.solve(sp.diff(f, x), x)
print(critical_points)   # [-1, 1]

second_derivative = sp.diff(f, x, 2)
for cp in critical_points:
    print(cp, second_derivative.subs(x, cp))  # sign tells min/max
```

---
glowSeed: 201
---

# Gradient Descent — The Algorithm

<div class="grid grid-cols-2 gap-8 items-center mt-2">

<div>

<v-clicks>

- We rarely have a closed-form solution for $\arg\min$; instead we iteratively step downhill
- Update rule: move a small step in the direction of the negative gradient
- The **learning rate** $\alpha$ controls step size — too large diverges, too small converges slowly
- Repeat until the gradient is near zero (convergence) or a fixed number of iterations is reached

</v-clicks>

<div class="p-5 mt-6 text-center [&>*]:my-1" border="2 solid teal-800" bg="teal-800/20" rounded-lg overflow-hidden>

$$\theta_{t+1} = \theta_t - \alpha \nabla f(\theta_t)$$

</div>

</div>

<div>
<svg viewBox="0 0 500 300" class="w-full">
  <path d="M 40.0,40.0 L 47.5,56.0 L 54.9,71.4 L 62.4,86.3 L 69.8,100.7 L 77.3,114.5 L 84.7,127.7 L 92.2,140.4 L 99.7,152.5 L 107.1,164.1 L 114.6,175.1 L 122.0,185.6 L 129.5,195.5 L 136.9,204.9 L 144.4,213.7 L 151.9,222.0 L 159.3,229.7 L 166.8,236.9 L 174.2,243.5 L 181.7,249.6 L 189.2,255.1 L 196.6,260.1 L 204.1,264.5 L 211.5,268.3 L 219.0,271.7 L 226.4,274.4 L 233.9,276.6 L 241.4,278.3 L 248.8,279.4 L 256.3,279.9 L 263.7,279.9 L 271.2,279.4 L 278.6,278.3 L 286.1,276.6 L 293.6,274.4 L 301.0,271.7 L 308.5,268.3 L 315.9,264.5 L 323.4,260.1 L 330.8,255.1 L 338.3,249.6 L 345.8,243.5 L 353.2,236.9 L 360.7,229.7 L 368.1,222.0 L 375.6,213.7 L 383.1,204.9 L 390.5,195.5 L 398.0,185.6 L 405.4,175.1 L 412.9,164.1 L 420.3,152.5 L 427.8,140.4 L 435.3,127.7 L 442.7,114.5 L 450.2,100.7 L 457.6,86.3 L 465.1,71.4 L 472.5,56.0 L 480.0,40.0"
        fill="none" stroke="#475569" stroke-width="2.5" />

  <!-- static step dots -->
  <g fill="#94a3b8">
    <circle cx="95.0" cy="145.0" r="4" />
    <circle cx="210.5" cy="267.8" r="4" />
    <circle cx="245.2" cy="278.9" r="4" />
    <circle cx="255.5" cy="279.9" r="4" />
    <circle cx="258.7" cy="280.0" r="4" />
  </g>
  <line x1="95.0" y1="145.0" x2="210.5" y2="267.8" stroke="#64748b" stroke-width="1.5" stroke-dasharray="4 4" />
  <line x1="210.5" y1="267.8" x2="245.2" y2="278.9" stroke="#64748b" stroke-width="1.5" stroke-dasharray="4 4" />
  <line x1="245.2" y1="278.9" x2="255.5" y2="279.9" stroke="#64748b" stroke-width="1.5" stroke-dasharray="4 4" />
  <line x1="255.5" y1="279.9" x2="258.7" y2="280.0" stroke="#64748b" stroke-width="1.5" stroke-dasharray="4 4" />

  <!-- animated rolling ball -->
  <circle r="8" fill="#ffb703">
    <animate attributeName="cx" values="95.0;210.5;245.2;255.5;258.7;259.6;259.9;260.0;95.0" keyTimes="0;0.2;0.35;0.48;0.58;0.68;0.78;0.9;1" dur="4s" repeatCount="indefinite" />
    <animate attributeName="cy" values="145.0;267.8;278.9;279.9;280.0;280.0;280.0;280.0;145.0" keyTimes="0;0.2;0.35;0.48;0.58;0.68;0.78;0.9;1" dur="4s" repeatCount="indefinite" />
  </circle>

  <text x="200" y="20" fill="#94a3b8" style="font-size:15px">f(θ) = (θ - 3)², each hop = one GD step</text>
</svg>
</div>

</div>

<!--
Spend real time on the learning rate: show what happens with alpha = 0.1 (smooth convergence), alpha = 0.9 (oscillation but still converges for this simple quadratic), and alpha = 1.1 (diverges) if time allows — this hands-on experimentation is one of the best ways to build intuition for a hyperparameter students will tune constantly for the rest of the course.

Note explicitly that this exact update rule, applied to millions of parameters simultaneously via the gradient vector, is literally how every model in this course gets trained, from linear regression up through deep networks.
-->

---
glowSeed: 202
---

# Gradient Descent — Code

```python
import numpy as np

def f(theta):
    return (theta - 3.0)**2

def grad_f(theta):
    return 2 * (theta - 3.0)

theta = 0.0
alpha = 0.1

history = [theta]
for step in range(50):
    theta = theta - alpha * grad_f(theta)
    history.append(theta)

print(f"Final theta: {theta:.4f}")   # converges toward 3.0
```

<!--
Run the code live and print theta at each step (or plot history) so students see the sequence of numbers actually converging — this is far more convincing than the formula alone.
-->

---
glowSeed: 233
---

# Gradient Descent Variants

<div class="text-sm opacity-70 mb-4">Batch, stochastic, and mini-batch — the same update rule, different amounts of data per step.</div>

<div class="grid grid-cols-3 gap-4 mt-4">

<div v-click>
<div class="p-4 text-sm" border="2 solid teal-800" bg="teal-800/20" rounded-lg overflow-hidden>
<div class="flex flex-col gap-2">
<div class="font-bold text-base">🎯 Batch GD</div>
<div>Gradient over the <strong>entire dataset</strong> every step. Accurate but slow for large datasets.</div>
<div class="[&>*]:my-0">

$\theta_{t+1} = \theta_t - \alpha \frac{1}{n}\sum_{i=1}^n \nabla \ell_i$

</div>
</div>

</div>
</div>

<div v-click>
<div class="p-4 text-sm" border="2 solid orange-800" bg="orange-800/20" rounded-lg overflow-hidden>
<div class="flex flex-col gap-2">
<div class="font-bold text-base">🎲 SGD</div>
<div>Gradient from a <strong>single random example</strong>. Fast, noisy updates — noise can help escape shallow minima/saddles.</div>
</div>

</div>
</div>

<div v-click>
<div class="p-4 text-sm" border="2 solid violet-800" bg="violet-800/20" rounded-lg overflow-hidden>
<div class="flex flex-col gap-2">
<div class="font-bold text-base">⚖️ Mini-batch</div>
<div>A small random subset per step — the <strong>standard choice</strong> in practice.</div>
<div class="[&>*]:my-0">

$\theta_{t+1} = \theta_t - \alpha \frac{1}{m}\sum_{i \in B} \nabla \ell_i$

</div>
</div>

</div>
</div>

</div>

<div v-click class="mt-8 flex justify-center">
<div class="px-6 py-3 text-lg [&>*]:my-1" border="2 solid white/5" bg="white/5" backdrop-blur-sm rounded-lg overflow-hidden>

<code>batch_size</code> in <code>model.fit(...)</code> is exactly this concept

</div>
</div>

<!--
This is a very practical, hands-on slide — emphasize the real trade-off practitioners face: batch gradient descent gives the most accurate direction per step but is often computationally infeasible for datasets with millions of examples (one step requires a full pass over the data), while SGD is noisy but lets you take vastly more steps per unit time.

Mini-batch is the practical default used by essentially every deep learning framework, and it's worth explicitly naming that the batch_size argument students will later pass to model.fit(...) in Keras is exactly this concept.
-->

---
glowSeed: 234
---

# GD Variants — Visual Comparison

<div class="grid grid-cols-2 gap-8 items-center mt-2">

<div>
<svg viewBox="0 0 500 400" class="w-full">
  <circle cx="250" cy="210" r="32" fill="none" stroke="#334155" stroke-width="1.5" />
  <circle cx="250" cy="210" r="64" fill="none" stroke="#334155" stroke-width="1.5" />
  <circle cx="250" cy="210" r="96" fill="none" stroke="#334155" stroke-width="1.5" />
  <circle cx="250" cy="210" r="128" fill="none" stroke="#334155" stroke-width="1.5" />
  <circle cx="250" cy="210" r="5" fill="#94a3b8" />

  <!-- batch: smooth direct path -->
  <polyline points="120,90 175,130 215,165 240,190 250,210" fill="none" stroke="#2dd4bf" stroke-width="3" />

  <!-- SGD: noisy zig-zag -->
  <polyline points="120,90 160,70 140,120 190,110 170,160 220,150 200,190 240,185 220,215 250,210"
            fill="none" stroke="#fb923c" stroke-width="2" stroke-dasharray="3 3" />

  <!-- mini-batch: moderate noise -->
  <polyline points="120,90 150,110 200,140 190,175 230,195 250,210" fill="none" stroke="#a78bfa" stroke-width="2.5" stroke-dasharray="6 3" />

  <circle cx="120" cy="90" r="5" fill="#f8fafc" />
  <text x="90" y="75" fill="#f8fafc" style="font-size:13px">start</text>
</svg>
<div class="text-sm mt-2 flex justify-center gap-6">
<span style="color:#2dd4bf">● Batch</span>
<span style="color:#fb923c">● SGD</span>
<span style="color:#a78bfa">● Mini-batch</span>
</div>
</div>

<div>

```python
import numpy as np
rng = np.random.default_rng(0)

# toy linear regression via mini-batch gradient descent
n, d = 500, 3
X = rng.normal(size=(n, d))
true_w = np.array([1.5, -2.0, 0.5])
y = X @ true_w + rng.normal(scale=0.1, size=n)

w = np.zeros(d)
alpha, batch_size, epochs = 0.05, 32, 20

for epoch in range(epochs):
    idx = rng.permutation(n)
    for start in range(0, n, batch_size):
        batch = idx[start:start+batch_size]
        Xb, yb = X[batch], y[batch]
        grad = -2 * Xb.T @ (yb - Xb @ w) / len(batch)
        w -= alpha * grad

print(w)   # should approach true_w
```

</div>

</div>

<!--
Run the mini-batch code live and show the weights converging to true_w.

Batch gradient descent traces a smooth, direct path to the minimum; SGD is a jagged, noisy zig-zag path that still generally trends toward the minimum; mini-batch sits in between — moderate noise, faster than batch. This is exactly the trade-off named on the previous slide, now made visual.
-->

---
glowSeed: 260
---

# Gradient Descent in scikit-learn and Keras

<div class="text-sm">
<v-clicks>

- scikit-learn: `SGDRegressor`, `SGDClassifier`, etc. expose gradient-based fitting directly
- Keras: `model.compile(optimizer=...)` + `model.fit(...)` use autodiff — no manual derivative code
- Both hide the update-rule bookkeeping behind `.fit()`, but the math is exactly what we just derived

</v-clicks>
</div>

<div class="grid grid-cols-2 gap-4 mt-2">

<div v-click>
<div class="p-2 text-xs" border="2 solid white/5" bg="white/5" backdrop-blur-sm rounded-lg overflow-hidden>

**scikit-learn**

```python
from sklearn.linear_model import SGDRegressor
import numpy as np

X = np.random.randn(500, 3)
y = X @ [1.5, -2.0, 0.5] + 0.1 * np.random.randn(500)

model = SGDRegressor(eta0=0.01)
model.fit(X, y)
print(model.coef_)   # approaches true_w
```

</div>
</div>

<div v-click>
<div class="p-2 text-xs" border="2 solid teal-800" bg="teal-800/20" rounded-lg overflow-hidden>

**Keras**

```python
import keras
from keras import layers

model = keras.Sequential([
    keras.Input(shape=(3,)),
    layers.Dense(1)
])
opt = keras.optimizers.SGD(0.1)
model.compile(optimizer=opt, loss='mse')
# model.fit(X, y, epochs=20, batch_size=32)
```

</div>
</div>

</div>

<div v-click class="mt-3 flex justify-center">
<div class="px-6 py-2 text-sm [&>*]:my-1" border="2 solid white/5" bg="white/5" backdrop-blur-sm rounded-lg overflow-hidden>

Manual <code>for</code> loop ⟶ <code>model.fit(X, y)</code> — **same algorithm, automated**

</div>
</div>

<!--
The goal of this slide is to demystify library "magic" — students should leave knowing that model.fit() is not a black box performing some entirely different, unknowable process; it is executing essentially the same loop written by hand two slides ago, just with automatic differentiation computing the gradients instead of a manually derived formula, and with considerable engineering for efficiency (vectorization, GPU acceleration, adaptive learning rates).

Preview that automatic differentiation itself is just repeated application of the chain rule, tracked automatically through a computation graph — worth stating explicitly since "autodiff" will otherwise sound like unrelated new machinery when it's introduced properly in the neural networks unit.
-->

---
class: text-center
glowSeed: 300
---

# Summary and What's Next

<div class="grid grid-cols-3 gap-6 max-w-5xl mx-auto mt-8 text-left">

<div v-click>
<div class="px-6 py-5 [&>*]:my-1" border="2 solid teal-800" bg="teal-800/20" rounded-lg overflow-hidden>
<div class="text-3xl mb-2">📐</div>
<div class="font-bold mb-2">Linear Algebra</div>
Gave us the objects: vectors, matrices, weights.
</div>
</div>

<div v-click>
<div class="px-6 py-5 [&>*]:my-1" border="2 solid amber-800" bg="amber-800/20" rounded-lg overflow-hidden>
<div class="text-3xl mb-2">🎲</div>
<div class="font-bold mb-2">Probability</div>
Gave us the objective: maximize likelihood/posterior.
</div>
</div>

<div v-click>
<div class="px-6 py-5 [&>*]:my-1" border="2 solid violet-800" bg="violet-800/20" rounded-lg overflow-hidden>
<div class="text-3xl mb-2">📉</div>
<div class="font-bold mb-2">Calculus</div>
Gives us the mechanism: gradient descent finds the minimizer.
</div>
</div>

</div>

<div v-click class="mt-4 text-left max-w-3xl mx-auto text-sm">

- Derivatives measure rate of change; gradients generalize this to multiple parameters
- The chain rule lets us differentiate compositions of functions — the mathematical basis of backpropagation
- Gradient descent iteratively walks downhill on a loss surface to find good parameters
- Batch/stochastic/mini-batch variants trade off accuracy of each step against computational cost

</div>

<div v-click class="mt-4 text-base opacity-90">
Next: <strong>Core ML Concepts</strong> — supervised vs. unsupervised learning, bias-variance tradeoff, and train/validation/test methodology
</div>

<!--
Use this slide to explicitly close the loop across all three Mathematical Foundations lectures: remind students that linear regression's loss function (squared error) was justified via MLE under a Gaussian noise assumption (probability lecture), that ridge regression's penalty term falls out of a Gaussian prior under MAP estimation (also probability), and that the mechanism for finding the actual minimizing weights in both cases is the gradient descent algorithm from today.

Tell students that from here on, when a new model or loss function is introduced, they should reflexively ask "what is this the MLE/MAP of, and how would gradient descent optimize it" — that habit is the through-line connecting the entire Mathematical Foundations unit to everything else in the course. Take questions before moving to Core ML Concepts.
-->

---
layout: center
class: text-center
glowSeed: 229
---

# Thank You

### Questions &amp; Discussion

<div class="pt-6 opacity-80">
Calculus for Optimization · Mathematical Foundations
</div>

<!--
Take questions before moving to Core ML Concepts.
-->
