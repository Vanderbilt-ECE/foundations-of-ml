---
theme: default
highlighter: shiki
css: unocss
colorSchema: dark
title: 'k-Means and Hierarchical Clustering'
info: |
  ## k-Means and Hierarchical Clustering
  Find groups when no labels define the answer
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
glowSeed: 710
---

# k-Means and Hierarchical Clustering

### Find groups when no labels define the answer

<div class="pt-8 opacity-80 text-lg">Unsupervised Learning · Foundations of Machine Learning</div>

<div class="mt-14 flex justify-center gap-4" aria-hidden="true">
<div class="w-28 h-3 rounded-full bg-teal-400/70"></div>
<div class="w-20 h-3 rounded-full bg-blue-400/60"></div>
<div class="w-14 h-3 rounded-full bg-violet-400/50"></div>
</div>

<!--
This deck opens the Unsupervised Learning unit. Everything before this point in the course — regression, classification, ensembles — assumed a labeled target y that the model was trained to predict. Clustering removes that label entirely: we are given only a design matrix X of feature vectors and asked to discover groups that make the data easier to describe, summarize, or act on. There is no ground-truth "correct" clustering to check against, which is the central methodological difference from everything covered so far, and it will resurface every time we ask "how do I know K is right?"

Roadmap for today: define the k-means objective and show it is a well-posed optimization problem, derive Lloyd's algorithm as coordinate descent on that objective, discuss why initialization matters and how k-means++ fixes it, cover how to choose K without labels (elbow, silhouette), catalog the geometric assumptions that make k-means fail, then pivot to hierarchical clustering as an alternative that trades speed for a full multi-resolution tree. This deck ends by handing off to PCA and t-SNE/UMAP, which are often used as a preprocessing step before clustering high-dimensional data.
-->

---
glowSeed: 711
---

# The k-Means Objective

<div class="grid grid-cols-2 gap-8 items-start">
<div>
<div class="space-y-3 mt-4">
<div v-click border="2 solid white/5" bg="white/5" rounded-lg px-4 py-3>
<span class="font-bold text-teal-300">Partition</span>
<span class="text-sm opacity-85"> — Assign n observations to K clusters.</span>
</div>
<div v-click border="2 solid white/5" bg="white/5" rounded-lg px-4 py-3>
<span class="font-bold text-blue-300">Centroids</span>
<span class="text-sm opacity-85"> — Represent each cluster by its mean.</span>
</div>
<div v-click border="2 solid white/5" bg="white/5" rounded-lg px-4 py-3>
<span class="font-bold text-amber-300">Loss without labels</span>
<span class="text-sm opacity-85"> — Minimize squared distance to the assigned centroid.</span>
</div>
</div>
</div>
<div>
<div v-click class="mt-4" style="font-size: .9em" border="2 solid teal-800" bg="teal-800/20" rounded-lg px-4 py-3>

$$
J=\sum_{i=1}^n\lVert x_i-\mu_{c_i}\rVert_2^2
$$

</div>

</div>
</div>

<!--
Define every symbol before moving on: x_i is the i-th data point (a vector in R^d), c_i in {1,...,K} is the cluster label we assign to point i, and mu_k is the centroid — the representative vector — of cluster k. J is the "within-cluster sum of squares" (WCSS), also called inertia in scikit-learn's documentation: sum over every point of its squared Euclidean distance to whichever centroid it is assigned to.

The key difficulty, worth pausing on: J has two different kinds of unknowns tangled together. The assignments c_i are discrete (which of K buckets does each point go in) and the centroids mu_k are continuous (real-valued vectors). Jointly minimizing over both simultaneously is NP-hard in general — there is no closed-form global solution. The trick that makes k-means tractable is to notice that if you FIX one kind of variable, minimizing over the other becomes an easy, closed-form problem: fix the centroids and the best assignment for each point is "nearest centroid" (a simple comparison); fix the assignments and the best centroid for each cluster is the mean of its points (we derive this on the next slide). Alternating between these two easy sub-problems is exactly Lloyd's algorithm, which the next slide formalizes. This pattern — alternate between two easy conditional optimizations when the joint problem is hard — is the same idea behind the EM algorithm you will see in the Gaussian Mixture Models deck; k-means is literally a special case of EM.
-->

---
glowSeed: 900
---

# Why the Mean? A Quick Derivation

