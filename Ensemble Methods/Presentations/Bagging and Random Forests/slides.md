---
theme: default
highlighter: shiki
css: unocss
colorSchema: dark
title: 'Bagging and Random Forests'
info: |
  ## Bagging and Random Forests
  Turn unstable trees into a stable ensemble
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
glowSeed: 610
---

# Bagging and Random Forests

### Turn unstable trees into a stable ensemble

<div class="pt-8 opacity-80 text-lg">Ensemble Methods · Foundations of Machine Learning</div>

<div class="mt-14 flex justify-center gap-4" aria-hidden="true">
<div class="w-28 h-3 rounded-full bg-teal-400/70"></div>
<div class="w-20 h-3 rounded-full bg-blue-400/60"></div>
<div class="w-14 h-3 rounded-full bg-violet-400/50"></div>
</div>

<!--
Welcome back. The previous unit covered decision trees on their own: they split feature space greedily, they can fit training data almost perfectly, and precisely because of that they are unstable — a small change to the training rows can produce a very different tree. This deck asks the natural next question: if a single deep tree is accurate but jumpy, can we keep the accuracy and tame the jumpiness by combining many trees instead of trusting one? The answer is bagging (bootstrap aggregating), and its most successful concrete instance, the random forest.

Roadmap for today: bootstrap sampling (how to manufacture many "fake" training sets from one real one) → bagging (train on each fake set, average the predictions) → why this specifically helps trees more than it helps already-stable models → random forests (bagging plus deliberate feature randomness, to stop the trees from correlating with each other) → out-of-bag evaluation (a nearly free validation score that falls out of the bootstrap procedure) → feature importance and its limits. By the end you should be able to explain, in one sentence, why bagging targets variance and leaves bias essentially unchanged — that sentence is the hinge this entire unit turns on, and the next deck (boosting) will do the mirror-image thing to bias.
-->

---
glowSeed: 611
---

# Bootstrap Sampling

<div class="grid grid-cols-2 gap-8 items-start">
<div>
<div class="space-y-3 mt-4">
<div v-click border="2 solid white/5" bg="white/5" rounded-lg px-4 py-3>
<span class="font-bold text-teal-300">Sample with replacement</span>
<span class="text-sm opacity-85"> — Draw n observations from n rows; repeats are expected.</span>
</div>
<div v-click border="2 solid white/5" bg="white/5" rounded-lg px-4 py-3>
<span class="font-bold text-blue-300">Out-of-bag rows</span>
<span class="text-sm opacity-85"> — About 36.8% of the original rows are absent from one bootstrap sample.</span>
</div>
<div v-click border="2 solid white/5" bg="white/5" rounded-lg px-4 py-3>
<span class="font-bold text-amber-300">Why it matters</span>
<span class="text-sm opacity-85"> — One dataset can imitate many plausible training sets.</span>
</div>
</div>
</div>
<div>
<div v-click class="mt-4" style="font-size: .9em" border="2 solid teal-800" bg="teal-800/20" rounded-lg px-4 py-3>

$$
\left(1-\frac1n\right)^n \longrightarrow e^{-1}\approx0.368
$$

</div>

<div v-click class="mt-4 text-sm" border="2 solid white/5" bg="white/5" rounded-lg px-4 py-3>
Worked example: with <code>n = 1{,}000</code> rows, each bootstrap sample still has 1,000 draws, but roughly <code>0.368 × 1{,}000 ≈ 368</code> rows never get drawn at all — those are that tree's out-of-bag rows.
</div>

</div>
</div>

<!--
A bootstrap sample is built by drawing n rows from an n-row dataset with replacement: every draw picks uniformly at random from all n original rows, including rows already picked, and the draw is independent of every other draw. Because repeats are allowed, a bootstrap sample is not a copy of the original data — some rows appear two or three times, and some rows do not appear at all. That "left-out" set is what we call out-of-bag (OOB) for that particular bootstrap sample.

Derive the 36.8% figure explicitly, it is worth doing on the board. The probability that one specific row is NOT chosen on a single draw is (1 − 1/n). Since the n draws are independent, the probability that row is never chosen across all n draws is (1 − 1/n)^n. As n grows, this expression converges to e^(−1) ≈ 0.368 — a classic limit from calculus (the same limit that defines e). So regardless of dataset size, about 36.8% of rows are left out of any one bootstrap sample, and the complementary ~63.2% appear at least once (often more than once). This is not a design choice we tune; it is a mathematical consequence of sampling n items with replacement from n items, and it is what makes out-of-bag evaluation possible later in this deck — free validation data.

