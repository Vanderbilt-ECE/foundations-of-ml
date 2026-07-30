---
theme: default
highlighter: shiki
css: unocss
colorSchema: dark
title: 'Support Vector Machines and the Kernel Trick'
info: |
  ## Support Vector Machines and the Kernel Trick
  Maximum-margin classification and implicit nonlinear feature spaces.
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
glowSeed: 481
---

# Support Vector Machines

### Maximum margins and the kernel trick

<div class="pt-5 opacity-80 text-lg">Supervised Learning · Classification</div>

<svg role="img" aria-label="Two classes separated by a maximum margin street with circled support vectors" viewBox="0 0 760 260" class="w-full max-w-3xl mx-auto mt-7">
  <path d="M235 250 L450 10" stroke="#60a5fa" stroke-width="3" stroke-dasharray="8 6"/><path d="M315 250 L530 10" stroke="#f8fafc" stroke-width="5"/><path d="M395 250 L610 10" stroke="#fb923c" stroke-width="3" stroke-dasharray="8 6"/>
  <path d="M235 250 L450 10 L610 10 L395 250 Z" fill="#0f766e22"/>
  <g fill="#60a5fa"><circle cx="175" cy="65" r="8"/><circle cx="245" cy="110" r="8"/><circle cx="315" cy="160" r="8"/><circle cx="375" cy="205" r="8"/></g>
  <g fill="#fb923c"><circle cx="470" cy="55" r="8"/><circle cx="535" cy="105" r="8"/><circle cx="585" cy="165" r="8"/><circle cx="640" cy="210" r="8"/></g>
  <circle cx="315" cy="160" r="17" fill="none" stroke="#f8fafc" stroke-width="3"/><circle cx="535" cy="105" r="17" fill="none" stroke="#f8fafc" stroke-width="3"/>
</svg>

<!--
Ask a genuinely new question that neither logistic regression nor decision trees asked: among all the hyperplanes that separate two classes, which one is best? Logistic regression finds a boundary implicitly, as a byproduct of maximizing likelihood; a decision tree finds axis-aligned splits by greedy impurity reduction. SVM asks the geometric question directly and answers it directly: choose the separating hyperplane with the most breathing room on both sides — the maximum margin — because that boundary should be the most robust to small perturbations or new data points near the class boundary.

Roadmap for today: why maximum margin is the right criterion, the hard-margin optimization problem and its solution's dependence only on "support vectors," soft margins for data that is not perfectly separable, the hinge loss that connects SVMs back to the general empirical-risk-minimization framework, the dual formulation, and the kernel trick that lets SVMs draw nonlinear boundaries without ever explicitly constructing a high-dimensional feature map. Contrast this geometric, margin-based optimization with logistic regression's probabilistic maximum-likelihood optimization — two very different justifications that often produce visually similar decision boundaries.
-->

---
glowSeed: 482
---

# Which Separating Line Would You Trust?

<div class="grid grid-cols-3 gap-4 mt-5 text-center text-sm">
<div v-click border="2 solid orange-800" bg="orange-800/20" rounded-lg p-3><strong>hugs blue</strong><svg role="img" aria-label="A valid separator too close to the blue class" viewBox="0 0 210 160" class="w-full"><g fill="#60a5fa"><circle cx="45" cy="40" r="6"/><circle cx="65" cy="85" r="6"/><circle cx="85" cy="120" r="6"/></g><g fill="#fb923c"><circle cx="135" cy="35" r="6"/><circle cx="155" cy="80" r="6"/><circle cx="175" cy="120" r="6"/></g><line x1="90" y1="145" x2="115" y2="15" stroke="#f8fafc" stroke-width="4"/></svg>fragile to blue shifts</div>
<div v-click border="2 solid teal-800" bg="teal-800/20" rounded-lg p-3><strong>maximum margin</strong><svg role="img" aria-label="A separator centered between the classes with a wide margin" viewBox="0 0 210 160" class="w-full"><g fill="#60a5fa"><circle cx="45" cy="40" r="6"/><circle cx="65" cy="85" r="6"/><circle cx="85" cy="120" r="6"/></g><g fill="#fb923c"><circle cx="135" cy="35" r="6"/><circle cx="155" cy="80" r="6"/><circle cx="175" cy="120" r="6"/></g><line x1="105" y1="145" x2="125" y2="15" stroke="#f8fafc" stroke-width="4"/><line x1="80" y1="145" x2="100" y2="15" stroke="#2dd4bf" stroke-dasharray="5 4"/><line x1="130" y1="145" x2="150" y2="15" stroke="#2dd4bf" stroke-dasharray="5 4"/></svg>largest buffer</div>
<div v-click border="2 solid orange-800" bg="orange-800/20" rounded-lg p-3><strong>hugs orange</strong><svg role="img" aria-label="A valid separator too close to the orange class" viewBox="0 0 210 160" class="w-full"><g fill="#60a5fa"><circle cx="45" cy="40" r="6"/><circle cx="65" cy="85" r="6"/><circle cx="85" cy="120" r="6"/></g><g fill="#fb923c"><circle cx="135" cy="35" r="6"/><circle cx="155" cy="80" r="6"/><circle cx="175" cy="120" r="6"/></g><line x1="125" y1="145" x2="145" y2="15" stroke="#f8fafc" stroke-width="4"/></svg>fragile to orange shifts</div>
</div>

