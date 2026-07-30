---
theme: default
highlighter: shiki
css: unocss
colorSchema: dark
title: 'Fairness, Bias, and Interpretability'
info: |
  ## Fairness, Bias, and Interpretability
  Ask what a model does, why, and to whom
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
glowSeed: 1010
---

# Fairness, Bias, and Interpretability

### Ask what a model does, why, and to whom

<div class="pt-8 opacity-80 text-lg">Broader Context · Foundations of Machine Learning</div>

<div class="mt-14 flex justify-center gap-4" aria-hidden="true">
<div class="w-28 h-3 rounded-full bg-teal-400/70"></div>
<div class="w-20 h-3 rounded-full bg-blue-400/60"></div>
<div class="w-14 h-3 rounded-full bg-violet-400/50"></div>
</div>

<!--
The previous deck asked whether a deployed system can fail after it leaves the lab. This deck asks a harder question about systems that are working exactly as validated: does the model treat different groups of people equitably, and can anyone — a developer, an auditor, or the person subject to a decision — explain why it produced a particular output? Neither question has a purely technical answer. Fairness requires choosing among mathematically incompatible definitions of "fair," and interpretability requires trading off, or sometimes combining, model complexity against explainability.

The path through this deck: first, where bias enters the machine learning pipeline (data, labels, and measurement, before the model ever sees anything); then a formal vocabulary of group fairness metrics with their exact definitions; then the mathematical result that these metrics cannot all be satisfied simultaneously when base rates differ, which is the single most important idea in the deck; then individual fairness as a different, complementary lens; and finally interpretability tools — global and local — including a full worked SHAP example. We use the COMPAS recidivism-prediction controversy as a running real-world case study because it is the best-documented instance where these exact tensions played out in a real, high-stakes system.
-->

---
glowSeed: 1011
---

# Bias Can Enter at Every Stage

<div class="grid grid-cols-2 gap-8 items-start">
<div>
<div class="space-y-3 mt-4">
<div v-click border="2 solid white/5" bg="white/5" rounded-lg px-4 py-3>
<span class="font-bold text-teal-300">Data bias</span>
<span class="text-sm opacity-85"> — Historical inequity or underrepresentation in <em>who was sampled</em> becomes the pattern the model learns to reproduce.</span>
</div>
<div v-click border="2 solid white/5" bg="white/5" rounded-lg px-4 py-3>
<span class="font-bold text-blue-300">Label bias</span>
<span class="text-sm opacity-85"> — The target variable $y$ is often a proxy for what we actually want (e.g., "arrested" as a proxy for "committed a crime"), and past human decisions can encode discrimination directly into that proxy.</span>
</div>
<div v-click border="2 solid white/5" bg="white/5" rounded-lg px-4 py-3>
<span class="font-bold text-amber-300">Measurement / proxy bias</span>
<span class="text-sm opacity-85"> — Features that look neutral (zip code, school name) can correlate strongly with a protected attribute like race or income, letting the model discriminate indirectly even when that attribute is excluded from the input.</span>
</div>
</div>
</div>
<div>
<div class="mt-5" role="img" aria-label="Data then Labels then Features then Model decision, each stage a point where bias can enter">
<div v-click class="flex items-center gap-3">
<div class="w-8 h-8 rounded-full bg-teal-500/20 border-2 border-teal-700 flex items-center justify-center text-sm font-bold">1</div>
<div class="flex-1 rounded-lg border-2 border-white/10 bg-white/5 px-3 py-2 text-sm font-bold">Data</div>
</div>
<div class="ml-4 h-1 border-l-2 border-teal-400/50"></div>
<div v-click class="flex items-center gap-3">
<div class="w-8 h-8 rounded-full bg-blue-500/20 border-2 border-blue-700 flex items-center justify-center text-sm font-bold">2</div>
<div class="flex-1 rounded-lg border-2 border-white/10 bg-white/5 px-3 py-2 text-sm font-bold">Labels</div>
</div>
<div class="ml-4 h-1 border-l-2 border-teal-400/50"></div>
<div v-click class="flex items-center gap-3">
<div class="w-8 h-8 rounded-full bg-amber-500/20 border-2 border-amber-700 flex items-center justify-center text-sm font-bold">3</div>
<div class="flex-1 rounded-lg border-2 border-white/10 bg-white/5 px-3 py-2 text-sm font-bold">Features</div>
</div>
<div class="ml-4 h-1 border-l-2 border-teal-400/50"></div>
<div v-click class="flex items-center gap-3">
<div class="w-8 h-8 rounded-full bg-violet-500/20 border-2 border-violet-700 flex items-center justify-center text-sm font-bold">4</div>
<div class="flex-1 rounded-lg border-2 border-white/10 bg-white/5 px-3 py-2 text-sm font-bold">Model decision</div>
</div>
</div>
<div v-click class="text-xs opacity-70 mt-2">"Fairness through unawareness" — simply deleting the protected attribute column — fails precisely because bias can re-enter at stage 3 through correlated proxies.</div>
</div>
</div>