Connect this to the bias–variance thought experiment from the earlier unit: there we imagined redrawing the training set from the population many times to see how much a model's predictions wiggle. Bootstrap resampling does something similar but from a single dataset in hand: it treats the empirical sample as a stand-in for the population and draws "new" training sets from it. It's an approximation, not magic — if your original 1,000 rows are not representative of the true population, no amount of resampling fixes that. But when the sample is reasonably representative, bootstrapping lets one dataset imitate many plausible training sets, which is exactly the raw material bagging needs.
-->

---
glowSeed: 612
---

# Bagging = Bootstrap + Aggregate

<div class="grid grid-cols-2 gap-8 items-start">
<div>
<div class="space-y-3 mt-4">
<div v-click border="2 solid white/5" bg="white/5" rounded-lg px-4 py-3>
<span class="font-bold text-teal-300">Train in parallel</span>
<span class="text-sm opacity-85"> — Fit the same high-variance learner on many bootstrap samples.</span>
</div>
<div v-click border="2 solid white/5" bg="white/5" rounded-lg px-4 py-3>
<span class="font-bold text-blue-300">Combine</span>
<span class="text-sm opacity-85"> — Average for regression; majority vote for classification.</span>
</div>
<div v-click border="2 solid white/5" bg="white/5" rounded-lg px-4 py-3>
<span class="font-bold text-amber-300">Effect</span>
<span class="text-sm opacity-85"> — Variance falls while the base learner's bias changes little.</span>
</div>
</div>
</div>
<div>
<div class="mt-5" role="img" aria-label="Dataset then Bootstrap samples then Deep trees then Average / vote">
<div v-click class="flex items-center gap-3">
<div class="w-8 h-8 rounded-full bg-teal-500/20 border-2 border-teal-700 flex items-center justify-center text-sm font-bold">1</div>
<div class="flex-1 rounded-lg border-2 border-white/10 bg-white/5 px-3 py-2 text-sm font-bold">Dataset</div>
</div>
<div class="ml-4 h-1 border-l-2 border-teal-400/50"></div>
<div v-click class="flex items-center gap-3">
<div class="w-8 h-8 rounded-full bg-blue-500/20 border-2 border-blue-700 flex items-center justify-center text-sm font-bold">2</div>
<div class="flex-1 rounded-lg border-2 border-white/10 bg-white/5 px-3 py-2 text-sm font-bold">Bootstrap samples</div>
</div>
<div class="ml-4 h-1 border-l-2 border-teal-400/50"></div>
<div v-click class="flex items-center gap-3">
<div class="w-8 h-8 rounded-full bg-amber-500/20 border-2 border-amber-700 flex items-center justify-center text-sm font-bold">3</div>
<div class="flex-1 rounded-lg border-2 border-white/10 bg-white/5 px-3 py-2 text-sm font-bold">Deep trees</div>
</div>
<div class="ml-4 h-1 border-l-2 border-teal-400/50"></div>
<div v-click class="flex items-center gap-3">
<div class="w-8 h-8 rounded-full bg-violet-500/20 border-2 border-violet-700 flex items-center justify-center text-sm font-bold">4</div>
<div class="flex-1 rounded-lg border-2 border-white/10 bg-white/5 px-3 py-2 text-sm font-bold">Average / vote</div>
</div>
</div>
<div v-click class="mt-4" style="font-size: .9em" border="2 solid teal-800" bg="teal-800/20" rounded-lg px-4 py-3>

$$
\hat f_{\mathrm{bag}}(x)=\frac1B\sum_{b=1}^B\hat f_b(x)
$$

</div>
</div>
</div>

<!--
Bagging — short for bootstrap aggregating — is the two-step recipe this whole deck builds toward. Step one: draw B bootstrap samples from the training data (B is typically 100–500 for random forests). Step two: fit the same base learner, usually a deep, unpruned decision tree, independently on each bootstrap sample, then combine the B fitted models' predictions — average them for regression, take a majority (or probability-averaged) vote for classification. "Independently" is doing real work in that sentence: each tree is grown on its own bootstrap sample with no knowledge of the others, which is exactly what makes this an easily parallelizable, embarrassingly simple procedure to implement and to reason about.

