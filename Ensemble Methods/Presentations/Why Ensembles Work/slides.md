---
theme: default
highlighter: shiki
css: unocss
colorSchema: dark
title: 'Why Ensembles Work'
info: |
  ## Why Ensembles Work
  Diversity turns many imperfect models into one stronger model
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
glowSeed: 670
---

# Why Ensembles Work

### Diversity turns many imperfect models into one stronger model

<div class="pt-8 opacity-80 text-lg">Ensemble Methods · Foundations of Machine Learning</div>

<div class="mt-14 flex justify-center gap-4" aria-hidden="true">
<div class="w-28 h-3 rounded-full bg-teal-400/70"></div>
<div class="w-20 h-3 rounded-full bg-blue-400/60"></div>
<div class="w-14 h-3 rounded-full bg-violet-400/50"></div>
</div>

<!--
The first two decks in this unit each gave you a concrete recipe: bootstrap-and-average (bagging, random forests), and sequentially-reweight-or-fit-residuals (AdaBoost, gradient boosting). Both worked, but both were justified mostly by intuition — dartboards, residual correction. This closing deck makes the justification rigorous and, just as importantly, states its limits precisely.

Roadmap: why diversity among models — not just averaging more copies of the same model — is the actual mechanism that helps → a full derivation of the variance of an averaged ensemble as a function of B (ensemble size) and ρ (pairwise error correlation), which is the formula that governs everything bagging and random forests do → a second, complementary argument for classification specifically — majority voting among independent, better-than-chance classifiers — with a worked numeric example → unifying bagging and boosting under one bias–variance lens → and finally, the honest limits: what ensembling cannot do. This is also the natural closing point of the supervised-learning arc of the course, so the deck ends by looking ahead to unsupervised learning.
-->

---
glowSeed: 671
---

# Diversity Is the Essential Ingredient

<div class="grid grid-cols-3 gap-4 mt-6">
<div v-click border="2 solid teal-800" bg="teal-800/20" rounded-lg p-4>
<div class="font-bold text-teal-300 mb-2">Identical errors</div>
<div class="text-sm leading-relaxed opacity-90">Perfectly correlated models fail on the same cases; averaging changes nothing.</div>
</div>
<div v-click border="2 solid blue-800" bg="blue-800/20" rounded-lg p-4>
<div class="font-bold text-blue-300 mb-2">Different errors</div>
<div class="text-sm leading-relaxed opacity-90">Less-correlated mistakes partially cancel when predictions are combined.</div>
</div>
<div v-click border="2 solid amber-800" bg="amber-800/20" rounded-lg p-4>
<div class="font-bold text-amber-300 mb-2">How algorithms create it</div>
<div class="text-sm leading-relaxed opacity-90">Bootstrap samples, feature subsets, and corrective reweighting manufacture diversity.</div>
</div>
</div>


<!--
Start with the thought experiment that motivates the whole deck. Suppose you train 100 copies of the exact same deterministic model on the exact same data — no randomness anywhere. Every copy makes exactly the same predictions and exactly the same mistakes. Averaging (or voting among) those 100 identical models produces exactly the same output as any one of them; you have paid 100× the compute for zero improvement. This is the "identical errors" card, and it is the key fact that explains why the previous two decks went to so much trouble to inject randomness or corrective structure — averaging only helps to the extent that the things being averaged actually disagree with each other, specifically in ways where their errors are not the same errors.

The "different errors" card is the flip side and the actual mechanism: if two models tend to be wrong on different examples (their errors are less than perfectly correlated), then combining them lets each one's mistakes get outvoted or diluted by the other's correct answer on that example. This is not about the individual models being more accurate in isolation — it's purely about how their disagreements interact when combined. The next slide makes this quantitative.