<!--
Empirical risk minimization, as covered in Core ML Concepts, has no intrinsic fairness objective — it faithfully minimizes average loss on whatever data-generating process produced the training set, and if that process was historically unfair, the model will learn to reproduce the unfairness as faithfully as it reproduces any other pattern, because from ERM's perspective an unfair pattern and a "legitimate" pattern are statistically indistinguishable.

Bias enters at three distinct, compounding stages, and it matters which one you're diagnosing because the fix differs. Data bias is about who is represented and how much: if a medical dataset under-samples a demographic group, the model's error rate on that group will typically be higher, not because of malice but because of a smaller effective sample size for that population. Label bias is about what the target variable actually measures: "arrested for a crime" is not the same as "committed a crime," and if arrests are influenced by biased historical policing patterns (recall the predictive-policing feedback loop from the previous deck), the label itself is contaminated before any model touches it. Measurement/proxy bias is the most insidious because it survives naive fixes: removing race or gender as an explicit input feature ("fairness through unawareness") does not remove its influence if other features like zip code, name, or school are correlated with it — the model can reconstruct the excluded signal from these correlated proxies. This is why the next slide introduces formal metrics: you cannot audit for problems like this by inspection alone; you need to measure outcomes.
-->

---
glowSeed: 1012
---

# Case Study — COMPAS Recidivism Risk Scores

<div class="grid grid-cols-2 gap-4 mt-6">
<div v-click border="2 solid teal-800" bg="teal-800/20" rounded-lg p-4>
<div class="font-bold text-teal-300 mb-2">The system</div>
<div class="text-sm leading-relaxed opacity-90">COMPAS is a proprietary tool used by U.S. courts to score a defendant's risk of reoffending, informing bail and sentencing decisions.</div>
</div>
<div v-click border="2 solid blue-800" bg="blue-800/20" rounded-lg p-4>
<div class="font-bold text-blue-300 mb-2">ProPublica's 2016 audit</div>
<div class="text-sm leading-relaxed opacity-90">Black defendants who did <em>not</em> reoffend were nearly twice as likely as white defendants to be labeled high-risk; white defendants who <em>did</em> reoffend were more often mislabeled low-risk.</div>
</div>
<div v-click border="2 solid amber-800" bg="amber-800/20" rounded-lg p-4>
<div class="font-bold text-amber-300 mb-2">Northpointe's rebuttal</div>
<div class="text-sm leading-relaxed opacity-90">The tool's vendor countered that COMPAS was well-calibrated: within each risk score bucket, the actual reoffense rate was similar across race.</div>
</div>
<div v-click border="2 solid violet-800" bg="violet-800/20" rounded-lg p-4>
<div class="font-bold text-violet-300 mb-2">Both sides were right</div>
<div class="text-sm leading-relaxed opacity-90">This became the canonical demonstration that calibration and error-rate balance are different, formally incompatible fairness properties.</div>
</div>
</div>

<!--
This case study anchors the rest of the deck. In 2016, journalists at ProPublica analyzed COMPAS risk scores against actual re-arrest outcomes for thousands of defendants in Broward County, Florida, and found a clear racial disparity in error rates: among defendants who did not go on to reoffend, Black defendants were flagged "high risk" at roughly twice the rate of white defendants (a false positive rate disparity); among defendants who did reoffend, white defendants were more often incorrectly scored "low risk" (a false negative rate disparity). By the definition of fairness based on equal error rates across groups, COMPAS looked clearly unfair.

