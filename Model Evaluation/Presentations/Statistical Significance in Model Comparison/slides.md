---
theme: default
highlighter: shiki
css: unocss
colorSchema: dark
title: 'Statistical Significance in Model Comparison'
info: |
  ## Statistical Significance in Model Comparison
  Is a measured improvement real—or sampling noise?
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
glowSeed: 550
---

# Statistical Significance in Model Comparison

### Is a measured improvement real—or sampling noise?

<div class="pt-8 opacity-80 text-lg">Model Evaluation · Foundations of Machine Learning</div>

<div class="mt-14 flex justify-center gap-4" aria-hidden="true">
<div class="w-28 h-3 rounded-full bg-teal-400/70"></div>
<div class="w-20 h-3 rounded-full bg-blue-400/60"></div>
<div class="w-14 h-3 rounded-full bg-violet-400/50"></div>
</div>

<!--
The last two decks built up a full toolkit of evaluation metrics — accuracy, precision, recall, F1, ROC-AUC, and the confusion matrix they all come from. This deck asks a question none of those tools answer by themselves: if model B scores 91% and model A scores 89% on the same test set, is B actually better, or did it just get a slightly easier random sample of test cases?

Roadmap: treat any test-set score as a random variable, not a fixed truth, then formalize "is this gap real" with the null-hypothesis significance-testing frame, apply McNemar's test to paired classifier predictions with a fully worked numeric example, extend to paired t-tests across cross-validation folds, and finish by separating statistical significance from practical significance — a gap can be "real" and still not be worth the added complexity of deploying it. This is the last piece of rigor before we look at evaluation failures like data leakage in the next deck.
-->

---
glowSeed: 551
---

# Performance Estimates Are Random Variables

<div class="grid grid-cols-2 gap-8 items-start">
<div>
<div class="space-y-3 mt-4">
<div v-click border="2 solid white/5" bg="white/5" rounded-lg px-4 py-3>
<span class="font-bold text-teal-300">A test score is a statistic</span>
<span class="text-sm opacity-85"> — It depends on which observations landed in the test set.</span>
</div>
<div v-click border="2 solid white/5" bg="white/5" rounded-lg px-4 py-3>
<span class="font-bold text-blue-300">Resample, remeasure</span>
<span class="text-sm opacity-85"> — A different split gives a different number for the same procedure.</span>
</div>
<div v-click border="2 solid white/5" bg="white/5" rounded-lg px-4 py-3>
<span class="font-bold text-amber-300">Implication</span>
<span class="text-sm opacity-85"> — "91% vs. 89%" is incomplete without a sense of uncertainty.</span>
</div>
</div>
</div>
<div>
<div v-click class="mt-4" style="font-size: .9em" border="2 solid teal-800" bg="teal-800/20" rounded-lg px-4 py-3>

$$
\widehat{\mathrm{Acc}}=\frac1n\sum_{i=1}^n\mathbf1[\hat y_i=y_i]
$$

</div>

</div>
</div>

<!--
Read the formula symbol by symbol: accuracy-hat is the mean, over the n test examples, of the indicator function 1[·], which equals 1 when the predicted label ŷ_i matches the true label y_i and 0 otherwise — literally "count how many predictions were right, divide by n." That makes accuracy-hat a sample mean, exactly like the sample mean of any other measured quantity, and every sample mean has a sampling distribution: if you drew a different random test set of the same size from the same underlying population, you would get a different accuracy-hat, purely from which examples happened to land in the sample. The n in the denominator directly controls how much this number bounces around — a 100-example test set produces a far noisier accuracy-hat than a 100,000-example one.

This connects directly to the sampling distribution of a sample mean, a concept from introductory statistics: just as a poll of 100 people gives an estimate of a population opinion with a margin of error, a test accuracy of 91% on 200 examples is an estimate with its own margin of error, not a platonic fact about the model. The implication for model comparison: seeing "91% vs. 89%" and declaring the 91% model the winner is exactly like seeing two polls, 51% vs. 49%, and declaring a landslide — the raw numbers alone cannot tell you whether the gap reflects a real difference or is well within the noise you would expect from resampling. The rest of this deck builds tools to make that judgment rigorously instead of by eyeballing two numbers.
-->

