---
theme: default
highlighter: shiki
css: unocss
colorSchema: dark
title: 'Accuracy, Precision, Recall, F1, and ROC/AUC'
info: |
  ## Accuracy, Precision, Recall, F1, and ROC/AUC
  Choose metrics that reflect the real cost of mistakes
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
glowSeed: 510
---

# Accuracy, Precision, Recall, F1, and ROC/AUC

### Choose metrics that reflect the real cost of mistakes

<div class="pt-8 opacity-80 text-lg">Model Evaluation · Foundations of Machine Learning</div>

<div class="mt-14 flex justify-center gap-4" aria-hidden="true">
<div class="w-28 h-3 rounded-full bg-teal-400/70"></div>
<div class="w-20 h-3 rounded-full bg-blue-400/60"></div>
<div class="w-14 h-3 rounded-full bg-violet-400/50"></div>
</div>

<!--
You already know how to build a classifier and how to split data into train, validation, and test sets — that scaffolding was covered in Core ML Concepts. This deck asks a different question: once you have a trained classifier and a held-out test set, how do you decide whether it is actually good? A single number like "accuracy" feels like the obvious answer, and the next slide shows exactly why that instinct is dangerous.

Roadmap: we start from the four raw counts every binary classifier produces (true positives, true negatives, false positives, false negatives), build precision, recall, and F1 directly out of those counts with a fully worked numeric example, then move to ROC curves and AUC, which summarize performance across every possible decision threshold rather than just one. We end with a decision rule for picking the right metric for a given deployment. Every formula in this deck will be derived symbol by symbol and checked against scikit-learn output, not just stated.
-->

---
glowSeed: 511
---

# Accuracy Can Look Great and Be Useless

<div class="grid grid-cols-2 gap-8 items-start">
<div>
<div class="space-y-3 mt-4">
<div v-click border="2 solid white/5" bg="white/5" rounded-lg px-4 py-3>
<span class="font-bold text-teal-300">Imbalanced data</span>
<span class="text-sm opacity-85"> — 990 healthy cases and 10 disease cases.</span>
</div>
<div v-click border="2 solid white/5" bg="white/5" rounded-lg px-4 py-3>
<span class="font-bold text-blue-300">Trivial classifier</span>
<span class="text-sm opacity-85"> — Always predict “healthy.”</span>
</div>
<div v-click border="2 solid white/5" bg="white/5" rounded-lg px-4 py-3>
<span class="font-bold text-amber-300">The trap</span>
<span class="text-sm opacity-85"> — 99% accuracy, but zero detected disease cases.</span>
</div>
</div>
</div>
<div>
<div v-click class="mt-4" style="font-size: .9em" border="2 solid teal-800" bg="teal-800/20" rounded-lg px-4 py-3>

$$
\mathrm{Accuracy}=\frac{TP+TN}{TP+TN+FP+FN}=0.99
$$

</div>

</div>
</div>

<!--
Walk through the arithmetic before revealing the punchline. Accuracy is defined as the fraction of all predictions that were correct: (TP + TN) divided by the total number of predictions. If the classifier always predicts "healthy," it gets every one of the 990 healthy patients right (990 true negatives) and every one of the 10 disease patients wrong (10 false negatives, zero true positives). Plug in: (0 + 990) / 1000 = 0.99. That is 99% accuracy from a model that has never once correctly flagged the disease it exists to detect.

This is the accuracy paradox: when one class vastly outnumbers the other, a classifier can score arbitrarily close to 100% accuracy by ignoring the minority class entirely. Accuracy answers "how often is the model right overall," which is the wrong question whenever the classes are imbalanced or the cost of a false negative differs from the cost of a false positive — exactly the situation in disease screening, fraud detection, and spam filtering. Note also a subtlety we will hit again later: if you tried to compute this model's precision, TP/(TP+FP), you would get 0/0 — precision is undefined when the model never predicts positive at all, not automatically zero. scikit-learn reports 0.0 with a warning by convention, but mathematically the ratio has no value. Next we break accuracy apart into the four counts that actually drive it.
-->

---
glowSeed: 512
---

# Four Counts Under Every Metric