<div class="grid grid-cols-2 gap-8 items-start">
<div>
<div class="space-y-3 mt-4">
<div v-click border="2 solid white/5" bg="white/5" rounded-lg px-4 py-3>
<span class="font-bold text-teal-300">Fix the assignments</span>
<span class="text-sm opacity-85"> — For cluster k, treat the point set $C_k$ as given.</span>
</div>
<div v-click border="2 solid white/5" bg="white/5" rounded-lg px-4 py-3>
<span class="font-bold text-blue-300">Differentiate and set to zero</span>
<span class="text-sm opacity-85"> — The unique minimizer of a sum of squared distances is the mean.</span>
</div>
<div v-click border="2 solid white/5" bg="white/5" rounded-lg px-4 py-3>
<span class="font-bold text-amber-300">Total variance splits in two</span>
<span class="text-sm opacity-85"> — Total sum of squares = within-cluster SS + between-cluster SS, a fixed constant.</span>
</div>
</div>
</div>
<div>
<div v-click class="mt-4" style="font-size: .85em" border="2 solid teal-800" bg="teal-800/20" rounded-lg px-4 py-3>

$$
\begin{aligned}
\frac{\partial}{\partial \mu_k}\sum_{i\in C_k}\lVert x_i-\mu_k\rVert^2 &= -2\sum_{i\in C_k}(x_i-\mu_k)=0\\
\Rightarrow\quad \mu_k &= \frac{1}{|C_k|}\sum_{i\in C_k} x_i
\end{aligned}
$$

</div>
<div v-click class="mt-4 text-sm opacity-85">
Because $TSS$ is fixed by the data, minimizing within-cluster SS is exactly equivalent to maximizing between-cluster SS — k-means pushes clusters apart precisely as much as it pulls each cluster's points together.
</div>
</div>
</div>

<!--
This slide answers a question students often skip past: why does "update" mean "recompute the mean" and not, say, the median or some other summary? The answer follows directly from the squared-Euclidean form of the objective J. If we hold the cluster assignments C_k fixed, J splits into K independent sub-problems, one per cluster, because a point's distance to its own centroid never involves any other cluster's centroid. Take the derivative of the k-th sub-problem's sum of squared distances with respect to mu_k, and set it to zero: the sum of the residuals must vanish, which rearranges directly to "mu_k equals the arithmetic mean of the points in cluster k." This is a genuine convex least-squares problem for each fixed assignment, and it has a unique closed-form solution — no iteration or search needed for the update step, only for alternating between assign and update.

Second point: recall the classical statistics identity TSS = WSS + BSS (total sum of squares equals within-cluster sum of squares plus between-cluster sum of squares), where TSS = sum of squared distances of every point to the GLOBAL mean, a number that does not depend on the clustering at all — it is fixed by the dataset. Since TSS is constant, minimizing WSS (which is exactly J) is mathematically identical to maximizing BSS, the spread between cluster centers. This is why k-means clusters end up well-separated as a side effect of minimizing within-cluster compactness: the two goals are two sides of the same coin, not separate objectives someone had to balance.

Common misconception to flag explicitly: this derivation assumes squared Euclidean distance. If you swap in a different distance metric (e.g., Manhattan/L1 distance, or cosine distance), the optimal "center" is no longer the mean — for L1 distance the minimizer is the coordinate-wise median instead. That variant is called k-medians. k-means is tied to squared Euclidean distance specifically because that is the metric for which the mean is provably optimal.
-->

---
glowSeed: 712
---

# Lloyd’s Algorithm Alternates Two Easy Steps

<div class="grid grid-cols-2 gap-8 items-start">
<div>
<div class="space-y-3 mt-4">
<div v-click border="2 solid white/5" bg="white/5" rounded-lg px-4 py-3>
<span class="font-bold text-teal-300">Assign</span>
<span class="text-sm opacity-85"> — Send each point to its nearest centroid.</span>
</div>
<div v-click border="2 solid white/5" bg="white/5" rounded-lg px-4 py-3>
<span class="font-bold text-blue-300">Update</span>
<span class="text-sm opacity-85"> — Move each centroid to the mean of its assigned points.</span>
</div>
<div v-click border="2 solid white/5" bg="white/5" rounded-lg px-4 py-3>
<span class="font-bold text-amber-300">Repeat</span>
<span class="text-sm opacity-85"> — J never increases, so the process converges to a local optimum.</span>
</div>
</div>
</div>
<div>
<div class="mt-5" role="img" aria-label="Initialize μ then Assign cᵢ then Update μ then Converged?">
<div v-click class="flex items-center gap-3">
<div class="w-8 h-8 rounded-full bg-teal-500/20 border-2 border-teal-700 flex items-center justify-center text-sm font-bold">1</div>
<div class="flex-1 rounded-lg border-2 border-white/10 bg-white/5 px-3 py-2 text-sm font-bold">Initialize μ</div>
</div>
<div class="ml-4 h-1 border-l-2 border-teal-400/50"></div>
<div v-click class="flex items-center gap-3">
<div class="w-8 h-8 rounded-full bg-blue-500/20 border-2 border-blue-700 flex items-center justify-center text-sm font-bold">2</div>
<div class="flex-1 rounded-lg border-2 border-white/10 bg-white/5 px-3 py-2 text-sm font-bold">Assign cᵢ</div>
</div>
<div class="ml-4 h-1 border-l-2 border-teal-400/50"></div>
<div v-click class="flex items-center gap-3">
<div class="w-8 h-8 rounded-full bg-amber-500/20 border-2 border-amber-700 flex items-center justify-center text-sm font-bold">3</div>
<div class="flex-1 rounded-lg border-2 border-white/10 bg-white/5 px-3 py-2 text-sm font-bold">Update μ</div>
</div>
<div class="ml-4 h-1 border-l-2 border-teal-400/50"></div>
<div v-click class="flex items-center gap-3">
<div class="w-8 h-8 rounded-full bg-violet-500/20 border-2 border-violet-700 flex items-center justify-center text-sm font-bold">4</div>
<div class="flex-1 rounded-lg border-2 border-white/10 bg-white/5 px-3 py-2 text-sm font-bold">Converged?</div>
</div>
</div>
<div v-click class="mt-4" style="font-size: .9em" border="2 solid teal-800" bg="teal-800/20" rounded-lg px-4 py-3>