---
glowSeed: 552
---

# The Null-Hypothesis Frame

<div class="grid grid-cols-2 gap-8 items-start">
<div>
<div class="space-y-3 mt-4">
<div v-click border="2 solid white/5" bg="white/5" rounded-lg px-4 py-3>
<span class="font-bold text-teal-300">H₀</span>
<span class="text-sm opacity-85"> — The models have equal true performance; the observed gap Δ is noise.</span>
</div>
<div v-click border="2 solid white/5" bg="white/5" rounded-lg px-4 py-3>
<span class="font-bold text-blue-300">p-value</span>
<span class="text-sm opacity-85"> — Probability of a gap at least this large, if H₀ were exactly true.</span>
</div>
<div v-click border="2 solid white/5" bg="white/5" rounded-lg px-4 py-3>
<span class="font-bold text-amber-300">Not what it means</span>
<span class="text-sm opacity-85"> — It is not the probability that H₀ is true, and 0.05 is a convention, not a cliff.</span>
</div>
</div>
</div>
<div>
<svg role="img" aria-label="Bell-shaped null distribution of the performance gap centered at zero, with shaded tails beyond the observed gap marking the p-value" viewBox="0 0 500 310" class="w-full max-w-xl mx-auto mt-6">
  <line x1="55" y1="260" x2="470" y2="260" stroke="#64748b" stroke-width="2"/>
  <path d="M60 255 C140 255 195 60 262 60 C330 60 385 255 465 255" fill="none" stroke="#2dd4bf" stroke-width="4"/>
  <line x1="150" y1="255" x2="150" y2="70" stroke="#f59e0b" stroke-width="2" stroke-dasharray="5 5"/>
  <line x1="378" y1="255" x2="378" y2="70" stroke="#f59e0b" stroke-width="2" stroke-dasharray="5 5"/>
  <line x1="262" y1="260" x2="262" y2="245" stroke="#94a3b8" stroke-width="2"/>
  <g fill="#cbd5e1" style="font-size: 12px" text-anchor="middle">
    <text x="262" y="280">0</text>
    <text x="150" y="280" fill="#fbbf24">−Δ<tspan font-size="9">obs</tspan></text>
    <text x="378" y="280" fill="#fbbf24">+Δ<tspan font-size="9">obs</tspan></text>
  </g>
  <g style="font-size: 12px">
    <text x="262" y="42" fill="#5eead4" text-anchor="middle">sampling distribution of the gap under H₀</text>
    <text x="105" y="235" fill="#fbbf24" text-anchor="middle">tail</text>
    <text x="420" y="235" fill="#fbbf24" text-anchor="middle">tail</text>
  </g>
</svg>

</div>
</div>

<!--
Formalize "is the gap real" with the standard hypothesis-testing recipe. The null hypothesis H₀ states that the two models have equal true performance, so any gap you observed in one experiment is attributable entirely to sampling noise — this is the curve on the slide, the distribution of gaps you would see across many hypothetical resamples if H₀ were exactly correct; it is centered at zero because under H₀ the expected gap is zero. You then compute a p-value: the probability, under that null distribution, of seeing a gap at least as extreme as the one you actually observed, Δ_obs — visualized here as the combined area in the two shaded tails beyond ±Δ_obs. A small p-value means your observed gap would be surprising if the models were truly equal, which is evidence (not proof) against H₀.

Two misconceptions to name explicitly. First, the p-value is not "the probability that H₀ is true" — it is a statement about how surprising the data is, assuming H₀, not a statement about how likely H₀ is given the data; those are different conditional probabilities and confusing them is one of the most common statistical errors. Second, the conventional threshold of 0.05 is exactly that — a convention, not a law of nature or a sharp cliff between "true" and "false." A p-value of 0.04 and a p-value of 0.06 reflect nearly identical evidence; treat significance as a continuum and always report the effect size (the actual magnitude of Δ) alongside the p-value, not the p-value in isolation. The next slide applies this frame to the specific case of two classifiers evaluated on the same test set.
-->

---
glowSeed: 553
---

# McNemar's Test Uses Paired Disagreements