Northpointe (the company selling COMPAS) and several academic researchers responded that the tool was well calibrated: if you looked only at defendants who received the same risk score, say "7 out of 10," the actual proportion who went on to reoffend was similar for Black and white defendants at that score. By the definition of fairness based on calibration — a score of 7 should mean the same thing regardless of race — COMPAS looked fair. Both empirical claims were independently verified and both are true simultaneously in this dataset. The resolution is not that one side made an error; it's that Black and white defendants in this dataset had different underlying base rates of reoffense (due to the same historical policing and social factors discussed throughout this course), and when base rates differ, it is a mathematical fact — not an engineering failure — that you cannot have equal calibration and equal error rates at the same time for an imperfect predictor. The next few slides build the formal vocabulary to state this precisely.
-->

---
glowSeed: 1013
---

# Three Group Fairness Definitions

<div class="grid grid-cols-2 gap-4 mt-6">
<div v-click border="2 solid teal-800" bg="teal-800/20" rounded-lg p-4>
<div class="font-bold text-teal-300 mb-2">Demographic parity</div>
<div class="text-sm leading-relaxed opacity-90">$P(\hat{Y}{=}1 \mid A{=}a) = P(\hat{Y}{=}1 \mid A{=}b)$ — equal positive-prediction rates across groups $a, b$, regardless of the true label.</div>
</div>
<div v-click border="2 solid blue-800" bg="blue-800/20" rounded-lg p-4>
<div class="font-bold text-blue-300 mb-2">Equalized odds</div>
<div class="text-sm leading-relaxed opacity-90">Equal true-positive rate <em>and</em> equal false-positive rate across groups, conditioned on the true label $Y$.</div>
</div>
<div v-click border="2 solid amber-800" bg="amber-800/20" rounded-lg p-4>
<div class="font-bold text-amber-300 mb-2">Predictive parity (calibration)</div>
<div class="text-sm leading-relaxed opacity-90">$P(Y{=}1 \mid \hat{Y}{=}1, A{=}a) = P(Y{=}1 \mid \hat{Y}{=}1, A{=}b)$ — equal precision: a positive prediction means the same thing in every group.</div>
</div>
<div v-click border="2 solid violet-800" bg="violet-800/20" rounded-lg p-4>
<div class="font-bold text-violet-300 mb-2">Audit method</div>
<div class="text-sm leading-relaxed opacity-90">Compute the same confusion-matrix-derived metrics from model evaluation (TPR, FPR, precision) separately within each protected group, then compare.</div>
</div>
</div>

<!--
Here $\hat{Y}$ is the model's predicted label, $Y$ is the true outcome, and $A$ is a protected attribute such as race or gender. Demographic parity (also called statistical parity) asks whether the model predicts "positive" at the same rate for every group, completely ignoring whether those predictions are correct — it is the simplest definition and the easiest to satisfy by construction (e.g., quota-based thresholds), but it can force a model to make more errors on the group with the different true base rate, since it doesn't care about accuracy at all.

Equalized odds is more demanding: it requires the true-positive rate (of those who are actually positive, what fraction does the model correctly flag) and the false-positive rate (of those who are actually negative, what fraction does the model incorrectly flag) to match across groups. This is the metric ProPublica implicitly used in the COMPAS analysis — it directly targets "does the tool make mistakes about defendants who won't reoffend at the same rate across race," which is exactly the false-positive-rate disparity they found. Predictive parity, in contrast, asks a calibration question: among everyone the model calls "positive" (or, more precisely, gives a specific score to), what fraction were actually positive — is a "high risk" label equally trustworthy regardless of race? This is what Northpointe defended. All three are legitimate, well-motivated fairness goals used throughout the fairness literature, and the audit procedure for any of them is the same technique from model evaluation: slice the confusion matrix by group and compare rates. The next slide proves why you generally cannot satisfy all three at once.
-->

---
glowSeed: 1014
---

# Fairness Metrics Can Be Mutually Incompatible