<div v-click class="mt-7" border="2 solid white/10" bg="white/5" rounded-lg p-4><strong>Support vectors</strong> are the closest points. They alone pin down the margin and boundary.</div>

<!--
Have students vote before revealing the middle choice — all three lines shown perfectly separate the training data with zero training error, so accuracy alone cannot distinguish them. The line that "hugs" the blue class is fragile: a new blue point sampled slightly further out, or ordinary sampling noise in the existing points, could easily fall on the wrong side. The maximum-margin line, by contrast, is centered in the widest possible strip separating the two classes, giving the most buffer against exactly that kind of perturbation in either direction.

Define support vectors carefully, since the term is used constantly for the rest of the deck: they are the training points that lie exactly on the margin boundary — the closest points of each class to the separating hyperplane. Critically, the maximum-margin hyperplane's position and orientation are determined entirely by these support vectors; every other training point could be moved further from the boundary, or even deleted, without changing the fitted boundary at all, since it played no role in the optimization's active constraints. This is the geometric root of an important practical property covered later: SVM predictions typically depend on only a small subset of the training data.
-->

---
glowSeed: 483
---

# Hard Margin as an Optimization Problem

<div class="grid grid-cols-2 gap-8 mt-3 items-center">
<div>
<div border="2 solid blue-800" bg="blue-800/20" rounded-lg p-4>

$$x^\top w+b=0\quad\text{decision boundary}$$
$$\text{margin width}=\frac{2}{\|w\|_2}$$
$$\min_{w,b}\frac12\|w\|_2^2\quad\text{s.t.}\quad y_i(x_i^\top w+b)\ge1$$

</div>
<v-clicks>

- Normalize the margin planes to scores $+1$ and $-1$
- Maximizing $2/\|w\|$ equals minimizing $\|w\|^2/2$
- Every training point must be correct and outside the margin

</v-clicks>
</div>
<svg role="img" aria-label="Decision boundary and two parallel margin planes separated by two over the norm of w" viewBox="0 0 470 320" class="w-full">
  <line x1="125" y1="300" x2="330" y2="20" stroke="#60a5fa" stroke-width="3" stroke-dasharray="7 5"/><line x1="205" y1="300" x2="410" y2="20" stroke="#f8fafc" stroke-width="5"/><line x1="285" y1="300" x2="455" y2="65" stroke="#fb923c" stroke-width="3" stroke-dasharray="7 5"/>
  <line x1="205" y1="145" x2="310" y2="220" stroke="#2dd4bf" stroke-width="4"/><text x="210" y="205" fill="#5eead4">2 / ‖w‖₂</text>
  <text x="45" y="55" fill="#93c5fd">score = −1</text><text x="310" y="35" fill="#f8fafc">score = 0</text><text x="345" y="285" fill="#fdba74">score = +1</text>
</svg>
</div>

