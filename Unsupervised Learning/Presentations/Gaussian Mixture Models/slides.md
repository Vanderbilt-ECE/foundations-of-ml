---
theme: default
highlighter: shiki
css: unocss
colorSchema: dark
title: 'Gaussian Mixture Models'
info: |
  ## Gaussian Mixture Models
  Replace hard spherical clusters with soft probabilistic components
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
glowSeed: 770
---

# Gaussian Mixture Models

### Replace hard spherical clusters with soft probabilistic components

<div class="pt-8 opacity-80 text-lg">Unsupervised Learning · Foundations of Machine Learning</div>

<div class="mt-14 flex justify-center gap-4" aria-hidden="true">
<div class="w-28 h-3 rounded-full bg-teal-400/70"></div>
<div class="w-20 h-3 rounded-full bg-blue-400/60"></div>
<div class="w-14 h-3 rounded-full bg-violet-400/50"></div>
</div>

<!--
This deck picks up exactly where k-Means and Hierarchical Clustering left off. That deck closed by naming k-means' central limitation: every point gets a hard, all-or-nothing assignment to exactly one cluster, and the implicit geometric assumption is that clusters are roughly spherical, similarly sized, and equally scaled — because nearest-centroid assignment under Euclidean distance can only ever carve out convex, Voronoi-shaped regions. Gaussian Mixture Models (GMMs) relax both of those constraints at once: they replace a single centroid per cluster with a full probability distribution (a multivariate Gaussian, which can be tilted and elongated via its covariance matrix), and they replace hard assignment with soft, probabilistic membership — a point can partially "belong" to more than one cluster.

Roadmap for today: the generative story behind a mixture distribution (how would you actually sample a point from a GMM?), responsibilities as the Bayes'-theorem posterior over which component generated a given point, the Expectation-Maximization (EM) algorithm that fits a GMM by alternating between computing responsibilities and updating each component's parameters, fitting and inspecting a GMM in scikit-learn, the flexibility-versus-parameter-count tradeoff GMMs introduce, and choosing the number of components with AIC/BIC rather than the elbow/silhouette diagnostics used for k-means. By the end, the promised connection lands explicitly: k-means turns out to be a specific limiting case of GMM/EM, not a separate algorithm.
-->

---
glowSeed: 771
---

# A Mixture Is a Generative Story

<div class="grid grid-cols-2 gap-8 items-start">
<div>
<div class="space-y-3 mt-4">
<div v-click border="2 solid white/5" bg="white/5" rounded-lg px-4 py-3>
<span class="font-bold text-teal-300">Choose a component</span>
<span class="text-sm opacity-85"> — Sample k according to its mixing weight πₖ.</span>
</div>
<div v-click border="2 solid white/5" bg="white/5" rounded-lg px-4 py-3>
<span class="font-bold text-blue-300">Generate a point</span>
<span class="text-sm opacity-85"> — Draw x from that component’s Gaussian.</span>
</div>
<div v-click border="2 solid white/5" bg="white/5" rounded-lg px-4 py-3>
<span class="font-bold text-amber-300">Flexible density</span>
<span class="text-sm opacity-85"> — Several simple Gaussians form a multimodal distribution.</span>
</div>
</div>
</div>
<div>
<div v-click class="mt-4" style="font-size: .9em" border="2 solid teal-800" bg="teal-800/20" rounded-lg px-4 py-3>

$$
p(x)=\sum_{k=1}^K\pi_k\,\mathcal N(x\mid\mu_k,\Sigma_k),\qquad \sum_k\pi_k=1
$$

</div>

</div>
</div>

<!--
A Gaussian Mixture Model is defined by its generative story — an explicit, two-step recipe for how a data point is imagined to have been produced, which is the same "generative" framing used for Naive Bayes earlier in the course. Step 1, choose a component: there are K components (clusters), each with a mixing weight π_k giving the probability of picking that component; sample a component index k with probability π_k, exactly like rolling a K-sided weighted die. Step 2, generate a point: given the chosen component k, draw x from that component's own multivariate Gaussian distribution, N(x | μ_k, Σ_k), with its own mean μ_k and covariance matrix Σ_k. The constraint Σ_k π_k = 1 simply says the K mixing weights form a valid probability distribution over "which component," exactly like class priors in Naive Bayes.