<div class="grid grid-cols-2 gap-8 items-start">
<div>
<div class="space-y-3 mt-4">
<div v-click border="2 solid white/5" bg="white/5" rounded-lg px-4 py-3>
<span class="font-bold text-teal-300">The impossibility result</span>
<span class="text-sm opacity-85"> — Chouldechova (2017) and Kleinberg, Mullainathan &amp; Raghavan (2016) proved: if group base rates $P(Y{=}1\mid A{=}a) \ne P(Y{=}1\mid A{=}b)$ and the predictor is imperfect, calibration and equalized odds cannot both hold exactly.</span>
</div>
<div v-click border="2 solid white/5" bg="white/5" rounded-lg px-4 py-3>
<span class="font-bold text-blue-300">Not an engineering bug</span>
<span class="text-sm opacity-85"> — No better optimizer, more data, or bigger model removes this mathematical conflict; it follows from the definitions themselves.</span>
</div>
<div v-click border="2 solid white/5" bg="white/5" rounded-lg px-4 py-3>
<span class="font-bold text-amber-300">A value judgment, not a math problem</span>
<span class="text-sm opacity-85"> — The application and the people affected must determine which kind of error the system should be more careful to avoid.</span>
</div>
</div>
</div>
<div v-click class="mt-4" style="font-size: .85em" border="2 solid teal-800" bg="teal-800/20" rounded-lg px-4 py-3>

$$
\begin{aligned}
P(Y{=}1\mid A{=}a) \ne P(Y{=}1\mid A{=}b) \\
\text{and imperfect prediction} \;\Longrightarrow\; \text{fairness tradeoffs}
\end{aligned}
$$

<div class="text-sm opacity-85 mt-2">This is precisely the COMPAS situation: reoffense base rates differed by race in the data, so equal calibration (Northpointe's claim) and equal false-positive rates (ProPublica's claim) could not both hold.</div>
</div>
</div>

<!--
This is the single most important result in the deck, so state it carefully. Consider a binary predictor that is not perfectly accurate (true of essentially every real classifier) applied to two groups with different base rates of the true outcome — different fractions of each group actually belong to the positive class. Under these conditions, it is a theorem, not an empirical accident, that you cannot simultaneously achieve perfect calibration (a given score means the same thing in both groups) and perfectly equalized error rates (false positive and false negative rates match across groups) — except in the degenerate case of a perfect predictor or identical base rates. This result was proven independently and nearly simultaneously by Alexandra Chouldechova and by Jon Kleinberg, Sendhil Mullainathan, and Cherian Raghavan in 2016–2017, directly in response to the COMPAS controversy.

The practical consequence is that "make the model fair" is an underspecified request — you must first choose which fairness definition matters most for your specific application, because you cannot generally have all of them. For a screening test where false negatives are catastrophic (e.g., failing to flag a violent-reoffense risk), you might prioritize equal false-negative rates across groups even at the cost of calibration. For a lending decision where a "high risk" label needs to mean the same thing regardless of who receives it for legal and trust reasons, you might prioritize calibration instead. This choice cannot be delegated to the optimizer — it is a policy decision made by people who understand the stakes and, ideally, made with input from the communities affected. The next slide introduces a second, orthogonal fairness lens — individual rather than group fairness — that surfaces yet another tension.
-->

---
glowSeed: 1015
---

# Individual and Group Fairness Can Conflict

<div class="grid grid-cols-3 gap-4 mt-6">
<div v-click border="2 solid teal-800" bg="teal-800/20" rounded-lg p-4>
<div class="font-bold text-teal-300 mb-2">Individual fairness</div>
<div class="text-sm leading-relaxed opacity-90">Dwork et al. (2012): "similar individuals should be treated similarly" — formally, a Lipschitz condition $d(\hat{Y}(x_1), \hat{Y}(x_2)) \le L \cdot d(x_1, x_2)$ on some similarity metric $d$.</div>
</div>
<div v-click border="2 solid blue-800" bg="blue-800/20" rounded-lg p-4>
<div class="font-bold text-blue-300 mb-2">The hard question</div>
<div class="text-sm leading-relaxed opacity-90">Defining "similar" requires a task-specific, value-laden distance metric — who decides which features count, and how much each one weighs?</div>
</div>
<div v-click border="2 solid amber-800" bg="amber-800/20" rounded-lg p-4>
<div class="font-bold text-amber-300 mb-2">The tension</div>
<div class="text-sm leading-relaxed opacity-90">Enforcing a group-level statistic (e.g., demographic parity) can require treating two individuals who are nearly identical except for group membership <em>differently</em>.</div>
</div>
</div>

