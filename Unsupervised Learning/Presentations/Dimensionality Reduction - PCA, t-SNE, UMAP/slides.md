---
theme: default
highlighter: shiki
css: unocss
colorSchema: dark
title: 'Dimensionality Reduction: PCA, t-SNE, and UMAP'
info: |
  ## Dimensionality Reduction: PCA, t-SNE, and UMAP
  Compress data while preserving useful structure
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

# Dimensionality Reduction: PCA, t-SNE, and UMAP

### Compress data while preserving useful structure

<div class="pt-8 opacity-80 text-lg">Unsupervised Learning · Foundations of Machine Learning</div>

<div class="mt-14 flex justify-center gap-4" aria-hidden="true">
<div class="w-28 h-3 rounded-full bg-teal-400/70"></div>
<div class="w-20 h-3 rounded-full bg-blue-400/60"></div>
<div class="w-14 h-3 rounded-full bg-violet-400/50"></div>
</div>

<!--
This deck follows k-Means and Hierarchical Clustering. That deck grouped points; this deck reduces the number of COORDINATES used to describe each point in the first place. The two topics are complementary and often used together: clustering algorithms like k-means rely on distance, and distance becomes unreliable in very high dimensions (the "curse of dimensionality" — in high-dimensional space, points tend to be nearly equidistant from each other, which erodes the notion of "nearest centroid" that k-means depends on). Reducing dimension before clustering, or reducing purely to visualize what a clustering found, is one of the most common reasons this topic follows immediately after k-means in the course.

Roadmap: start with PCA, which is linear and has a full closed-form derivation — we will show explicitly why "the direction of maximum variance" is mathematically identical to "the top eigenvector of the covariance matrix," not just assert it. Then generalize from one direction to a full change of basis (all principal components at once), connect this to the SVD (which is what scikit-learn actually computes under the hood), and show how to pick the number of components to keep. Then pivot to t-SNE and UMAP, two nonlinear methods that sacrifice PCA's interpretability and speed in exchange for much better visualizations of complex, curved structure — explained at the level of what problem they solve and how, without the full derivation, since both are legitimately more mathematically involved than is productive to derive from scratch in this course. This deck closes the Unsupervised Learning unit's geometric thread and hands off to Gaussian Mixture Models, where the covariance matrix reappears as the shape of a soft cluster.
-->

---
glowSeed: 741
---

# Why Reduce Dimension?

<div class="grid grid-cols-2 gap-4 mt-6">
<div v-click border="2 solid teal-800" bg="teal-800/20" rounded-lg p-4>
<div class="font-bold text-teal-300 mb-2">Visualize</div>
<div class="text-sm leading-relaxed opacity-90">Project high-dimensional data into two or three dimensions.</div>
</div>
<div v-click border="2 solid blue-800" bg="blue-800/20" rounded-lg p-4>
<div class="font-bold text-blue-300 mb-2">Denoise</div>
<div class="text-sm leading-relaxed opacity-90">Discard directions containing little stable variation.</div>
</div>
<div v-click border="2 solid amber-800" bg="amber-800/20" rounded-lg p-4>
<div class="font-bold text-amber-300 mb-2">Accelerate</div>
<div class="text-sm leading-relaxed opacity-90">Give downstream k-NN or k-means fewer coordinates.</div>
</div>
<div v-click border="2 solid violet-800" bg="violet-800/20" rounded-lg p-4>
<div class="font-bold text-violet-300 mb-2">Compress</div>
<div class="text-sm leading-relaxed opacity-90">Represent many correlated features with a smaller latent basis.</div>
</div>
</div>


<!--
The four motivations here are genuinely distinct use cases, not synonyms, and it's worth having students articulate the difference. Visualize: humans cannot perceive more than 3 spatial dimensions, so any dataset with more than 3 features needs SOME projection before a human can look at it directly — this is purely about the limits of human perception, not about the data's true complexity. Denoise: real measurements often have more apparent dimensions (features) than true underlying degrees of freedom; a dataset of many correlated sensor readings might have an intrinsic dimensionality of just a handful of true underlying factors, and the "extra" directions are largely measurement noise that is safe to discard. Accelerate: nearest-neighbor search, k-means, and other distance-based algorithms scale with the number of features, and both compute cost and the curse of dimensionality (points becoming nearly equidistant) get worse as dimension grows — reducing dimension first can make those algorithms both faster and more meaningful. Compress: when features are highly correlated (e.g., height in inches and height in centimeters, or many pixels in a photograph that vary together), a much smaller set of derived coordinates can represent almost all the information the original features carried.