<!--
Derive the margin width from point-to-hyperplane distance, since it explains where 2/‖w‖ comes from rather than asking students to accept it on faith. The signed distance from any point x to the hyperplane x^T w + b = 0 is (x^T w + b)/‖w‖. By construction, points exactly on the positive margin plane satisfy x^T w + b = 1, and points on the negative margin plane satisfy x^T w + b = -1, so the distance from the positive margin plane to the boundary is 1/‖w‖, and by symmetry the same distance separates the boundary from the negative margin plane — giving a total margin width, positive plane to negative plane, of 1/‖w‖ + 1/‖w‖ = 2/‖w‖.

Maximizing 2/‖w‖ is the actual goal, but it is easier to instead minimize ‖w‖²/2: minimizing the squared norm is a smooth, convex quadratic objective (no square root to differentiate) and is exactly equivalent, since 2/‖w‖ is maximized precisely when ‖w‖ is minimized, and squaring a nonnegative quantity preserves its ordering. This is the L2 norm from the very first Linear Algebra lecture in Mathematical Foundations returning in a load-bearing role: minimizing ‖w‖ literally means finding the shortest weight vector consistent with correctly separating every point by at least the margin, and every training point must satisfy y_i(x_i^T w + b) ≥ 1 — correctly classified, and outside the margin, not just on the correct side of the boundary.
-->

---
glowSeed: 483.5
---

# A Worked Margin Calculation

<div class="grid grid-cols-2 gap-7 mt-3 items-center">
<div>

<div border="2 solid white/10" bg="white/5" rounded-lg p-4 class="text-sm">
Support vectors: $(1,0)$ labeled $-1$ and $(3,0)$ labeled $+1$
</div>

<v-clicks>

- Boundary must sit halfway: $x_1 = 2$, so $w=(1,0),\ b=-2$
- Check $(1,0)$: $y(x^\top w+b)=(-1)(1-2)=1$ ✓ on margin
- Check $(3,0)$: $y(x^\top w+b)=(1)(3-2)=1$ ✓ on margin
- $\|w\|_2=1\Rightarrow$ margin width $=2/\|w\|_2=2$

</v-clicks>

</div>

```python
import numpy as np

w, b = np.array([1.0, 0.0]), -2.0
x_pos, x_neg = np.array([3.0, 0.0]), np.array([1.0, 0.0])

score_pos = x_pos @ w + b   # 1.0
score_neg = x_neg @ w + b   # -1.0
assert 1 * score_pos == 1 and -1 * score_neg == 1

margin_width = 2 / np.linalg.norm(w)
assert margin_width == 2.0   # matches x=1 to x=3 gap
```

</div>

<!--
Ground the abstract formula 2/‖w‖ in an example simple enough to verify by hand. Two support vectors sit on the x-axis: (1,0) belongs to the negative class, (3,0) to the positive class. The boundary that maximizes the margin between two points on a line must sit exactly halfway, at x=2, so choose w=(1,0) and b=-2 to place that boundary at x_1 - 2 = 0.

Check both points against the margin constraint y_i(x_i^T w + b) ≥ 1: for (1,0) with y=-1, the score is 1(1)+0(0)-2 = -1, and y times that score is (-1)(-1)=1, satisfying the constraint with equality — this point sits exactly on the margin, confirming it is a genuine support vector. Symmetrically for (3,0) with y=+1, the score is 3-2=1, and y times score is (1)(1)=1, also exactly on the margin. Since ‖w‖ = ‖(1,0)‖ = 1, the margin width formula gives 2/‖w‖ = 2/1 = 2 — which matches the geometric distance between x=1 and x=3 exactly, a good sanity check that the formula and the geometry agree. This tiny example generalizes: in higher dimensions the same algebra holds, just with w no longer confined to one axis.
-->

---
glowSeed: 484
---

# Soft Margins Handle Real Data

<div class="grid grid-cols-2 gap-7 mt-2">
<div>
<div border="2 solid violet-800" bg="violet-800/20" rounded-lg p-4>

$$\min_{w,b,\xi}\frac12\|w\|_2^2+C\sum_i\xi_i$$
$$y_i(x_i^\top w+b)\ge1-\xi_i,\qquad \xi_i\ge0$$

</div>
<div class="grid grid-cols-2 gap-3 mt-4 text-sm text-center">
<div v-click border="2 solid blue-800" bg="blue-800/20" rounded-lg p-4><strong>small C</strong><br/>wide margin<br/>tolerates violations<br/>stronger regularization</div>
<div v-click border="2 solid orange-800" bg="orange-800/20" rounded-lg p-4><strong>large C</strong><br/>narrow margin<br/>punishes violations<br/>weaker regularization</div>
</div>
</div>