The "how algorithms create it" card is an explicit recap tying this deck back to the mechanisms already covered: bagging creates diversity via bootstrap resampling of rows (each tree trains on a different, overlapping subset of data); random forests add feature subsampling at each split specifically to push correlation down further, because bootstrap resampling alone leaves trees more correlated than we'd like when one feature dominates; boosting creates a different kind of diversity — not statistical independence, but deliberate specialization, where each new learner is built to be good exactly where the current ensemble is weak. Reframe both bagging and boosting through this single lens before moving to the formula: every ensemble method in this unit is, underneath its specific mechanics, a way of manufacturing useful disagreement.
-->

---
glowSeed: 672
---

# Variance of an Averaged Ensemble

<div class="grid grid-cols-2 gap-8 items-start">
<div>
<div class="space-y-3 mt-4">
<div v-click border="2 solid white/5" bg="white/5" rounded-lg px-4 py-3>
<span class="font-bold text-teal-300">Independent models</span>
<span class="text-sm opacity-85"> — When ρ = 0, variance shrinks by a factor of B.</span>
</div>
<div v-click border="2 solid white/5" bg="white/5" rounded-lg px-4 py-3>
<span class="font-bold text-blue-300">Correlated models</span>
<span class="text-sm opacity-85"> — Positive error correlation creates a nonzero floor.</span>
</div>
<div v-click border="2 solid white/5" bg="white/5" rounded-lg px-4 py-3>
<span class="font-bold text-amber-300">Design implication</span>
<span class="text-sm opacity-85"> — Lowering ρ can matter more than merely adding estimators.</span>
</div>
</div>
</div>
<div>
<div v-click class="mt-4" style="font-size: .85em" border="2 solid teal-800" bg="teal-800/20" rounded-lg px-4 py-3>

$$
\operatorname{Var}\!\left(\frac1B\sum_b\hat f_b\right)=\rho\sigma^2+\frac{1-\rho}{B}\sigma^2\ \longrightarrow\ \rho\sigma^2
$$

</div>
<div v-click class="mt-4 text-sm" border="2 solid white/5" bg="white/5" rounded-lg px-4 py-3>
Worked example: σ² = 4 for a single tree, ρ = 0.2 correlation between trees, B = 50. Variance = 0.2·4 + (0.8·4)/50 = 0.8 + 0.064 = 0.864 — most of the reduction already happened; more trees barely help further.
</div>
</div>
</div>