Key conceptual distinction to plant here explicitly: "raw feature count" is simply how many columns the dataset happens to have; "intrinsic dimensionality" is the true number of independent directions along which the data actually varies. A dataset can have 1000 raw features but an intrinsic dimensionality of 3 if those 1000 features are all noisy linear combinations of 3 underlying factors. Dimensionality reduction methods are, in essence, attempts to estimate and recover that smaller intrinsic dimensionality.
-->

---
glowSeed: 742
---

# PCA Maximizes Projected Variance

<div class="grid grid-cols-2 gap-8 items-start">
<div>
<div class="space-y-3 mt-4">
<div v-click border="2 solid white/5" bg="white/5" rounded-lg px-4 py-3>
<span class="font-bold text-teal-300">Center first</span>
<span class="text-sm opacity-85"> — PCA describes variation around the data mean.</span>
</div>
<div v-click border="2 solid white/5" bg="white/5" rounded-lg px-4 py-3>
<span class="font-bold text-blue-300">Choose a unit direction</span>
<span class="text-sm opacity-85"> — Prevent the objective from growing by simple rescaling.</span>
</div>
<div v-click border="2 solid white/5" bg="white/5" rounded-lg px-4 py-3>
<span class="font-bold text-amber-300">Equivalent view</span>
<span class="text-sm opacity-85"> — The same subspace minimizes linear reconstruction error.</span>
</div>
</div>
</div>
<div>
<div v-click class="mt-4" style="font-size: .85em" border="2 solid teal-800" bg="teal-800/20" rounded-lg px-4 py-3>

$$
\Sigma=\frac{1}{n-1}X_{\mathrm{c}}^\top X_{\mathrm{c}},\qquad
v_1=\arg\max_{\lVert v\rVert=1}v^\top\Sigma v
$$

</div>

</div>
</div>