$$
c_i\leftarrow\arg\min_k\lVert x_i-\mu_k\rVert^2,\quad \mu_k\leftarrow\frac1{|C_k|}\sum_{i\in C_k}x_i
$$

</div>
</div>
</div>

<!--
Walk the four-step loop explicitly. Step 1, initialize: pick K starting centroids, typically by sampling K points from the data (naive) or via k-means++ (the next slide). Step 2, assign: for every point, compute its distance to all K centroids and label it with the nearest one — this is the closed-form solution to "minimize J over assignments, holding centroids fixed" that we get for free because Euclidean distance makes "nearest" the same as "argmin squared distance." Step 3, update: recompute each centroid as the mean of the points currently assigned to it — this is exactly the derivation from the previous slide, "minimize J over centroids, holding assignments fixed." Step 4, check convergence: if no point changed its assignment (or centroids moved by less than some tiny tolerance), stop; otherwise go back to step 2.

The critical correctness argument: J can never increase from one full iteration to the next. The assign step can only decrease or hold J constant, because every point is being reassigned to a provably closer (or equal) centroid than before. The update step can only decrease or hold J constant, because we just proved the mean is the unique minimizer of the sum of squared distances for a fixed assignment. Since J is monotonically non-increasing and bounded below by zero, the algorithm is guaranteed to converge in a finite number of steps (there are only finitely many possible assignments of n points to K clusters).

Crucial misconception to name directly: convergence to A local optimum is guaranteed; convergence to THE global optimum is not. The k-means objective J is non-convex in the joint (assignment, centroid) space, so Lloyd's algorithm can get stuck in a local minimum that depends entirely on where it started. This motivates the very next slide.
-->

---
glowSeed: 901
---

# Worked Example: One Full Iteration

<div class="text-sm">

**Data (6 points, K = 2):** $(1,2),\ (1.5,1.8),\ (5,8),\ (8,8),\ (1,0.6),\ (9,11)$ &nbsp;&nbsp; **Initial centroids:** $\mu_1=(1,2)$, $\mu_2=(5,8)$

<div class="grid grid-cols-2 gap-8 items-start mt-4">
<div v-click>

**Assign** — nearest centroid by distance:

| point | to $\mu_1$ | to $\mu_2$ | assign |
|---|---|---|---|
| (1, 2) | 0 | 7.21 | 1 |
| (1.5, 1.8) | 0.54 | 7.12 | 1 |
| (5, 8) | 7.21 | 0 | 2 |
| (8, 8) | 9.22 | 3.00 | 2 |
| (1, 0.6) | 1.40 | 8.41 | 1 |
| (9, 11) | 12.04 | 5.00 | 2 |

</div>
<div>

<div v-click border="2 solid teal-800" bg="teal-800/20" rounded-lg px-4 py-3 style="font-size: .9em">

**Update** — recompute means:

$$
\mu_1=\tfrac13\big[(1,2)+(1.5,1.8)+(1,0.6)\big]=(1.17,\,1.47)
$$

$$
\mu_2=\tfrac13\big[(5,8)+(8,8)+(9,11)\big]=(7.33,\,9.00)
$$

</div>

<div v-click class="mt-3 text-xs opacity-85">
$J$ after this update $\approx 15.98$. One more assign/update pass would move $\mu_1,\mu_2$ only slightly — this problem is close to convergence after a single iteration.
</div>

</div>
</div>
</div>

