---
theme: default
highlighter: shiki
css: unocss
colorSchema: dark
title: 'Common Pitfalls: Data Leakage and Class Imbalance'
info: |
  ## Common Pitfalls: Data Leakage and Class Imbalance
  When excellent-looking numbers cannot be trusted
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
glowSeed: 580
---

# Common Pitfalls: Data Leakage and Class Imbalance

### When excellent-looking numbers cannot be trusted

<div class="pt-8 opacity-80 text-lg">Model Evaluation · Foundations of Machine Learning</div>

<div class="mt-14 flex justify-center gap-4" aria-hidden="true">
<div class="w-28 h-3 rounded-full bg-teal-400/70"></div>
<div class="w-20 h-3 rounded-full bg-blue-400/60"></div>
<div class="w-14 h-3 rounded-full bg-violet-400/50"></div>
</div>

<!--
Every metric and every significance test built in this module — accuracy, precision, recall, F1, ROC-AUC, the confusion matrix, McNemar's test, the paired t-test — assumes the underlying evaluation itself is sound: that the test score actually reflects how the model will perform on new, unseen data. This closing deck is about the two most common ways that assumption silently breaks, producing numbers that look excellent right up until deployment.

Roadmap: data leakage — information the model should not have had access to sneaking into training — with an end-to-end demonstration showing exactly how much a leaky evaluation can lie to you, then class imbalance — how a skewed label distribution distorts both training and evaluation even when the pipeline is otherwise correct. We close with a pre-deployment checklist that ties this back to every prior deck in the module: the setup has to be right before any metric or significance test means anything at all.
-->

---
glowSeed: 581
---

# Data Leakage: Information From the Wrong Time

<div class="grid grid-cols-2 gap-8 items-start">
<div>
<div class="space-y-3 mt-4">
<div v-click border="2 solid white/5" bg="white/5" rounded-lg px-4 py-3>
<span class="font-bold text-teal-300">Definition</span>
<span class="text-sm opacity-85"> — Information unavailable at prediction time influences training or feature construction.</span>
</div>
<div v-click border="2 solid white/5" bg="white/5" rounded-lg px-4 py-3>
<span class="font-bold text-blue-300">Result</span>
<span class="text-sm opacity-85"> — Evaluation looks excellent; deployment performance collapses.</span>
</div>
<div v-click border="2 solid white/5" bg="white/5" rounded-lg px-4 py-3>
<span class="font-bold text-amber-300">Diagnostic question</span>
<span class="text-sm opacity-85"> — Would this exact information exist, in this exact form, at the moment the model must predict?</span>
</div>
</div>
</div>
<div>
<div class="mt-5" role="img" aria-label="Full data then Leaky transform then Train then Inflated score">
<div v-click class="flex items-center gap-3">
<div class="w-8 h-8 rounded-full bg-teal-500/20 border-2 border-teal-700 flex items-center justify-center text-sm font-bold">1</div>
<div class="flex-1 rounded-lg border-2 border-white/10 bg-white/5 px-3 py-2 text-sm font-bold">Full data (train + test together)</div>
</div>
<div class="ml-4 h-1 border-l-2 border-teal-400/50"></div>
<div v-click class="flex items-center gap-3">
<div class="w-8 h-8 rounded-full bg-blue-500/20 border-2 border-blue-700 flex items-center justify-center text-sm font-bold">2</div>
<div class="flex-1 rounded-lg border-2 border-white/10 bg-white/5 px-3 py-2 text-sm font-bold">Transform fit on everything, test included</div>
</div>
<div class="ml-4 h-1 border-l-2 border-teal-400/50"></div>
<div v-click class="flex items-center gap-3">
<div class="w-8 h-8 rounded-full bg-amber-500/20 border-2 border-amber-700 flex items-center justify-center text-sm font-bold">3</div>
<div class="flex-1 rounded-lg border-2 border-white/10 bg-white/5 px-3 py-2 text-sm font-bold">Train and evaluate as usual</div>
</div>
<div class="ml-4 h-1 border-l-2 border-teal-400/50"></div>
<div v-click class="flex items-center gap-3">
<div class="w-8 h-8 rounded-full bg-violet-500/20 border-2 border-violet-700 flex items-center justify-center text-sm font-bold">4</div>
<div class="flex-1 rounded-lg border-2 border-white/10 bg-white/5 px-3 py-2 text-sm font-bold">Inflated score — the test set has already leaked in</div>
</div>
</div>