<div class="grid grid-cols-2 gap-8 items-start">
<div>
<div class="space-y-3 mt-4">
<div v-click border="2 solid white/5" bg="white/5" rounded-lg px-4 py-3>
<span class="font-bold text-teal-300">TP</span>
<span class="text-sm opacity-85"> — Predicted positive, actually positive.</span>
</div>
<div v-click border="2 solid white/5" bg="white/5" rounded-lg px-4 py-3>
<span class="font-bold text-blue-300">TN</span>
<span class="text-sm opacity-85"> — Predicted negative, actually negative.</span>
</div>
<div v-click border="2 solid white/5" bg="white/5" rounded-lg px-4 py-3>
<span class="font-bold text-amber-300">FP</span>
<span class="text-sm opacity-85"> — Predicted positive, actually negative (false alarm, Type I).</span>
</div>
<div v-click border="2 solid white/5" bg="white/5" rounded-lg px-4 py-3>
<span class="font-bold text-violet-300">FN</span>
<span class="text-sm opacity-85"> — Predicted negative, actually positive (missed case, Type II).</span>
</div>
</div>
</div>
<div>
<div role="img" aria-label="Confusion matrix with rows as actual class and columns as predicted class" class="mt-6 max-w-lg mx-auto">
<div class="grid grid-cols-[6.5rem_1fr_1fr] gap-2 text-center text-xs">
<div></div><div class="font-bold text-blue-300">Pred: Negative</div><div class="font-bold text-blue-300">Pred: Positive</div>
<div class="flex items-center justify-end pr-2 font-bold text-teal-300">Actual: Negative</div><div border="2 solid teal-800" bg="teal-800/20" rounded-lg p-4><div class="text-lg font-bold">TN</div></div><div border="2 solid red-800" bg="red-800/20" rounded-lg p-4><div class="text-lg font-bold">FP</div></div>
<div class="flex items-center justify-end pr-2 font-bold text-teal-300">Actual: Positive</div><div border="2 solid red-800" bg="red-800/20" rounded-lg p-4><div class="text-lg font-bold">FN</div></div><div border="2 solid teal-800" bg="teal-800/20" rounded-lg p-4><div class="text-lg font-bold">TP</div></div>
</div>
</div>
<div v-click class="mt-3 text-xs opacity-75">Convention used throughout this course: rows are the actual (ground-truth) label, columns are the predicted label — matching <code>sklearn.metrics.confusion_matrix</code>.</div>
</div>
</div>

<!--
Every classification metric in this deck is a ratio built from exactly these four counts, so get the definitions precise. TP and TN are the diagonal: cases where the prediction matched reality. FP is a false alarm — the model said positive but the truth was negative, also called a Type I error. FN is a miss — the model said negative but the truth was positive, also called a Type II error. Fix the orientation now, because libraries disagree: this course follows scikit-learn's convention where rows are the actual label and columns are the predicted label, so reading left to right along the "Actual: Positive" row tells you how the model handled real positive cases (FN then TP).

Have students state each cell out loud in the disease-screening context from the previous slide: TN is a healthy patient correctly cleared, TP is a sick patient correctly flagged, FP is a healthy patient wrongly flagged (costs a follow-up test), FN is a sick patient wrongly cleared (costs a missed diagnosis). Notice those two error types are not interchangeable — an FN in cancer screening is far more costly than an FP, while in spam filtering an FP (a real email marked as spam) is usually worse than an FN. Every metric on the following slides is just a different weighted combination of these four numbers, chosen to emphasize the errors that matter for a given application. Next we anchor these counts in one concrete numeric example we will reuse for the rest of the deck.
-->

---
glowSeed: 513
---

# Worked Example: One Confusion Matrix, Every Metric