<div v-click class="mt-6 text-sm opacity-85" border="2 solid white/10" bg="white/5" rounded-lg px-4 py-3>
Group fairness asks "do the group-level statistics match?" Individual fairness asks "are similar people treated similarly?" A system can satisfy one while visibly violating the other — there is no metric that automatically reconciles both.
</div>

<!--
Individual fairness, formalized by Cynthia Dwork and coauthors in 2012, sidesteps group statistics entirely and instead asks a case-by-case question: does the model give similar outputs to similar inputs? Formally this is stated as a Lipschitz condition — the difference in the model's predictions between two individuals should be bounded by some constant L times how "different" those two individuals are according to a chosen similarity metric d. This should sound familiar: it's structurally the same idea as the distance metrics used in k-nearest-neighbors and clustering, but now applied with real consequences attached to the notion of "nearby."

The hard, unavoidable problem is that choosing the distance metric d is itself a value judgment, not a technical detail — should two loan applicants be considered "similar" if they have the same income and different zip codes? Different credit histories but the same income? There is no value-neutral way to build this metric; whoever designs it is implicitly encoding what should and shouldn't matter for the decision. And critically, individual and group fairness can actively conflict: imagine two applicants who are identical on every feature except protected group membership — individual fairness demands they get the same outcome, but a group-fairness intervention designed to equalize an aggregate statistic (like demographic parity) might require adjusting one group's threshold in a way that treats these two similar individuals differently. Neither framework is "more correct" — they answer different questions, and a real deployment often needs to be evaluated against both, with an explicit account of which one takes priority when they disagree. Having now covered the "is it fair" half of this deck, the remaining slides turn to "can we explain what it did" — interpretability.
-->

---
glowSeed: 1016
---

# Interpretability Has Global and Local Forms

<div class="grid grid-cols-3 gap-4 mt-6">
<div v-click border="2 solid teal-800" bg="teal-800/20" rounded-lg p-4>
<div class="font-bold text-teal-300 mb-2">Global</div>
<div class="text-sm leading-relaxed opacity-90">Understand overall model behavior across all inputs: linear-model coefficients, a small decision tree's splits, or aggregated feature importance from a random forest.</div>
</div>
<div v-click border="2 solid blue-800" bg="blue-800/20" rounded-lg p-4>
<div class="font-bold text-blue-300 mb-2">Local</div>
<div class="text-sm leading-relaxed opacity-90">Explain one specific prediction, even when the whole model (a deep network, a large ensemble) is too complex to summarize in one description.</div>
</div>
<div v-click border="2 solid amber-800" bg="amber-800/20" rounded-lg p-4>
<div class="font-bold text-amber-300 mb-2">Why it matters</div>
<div class="text-sm leading-relaxed opacity-90">Debugging unexpected behavior, building user and regulator trust, meeting legal compliance (e.g., adverse-action notices in lending), and running the fairness audits from earlier in this deck.</div>
</div>
</div>

<div v-click class="mt-6" border="2 solid white/10" bg="white/5" rounded-lg px-4 py-3>
<div class="text-sm opacity-90"><strong>Complexity–interpretability spectrum across this course:</strong> linear/logistic regression (fully global, coefficients are the explanation) → single decision tree (global, trace root to leaf) → random forest / gradient boosting (global importance only via aggregation) → neural network (neither is naturally readable — needs dedicated local tools like SHAP).</div>
</div>

<!--
Global interpretability asks "what has this model learned, in general?" and works best for models that are structurally simple: a linear regression's coefficients directly tell you the marginal effect of each feature (holding others fixed), and a shallow decision tree can be read top-to-bottom as an explicit set of if-then rules — both are inherently, exactly interpretable because the model's structure IS the explanation. Local interpretability asks a narrower but often more legally and practically relevant question: "why did the model make THIS decision for THIS person?" — this is what a rejected loan applicant or a flagged patient actually needs answered, and it remains answerable even for models whose global behavior is too complex to summarize (a random forest with 500 trees, or a deep neural network with millions of parameters).