```python
from sklearn.datasets import make_classification
from sklearn.svm import SVC

X, y = make_classification(
    n_samples=200, n_features=2,
    n_redundant=0, flip_y=.1,
    random_state=0)

for C in [.01, 1, 100]:
    model = SVC(kernel='linear', C=C).fit(X, y)
    print(C, model.n_support_)
```
</div>

<!--
The hard-margin formulation from the previous two slides has no solution at all when the classes overlap even slightly — there may be no hyperplane that puts every single point on the correct side of its margin, and the optimization problem is infeasible. Soft margins fix this by introducing a slack variable ξ_i ≥ 0 for every training point, which measures how far that point is allowed to violate its margin constraint: ξ_i = 0 means the point satisfies the original hard-margin constraint, a small positive ξ_i means the point is inside the margin but still correctly classified, and ξ_i > 1 means the point is actually misclassified. Each unit of slack is "purchased" at a cost of C in the objective, so the optimizer no longer requires zero violations, but it does pay a price proportional to C for every violation it accepts.

State the direction of C slowly and explicitly, since it governs the whole bias-variance tradeoff for SVMs: small C makes violations cheap, so the optimizer happily accepts a wider, more heavily regularized margin with several points inside or across it, trading some training accuracy for a smoother, more generalizable boundary; large C makes violations expensive, so the optimizer shrinks the margin and works hard to classify every point correctly, risking overfitting to noise near the boundary. This is exactly the same direction as scikit-learn's `LogisticRegression` C parameter (small C, more regularization; large C, less), even though the two models minimize entirely different loss functions — hinge loss here, log loss there.
-->

---
glowSeed: 485
---

# Hinge Loss Connects SVMs to ERM

<div class="grid grid-cols-2 gap-7 mt-3 items-center">
<div>
<div border="2 solid teal-800" bg="teal-800/20" rounded-lg p-4>

$$\ell_{hinge}(y,s)=\max(0,1-ys),\quad s=x^\top w+b$$
$$\frac1n\sum_i\max(0,1-y_is_i)+\frac{1}{2Cn}\|w\|_2^2$$

</div>

```python
import numpy as np

def hinge_loss(y, score):
    return np.maximum(0, 1-y*score)

assert hinge_loss(1, 2) == 0
assert hinge_loss(1, .5) == .5
assert hinge_loss(1, -1) == 2
```
</div>
<svg role="img" aria-label="Hinge, logistic, and zero one losses plotted against signed margin" viewBox="0 0 470 310" class="w-full">
  <line x1="45" y1="270" x2="440" y2="270" stroke="#64748b"/><line x1="245" y1="270" x2="245" y2="25" stroke="#64748b"/>
  <path d="M55 35 L315 270 L430 270" fill="none" stroke="#2dd4bf" stroke-width="5"/><path d="M55 45 C155 70 220 135 260 190 C310 250 370 266 430 269" fill="none" stroke="#60a5fa" stroke-width="4"/><path d="M55 80 H245 V270 H430" fill="none" stroke="#fb923c" stroke-width="3" stroke-dasharray="6 5"/>
  <text x="330" y="60" fill="#5eead4">hinge</text><text x="330" y="90" fill="#93c5fd">log</text><text x="330" y="120" fill="#fdba74">0–1</text><text x="180" y="300" fill="#94a3b8">signed margin ys</text>
</svg>
</div>

<!--
Close the loop back to the general empirical-risk-minimization template introduced in the loss-functions material: every classifier in this course fits into the same "minimize average loss plus a regularization penalty" shape, and the soft-margin SVM objective from the previous slide is exactly that, once rewritten with the hinge loss ℓ_hinge(y,s) = max(0, 1-ys), where s = x^T w + b is the raw signed score before thresholding. Walk through the three assertions in the code: hinge_loss(1, 2) is 0 because the true label is 1 and the score 2 is well beyond the margin on the correct side (ys = 2 ≥ 1); hinge_loss(1, .5) is 0.5 because the score is inside the margin (ys = 0.5 < 1), a partial penalty; hinge_loss(1, -1) is 2 because the point is on the wrong side entirely (ys = -1), a larger penalty.

