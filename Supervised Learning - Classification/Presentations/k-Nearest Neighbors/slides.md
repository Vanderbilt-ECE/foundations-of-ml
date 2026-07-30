---
theme: default
highlighter: shiki
css: unocss
colorSchema: dark
title: 'k-Nearest Neighbors'
info: |
  ## k-Nearest Neighbors
  Classification by local similarity, with no training-time optimization.
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
glowSeed: 421
---

# k-Nearest Neighbors

### Classification without training

<div class="pt-5 opacity-80 text-lg">Supervised Learning · Classification</div>

<svg role="img" aria-label="A query star surrounded by five nearby labeled points with a three to two majority" viewBox="0 0 650 260" class="w-full max-w-2xl mx-auto mt-7">
  <circle cx="330" cy="135" r="105" fill="#0f766e22" stroke="#2dd4bf" stroke-width="3" stroke-dasharray="8 6"/>
  <g fill="#60a5fa"><circle cx="280" cy="85" r="10"/><circle cx="385" cy="95" r="10"/><circle cx="355" cy="195" r="10"/></g>
  <g fill="#fb923c"><circle cx="245" cy="165" r="10"/><circle cx="420" cy="160" r="10"/></g>
  <text x="314" y="151" fill="#fbbf24" style="font-size:42px">★</text>
  <text x="235" y="245" fill="#94a3b8">five neighbors → blue wins 3–2</text>
</svg>

<!--
Contrast with logistic regression immediately, since students just saw a very different paradigm: k-NN has no loss function, no gradient, and no learned coefficients at all. It is non-parametric — it makes no fixed-form assumption about the decision boundary's shape, and its effective complexity grows with the amount of training data rather than being fixed by a parameter count — and instance-based, meaning the "model" is literally just the stored training examples themselves.

k-NN is conventionally called a lazy learner, in contrast to eager learners like logistic regression: it does essentially no work at training time (it just stores the data) and defers all computation to prediction time, when it must search for the nearest stored points to the new query. In this opening figure, a query point (the star) has five nearest neighbors — three blue and two orange — so majority vote predicts blue. The dashed circle is not a fixed radius; it just marks whichever boundary happens to enclose exactly k=5 points for this particular query.
-->

---
glowSeed: 422
---

# The Core Idea

<div class="grid grid-cols-2 gap-7 mt-3 items-center">
<div>
<div border="2 solid teal-800" bg="teal-800/20" rounded-lg p-4>

$$N_k(x)=\text{the }k\text{ closest training points to }x$$
$$\hat y(x)=\operatorname{majority}\{y_i:x_i\in N_k(x)\}$$
$$d(x,x_i)=\|x-x_i\|_2$$

</div>

```python
from sklearn.datasets import make_classification
from sklearn.neighbors import KNeighborsClassifier

X, y = make_classification(
    n_samples=200, n_features=2,
    n_redundant=0, random_state=0)
model = KNeighborsClassifier(n_neighbors=5)
model.fit(X, y)  # stores X and y
print(model.predict_proba(X[:3]))
```
</div>
<div>
<v-clicks>

- Find neighbors using a distance metric
- Vote on their labels
- Fit is nearly free; prediction computes the distances
- The probability is the fraction of neighbors in each class

</v-clicks>
<div v-click class="mt-5 grid grid-cols-2 gap-3 text-center text-sm">
<div border="2 solid teal-800" bg="teal-800/20" rounded p-4><strong>Training</strong><br/>store examples</div>
<div border="2 solid orange-800" bg="orange-800/20" rounded p-4><strong>Prediction</strong><br/>search + vote</div>
</div>
</div>
</div>

<!--
Walk through the notation: N_k(x) is the set of the k training points closest to a query point x under some distance function d, and the prediction ŷ(x) is simply the majority class label among those k neighbors — a plurality vote, with ties conventionally broken by the class of the single nearest point or by scikit-learn's internal ordering. The default distance, Euclidean (L2) distance, is the ordinary straight-line distance between two feature vectors: the square root of the sum of squared coordinate differences.