</div>
</div>

<!--
Data leakage is a timing and information-boundary failure: some piece of information that would not actually be available at the moment a real prediction has to be made — often because it comes from the test set itself, or from the future relative to the prediction point, or is a disguised copy of the label — ends up influencing the trained model anyway. The mechanism in this flow diagram is the most common form: statistics are computed from the full dataset (steps 1–2), including examples that are supposed to be held out for testing, before the model is trained and scored (steps 3–4). Because the "held-out" test examples secretly contributed to the transform the model relies on, the resulting score in step 4 measures something closer to "how well did the model memorize statistics of this exact dataset" than "how well will the model generalize to new data."

The single diagnostic question to apply to any feature or preprocessing step is: would this information exist, in this exact form, at the moment a real, future example needs a prediction? If a feature encodes information about the entire dataset (like "this row's z-score relative to all 10,000 rows, test rows included"), the answer is no — a genuinely new example arriving one at a time would not have access to statistics that depend on rows not yet collected. The next three slides work through the specific, concrete version of this failure that catches almost every beginner: fitting preprocessing before splitting.
-->

---
glowSeed: 582
---

# Split Before You Fit Preprocessing

<div class="grid grid-cols-3 gap-4 mt-6">
<div v-click border="2 solid teal-800" bg="teal-800/20" rounded-lg p-4>
<div class="font-bold text-teal-300 mb-2">Wrong</div>
<div class="text-sm leading-relaxed opacity-90">Fit scaling, imputation, or feature selection on the full dataset, then split into train/test.</div>
</div>
<div v-click border="2 solid blue-800" bg="blue-800/20" rounded-lg p-4>
<div class="font-bold text-blue-300 mb-2">Right</div>
<div class="text-sm leading-relaxed opacity-90">Split first; fit every transform only on the training data; apply the fitted transform unchanged to validation/test.</div>
</div>
<div v-click border="2 solid amber-800" bg="amber-800/20" rounded-lg p-4>
<div class="font-bold text-amber-300 mb-2">Best guardrail</div>
<div class="text-sm leading-relaxed opacity-90">Use a scikit-learn Pipeline so cross-validation automatically refits preprocessing inside each training fold.</div>
</div>
</div>


<!--
This is the single most common beginner leakage path, and it is also the easiest one to prevent structurally rather than by vigilance alone. The wrong order: call StandardScaler().fit(X) — or a SelectKBest, an imputer's mean, a PCA, any transform with learned parameters — on the entire dataset X, and only afterward split into X_train and X_test. Every statistic that transform learned (the mean and standard deviation for scaling, the selected feature indices for selection, the principal components for PCA) was computed using the test rows too, so the "held-out" test set has already been peeked at before the model ever sees it, even though no single line of code looks obviously wrong.

The right order reverses this: split first, fit every learned transform using only X_train, then apply that already-fitted transform to X_test without refitting it — X_test never contributes a single number to how the transform behaves. In practice, doing this by hand for every transform, every time, across cross-validation folds, is tedious and error-prone, which is exactly why the guardrail on this slide — a scikit-learn Pipeline combined with cross_val_score or GridSearchCV — exists: the pipeline automatically refits every preprocessing step from scratch on only the current training fold each time, so leakage of this specific kind becomes structurally impossible rather than something you have to remember to avoid. The next slide shows the code, then we quantify exactly how much this mistake can inflate a score.
-->

---
glowSeed: 583
---

# A Pipeline Enforces the Boundary