<!--
Every number on this slide was computed with numpy and verified, not hand-arithmetic: distances via the Euclidean norm formula, means via straightforward averaging. Walk through row one as a sanity check: the point (1,2) IS mu_1 exactly, so its distance to mu_1 is zero and it obviously gets assigned to cluster 1. Walk through (8,8): distance to mu_1=(1,2) is sqrt(7^2+6^2)=sqrt(85)=9.22, distance to mu_2=(5,8) is sqrt(3^2+0^2)=3.00, so it goes to cluster 2 despite being much closer numerically to cluster 2's original seed than cluster 1's.

After assignment, recompute each centroid as the plain average of its members' coordinates — this is the closed-form update derived two slides ago. Point out that the new centroids have moved toward the "center of mass" of their assigned points and away from the arbitrary initial seeds, which is the whole mechanism by which k-means refines an initial guess into a locally optimal partition. If this were a live demo, running a second assign/update pass on these six points would reassign no points (the two clusters are well-separated and already stable), which is what convergence looks like concretely: the loop exits because step 4's convergence check finds no assignment changed.
-->

---
glowSeed: 713
---

# Initialization Changes the Answer

<div class="grid grid-cols-3 gap-4 mt-6">
<div v-click border="2 solid teal-800" bg="teal-800/20" rounded-lg p-4>
<div class="font-bold text-teal-300 mb-2">Single random start</div>
<div class="text-sm leading-relaxed opacity-90">Centroids can crowd one region and settle in a poor local optimum.</div>
</div>
<div v-click border="2 solid blue-800" bg="blue-800/20" rounded-lg p-4>
<div class="font-bold text-blue-300 mb-2">Multiple restarts</div>
<div class="text-sm leading-relaxed opacity-90">Keep the run with the smallest final inertia.</div>
</div>
<div v-click border="2 solid amber-800" bg="amber-800/20" rounded-lg p-4>
<div class="font-bold text-amber-300 mb-2">k-means++</div>
<div class="text-sm leading-relaxed opacity-90">Favor initial centroids far from those already selected.</div>
</div>
</div>

<div v-click class="mt-6 text-sm" border="2 solid white/5" bg="white/5" rounded-lg px-4 py-3>
k-means++ mechanics: pick the first centroid uniformly at random from the data. For every subsequent centroid, compute $D(x)$, the distance from each point $x$ to the <em>nearest centroid chosen so far</em>, then sample the next centroid with probability proportional to $D(x)^2$ — points far from existing centroids are much more likely to be picked, but it is still random, not a deterministic "pick the farthest point."
</div>

<!--
Because Lloyd's algorithm only guarantees a local optimum, the initial centroid positions determine which local optimum you land in. A single random start can put two or more initial centroids inside the same true cluster, leaving another true cluster with no nearby centroid at all — the algorithm then converges having merged one real cluster's territory across two centroids and split another cluster's members between the wrong ones. This is a systematic failure mode, not a rare edge case, especially as K grows.