Reuse the dartboard intuition from bias–variance: imagine B archers, each individually a bit erratic, so their arrows scatter around the bullseye instead of clustering tightly. If their aim is unbiased on average — the scatter is centered on the bullseye, not systematically off to one side — then averaging their B arrow positions lands much closer to the bullseye than any single archer's shot, because the individual errors partially cancel. Bagging is that averaging step applied to trees: each bootstrapped tree is a noisy but roughly-unbiased predictor, and averaging B of them tightens the prediction cloud around the same center. The center itself — the bias — is a property of the base learner and the true relationship, and averaging does very little to move it. Say this explicitly, because it is the single most commonly confused point in this deck and the exam-style question most students miss: bagging is a variance-reduction technique, not a bias-reduction technique. If your base learner is systematically wrong (high bias, e.g., a linear model applied to a strongly nonlinear relationship), bagging a hundred copies of it will still be systematically wrong.
-->

---
glowSeed: 613
---

# Why Averaging Reduces Variance

<div class="grid grid-cols-2 gap-8 items-start">
<div>
<div class="space-y-3 mt-4">
<div v-click border="2 solid white/5" bg="white/5" rounded-lg px-4 py-3>
<span class="font-bold text-teal-300">Assumption</span>
<span class="text-sm opacity-85"> — Treat the B trees as identically distributed with variance σ² each.</span>
</div>
<div v-click border="2 solid white/5" bg="white/5" rounded-lg px-4 py-3>
<span class="font-bold text-blue-300">If independent</span>
<span class="text-sm opacity-85"> — Variance of the average shrinks by a full factor of B.</span>
</div>
<div v-click border="2 solid white/5" bg="white/5" rounded-lg px-4 py-3>
<span class="font-bold text-amber-300">The catch</span>
<span class="text-sm opacity-85"> — Real bootstrap trees are correlated, not independent — the next deck derives the floor this creates.</span>
</div>
</div>
</div>
<div>
<div v-click class="mt-4" style="font-size: .85em" border="2 solid teal-800" bg="teal-800/20" rounded-lg px-4 py-3>

$$
\begin{aligned}
\operatorname{Var}\!\left(\frac1B\sum_{b=1}^B \hat f_b(x)\right) &= \frac{1}{B^2}\sum_{b=1}^B \operatorname{Var}(\hat f_b(x)) \\
&= \frac{1}{B^2}\cdot B\sigma^2 = \frac{\sigma^2}{B}
\end{aligned}
$$

</div>
<div v-click class="mt-4 text-sm" border="2 solid white/5" bg="white/5" rounded-lg px-4 py-3>
Worked example: a single deep tree has prediction variance σ² = 4. Average B = 25 independent trees and the variance drops to 4/25 = 0.16 — a 25× reduction, with the mean (the bias) essentially unchanged.
</div>
</div>
</div>

<!--
This slide makes the "variance falls, bias stays put" claim rigorous rather than just asserted. Start from the definition of variance of a sum: for any random variables, Var(sum) expands into a double sum of covariance terms. If we assume, for a moment, that the B trees are independent of each other (an idealization we will drop in the next deck), every cross term Cov(f_b, f_b') for b ≠ b' is zero, and only the B diagonal variance terms survive, each equal to σ². Pulling the constant 1/B² out front and summing B copies of σ² gives Bσ², so the whole expression collapses to σ²/B. That is the entire derivation — two lines, one assumption. It says that averaging B independent, equally-noisy predictors divides the variance by B, so tripling the number of trees cuts variance to a third, and it keeps falling toward zero as B grows without bound, in principle.

Walk through the worked numeric example explicitly: if a single tree's predictions have variance 4 (think of this as the typical squared deviation of the tree's prediction from the "average tree's" prediction, across many resampled training sets), then 25 independent trees averaged together bring that down to 0.16 — a twenty-five-fold reduction. Crucially, nothing in this derivation touched E[f_b(x)], the expected prediction — averaging does not change where the predictions are centered, only how tightly they cluster there. That is the formal version of "bagging reduces variance, not bias."