<div class="grid grid-cols-2 gap-4 mt-6">
<div v-click border="2 solid teal-800" bg="teal-800/20" rounded-lg p-4>
<div class="font-bold text-teal-300 mb-2">Fit</div>
<div class="text-sm leading-relaxed opacity-90">Each cross-validation fold learns its own scaling statistics from its own training rows.</div>
</div>
<div v-click border="2 solid blue-800" bg="blue-800/20" rounded-lg p-4>
<div class="font-bold text-blue-300 mb-2">Transform</div>
<div class="text-sm leading-relaxed opacity-90">Held-out rows for that fold are transformed, never used to compute the statistics.</div>
</div>
</div>

```python {6-8,9}
from sklearn.pipeline import make_pipeline
from sklearn.preprocessing import StandardScaler
from sklearn.linear_model import LogisticRegression
from sklearn.model_selection import cross_val_score

model = make_pipeline(
    StandardScaler(), LogisticRegression(),
)
scores = cross_val_score(model, X, y, cv=5)
assert np.isfinite(scores).all()
```

<!--
make_pipeline chains StandardScaler and LogisticRegression into a single estimator object that exposes one fit/predict interface but internally keeps the boundary between them strict. cross_val_score(model, X, y, cv=5) then does the correct thing automatically: for each of the 5 folds, it takes the training portion of that fold, calls the whole pipeline's fit on it — which fits StandardScaler's mean and standard deviation using only those training rows, then fits LogisticRegression on the scaled training rows — and only then calls the pipeline's predict on the held-out portion of that fold, which reuses the already-fitted scaler's parameters without recomputing them from the held-out data.

The assert on the last line is a habit worth adopting generally, not just here: after any cross-validation run, check that every returned score is finite (np.isfinite) before trusting or reporting it, since a NaN or infinite score usually signals a numerical problem (a fold with a degenerate class distribution, non-converged optimization) that would otherwise silently corrupt a mean score. Default to wrapping preprocessing and modeling in a Pipeline whenever any step "learns" something from the data — scaling, imputation, feature selection, dimensionality reduction — because manual, outside-the-pipeline preprocessing is where leakage most often hides. Next we make the cost of skipping this discipline concrete with real numbers.
-->

---
glowSeed: 584
---

# How Much Does Leakage Actually Inflate a Score?

<div class="grid grid-cols-2 gap-6 items-start">
<div>
<div class="text-sm opacity-85 mb-3">Setup: 200 examples, 5,000 pure-noise features, labels assigned independently at random — the true relationship between X and y is <strong>zero</strong>. Any signal a model finds is illusory.</div>

```python {2-3,6-7}
# LEAKY: select top-20 features using ALL data
selector = SelectKBest(f_classif, k=20)
selector.fit(X, y)                # sees y for every row
X_sel = selector.transform(X)
leaky = cross_val_score(
    LogisticRegression(), X_sel, y, cv=5,
)  # mean ≈ 0.81

# HONEST: selection refit inside each fold
pipe = make_pipeline(
    SelectKBest(f_classif, k=20), LogisticRegression(),
)
honest = cross_val_score(pipe, X, y, cv=5)
# mean ≈ 0.43 — chance is 0.50
```

</div>
<div>
<div v-click class="mt-2" border="2 solid red-800" bg="red-800/20" rounded-lg p-4>
<div class="font-bold text-red-300 mb-1">Leaky pipeline</div>
<div class="text-2xl font-bold">≈ 0.81 accuracy</div>
<div class="text-xs opacity-75 mt-1">Feature selection saw the labels for every row, including the "held-out" fold, before cross-validation began — it hand-picked 20 noise columns that happen to correlate with y by chance.</div>
</div>
<div v-click class="mt-4" border="2 solid teal-800" bg="teal-800/20" rounded-lg p-4>
<div class="font-bold text-teal-300 mb-1">Honest pipeline</div>
<div class="text-2xl font-bold">≈ 0.43 accuracy</div>
<div class="text-xs opacity-75 mt-1">Selection is refit inside each fold using only that fold's training rows; performance correctly lands near the 0.50 chance rate for a label with no real signal.</div>
</div>
</div>
</div>

