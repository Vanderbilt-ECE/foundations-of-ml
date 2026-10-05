---
theme: default
highlighter: shiki
css: unocss
colorSchema: dark
title: 'Confusion Matrices'
info: |
  ## Confusion Matrices
  See which mistakes a classifier makes—not only how many
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
glowSeed: 530
---

# Confusion Matrices

### See which mistakes a classifier makes—not only how many

<div class="pt-8 opacity-80 text-lg">Model Evaluation · Foundations of Machine Learning</div>

<div class="mt-14 flex justify-center gap-4" aria-hidden="true">
<div class="w-28 h-3 rounded-full bg-teal-400/70"></div>
<div class="w-20 h-3 rounded-full bg-blue-400/60"></div>
<div class="w-14 h-3 rounded-full bg-violet-400/50"></div>
</div>

<!--
The previous deck built precision, recall, F1, and AUC out of four raw counts — TP, TN, FP, FN — and showed how a single scalar metric can hide important structure, especially under class imbalance. This deck steps back one level further: instead of collapsing a classifier's behavior into one number or even four, we look at the full confusion matrix itself, the table those four counts come from, and treat it as the primary diagnostic object.

Roadmap: binary confusion matrices and reading direction conventions, a worked example showing two classifiers with identical accuracy but opposite failure modes, generating the matrix in scikit-learn from held-out predictions, generalizing to K classes with a genuine multiclass example, and finally macro/weighted/micro averaging — three different ways to collapse per-class metrics back into one number, each of which can tell a very different story about a model with a rare class.
-->

---
glowSeed: 531
---

# The Binary Confusion Matrix