Now flag the catch explicitly, because it previews the entire next deck: bootstrap-sampled trees are not actually independent. They are all grown from overlapping resamples of the same original dataset, so their errors are positively correlated. With correlation ρ > 0 between trees, the variance of the average does not go to zero as B → ∞; it approaches a floor of ρσ² instead of 0. Random forests exist specifically to push ρ down — by restricting each split to a random subset of features (next slide) — because lowering the correlation floor is worth more, once B is already reasonably large, than simply growing more trees. Hold that thought; "Why Ensembles Work" derives the full ρσ² + (1−ρ)σ²/B formula and its consequences.
-->

---
glowSeed: 614
---

# Why Trees Are the Natural Base Learner

<div class="grid grid-cols-3 gap-4 mt-6">
<div v-click border="2 solid teal-800" bg="teal-800/20" rounded-lg p-4>
<div class="font-bold text-teal-300 mb-2">Deep decision tree</div>
<div class="text-sm leading-relaxed opacity-90">Low bias, high variance: plenty of instability for averaging to remove.</div>
</div>
<div v-click border="2 solid blue-800" bg="blue-800/20" rounded-lg p-4>
<div class="font-bold text-blue-300 mb-2">Linear regression</div>
<div class="text-sm leading-relaxed opacity-90">Already comparatively stable: bagging has little variance to cancel.</div>
</div>
<div v-click border="2 solid amber-800" bg="amber-800/20" rounded-lg p-4>
<div class="font-bold text-amber-300 mb-2">Design rule</div>
<div class="text-sm leading-relaxed opacity-90">Bagging pays off when base learners are accurate but unstable.</div>
</div>
</div>


<!--
Answer the natural "why not bag everything?" question directly, using the bias–variance framework from the previous unit as the lens. Bagging's entire mechanism of action is variance cancellation through averaging — it has nothing to offer a base learner whose problem is bias, and it can only remove variance that exists in the first place. A grown-out, unpruned decision tree is close to a worst-case example of a low-bias, high-variance learner: it keeps splitting until leaves are pure or tiny, so it can represent almost any function in the training data (low bias), but a single different training row near the top of the tree can send an entirely different sequence of splits cascading down (high variance). That combination — accurate on average, wildly different from run to run — is precisely what bagging is built to fix.

Contrast this with ordinary linear regression fit by least squares. Its coefficients do have some sampling variance, but that variance is typically small and well-behaved relative to a deep tree's, because the model class itself is heavily constrained (a hyperplane, not an arbitrary partition of feature space). Bagging 200 bootstrapped linear regressions produces something extremely close to the single linear regression fit on all the data — there just is not much variance sitting there to cancel, so you pay the 200× compute cost for close to nothing.

State the design rule as a checklist item students can actually apply: reach for bagging when (1) the base learner is expressive enough to be accurate, and (2) that same expressiveness makes it unstable to resampling. Deep trees satisfy both. Shallow trees, linear models, and other high-bias/low-variance learners satisfy neither, and are much better candidates for boosting instead — which is exactly the contrast the "Bagging vs. Boosting" slide in the next deck makes explicit.
-->

---
glowSeed: 615
---

# Random Forests Add Feature Randomness