Emphasize the reversed cost profile relative to logistic regression: calling `.fit(X, y)` on a KNeighborsClassifier does almost no work — it just stores X and y (optionally building a spatial index) — so training is nearly free. All the real computation happens at `.predict()` time, when the model must compute distances from the query point to some or all stored training points, sort them, and vote. This is the exact opposite of logistic regression, where fitting is expensive (iterative optimization over the whole dataset) but prediction is cheap — just one dot product between the learned weight vector and the query features. `predict_proba` reports, for each class, the fraction of the k neighbors that belong to it, so it is a genuine (if coarse) probability estimate, not just a hard vote.
-->

---
glowSeed: 423
---

# Choosing k Is Choosing Complexity

<div class="grid grid-cols-3 gap-4 mt-5 text-center text-sm">
<div v-click border="2 solid orange-800" bg="orange-800/20" rounded-lg p-4>
<div class="text-3xl font-bold text-orange-300">k = 1</div>
<svg role="img" aria-label="Jagged local decision boundary for one nearest neighbor" viewBox="0 0 210 145" class="w-full mt-2"><path d="M20 118 C45 25 65 130 88 55 S120 120 145 45 S170 115 195 32" fill="none" stroke="#fb923c" stroke-width="5"/><g fill="#f8fafc"><circle cx="32" cy="35" r="5"/><circle cx="65" cy="100" r="5"/><circle cx="110" cy="35" r="5"/><circle cx="165" cy="100" r="5"/></g></svg>
Low bias · high variance
</div>
<div v-click border="2 solid teal-800" bg="teal-800/20" rounded-lg p-4>
<div class="text-3xl font-bold text-teal-300">k = 15</div>
<svg role="img" aria-label="Smooth useful decision boundary for fifteen nearest neighbors" viewBox="0 0 210 145" class="w-full mt-2"><path d="M20 115 Q105 15 195 112" fill="none" stroke="#2dd4bf" stroke-width="5"/><g fill="#f8fafc"><circle cx="32" cy="35" r="5"/><circle cx="65" cy="100" r="5"/><circle cx="110" cy="35" r="5"/><circle cx="165" cy="100" r="5"/></g></svg>
Useful middle ground
</div>
<div v-click border="2 solid blue-800" bg="blue-800/20" rounded-lg p-4>
<div class="text-3xl font-bold text-blue-300">k = n</div>
<svg role="img" aria-label="Nearly constant boundary for all neighbors" viewBox="0 0 210 145" class="w-full mt-2"><line x1="20" y1="78" x2="195" y2="78" stroke="#60a5fa" stroke-width="5"/><g fill="#f8fafc"><circle cx="32" cy="35" r="5"/><circle cx="65" cy="100" r="5"/><circle cx="110" cy="35" r="5"/><circle cx="165" cy="100" r="5"/></g></svg>
Majority class everywhere
</div>
</div>

<div v-click class="mt-7 text-center text-lg" border="2 solid white/10" bg="white/5" rounded-lg p-4>Choose <code>k</code> by cross-validation. Small <code>k</code> is flexible; large <code>k</code> is smooth.</div>

<!--
Reuse the bias-variance language from earlier units, but note that the direction is opposite to polynomial degree in regression: there, larger degree means more flexibility; here, smaller k means more flexibility. At k=1, the predicted label at any point is just the label of the single closest training example, so the decision boundary snakes around to fit every training point exactly — zero bias on the training set, but very high variance, since one noisy or mislabeled point can flip the prediction for an entire neighborhood. At k=15 neighbors are averaged over a larger, more representative local neighborhood, producing a much smoother boundary that usually generalizes better.

At the extreme k=n (using every training point as a "neighbor" for every query), the vote is identical everywhere: it just returns the global majority class regardless of the query's features, which is maximum bias and zero variance — the model has stopped using x at all. As with polynomial degree, ridge/lasso lambda, and tree depth, the right value of k is a bias-variance tradeoff that should be chosen by cross-validation, not picked arbitrarily or set to a small odd number out of habit.
-->

---
glowSeed: 423.5
---

# A Worked Vote by Hand

<div class="grid grid-cols-2 gap-7 mt-3 items-center">
<div>

<div border="2 solid white/10" bg="white/5" rounded-lg p-4 class="text-sm">
Query point $q = (2, 3)$, $k = 3$
</div>

<div class="mt-3 text-sm">

| point | label | $d_2(q, x_i)$ |
|---|---|---|
| $(1, 1)$ | orange | $\sqrt{5}\approx2.24$ |
| $(3, 5)$ | blue | $\sqrt{5}\approx2.24$ |
| $(6, 2)$ | orange | $\sqrt{17}\approx4.12$ |
| $(2, 6)$ | blue | $3.00$ |