<!--
Define every symbol. X_c is the centered data matrix (n rows, d columns; each column mean-subtracted so the origin sits at the data's centroid). Sigma is the d-by-d empirical covariance matrix, computed as (1/(n-1)) X_c^T X_c — literally the same sample-covariance formula from the probability/statistics unit, just written in matrix form: entry (j,k) of Sigma is the sample covariance between feature j and feature k. A unit vector v defines a direction in feature space; projecting a centered point x_c onto v gives the scalar v^T x_c, and the variance of these projected scalars across all n points works out to exactly v^T Sigma v — this is the quantity PCA maximizes.

Walk through why each of the three steps on the left is necessary. Centering first: if we didn't subtract the mean, "variance of the projection" would be contaminated by the projection of the mean itself, which has nothing to do with how spread out the data actually is — PCA is about spread, not location. Unit-length constraint: without constraining ||v||=1, the objective v^T Sigma v grows without bound simply by rescaling v to be longer, since it's quadratic in v — the constraint forces the optimizer to find a DIRECTION, not a magnitude. Equivalent view (reconstruction error): there is a classical dual formulation of PCA — instead of asking "which direction maximizes variance," ask "which k-dimensional subspace, when we project onto it and then project back, minimizes the total squared reconstruction error." These two formulations provably select exactly the same subspace; the "maximize variance" framing is more common because the optimization is more transparent, but the "minimize reconstruction error" framing is what directly motivates PCA as a lossy compression scheme, and it's the framing that connects to autoencoders later in the course when we revisit dimensionality reduction with neural networks.

Use an elongated point cloud as the mental picture: project the cloud onto its long axis and the projected values are spread out (high variance); project onto the short axis and the projected values are squeezed together (low variance). PCA's first component finds exactly this long axis, automatically, for data in any number of dimensions.
-->

---
glowSeed: 743
---

# The Optimizer Is an Eigenvector

<div class="grid grid-cols-2 gap-8 items-start">
<div>
<div class="space-y-3 mt-4">
<div v-click border="2 solid white/5" bg="white/5" rounded-lg px-4 py-3>
<span class="font-bold text-teal-300">Constrained objective</span>
<span class="text-sm opacity-85"> — Use a Lagrange multiplier for vᵀv = 1.</span>
</div>
<div v-click border="2 solid white/5" bg="white/5" rounded-lg px-4 py-3>
<span class="font-bold text-blue-300">Stationary condition</span>
<span class="text-sm opacity-85"> — Σv = λv.</span>
</div>
<div v-click border="2 solid white/5" bg="white/5" rounded-lg px-4 py-3>
<span class="font-bold text-amber-300">Select</span>
<span class="text-sm opacity-85"> — The largest eigenvalue gives the largest achievable variance.</span>
</div>
</div>
</div>
<div>
<div v-click class="mt-4" style="font-size: .9em" border="2 solid teal-800" bg="teal-800/20" rounded-lg px-4 py-3>

$$
\mathcal L=v^\top\Sigma v-\lambda(v^\top v-1)\ \Rightarrow\ \Sigma v=\lambda v
$$

</div>

</div>
</div>

<!--
This is the exact algebra promised at the start: turn the constrained optimization "maximize v^T Sigma v subject to ||v||=1" into an unconstrained one using a Lagrange multiplier lambda. Form the Lagrangian L(v, lambda) = v^T Sigma v - lambda(v^T v - 1), then differentiate with respect to v and set the gradient to zero: d/dv [v^T Sigma v] = 2 Sigma v (using the standard matrix-calculus identity that the gradient of a quadratic form x^T A x for symmetric A is 2Ax), and d/dv [lambda(v^T v - 1)] = 2 lambda v. Setting the difference to zero and dividing by 2 gives exactly Sigma v = lambda v — the defining equation of an eigenvector, from the Linear Algebra deck at the start of the course.

This is the payoff worth pausing on explicitly: the vector v that maximizes projected variance MUST be an eigenvector of the covariance matrix Sigma, for some eigenvalue lambda. That is not an assumption or an analogy — it falls straight out of setting the derivative of the Lagrangian to zero. Once we know the optimal v is SOME eigenvector, plug the stationary condition back into the original objective: v^T Sigma v = v^T (lambda v) = lambda (v^T v) = lambda, since v is a unit vector. So the value of the objective at any stationary point is exactly its eigenvalue. To maximize the objective, therefore, pick the eigenvector with the LARGEST eigenvalue — that is v_1, the first principal component, and its eigenvalue lambda_1 equals the maximum achievable projected variance. This is why we sort eigenvalues in descending order on the very next slide: eigenvalue rank directly IS variance rank.
-->

---
glowSeed: 744
---

# Full PCA Is a Change of Basis

<div class="grid grid-cols-2 gap-8 items-start">
<div>
<div class="space-y-3 mt-4">
<div v-click border="2 solid white/5" bg="white/5" rounded-lg px-4 py-3>
<span class="font-bold text-teal-300">Order eigenvectors</span>
<span class="text-sm opacity-85"> — Sort covariance directions by descending eigenvalue.</span>
</div>
<div v-click border="2 solid white/5" bg="white/5" rounded-lg px-4 py-3>
<span class="font-bold text-blue-300">Keep the first k</span>
<span class="text-sm opacity-85"> — They are mutually orthogonal because Σ is symmetric.</span>
</div>
<div v-click border="2 solid white/5" bg="white/5" rounded-lg px-4 py-3>
<span class="font-bold text-amber-300">Project</span>
<span class="text-sm opacity-85"> — Coordinates in that basis are the principal-component scores.</span>
</div>
</div>
</div>
<div>
<div class="mt-5" role="img" aria-label="Centered X then Covariance Σ then Eigenvectors Qₖ then XQₖ">
<div v-click class="flex items-center gap-3">
<div class="w-8 h-8 rounded-full bg-teal-500/20 border-2 border-teal-700 flex items-center justify-center text-sm font-bold">1</div>
<div class="flex-1 rounded-lg border-2 border-white/10 bg-white/5 px-3 py-2 text-sm font-bold">Centered X</div>
</div>
<div class="ml-4 h-1 border-l-2 border-teal-400/50"></div>
<div v-click class="flex items-center gap-3">
<div class="w-8 h-8 rounded-full bg-blue-500/20 border-2 border-blue-700 flex items-center justify-center text-sm font-bold">2</div>
<div class="flex-1 rounded-lg border-2 border-white/10 bg-white/5 px-3 py-2 text-sm font-bold">Covariance Σ</div>
</div>
<div class="ml-4 h-1 border-l-2 border-teal-400/50"></div>
<div v-click class="flex items-center gap-3">
<div class="w-8 h-8 rounded-full bg-amber-500/20 border-2 border-amber-700 flex items-center justify-center text-sm font-bold">3</div>
<div class="flex-1 rounded-lg border-2 border-white/10 bg-white/5 px-3 py-2 text-sm font-bold">Eigenvectors Qₖ</div>
</div>
<div class="ml-4 h-1 border-l-2 border-teal-400/50"></div>
<div v-click class="flex items-center gap-3">
<div class="w-8 h-8 rounded-full bg-violet-500/20 border-2 border-violet-700 flex items-center justify-center text-sm font-bold">4</div>
<div class="flex-1 rounded-lg border-2 border-white/10 bg-white/5 px-3 py-2 text-sm font-bold">XQₖ</div>
</div>
</div>
<div v-click class="mt-4" style="font-size: .9em" border="2 solid teal-800" bg="teal-800/20" rounded-lg px-4 py-3>

$$
\Sigma=Q\Lambda Q^\top,\qquad X_{\mathrm{reduced}}=X_{\mathrm{centered}}Q_k
$$

</div>
</div>
</div>

<!--
This generalizes the single-eigenvector result to the full picture. Because Sigma is real and symmetric, the spectral theorem (from the Linear Algebra deck) guarantees it has a complete set of d real eigenvalues and orthogonal eigenvectors: Sigma = Q Lambda Q^T, where Q is an orthogonal matrix whose columns are the eigenvectors (q_1, ..., q_d) and Lambda is diagonal with the eigenvalues sorted, by convention, in descending order (lambda_1 >= lambda_2 >= ... >= lambda_d). Each q_i solves the same maximize-variance problem as the previous slide, but subject to an ADDITIONAL constraint: orthogonal to every q_j already chosen. This is why the components are mutually orthogonal — it isn't a coincidence or extra assumption, it is forced by the symmetric spectral decomposition.

Walk the four-step pipeline: (1) center X by subtracting the column means — never skip this; (2) compute the covariance matrix Sigma; (3) eigendecompose Sigma and keep only the top k eigenvectors (those with the k largest eigenvalues) as the columns of Q_k, a d-by-k matrix; (4) project the centered data onto this new basis via X_centered @ Q_k, producing an n-by-k matrix of principal-component SCORES — the new, lower-dimensional coordinates for every original point. This is literally a change of basis: instead of describing each point by its original d correlated features, we describe it by k new, mutually uncorrelated coordinates ranked by how much variance each one explains.

The discarded directions (eigenvectors k+1 through d, with the smallest eigenvalues) are exactly where reconstruction error comes from: if you project onto Q_k and then project back into the original d-dimensional space, the squared reconstruction error per point equals the sum of the variances along the discarded directions — small eigenvalues discarded means small reconstruction error. This is the formal version of "PCA finds the subspace that best approximates the data," and it is the same quantity minimized in the "equivalent view" bullet from two slides ago.
-->

---
glowSeed: 903
---

# The SVD Route

<div class="grid grid-cols-2 gap-8 items-start">
<div>
<div class="space-y-3 mt-4">
<div v-click border="2 solid white/5" bg="white/5" rounded-lg px-4 py-3>
<span class="font-bold text-teal-300">Factor $X_c$ directly</span>
<span class="text-sm opacity-85"> — No need to form $\Sigma$ explicitly.</span>
</div>
<div v-click border="2 solid white/5" bg="white/5" rounded-lg px-4 py-3>
<span class="font-bold text-blue-300">Right singular vectors = eigenvectors</span>
<span class="text-sm opacity-85"> — $V$'s columns are the principal directions.</span>
</div>
<div v-click border="2 solid white/5" bg="white/5" rounded-lg px-4 py-3>
<span class="font-bold text-amber-300">Singular values relate to eigenvalues</span>
<span class="text-sm opacity-85"> — $\lambda_i = d_i^2/(n-1)$.</span>
</div>
</div>
</div>
<div>
<div v-click class="mt-4" style="font-size: .85em" border="2 solid teal-800" bg="teal-800/20" rounded-lg px-4 py-3>

$$
X_c=UDV^\top,\qquad \Sigma=\frac{X_c^\top X_c}{n-1}=V\frac{D^2}{n-1}V^\top
$$

</div>
<div v-click class="mt-4 text-sm opacity-85">
This is what <code>sklearn.decomposition.PCA</code> actually computes — factoring $X_c$ directly is more numerically stable than forming $\Sigma$ and eigendecomposing it.
</div>
</div>
</div>

<!--
Every non-square or rectangular matrix has a singular value decomposition: X_c = U D V^T, where U (n-by-n, or n-by-d in the "thin" form) and V (d-by-d) are orthogonal matrices, and D is diagonal with non-negative entries d_1 >= d_2 >= ... >= 0 called singular values. Substitute this factorization into the covariance formula: Sigma = X_c^T X_c / (n-1) = (V D U^T)(U D V^T)/(n-1) = V D^2 V^T / (n-1), using U^T U = I because U is orthogonal. Compare this to the eigendecomposition Sigma = Q Lambda Q^T from the previous slide: they must be the same decomposition (up to sign conventions), which tells us directly that V's columns ARE the covariance matrix's eigenvectors, and that the eigenvalues are lambda_i = d_i^2 / (n-1) — each eigenvalue is the corresponding squared singular value, rescaled by the sample-size correction.

Why this matters practically, not just theoretically: scikit-learn's PCA does NOT form the covariance matrix and call an eigenvalue solver on it. It computes the SVD of the centered data matrix directly. Two reasons: numerical stability (squaring numbers when forming X^T X can lose precision, especially for ill-conditioned data, whereas SVD avoids that squaring step) and, for very wide datasets (d much larger than n, e.g., gene expression data with 20,000 genes and 200 samples), computing a d-by-d covariance matrix is far more expensive than computing an SVD bounded by the smaller dimension n. This is purely an implementation detail — the MATHEMATICAL result (which directions, which variances) is identical either way — but it explains why the sklearn API returns `components_` and `singular_values_` rather than talking about eigenvectors directly, and it's worth knowing so the terminology doesn't feel like a different algorithm.
-->

---
glowSeed: 904
---

# Worked Example: PCA by Hand

<div class="grid grid-cols-2 gap-8 items-start text-sm">
<div>

**10 points, 2 features** (mean $\bar x=(1.81,\,1.91)$, already centered below)

<div v-click border="2 solid teal-800" bg="teal-800/20" rounded-lg px-4 py-3 style="font-size:.9em">

$$
\Sigma=\begin{bmatrix}0.617 & 0.615\\0.615 & 0.717\end{bmatrix}
$$

</div>

<div v-click class="mt-3 text-xs opacity-85">
Off-diagonal $\approx$ diagonal: the two features are strongly, almost perfectly, positively correlated — a visual scatter would look like a thin, tilted cigar.
</div>

</div>
<div>

<div v-click border="2 solid white/5" bg="white/5" rounded-lg px-4 py-3 style="font-size:.9em">

$$
\lambda_1=1.284,\ \ \lambda_2=0.049
$$

$$
v_1=(0.678,\ 0.735)
$$

</div>

<div v-click class="mt-3 text-xs opacity-85">
Explained variance ratio: $\lambda_1/(\lambda_1+\lambda_2)=96.3\%$. One component captures almost all the spread — exactly what we'd expect from a near-perfectly correlated pair of features.
</div>

</div>
</div>

<!--
Every number here was computed with numpy and verified: covariance matrix from 10 two-dimensional points designed to be strongly correlated (think "hours studied" and "exam score" — as one goes up, so does the other, almost linearly). The covariance matrix's off-diagonal entry (0.615) is nearly as large as its diagonal entries (0.617, 0.717), which is the numerical signature of strong positive correlation — this is worth having students recognize on sight, since it previews exactly why one principal component dominates.

Eigendecomposing this 2x2 Sigma by the quadratic formula (det(Sigma - lambda I) = 0) gives lambda_1 = 1.284 and lambda_2 = 0.049. The corresponding top eigenvector v_1 = (0.678, 0.735) points diagonally — roughly the "45-degree" direction where both features increase together, which is exactly the long axis of the cigar-shaped scatter. The explained variance ratio lambda_1/(lambda_1+lambda_2) = 96.3% quantifies this: projecting onto v_1 alone preserves 96.3% of the total variance in the original two-dimensional data, discarding only 3.7% by dropping the second dimension. This is the numeric payoff of everything derived so far — a concrete case where 2 features compress losslessly-for-practical-purposes into 1.
-->

---
glowSeed: 745
---

# PCA in scikit-learn

<div class="grid grid-cols-2 gap-4 mt-6">
<div v-click border="2 solid teal-800" bg="teal-800/20" rounded-lg p-4>
<div class="font-bold text-teal-300 mb-2">Fit</div>
<div class="text-sm leading-relaxed opacity-90">Learn principal directions from training data.</div>
</div>
<div v-click border="2 solid blue-800" bg="blue-800/20" rounded-lg p-4>
<div class="font-bold text-blue-300 mb-2">Transform</div>
<div class="text-sm leading-relaxed opacity-90">Project into the lower-dimensional coordinates.</div>
</div>
</div>

```python
from sklearn.decomposition import PCA

pca = PCA(n_components=0.95)
X_train_small = pca.fit_transform(X_train)
X_test_small = pca.transform(X_test)

assert pca.explained_variance_ratio_.sum() >= 0.95
assert X_train_small.shape[1] <= X_train.shape[1]
```

<!--
This is the practical scikit-learn workflow implementing the full derivation from the previous four slides. `PCA(n_components=0.95)` uses a convenient API feature worth explaining: passing a float between 0 and 1 (rather than an integer) tells scikit-learn to automatically choose however many components are needed so the cumulative explained variance ratio reaches at least that threshold — internally, it computes the full SVD, then keeps components in descending-eigenvalue order until the running sum of λ_k/Σλ_j crosses 0.95, exactly the "cumulative target" idea the next slide names explicitly.

`.fit_transform(X_train)` performs both steps at once on the training data: `fit` learns the principal directions (the eigenvectors/right singular vectors) and the centering mean from `X_train` only, and `transform` immediately projects `X_train` onto those learned directions. Critically, `pca.transform(X_test)` reuses the exact same directions and the exact same training-set mean learned during `fit` — it does not refit PCA on the test data. This is the same leakage discipline drilled throughout the course for `StandardScaler` and other fitted transforms: if PCA were fit on the full dataset (train and test combined) before splitting, the "directions of maximum variance" would have been informed by test-set structure, silently leaking information across the train/test boundary. In practice, wrap PCA inside a `Pipeline` alongside a scaler and a downstream model (e.g., `make_pipeline(StandardScaler(), PCA(n_components=0.95), KMeans(...))`), so cross-validation refits both the scaler and PCA from scratch inside each training fold. The two assertions simply confirm the API contract: the retained components explain at least 95% of variance, and the reduced representation has fewer columns than the original. Transition: the next slide names the diagnostic tool — the scree plot — used to choose that variance threshold in the first place.
-->

---
glowSeed: 746
---

# Explained Variance Chooses k

<div class="grid grid-cols-2 gap-8 items-start">
<div>
<div class="space-y-3 mt-4">
<div v-click border="2 solid white/5" bg="white/5" rounded-lg px-4 py-3>
<span class="font-bold text-teal-300">Eigenvalue</span>
<span class="text-sm opacity-85"> — Variance captured by one component.</span>
</div>
<div v-click border="2 solid white/5" bg="white/5" rounded-lg px-4 py-3>
<span class="font-bold text-blue-300">Ratio</span>
<span class="text-sm opacity-85"> — Divide by total variance.</span>
</div>
<div v-click border="2 solid white/5" bg="white/5" rounded-lg px-4 py-3>
<span class="font-bold text-amber-300">Cumulative target</span>
<span class="text-sm opacity-85"> — Keep enough components for a target such as 95%.</span>
</div>
</div>
</div>
<div>
<svg role="img" aria-label="Scree plot: per-component explained variance drops sharply while cumulative explained variance rises and levels off near PC4" viewBox="0 0 500 310" class="w-full max-w-xl mx-auto mt-7">
  <line x1="55" y1="260" x2="470" y2="260" stroke="#64748b" stroke-width="2"/><line x1="55" y1="35" x2="55" y2="260" stroke="#64748b" stroke-width="2"/>
  <g fill="#fb923c"><rect x="50" y="60" width="30" height="200"/><rect x="148" y="140" width="30" height="120"/><rect x="246" y="205" width="30" height="55"/><rect x="344" y="235" width="30" height="25"/><rect x="442" y="248" width="30" height="12"/></g>
  <path d="M65 200 C130 90,163 55,261 42 S359 38,457 36" fill="none" stroke="#2dd4bf" stroke-width="4" stroke-dasharray="8 6"/>
  <g fill="#cbd5e1" style="font-size: 12px" text-anchor="middle"><text x="65" y="285">PC1</text><text x="163" y="285">PC2</text><text x="261" y="285">PC3</text><text x="359" y="285">PC4</text><text x="457" y="285">PC5</text></g>
  <g style="font-size: 12px"><text x="380" y="30" fill="#5eead4">cumulative (rises, levels off)</text><text x="90" y="80" fill="#fdba74">per-component (bars, drop off)</text></g>
</svg>
<div v-click class="mt-4" style="font-size: .9em" border="2 solid teal-800" bg="teal-800/20" rounded-lg px-4 py-3>

$$
r_k=\frac{\lambda_k}{\sum_j\lambda_j}
$$

</div>
</div>
</div>

<!--
This is the diagnostic tool, called a scree plot, for choosing how many principal components to keep, and it directly reuses vocabulary from the k-Means deck's elbow method. The eigenvalue λ_k (equivalently, d_k²/(n-1) from the SVD relationship two slides ago) is literally the variance captured by component k alone — the bars in the chart, in strictly descending order by construction, since components are sorted by eigenvalue. The ratio r_k = λ_k / Σ_j λ_j normalizes each component's contribution as a fraction of total variance, so the r_k values across all d components sum to exactly 1.

The dashed line plots the cumulative sum of r_k as more components are added — it starts at r_1 (PC1 alone) and climbs toward 1.0 as every component is eventually included. The "cumulative target" bullet is exactly what `PCA(n_components=0.95)` automates from the previous slide: pick the smallest k such that the cumulative curve crosses a chosen threshold (95% is a common default, but the right number depends on the application — denoising might tolerate 90%, a compression task might demand 99%). The bar heights dropping off sharply after PC3 in this chart, with the cumulative curve nearly flat afterward, is the visual signature of low intrinsic dimensionality — exactly the "1000 raw features, 3 true underlying factors" scenario named on the "Why Reduce Dimension?" slide.

Draw the explicit parallel to k-means' elbow method: both diagnostics plot a monotonic quantity (inertia there, cumulative explained variance here) against a complexity parameter (K there, number of components here) and look for a bend where additional complexity stops paying for itself — the difference is that k-means' elbow is inertia decreasing (lower is better, stop when it stops falling much), while PCA's elbow is cumulative variance increasing (higher is better, stop when it stops rising much). Both are heuristics, not exact answers — like the elbow method, the "right" k here is ultimately a judgment call informed by the downstream use case. Transition: PCA's linear directions handle a wide range of real cases well, but next we look at what happens when the true underlying structure is not a flat subspace at all.
-->

---
glowSeed: 747
---

# PCA vs. t-SNE / UMAP

<div class="grid grid-cols-3 gap-4 mt-6">
<div v-click border="2 solid teal-800" bg="teal-800/20" rounded-lg p-4>
<div class="font-bold text-teal-300 mb-2">PCA</div>
<div class="text-sm leading-relaxed opacity-90">Linear, deterministic, fast, globally interpretable variance axes.</div>
</div>
<div v-click border="2 solid blue-800" bg="blue-800/20" rounded-lg p-4>
<div class="font-bold text-blue-300 mb-2">t-SNE / UMAP</div>
<div class="text-sm leading-relaxed opacity-90">Nonlinear, visualization-focused, preserve local neighborhoods.</div>
</div>
<div v-click border="2 solid amber-800" bg="amber-800/20" rounded-lg p-4>
<div class="font-bold text-amber-300 mb-2">Caution</div>
<div class="text-sm leading-relaxed opacity-90">Distances and apparent cluster sizes in nonlinear embeddings can mislead.</div>
</div>
</div>


<!--
PCA's entire derivation this deck just built assumes the data's true structure lies near a flat, linear subspace — a plane or hyperplane through the data. Real high-dimensional data (images, word embeddings, genomic profiles) often lies instead near a curved, nonlinear manifold — imagine a Swiss-roll shape or an S-curve embedded in 3D: a straight 2D plane cannot cleanly separate points that are close along the curved surface from points that are far along it, even though the intrinsic structure is genuinely low-dimensional (2D, if you could "unroll" it). PCA, restricted to linear projections, will find the flattest plane through such data but can badly scramble genuinely distant points into apparent proximity. t-SNE and UMAP exist to handle exactly this case.

Both algorithms solve a common underlying problem, framed as neighbor-preservation rather than variance-maximization: for each point, first compute which other points are its "neighbors" in the original high-dimensional space (t-SNE uses a Gaussian-kernel-based similarity with a tunable "perplexity" parameter, roughly interpretable as an effective neighborhood size; UMAP uses a related but different neighbor-graph construction rooted in topological data analysis). Then, both algorithms search for a low-dimensional (typically 2D) arrangement of points that keeps those same neighbor relationships intact as closely as possible — nearby points in high dimensions should stay nearby in the 2D embedding, even if that requires drastically distorting large-scale, global distances to make it work. This is why t-SNE/UMAP plots often look like well-separated, tight blobs even when the true high-dimensional clusters have very different densities or sizes — local neighborhood structure is what's being optimized and preserved, not overall geometry or absolute distances.

That local-preservation focus is exactly the source of the "Caution" card, and it deserves concrete, specific warnings rather than a vague "be careful": (1) inter-cluster distances in a t-SNE/UMAP plot are not meaningful — two clusters plotted far apart are not necessarily more different than two plotted closer together, since only local neighbor structure was optimized; (2) apparent cluster SIZE (how much 2D area a group of points occupies) does not reliably reflect the true spread or density of that group in the original space; (3) both algorithms are stochastic and sensitive to hyperparameters (t-SNE's perplexity, UMAP's `n_neighbors` and `min_dist`) — rerunning with a different random seed or different hyperparameter can produce a visibly different layout of the SAME data, so a single run should never be treated as ground truth. Contrast this directly with PCA: PCA is deterministic (the same data always gives the same components) and its axes have a precise, checkable meaning (a direction of maximum variance, with an exact explained-variance-ratio number) — t-SNE and UMAP trade away both of those properties for dramatically better visual separation of nonlinear cluster structure. The practical workflow this motivates: use t-SNE/UMAP to explore and generate hypotheses about structure in high-dimensional data, but use PCA, the raw features, or a domain-specific metric to confirm anything that visualization suggests before treating it as a real finding.
-->

---
glowSeed: 748
---

# Dimensionality Reduction

<div class="mt-8"><div class="grid grid-cols-3 gap-4 mt-6">
<div v-click border="2 solid teal-800" bg="teal-800/20" rounded-lg p-4>
<div class="font-bold text-teal-300 mb-2">PCA</div>
<div class="text-sm leading-relaxed opacity-90">Eigenvectors of covariance.</div>
</div>
<div v-click border="2 solid blue-800" bg="blue-800/20" rounded-lg p-4>
<div class="font-bold text-blue-300 mb-2">Variance</div>
<div class="text-sm leading-relaxed opacity-90">Guides retained dimension.</div>
</div>
<div v-click border="2 solid amber-800" bg="amber-800/20" rounded-lg p-4>
<div class="font-bold text-amber-300 mb-2">Nonlinear maps</div>
<div class="text-sm leading-relaxed opacity-90">Reveal local manifolds.</div>
</div>
</div></div>

<div v-click class="mt-10 text-center text-lg" border="2 solid white/10" bg="white/5" rounded-lg px-6 py-4>Next: Gaussian mixtures make clustering probabilistic.</div>

<!--
Recap the full arc of this deck concretely. PCA is not a heuristic — it is a fully derived algorithm: maximize projected variance subject to a unit-length constraint, apply Lagrange multipliers, and the stationary condition falls out to exactly the eigenvector equation Σv=λv, so the covariance matrix's eigenvectors and eigenvalues are provably the variance-maximizing directions and the variance they capture, respectively (an equivalent SVD-based route is what scikit-learn actually runs, for numerical-stability reasons). Explained variance ratios and the scree plot give a principled, quantitative way to choose how many components to keep, directly paralleling the elbow method used to choose K for k-means. Nonlinear methods — t-SNE and UMAP — relax PCA's linearity assumption to handle curved manifold structure, at the cost of losing PCA's determinism, its interpretable axes, and any meaningful notion of global distance in the resulting plot.

This closes the geometric thread running through the entire Unsupervised Learning unit: k-Means and Hierarchical Clustering discovered discrete groups using distance; Gaussian Mixture Models replaced single centroids with full covariance matrices and hard assignment with soft probabilistic membership — and this deck's covariance matrix, Σ, is the exact same object GMM used to shape each component; and this deck itself reduces the number of coordinates describing each point, often as a preprocessing step that makes the other two techniques work better in high dimensions. Across all three decks, the throughline has been the same: extract structure from data with no labeled target to check against, using the tools (covariance, eigendecomposition, distance, iterative optimization) built up across the entire course.

This is also the natural close of the course's classical machine learning arc. Having covered supervised learning (regression, classification, ensembles), the tools to evaluate any model honestly (Model Evaluation), and now unsupervised learning, the final module, Neural Networks and Deep Learning Basics, returns to supervised learning with composable nonlinear models built from simple, stackable units — architecturally a very different toolkit, but trained with the same underlying optimization principles (loss functions, gradient descent, regularization) established throughout this course.
-->