<div class="grid grid-cols-2 gap-8 items-start">
<div>
<div class="space-y-3 mt-4">
<div v-click border="2 solid white/5" bg="white/5" rounded-lg px-4 py-3>
<span class="font-bold text-teal-300">Correlated trees limit averaging</span>
<span class="text-sm opacity-85"> — A dominant feature can force nearly every bagged tree into the same early splits.</span>
</div>
<div v-click border="2 solid white/5" bg="white/5" rounded-lg px-4 py-3>
<span class="font-bold text-blue-300">Random feature subsets</span>
<span class="text-sm opacity-85"> — At each split, consider only m of the d available features.</span>
</div>
<div v-click border="2 solid white/5" bg="white/5" rounded-lg px-4 py-3>
<span class="font-bold text-amber-300">More diversity</span>
<span class="text-sm opacity-85"> — Different roots and branches reduce correlation between tree errors.</span>
</div>
</div>
</div>
<div>
<svg role="img" aria-label="Three decision trees grown on different random feature subsets, combined by majority vote" viewBox="0 0 460 300" class="w-full max-w-xl mx-auto mt-6">
  <g stroke="#475569" stroke-width="2">
    <line x1="70" y1="45" x2="45" y2="105"/><line x1="70" y1="45" x2="95" y2="105"/>
    <line x1="230" y1="45" x2="205" y2="105"/><line x1="230" y1="45" x2="255" y2="105"/>
    <line x1="390" y1="45" x2="365" y2="105"/><line x1="390" y1="45" x2="415" y2="105"/>
  </g>
  <g stroke="#334155" stroke-width="2" opacity=".8">
    <line x1="70" y1="122" x2="230" y2="222"/>
    <line x1="230" y1="122" x2="230" y2="222"/>
    <line x1="390" y1="122" x2="230" y2="222"/>
  </g>
  <g fill="#0f172a" stroke-width="4">
    <circle cx="70" cy="45" r="18" stroke="#2dd4bf"/>
    <circle cx="230" cy="45" r="18" stroke="#f59e0b"/>
    <circle cx="390" cy="45" r="18" stroke="#a78bfa"/>
    <circle cx="45" cy="105" r="13" stroke="#60a5fa"/><circle cx="95" cy="105" r="13" stroke="#60a5fa"/>
    <circle cx="205" cy="105" r="13" stroke="#60a5fa"/><circle cx="255" cy="105" r="13" stroke="#60a5fa"/>
    <circle cx="365" cy="105" r="13" stroke="#60a5fa"/><circle cx="415" cy="105" r="13" stroke="#60a5fa"/>
  </g>
  <rect x="140" y="222" width="180" height="46" rx="8" fill="#0f172a" stroke="#2dd4bf" stroke-width="3"/>
  <g fill="#cbd5e1" style="font-size: 12px" text-anchor="middle">
    <text x="70" y="140">Tree 1: splits on A</text>
    <text x="230" y="140">Tree 2: splits on C</text>
    <text x="390" y="140">Tree 3: splits on B</text>
    <text x="230" y="250" style="font-size: 13px; font-weight: 700">Majority vote / average</text>
  </g>
</svg>
<div v-click class="mt-4" style="font-size: .9em" border="2 solid teal-800" bg="teal-800/20" rounded-lg px-4 py-3>

$$
m\approx\sqrt d\ \text{for classification (a common default)}
$$

</div>
</div>
</div>

<!--
Here is the problem plain bagging does not solve. Suppose one feature is a strong predictor — say it alone explains most of the signal. Nearly every bootstrap sample still contains enough of that feature's signal to make it the best splitting choice at the root, so nearly every bagged tree starts with the same first split, and often several of the same early splits after that. The trees stop being independent-ish and become highly correlated copies of each other, which is exactly the ρ from the variance formula on the previous slide creeping toward 1 — and correlated errors do not cancel when you average them.

Random forests fix this with one small, deliberate change to how each split is chosen: at every node, instead of searching all d features for the best split, the algorithm restricts the search to a random subset of only m < d features (a fresh random subset is drawn at every single node, not once per tree). This forces trees to occasionally ignore the dominant feature and split on something else, which produces trees with different root splits, different branch structures, and — most importantly — errors that are less correlated with each other. Look at the diagram: three trees drawn from different random feature subsets end up splitting on different top features (A, C, B), so their mistakes are less likely to coincide, and the resulting vote benefits from genuine disagreement rather than three copies of the same opinion.

The formula m ≈ √d is scikit-learn's default for classification (and roughly d/3 for regression) — it is a starting point supported by practice and some theory, not a law; treat it as a hyperparameter worth tuning via cross-validation on a given dataset. Emphasize that random forest = bagging (bootstrap resampling of rows) + this extra feature-subsampling step (restricting columns at each split); dropping the feature randomness and keeping only the row bootstrapping is exactly plain bagging of trees, which is what the previous slides described.
-->

---
glowSeed: 616
---

# Out-of-Bag Evaluation