<!--
This is a controlled demonstration where we know the ground truth: X is 200 rows of pure Gaussian noise across 5,000 columns, and y is assigned independently at random — by construction there is zero true relationship between any feature and the label, so any classifier's honest expected accuracy is 0.5, chance. The leaky version runs SelectKBest(f_classif, k=20).fit(X, y) once on the entire dataset before cross-validation starts; because f_classif scores each of the 5,000 features against y, and with 5,000 candidates some will correlate with y purely by chance, this selects 20 columns that look predictive — but only because the selection step already "saw" the labels of every row, including whichever rows later land in each fold's held-out portion. Running 5-fold cross-validation on that pre-selected feature set gives roughly 0.81 accuracy — a number that looks like a genuinely strong classifier.

The honest version wraps SelectKBest inside a Pipeline with LogisticRegression, so cross_val_score refits the feature selection from scratch using only each fold's training rows, exactly as the previous slide's discipline demands; every fold selects a different set of 20 "best" noise columns because each fold sees different training data, and none of those columns has any real relationship to that fold's held-out labels. The honest score lands around 0.43 — statistically indistinguishable from the 0.5 chance rate you would expect for genuinely unrelated data. The gap between 0.81 and 0.43 on data with zero true signal is the entire lesson of this deck in one comparison: the leaky pipeline did not build a better model, it built an evaluation that lied by roughly 38 percentage points. This exact bug — feature selection or hyperparameter tuning performed outside the cross-validation loop — is common enough in real published work that it has its own name in the literature: "double dipping."
-->

---
glowSeed: 585
---

# Target and Temporal Leakage

<div class="grid grid-cols-2 gap-8 items-start">
<div>
<div class="space-y-3 mt-4">
<div v-click border="2 solid white/5" bg="white/5" rounded-lg px-4 py-3>
<span class="font-bold text-teal-300">Target proxy</span>
<span class="text-sm opacity-85"> — A feature indirectly encodes the label, e.g. "sent to collections" as a feature for predicting loan default.</span>
</div>
<div v-click border="2 solid white/5" bg="white/5" rounded-lg px-4 py-3>
<span class="font-bold text-blue-300">Future information</span>
<span class="text-sm opacity-85"> — A feature's time window extends past the moment of prediction, e.g. using a patient's full hospital stay to predict admission.</span>
</div>
<div v-click border="2 solid white/5" bg="white/5" rounded-lg px-4 py-3>
<span class="font-bold text-amber-300">Symptom</span>
<span class="text-sm opacity-85"> — Suspiciously high performance, or one feature with implausibly enormous importance, that cannot survive real timing constraints.</span>
</div>
</div>
</div>
<div>
<div class="mt-5" role="img" aria-label="Past features then Prediction time then Future event then Leaked label">
<div v-click class="flex items-center gap-3">
<div class="w-8 h-8 rounded-full bg-teal-500/20 border-2 border-teal-700 flex items-center justify-center text-sm font-bold">1</div>
<div class="flex-1 rounded-lg border-2 border-white/10 bg-white/5 px-3 py-2 text-sm font-bold">Past features (legitimately available)</div>
</div>
<div class="ml-4 h-1 border-l-2 border-teal-400/50"></div>
<div v-click class="flex items-center gap-3">
<div class="w-8 h-8 rounded-full bg-blue-500/20 border-2 border-blue-700 flex items-center justify-center text-sm font-bold">2</div>
<div class="flex-1 rounded-lg border-2 border-white/10 bg-white/5 px-3 py-2 text-sm font-bold">Prediction time — the model must act now</div>
</div>
<div class="ml-4 h-1 border-l-2 border-teal-400/50"></div>
<div v-click class="flex items-center gap-3">
<div class="w-8 h-8 rounded-full bg-amber-500/20 border-2 border-amber-700 flex items-center justify-center text-sm font-bold">3</div>
<div class="flex-1 rounded-lg border-2 border-white/10 bg-white/5 px-3 py-2 text-sm font-bold">Future event (not yet knowable)</div>
</div>
<div class="ml-4 h-1 border-l-2 border-teal-400/50"></div>
<div v-click class="flex items-center gap-3">
<div class="w-8 h-8 rounded-full bg-violet-500/20 border-2 border-violet-700 flex items-center justify-center text-sm font-bold">4</div>
<div class="flex-1 rounded-lg border-2 border-white/10 bg-white/5 px-3 py-2 text-sm font-bold">Leaked label — feature 3 quietly encodes it</div>
</div>
</div>