Two mitigations, and know the difference. "Multiple restarts" (scikit-learn's default n_init) means literally rerunning the whole assign/update loop from several independent random initializations and keeping whichever final result has the lowest J — brute-force but effective, and this is what makes k-means practically reliable despite the non-convexity.

k-means++ is a smarter INITIALIZATION scheme, not a replacement for Lloyd's algorithm — you still run the same assign/update loop afterward, just starting from better seeds. The mechanics: choose the first centroid uniformly at random, then for each remaining centroid, compute D(x)^2 (squared distance from each unassigned point to its nearest already-chosen centroid) and sample the next centroid proportional to that quantity. Points already close to an existing centroid have tiny D(x)^2 and are unlikely to be picked again; points far from every existing centroid have large D(x)^2 and are preferentially selected. This spreads the initial centroids across the data's actual spatial extent, which provably gives an expected approximation ratio of O(log K) relative to the optimal clustering — a real theoretical guarantee, not just a heuristic. scikit-learn's KMeans uses k-means++ by default (init='k-means++'), typically combined with n_init multiple restarts for extra robustness.
-->

---
glowSeed: 714
---

# Choosing K Without Labels

<div class="grid grid-cols-2 gap-8 items-start">
<div>
<div class="space-y-3 mt-4">
<div v-click border="2 solid white/5" bg="white/5" rounded-lg px-4 py-3>
<span class="font-bold text-teal-300">Elbow</span>
<span class="text-sm opacity-85"> — Inertia always falls; look for diminishing returns.</span>
</div>
<div v-click border="2 solid white/5" bg="white/5" rounded-lg px-4 py-3>
<span class="font-bold text-blue-300">Silhouette</span>
<span class="text-sm opacity-85"> — Reward tight clusters that are separated from their nearest neighbor cluster.</span>
</div>
<div v-click border="2 solid white/5" bg="white/5" rounded-lg px-4 py-3>
<span class="font-bold text-amber-300">No oracle</span>
<span class="text-sm opacity-85"> — These are structural diagnostics, not ground-truth accuracy.</span>
</div>
</div>
</div>
<div>
<svg role="img" aria-label="Inertia decreases monotonically with K while silhouette score peaks at K=3" viewBox="0 0 500 310" class="w-full max-w-xl mx-auto mt-7">
  <line x1="55" y1="260" x2="470" y2="260" stroke="#64748b" stroke-width="2"/><line x1="55" y1="35" x2="55" y2="260" stroke="#64748b" stroke-width="2"/>
  <path d="M65 60 C110 80,120 95,163 110 S220 135,261 150 S320 170,359 185 S420 200,457 215" fill="none" stroke="#2dd4bf" stroke-width="5"/>
  <path d="M65 150 C100 110,130 90,163 90 S220 110,261 130 S320 150,359 170 S420 185,457 200" fill="none" stroke="#60a5fa" stroke-width="4" stroke-dasharray="9 7"/>
  <g fill="#f59e0b"><circle cx="65" cy="150" r="6"/><circle cx="163" cy="90" r="7"/><circle cx="261" cy="130" r="6"/><circle cx="359" cy="170" r="6"/><circle cx="457" cy="200" r="6"/></g>
  <g fill="#cbd5e1" style="font-size: 12px" text-anchor="middle"><text x="65" y="285">2</text><text x="163" y="285">3</text><text x="261" y="285">4</text><text x="359" y="285">5</text><text x="457" y="285">6</text></g>
  <g style="font-size: 12px"><text x="335" y="52" fill="#5eead4">inertia (always falls)</text><text x="70" y="75" fill="#93c5fd">silhouette (peaks at K=3)</text></g>
</svg>
<div v-click class="mt-4" style="font-size: .9em" border="2 solid teal-800" bg="teal-800/20" rounded-lg px-4 py-3>

$$
s(i)=\frac{b(i)-a(i)}{\max(a(i),b(i))}
$$

</div>
</div>
</div>

<!--
Define the silhouette formula explicitly. For a point i, a(i) is its mean distance to every other point in its OWN cluster (a measure of cohesion — smaller is better), and b(i) is its mean distance to every point in the nearest OTHER cluster (a measure of separation — larger is better). s(i) = (b(i) - a(i)) / max(a(i), b(i)) ranges from -1 to +1: close to +1 means the point sits comfortably inside a tight, well-separated cluster; close to 0 means it sits near a cluster boundary; negative means it is probably in the wrong cluster entirely (closer on average to a different cluster than its own). The silhouette SCORE for a candidate K is the mean of s(i) across all points, and unlike inertia it is comparable across different values of K.

Elbow method: inertia (J, the k-means objective from earlier) is mathematically guaranteed to be non-increasing as K grows — with K = n (one cluster per point) inertia hits exactly zero. So you cannot simply pick the K that minimizes inertia; you look for the "elbow," the K after which adding more clusters buys only a small further reduction, on the reasoning that additional clusters beyond the true structure are splitting real clusters rather than finding new ones. The elbow is often visually ambiguous, which is the chart's main weakness.

Silhouette avoids this problem because it directly measures cluster quality (cohesion vs. separation) rather than a quantity that trivially improves with more parameters, so it CAN have a genuine interior maximum, shown here peaking at K=3. Prefer silhouette when the elbow is unclear, and always sanity-check both against domain knowledge — neither method knows the "true" number of clusters if the data was not generated by well-separated clusters in the first place; they are structural diagnostics, not proof of a correct answer. In scikit-learn, `silhouette_score(X, labels)` computes this directly.
-->

---
glowSeed: 715
---

# Where k-Means Fails

<div class="grid grid-cols-2 gap-4 mt-6">
<div v-click border="2 solid teal-800" bg="teal-800/20" rounded-lg p-4>
<div class="font-bold text-teal-300 mb-2">Nonconvex shapes</div>
<div class="text-sm leading-relaxed opacity-90">One centroid cannot represent a curved cluster.</div>
</div>
<div v-click border="2 solid blue-800" bg="blue-800/20" rounded-lg p-4>
<div class="font-bold text-blue-300 mb-2">Unequal sizes</div>
<div class="text-sm leading-relaxed opacity-90">Euclidean partitions can steal points from a larger cluster.</div>
</div>
<div v-click border="2 solid amber-800" bg="amber-800/20" rounded-lg p-4>
<div class="font-bold text-amber-300 mb-2">Outliers</div>
<div class="text-sm leading-relaxed opacity-90">Means and squared distance are not robust.</div>
</div>
<div v-click border="2 solid violet-800" bg="violet-800/20" rounded-lg p-4>
<div class="font-bold text-violet-300 mb-2">Unscaled features</div>
<div class="text-sm leading-relaxed opacity-90">Large numeric ranges dominate distance.</div>
</div>
</div>


<!--
Every failure mode here traces back to one root cause: k-means implicitly assumes clusters are convex, roughly spherical, similarly sized, and measured in a space where Euclidean distance is meaningful. State this as the single unifying misconception to correct — students often think of k-means as a general-purpose clustering tool, but it is really "fit K spherical Gaussians with equal, isotropic variance and hard-assign," which is a strong geometric assumption in disguise (this connects directly forward to the GMM deck, where relaxing exactly this assumption is the entire point).

Nonconvex shapes: two concentric rings or two interleaved crescents cannot be separated by nearest-centroid boundaries, because nearest-centroid partitions are always convex regions (specifically, a Voronoi diagram) — no placement of centroids can carve out a ring shape.

Unequal sizes / unequal spread: if one true cluster is large and diffuse and another is small and tight, squared Euclidean distance to a centroid can pull boundary points from the big cluster into the small one's centroid's "territory," because the big cluster's own points are, on average, farther from its own centroid.

Outliers: because the update step averages, and squared distance is used in the objective, a single far-away point can pull a centroid noticeably off its cluster's true center — the same lack of robustness that makes the mean (versus the median) sensitive to outliers in basic statistics.

Unscaled features: if one feature is measured in the thousands (e.g., income in dollars) and another in single digits (e.g., years of education), Euclidean distance is dominated by the large-scale feature almost entirely, so k-means clusters mostly on that one dimension. The fix is the same StandardScaler / normalization discipline used everywhere else in the course, and it belongs inside a pipeline before KMeans, never applied by leaking test-set statistics into the scaler.
-->

---
glowSeed: 902
---

# k-Means in scikit-learn

<div class="grid grid-cols-2 gap-4 mt-6">
<div v-click border="2 solid teal-800" bg="teal-800/20" rounded-lg p-4>
<div class="font-bold text-teal-300 mb-2">Pipeline</div>
<div class="text-sm leading-relaxed opacity-90">Scale features, then cluster — distance-based methods need comparable units.</div>
</div>
<div v-click border="2 solid blue-800" bg="blue-800/20" rounded-lg p-4>
<div class="font-bold text-blue-300 mb-2">Model selection</div>
<div class="text-sm leading-relaxed opacity-90">Sweep K, score each fit with silhouette, keep the best.</div>
</div>
</div>

```python {all|1-2|4-8|10-13}
from sklearn.cluster import KMeans
from sklearn.metrics import silhouette_score
from sklearn.pipeline import make_pipeline
from sklearn.preprocessing import StandardScaler

pipe = make_pipeline(StandardScaler(), KMeans(n_clusters=3, init="k-means++",
                                               n_init=10, random_state=0))
labels = pipe.fit_predict(X)

X_scaled = StandardScaler().fit_transform(X)
for k in range(2, 7):
    km = KMeans(n_clusters=k, init="k-means++", n_init=10, random_state=0)
    labs = km.fit_predict(X_scaled)
    print(k, silhouette_score(X_scaled, labs), km.inertia_)
```

<!--
Run this live if possible. Two habits to make explicit: (1) StandardScaler before KMeans inside a Pipeline — this is not optional cosmetics, it directly fixes the "unscaled features dominate distance" failure mode from the previous slide, and wrapping both steps in a Pipeline means fit_predict calls fit_transform on the scaler and fit on the clusterer together, so if this pipeline is later used inside cross-validation, the scaler's mean/variance are refit on each training fold rather than leaking test-set statistics. (2) init="k-means++" with n_init=10 (scikit-learn's historical default was n_init=10; more recent versions default to "auto") — this is the practical combination of the two initialization fixes from two slides ago: smart seeding plus multiple restarts.