</div>

<v-clicks>

- Sort by distance: $(1,1)$, $(3,5)$, $(2,6)$, $(6,2)$
- 3 nearest neighbors: orange, blue, blue
- Majority vote: **blue** (2 of 3)

</v-clicks>

</div>

```python
import numpy as np

X = np.array([[1, 1], [3, 5], [6, 2], [2, 6]])
y = np.array(['orange', 'blue', 'orange', 'blue'])
q = np.array([2, 3])

dist = np.linalg.norm(X - q, axis=1)
order = np.argsort(dist)[:3]
neighbors = y[order]
vote = np.unique(neighbors, return_counts=True)
print(dist.round(2), neighbors, vote)
```

</div>

<!--
Make the mechanism completely concrete with real numbers before returning to the more abstract distance-metric discussion. The query is q = (2, 3). Compute Euclidean distance to each of four labeled points by hand: to (1,1), the squared differences are (2-1)^2 + (3-1)^2 = 1 + 4 = 5, so distance is sqrt(5) ≈ 2.24; to (3,5), (2-3)^2 + (3-5)^2 = 1 + 4 = 5, also sqrt(5) ≈ 2.24; to (6,2), (2-6)^2+(3-2)^2 = 16+1 = 17, so sqrt(17) ≈ 4.12; to (2,6), (2-2)^2+(3-6)^2 = 0+9 = 9, so distance is exactly 3.00.

With k=3, the three closest points are (1,1) at 2.24 (orange), (3,5) at 2.24 (blue), and (2,6) at 3.00 (blue) — (6,2) at 4.12 is excluded. That is 2 blue votes versus 1 orange vote, so the model predicts blue for this query, and predict_proba would report roughly 0.67 for blue and 0.33 for orange. Note the tie in raw distance between (1,1) and (3,5) — ties in distance are common with small integer coordinates and are broken by whatever consistent ordering the implementation uses; they rarely change the outcome once k is larger than 1.
-->

---
glowSeed: 424
---

# Distance Defines “Nearest”

<div border="2 solid white/10" bg="white/5" rounded-lg px-5 py-3>

$$d_p(x,x_i)=\left(\sum_j|x_j-x_{ij}|^p\right)^{1/p}$$

</div>

<div class="grid grid-cols-3 gap-4 mt-5 text-center text-sm">
<div v-click border="2 solid violet-800" bg="violet-800/20" rounded-lg p-3><strong>L1 · Manhattan</strong><svg role="img" aria-label="Diamond shaped L1 unit ball" viewBox="0 0 180 120" class="w-full mt-2"><path d="M90 10 L165 60 L90 110 L15 60 Z" fill="#7c3aed33" stroke="#c084fc" stroke-width="4"/></svg>Robust to coordinate-wise extremes</div>
<div v-click border="2 solid teal-800" bg="teal-800/20" rounded-lg p-3><strong>L2 · Euclidean</strong><svg role="img" aria-label="Circular L2 unit ball" viewBox="0 0 180 120" class="w-full mt-2"><ellipse cx="90" cy="60" rx="62" ry="50" fill="#0f766e33" stroke="#2dd4bf" stroke-width="4"/></svg>Most common default</div>
<div v-click border="2 solid blue-800" bg="blue-800/20" rounded-lg p-3><strong>L∞ · Chebyshev</strong><svg role="img" aria-label="Square L infinity unit ball" viewBox="0 0 180 120" class="w-full mt-2"><rect x="30" y="12" width="120" height="96" fill="#2563eb33" stroke="#60a5fa" stroke-width="4"/></svg>Largest coordinate difference</div>
</div>

<!--
The Minkowski distance $d_p$ is a family that generalizes several familiar distances with one exponent p: summing the absolute coordinate differences raised to the p-th power, then taking the p-th root. Call back to the Linear Algebra unit's discussion of vector norms and their unit balls — the shape of the "ball" of points at distance 1 from the origin literally determines which nearby points count as neighbors first. L1 (Manhattan, p=1) has a diamond-shaped unit ball, so it sums absolute coordinate differences; it is more robust to a single feature having an extreme outlier value, since it does not square (and thus amplify) large individual differences.