<div class="grid grid-cols-2 gap-6 items-start">
<div>
<div role="img" aria-label="Confusion matrix with TN 810, FP 90, FN 20, TP 80 for a 1000-patient disease screen" class="mt-2">
<div class="grid grid-cols-[6.5rem_1fr_1fr] gap-2 text-center text-xs">
<div></div><div class="font-bold text-blue-300">Pred: Neg</div><div class="font-bold text-blue-300">Pred: Pos</div>
<div class="flex items-center justify-end pr-2 font-bold text-teal-300">Actual: Neg</div><div border="2 solid teal-800" bg="teal-800/20" rounded-lg p-4><div class="text-xl font-bold">810</div><div class="text-xs opacity-70">TN</div></div><div border="2 solid red-800" bg="red-800/20" rounded-lg p-4><div class="text-xl font-bold">90</div><div class="text-xs opacity-70">FP</div></div>
<div class="flex items-center justify-end pr-2 font-bold text-teal-300">Actual: Pos</div><div border="2 solid red-800" bg="red-800/20" rounded-lg p-4><div class="text-xl font-bold">20</div><div class="text-xs opacity-70">FN</div></div><div border="2 solid teal-800" bg="teal-800/20" rounded-lg p-4><div class="text-xl font-bold">80</div><div class="text-xs opacity-70">TP</div></div>
</div>
</div>
<div class="mt-3 text-xs opacity-75">1,000 patients: 100 truly have the disease, 900 do not.</div>
</div>
<div>
<v-clicks>

- $\mathrm{Accuracy} = \dfrac{80+810}{1000} = 0.890$
- $\mathrm{Precision} = \dfrac{80}{80+90} = 0.471$
- $\mathrm{Recall} = \dfrac{80}{80+20} = 0.800$
- $F_1 = 2\cdot\dfrac{0.471\times0.800}{0.471+0.800} = 0.593$
- $\mathrm{FPR} = \dfrac{90}{90+810} = 0.100$

</v-clicks>

</div>
</div>

<!--
This is the confusion matrix we reuse for the rest of the deck: 1,000 patients, 100 truly positive, 900 truly negative, and a classifier that produces TP=80, FN=20, FP=90, TN=810. Every number on the right was computed directly from those four counts and verified against scikit-learn's confusion_matrix, precision_score, recall_score, and f1_score.

Accuracy is 89%, which sounds respectable — but look at precision: only 47.1% of the patients the model flagged as positive actually have the disease, because 90 false positives are mixed in with 80 true positives (80/170). Recall is 80%, meaning the model catches 80 of the 100 true cases and misses 20 (80/100) — much better than the trivial "always healthy" classifier's 0% recall from two slides ago, but still missing one in five real cases. F1 is the harmonic mean of precision and recall, 0.593, sitting closer to the smaller of the two inputs, which is the point of using a harmonic mean instead of an arithmetic mean — we derive that on the next slide. The false-positive rate, FP/(FP+TN) = 0.10, is a different denominator entirely: it asks what fraction of the healthy patients were incorrectly flagged, and we will need it for ROC curves later. Keep these five numbers in mind — every formula from here forward should reproduce them.
-->

---
glowSeed: 514
---

# Precision and Recall Ask Different Questions

<div class="grid grid-cols-2 gap-8 items-start">
<div>
<div class="space-y-3 mt-4">
<div v-click border="2 solid white/5" bg="white/5" rounded-lg px-4 py-3>
<span class="font-bold text-teal-300">Precision</span>
<span class="text-sm opacity-85"> — When the model says yes, how often is it right?</span>
</div>
<div v-click border="2 solid white/5" bg="white/5" rounded-lg px-4 py-3>
<span class="font-bold text-blue-300">Recall</span>
<span class="text-sm opacity-85"> — Of all real positives, how many did the model catch?</span>
</div>
<div v-click border="2 solid white/5" bg="white/5" rounded-lg px-4 py-3>
<span class="font-bold text-amber-300">Tradeoff</span>
<span class="text-sm opacity-85"> — Changing a decision threshold usually moves one against the other.</span>
</div>
</div>
</div>
<div>
<div v-click class="mt-4" style="font-size: .9em" border="2 solid teal-800" bg="teal-800/20" rounded-lg px-4 py-3>

$$
\mathrm{Precision}=\frac{TP}{TP+FP},\qquad \mathrm{Recall}=\frac{TP}{TP+FN}
$$

</div>

</div>
</div>

<!--
Precision's denominator is TP + FP — everything the model called positive, correct or not. It answers "of the alarms the model raised, what fraction were real?" Recall's denominator is TP + FN — every actual positive that exists, caught or not. It answers "of the real positives out there, what fraction did the model find?" Notice they share the same numerator, TP, but divide by two completely different totals, which is exactly why a model can score high on one and low on the other, as our worked example just showed (47.1% precision, 80% recall).