The formula p(x) = Σ_k π_k N(x|μ_k,Σ_k) marginalizes out the unobserved component identity: it says the overall probability density at any point x is a weighted sum of each component's density, weighted by how likely that component was to be chosen in the first place. This is worth contrasting with k-means directly: k-means represents each cluster with a single point (its centroid); a GMM represents each cluster with an entire probability distribution, which can be wide or narrow, and — once Σ_k is allowed to be a full (not just diagonal) covariance matrix — tilted at an angle or stretched more along one direction than another. Summing several individually simple, unimodal Gaussian bumps produces a flexible, potentially multimodal density that no single Gaussian could represent alone — the classic picture is two 1D bell curves of different heights and widths, placed at different locations, whose sum has two visible peaks. Transition: given a fitted GMM, the next question is how to use it to actually assign points to clusters.
-->

---
glowSeed: 772
---

# Responsibilities Are Soft Assignments

<div class="grid grid-cols-2 gap-8 items-start">
<div>
<div class="space-y-3 mt-4">
<div v-click border="2 solid white/5" bg="white/5" rounded-lg px-4 py-3>
<span class="font-bold text-teal-300">Posterior membership</span>
<span class="text-sm opacity-85"> — Each point receives a probability for every component.</span>
</div>
<div v-click border="2 solid white/5" bg="white/5" rounded-lg px-4 py-3>
<span class="font-bold text-blue-300">Bayes’ theorem</span>
<span class="text-sm opacity-85"> — Prior × likelihood, normalized across components.</span>
</div>
<div v-click border="2 solid white/5" bg="white/5" rounded-lg px-4 py-3>
<span class="font-bold text-amber-300">Boundary uncertainty</span>
<span class="text-sm opacity-85"> — Ambiguous points can split responsibility between clusters.</span>
</div>
</div>
</div>
<div>
<div v-click class="mt-4" style="font-size: .9em" border="2 solid teal-800" bg="teal-800/20" rounded-lg px-4 py-3>

$$
\gamma_{ik}=P(z_i=k\mid x_i)=\frac{\pi_k\mathcal N(x_i\mid\mu_k,\Sigma_k)}{\sum_j\pi_j\mathcal N(x_i\mid\mu_j,\Sigma_j)}
$$

</div>

</div>
</div>

<!--
This is a direct application of Bayes' theorem, exactly as introduced in the Mathematical Foundations probability material and reused for Naive Bayes: given an observed point x_i, we want P(z_i=k | x_i), the posterior probability that x_i was generated by component k — this quantity is called the "responsibility" γ_ik, since it measures how responsible component k is for having produced that point. The prior is π_k, the mixing weight (how common component k is overall, before seeing any data). The likelihood is N(x_i | μ_k, Σ_k), how plausible x_i looks under component k's specific Gaussian. Multiplying prior times likelihood gives an unnormalized score for each component, and dividing by the sum of that same product across every component j normalizes the K scores into a valid probability distribution that sums to 1 over k — precisely the same "sum in the denominator, same for every class, just for normalization" structure as the Naive Bayes posterior.

The crucial contrast with k-means: k-means' assignment step asks "which single centroid is nearest?" and commits fully to that one answer, a hard 0-or-1 assignment. GMM's responsibility γ_ik is a soft, graded number between 0 and 1 for every component simultaneously — a point sitting near the boundary between two components' distributions might get γ_ik ≈ 0.6 for component 1 and γ_ik ≈ 0.4 for component 2, honestly representing genuine ambiguity about which cluster it belongs to, rather than forcing an artificial hard choice the data does not clearly support. Points near a component's mean, far from any other component, will have γ_ik ≈ 1 for that component and ≈ 0 for all others — soft assignment does not mean every point is ambiguous, only that ambiguous points are allowed to be represented as such. Transition: responsibilities answer "given the current parameters, how likely is each point's component membership" — the next slide covers how those parameters themselves get fit from data.
-->

---
glowSeed: 773
---

# Expectation–Maximization