<div class="grid grid-cols-2 gap-8 items-start">
<div>
<div class="space-y-3 mt-4">
<div v-click border="2 solid white/5" bg="white/5" rounded-lg px-4 py-3>
<span class="font-bold text-teal-300">Same test examples</span>
<span class="text-sm opacity-85"> — Each row has a prediction from model A and model B on the identical case.</span>
</div>
<div v-click border="2 solid white/5" bg="white/5" rounded-lg px-4 py-3>
<span class="font-bold text-blue-300">Only discordant cells matter</span>
<span class="text-sm opacity-85"> — n₀₁ = A wrong / B right; n₁₀ = A right / B wrong.</span>
</div>
<div v-click border="2 solid white/5" bg="white/5" rounded-lg px-4 py-3>
<span class="font-bold text-amber-300">Ignore agreements</span>
<span class="text-sm opacity-85"> — Both-right (n₁₁) and both-wrong (n₀₀) do not distinguish the models.</span>
</div>
</div>
</div>
<div>
<div role="img" aria-label="McNemar agreement table: rows model A correct or wrong, columns model B correct or wrong, cells n11 n10 n01 n00" class="mt-4 max-w-lg mx-auto">
<div class="grid grid-cols-[6.5rem_1fr_1fr] gap-2 text-center text-xs">
<div></div><div class="font-bold text-blue-300">B correct</div><div class="font-bold text-blue-300">B wrong</div>
<div class="flex items-center justify-end pr-2 font-bold text-teal-300">A correct</div><div border="2 solid white/10" bg="white/5" rounded-lg p-4><div class="text-lg font-bold">n₁₁</div><div class="text-xs opacity-60">both right</div></div><div border="2 solid red-800" bg="red-800/20" rounded-lg p-4><div class="text-lg font-bold">n₁₀</div><div class="text-xs opacity-60">A only</div></div>
<div class="flex items-center justify-end pr-2 font-bold text-teal-300">A wrong</div><div border="2 solid red-800" bg="red-800/20" rounded-lg p-4><div class="text-lg font-bold">n₀₁</div><div class="text-xs opacity-60">B only</div></div><div border="2 solid white/10" bg="white/5" rounded-lg p-4><div class="text-lg font-bold">n₀₀</div><div class="text-xs opacity-60">both wrong</div></div>
</div>
</div>
<div v-click class="mt-4" style="font-size: .9em" border="2 solid teal-800" bg="teal-800/20" rounded-lg px-4 py-3>

$$
\chi^2=\frac{(|n_{01}-n_{10}|-1)^2}{n_{01}+n_{10}}
$$

</div>
</div>
</div>

<!--
This table is a genuinely different object from the confusion matrix in the previous deck: that matrix cross-tabulated actual label against predicted label for one model; this one cross-tabulates model A's correctness against model B's correctness on the same set of test examples, so it says nothing about which class each example belongs to, only about which model got which examples right. n₁₁ is examples both models got right; n₀₀ is examples both got wrong; these two "agreement" cells carry no information about which model is better, because they happen regardless of any real skill difference. The action is entirely in the two discordant cells: n₁₀ is examples A got right and B got wrong (evidence for A), n₀₁ is examples A got wrong and B got right (evidence for B).

McNemar's test asks: under H₀ (the two models are equally likely to be the one that's right when they disagree), n₀₁ and n₁₀ should each be about half of the total disagreements n₀₁+n₁₀. The χ² statistic formalizes that: (|n₀₁ − n₁₀| − 1)² in the numerator measures the squared imbalance between the two discordant counts (the −1 is a continuity correction, since a discrete count is being approximated by a continuous χ² distribution), divided by n₀₁+n₁₀, the total number of disagreements, which sets the scale of noise you'd expect from that many coin flips. This statistic follows a χ² distribution with 1 degree of freedom under H₀, so a p-value follows immediately by comparing against that reference distribution. Next slide works this out with real numbers.
-->

---
glowSeed: 554
---

# Worked Example: McNemar's Test