The tradeoff is mechanical, not accidental: most classifiers output a probability or score, and you pick a threshold above which you call the case "positive." Lower the threshold and you flag more cases as positive — recall goes up (you catch more true positives) but precision typically goes down (you also catch more false positives). Raise the threshold and the reverse happens. A spam filter usually favors precision, because a false positive (blocking a real email) is more annoying than a false negative (one spam email slipping through). A disease screen usually favors recall, because a false negative (a missed diagnosis) can be fatal while a false positive just costs a follow-up test. There is no universally "better" value — the right balance depends entirely on which error is more expensive in your application, which is the central theme of this whole deck.
-->

---
glowSeed: 515
---

# F1 Penalizes Imbalance Between the Two

<div class="grid grid-cols-2 gap-8 items-start">
<div>
<div class="space-y-3 mt-4">
<div v-click border="2 solid white/5" bg="white/5" rounded-lg px-4 py-3>
<span class="font-bold text-teal-300">Harmonic mean</span>
<span class="text-sm opacity-85"> — Both precision and recall must be reasonably high.</span>
</div>
<div v-click border="2 solid white/5" bg="white/5" rounded-lg px-4 py-3>
<span class="font-bold text-blue-300">Extreme example</span>
<span class="text-sm opacity-85"> — Precision 1.0, recall 0.01 gives F1 ≈ 0.0198, not the arithmetic-mean 0.505.</span>
</div>
<div v-click border="2 solid white/5" bg="white/5" rounded-lg px-4 py-3>
<span class="font-bold text-amber-300">Fβ</span>
<span class="text-sm opacity-85"> — Use β &gt; 1 to weight recall more, β &lt; 1 to weight precision more.</span>
</div>
</div>
</div>
<div>
<div v-click class="mt-4" style="font-size: .9em" border="2 solid teal-800" bg="teal-800/20" rounded-lg px-4 py-3>

$$
F_1=2\frac{PR}{P+R},\qquad F_\beta=(1+\beta^2)\frac{PR}{\beta^2P+R}
$$

</div>

</div>
</div>

<!--
F1 is the harmonic mean of precision (P) and recall (R), not their average. The formula 2PR/(P+R) comes directly from the general harmonic-mean formula for two numbers, 2/(1/P + 1/R); multiplying numerator and denominator by PR gives 2PR/(P+R). The harmonic mean is always less than or equal to the arithmetic mean, and it is pulled hard toward whichever of the two numbers is smaller. Verify with the extreme case on the slide: precision 1.0 and recall 0.01 average arithmetically to 0.505, which sounds mediocre-but-usable — but the harmonic mean is 2(1.0)(0.01)/(1.0+0.01) ≈ 0.0198, correctly signaling that a model catching 1% of positives is nearly useless no matter how precise it is when it does fire.

That "punish the weak link" behavior is why F1 is useful when both precision and recall must be reasonably high. Fβ changes their relative emphasis. β=1 gives F1. Values above 1 emphasize recall, and values below 1 emphasize precision. Because β enters the formula as β², F2 places four times as much coefficient weight on recall as on precision. On our worked example (P=0.471, R=0.800), F1 = 0.593; recomputing F2 shows the result shift toward recall. Next we move from single-threshold metrics to a curve that sweeps every possible threshold.
-->

---
glowSeed: 516
---

# ROC Curves Sweep the Threshold