The key qualitative difference from log loss, visible in the plotted curves: hinge loss becomes exactly zero once a point is correctly classified with score at least 1 beyond the margin, so confident, already-correct points exert precisely zero influence on the gradient — this is the mathematical reason only support vectors matter for the fitted boundary. Log loss, by contrast, never reaches exactly zero for any finite score; it keeps decreasing asymptotically as confidence increases, so every single training point, however easy, contributes at least a small amount to logistic regression's gradient at all times. This single structural difference explains why SVM solutions are sparse (defined by a subset of support vectors) while logistic regression solutions use information from the entire training set.
-->

---
glowSeed: 485.5
---

# The Dual Formulation

<div class="grid grid-cols-2 gap-7 mt-2 items-center">
<div>
<div border="2 solid violet-800" bg="violet-800/20" rounded-lg p-4>

$$\max_{\alpha}\sum_i\alpha_i-\frac12\sum_i\sum_j\alpha_i\alpha_jy_iy_j\bigl(x_i^\top x_j\bigr)$$
$$\text{s.t.}\quad 0\le\alpha_i\le C,\quad \sum_i\alpha_iy_i=0$$

</div>

<v-clicks>

- Lagrangian stationarity gives $w=\sum_i\alpha_iy_ix_i$
- Support vectors are exactly the points with $\alpha_i>0$
- Prediction: $\hat y(x)=\operatorname{sign}\!\bigl(\sum_i\alpha_iy_i(x_i^\top x)+b\bigr)$
- The data enters **only** through dot products $x_i^\top x_j$

</v-clicks>

</div>

<div border="2 solid teal-800" bg="teal-800/20" rounded-lg p-4 class="text-sm">
This dot-product-only structure is exactly what the kernel trick exploits next: replace <code>xᵢᵀxⱼ</code> everywhere with a kernel function and the whole derivation still holds.
</div>

</div>

<!--
The primal problem from earlier slides minimizes over w and b directly, subject to inequality constraints. Constrained optimization theory (Lagrangian duality) rewrites this as an equivalent problem: introduce one multiplier alpha_i ≥ 0 per training-point constraint, form the Lagrangian, and require stationarity — the gradient of the Lagrangian with respect to w and b must be zero at the optimum. Setting ∂L/∂w = 0 yields w = Σ_i alpha_i y_i x_i: the optimal weight vector is a weighted combination of the training points, where the weight is alpha_i y_i. Setting ∂L/∂b = 0 yields the constraint Σ_i alpha_i y_i = 0.

Substituting these two stationarity conditions back into the Lagrangian eliminates w and b entirely, leaving a maximization problem purely over the alpha_i's — the dual problem shown above, subject to 0 ≤ alpha_i ≤ C, and the same Σ alpha_i y_i = 0 constraint (C caps each alpha_i in the soft-margin case; hard margin is the C→∞ limit). Complementary slackness, another consequence of the optimization theory, guarantees that alpha_i > 0 only for points sitting exactly on or inside the margin — these are precisely the support vectors introduced earlier; every other point has alpha_i = 0 and contributes nothing to w or to the prediction function. Emphasize the single most important structural fact about the dual: both the objective and the prediction rule reference the training data only through pairwise dot products, x_i^T x_j during training and x_i^T x during prediction — never through the raw feature vectors individually. That is the exact opening the kernel trick needs, covered next.
-->

---
glowSeed: 486
---

# The Kernel Trick

<div border="2 solid blue-800" bg="blue-800/20" rounded-lg px-5 py-3>

$$x_i^\top x_j\quad\longrightarrow\quad K(x_i,x_j)=\phi(x_i)^\top\phi(x_j)$$

</div>