<div class="grid grid-cols-2 gap-8 items-start">
<div>
<div class="space-y-3 mt-4">
<div v-click border="2 solid white/5" bg="white/5" rounded-lg px-4 py-3>
<span class="font-bold text-teal-300">E-step</span>
<span class="text-sm opacity-85"> — Compute responsibilities using current parameters.</span>
</div>
<div v-click border="2 solid white/5" bg="white/5" rounded-lg px-4 py-3>
<span class="font-bold text-blue-300">M-step</span>
<span class="text-sm opacity-85"> — Update means, covariances, and mixing weights using weighted statistics.</span>
</div>
<div v-click border="2 solid white/5" bg="white/5" rounded-lg px-4 py-3>
<span class="font-bold text-amber-300">Repeat</span>
<span class="text-sm opacity-85"> — Likelihood improves until convergence to a local optimum.</span>
</div>
</div>
</div>
<div>
<div class="mt-5" role="img" aria-label="Initialize then E: soft assign then M: update then Converged?">
<div v-click class="flex items-center gap-3">
<div class="w-8 h-8 rounded-full bg-teal-500/20 border-2 border-teal-700 flex items-center justify-center text-sm font-bold">1</div>
<div class="flex-1 rounded-lg border-2 border-white/10 bg-white/5 px-3 py-2 text-sm font-bold">Initialize</div>
</div>
<div class="ml-4 h-1 border-l-2 border-teal-400/50"></div>
<div v-click class="flex items-center gap-3">
<div class="w-8 h-8 rounded-full bg-blue-500/20 border-2 border-blue-700 flex items-center justify-center text-sm font-bold">2</div>
<div class="flex-1 rounded-lg border-2 border-white/10 bg-white/5 px-3 py-2 text-sm font-bold">E: soft assign</div>
</div>
<div class="ml-4 h-1 border-l-2 border-teal-400/50"></div>
<div v-click class="flex items-center gap-3">
<div class="w-8 h-8 rounded-full bg-amber-500/20 border-2 border-amber-700 flex items-center justify-center text-sm font-bold">3</div>
<div class="flex-1 rounded-lg border-2 border-white/10 bg-white/5 px-3 py-2 text-sm font-bold">M: update</div>
</div>
<div class="ml-4 h-1 border-l-2 border-teal-400/50"></div>
<div v-click class="flex items-center gap-3">
<div class="w-8 h-8 rounded-full bg-violet-500/20 border-2 border-violet-700 flex items-center justify-center text-sm font-bold">4</div>
<div class="flex-1 rounded-lg border-2 border-white/10 bg-white/5 px-3 py-2 text-sm font-bold">Converged?</div>
</div>
</div>
<div v-click class="mt-4" style="font-size: .9em" border="2 solid teal-800" bg="teal-800/20" rounded-lg px-4 py-3>

$$
\mu_k=\frac{\sum_i\gamma_{ik}x_i}{\sum_i\gamma_{ik}},\qquad \pi_k=\frac1n\sum_i\gamma_{ik}
$$

</div>
</div>
</div>

<!--
Expectation-Maximization (EM) fits a GMM's parameters (every π_k, μ_k, Σ_k) by alternating between two easy steps, exactly mirroring the structure of Lloyd's algorithm from the k-Means deck — this parallel is worth drawing explicitly, since it is the cleanest way to understand EM. The E-step ("Expectation"): with the current parameter estimates held fixed, compute every responsibility γ_ik using the Bayes'-theorem formula from the previous slide — this is the direct soft analogue of k-means' hard "assign" step. The M-step ("Maximization"): with the responsibilities held fixed, re-estimate the parameters that best explain the data given those (now known) soft memberships — the direct analogue of k-means' "update centroids to the mean" step.

Walk through the M-step formulas shown: μ_k = (Σ_i γ_ik x_i) / (Σ_i γ_ik) is a responsibility-weighted average of every point, not a plain average over only the points "in" cluster k (there is no such hard set anymore) — points with higher responsibility for component k pull its mean toward them more strongly, while points with near-zero responsibility barely influence it at all. This is the natural soft generalization of k-means' μ_k = mean of C_k: if every γ_ik were forced to be exactly 0 or 1 (hard assignment) instead of a graded probability, this formula collapses exactly to k-means' update rule — a first concrete hint of the deeper equivalence covered on the closing slide. π_k = (1/n) Σ_i γ_ik re-estimates each mixing weight as the average responsibility component k received across all n points — literally "what fraction of the data, weighted by soft membership, does this component account for." (Σ_k, the covariance update, follows the same responsibility-weighted-average logic applied to the outer product of centered points, omitted here for brevity but implemented identically in scikit-learn.)