</div>
</div>

<!--
Preprocessing-before-split leakage is mechanical and structural; target and temporal leakage is about feature content and is harder to catch automatically, because the code can be entirely correct — split first, fit only on training data, use a pipeline — and the leakage still happens because a feature itself should not exist at prediction time. A target proxy is a feature that is not literally the label but is causally downstream of it or a near-restatement of it: predicting loan default using a "sent to collections" flag is a canonical example, because being sent to collections essentially only happens to people who are already defaulting or about to — the feature is a leaked description of the outcome, not a genuine predictor of it. A model trained on that feature will look almost perfect and be almost useless, because at the real moment a default-risk prediction is needed, the collections flag does not exist yet.

Future-information leakage is the temporal version: a feature's value was computed using a time window that extends past the actual moment the model has to predict — for example, using statistics from a patient's entire hospital stay (including events that happen after admission) to predict whether that patient will be admitted, or using a full month's transaction history to predict a fraud decision that has to be made in real time on a single transaction. The practical symptom of either failure is the same: performance that looks too good relative to how hard the underlying problem intuitively is, or a feature-importance ranking dominated by one implausibly powerful feature. Whenever you see either symptom, apply the diagnostic question from the start of this deck to every feature individually: would this exact value exist, unaltered, at the real moment a genuinely new example needs a prediction?
-->

---
glowSeed: 586
---

# Class Imbalance Distorts Training and Evaluation

<div class="grid grid-cols-2 gap-8 items-start">
<div>
<div class="space-y-3 mt-4">
<div v-click border="2 solid white/5" bg="white/5" rounded-lg px-4 py-3>
<span class="font-bold text-teal-300">Evaluation</span>
<span class="text-sm opacity-85"> — Accuracy can ignore near-total failure on a rare class (the accuracy paradox, revisited).</span>
</div>
<div v-click border="2 solid white/5" bg="white/5" rounded-lg px-4 py-3>
<span class="font-bold text-blue-300">Training</span>
<span class="text-sm opacity-85"> — The majority class dominates average empirical risk, so the optimizer barely notices minority-class errors.</span>
</div>
<div v-click border="2 solid white/5" bg="white/5" rounded-lg px-4 py-3>
<span class="font-bold text-amber-300">Consequence</span>
<span class="text-sm opacity-85"> — The fitted model learns that majority-favoring errors are cheap and minority errors are nearly free.</span>
</div>
</div>
</div>
<div>
<div v-click class="mt-4" style="font-size: .9em" border="2 solid teal-800" bg="teal-800/20" rounded-lg px-4 py-3>

$$
\widehat R(\theta)=\frac1n\sum_i\ell(f_\theta(x_i),y_i)
$$

</div>
<div v-click class="mt-3 text-xs opacity-75">With 990 majority and 10 minority examples, minority mistakes contribute only 10/1000 = 1% of the total sum — the optimizer has almost no incentive to fix them.</div>

</div>
</div>

<!--
The Accuracy deck opened with the accuracy paradox — a trivial "always predict majority" classifier hitting 99% accuracy on a 990/10 split — and this slide connects that same imbalance directly to the training objective itself, not just the reporting metric, which is a distinct and equally important failure mode. R-hat(θ) is the empirical risk: the average, over all n training examples, of the loss ℓ between the model's prediction f_θ(x_i) and the true label y_i — this is literally what gradient descent is minimizing during training, whether ℓ is cross-entropy, squared error, or another loss.