<svg role="img" aria-label="Concentric circles in two dimensions map to two height levels in three dimensions where a plane separates them" viewBox="0 0 820 330" class="w-full max-w-2xl mx-auto mt-2">
  <g transform="translate(30,20)"><text x="100" y="10" fill="#f8fafc">original 2D space</text><circle cx="155" cy="155" r="95" fill="none" stroke="#60a5fa" stroke-width="4"/><circle cx="155" cy="155" r="42" fill="none" stroke="#fb923c" stroke-width="4"/><g fill="#60a5fa"><circle cx="60" cy="155" r="6"/><circle cx="155" cy="60" r="6"/><circle cx="250" cy="155" r="6"/><circle cx="155" cy="250" r="6"/></g><g fill="#fb923c"><circle cx="125" cy="145" r="6"/><circle cx="175" cy="130" r="6"/><circle cx="165" cy="185" r="6"/></g></g>
  <text x="372" y="165" fill="#2dd4bf" style="font-size:42px">φ →</text>
  <g transform="translate(450,20)"><text x="105" y="10" fill="#f8fafc">lifted feature space</text><line x1="35" y1="270" x2="315" y2="270" stroke="#64748b"/><line x1="35" y1="270" x2="35" y2="45" stroke="#64748b"/><polygon points="45,145 275,110 330,165 95,200" fill="#0f766e55" stroke="#2dd4bf" stroke-width="3"/><g fill="#60a5fa"><circle cx="75" cy="75" r="7"/><circle cx="140" cy="65" r="7"/><circle cx="220" cy="80" r="7"/><circle cx="285" cy="70" r="7"/></g><g fill="#fb923c"><circle cx="120" cy="235" r="7"/><circle cx="185" cy="230" r="7"/><circle cx="250" cy="240" r="7"/></g></g>
</svg>

<div v-click class="text-center mt-2">A nonlinear boundary below becomes a flat separating plane above—without explicitly constructing <code>φ(x)</code>.</div>

<!--
Walk through the concentric-circles lift slowly, since it is the clearest possible illustration of why nonlinear features help: in the original 2D space, the inner circle (one class) and outer ring (the other class) cannot be separated by any straight line — no linear boundary exists. But if we map each point through a feature function φ that adds a third coordinate related to distance from the origin (for instance, φ(x) = (x_1, x_2, x_1²+x_2²)), the inner-circle points land at a low height and the outer-ring points land at a high height in this lifted 3D space, and a flat plane can now separate them perfectly. A curved boundary in the original space becomes a flat one after a nonlinear lift — this is the same idea behind polynomial regression's basis expansion, just applied to classification.

The key insight the dual formulation just handed us: since both training and prediction only ever need the dot product x_i^T x_j (or x_i^T x), we do not need to explicitly compute φ(x) for every point and then take dot products of those lifted vectors — we only need a function K(x_i, x_j) that directly computes what that dot product would have been, φ(x_i)^T φ(x_j), without ever materializing φ(x) itself. This substitution is the kernel trick, and its power is that K can correspond to a feature map φ that is very high-dimensional, or even infinite-dimensional (as with the RBF kernel on the next slide), while K itself remains cheap to evaluate — turning an intractable explicit computation into a tractable implicit one.
-->

---
glowSeed: 487
---

# Common Kernels

<div class="grid grid-cols-3 gap-4 mt-3 text-sm">
<div v-click border="2 solid blue-800" bg="blue-800/20" rounded-lg p-4><strong>Linear</strong><div class="mt-3"><code>K(xᵢ,xⱼ) = xᵢᵀxⱼ</code></div><div class="opacity-70 mt-3">no feature lift</div></div>
<div v-click border="2 solid violet-800" bg="violet-800/20" rounded-lg p-4><strong>Polynomial</strong><div class="mt-3"><code>(xᵢᵀxⱼ + c)ᵖ</code></div><div class="opacity-70 mt-3">implicit polynomial terms</div></div>
<div v-click border="2 solid teal-800" bg="teal-800/20" rounded-lg p-4><strong>RBF / Gaussian</strong><div class="mt-3"><code>exp(−γ‖xᵢ−xⱼ‖²)</code></div><div class="opacity-70 mt-3">flexible local influence</div></div>
</div>

```python
from sklearn.datasets import make_circles
from sklearn.model_selection import cross_val_score

Xc, yc = make_circles(
    n_samples=200, noise=.1, factor=.4,
    random_state=0)
for kernel in ['linear', 'poly', 'rbf']:
    score = cross_val_score(
        SVC(kernel=kernel, gamma='scale'),
        Xc, yc, cv=5).mean()
    print(kernel, score)
```

<div v-click class="mt-4 text-center text-sm opacity-80">Choose kernel, <code>C</code>, degree <code>p</code>, and <code>γ</code> by cross-validation. Large <code>γ</code> is highly local; small <code>γ</code> underfits.</div>