Just as with Lloyd's algorithm, each E-step and M-step can only improve (or leave unchanged) the data's overall log-likelihood under the model — this is a theorem, not a coincidence — so EM is guaranteed to converge, but only to a local optimum, since the underlying log-likelihood surface is non-convex. Initialization sensitivity and the practical fixes (multiple random restarts, `k-means++`-style seeding) apply to GMM/EM for exactly the same reason they applied to k-means. Transition: this is the algorithm scikit-learn runs when you call `.fit()` — the next slide shows the actual API.
-->

---
glowSeed: 773.5
---

# A Worked Responsibility Calculation

<div class="grid grid-cols-2 gap-7 mt-3 items-center">
<div>

<div border="2 solid white/10" bg="white/5" rounded-lg p-4 class="text-sm">
Two 1D components: $\pi_1=\pi_2=0.5$, $\mathcal N(\mu_1{=}0,\sigma_1{=}1)$, $\mathcal N(\mu_2{=}4,\sigma_2{=}1)$. Point $x=1.5$.
</div>

<v-clicks>

- $\mathcal N(1.5\mid 0,1)=\frac{1}{\sqrt{2\pi}}e^{-1.5^2/2}\approx0.1295$
- $\mathcal N(1.5\mid 4,1)=\frac{1}{\sqrt{2\pi}}e^{-2.5^2/2}\approx0.0175$
- unnormalized: $.5(.1295)=.0648$ and $.5(.0175)=.0088$
- $\gamma_{i1}=\dfrac{.0648}{.0648+.0088}\approx0.880,\quad \gamma_{i2}\approx0.120$

</v-clicks>

</div>

```python
import numpy as np
from scipy.stats import norm

x = 1.5
pi = [0.5, 0.5]
lik = [norm.pdf(x, 0, 1), norm.pdf(x, 4, 1)]
unnorm = [p * l for p, l in zip(pi, lik)]
resp = [u / sum(unnorm) for u in unnorm]
assert round(resp[0], 2) == 0.88
```

</div>

<!--
Ground the abstract Bayes'-theorem formula in real numbers. The point x=1.5 sits closer to component 1's mean (0) than component 2's mean (4), so intuitively it should be assigned mostly to component 1 — this calculation confirms exactly how much "mostly." Evaluate each component's Gaussian density at x=1.5 using the standard normal PDF formula: component 1 gives about 0.1295 (x is only 1.5 standard deviations from its mean), component 2 gives about 0.0175 (x is 2.5 standard deviations from its mean, in the thinner tail). Multiply each by its mixing weight (0.5 for both, so this step doesn't favor either component here) to get unnormalized scores 0.0648 and 0.0088.

Normalize by dividing each by their sum, 0.0736: γ_i1 ≈ 0.880 and γ_i2 ≈ 0.120. Notice this point is NOT hard-assigned to component 1 the way k-means would assign it to whichever centroid is nearest — it retains a genuine, quantified 12% responsibility for component 2, reflecting that x=1.5, while closer to 0, is not implausibly far from 4 either given each component's spread (σ=1). If x had been exactly at the midpoint, 2.0, symmetry would give γ_i1=γ_i2=0.5 exactly — maximum genuine ambiguity, honestly represented rather than arbitrarily broken. This single-point calculation is exactly what the E-step performs for every point in the dataset, all at once, on every iteration. Transition: now see this machinery running end-to-end in scikit-learn.
-->

---
glowSeed: 774
---

# Fit and Inspect a GMM

<div class="grid grid-cols-2 gap-4 mt-6">
<div v-click border="2 solid teal-800" bg="teal-800/20" rounded-lg p-4>
<div class="font-bold text-teal-300 mb-2">predict_proba</div>
<div class="text-sm leading-relaxed opacity-90">Returns responsibilities whose rows sum to one.</div>
</div>
<div v-click border="2 solid blue-800" bg="blue-800/20" rounded-lg p-4>
<div class="font-bold text-blue-300 mb-2">predict</div>
<div class="text-sm leading-relaxed opacity-90">Uses the largest responsibility when a hard label is needed.</div>
</div>
</div>

```python
from sklearn.mixture import GaussianMixture

gmm = GaussianMixture(
    n_components=3, covariance_type="full", random_state=0,
)
gmm.fit(X)
responsibility = gmm.predict_proba(X)

assert responsibility.shape == (len(X), 3)
assert np.allclose(responsibility.sum(axis=1), 1)
```

<!--
This is the practical scikit-learn workflow implementing everything derived so far. `GaussianMixture(n_components=3, covariance_type="full")` sets up a 3-component mixture where each component gets its own full (unconstrained) covariance matrix — flag the `covariance_type` parameter explicitly, since it is a real modeling choice with real consequences: `"full"` allows each component to be independently tilted, elongated, and scaled (the most flexible, most parameter-hungry option); `"diag"` restricts each component's covariance to a diagonal matrix, allowing different variance per feature but no tilt/correlation between features; `"tied"` forces every component to share one common covariance matrix (only means differ, closest in spirit to k-means' implicit assumption); `"spherical"` restricts each component to a single scalar variance in every direction — genuinely spherical Gaussians, the most constrained and most similar to plain k-means. `.fit(X)` runs the EM loop from the previous two slides to convergence.