Because this is an unweighted average over all n examples, and 990 of the 1000 examples belong to the majority class, the majority class's errors dominate the sum by sheer count — a mistake on a minority example contributes exactly the same amount to the sum as a mistake on a majority example, but there are 99 times fewer minority examples to make mistakes on, so minority-class errors are a small fraction of the total loss even when the model gets every single minority example wrong. The optimizer, which only "sees" this one aggregate number, therefore has very little gradient pressure pushing it to get minority examples right — it can achieve a near-minimal average loss by nailing the majority class and effectively ignoring the minority class, which is precisely the training-time mirror of the accuracy paradox at evaluation time. Both problems share the same root cause (an unweighted average over an imbalanced population) and, correspondingly, many of the same fixes, covered next.
-->

---
glowSeed: 587
---

# Mitigation Has Tradeoffs

<div class="grid grid-cols-2 gap-4 mt-6">
<div v-click border="2 solid teal-800" bg="teal-800/20" rounded-lg p-4>
<div class="font-bold text-teal-300 mb-2">Class weighting</div>
<div class="text-sm leading-relaxed opacity-90">Multiply minority-example loss contributions (e.g. class_weight="balanced") so the optimizer can no longer ignore them.</div>
</div>
<div v-click border="2 solid blue-800" bg="blue-800/20" rounded-lg p-4>
<div class="font-bold text-blue-300 mb-2">Resampling</div>
<div class="text-sm leading-relaxed opacity-90">Over-sample the minority class or under-sample the majority class before training.</div>
</div>
<div v-click border="2 solid amber-800" bg="amber-800/20" rounded-lg p-4>
<div class="font-bold text-amber-300 mb-2">Threshold tuning</div>
<div class="text-sm leading-relaxed opacity-90">Move the operating point off the default 0.5 to favor recall or precision, using the ROC/PR tradeoff from the metrics deck.</div>
</div>
<div v-click border="2 solid violet-800" bg="violet-800/20" rounded-lg p-4>
<div class="font-bold text-violet-300 mb-2">Metrics</div>
<div class="text-sm leading-relaxed opacity-90">Always report per-class precision, recall, and F1 — never accuracy alone — for an imbalanced problem.</div>
</div>
</div>


<!--
No mitigation here is free, and each one should be chosen deliberately against the real cost of the errors it changes, not applied by default. Class weighting multiplies each example's contribution to the loss by a factor inversely related to its class frequency (scikit-learn's class_weight="balanced" does this automatically), which directly counters the empirical-risk imbalance from the previous slide — but it can make the model more sensitive to noisy or mislabeled minority examples, since those now carry outsized weight too. Resampling — oversampling the minority class (duplicating examples, or synthetically generating new ones with a technique like SMOTE) or undersampling the majority class — changes what the model sees during training; oversampling risks overfitting to duplicated minority examples, and undersampling throws away majority-class information that might otherwise have been useful.

Threshold tuning does not touch training at all — it moves the decision boundary at inference time, trading precision for recall or vice versa along the ROC or precision-recall curve built in the earlier metrics deck; this is often the lowest-risk intervention because it does not change the underlying model, just how its output probabilities get converted to a hard decision. Metrics discipline is the one item on this list that costs nothing and should always be applied: for any imbalanced problem, report per-class precision, recall, and F1 (or the macro/weighted breakdown from the Confusion Matrices deck) rather than a single accuracy or micro-averaged number, because — as shown twice already in this module — those aggregates can look excellent while the minority class fails almost completely. Align whichever mitigation you choose with the real, application-specific cost of a minority-class miss versus a majority-class false alarm.
-->

---
glowSeed: 588
---

# Before You Ship

<div class="grid grid-cols-2 gap-4 mt-6">
<div v-click border="2 solid teal-800" bg="teal-800/20" rounded-lg p-4>
<div class="font-bold text-teal-300 mb-2">Preprocessing</div>
<div class="text-sm leading-relaxed opacity-90">Was every learned transform fit only on training data, inside a Pipeline?</div>
</div>
<div v-click border="2 solid blue-800" bg="blue-800/20" rounded-lg p-4>
<div class="font-bold text-blue-300 mb-2">Availability</div>
<div class="text-sm leading-relaxed opacity-90">Do all features exist, unaltered, at the real moment of prediction?</div>
</div>
<div v-click border="2 solid amber-800" bg="amber-800/20" rounded-lg p-4>
<div class="font-bold text-amber-300 mb-2">Metric</div>
<div class="text-sm leading-relaxed opacity-90">Does the reported metric expose minority-class performance, not just an aggregate?</div>
</div>
<div v-click border="2 solid violet-800" bg="violet-800/20" rounded-lg p-4>
<div class="font-bold text-violet-300 mb-2">Test discipline</div>
<div class="text-sm leading-relaxed opacity-90">Was the test set touched exactly once, after every modeling decision was already fixed?</div>
</div>
</div>