<div class="grid grid-cols-2 gap-4 mt-6">
<div v-click border="2 solid teal-800" bg="teal-800/20" rounded-lg p-4>
<div class="font-bold text-teal-300 mb-2">For each row</div>
<div class="text-sm leading-relaxed opacity-90">Predict using only trees whose bootstrap sample omitted that row.</div>
</div>
<div v-click border="2 solid blue-800" bg="blue-800/20" rounded-lg p-4>
<div class="font-bold text-blue-300 mb-2">Nearly free validation</div>
<div class="text-sm leading-relaxed opacity-90">Aggregate those predictions into an OOB score without a separate split.</div>
</div>
</div>

```python
from sklearn.ensemble import RandomForestClassifier

rf = RandomForestClassifier(
    n_estimators=200, max_features="sqrt",
    oob_score=True, random_state=0,
)

rf.fit(X, y)
print(rf.oob_score_)
```

<!--
Out-of-bag (OOB) evaluation reuses the ~36.8% of rows that each individual tree never saw, derived on the "Bootstrap Sampling" slide. For a given training row i, collect every tree in the forest whose bootstrap sample happened to leave row i out — with n_estimators=200 and about 36.8% exclusion per tree, row i is typically OOB for roughly 74 of the 200 trees. Have exactly those trees predict on row i (majority vote for classification, average for regression), and compare that OOB prediction to the true label. Do this for every row and aggregate — that aggregate accuracy is the OOB score, rf.oob_score_ in scikit-learn.

The key property to emphasize is that this is a legitimate estimate of test-set performance, obtained without setting aside a validation split and without any extra training runs — each row's OOB prediction comes only from trees that never trained on it, which is exactly the condition a validation set is trying to guarantee. That is why OOB scoring is described as "nearly free": you get held-out-quality evaluation as a byproduct of training the ensemble you already needed to train.

Two caveats worth stating explicitly. First, this shortcut is specific to bootstrap-based ensembles (bagging, random forests) — boosting has no analogous free lunch, because boosting's trees are fit sequentially on reweighted versions of the full dataset, not on held-out row subsets, so you cannot cleanly identify which learners "haven't seen" a given row. Second, OOB scores and k-fold cross-validation scores estimate the same quantity (expected test performance) but are not numerically identical estimators — they can and do differ, typically by a small amount, because they use different resampling schemes. In practice, running 5-fold CV alongside oob_score_ and confirming they roughly agree is a healthy sanity check before trusting either number, especially with a moderate n_estimators where the ~74-tree-per-row OOB sample can itself be somewhat noisy.
-->

---
glowSeed: 617
---

# Feature Importance — Useful, Not Causal

<div class="grid grid-cols-2 gap-8 items-start">
<div>
<div class="space-y-3 mt-4">
<div v-click border="2 solid white/5" bg="white/5" rounded-lg px-4 py-3>
<span class="font-bold text-teal-300">Impurity reduction</span>
<span class="text-sm opacity-85"> — Aggregate how much each feature improves splits across all trees.</span>
</div>
<div v-click border="2 solid white/5" bg="white/5" rounded-lg px-4 py-3>
<span class="font-bold text-blue-300">Practical use</span>
<span class="text-sm opacity-85"> — A quick global view for interpretation and feature screening.</span>
</div>
<div v-click border="2 solid white/5" bg="white/5" rounded-lg px-4 py-3>
<span class="font-bold text-amber-300">Caveats</span>
<span class="text-sm opacity-85"> — High-cardinality and correlated features can distort the ranking.</span>
</div>
</div>
</div>
<div>
<svg role="img" aria-label="Bar chart of impurity-based feature importance, decreasing from f1 to f5" viewBox="0 0 500 310" class="w-full max-w-xl mx-auto mt-7">
  <line x1="55" y1="260" x2="470" y2="260" stroke="#64748b" stroke-width="2"/>
  <line x1="55" y1="35" x2="55" y2="260" stroke="#64748b" stroke-width="2"/>
  <g fill="#2dd4bf">
    <rect x="37" y="60" width="55" height="200" opacity="0.95"/>
    <rect x="135" y="113" width="55" height="147" opacity="0.85"/>
    <rect x="233" y="154" width="55" height="106" opacity="0.75"/>
    <rect x="331" y="183" width="55" height="77" opacity="0.65"/>
    <rect x="429" y="201" width="55" height="59" opacity="0.55"/>
  </g>
  <g fill="#e2e8f0" style="font-size: 12px" text-anchor="middle">
    <text x="65" y="52">0.34</text><text x="163" y="105">0.25</text><text x="261" y="146">0.18</text>
    <text x="359" y="175">0.13</text><text x="457" y="193">0.10</text>
  </g>
  <g fill="#cbd5e1" style="font-size: 12px" text-anchor="middle">
    <text x="65" y="285">f₁</text><text x="163" y="285">f₂</text><text x="261" y="285">f₃</text><text x="359" y="285">f₄</text><text x="457" y="285">f₅</text>
  </g>
  <text x="30" y="30" fill="#94a3b8" style="font-size: 12px">importance</text>