`predict_proba(X)` returns exactly the responsibility matrix γ derived by hand two slides ago — one row per data point, one column per component, and the assertion confirms each row sums to 1 (a valid probability distribution over "which component generated this point"), exactly as guaranteed by the normalization step in the responsibility formula. `predict(X)`, in contrast, collapses each row down to a single hard label by taking `argmax` over the responsibilities — useful when a downstream step genuinely needs one label per point (e.g., coloring a scatter plot), but it discards the soft-membership information that is GMM's whole point; prefer `predict_proba` whenever the ambiguity itself is informative. In a live demo, plot points colored by their dominant responsibility and note that points near a true cluster's center get responsibilities near 1.0 for their component, while points near the boundary between two components show visibly blended probabilities (e.g., 0.6/0.4) — exactly the qualitative behavior the worked example two slides ago quantified for a single point. Transition: this flexibility is not free — the next slide names its cost.
-->

---
glowSeed: 775
---

# What GMM Fixes—and Costs

<div class="grid grid-cols-3 gap-4 mt-6">
<div v-click border="2 solid teal-800" bg="teal-800/20" rounded-lg p-4>
<div class="font-bold text-teal-300 mb-2">More flexible</div>
<div class="text-sm leading-relaxed opacity-90">Full covariance supports tilted, elongated, differently sized clusters and soft membership.</div>
</div>
<div v-click border="2 solid blue-800" bg="blue-800/20" rounded-lg p-4>
<div class="font-bold text-blue-300 mb-2">More parameters</div>
<div class="text-sm leading-relaxed opacity-90">Each component estimates a covariance matrix as well as a mean.</div>
</div>
<div v-click border="2 solid amber-800" bg="amber-800/20" rounded-lg p-4>
<div class="font-bold text-amber-300 mb-2">Tradeoff</div>
<div class="text-sm leading-relaxed opacity-90">Needs more data and can face numerical instability in high dimension.</div>
</div>
</div>


<!--
Directly map this slide back to the "Where k-Means Fails" slide from the previous deck, since GMM fixes several of those failure modes by name. Full covariance matrices fix the "nonconvex shapes cannot be captured by one centroid" and "unequal sizes" problems: a component with an elongated, tilted Σ_k can represent a cigar-shaped or diagonal cluster that no single spherical centroid could, and each component's Σ_k is fit independently, so components can have genuinely different sizes and shapes rather than k-means' implicit assumption of roughly equal spherical clusters. Soft membership fixes the artificial-hard-boundary problem: points genuinely near a boundary between two true clusters get a probability split reflecting real ambiguity instead of being forced into one bucket by whichever centroid happens to be a hair closer.