<div class="grid grid-cols-2 gap-6 items-start">
<div>
<div role="img" aria-label="McNemar table with n11 400, n10 8, n01 22, n00 70" class="mt-2 max-w-md mx-auto">
<div class="grid grid-cols-[6rem_1fr_1fr] gap-2 text-center text-xs">
<div></div><div class="font-bold text-blue-300">B correct</div><div class="font-bold text-blue-300">B wrong</div>
<div class="flex items-center justify-end pr-1 font-bold text-teal-300">A correct</div><div border="2 solid white/10" bg="white/5" rounded-lg p-4><div class="text-lg font-bold">400</div></div><div border="2 solid red-800" bg="red-800/20" rounded-lg p-4><div class="text-lg font-bold">8</div></div>
<div class="flex items-center justify-end pr-1 font-bold text-teal-300">A wrong</div><div border="2 solid red-800" bg="red-800/20" rounded-lg p-4><div class="text-lg font-bold">22</div></div><div border="2 solid white/10" bg="white/5" rounded-lg p-4><div class="text-lg font-bold">70</div></div>
</div>
</div>
<div class="text-xs opacity-75 mt-3">500 shared test examples. B corrects 22 cases A misses; A corrects only 8 cases B misses.</div>
</div>
<div>
<v-clicks>

- $\chi^2 = \dfrac{(|22-8|-1)^2}{22+8} = \dfrac{169}{30} = 5.63$
- $p \approx 0.018$ (χ² with 1 df)
- Exact binomial on $n_{01}=22$ of $30$: $p \approx 0.016$
- Both $< 0.05$: reject H₀ — model B's edge is unlikely to be chance

</v-clicks>

</div>
</div>

<!--
Plug the discordant counts from this table into the formula from the previous slide: n₀₁ = 22 (B right, A wrong) and n₁₀ = 8 (A right, B wrong), so χ² = (|22−8|−1)² / (22+8) = 13² / 30 = 169/30 ≈ 5.63. Comparing that to a χ² distribution with 1 degree of freedom gives p ≈ 0.018 — verified directly against scipy.stats.chi2. Because 22+8 = 30 is a fairly small number of disagreements, it is worth cross-checking with the exact test: under H₀, n₀₁ should be Binomial(n₀₁+n₁₀, 0.5) = Binomial(30, 0.5), and the exact two-sided binomial test on observing 22 (or fewer than 8, the symmetric tail) gives p ≈ 0.016 — close to the χ² approximation and confirming the same conclusion. As a rule of thumb, prefer the exact binomial test over the χ² approximation whenever the number of discordant pairs is small, roughly under 25, since the χ² approximation can be unreliable in that regime; here they happen to agree closely.

Both p-values are below the conventional 0.05 threshold, so we reject H₀: it is unlikely that models A and B are truly equally good and this 22-vs-8 split in their disagreements arose by chance alone. Practically, this means model B's advantage over model A, observed on these 500 shared test examples, is probably a real difference in skill and not sampling noise — though remember from the previous slide that "statistically significant" is a claim about surprise under H₀, not a guarantee about the true size of the gap or whether that gap is large enough to matter operationally, which is exactly the distinction the "statistical vs. practical significance" slide later in this deck will sharpen.
-->

---
glowSeed: 555
---

# Paired Tests Across CV Folds

<div class="grid grid-cols-2 gap-8 items-start">
<div>
<div class="space-y-3 mt-4">
<div v-click border="2 solid white/5" bg="white/5" rounded-lg px-4 py-3>
<span class="font-bold text-teal-300">Pair the folds</span>
<span class="text-sm opacity-85"> — Both models are evaluated on the same held-out fold each time.</span>
</div>
<div v-click border="2 solid white/5" bg="white/5" rounded-lg px-4 py-3>
<span class="font-bold text-blue-300">Test differences</span>
<span class="text-sm opacity-85"> — Analyze dᵢ = score Aᵢ − score Bᵢ for each of k folds, not the raw scores.</span>
</div>
<div v-click border="2 solid white/5" bg="white/5" rounded-lg px-4 py-3>
<span class="font-bold text-amber-300">Caveat</span>
<span class="text-sm opacity-85"> — Overlapping training folds violate full independence and can make ordinary t-tests optimistic.</span>
</div>
</div>
</div>
<div>
<div v-click class="mt-4" style="font-size: .9em" border="2 solid teal-800" bg="teal-800/20" rounded-lg px-4 py-3>

$$
t=\frac{\bar d}{s_d/\sqrt{k}}
$$