<div class="grid grid-cols-2 gap-8 items-start">
<div>
<div class="space-y-3 mt-4">
<div v-click border="2 solid white/5" bg="white/5" rounded-lg px-4 py-3>
<span class="font-bold text-teal-300">Diagonal</span>
<span class="text-sm opacity-85"> — Correct predictions: TN and TP.</span>
</div>
<div v-click border="2 solid white/5" bg="white/5" rounded-lg px-4 py-3>
<span class="font-bold text-blue-300">Off-diagonal</span>
<span class="text-sm opacity-85"> — Errors: FP and FN.</span>
</div>
<div v-click border="2 solid white/5" bg="white/5" rounded-lg px-4 py-3>
<span class="font-bold text-amber-300">Axis convention</span>
<span class="text-sm opacity-85"> — This course: rows = actual, columns = predicted (sklearn's default). Libraries disagree — always read the labels.</span>
</div>
</div>
</div>
<div>
<div role="img" aria-label="Confusion matrix with rows as actual class and columns as predicted class, cells TN FP FN TP" class="mt-6 max-w-lg mx-auto">
<div class="grid grid-cols-[6.5rem_1fr_1fr] gap-2 text-center text-xs">
<div></div><div class="font-bold text-blue-300">Pred: Negative</div><div class="font-bold text-blue-300">Pred: Positive</div>
<div class="flex items-center justify-end pr-2 font-bold text-teal-300">Actual: Negative</div><div border="2 solid teal-800" bg="teal-800/20" rounded-lg p-4><div class="text-lg font-bold">TN</div></div><div border="2 solid red-800" bg="red-800/20" rounded-lg p-4><div class="text-lg font-bold">FP</div></div>
<div class="flex items-center justify-end pr-2 font-bold text-teal-300">Actual: Positive</div><div border="2 solid red-800" bg="red-800/20" rounded-lg p-4><div class="text-lg font-bold">FN</div></div><div border="2 solid teal-800" bg="teal-800/20" rounded-lg p-4><div class="text-lg font-bold">TP</div></div>
</div>
</div>
</div>
</div>

<!--
The confusion matrix is the table those four counts come from: two rows for the two possible true labels, two columns for the two possible predicted labels, four cells. The diagonal (TN, top-left; TP, bottom-right) is every correct prediction. The off-diagonal (FP, top-right; FN, bottom-left) is every error, split by direction: FP is a negative example the model called positive, FN is a positive example the model called negative.

Fix the reading convention before doing anything else with this matrix, because it is the single most common source of confusion when comparing two classifiers or two libraries: this course follows scikit-learn's convention, confusion_matrix(y_true, y_pred), where rows index the actual label and columns index the predicted label. Under that convention, row sums are the true class sizes (support) and column sums are how many times the model predicted each class. Some textbooks and tools flip this — predicted-as-rows, actual-as-columns — which silently swaps where FP and FN appear. There is no universal standard, so the discipline is: before reading any confusion matrix, find its axis labels and confirm which convention it uses. Have students derive accuracy, precision, and recall directly from these four cells using the formulas from the previous deck before moving on.
-->

---
glowSeed: 532
---

# Same Accuracy, Different Failure

<div class="grid grid-cols-2 gap-6 items-start">
<div>
<div class="text-sm font-bold text-teal-300 mb-2 text-center">Model A — false-positive heavy</div>
<div role="img" aria-label="Model A confusion matrix: TN 840, FP 60, FN 20, TP 80" class="max-w-xs mx-auto">
<div class="grid grid-cols-[4rem_1fr_1fr] gap-1 text-center text-xs">
<div></div><div class="font-bold text-blue-300">Pred N</div><div class="font-bold text-blue-300">Pred P</div>
<div class="flex items-center justify-end pr-1 font-bold text-teal-300">Act N</div><div border="2 solid teal-800" bg="teal-800/20" rounded p-2>840</div><div border="2 solid red-800" bg="red-800/20" rounded p-2>60</div>
<div class="flex items-center justify-end pr-1 font-bold text-teal-300">Act P</div><div border="2 solid red-800" bg="red-800/20" rounded p-2>20</div><div border="2 solid teal-800" bg="teal-800/20" rounded p-2>80</div>
</div>
</div>
<div class="text-xs opacity-75 mt-2 text-center">Accuracy = 920/1000 = 0.92. More false alarms (60 FP), fewer misses (20 FN).</div>
</div>
<div>
<div class="text-sm font-bold text-blue-300 mb-2 text-center">Model B — false-negative heavy</div>
<div role="img" aria-label="Model B confusion matrix: TN 870, FP 30, FN 50, TP 50" class="max-w-xs mx-auto">
<div class="grid grid-cols-[4rem_1fr_1fr] gap-1 text-center text-xs">
<div></div><div class="font-bold text-blue-300">Pred N</div><div class="font-bold text-blue-300">Pred P</div>
<div class="flex items-center justify-end pr-1 font-bold text-teal-300">Act N</div><div border="2 solid teal-800" bg="teal-800/20" rounded p-2>870</div><div border="2 solid red-800" bg="red-800/20" rounded p-2>30</div>
<div class="flex items-center justify-end pr-1 font-bold text-teal-300">Act P</div><div border="2 solid red-800" bg="red-800/20" rounded p-2>50</div><div border="2 solid teal-800" bg="teal-800/20" rounded p-2>50</div>
</div>
</div>
<div class="text-xs opacity-75 mt-2 text-center">Accuracy = 920/1000 = 0.92. Few false alarms, many misses (50 FN, recall only 50%).</div>
</div>
</div>

<div v-click class="mt-5 text-center text-sm" border="2 solid amber-800" bg="amber-800/20" rounded-lg px-4 py-3>
Accuracy alone cannot distinguish these two error profiles — you must look at the matrix to see which type of mistake a model makes.
</div>

<!--
These classifiers have exactly the same accuracy, 920/1000 = 0.92, while failing in operationally different ways. Model A trades precision for recall: it produces 60 false positives and 20 false negatives, so recall is 80/100 = 0.80 and precision is 80/140 ≈ 0.57. Model B does the reverse: it produces only 30 false positives but 50 false negatives, so precision is 50/80 = 0.625 while recall falls to 50/100 = 0.50.

Ask which model fits which deployment. For airport security screening, missing a real threat is more costly than a false alarm that triggers extra screening, so Model A's higher-recall profile is the better fit. For a spam filter, a false positive can hide a legitimate message while a false negative usually means one more spam message to delete, so Model B's profile may fit better. The general lesson is that accuracy can be identical while the consequences differ sharply.
-->

---
glowSeed: 5321
---

# Specificity and Negative Predictive Value

<div class="grid grid-cols-2 gap-8 items-start">
<div>
<div class="space-y-3 mt-4">
<div v-click border="2 solid white/5" bg="white/5" rounded-lg px-4 py-3>
<span class="font-bold text-teal-300">Specificity</span>
<span class="text-sm opacity-85"> — Of all actual negatives, how many did the model correctly reject?</span>
</div>
<div v-click border="2 solid white/5" bg="white/5" rounded-lg px-4 py-3>
<span class="font-bold text-blue-300">Negative predictive value</span>
<span class="text-sm opacity-85"> — When the model says negative, how often is it right?</span>
</div>
<div v-click border="2 solid white/5" bg="white/5" rounded-lg px-4 py-3>
<span class="font-bold text-amber-300">Clinical language</span>
<span class="text-sm opacity-85"> — Recall is also sensitivity. These four rates describe both sides of a screening decision.</span>
</div>
</div>
</div>
<div>
<div v-click class="mt-5" border="2 solid teal-800" bg="teal-800/20" rounded-lg px-4 py-3>

$$
\mathrm{Specificity}=\frac{TN}{TN+FP}
$$

</div>
<div v-click class="mt-4" border="2 solid blue-800" bg="blue-800/20" rounded-lg px-4 py-3>

$$
\mathrm{NPV}=\frac{TN}{TN+FN}
$$

</div>
</div>
</div>

<!--
Precision and recall focus on positive decisions. Specificity and negative predictive value complete the picture. Specificity conditions on the actual negatives, so its denominator is TN+FP. Negative predictive value conditions on negative predictions, so its denominator is TN+FN. Recall is often called sensitivity in medical settings.

Keep the conditioning questions explicit. Sensitivity and specificity describe performance within the true positive and true negative groups. Precision and NPV describe how trustworthy positive and negative predictions are. Precision and NPV therefore change when prevalence changes, even if sensitivity and specificity remain stable.
-->

---
glowSeed: 533
---

# Compute and Display the Matrix

<div class="grid grid-cols-2 gap-4 mt-6">
<div v-click border="2 solid teal-800" bg="teal-800/20" rounded-lg p-4>
<div class="font-bold text-teal-300 mb-2">Raw counts</div>
<div class="text-sm leading-relaxed opacity-90">confusion_matrix returns the table as a NumPy array.</div>
</div>
<div v-click border="2 solid blue-800" bg="blue-800/20" rounded-lg p-4>
<div class="font-bold text-blue-300 mb-2">Readable diagnostic</div>
<div class="text-sm leading-relaxed opacity-90">ConfusionMatrixDisplay adds axis labels and color intensity.</div>
</div>
</div>

```python {2,4,5-7}
from sklearn.metrics import (
    confusion_matrix, ConfusionMatrixDisplay,
)

y_pred = model.predict(X_test)          # never predict(X_train)
cm = confusion_matrix(y_test, y_pred)   # rows=actual, cols=predicted
print(cm)
ConfusionMatrixDisplay(
    cm, display_labels=["Negative", "Positive"],
).plot()
```

<!--
confusion_matrix takes the true labels and the predicted labels and returns a NumPy array following the rows-are-actual, columns-are-predicted convention we fixed two slides ago; by default classes are ordered alphabetically/numerically, but you can force an order with the labels argument, which matters when you want negative-then-positive rather than whatever the sort order gives you. ConfusionMatrixDisplay wraps that array into a readable heatmap with axis labels and shaded cell intensity so a reviewer does not have to squint at raw numbers.

The single most important discipline on this slide is highlighted in the code: y_pred must come from model.predict(X_test), never model.predict(X_train). A confusion matrix built from training-set predictions measures how well the model memorized the data it already saw, which is systematically optimistic — sometimes dramatically so for high-capacity models that can overfit — and tells you nothing reliable about generalization. This is the same held-out-evaluation discipline from Train-Validation-Test Splits, just applied to the confusion matrix specifically rather than to a single scalar metric. Every confusion matrix in this deck, and every confusion matrix you build for an assignment, should be computed on data the model did not train on.
-->

---
glowSeed: 534
---

# Multiclass: A K × K Error Map

<div class="grid grid-cols-2 gap-6 items-start">
<div>
<div class="space-y-3 mt-2">
<div v-click border="2 solid white/5" bg="white/5" rounded-lg px-4 py-3>
<span class="font-bold text-teal-300">Diagonal</span>
<span class="text-sm opacity-85"> — Correct predictions for each of the K classes.</span>
</div>
<div v-click border="2 solid white/5" bg="white/5" rounded-lg px-4 py-3>
<span class="font-bold text-blue-300">Off-diagonal structure</span>
<span class="text-sm opacity-85"> — Which specific class pairs the model confuses, e.g. digit 4 ↔ 9.</span>
</div>
<div v-click border="2 solid white/5" bg="white/5" rounded-lg px-4 py-3>
<span class="font-bold text-amber-300">Per-class metrics</span>
<span class="text-sm opacity-85"> — Treat class k as "positive," every other class as "negative."</span>
</div>
</div>
<div v-click class="mt-3 text-sm" style="font-size: .85em" border="2 solid teal-800" bg="teal-800/20" rounded-lg px-4 py-3>

$$
P_k=\frac{C_{kk}}{\sum_i C_{ik}},\qquad R_k=\frac{C_{kk}}{\sum_j C_{kj}}
$$

</div>
</div>
<div>
<div role="img" aria-label="3 by 3 confusion matrix for digits 0, 4, 9 showing confusion concentrated between 4 and 9" class="mt-2 max-w-md mx-auto">
<div class="grid grid-cols-[3rem_1fr_1fr_1fr] gap-1 text-center text-xs">
<div></div><div class="font-bold text-blue-300">P: 0</div><div class="font-bold text-blue-300">P: 4</div><div class="font-bold text-blue-300">P: 9</div>
<div class="flex items-center justify-end pr-1 font-bold text-teal-300">A: 0</div><div border="2 solid teal-800" bg="teal-800/20" rounded p-3 font-bold>50</div><div border="2 solid white/10" bg="white/5" rounded p-3>0</div><div border="2 solid white/10" bg="white/5" rounded p-3>0</div>
<div class="flex items-center justify-end pr-1 font-bold text-teal-300">A: 4</div><div border="2 solid white/10" bg="white/5" rounded p-3>0</div><div border="2 solid teal-800" bg="teal-800/20" rounded p-3 font-bold>40</div><div border="2 solid red-800" bg="red-800/20" rounded p-3 font-bold>8</div>
<div class="flex items-center justify-end pr-1 font-bold text-teal-300">A: 9</div><div border="2 solid white/10" bg="white/5" rounded p-3>0</div><div border="2 solid red-800" bg="red-800/20" rounded p-3 font-bold>6</div><div border="2 solid teal-800" bg="teal-800/20" rounded p-3 font-bold>44</div>
</div>
</div>
<div class="text-xs opacity-75 mt-3">Digit classifier, 148 test images. 0s are never confused; 4s and 9s — visually similar handwritten shapes — leak into each other in both directions.</div>
</div>
</div>

<!--
Generalize the 2×2 matrix to K classes and nothing structurally changes: it is still a table of counts C indexed by (actual row, predicted column), the diagonal C_kk is still "correct," and the off-diagonal is still errors — but now errors have direction and identity, because a K×K matrix tells you not just that the model was wrong but which class it confused with which. The example here is a 3-class digit classifier (0, 4, 9): the digit 0 is never confused with anything (its row and column outside the diagonal are all zero), but 4 and 9 leak into each other substantially — 8 true 4s predicted as 9, and 6 true 9s predicted as 4 — which matches real handwriting, where a hastily written 4 and 9 can look alike. This off-diagonal structure often reveals something about the data itself, not just the model, which is why reading the full matrix is more informative than any single aggregate score.

To get a per-class precision and recall out of a multiclass matrix, treat class k as the positive class and every other class as negative, exactly the one-vs-rest framing scikit-learn uses internally. P_k = C_kk / Σ_i C_ik: the diagonal count for class k divided by the sum of column k (everything predicted as k) — this is precision because the column is "all things predicted k." R_k = C_kk / Σ_j C_kj: the diagonal count divided by the sum of row k (everything actually k) — this is recall because the row is "all things actually k." These formulas are only correct under the rows-are-actual, columns-are-predicted convention fixed earlier in the deck; flip that convention and the two formulas for P_k and R_k swap. Next we see how to collapse K per-class numbers back into one summary score, and how that collapse can hide the very structure we just uncovered.
-->

---
glowSeed: 535
---

# Macro, Weighted, and Micro Averaging

<div class="grid grid-cols-2 gap-4 mt-4">
<div v-click border="2 solid teal-800" bg="teal-800/20" rounded-lg p-4>
<div class="font-bold text-teal-300 mb-2">Macro</div>
<div class="text-sm leading-relaxed opacity-90">Unweighted mean of per-class scores; every class counts equally regardless of size.</div>
</div>
<div v-click border="2 solid blue-800" bg="blue-800/20" rounded-lg p-4>
<div class="font-bold text-blue-300 mb-2">Weighted</div>
<div class="text-sm leading-relaxed opacity-90">Mean of per-class scores weighted by support (class size).</div>
</div>
<div v-click border="2 solid amber-800" bg="amber-800/20" rounded-lg p-4>
<div class="font-bold text-amber-300 mb-2">Micro</div>
<div class="text-sm leading-relaxed opacity-90">Pool every TP/FP/FN across all classes first, then compute one ratio; equals accuracy here.</div>
</div>
<div v-click border="2 solid violet-800" bg="violet-800/20" rounded-lg p-4>
<div class="font-bold text-violet-300 mb-2">Rule of thumb</div>
<div class="text-sm leading-relaxed opacity-90">Always check per-class recall when a rare class matters.</div>
</div>
</div>

<div v-click class="mt-4 text-xs" border="2 solid white/10" bg="white/5" rounded-lg px-4 py-3>
Support 920 / 970 / 10, rare class recall = 0.10 &nbsp;→&nbsp; <span class="text-red-300 font-bold">macro recall = 0.682</span>, but <span class="text-teal-300 font-bold">weighted recall = 0.969</span> and <span class="text-teal-300 font-bold">micro recall = 0.969</span>. The averages that weight by class size never show you the rare class is failing.
</div>

<!--
All three averages start from the same per-class precision, recall, or F1, but they collapse them into one number in different ways, and the difference is not cosmetic. Macro-average takes the unweighted arithmetic mean across classes — every class, however small, contributes equally, so a model that is terrible on one rare class drags the macro score down noticeably. Weighted-average takes the mean weighted by each class's support (how many true examples it has), so large classes dominate. Micro-average takes a different approach entirely: pool the TP, FP, FN counts across all classes into single totals first, then compute one precision/recall/F1 from those totals — for standard single-label multiclass classification this always equals overall accuracy, because every misclassification is simultaneously an FP for the predicted class and an FN for the true class, so they cancel symmetrically in the pooled counts.

The worked numbers on this slide make the danger concrete: three classes with support 920, 970, and 10, where the rare class is almost never recalled correctly (10% recall — the model catches essentially nothing of it). Macro recall reports 0.682, which correctly signals a serious problem, because the rare class's poor 0.10 gets full equal weight alongside the other two classes' 0.98 and 0.97. But weighted recall reports 0.969 and micro recall also reports 0.969 — both numbers look excellent, because the rare class, contributing only 10 of 1,900 examples, is mathematically swamped by the two large classes. If you only reported weighted or micro F1 on a rare-but-important class — fraud, a rare disease subtype, a safety-critical failure mode — you would ship a system that fails almost completely on exactly the case you cared about, while your one summary number looked great. Rule of thumb: whenever a rare class matters, inspect its per-class recall and precision directly rather than trusting any averaged summary.
-->

---
glowSeed: 536
---

# One Table, Every Classification Metric

<div class="mt-6"><div class="grid grid-cols-3 gap-4 mt-4">
<div v-click border="2 solid teal-800" bg="teal-800/20" rounded-lg p-4>
<div class="font-bold text-teal-300 mb-2">Diagnose</div>
<div class="text-sm leading-relaxed opacity-90">Read error direction from off-diagonal cells.</div>
</div>
<div v-click border="2 solid blue-800" bg="blue-800/20" rounded-lg p-4>
<div class="font-bold text-blue-300 mb-2">Generalize</div>
<div class="text-sm leading-relaxed opacity-90">Use K × K for multiclass; per-class P/R from rows/columns.</div>
</div>
<div v-click border="2 solid amber-800" bg="amber-800/20" rounded-lg p-4>
<div class="font-bold text-amber-300 mb-2">Summarize carefully</div>
<div class="text-sm leading-relaxed opacity-90">Choose macro, weighted, or micro explicitly — do not accept a library default blindly.</div>
</div>
</div></div>

<div v-click class="mt-10 text-center text-lg" border="2 solid white/10" bg="white/5" rounded-lg px-6 py-4>Next: decide whether two measured model scores are genuinely different.</div>

<!--
The confusion matrix preserves information that every aggregate metric discards, which is the thread running through this whole deck: accuracy collapses four numbers into one, precision and recall each collapse them into a different one, and even a full multiclass matrix eventually gets summarized into macro, weighted, or micro F1 for a leaderboard or a report. Every collapse loses information, and the two worked examples in this deck showed exactly what gets lost — two same-accuracy-range models with opposite error profiles, and a rare class whose failure disappears under weighted or micro averaging.

The practical habit to leave with: always look at the raw confusion matrix before trusting any single summary metric, always compute it on held-out data, and when you do report an averaged multiclass score, state explicitly which averaging scheme you used and why — macro if every class matters equally regardless of size, weighted if you want an accuracy-like number that respects class frequency, micro if you want the single global agreement rate. The next deck asks a different question about the numbers we have been computing: given that a test-set score is itself a noisy estimate, when can you actually say one model beats another, versus when is the gap just sampling variation?
-->