The cost is real and worth stating with actual numbers: a k-means centroid in d dimensions needs only d parameters (the mean); a full-covariance Gaussian component needs d parameters for the mean plus d(d+1)/2 parameters for its symmetric covariance matrix — for d=10 features, that is 10 mean parameters but 55 covariance parameters per component, and the count grows quadratically with dimension. More free parameters means more data is needed to estimate them reliably (the same statistical-power concern that motivates preferring simpler models when data is scarce, echoing the bias-variance tradeoff), and in high dimensions with limited data, `covariance_type="full"` can produce numerically unstable or singular covariance estimates — a common practical fix is to use a more constrained `covariance_type` (`"diag"`, `"tied"`, or `"spherical"`, defined on the previous slide) as a form of regularization, trading some flexibility back for stability, exactly the same bias-variance logic that motivated ridge and lasso in the regression module. Transition: with the flexibility/cost tradeoff on the table, choosing how many components K to fit needs a principled way to penalize that added complexity — which is exactly what AIC/BIC do.
-->

---
glowSeed: 776
---

# Choose Components With Information Criteria

<div class="grid grid-cols-2 gap-8 items-start">
<div>
<div class="space-y-3 mt-4">
<div v-click border="2 solid white/5" bg="white/5" rounded-lg px-4 py-3>
<span class="font-bold text-teal-300">Likelihood rewards fit</span>
<span class="text-sm opacity-85"> — More components can always explain the sample better.</span>
</div>
<div v-click border="2 solid white/5" bg="white/5" rounded-lg px-4 py-3>
<span class="font-bold text-blue-300">AIC / BIC penalize complexity</span>
<span class="text-sm opacity-85"> — Extra free parameters must earn their keep.</span>
</div>
<div v-click border="2 solid white/5" bg="white/5" rounded-lg px-4 py-3>
<span class="font-bold text-amber-300">Decision</span>
<span class="text-sm opacity-85"> — Prefer the K with the smallest criterion.</span>
</div>
</div>
</div>
<div>
<svg role="img" aria-label="Log-likelihood rises monotonically with more components while BIC forms a U-shape with a minimum at K=3" viewBox="0 0 500 310" class="w-full max-w-xl mx-auto mt-7">
  <line x1="55" y1="260" x2="470" y2="260" stroke="#64748b" stroke-width="2"/><line x1="55" y1="35" x2="55" y2="260" stroke="#64748b" stroke-width="2"/>
  <path d="M65 230 C130 170,200 110,261 80 S390 45,457 38" fill="none" stroke="#60a5fa" stroke-width="4" stroke-dasharray="9 7"/>
  <path d="M65 200 C130 140,200 100,261 95 S390 130,457 175" fill="none" stroke="#2dd4bf" stroke-width="5"/>
  <circle cx="261" cy="95" r="7" fill="#f8fafc"/>
  <g fill="#cbd5e1" style="font-size: 12px" text-anchor="middle"><text x="65" y="285">1</text><text x="163" y="285">2</text><text x="261" y="285">3</text><text x="359" y="285">4</text><text x="457" y="285">5 components</text></g>
  <g style="font-size: 12px"><text x="380" y="30" fill="#93c5fd">log-likelihood (always rises)</text><text x="270" y="115" fill="#5eead4">BIC (min at K=3)</text></g>
</svg>
<div v-click class="mt-4" style="font-size: .9em" border="2 solid teal-800" bg="teal-800/20" rounded-lg px-4 py-3>

$$
\mathrm{BIC}=-2\log\hat L+p\log n,\qquad \mathrm{AIC}=-2\log\hat L+2p
$$

</div>
</div>
</div>

<!--
This is the direct GMM analogue of the elbow/silhouette diagnostics used to pick K for k-means, but the underlying logic is closer to the regularization tradeoffs from the regression module. Log-likelihood, log(L-hat), measures how well the fitted mixture explains the observed data, and — exactly like k-means' inertia always decreasing as K grows — log-likelihood can only ever improve (or stay flat) as more components are added, because a model with more components is strictly more flexible and can always fit the training sample at least as well; using raw log-likelihood alone to pick K would always select the maximum K allowed, chasing noise rather than true structure, the unsupervised-learning version of overfitting.

AIC and BIC fix this the same way a regularization penalty fixes overfitting in supervised learning: both add a complexity penalty to the negative log-likelihood, so a candidate K only wins if its improved fit is large enough to justify its added parameter count p (recall from the previous slide: p grows with both K and the chosen covariance_type). BIC = -2 log(L-hat) + p·log(n) penalizes each parameter by log(n), so the penalty grows with sample size — for large n, BIC pushes toward simpler models than AIC does, which uses a flat penalty of 2p regardless of n (AIC = -2 log(L-hat) + 2p). Since both formulas are framed as things to minimize (not maximize, unlike log-likelihood itself), lower is better: read the chart as log-likelihood climbing without bound while BIC dips to a genuine minimum at K=3 before rising again as the penalty for extra parameters outweighs the shrinking fit improvement — that minimum is the model-selection answer, chosen from held-out reasoning about complexity rather than raw fit quality.