The loop demonstrates the elbow/silhouette workflow concretely: for each candidate K, fit and record both inertia (which will only ever decrease as K increases) and silhouette score (which can peak at the true K). In a live run, watch inertia decrease monotonically while silhouette rises, peaks, then falls — reproducing the shape of the chart on the previous slide with real numbers.
-->

---
glowSeed: 716
---

# Hierarchical Clustering Builds a Dendrogram

<div class="grid grid-cols-2 gap-8 items-start">
<div>
<div class="space-y-3 mt-4">
<div v-click border="2 solid white/5" bg="white/5" rounded-lg px-4 py-3>
<span class="font-bold text-teal-300">Bottom up</span>
<span class="text-sm opacity-85"> — Start with one cluster per point.</span>
</div>
<div v-click border="2 solid white/5" bg="white/5" rounded-lg px-4 py-3>
<span class="font-bold text-blue-300">Merge</span>
<span class="text-sm opacity-85"> — Repeatedly combine the closest pair under a linkage rule.</span>
</div>
<div v-click border="2 solid white/5" bg="white/5" rounded-lg px-4 py-3>
<span class="font-bold text-amber-300">Choose later</span>
<span class="text-sm opacity-85"> — Cut the dendrogram after fitting to obtain any desired number of clusters.</span>
</div>
</div>
</div>
<div>
<svg role="img" aria-label="Dendrogram of five points merging bottom-up, with a horizontal cut line producing two clusters" viewBox="0 0 460 300" class="w-full mt-3">
  <line x1="60" y1="260" x2="60" y2="230" stroke="#2dd4bf" stroke-width="2.5"/>
  <line x1="120" y1="260" x2="120" y2="230" stroke="#2dd4bf" stroke-width="2.5"/>
  <line x1="60" y1="230" x2="120" y2="230" stroke="#2dd4bf" stroke-width="2.5"/>

  <line x1="240" y1="260" x2="240" y2="230" stroke="#2dd4bf" stroke-width="2.5"/>
  <line x1="300" y1="260" x2="300" y2="230" stroke="#2dd4bf" stroke-width="2.5"/>
  <line x1="240" y1="230" x2="300" y2="230" stroke="#2dd4bf" stroke-width="2.5"/>

  <line x1="90" y1="230" x2="90" y2="180" stroke="#60a5fa" stroke-width="2.5"/>
  <line x1="180" y1="260" x2="180" y2="180" stroke="#60a5fa" stroke-width="2.5"/>
  <line x1="90" y1="180" x2="180" y2="180" stroke="#60a5fa" stroke-width="2.5"/>

  <line x1="135" y1="180" x2="135" y2="100" stroke="#f472b6" stroke-width="2.5"/>
  <line x1="270" y1="230" x2="270" y2="100" stroke="#f472b6" stroke-width="2.5"/>
  <line x1="135" y1="100" x2="270" y2="100" stroke="#f472b6" stroke-width="2.5"/>

  <g fill="#cbd5e1" style="font-size: 13px" text-anchor="middle">
    <text x="60" y="278">A</text><text x="120" y="278">B</text><text x="180" y="278">C</text>
    <text x="240" y="278">D</text><text x="300" y="278">E</text>
  </g>

  <line x1="35" y1="150" x2="420" y2="150" stroke="#fbbf24" stroke-width="2" stroke-dasharray="8 5"/>
  <text x="425" y="146" fill="#fbbf24" style="font-size:12px">cut → 2 clusters</text>
  <text x="15" y="253" fill="#94a3b8" style="font-size:11px">low</text>
  <text x="15" y="108" fill="#94a3b8" style="font-size:11px">high</text>
  <text x="0" y="80" fill="#94a3b8" style="font-size:12px">merge height</text>