The spectrum box connects this directly to models from earlier in the course: linear and logistic regression sit at the fully-interpretable end because the model literally is its own explanation; single decision trees are still fully traceable; random forests and gradient-boosted trees lose exact global traceability but retain approximate global feature-importance summaries (how much each feature reduced impurity on average, aggregated over all trees); neural networks lose both, which is exactly why dedicated local explanation techniques like SHAP, covered next, were developed specifically for these harder cases. The reason this matters beyond curiosity: it's the direct technical tool for actually running the fairness audits from earlier — if predictive parity fails for a group, interpretability tools help you find out whether a specific proxy feature is doing the damage.
-->

---
glowSeed: 1017
---

# SHAP Explains One Prediction Additively

<div class="grid grid-cols-2 gap-8 items-start">
<div>
<div class="space-y-3 mt-4">
<div v-click border="2 solid white/5" bg="white/5" rounded-lg px-4 py-3>
<span class="font-bold text-teal-300">Baseline</span>
<span class="text-sm opacity-85"> — Start at $\mathbb{E}[f(X)]$, the model's average prediction over the whole training set.</span>
</div>
<div v-click border="2 solid white/5" bg="white/5" rounded-lg px-4 py-3>
<span class="font-bold text-blue-300">Feature contributions</span>
<span class="text-sm opacity-85"> — Each SHAP value $\phi_i$ is the feature's average marginal contribution across every possible ordering of features, borrowed from Shapley values in cooperative game theory.</span>
</div>
<div v-click border="2 solid white/5" bg="white/5" rounded-lg px-4 py-3>
<span class="font-bold text-amber-300">Additive guarantee</span>
<span class="text-sm opacity-85"> — Contributions sum exactly to this case's prediction: $f(x) = \mathbb{E}[f(X)] + \sum_i \phi_i$.</span>
</div>
</div>
</div>
<div>
<svg role="img" aria-label="SHAP waterfall chart: starting from a baseline of 0.30 default probability, income lowers it to 0.20, debt-to-income raises it to 0.38, and credit history raises it further to a final prediction of 0.52" viewBox="0 0 500 310" class="w-full max-w-xl mx-auto mt-7">
  <line x1="55" y1="260" x2="470" y2="260" stroke="#64748b" stroke-width="2"/><line x1="55" y1="35" x2="55" y2="260" stroke="#64748b" stroke-width="2"/>
  <rect x="65" y="120" width="55" height="140" fill="#94a3b8" opacity="0.8"/>
  <rect x="150" y="150" width="55" height="110" fill="#2dd4bf" opacity="0.85"/>
  <rect x="235" y="90" width="55" height="60" fill="#f59e0b" opacity="0.85"/>
  <rect x="320" y="55" width="55" height="35" fill="#f59e0b" opacity="0.85"/>
  <rect x="405" y="55" width="55" height="205" fill="#60a5fa" opacity="0.85"/>
  <g fill="#cbd5e1" style="font-size: 11px" text-anchor="middle">
    <text x="92" y="285">baseline</text><text x="177" y="285">income</text><text x="262" y="285">debt/inc.</text><text x="347" y="285">history</text><text x="432" y="285">final</text>
  </g>
  <g fill="#e2e8f0" style="font-size: 11px" text-anchor="middle">
    <text x="92" y="113">0.30</text><text x="177" y="143">-0.10</text><text x="262" y="83">+0.08</text><text x="347" y="48">+0.10</text><text x="432" y="48">0.52</text>
  </g>
</svg>
<div class="text-xs opacity-70 text-center mt-1">Worked example: a loan-default model, starting from the 30% average default rate.</div>
</div>
</div>

<!--
SHAP (SHapley Additive exPlanations, Lundberg &amp; Lee 2017) answers "why did the model predict THIS value for THIS specific input?" by adapting Shapley values from cooperative game theory, where the "players" are the input features and the "payout" being split is the difference between this prediction and the average prediction. Concretely: imagine adding features to the model one at a time, in every possible order, and each time measuring how much the prediction moves when a given feature is added to the ones already present; the SHAP value for a feature is the average of that movement across all possible orderings. This averaging-over-orderings step is what makes SHAP values fair in a precise game-theoretic sense, and it guarantees the additive property shown in the equation — the baseline plus every feature's contribution sums up EXACTLY to the model's actual prediction for that case, with no leftover unexplained residual.