L2 (Euclidean, p=2) has a circular unit ball and is the most common default — it matches our everyday geometric intuition of straight-line distance but assumes the features are continuous and on comparable, meaningfully-scaled axes. L∞ (Chebyshev, p→∞) has a square unit ball and reduces to simply the single largest coordinate difference, ignoring how close the other coordinates are; it is useful when one dominant dimension of dissimilarity should determine "nearness" regardless of the others. The choice of metric is a modeling decision, not a neutral default, and connects directly to the feature-scaling warning coming up shortly.
-->

---
glowSeed: 4241
---

# Distance Metrics in scikit-learn

```python
euclidean = KNeighborsClassifier(
    n_neighbors=5, metric='minkowski', p=2
).fit(X, y)

manhattan = KNeighborsClassifier(
    n_neighbors=5, metric='minkowski', p=1
).fit(X, y)

print(euclidean.predict(X[:5]))
print(manhattan.predict(X[:5]))
```

<div class="grid grid-cols-2 gap-4 mt-6 text-center text-sm">
<div v-click border="2 solid teal-800" bg="teal-800/20" rounded-lg p-4><strong>p = 2</strong><br/>Euclidean neighborhoods</div>
<div v-click border="2 solid violet-800" bg="violet-800/20" rounded-lg p-4><strong>p = 1</strong><br/>Manhattan neighborhoods</div>
</div>

<div v-click class="mt-5 text-center opacity-80">Categorical or mixed features need Hamming or another domain-appropriate similarity.</div>

<!--
In scikit-learn, `KNeighborsClassifier`'s metric parameter defaults to `'minkowski'` with `p=2`, which is just Euclidean distance expressed as a special case of the general Minkowski family from the previous slide; setting `p=1` switches to Manhattan distance. Run both variants side by side on the same data and compare predictions for query points near a decision boundary — they will usually agree away from boundaries but can disagree right at the margin, which is a concrete demonstration that the metric is a real modeling choice affecting predictions, not a harmless implementation detail that can be left at its default without thought.

Plain Euclidean or Manhattan distance is inappropriate for raw categorical variables, since there is no meaningful numeric "distance" between, say, categories "red" and "blue" encoded as arbitrary integers — subtracting category codes produces numbers with no real geometric meaning. For categorical or mixed feature types, use Hamming distance (counts mismatched categorical attributes) for purely categorical data, or a domain-appropriate composite/similarity measure — such as Gower's distance — that combines numeric and categorical parts sensibly for mixed feature sets.
-->

---
glowSeed: 425
---

# The Curse of Dimensionality

<div class="grid grid-cols-2 gap-7 mt-3 items-center">
<div>
<v-clicks>

- k-NN assumes nearby points have similar labels
- High-dimensional points spread out and become roughly equidistant
- “Nearest” loses meaning as $d$ grows
- Feature selection or dimensionality reduction can restore useful neighborhoods

</v-clicks>
<div v-click border="2 solid orange-800" bg="orange-800/20" rounded-lg p-4 class="mt-5">

$$\frac{d_{nearest}}{d_{farthest}}\longrightarrow1\quad\text{as }d\to\infty$$

</div>
</div>
<div>
<svg role="img" aria-label="Nearest to farthest distance ratio rises toward one as dimensions increase" viewBox="0 0 460 285" class="w-full">
  <line x1="45" y1="245" x2="430" y2="245" stroke="#64748b"/><line x1="45" y1="245" x2="45" y2="25" stroke="#64748b"/>
  <line x1="45" y1="45" x2="430" y2="45" stroke="#60a5fa" stroke-dasharray="6 5"/><text x="15" y="50" fill="#94a3b8">1</text>
  <path d="M55 215 C105 180 135 130 190 92 C245 58 320 48 420 46" fill="none" stroke="#fb923c" stroke-width="5"/>
  <circle cx="75" cy="200" r="6" fill="#f8fafc"/><circle cx="160" cy="110" r="6" fill="#f8fafc"/><circle cx="285" cy="55" r="6" fill="#f8fafc"/><circle cx="410" cy="47" r="6" fill="#f8fafc"/>
  <text x="160" y="275" fill="#94a3b8">dimensions</text>
</svg>