</div>
<div v-click class="mt-3 text-xs opacity-75">
d̄ = mean of the k paired differences. s_d = their sample standard deviation. Large |t| ⇒ the mean gap is large relative to how much it varies across folds.
</div>
</div>
</div>

<!--
McNemar's test needs individual per-example correctness, which works for a single held-out test set; when instead you have k-fold cross-validation scores for two models, use a paired t-test on the fold-level differences. Pairing is the key idea: rather than treating model A's k scores and model B's k scores as two independent samples, exploit the fact that fold i produced a score for both models on the identical held-out data, so form dᵢ = scoreAᵢ − scoreBᵢ for each fold and analyze that one sequence of k differences instead. This removes fold-to-fold difficulty variation from the comparison — some folds are just harder than others for every model — which is exactly the extra sensitivity that pairing buys you over an unpaired test.

Read the t-statistic symbol by symbol: d̄ is the sample mean of the k paired differences (the average fold-level gap); s_d is their sample standard deviation (how much that gap swings from fold to fold); k is the number of folds; s_d/√k is the standard error of d̄. A large |t| means the average gap is large relative to its own fold-to-fold noise, which under the t-distribution with k−1 degrees of freedom yields a p-value exactly as before. The caveat matters and should not be glossed over: standard t-test theory assumes independent samples, but k-fold CV training sets overlap heavily by construction (fold 1's training set and fold 2's training set share most of their examples), which violates independence and tends to make the test's p-values optimistic — smaller than they should be — inflating the false-positive rate of claiming significance. Treat the paired CV t-test as a useful, commonly used heuristic, not an exact procedure, and be more cautious with borderline p-values than you would be with a truly independent-sample test.
-->

---
glowSeed: 556
---

# Statistical vs. Practical Significance

<div class="grid grid-cols-3 gap-4 mt-6">
<div v-click border="2 solid teal-800" bg="teal-800/20" rounded-lg p-4>
<div class="font-bold text-teal-300 mb-2">Statistically significant</div>
<div class="text-sm leading-relaxed opacity-90">The observed effect is unlikely under the null model — a claim about surprise, not size.</div>
</div>
<div v-click border="2 solid blue-800" bg="blue-800/20" rounded-lg p-4>
<div class="font-bold text-blue-300 mb-2">Practically meaningful</div>
<div class="text-sm leading-relaxed opacity-90">The effect is large enough to justify added complexity, cost, latency, or risk.</div>
</div>
<div v-click border="2 solid amber-800" bg="amber-800/20" rounded-lg p-4>
<div class="font-bold text-amber-300 mb-2">Report both</div>
<div class="text-sm leading-relaxed opacity-90">Give the effect size and an interval, not only a p-value.</div>
</div>
</div>


<!--
A p-value answers "how surprising is this gap if the models were truly equal," and nothing more — it does not tell you how big the gap is. With enough test examples, an utterly trivial improvement, say 0.1 percentage points of accuracy, can produce a tiny p-value and get flagged "statistically significant," because sample size shrinks the standard error in the denominator of any test statistic, making even minuscule effects detectable. This is the flip side of the small-sample caveat from earlier slides: small samples make real effects hard to detect; large samples make tiny, worthless effects easy to detect.

So statistical significance and practical significance are separate questions that both need answering. Statistical significance asks whether the gap is probably real. Practical significance asks whether the gap is big enough to be worth acting on — worth the added training cost, the added inference latency, the added maintenance burden of a more complex model, or the risk of deploying something new. A model that is "significantly" better by 0.1% accuracy at ten times the inference cost is very likely not worth shipping. The professional habit that follows: never report a p-value alone; report the effect size (the actual measured gap) and, where possible, a confidence interval around it, so a reader can judge both questions — is this real, and does it matter — for themselves.
-->

---
glowSeed: 557
---

# Model Comparison Checklist