<!--
This is the full formula that the "Why Averaging Reduces Variance" derivation in the Bagging deck deliberately deferred, because it required the idealized independence assumption there. Here we redo the derivation without that assumption. For B predictors each with variance σ² and every pair sharing the same pairwise correlation ρ, the variance of their average expands as (1/B²) times a double sum of covariance terms: B diagonal terms, each equal to σ² (Var(f_b) = σ²), plus B(B−1) off-diagonal terms, each equal to ρσ² (Cov(f_b, f_b') = ρσ² for b ≠ b', by definition of correlation). Summing: (1/B²)[Bσ² + B(B−1)ρσ²] = σ²/B + ρσ²(B−1)/B. As B grows, (B−1)/B → 1, so this simplifies to the formula shown: ρσ² + (1−ρ)σ²/B. Two named terms: (1−ρ)σ²/B is the part that shrinks as you add more models — this is the part bagging's "more trees" lever controls; ρσ² does not depend on B at all — it is a hard floor set entirely by how correlated the models' errors are.

Read the two limits off the formula directly. When ρ = 0 (models genuinely independent), the floor term vanishes and the formula reduces to σ²/B, exactly the idealized result from the Bagging deck — variance keeps shrinking toward zero as B → ∞. When ρ > 0 (the realistic case for bootstrap-resampled trees, which all train on overlapping data), the (1−ρ)σ²/B term still shrinks with B, but it shrinks toward the fixed floor ρσ², not toward zero — no amount of additional trees can push variance below ρσ².

Walk through the worked numeric example carefully: with σ² = 4, ρ = 0.2, B = 50, variance is 0.2 × 4 + (0.8 × 4)/50 = 0.8 + 0.064 = 0.864. Compare this to B = 500: 0.8 + 0.0064 = 0.8064 — barely different from the B = 50 result, because almost the entire achievable reduction already happened by B = 50, and the remaining gap to the floor (0.8) is nearly closed. This is exactly why the design implication card says lowering ρ can matter more than adding estimators: once B is moderately large, spending effort on decorrelating the trees (feature subsampling, as random forests do) moves the needle far more than doubling or tripling the forest size. This is the formal justification for random forests existing at all.
-->

---
glowSeed: 673
---

# Correlation Sets the Variance Floor

<div class="grid grid-cols-2 gap-8 items-start">
<div>
<div class="space-y-3 mt-4">
<div v-click border="2 solid white/5" bg="white/5" rounded-lg px-4 py-3>
<span class="font-bold text-teal-300">ρ = 0</span>
<span class="text-sm opacity-85"> — Variance keeps falling toward zero.</span>
</div>
<div v-click border="2 solid white/5" bg="white/5" rounded-lg px-4 py-3>
<span class="font-bold text-blue-300">ρ = 0.2</span>
<span class="text-sm opacity-85"> — More models help, then flatten near 0.2σ².</span>
</div>
<div v-click border="2 solid white/5" bg="white/5" rounded-lg px-4 py-3>
<span class="font-bold text-amber-300">ρ = 0.5</span>
<span class="text-sm opacity-85"> — A highly correlated ensemble has little room to improve.</span>
</div>
</div>
</div>
<div>
<svg role="img" aria-label="Variance over sigma squared versus ensemble size B for three correlation levels, each flattening at its own rho times sigma squared floor" viewBox="0 0 500 310" class="w-full max-w-xl mx-auto mt-7">
  <line x1="55" y1="260" x2="470" y2="260" stroke="#64748b" stroke-width="2"/>
  <line x1="55" y1="35" x2="55" y2="260" stroke="#64748b" stroke-width="2"/>
  <polyline points="65,35 163,237 261,255 359,258 457,260" fill="none" stroke="#2dd4bf" stroke-width="4"/>
  <polyline points="65,35 163,197 261,211 359,213 457,215" fill="none" stroke="#60a5fa" stroke-width="4" stroke-dasharray="9 7"/>
  <polyline points="65,35 163,136 261,145 359,146 457,147" fill="none" stroke="#f59e0b" stroke-width="4" stroke-dasharray="3 5"/>
  <g fill="#2dd4bf"><circle cx="65" cy="35" r="5"/><circle cx="163" cy="237" r="5"/><circle cx="261" cy="255" r="5"/><circle cx="359" cy="258" r="5"/><circle cx="457" cy="260" r="5"/></g>
  <g fill="#60a5fa"><circle cx="65" cy="35" r="5"/><circle cx="163" cy="197" r="5"/><circle cx="261" cy="211" r="5"/><circle cx="359" cy="213" r="5"/><circle cx="457" cy="215" r="5"/></g>
  <g fill="#f59e0b"><circle cx="65" cy="35" r="5"/><circle cx="163" cy="136" r="5"/><circle cx="261" cy="145" r="5"/><circle cx="359" cy="146" r="5"/><circle cx="457" cy="147" r="5"/></g>
  <g fill="#cbd5e1" style="font-size: 12px" text-anchor="middle"><text x="65" y="285">1</text><text x="163" y="285">10</text><text x="261" y="285">50</text><text x="359" y="285">100</text><text x="457" y="285">500</text></g>
  <text x="260" y="303" fill="#94a3b8" style="font-size: 12px" text-anchor="middle">B (number of models)</text>
  <g style="font-size: 12px"><text x="330" y="45" fill="#5eead4">ρ = 0</text><text x="330" y="63" fill="#93c5fd">ρ = 0.2</text><text x="330" y="81" fill="#fbbf24">ρ = 0.5</text></g>
</svg>

</div>
</div>

<!--
This chart is a direct plot of the formula from the previous slide, variance/σ² = ρ + (1−ρ)/B, for three fixed correlation values across B = 1, 10, 50, 100, 500 — it is the rigorous justification for decorrelating trees, not just an illustration. All three curves start at the same point (B = 1: variance/σ² = 1, since a single model's average is just itself). From there they diverge sharply. The teal ρ = 0 curve keeps descending toward zero across the whole range shown — by B = 500 it is essentially negligible (0.002σ²) — confirming that fully independent models benefit from unlimited averaging. The blue ρ = 0.2 curve drops fast at first (B = 1 to B = 10) but visibly flattens out around 0.2σ² by B = 50, and gains almost nothing moving from B = 50 to B = 500. The amber ρ = 0.5 curve flattens even earlier and even higher, near 0.5σ² — a highly correlated ensemble simply cannot be averaged into low variance no matter how many members it has.

The shape common to all three curves — steep initial drop, then a flat plateau — is the pattern to have students recognize on sight, because it is exactly the diminishing-returns curve real random forests show in practice: going from 10 to 100 trees usually helps noticeably; going from 500 to 5,000 trees usually helps almost imperceptibly, because you are deep in the flat part of one of these curves already. The height of the plateau, not the number of trees, is what a practitioner should focus on improving once B is moderately large — and the height of the plateau is set entirely by ρ. This is the rigorous version of "random forests add feature randomness to decorrelate trees" from the Bagging deck: feature subsampling is a direct, deliberate intervention on ρ, and this chart shows exactly how much that intervention is worth.
-->

---
glowSeed: 674
---

# Majority Vote Beats Any Single Voter

<div class="grid grid-cols-2 gap-8 items-start">
<div>
<div class="space-y-3 mt-4">
<div v-click border="2 solid white/5" bg="white/5" rounded-lg px-4 py-3>
<span class="font-bold text-teal-300">Setup</span>
<span class="text-sm opacity-85"> — B independent classifiers, each correct with probability p &gt; 0.5.</span>
</div>
<div v-click border="2 solid white/5" bg="white/5" rounded-lg px-4 py-3>
<span class="font-bold text-blue-300">Majority correct</span>
<span class="text-sm opacity-85"> — Sum a Binomial(B, p) tail for at least ⌈B/2⌉ correct votes.</span>
</div>
<div v-click border="2 solid white/5" bg="white/5" rounded-lg px-4 py-3>
<span class="font-bold text-amber-300">B → ∞</span>
<span class="text-sm opacity-85"> — Majority-vote accuracy converges to 1, however small the edge over chance.</span>
</div>
</div>
</div>
<div>
<div v-click class="mt-4" style="font-size: .82em" border="2 solid teal-800" bg="teal-800/20" rounded-lg px-4 py-3>

$$
P(\text{majority correct})=\sum_{k=\lceil B/2\rceil}^{B}\binom{B}{k}p^k(1-p)^{B-k}
$$

</div>
<div v-click class="mt-4 text-sm" border="2 solid white/5" bg="white/5" rounded-lg px-4 py-3>
Worked example: p = 0.7, B = 3. Majority correct means 2 or 3 of 3 right:
<code>3·0.7²·0.3 + 0.7³ = 0.441 + 0.343 = 0.784</code> — better than any single 70%-accurate voter. With B = 11 independent voters at p = 0.7, majority accuracy rises to roughly 0.94.
</div>
</div>
</div>

<!--
This is the classification-specific companion to the variance argument, sometimes called the Condorcet Jury Theorem in its original 18th-century voting-theory form, and it deserves equal billing with the variance formula because it is the cleanest possible statement of "why ensembles work" for classifiers specifically. Setup: B classifiers, each independently correct with probability p on a given example, and p is only assumed to be greater than 0.5 — barely better than a coin flip is enough. Combine them by majority vote. The ensemble's prediction is correct whenever at least ⌈B/2⌉ (a majority) of the B individual votes are correct. Since each vote is an independent Bernoulli trial with success probability p, the number of correct votes out of B follows a Binomial(B, p) distribution, and "majority correct" is the probability mass in the upper tail of that binomial — exactly the sum shown in the equation card.

Work the numeric example on the board, it is small enough to compute by hand and it is genuinely persuasive. Three independent classifiers, each 70% accurate (p = 0.7). Majority correct means 2 out of 3 or 3 out of 3 are correct: P(exactly 2 correct) = C(3,2)·0.7²·0.3¹ = 3 × 0.49 × 0.3 = 0.441; P(exactly 3 correct) = 0.7³ = 0.343. Sum: 0.784. So three 70%-accurate voters, combined by majority vote, are collectively 78.4% accurate — a meaningful improvement over any one of them alone, from independence alone, with no other cleverness. Push the example further: at B = 11 independent voters with the same p = 0.7, majority-vote accuracy climbs to roughly 94%, and in the limit as B → ∞, it converges all the way to 1 (Hoeffding's inequality bounds how fast) — provided the crucial independence assumption holds and p stays fixed above 0.5.

Immediately flag the assumption this proof leans on hardest, because it is also this proof's biggest practical weakness: true independence between classifiers. Real ensemble members — bootstrap-resampled trees, boosted stumps — are correlated to varying degrees, exactly as the previous two slides established, so this theorem's clean convergence-to-1 guarantee does not literally hold in practice; it is best read as a best-case bound and an intuition pump, not a promise. The two arguments in this deck — this one and the variance-floor derivation — are really the same idea told twice, once for classification (accuracy of a vote) and once for regression (variance of an average), and both say the same thing: combining helps in proportion to how independent the errors are, and that independence, not the raw count of models, is the resource to optimize.
-->

---
glowSeed: 675
---

# Bias–Variance, Revisited

<div class="grid grid-cols-2 gap-8 items-start">
<div>
<div class="space-y-3 mt-4">
<div v-click border="2 solid white/5" bg="white/5" rounded-lg px-4 py-3>
<span class="font-bold text-teal-300">Bagging / random forests</span>
<span class="text-sm opacity-85"> — Start with a low-bias, high-variance deep tree and reduce variance.</span>
</div>
<div v-click border="2 solid white/5" bg="white/5" rounded-lg px-4 py-3>
<span class="font-bold text-blue-300">Boosting</span>
<span class="text-sm opacity-85"> — Start with high-bias, low-variance stumps and correct systematic error.</span>
</div>
<div v-click border="2 solid white/5" bg="white/5" rounded-lg px-4 py-3>
<span class="font-bold text-amber-300">One framework</span>
<span class="text-sm opacity-85"> — Both methods move a learner toward lower expected test error.</span>
</div>
</div>
</div>
<div>
<div class="mt-5" role="img" aria-label="Base learner then Manufacture diversity then Combine then Lower test error">
<div v-click class="flex items-center gap-3">
<div class="w-8 h-8 rounded-full bg-teal-500/20 border-2 border-teal-700 flex items-center justify-center text-sm font-bold">1</div>
<div class="flex-1 rounded-lg border-2 border-white/10 bg-white/5 px-3 py-2 text-sm font-bold">Base learner</div>
</div>
<div class="ml-4 h-1 border-l-2 border-teal-400/50"></div>
<div v-click class="flex items-center gap-3">
<div class="w-8 h-8 rounded-full bg-blue-500/20 border-2 border-blue-700 flex items-center justify-center text-sm font-bold">2</div>
<div class="flex-1 rounded-lg border-2 border-white/10 bg-white/5 px-3 py-2 text-sm font-bold">Manufacture diversity</div>
</div>
<div class="ml-4 h-1 border-l-2 border-teal-400/50"></div>
<div v-click class="flex items-center gap-3">
<div class="w-8 h-8 rounded-full bg-amber-500/20 border-2 border-amber-700 flex items-center justify-center text-sm font-bold">3</div>
<div class="flex-1 rounded-lg border-2 border-white/10 bg-white/5 px-3 py-2 text-sm font-bold">Combine</div>
</div>
<div class="ml-4 h-1 border-l-2 border-teal-400/50"></div>
<div v-click class="flex items-center gap-3">
<div class="w-8 h-8 rounded-full bg-violet-500/20 border-2 border-violet-700 flex items-center justify-center text-sm font-bold">4</div>
<div class="flex-1 rounded-lg border-2 border-white/10 bg-white/5 px-3 py-2 text-sm font-bold">Lower test error</div>
</div>
</div>

</div>
</div>

<!--
Expected test error decomposes (from the earlier bias–variance unit) into bias² + variance + irreducible noise. This slide's job is to show that bagging and boosting are not two unrelated tricks but two different entry points into that same decomposition, attacking different terms. Bagging and random forests deliberately start from a base learner sitting at the low-bias, high-variance end of the tradeoff — a deep, unpruned tree — precisely because that is where averaging (this deck's variance-floor derivation) has the most room to help; they leave bias essentially where it started and pull variance down toward the ρσ² floor. Boosting deliberately starts from the opposite end — high-bias, low-variance stumps — precisely because sequential, corrective fitting is a bias-reduction mechanism: each round explicitly targets the systematic error (residual, or reweighted mistakes) the ensemble so far still carries, driving bias down round by round, largely independent of averaging or correlation arguments.

Walk the diagram as the shared four-step pipeline underlying both algorithms: choose a base learner appropriate to which error term you intend to attack (step 1); manufacture diversity or corrective structure appropriate to that goal — bootstrap and feature resampling for bagging, reweighting or gradient-fitting for boosting (step 2); combine the resulting models — averaging or majority vote for bagging, weighted sum for boosting (step 3); land at lower expected test error than the base learner alone achieved (step 4). This is "one framework" in the sense that matters for an exam-style question: both are search strategies within the same bias–variance decomposition, just approaching it from opposite starting corners.

This is the theoretical synthesis of the full ensemble unit — if a student internalizes only one slide from these three decks, it should be this one: name the base learner's position in the bias–variance tradeoff, and you can predict which ensembling strategy is appropriate for it.
-->

---
glowSeed: 676
---

# The Limits of Ensembling

<div class="grid grid-cols-2 gap-4 mt-6">
<div v-click border="2 solid teal-800" bg="teal-800/20" rounded-lg p-4>
<div class="font-bold text-teal-300 mb-2">Noise floor</div>
<div class="text-sm leading-relaxed opacity-90">No ensemble can remove irreducible uncertainty in the data.</div>
</div>
<div v-click border="2 solid blue-800" bg="blue-800/20" rounded-lg p-4>
<div class="font-bold text-blue-300 mb-2">Diminishing returns</div>
<div class="text-sm leading-relaxed opacity-90">Additional estimators eventually add little accuracy.</div>
</div>
<div v-click border="2 solid amber-800" bg="amber-800/20" rounded-lg p-4>
<div class="font-bold text-amber-300 mb-2">Latency and compute</div>
<div class="text-sm leading-relaxed opacity-90">Hundreds of models cost more to train and query than one.</div>
</div>
<div v-click border="2 solid violet-800" bg="violet-800/20" rounded-lg p-4>
<div class="font-bold text-violet-300 mb-2">Interpretability</div>
<div class="text-sm leading-relaxed opacity-90">A forest is harder to explain than a single tree.</div>
</div>
</div>


<!--
Every technique in this unit reduces bias or variance; none of them touches the third term of the decomposition, irreducible noise — the genuine randomness in how y relates to x that no model, however combined, can predict away. If two patients with identical measured features sometimes respond differently to the same treatment for reasons not captured in the data, ensembling a thousand trees still cannot resolve that; it is a hard floor on achievable accuracy that this whole unit's machinery cannot touch, distinct from and in addition to the ρσ² correlation floor from earlier in this deck.

Diminishing returns follows directly from the variance-floor chart: once B is past the steep part of the curve, additional estimators buy vanishingly little accuracy improvement, so blindly increasing n_estimators past a few hundred is usually wasted compute for bagging, and for boosting it can actively hurt (per the learning-rate slide in the previous deck) rather than merely plateau.

Latency and compute cost is a deployment-reality point, not a statistical one, and it is easy for students focused on accuracy metrics to forget: a random forest of 500 trees, or a gradient-boosted ensemble of 500 rounds, means every single prediction at serving time requires running the input through 500 models and combining the results — that is 500× the inference cost, memory footprint, and latency of a single tree, which matters enormously for latency-sensitive applications (real-time bidding, on-device inference) even when it's irrelevant for offline batch scoring.

Interpretability closes the list: a single decision tree can be drawn on one page and read like a flowchart — an analyst can trace exactly why one prediction was made. A forest of 500 differently-structured trees, or a boosted sequence of 500 sequential corrections, has no such single readable structure; feature importance (from the Bagging deck) and tools like SHAP values are the practical workarounds, but they are summaries and approximations of the ensemble's behavior, not the same thing as being able to read the decision logic directly. Accuracy is only one axis; deployment cost and explanation burden matter too, and a good practitioner weighs all of these before reaching for an ensemble by default.
-->

---
glowSeed: 677
---

# Why Ensembles Work

<div class="mt-8"><div class="grid grid-cols-3 gap-4 mt-6">
<div v-click border="2 solid teal-800" bg="teal-800/20" rounded-lg p-4>
<div class="font-bold text-teal-300 mb-2">Diversity</div>
<div class="text-sm leading-relaxed opacity-90">Errors must differ.</div>
</div>
<div v-click border="2 solid blue-800" bg="blue-800/20" rounded-lg p-4>
<div class="font-bold text-blue-300 mb-2">Correlation</div>
<div class="text-sm leading-relaxed opacity-90">Sets the variance floor.</div>
</div>
<div v-click border="2 solid amber-800" bg="amber-800/20" rounded-lg p-4>
<div class="font-bold text-amber-300 mb-2">Tradeoffs</div>
<div class="text-sm leading-relaxed opacity-90">Noise, cost, and opacity remain.</div>
</div>
</div></div>

<div v-click class="mt-10 text-center text-lg" border="2 solid white/10" bg="white/5" rounded-lg px-6 py-4>Next: unsupervised learning—finding structure without labels.</div>

<!--
Close the entire ensemble unit by having students restate, in their own words, the three-card summary: diversity is the raw ingredient (identical models gain nothing from combination, per the very first slide of this deck); correlation ρ between ensemble members sets a hard floor on how much variance any amount of averaging can remove, which is the single formula (ρσ² + (1−ρ)σ²/B) that explains why random forests add feature randomness and why more trees eventually stop helping; and even a perfectly-executed ensemble is still bounded by irreducible noise, still costs more to train and serve than a single model, and is still harder to explain — tradeoffs a practitioner weighs deliberately, not incidentally.

Mark the close of the supervised-learning arc explicitly: linear and logistic regression, trees, and now ensembles have all been about learning a function from labeled (x, y) pairs to minimize some notion of expected error, decomposed throughout into bias, variance, and noise. The next unit drops the labels entirely — unsupervised learning asks what structure can be discovered in x alone, without any y to predict, starting with clustering and dimensionality reduction. Take questions before moving to Unsupervised Learning; a good bridging question to pose to the class is whether ensembling ideas (combining multiple models to reduce a specific error term) have any analogue when there is no labeled error to measure in the first place — a preview of ensemble clustering methods some students may encounter later.
-->