<div class="grid grid-cols-2 gap-8 items-start">
<div>
<div class="space-y-3 mt-4">
<div v-click border="2 solid white/5" bg="white/5" rounded-lg px-4 py-3>
<span class="font-bold text-teal-300">Each point</span>
<span class="text-sm opacity-85"> — A different classification threshold, from 1 down to 0.</span>
</div>
<div v-click border="2 solid white/5" bg="white/5" rounded-lg px-4 py-3>
<span class="font-bold text-blue-300">Axes</span>
<span class="text-sm opacity-85"> — y = true-positive rate (recall), x = false-positive rate.</span>
</div>
<div v-click border="2 solid white/5" bg="white/5" rounded-lg px-4 py-3>
<span class="font-bold text-amber-300">Ideal vs. random</span>
<span class="text-sm opacity-85"> — Upper-left corner is perfect; the dashed diagonal is a coin flip.</span>
</div>
</div>
</div>
<div>
<svg role="img" aria-label="ROC curve rising monotonically from the origin to the top-right corner, above the diagonal chance line" viewBox="0 0 500 310" class="w-full max-w-xl mx-auto mt-4">
  <line x1="55" y1="260" x2="470" y2="260" stroke="#64748b" stroke-width="2"/>
  <line x1="55" y1="35" x2="55" y2="260" stroke="#64748b" stroke-width="2"/>
  <line x1="55" y1="260" x2="470" y2="35" stroke="#94a3b8" stroke-width="2" stroke-dasharray="6 6"/>
  <polyline points="55,260 63,204 76,159 96,120 138,84 200,62 283,46 470,35" fill="none" stroke="#2dd4bf" stroke-width="4"/>
  <g fill="#f59e0b">
    <circle cx="76" cy="159" r="6"/>
    <circle cx="138" cy="84" r="6"/>
    <circle cx="283" cy="46" r="6"/>
  </g>
  <g fill="#cbd5e1" style="font-size: 12px" text-anchor="middle">
    <text x="55" y="285">0</text><text x="262" y="285">FPR</text><text x="470" y="285">1</text>
    <text x="30" y="260">0</text><text x="18" y="150" transform="rotate(-90 18 150)">TPR</text><text x="30" y="40">1</text>
  </g>
  <g style="font-size: 12px">
    <text x="330" y="52" fill="#5eead4">ROC curve</text>
    <text x="330" y="230" fill="#94a3b8">chance (AUC = 0.5)</text>
  </g>
</svg>

</div>
</div>

<!--
A ROC curve is built by sweeping the classification threshold from 1 down to 0 and plotting one point per threshold: x is the false-positive rate, FP/(FP+TN) — the fraction of true negatives incorrectly flagged; y is the true-positive rate, TP/(TP+FN), which is just recall by another name. At a threshold of 1, the model calls nothing positive, so both rates are 0 (bottom-left corner). At a threshold of 0, it calls everything positive, so both rates are 1 (top-right corner). Every intermediate threshold traces a point in between, and the curve must be monotone — moving from one threshold to a slightly lower one can only add positive predictions, so TPR and FPR can each only increase or stay flat, never decrease.

The dashed diagonal line is what a classifier with zero discriminative power produces — one that ranks positives and negatives in a completely random order — because at every threshold it flags the same fraction of true positives as false positives. A useful classifier's curve bows up and to the left of that diagonal: it can achieve a high true-positive rate while keeping the false-positive rate low. The closer the curve hugs the upper-left corner (TPR=1, FPR=0), the better the model separates the two classes across all thresholds simultaneously, not just at the one threshold you might deploy with. Common misconception: a single point on this curve corresponds to accuracy or F1 at one threshold, but the curve as a whole describes threshold-independent ranking ability — which is exactly what AUC quantifies next.
-->

---
glowSeed: 517
---

# AUC Measures Ranking Quality

<div class="grid grid-cols-2 gap-8 items-start">
<div>
<div class="space-y-3 mt-4">
<div v-click border="2 solid white/5" bg="white/5" rounded-lg px-4 py-3>
<span class="font-bold text-teal-300">Threshold independent</span>
<span class="text-sm opacity-85"> — The area under the entire ROC curve, one number.</span>
</div>
<div v-click border="2 solid white/5" bg="white/5" rounded-lg px-4 py-3>
<span class="font-bold text-blue-300">Probability view</span>
<span class="text-sm opacity-85"> — Chance that a random positive receives a higher score than a random negative.</span>
</div>
<div v-click border="2 solid white/5" bg="white/5" rounded-lg px-4 py-3>
<span class="font-bold text-amber-300">Not calibration</span>
<span class="text-sm opacity-85"> — A strong AUC does not choose a useful operating threshold for you.</span>
</div>
</div>
</div>
<div>
<div v-click class="mt-4" style="font-size: .9em" border="2 solid teal-800" bg="teal-800/20" rounded-lg px-4 py-3>