<div class="grid grid-cols-2 gap-4 mt-6">
<div v-click border="2 solid teal-800" bg="teal-800/20" rounded-lg p-4>
<div class="font-bold text-teal-300 mb-2">Pair observations</div>
<div class="text-sm leading-relaxed opacity-90">Exploit shared test examples (McNemar) or shared folds (paired t-test).</div>
</div>
<div v-click border="2 solid blue-800" bg="blue-800/20" rounded-lg p-4>
<div class="font-bold text-blue-300 mb-2">Quantify uncertainty</div>
<div class="text-sm leading-relaxed opacity-90">Report a p-value or confidence interval, not just two point estimates.</div>
</div>
<div v-click border="2 solid amber-800" bg="amber-800/20" rounded-lg p-4>
<div class="font-bold text-amber-300 mb-2">Control multiplicity</div>
<div class="text-sm leading-relaxed opacity-90">Do not cherry-pick one winner from many tested models or metrics.</div>
</div>
<div v-click border="2 solid violet-800" bg="violet-800/20" rounded-lg p-4>
<div class="font-bold text-violet-300 mb-2">Judge value</div>
<div class="text-sm leading-relaxed opacity-90">Weigh the effect size against deployment cost and risk.</div>
</div>
</div>


<!--
Turn the whole deck into a checklist you can run before claiming one model beats another. Pair your observations whenever you can — McNemar's test when you have per-example correctness on a shared test set, a paired t-test on per-fold scores when you have cross-validation results — because pairing removes noise that has nothing to do with which model is better and makes real gaps easier to detect. Quantify uncertainty explicitly rather than eyeballing two point estimates; a p-value or a confidence interval turns "91% vs. 89%, B wins" into a defensible claim.

Control multiplicity: if you evaluate 20 candidate models or 20 different metrics against a baseline and report only the one comparison that came out significant, you have effectively run 20 tests and cherry-picked the lucky one — at the conventional 0.05 threshold, roughly one comparison in twenty will look "significant" by pure chance even if nothing is actually different. This is directly analogous to repeatedly touching the test set during model development, a leakage-adjacent failure the next deck covers in depth. Finally, judge value: even a real, statistically defensible gap has to be weighed against what it costs to capture — more parameters, more inference time, more engineering complexity — before it justifies replacing a simpler, working model.
-->

---
glowSeed: 558
---

# Trustworthy Comparisons

<div class="mt-8"><div class="grid grid-cols-3 gap-4 mt-6">
<div v-click border="2 solid teal-800" bg="teal-800/20" rounded-lg p-4>
<div class="font-bold text-teal-300 mb-2">Scores vary</div>
<div class="text-sm leading-relaxed opacity-90">One number is one sample from a distribution.</div>
</div>
<div v-click border="2 solid blue-800" bg="blue-800/20" rounded-lg p-4>
<div class="font-bold text-blue-300 mb-2">Pair wisely</div>
<div class="text-sm leading-relaxed opacity-90">Use shared examples or folds; McNemar or paired t-test.</div>
</div>
<div v-click border="2 solid amber-800" bg="amber-800/20" rounded-lg p-4>
<div class="font-bold text-amber-300 mb-2">Size matters</div>
<div class="text-sm leading-relaxed opacity-90">Practical significance ≠ statistical significance.</div>
</div>
</div></div>

<div v-click class="mt-10 text-center text-lg" border="2 solid white/10" bg="white/5" rounded-lg px-6 py-4>Next: common evaluation failures — leakage and class imbalance.</div>

<!--
A trustworthy model comparison needs three ingredients working together: acknowledgment that any test-set score is a sample from a distribution rather than a fixed truth; a paired significance test — McNemar's on shared per-example correctness, or a paired t-test on shared cross-validation folds — that exploits the shared evaluation data to isolate the true model-vs-model gap from incidental sampling noise; and an honest separation between "the gap is probably real" (statistical significance) and "the gap is worth the cost of acting on it" (practical significance), reported together rather than collapsed into a single p-value.

This closes the rigor thread of the module: we now have precise metrics (accuracy, precision, recall, F1, ROC-AUC), a diagnostic tool for reading exactly how a model fails (the confusion matrix), and a way to decide whether an observed difference between two models is real. None of these tools mean anything, though, if the evaluation itself was set up incorrectly — if the test set was contaminated by information it shouldn't have had, or if the metric quietly hid a rare class's failure. The next deck covers exactly those setup failures: data leakage and class imbalance, worked through concrete, end-to-end examples of how each one silently inflates a model's apparent performance.
-->