</svg>
</div>
</div>

<!--
Read the dendrogram left to right, bottom to top. Every leaf starts as its own singleton cluster. The y-axis is "merge height" — the distance (under whichever linkage rule is chosen) at which two clusters were combined. A and B are the most similar pair and merge first, at a low height; D and E likewise merge early. Then {A,B} merges with C at a higher height (they are less similar than A and B were to each other), and finally {A,B,C} merges with {D,E} at the highest height shown, producing one root cluster containing everyone.

This entire structure is computed ONCE, with no K specified in advance — contrast this explicitly with k-means, which requires committing to K before fitting. The number of clusters becomes a post-hoc decision: draw a horizontal line at any height and count how many vertical branches it crosses — that count is the number of clusters at that resolution. The dashed cut line here crosses two branches (the {A,B,C} branch and the {D,E} branch), giving 2 clusters; a cut placed lower, below the A-B and D-E merges, would give more, smaller clusters; a cut at the very top would give 1 cluster (everyone together). This is the concrete payoff of hierarchical clustering: one fit serves every possible K, and the dendrogram itself — showing which points are "close" at every resolution — is often more informative than any single flat partition.

In scikit-learn, `AgglomerativeClustering(n_clusters=k)` performs the merges and stops when k clusters remain (functionally the same as computing the full tree and cutting it); `scipy.cluster.hierarchy.dendrogram` draws the full tree shown here.
-->

---
glowSeed: 717
---

# Linkage Defines “Closest Clusters”