</svg>

</div>
</div>

<!--
Impurity-based feature importance is computed by tracking, for every split in every tree, how much that split reduced impurity (Gini impurity for classification, variance/MSE for regression), weighted by how many training samples passed through that node. Sum this quantity across all splits that used a given feature, across all trees in the forest, then normalize so the importances sum to 1. The bar chart shows a typical shape: one or two features dominate, and the rest trail off — here f1 accounts for 34% of total impurity reduction, down to f5 at 10%.

This is genuinely useful as a quick, nearly-free global summary for interpretation and feature screening — it tells you which features the forest is leaning on, which is valuable for debugging a pipeline, communicating with stakeholders, or deciding what to measure more carefully next time. But stress the caveat hard: this is predictive attribution within the specific model that was fit, not a causal or even a uniquely correct ranking of "true" feature relevance. Two well-known distortions to name explicitly: high-cardinality features (many possible split points, like a raw ID or a fine-grained ZIP code) get inflated importance simply because trees have more candidate splits to try on them, regardless of true signal; and when two features are highly correlated, the tree can split on either one somewhat arbitrarily from sample to sample, so importance gets split between them and each individually looks less important than it really is jointly. Permutation importance (shuffling one feature's column and measuring the drop in held-out performance) is a more robust alternative worth mentioning as the fix for the high-cardinality bias, though it is not covered in depth here.
-->

---
glowSeed: 618
---

# Bagging vs. the Next Idea

<div class="mt-8"><div class="grid grid-cols-3 gap-4 mt-6">
<div v-click border="2 solid teal-800" bg="teal-800/20" rounded-lg p-4>
<div class="font-bold text-teal-300 mb-2">Bootstrap</div>
<div class="text-sm leading-relaxed opacity-90">Simulate many training sets.</div>
</div>
<div v-click border="2 solid blue-800" bg="blue-800/20" rounded-lg p-4>
<div class="font-bold text-blue-300 mb-2">Bagging</div>
<div class="text-sm leading-relaxed opacity-90">Average high-variance learners.</div>
</div>
<div v-click border="2 solid amber-800" bg="amber-800/20" rounded-lg p-4>
<div class="font-bold text-amber-300 mb-2">Random forest</div>
<div class="text-sm leading-relaxed opacity-90">Decorrelate trees with feature randomness.</div>
</div>
</div></div>

<div v-click class="mt-10 text-center text-lg" border="2 solid white/10" bg="white/5" rounded-lg px-6 py-4>Next: boosting trains weak learners sequentially, each correcting what remains wrong.</div>

<!--
Close by tying the three ideas together in the order students should be able to reproduce: bootstrap sampling is the resampling mechanism that manufactures many plausible training sets from one dataset; bagging is what you do with that mechanism — fit the same unstable learner on each resampled set and average the results to cancel variance while leaving bias essentially untouched; and random forests are bagging plus one extra ingredient, per-split feature subsampling, added specifically to decorrelate the trees so the variance floor from correlated errors sits as low as possible. If a student can explain why each layer exists and what specific problem it solves, they have the core of this deck.

Transition explicitly to what's next: everything here has been parallel and independent — B trees, grown all at once, with no communication between them, combined only at the very end by averaging or voting. Boosting inverts that structure entirely. It trains learners sequentially, and each new learner is deliberately built to focus on whatever the ensemble so far still gets wrong, rather than being an independent, unrelated attempt at the whole problem. Where bagging's goal was "cancel variance by averaging independent-ish noisy estimates," boosting's goal will be "reduce bias by relentlessly, sequentially correcting mistakes." Hold onto the variance-vs-bias framing from this deck — the next deck's payoff line is that boosting is bagging's mirror image on exactly that axis.
-->