$$
\mathrm{AUC}=P(s^+>s^-)+\tfrac12P(s^+=s^-)
$$

</div>

<div v-click class="mt-4 text-sm opacity-85">
AUC = 0.5 is random ranking. AUC = 1.0 is a perfect ranking. AUC = 0.0 means the model ranks every pair backwards — flip its decision rule and it becomes perfect.
</div>

</div>
</div>

<!--
AUC, area under the ROC curve, compresses the entire curve into one number. Pick one positive and one negative example at random. AUC is the probability that the positive receives a higher score, plus half the probability of a tie. The half-credit term matters for models that emit a small set of discrete scores. This concordance interpretation is equivalent to the area interpretation and requires no classification threshold.

Because AUC only cares about relative ranking, it is threshold-independent: it does not change if you rescale or monotonically transform the scores. That is also its biggest limitation — a model can have excellent AUC while producing scores that are badly miscalibrated as probabilities (e.g., its "0.9" outputs are not right 90% of the time), and AUC alone tells you nothing about which threshold to deploy at; you still need to pick one using precision, recall, or a cost-weighted criterion from the raw ROC curve or a validation set. AUC = 0.5 means the model has learned nothing about which class is which — it is equivalent to random guessing, not "50% accurate." The next slide shows a case where AUC is much more misleading than it first appears.
-->

---
glowSeed: 518
---

# ROC Coordinates Can Hide Alert Burden

<div class="grid grid-cols-2 gap-8 items-start">
<div>
<div class="space-y-3 mt-4">
<div v-click border="2 solid white/5" bg="white/5" rounded-lg px-4 py-3>
<span class="font-bold text-teal-300">Operating point</span>
<span class="text-sm opacity-85"> — 10 positives, 9,990 negatives; flag 100 cases and catch 8 positives.</span>
</div>
<div v-click border="2 solid white/5" bg="white/5" rounded-lg px-4 py-3>
<span class="font-bold text-blue-300">FPR barely moves</span>
<span class="text-sm opacity-85"> — 92 false positives out of 9,990 negatives is only FPR ≈ 0.009.</span>
</div>
<div v-click border="2 solid white/5" bg="white/5" rounded-lg px-4 py-3>
<span class="font-bold text-amber-300">Precision tells the truth</span>
<span class="text-sm opacity-85"> — Of the 100 flagged cases, only 8 are real: precision = 0.08.</span>
</div>
</div>
</div>
<div>
<div v-click class="mt-4 text-sm" border="2 solid teal-800" bg="teal-800/20" rounded-lg px-4 py-3>
ROC point: TPR = 0.80, FPR ≈ 0.009
</div>
<div v-click class="mt-3 text-sm" border="2 solid red-800" bg="red-800/20" rounded-lg px-4 py-3>
Alert quality: precision = 0.08
</div>
<div v-click class="mt-4 text-xs opacity-75">
FPR's denominator is <em>every negative</em> (9,990). With a huge negative class, hundreds of false positives barely register as a rate — but they overwhelm the flagged set. Precision-Recall curves use TP+FP as a denominator and expose this directly.
</div>
</div>
</div>

<!--
This operating point shows why ROC coordinates can look reassuring under heavy class imbalance. When TN is huge, even many false positives barely move FP/(FP+TN). Here the model catches 8 of 10 positives, so TPR is 0.80, and produces 92 false positives, so FPR is only about 0.009.

Precision uses the flagged set as its denominator: only 8 of 100 alerts are real. A precision-recall curve exposes this burden across thresholds. Its no-skill precision baseline equals prevalence, 10/10,000 = 0.001 here. One operating point cannot determine ROC-AUC or the area under a precision-recall curve; both require the complete score ranking. Also distinguish average precision, the summary returned by scikit-learn's average_precision_score, from trapezoidal PR-AUC because the two calculations can differ.
-->

---
glowSeed: 5181
---

# Calibration: Do the Probabilities Mean What They Say?