<div class="grid grid-cols-2 gap-4 mt-6">
<div v-click border="2 solid teal-800" bg="teal-800/20" rounded-lg p-4>
<div class="font-bold text-teal-300 mb-2">Single</div>
<div class="text-sm leading-relaxed opacity-90">Nearest pair; prone to chaining.</div>
</div>
<div v-click border="2 solid blue-800" bg="blue-800/20" rounded-lg p-4>
<div class="font-bold text-blue-300 mb-2">Complete</div>
<div class="text-sm leading-relaxed opacity-90">Farthest pair; favors compact groups.</div>
</div>
<div v-click border="2 solid amber-800" bg="amber-800/20" rounded-lg p-4>
<div class="font-bold text-amber-300 mb-2">Average</div>
<div class="text-sm leading-relaxed opacity-90">Average all cross-cluster pair distances.</div>
</div>
<div v-click border="2 solid violet-800" bg="violet-800/20" rounded-lg p-4>
<div class="font-bold text-violet-300 mb-2">Ward</div>
<div class="text-sm leading-relaxed opacity-90">Minimize the increase in within-cluster variance.</div>
</div>
</div>


<!--
Linkage answers a question the dendrogram slide glossed over: when merging two CLUSTERS (not two points), which pairwise distance actually represents "the distance between the clusters"? Each choice encodes a different geometric assumption, exactly analogous to how the k-means objective encodes "spherical, equal-size clusters."

Single linkage: distance between two clusters is the distance between their single closest pair of points. This can follow long, thin, winding chains of nearby points ("chaining") and merge two visually distinct blobs if there happens to be a bridge of intermediate points connecting them — good for elongated, non-convex clusters, bad when you want compact groups.

Complete linkage: distance between two clusters is the distance between their single FARTHEST pair of points. This favors compact, roughly equal-diameter clusters and actively resists chaining, but can be overly conservative about merging genuinely close clusters if each contains even one outlier far from the other cluster.

Average linkage: average every pairwise distance between the two clusters' members. A compromise between single and complete — less sensitive to individual outlier pairs than either extreme.

Ward's method: merge whichever pair of clusters causes the smallest INCREASE in total within-cluster variance (the same within-cluster sum-of-squares objective from the k-means slides). This is the most direct analog to k-means among the linkage choices and, empirically, tends to produce clusters most similar to what k-means would find — it is scikit-learn's default for AgglomerativeClustering.

Misconception to flag: linkage is a modeling choice, not a mechanical detail — switching linkage on the same data and same K can produce meaningfully different clusters, and there is no universally "correct" linkage. Always report which linkage was used, and consider trying more than one when the choice actually matters for downstream decisions.
-->

---
glowSeed: 718
---

# Two Ways to Find Groups

<div class="mt-8"><div class="grid grid-cols-3 gap-4 mt-6">
<div v-click border="2 solid teal-800" bg="teal-800/20" rounded-lg p-4>
<div class="font-bold text-teal-300 mb-2">k-means</div>
<div class="text-sm leading-relaxed opacity-90">Fast, flat, needs K.</div>
</div>
<div v-click border="2 solid blue-800" bg="blue-800/20" rounded-lg p-4>
<div class="font-bold text-blue-300 mb-2">Hierarchical</div>
<div class="text-sm leading-relaxed opacity-90">Rich tree, higher cost.</div>
</div>
<div v-click border="2 solid amber-800" bg="amber-800/20" rounded-lg p-4>
<div class="font-bold text-amber-300 mb-2">Both</div>
<div class="text-sm leading-relaxed opacity-90">Scale distance features first.</div>
</div>
</div></div>

<div v-click class="mt-10 text-center text-lg" border="2 solid white/10" bg="white/5" rounded-lg px-6 py-4>Next: reduce dimensionality with PCA, t-SNE, and UMAP.</div>

<!--
Close by connecting every idea in this deck back to the two decisions that actually matter in practice. k-means: minimizes within-cluster sum of squares J via alternating assign/update (Lloyd's algorithm), needs K chosen up front (elbow or silhouette), needs a good initialization (k-means++ plus multiple restarts) because the objective is non-convex, and assumes roughly spherical, similarly sized, similarly scaled clusters. Hierarchical clustering: builds one tree via repeated nearest-cluster merges under a chosen linkage rule (single, complete, average, or Ward), defers the choice of K to a post-hoc cut of the dendrogram, and scales worse (typically O(n^2) or O(n^3) versus k-means' roughly linear-per-iteration cost), which matters for large n. Both require standardized features when units differ, because both ultimately rely on a distance metric.

Transition explicitly: everything in this deck used HARD assignment — every point belongs to exactly one cluster, full stop. The next deck, Gaussian Mixture Models, asks "what if a point near a cluster boundary should be allowed partial membership in more than one cluster?" and answers it by replacing centroids with full probability distributions and hard assignment with a soft, probabilistic one — while showing that k-means falls out as an exact special case of GMM in a particular limit. That connection is the throughline into the next deck.
-->