```python
rng = np.random.default_rng(0)
for d in [2, 10, 100, 1000]:
    points = rng.uniform(0, 1, (1000, d))
    query = rng.uniform(0, 1, d)
    dist = np.linalg.norm(points-query, axis=1)
    print(d, dist.min()/dist.max())
```
</div>
</div>

<!--
k-NN's entire premise rests on one assumption: points that are close in feature space have similar labels. The curse of dimensionality is the empirical and theoretical fact that this assumption quietly breaks down as the number of features d grows. Run the simulation in the code block and watch the ratio of the nearest point's distance to the farthest point's distance climb toward 1 as d increases from 2 to 1000 — in high dimensions, essentially all points become roughly equidistant from any query, so "nearest" stops carrying useful information about similarity.

The geometric intuition: in high-dimensional space, the volume of a hypersphere concentrates overwhelmingly near its outer shell rather than near its center, so randomly distributed points end up scattered close to the boundary of whatever region contains them, and pairwise distances become dominated by many small, roughly-independent per-coordinate contributions that average out to similar totals. This is a genuine practical failure mode, not a theoretical curiosity — k-NN on hundreds of raw features often performs worse than on a handful of well-chosen ones. Preview two remedies covered elsewhere in the course: feature selection, which discards uninformative features outright, and PCA (dimensionality reduction), which projects onto a lower-dimensional subspace that preserves the directions of greatest variance while discarding much of the noise that inflates distances.
-->

---
glowSeed: 426
---

# Feature Scaling Is Essential

<div class="grid grid-cols-2 gap-7 mt-4 items-center">
<svg role="img" aria-label="Unscaled features stretch one axis while standardized features balance both axes" viewBox="0 0 500 300" class="w-full">
  <g transform="translate(20,30)"><rect width="210" height="220" rx="10" fill="#7c2d1233" stroke="#fb923c"/><text x="62" y="-8" fill="#fdba74">unscaled</text><g fill="#f8fafc"><circle cx="20" cy="55" r="5"/><circle cx="55" cy="65" r="5"/><circle cx="105" cy="70" r="5"/><circle cx="170" cy="62" r="5"/><circle cx="195" cy="75" r="5"/></g><text x="35" y="205" fill="#94a3b8">income dominates →</text></g>
  <g transform="translate(270,30)"><rect width="210" height="220" rx="10" fill="#0f766e33" stroke="#2dd4bf"/><text x="72" y="-8" fill="#5eead4">scaled</text><g fill="#f8fafc"><circle cx="45" cy="175" r="5"/><circle cx="65" cy="115" r="5"/><circle cx="105" cy="70" r="5"/><circle cx="155" cy="95" r="5"/><circle cx="175" cy="45" r="5"/></g><text x="46" y="205" fill="#94a3b8">both axes matter</text></g>
</svg>
<div>
<v-clicks>

- Distance is dominated by the largest numeric scale
- k-NN has no learned weight that can compensate
- Standardize inside a pipeline so each CV fold fits its own scaler

</v-clicks>

```python
from sklearn.pipeline import make_pipeline
from sklearn.preprocessing import StandardScaler

model = make_pipeline(
    StandardScaler(),
    KNeighborsClassifier(n_neighbors=5)
)
model.fit(X, y)
```
</div>
</div>

<!--
This is the single most important practical warning in this deck: always scale k-NN inputs unless the metric and units have been deliberately designed otherwise. Because distance sums contributions from every feature, a feature measured on a large numeric scale, such as income in dollars, will completely dominate the distance calculation compared to a feature on a small scale, such as age in years, even if age is actually more predictive. Unlike logistic regression or linear regression, k-NN has no learned per-feature weight that could automatically down-weight the oversized feature — every raw coordinate contributes with equal, unlearned influence to the distance, so scaling is not optional polish, it is required for the model to work as intended.

Standardizing (subtracting the mean and dividing by the standard deviation, via `StandardScaler`) puts every feature on a comparable scale before distances are computed. Wrap the scaler and the classifier in a single `Pipeline`, and fit that pipeline within cross-validation, so that each fold computes its own mean and standard deviation from only its training portion — fitting the scaler once on the full dataset before splitting would leak information from the validation fold into training, silently inflating the reported cross-validation score.
-->

---
glowSeed: 427
---

# Cheap Fit, Expensive Prediction