Walk through the worked example in the chart: a loan-default model's average predicted default probability across the training set is 0.30 (the baseline, gray bar). For this specific applicant, a high income pushes the prediction down by 0.10 to 0.20 (teal bar). A high debt-to-income ratio pushes it back up by 0.08 to 0.28, and a spotty credit history pushes it up another 0.10 (amber bars) to a final prediction of 0.52 for this specific person. Every number is traceable and the whole chain sums exactly to the model's output — this is what makes SHAP a local explanation: it explains this one applicant's score, not the model's general behavior. Contrast this with global random-forest feature importance, which would tell you "credit history matters most on average across all applicants" but nothing about this particular case. Crucially, neither tool establishes causality — a SHAP value tells you the feature was associated with pushing the prediction up or down given the model's learned associations, not that changing the feature would causally change the true outcome. Use SHAP for debugging, compliance, and — directly connecting back to the fairness section — for auditing whether the same feature is contributing very differently to a decision for otherwise-similar individuals across protected groups.
-->

---
glowSeed: 1018
---

# Fairness and Interpretability

<div class="mt-4"><div class="grid grid-cols-4 gap-4 mt-6">
<div v-click border="2 solid teal-800" bg="teal-800/20" rounded-lg p-4>
<div class="font-bold text-teal-300 mb-2">Audit sources</div>
<div class="text-sm leading-relaxed opacity-90">Bias enters via data, labels, and proxy features — check all three, not just the model.</div>
</div>
<div v-click border="2 solid blue-800" bg="blue-800/20" rounded-lg p-4>
<div class="font-bold text-blue-300 mb-2">Choose values</div>
<div class="text-sm leading-relaxed opacity-90">Group fairness definitions provably conflict when base rates differ — pick deliberately, don't default.</div>
</div>
<div v-click border="2 solid amber-800" bg="amber-800/20" rounded-lg p-4>
<div class="font-bold text-amber-300 mb-2">Individual lens</div>
<div class="text-sm leading-relaxed opacity-90">Also ask whether similar people are treated similarly, not only whether group statistics match.</div>
</div>
<div v-click border="2 solid violet-800" bg="violet-800/20" rounded-lg p-4>
<div class="font-bold text-violet-300 mb-2">Explain</div>
<div class="text-sm leading-relaxed opacity-90">Use global tools (coefficients, feature importance) and local tools (SHAP) together.</div>
</div>
</div></div>

<div v-click class="mt-10 text-center text-lg" border="2 solid white/10" bg="white/5" rounded-lg px-6 py-4>Next: where classical ML ends and modern deep learning begins.</div>

<!--
This deck's central lesson is that fairness is not one scalar objective waiting to be optimized like accuracy or loss — it is a set of legitimate, competing definitions that provably cannot all be satisfied at once when group base rates differ, as the COMPAS case study demonstrated concretely with real, well-documented data. The goal was never to hand you a single "fair" formula; it was to give you the vocabulary (demographic parity, equalized odds, predictive parity, individual fairness) to recognize which tradeoff a system is making, to make that tradeoff a deliberate and defensible choice rather than an accidental byproduct of whichever metric the training pipeline happened to optimize, and to involve people affected by the decision in choosing which errors matter most.

Interpretability tools — global summaries like linear coefficients and tree structure, local explanations like SHAP — are the practical instruments that make fairness auditing possible in the first place: you cannot ask "is this feature acting as an illegal proxy for race" without a tool that tells you how much a feature contributed to a specific decision. Bring this "informed scrutiny, not a universal formula" mindset into the final deck of the module, which asks when the classical models built throughout this course (linear/logistic regression, trees, ensembles) remain the right tool, and when the added complexity, cost, and reduced interpretability of deep learning is actually justified by the problem at hand — interpretability and fairness auditing being measurably harder for deep models is itself one of the practical considerations in that choice.
-->