Practical guidance: BIC is the more common default for choosing GMM components specifically because it more aggressively favors parsimony, which tends to avoid the overfitting failure mode more reliably than AIC when n is reasonably large (the typical case); scikit-learn exposes both directly via `GaussianMixture.bic(X)` and `.aic(X)`, so a simple loop over candidate K values, refitting and recording each score, reproduces this chart with real numbers. Transition: with model selection covered, the deck closes by tying every piece — mixtures, EM, soft assignment, model selection — back to k-means explicitly.
-->

---
glowSeed: 777
---

# Probabilistic Clustering

<div class="mt-8"><div class="grid grid-cols-3 gap-4 mt-6">
<div v-click border="2 solid teal-800" bg="teal-800/20" rounded-lg p-4>
<div class="font-bold text-teal-300 mb-2">Mixture</div>
<div class="text-sm leading-relaxed opacity-90">Weighted Gaussian components.</div>
</div>
<div v-click border="2 solid blue-800" bg="blue-800/20" rounded-lg p-4>
<div class="font-bold text-blue-300 mb-2">EM</div>
<div class="text-sm leading-relaxed opacity-90">Soft assign, then update.</div>
</div>
<div v-click border="2 solid amber-800" bg="amber-800/20" rounded-lg p-4>
<div class="font-bold text-amber-300 mb-2">BIC / AIC</div>
<div class="text-sm leading-relaxed opacity-90">Balance fit and complexity.</div>
</div>
</div></div>

<div v-click class="mt-10 text-center text-lg" border="2 solid white/10" bg="white/5" rounded-lg px-6 py-4>Next: neural networks return to supervised learning with composable nonlinear models.</div>

<!--
Close by making the k-means/GMM connection fully explicit, since it has been building throughout this deck. Take a GMM with equal mixing weights (π_k = 1/K for every k), spherical covariance shared across all components (Σ_k = σ²I for every k), and let σ² → 0. In that limit, the responsibility formula's Gaussian densities become so sharply peaked that the responsibility γ_ik for a point's single nearest component (by Euclidean distance to μ_k) goes to 1, and every other component's responsibility goes to 0 — soft assignment collapses into exactly k-means' hard nearest-centroid assignment. Simultaneously, the M-step's responsibility-weighted mean μ_k = (Σ_i γ_ik x_i)/(Σ_i γ_ik) collapses into k-means' plain average of the points hard-assigned to cluster k, since every γ_ik is now exactly 0 or 1. So k-means is not a different algorithm from GMM/EM — it is the specific limiting case where every component is forced to be an identical, infinitesimally narrow sphere.

That equivalence explains, in one stroke, every difference catalogued across these two decks: GMM's full covariance matrices are what let it represent tilted, elongated, and differently-sized clusters that k-means' implicit spherical assumption cannot; GMM's soft responsibilities are what let it represent genuine boundary ambiguity that k-means' hard assignment forces into an arbitrary choice; and that added flexibility is exactly what costs GMM its extra parameters, its need for more data, and its AIC/BIC-based model-selection step in place of k-means' simpler elbow/silhouette diagnostics. Both algorithms fit into the exact same broader theme running through this entire unit — discover structure without labeled targets, using variants of an iterative "estimate, then refit" loop (Lloyd's algorithm and EM are both instances of a more general alternating-optimization strategy).

Transition to the next deck: both k-means and GMM clustered points using their raw features directly, which becomes difficult and unreliable in high dimensions (the same curse-of-dimensionality concern raised for k-NN back in the Supervised Learning - Classification module — in high dimensions, meaningful distance comparisons break down for clustering just as they did for nearest-neighbor classification). The next deck, Dimensionality Reduction, covers PCA, t-SNE, and UMAP — techniques often used specifically as a preprocessing step before clustering high-dimensional data, projecting it down to a lower-dimensional space where distance-based methods like k-means and GMM work reliably again.
-->