<div class="grid grid-cols-2 gap-7 mt-4">
<div>
<div class="grid grid-cols-[8rem_1fr_1fr] gap-2 text-center text-sm">
<div></div><div class="font-bold text-teal-300">fit</div><div class="font-bold text-orange-300">predict</div>
<div class="text-right pr-2">k-NN</div><div class="rounded bg-teal-500/20 p-3">store</div><div class="rounded bg-orange-500/40 p-3"><code>O(nd)</code></div>
<div class="text-right pr-2">logistic</div><div class="rounded bg-teal-500/40 p-3">optimize</div><div class="rounded bg-orange-500/20 p-3">dot product</div>
</div>
<v-clicks>

- Keep the whole training set in memory
- KD-trees and ball trees help in low/moderate dimension
- k-NN regression averages neighbor targets instead of voting

</v-clicks>
</div>

```python
from sklearn.neighbors import KNeighborsRegressor
import time

model = KNeighborsClassifier(
    n_neighbors=5, algorithm='kd_tree'
).fit(X, y)
start = time.perf_counter()
model.predict(X)
print(time.perf_counter() - start)

regressor = KNeighborsRegressor(n_neighbors=5)
```
</div>

<!--
Use the small table to crystallize the deployment tradeoff: for k-NN, fitting is essentially free (just store the data) but each prediction costs O(nd) in the naive case — comparing the query to all n stored points across d features — whereas logistic regression pays an expensive iterative optimization cost once at training time but then predicts with a single cheap dot product. If a system needs to serve millions of low-latency predictions per second, a compressed parametric model like logistic regression, or a tree, is usually the better production choice; k-NN is more attractive when training data changes frequently and retraining a parametric model would be inconvenient, or when the interpretability of "here are the similar past cases" is itself valuable.

Mention spatial index structures briefly — KD-trees and ball trees, both available via scikit-learn's `algorithm` parameter — which can speed up nearest-neighbor search substantially in low-to-moderate dimensions by avoiding a full linear scan over every stored point, though their benefit erodes in high dimensions for the same curse-of-dimensionality reasons discussed earlier; their internal mechanics are out of scope for this course. Note also that `KNeighborsRegressor` is the direct regression counterpart: instead of a majority vote among the k nearest neighbors' labels, it averages the k nearest neighbors' numeric target values.
-->

---
layout: center
class: text-center
glowSeed: 428
---

# k-NN in One View

<div class="grid grid-cols-2 gap-4 mt-7 text-left">
<div v-click border="2 solid teal-800" bg="teal-800/20" rounded-lg p-5><strong>Rule</strong><div class="text-sm opacity-80 mt-2">vote among the k nearest stored examples</div></div>
<div v-click border="2 solid blue-800" bg="blue-800/20" rounded-lg p-5><strong>Complexity</strong><div class="text-sm opacity-80 mt-2">small k flexes; large k smooths</div></div>
<div v-click border="2 solid violet-800" bg="violet-800/20" rounded-lg p-5><strong>Geometry</strong><div class="text-sm opacity-80 mt-2">metric and scaling define “near”</div></div>
<div v-click border="2 solid orange-800" bg="orange-800/20" rounded-lg p-5><strong>Caveat</strong><div class="text-sm opacity-80 mt-2">high dimensions and large n make prediction hard</div></div>
</div>

<div v-click class="mt-8 text-lg">Next: <strong>Naive Bayes</strong> — a generative classifier built directly from Bayes’ theorem.</div>

<!--
Close the contrast this deck built up: logistic regression is optimization-based, learning a fixed, compact set of weights by minimizing a loss function, while k-NN is instance-based memorization, storing the raw training set and deferring all work to prediction time. Both are valid ways to draw a decision boundary, but they trade off differently on interpretability of the model itself, training cost, prediction cost, and sensitivity to feature scaling and dimensionality — remind students that misconception check: k-NN being simple to describe does not mean it is simple to deploy well, since scaling and dimensionality both require active management.

Preview the third strategy in this module, generative probability, in the next deck on Naive Bayes: rather than drawing a boundary directly (discriminative, like logistic regression) or relying on geometric proximity (instance-based, like k-NN), a generative classifier models how each class produces its features and then inverts that model with Bayes' theorem — the direct return of the Bayes'-rule machinery introduced in the probability unit — to decide which class most likely generated a given observation.
-->