<div class="grid grid-cols-2 gap-8 items-start">
<div>
<div class="space-y-3 mt-4">
<div v-click border="2 solid white/5" bg="white/5" rounded-lg px-4 py-3><span class="font-bold text-teal-300">Discrimination</span><span class="text-sm opacity-85"> — Can the model rank positives above negatives? ROC-AUC and average precision address this.</span></div>
<div v-click border="2 solid white/5" bg="white/5" rounded-lg px-4 py-3><span class="font-bold text-blue-300">Calibration</span><span class="text-sm opacity-85"> — Among cases scored near 0.8, does the event occur about 80% of the time?</span></div>
<div v-click border="2 solid white/5" bg="white/5" rounded-lg px-4 py-3><span class="font-bold text-amber-300">Check both</span><span class="text-sm opacity-85"> — A model can rank perfectly and still report misleading probabilities.</span></div>
</div>
</div>
<div>
<div v-click class="mt-4" border="2 solid teal-800" bg="teal-800/20" rounded-lg px-4 py-3>
<div class="font-bold text-teal-300 mb-2">Reliability diagram</div>
<div class="text-sm opacity-90">Group predictions by score and compare mean predicted probability with observed frequency.</div>
</div>
<div v-click class="mt-4" border="2 solid blue-800" bg="blue-800/20" rounded-lg px-4 py-3>
<div class="font-bold text-blue-300 mb-2">Proper scoring rules</div>
<div class="text-sm opacity-90">Log loss and Brier score reward useful probability estimates, not only correct rankings.</div>
</div>
</div>
</div>

<!--
AUC measures ranking, not whether the numeric probabilities are trustworthy. A model can preserve the same ranking after a monotone transformation and retain the same AUC even though its probabilities become badly distorted. Calibration asks whether predicted probabilities match observed frequencies.

Use a reliability diagram to compare predicted and observed rates across probability bins. Log loss penalizes confident wrong predictions strongly. Brier score is the mean squared error of predicted probabilities for a binary outcome. If calibration is needed, fit the calibration method using training or validation data inside the model-selection process, never on the final test set.
-->

---
glowSeed: 5182
---

# Choose the Threshold on Validation Data

<div class="grid grid-cols-2 gap-8 items-start">
<div>
<div class="space-y-3 mt-4">
<div v-click border="2 solid white/5" bg="white/5" rounded-lg px-4 py-3><span class="font-bold text-teal-300">Define the objective</span><span class="text-sm opacity-85"> — Specify error costs, capacity limits, or a required recall before searching thresholds.</span></div>
<div v-click border="2 solid white/5" bg="white/5" rounded-lg px-4 py-3><span class="font-bold text-blue-300">Tune on validation data</span><span class="text-sm opacity-85"> — Choose the threshold without looking at final test performance.</span></div>
<div v-click border="2 solid white/5" bg="white/5" rounded-lg px-4 py-3><span class="font-bold text-amber-300">Evaluate once</span><span class="text-sm opacity-85"> — Lock the model and threshold, then report final test metrics.</span></div>
</div>
</div>
<div>
<div v-click class="mt-5" border="2 solid teal-800" bg="teal-800/20" rounded-lg px-4 py-3>

$$
\mathrm{Expected\ cost}(t)=C_{FP}\,FP(t)+C_{FN}\,FN(t)
$$

</div>
<div v-click class="mt-4 text-sm opacity-85">Precision can change when deployment prevalence changes, even if sensitivity and specificity stay fixed. Recheck the operating point when the population changes.</div>
</div>
</div>

<!--
Choosing a threshold is part of model selection. First define what the operating point must accomplish: minimize an explicit cost, meet a minimum recall, keep false alerts below reviewer capacity, or satisfy another deployment constraint. Search thresholds using validation predictions or out-of-fold training predictions. Then lock the threshold before touching the test set.

The default threshold of 0.5 has no universal operational meaning. Precision and negative predictive value also depend on prevalence, so an operating point chosen in one population may behave differently after deployment. Re-evaluate it when the base rate or error costs change.
-->

---
glowSeed: 519
---

# Choose the Metric From the Consequences