<!--
Turn this deck into a reusable pre-deployment checklist. Preprocessing: confirm every transform with learned parameters — scaler, imputer, feature selector, encoder — was fit exclusively on training data, ideally enforced structurally with a Pipeline rather than by manual discipline alone, since the worked example earlier in this deck showed the leaky version can inflate accuracy by tens of percentage points on data with zero real signal. Availability: for every single feature, ask whether it would exist, in that exact form, at the genuine moment a new prediction is needed — this catches both target-proxy leakage and future-information leakage.

Metric: for any classification problem with meaningful class imbalance, confirm the reported number is not accuracy alone, and that per-class precision/recall/F1 or macro-averaged scores are available to expose minority-class performance specifically. Test discipline: confirm the test set was used exactly once, at the very end, after every hyperparameter, feature, and architecture decision was already locked in using only training and validation data — repeatedly checking test performance while iterating is a slow-motion version of the same leakage this deck opened with, because it lets information from the test set gradually influence modeling decisions. Run this checklist before trusting any of the metrics or significance tests from earlier in the module.
-->

---
glowSeed: 589
---

# Evaluation Can Fail Before the Metric

<div class="mt-8"><div class="grid grid-cols-3 gap-4 mt-6">
<div v-click border="2 solid teal-800" bg="teal-800/20" rounded-lg p-4>
<div class="font-bold text-teal-300 mb-2">Leakage</div>
<div class="text-sm leading-relaxed opacity-90">Breaks information boundaries; can inflate scores by tens of points on pure noise.</div>
</div>
<div v-click border="2 solid blue-800" bg="blue-800/20" rounded-lg p-4>
<div class="font-bold text-blue-300 mb-2">Imbalance</div>
<div class="text-sm leading-relaxed opacity-90">Hides minority failure in aggregate metrics and starves it of training signal.</div>
</div>
<div v-click border="2 solid amber-800" bg="amber-800/20" rounded-lg p-4>
<div class="font-bold text-amber-300 mb-2">Pipelines + per-class metrics</div>
<div class="text-sm leading-relaxed opacity-90">Prevent the two most common evaluation failures structurally.</div>
</div>
</div></div>

<div v-click class="mt-10 text-center text-lg" border="2 solid white/10" bg="white/5" rounded-lg px-6 py-4>Next: ensemble methods combine trees for stronger predictions.</div>

<!--
This deck, and this module, close on the same idea from two different angles: a metric is only as trustworthy as the evaluation that produced it. Data leakage breaks the boundary between what the model is allowed to know and what it actually sees, and the worked demonstration in this deck showed that boundary violation alone can turn a genuinely useless model — literally noise, zero true signal — into one that reports 81% accuracy. Class imbalance is subtler: it does not require any coding mistake, and it distorts both the training objective (the optimizer under-weights minority-class errors because they are numerically rare) and the evaluation (aggregate metrics like accuracy or micro/weighted F1 can look excellent while a rare, important class fails almost completely).

The fix for both is largely structural rather than a matter of vigilance alone: default to Pipelines so preprocessing cannot leak across the train/test boundary, and default to per-class and macro-averaged metrics so imbalance cannot hide inside an aggregate number. This closes the Model Evaluation module: you now have precise metrics, a diagnostic tool for reading exactly how a model fails, a way to test whether one model is genuinely better than another, and the discipline to make sure the whole evaluation is measuring something real in the first place. Next, the course moves from evaluating models to building stronger ones: ensemble methods that combine many decision trees into a single, more accurate predictor.
-->