<!--
Three named kernels cover most practical use cases. The linear kernel K(x_i,x_j) = x_i^T x_j is just the ordinary dot product — no feature lift at all, equivalent to the original linear SVM, appropriate when the classes are already close to linearly separable in the raw feature space. The polynomial kernel (x_i^T x_j + c)^p implicitly computes dot products in a feature space containing all polynomial terms up to degree p (products and powers of the original features), without ever explicitly forming that expanded feature vector. The RBF (radial basis function, also called Gaussian) kernel exp(-γ‖x_i-x_j‖²) corresponds to an infinite-dimensional feature space — it can be shown via a Taylor series expansion of the exponential that no finite-dimensional φ produces this kernel — yet it remains cheap to evaluate because it only ever needs the squared distance between two points, never the (nonexistent, explicit) infinite-dimensional vectors themselves.

Run the circles experiment live: with the concentric-circles dataset (which is not linearly separable, by construction), the linear kernel should perform near chance level (roughly 50% cross-validated accuracy for balanced two-class data), while the RBF kernel should score near-perfect, since its implicit feature space can represent the circular boundary these data actually need. Gamma, the RBF kernel's parameter, controls the radius of influence of each training point: large gamma makes each point's influence very localized, which can memorize training noise (high variance, risk of overfitting); small gamma makes influence spread widely, producing an almost-linear, smoother boundary (higher bias). Treat kernel choice, C, polynomial degree p, and gamma all as hyperparameters to select by cross-validation, exactly like k in k-NN or tree depth — there is no default combination that is right for every dataset.
-->

---
layout: center
class: text-center
glowSeed: 488
---

# Five Ways to Classify

<div class="grid grid-cols-5 gap-2 mt-7 text-left text-xs">
<div v-click border="2 solid blue-800" bg="blue-800/20" rounded-lg p-3><strong>Logistic</strong><div class="opacity-75 mt-2">probability + log loss</div></div>
<div v-click border="2 solid teal-800" bg="teal-800/20" rounded-lg p-3><strong>k-NN</strong><div class="opacity-75 mt-2">neighbor vote</div></div>
<div v-click border="2 solid violet-800" bg="violet-800/20" rounded-lg p-3><strong>Naive Bayes</strong><div class="opacity-75 mt-2">generative probability</div></div>
<div v-click border="2 solid orange-800" bg="orange-800/20" rounded-lg p-3><strong>Trees</strong><div class="opacity-75 mt-2">greedy rules</div></div>
<div v-click border="2 solid amber-800" bg="amber-800/20" rounded-lg p-3><strong>SVM</strong><div class="opacity-75 mt-2">margin geometry</div></div>
</div>

<div v-click class="mt-8" border="2 solid white/10" bg="white/5" rounded-lg p-4>Soft margins trade width against violations. Kernels make nonlinear boundaries implicit. Support vectors alone define the fit.</div>

<div v-click class="mt-7 text-lg"><strong>Next:</strong> Model Evaluation — precision, recall, F1, ROC/AUC, and fair comparison.</div>

<!--
Close the complete classification unit with all five strategies side by side: logistic regression fits a probability model by maximum likelihood; k-NN votes among stored neighbors with no training-time work; Naive Bayes inverts a generative probability model via Bayes' rule; decision trees greedily partition space with interpretable rules; SVMs maximize geometric margin, expressible in a dual form that supports the kernel trick for implicit nonlinear boundaries. None of these five is universally best — the right choice depends on dataset size, feature dimensionality, whether interpretability is required, prediction-latency constraints, and whether the true boundary is likely linear or curved.

Recap the SVM-specific takeaways one more time: soft margins trade margin width against how many training points are allowed to violate it, governed by C; kernels make nonlinear boundaries implicit and tractable by replacing explicit high-dimensional feature computation with cheap pairwise kernel evaluations; and support vectors alone — the points with nonzero alpha_i in the dual — define the fit, so the model can be compact even when trained on large datasets. The next unit, Model Evaluation, supplies precision, recall, F1, and ROC/AUC — the rigorous tools needed to compare all five of these classifiers fairly, especially under class imbalance or asymmetric misclassification costs.
-->