<div class="grid grid-cols-2 gap-4 mt-6">
<div v-click border="2 solid teal-800" bg="teal-800/20" rounded-lg p-4>
<div class="font-bold text-teal-300 mb-2">Accuracy</div>
<div class="text-sm leading-relaxed opacity-90">Balanced classes and similar error costs.</div>
</div>
<div v-click border="2 solid blue-800" bg="blue-800/20" rounded-lg p-4>
<div class="font-bold text-blue-300 mb-2">Precision</div>
<div class="text-sm leading-relaxed opacity-90">False positives are costly.</div>
</div>
<div v-click border="2 solid amber-800" bg="amber-800/20" rounded-lg p-4>
<div class="font-bold text-amber-300 mb-2">Recall</div>
<div class="text-sm leading-relaxed opacity-90">False negatives are costly.</div>
</div>
<div v-click border="2 solid violet-800" bg="violet-800/20" rounded-lg p-4>
<div class="font-bold text-violet-300 mb-2">F1 / average precision / ROC-AUC</div>
<div class="text-sm leading-relaxed opacity-90">Balance precision and recall, or compare ranking across thresholds. Prefer a precision-recall summary when positives are rare.</div>
</div>
</div>


<!--
Metric choice is a modeling decision tied to the real application. Use accuracy when classes are reasonably balanced and the two error types have similar costs; precision when false alarms are costly; recall when misses are costly; and F1 when both precision and recall must be reasonably high. Use ROC-AUC to summarize ranking across false-positive and true-positive rates. Under heavy imbalance, inspect the precision-recall curve and report a clearly named summary such as average precision.

None of these choices are mutually exclusive in practice — a deployed system typically reports several of them together (a confusion matrix, precision, recall, F1, and AUC) so that a reviewer can see the full picture rather than a single, potentially misleading summary. The next slide packages this into a reusable toolbox and hands off to the deck on reading a confusion matrix in full detail, including the multiclass case.
-->

---
glowSeed: 520
---

# A Metric Toolbox

<div class="mt-8"><div class="grid grid-cols-4 gap-4 mt-6">
<div v-click border="2 solid teal-800" bg="teal-800/20" rounded-lg p-4>
<div class="font-bold text-teal-300 mb-2">Counts</div>
<div class="text-sm leading-relaxed opacity-90">Start with TP, TN, FP, FN.</div>
</div>
<div v-click border="2 solid blue-800" bg="blue-800/20" rounded-lg p-4>
<div class="font-bold text-blue-300 mb-2">Costs</div>
<div class="text-sm leading-relaxed opacity-90">Know which error hurts.</div>
</div>
<div v-click border="2 solid amber-800" bg="amber-800/20" rounded-lg p-4>
<div class="font-bold text-amber-300 mb-2">Thresholds</div>
<div class="text-sm leading-relaxed opacity-90">Evaluate the full tradeoff.</div>
</div>
<div v-click border="2 solid violet-800" bg="violet-800/20" rounded-lg p-4>
<div class="font-bold text-violet-300 mb-2">Probabilities</div>
<div class="text-sm leading-relaxed opacity-90">Check calibration when decisions use predicted risk.</div>
</div>
</div></div>

<div v-click class="mt-10 text-center text-lg" border="2 solid white/10" bg="white/5" rounded-lg px-6 py-4>Next: read the confusion matrix itself, including the multiclass case.</div>

<!--
Every metric in this deck is a different summary of the same underlying object: the four counts TP, TN, FP, FN, or their multiclass generalization. The workflow to take away is three steps. First, compute the raw counts from held-out predictions — never from training-set predictions, which are systematically optimistic. Second, identify which error type is more costly in the deployment context, because that determines which metric (or which weighted Fβ) is the right one to optimize and report. Third, if the deployment allows any flexibility in the decision threshold, evaluate the full curve — ROC or, under imbalance, precision-recall — rather than a single operating point, since a model that looks mediocre at the default 0.5 threshold might be excellent at a different one.

Common misconceptions to keep in mind going forward: accuracy alone hides minority-class failure (the accuracy paradox from slide 2); precision and recall trade off against each other as the threshold moves, so quoting one without the other is incomplete; F1 answers "are both precision and recall reasonably good," not "is this the best possible model"; and ROC-AUC can look strong while a model is nearly useless in practice when positives are rare. The next deck takes the confusion matrix itself as the primary object of study — reading off failure patterns directly from its cells, generalizing to K classes, and choosing between macro, weighted, and micro averaging.
-->
