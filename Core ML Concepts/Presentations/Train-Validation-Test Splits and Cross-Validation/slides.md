---
theme: default
highlighter: shiki
css: unocss
colorSchema: dark
title: 'Train/Validation/Test Splits and Cross-Validation'
info: |
  ## Train/Validation/Test Splits and Cross-Validation
  How to measure generalization honestly.
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
glowSeed: 241
---

# Train / Validation / Test

### How do we honestly measure performance?

<div class="pt-6 opacity-80 text-lg">Topic 3 of Core ML Concepts</div>

<div class="mt-18 grid grid-cols-[3fr_1fr_1fr] gap-2 text-sm font-bold">
<div class="h-20 rounded-lg bg-teal-500/25 border-2 border-teal-700 flex items-center justify-center">Train · fit parameters</div>
<div class="h-20 rounded-lg bg-blue-500/25 border-2 border-blue-700 flex items-center justify-center">Validation · choose</div>
<div class="h-20 rounded-lg bg-orange-500/25 border-2 border-orange-700 flex items-center justify-center">🔒 Test · report</div>
</div>

<!--
State the core problem plainly before naming the fix: if a model is evaluated using the same data it learned from, the resulting score is systematically, unavoidably too optimistic — this is not a minor caveat, it is close to a logical necessity, since the model was explicitly adjusted to perform well on exactly those points. This deck is a discipline, not a single trick, for separating three distinct jobs that are easy to accidentally blur together: fitting parameters, making modeling decisions (which hyperparameters, which model family), and reporting a final, honest performance number.

Define each of the three bands on the title slide precisely, since these three words get used loosely elsewhere and precisely here. Train: the data used to directly fit a model's parameters — weights, thresholds, split points — via the ERM objective from the Loss Functions deck. Validation: data used to make *decisions* about the model — which hyperparameters, which architecture, when to stop training — without ever updating the model's parameters directly from this data. Test (locked, indicated by the lock icon): data touched exactly once, at the very end, after every single decision has already been made, purely to report an honest final number.

Common misconception to flag immediately, since it will recur throughout the deck: "validation set" and "test set" are not interchangeable synonyms for "held-out data." A validation set can be looked at repeatedly during development — that repeated looking is precisely its job. A test set that gets looked at more than once, or that influences even one modeling decision, has functionally become a second validation set and loses its ability to give an honest final answer. Roadmap for today: establish why training error misleads, fix it with a held-out test set, extend to a validation set for model selection, formalize k-fold cross-validation to reduce the noise of any single split, cover data leakage as the main way this discipline silently breaks, and finish with matching the split strategy to the data's structure (stratified, grouped, or time-aware).
-->

---
glowSeed: 242
---

# Why Training Error Is Not Enough

<div class="grid grid-cols-2 gap-6 mt-4">
<div>
<v-clicks>

- Flexible models can **memorize** noisy training examples
- Training error rewards memorization
- Generalization asks about fresh draws from the population
- Therefore training error is an optimistically biased estimate

</v-clicks>

<div v-click class="mt-5" border="2 solid red-800" bg="red-800/20" rounded-lg p-4>

$$\text{Error}_{train}\not\approx\mathbb E_{(x,y)\sim\mathcal D}[\ell(f_\theta(x),y)]$$

</div>
</div>

<div v-click>
<svg viewBox="0 0 430 300" class="w-full">
  <g fill="#f8fafc"><circle cx="30" cy="210" r="5"/><circle cx="75" cy="105" r="5"/><circle cx="120" cy="145" r="5"/><circle cx="165" cy="55" r="5"/><circle cx="210" cy="125" r="5"/><circle cx="255" cy="70" r="5"/><circle cx="300" cy="180" r="5"/><circle cx="350" cy="135" r="5"/><circle cx="400" cy="225" r="5"/></g>
  <path d="M25 215 C45 255,55 70,75 105 S100 175,120 145 S140 25,165 55 S190 165,210 125 S235 30,255 70 S280 225,300 180 S330 100,350 135 S380 260,405 220" fill="none" stroke="#fb923c" stroke-width="4" />
  <text x="120" y="280" fill="#fb923c" style="font-size: 15px">zero-ish training error ≠ learning</text>
</svg>
</div>
</div>

<!--
Walk through the logical chain in the bullet points, since each step follows from the last. Flexible models (deep trees, high-degree polynomials, large neural networks) have enough parameters to essentially memorize a finite training set — fit each individual point's exact value, including whatever random noise that point happened to contain. Training error, by definition, only measures fit to the exact points a model was trained on, so it rewards this memorization behavior without being able to distinguish "learned the true pattern" from "memorized the specific noisy examples." But generalization — what we actually care about — asks how the model performs on a fresh draw from the population $\mathcal D$, points the model has never seen and whose noise realizations are entirely different. Therefore training error is a biased estimator of true performance, and the bias always runs in the optimistic direction: $\text{Error}_{train}$ systematically underestimates $\mathbb E_{(x,y)\sim\mathcal D}[\ell(f_\theta(x),y)]$, the true risk from the Loss Functions deck.

The formula in the red box states this precisely: training error is *not approximately equal to* true risk — the "not approximately equal" symbol is chosen deliberately over a plain inequality, because the *size* of this gap can be arbitrarily large depending on how flexible the model is relative to how much data it has.

The chart makes this visceral: the orange curve achieves essentially zero training error by weaving through every single noisy point, but that jagged path bears little resemblance to any believable smooth underlying signal — it is chasing individual noise realizations, not recovering a pattern. Ask students directly, before revealing the punchline: "if you evaluated this exact fitted curve on 10 brand-new points from the same process, what error would you expect?" The honest answer is "much worse than zero," and that gap between the reported (training) score and the true (population) performance is the entire subject of this deck. Transition: let's make this concrete with five lines of code that reproduce zero training error on purpose.
-->

---
glowSeed: 243
---

# Memorization in Five Lines

```python {1-2|4-6|8-9|all}
from sklearn.tree import DecisionTreeRegressor
from sklearn.metrics import mean_squared_error
import numpy as np

rng = np.random.default_rng(0)
X = rng.uniform(0, 1, (50, 1))
y = np.sin(2*np.pi*X.ravel()) + rng.normal(scale=.3, size=50)

tree = DecisionTreeRegressor(max_depth=None).fit(X, y)
print(mean_squared_error(y, tree.predict(X)))  # 0.0
```

<div v-click class="mt-7" border="2 solid amber-800" bg="amber-800/20" rounded-lg px-6 py-4 text-lg text-center>
The model has already seen every answer in this “exam.”
</div>

<!--
Run this live if possible; watching the printed `0.0` appear is more convincing than reading it on a slide. Walk through why the number is exactly zero, not just small: `DecisionTreeRegressor(max_depth=None)` is allowed to keep splitting until every leaf contains a single training point, so the tree can carve out a leaf for each of the 50 rows individually and simply return that row's own noisy $y$ value as its prediction. Mean squared error computed against the same data the tree memorized is therefore mechanically zero — this is not a sign the tree found the true sine-wave pattern underneath the noise, it is a sign the tree has enough capacity to store the training set outright.

The line labeled "0.0" should trigger suspicion rather than celebration, and it is worth asking students directly why: real-world targets almost always contain noise (measurement error, unmodeled factors, inherent randomness), so a model that fits the training targets perfectly has necessarily fit that noise too, not just the underlying signal. A score of exactly zero on training data is close to diagnostic of overfitting by itself, precisely because a well-fit-but-honest model should still show a small nonzero training error unless the true relationship truly has zero noise (rare outside toy examples).

The amber callout — "the model has already seen every answer in this exam" — is the plain-language version of the same point: evaluating on training data is like grading a test using the answer key the student copied from during the test itself. It tells you nothing about whether the student (model) actually learned the material (the underlying pattern) versus simply memorized the specific questions (training rows). Transition: the fix is procedural, not algorithmic — hold out data the model never sees during fitting, which is the very next slide.
-->

---
glowSeed: 244
---

# First Fix: Hold Out a Test Set

<div class="mt-7 grid grid-cols-[4fr_1fr] gap-2 text-center font-bold">
<div class="h-28 rounded-l-xl bg-teal-500/25 border-2 border-teal-700 flex flex-col items-center justify-center"><div class="text-2xl">80%</div><div>train</div></div>
<div class="h-28 rounded-r-xl bg-orange-500/25 border-2 border-orange-700 flex flex-col items-center justify-center"><div class="text-2xl">20%</div><div>🔒 test</div></div>
</div>

<div class="grid grid-cols-3 gap-4 mt-8 text-sm">
<div v-click border="2 solid teal-800" bg="teal-800/20" rounded-lg p-4><strong>Fit</strong><div class="opacity-75 mt-2">Only training examples update model parameters</div></div>
<div v-click border="2 solid blue-800" bg="blue-800/20" rounded-lg p-4><strong>Shuffle wisely</strong><div class="opacity-75 mt-2">Randomize unless order or groups matter</div></div>
<div v-click border="2 solid orange-800" bg="orange-800/20" rounded-lg p-4><strong>Unlock once</strong><div class="opacity-75 mt-2">Final evaluation after all choices are fixed</div></div>
</div>

```python
X_train, X_test, y_train, y_test = train_test_split(
    X, y, test_size=.2, random_state=42
)
```

<!--
The fix for the previous slide's memorization problem is procedural rather than algorithmic: set aside a chunk of the data before any fitting happens, and never let the model's parameters be updated from it. The three cards name the three rules that make this work in practice. "Fit" — only the training rows are allowed to influence the parameters the model learns (its weights, thresholds, split points); the test rows must never appear in a `.fit()` call. "Shuffle wisely" — a plain random shuffle before splitting is the default, but it is only correct when rows are independent and identically distributed; later slides (Data Leakage, The Split Must Match the Data) cover the cases — grouped data, time series — where naive shuffling itself introduces leakage. "Unlock once" — the test set should be evaluated a single time, at the very end, after every modeling decision (which features, which model family, which hyperparameters) has already been finalized using only the training data.

Common ratios include 70/30, 80/20, and 90/10, and the right choice depends mostly on dataset size: with only a few hundred rows, a 20% test set may be too small to give a stable estimate, while with millions of rows even a 1% test set is often plenty. Emphasize that the specific ratio is a minor tuning knob — the rule that actually matters is that the test set stays completely unseen by both the model-fitting process and the human making tuning decisions. The code snippet's `random_state=42` is worth flagging explicitly: fixing the random seed makes the split reproducible across runs, which matters for debugging and for fair comparison between different models trained on "the same" split.

This single train/test split answers "did the model memorize?" but not yet "which model or which hyperparameter should we use?" — because the test set is locked and cannot be repeatedly consulted for that kind of iteration. Transition: the next slide introduces a third band, the validation set, specifically to support that iterative decision-making without touching the locked test set.
-->

---
glowSeed: 245
---

# But How Do We Choose a Model?

<div class="mt-5 grid grid-cols-[3fr_1fr_1fr] gap-2 text-center font-bold">
<div class="h-24 rounded-l-xl bg-teal-500/25 border-2 border-teal-700 flex flex-col items-center justify-center"><div class="text-2xl">60%</div><div>train</div></div>
<div class="h-24 bg-blue-500/25 border-2 border-blue-700 flex flex-col items-center justify-center"><div class="text-2xl">20%</div><div>validation ↻</div></div>
<div class="h-24 rounded-r-xl bg-orange-500/25 border-2 border-orange-700 flex flex-col items-center justify-center"><div class="text-2xl">20%</div><div>🔒 test</div></div>
</div>

<div class="grid grid-cols-3 gap-4 mt-8">
<div v-click border="2 solid teal-800" bg="teal-800/20" rounded-lg p-4><div class="text-2xl font-bold text-teal-300">Parameters</div><div class="text-sm mt-2">learned from training data</div><div class="text-xs opacity-70 mt-3">weights, thresholds</div></div>
<div v-click border="2 solid blue-800" bg="blue-800/20" rounded-lg p-4><div class="text-2xl font-bold text-blue-300">Hyperparameters</div><div class="text-sm mt-2">chosen using validation</div><div class="text-xs opacity-70 mt-3">depth, λ, degree</div></div>
<div v-click border="2 solid orange-800" bg="orange-800/20" rounded-lg p-4><div class="text-2xl font-bold text-orange-300">Report</div><div class="text-sm mt-2">one final test score</div><div class="text-xs opacity-70 mt-3">after choices are locked</div></div>
</div>

<!--
This slide answers the question left open by the two-way split: how do we choose among candidate models or hyperparameter settings without ever touching the locked test set? The answer is a third band, the validation set, carved out of the original data alongside train and test. The three cards map each band to a distinct kind of decision: parameters (weights, split thresholds — the numbers a training algorithm directly optimizes, covered by the ERM objective from the Loss Functions deck) are learned from training data only; hyperparameters (tree depth, regularization strength λ, polynomial degree — settings chosen by a human or a search procedure, not learned by gradient descent or its equivalent) are chosen by comparing performance across candidates on the validation set; and the final report is a single test-set score computed once every other decision is already locked in.

Validation data supports genuine iteration in a way the test set cannot: fit model A, check its validation score, fit model B, compare, adjust a hyperparameter, refit, recheck — repeating this loop as many times as useful, because the validation set's whole purpose is to be looked at repeatedly during development. This is the precise distinction between validation and test that the title slide flagged as a common point of confusion: a test set that gets consulted more than once, or that influences even a single modeling choice, has functionally become a second validation set, and any "final" score computed from it is no longer an honest estimate of generalization — it has been implicitly tuned to, the same way training error was implicitly tuned to on the "Memorization" slide.

The practical takeaway to state explicitly: if you ever catch yourself going back to tweak a hyperparameter *because* the test score changed, that is the leakage this whole framework exists to prevent. Transition: the next slide shows the actual scikit-learn code for building this three-way split correctly.
-->

---
glowSeed: 246
---

# Build the Three-Way Split

```python {1|3-4|6-7|9|all}
from sklearn.model_selection import train_test_split

# Lock away 20% first
X_pool, X_test, y_pool, y_test = train_test_split(
    X, y, test_size=.20, random_state=42
)

# 25% of the remaining 80% is 20% of the original
X_train, X_val, y_train, y_val = train_test_split(
    X_pool, y_pool, test_size=.25, random_state=42
)

print(len(X_train), len(X_val), len(X_test))  # 60 / 20 / 20
```

<div v-click class="mt-5 grid grid-cols-3 gap-4 text-center text-sm">
<div border="2 solid teal-800" bg="teal-800/20" rounded-lg p-3>fit many times</div>
<div border="2 solid blue-800" bg="blue-800/20" rounded-lg p-3>inspect many times</div>
<div border="2 solid orange-800" bg="orange-800/20" rounded-lg p-3>inspect once</div>
</div>

<!--
This slide is the mechanical "how" behind the previous slide's three-way split. The key idea, easy to get wrong: `train_test_split` only ever splits whatever data you hand it into two pieces, so a three-way split requires calling it twice. First call: split off the test set from the full dataset (`test_size=.20` takes 20% of the original data and locks it away as `X_test`/`y_test`, leaving `X_pool`/`y_pool` holding the remaining 80%). Second call: split that 80% pool again into training and validation.

Walk through the arithmetic explicitly, since it is the single most common ratio mistake students make: `test_size=.25` in the second call takes 25% of the *pool*, not 25% of the original dataset. The pool is already only 80% of the original, so 25% of 80% is 0.25 × 0.80 = 0.20, i.e. 20% of the original data — matching the "60/20/20" comment in the code. A student who wants a clean 60/20/20 split and naively uses `test_size=.20` on the second call (reasoning "I want 20% for validation") would actually get 0.20 × 0.80 = 16% of the original data for validation and end up with 64% for training — a subtly wrong split that silently changes the experiment's effective ratios. The general formula worth writing on the board: if you want fractions $(p_{train}, p_{val}, p_{test})$ of the original data with $p_{train}+p_{val}+p_{test}=1$, the second call's `test_size` should be $p_{val}/(p_{train}+p_{val})$, i.e. the validation fraction relative to what remains after removing the test set.

The three labels under the code — "fit many times," "inspect many times," "inspect once" — summarize each band's access pattern in one phrase and are worth repeating verbatim, since they are the operational definition of train/validation/test that will recur for the rest of the deck. Transition: this static three-way split still throws away information (the validation set is never used for training) and is sensitive to exactly which rows happened to land in which band — but before addressing that, the next slide covers a different failure mode: how the split itself can silently leak information across boundaries.
-->

---
glowSeed: 247
---

# The Hidden Enemy: Data Leakage

<div class="grid grid-cols-2 gap-6 mt-5">
<div v-click class="rounded-lg overflow-hidden border-2 border-red-800 bg-red-800/20">
<div class="bg-red-800/40 px-5 py-3 font-bold">❌ Leaky workflow</div>
<div class="px-5 py-4 text-sm">
Normalize all rows, select features using all labels, then split.
<div class="mt-4 font-bold text-red-200">Test information influenced training.</div>
</div>
</div>
<div v-click class="rounded-lg overflow-hidden border-2 border-teal-800 bg-teal-800/20">
<div class="bg-teal-800/40 px-5 py-3 font-bold">✓ Safe workflow</div>
<div class="px-5 py-4 text-sm">
Split first; fit preprocessing on training folds only; transform held-out rows.
<div class="mt-4 font-bold text-teal-200">Use a pipeline to enforce the boundary.</div>
</div>
</div>
</div>

```python {1|3-6|all}
from sklearn.pipeline import make_pipeline
from sklearn.preprocessing import StandardScaler
from sklearn.linear_model import Ridge

model = make_pipeline(StandardScaler(), Ridge(alpha=1.0))
model.fit(X_train, y_train)  # scaler sees training rows only
```

<div v-click class="mt-4 text-center text-sm opacity-80">Split by patient, user, device, or time when rows are not independent.</div>

<!--
Data leakage is the failure mode this entire deck exists to prevent, and it is worth stating plainly: leakage means information from outside the training data — most dangerously, information derived from the test set — influences the model or the modeling decisions, silently inflating the reported performance so it no longer reflects true generalization. The leaky workflow on the left is a common, easy-to-miss mistake: computing a `StandardScaler`'s mean and standard deviation (or selecting features by correlation with the label) using *all* rows, including the ones that will later become the test set, before splitting. Even though the model itself never sees the test labels directly, the scaler's mean/variance were computed partly from test rows, so the transformed training data already carries a small amount of test-set information baked into it — this is leakage even though it looks harmless.

The safe workflow flips the order: split first, then fit any preprocessing step (scaling, imputation, feature selection) using only the training partition, and apply that already-fitted transformation to the held-out rows without refitting it on them. The code example shows why `Pipeline` is the practical tool for enforcing this discipline automatically: `make_pipeline(StandardScaler(), Ridge(alpha=1.0))` bundles the scaler and the model into one object, and calling `.fit(X_train, y_train)` guarantees the scaler's statistics are computed from `X_train` alone — the pipeline makes it structurally impossible to accidentally fit the scaler on test rows. This matters even more under cross-validation (next slides): without a pipeline, a scaler fit once on the whole training pool before the CV loop would leak information across folds, since each fold's "held-out" portion would have already influenced the scaler that transforms it.

The closing line — "split by patient, user, device, or time when rows are not independent" — previews a second leakage channel covered later ("The Split Must Match the Data"): even a leakage-free preprocessing pipeline can still leak if a random shuffle puts two rows from the same patient into different folds, since the model can partly "recognize" that patient rather than generalize to new ones. Transition: leakage aside, a single validation split has its own weakness — it depends on which specific rows happened to land in which partition, which the next slide quantifies.
-->

---
glowSeed: 248
---

# One Validation Split Is Noisy

<div class="grid grid-cols-2 gap-8 mt-7 items-center">
<div>
<div v-click border="2 solid blue-800" bg="blue-800/20" rounded-lg p-5 mb-4>
<div class="text-sm opacity-70">random_state = 7</div>
<div class="text-4xl font-bold text-blue-300 mt-2">MSE = 0.14</div>
</div>
<div v-click border="2 solid violet-800" bg="violet-800/20" rounded-lg p-5>
<div class="text-sm opacity-70">random_state = 19</div>
<div class="text-4xl font-bold text-violet-300 mt-2">MSE = 0.19</div>
</div>
</div>

<div>
<v-clicks>

- Same model, same dataset
- Only the random partition changed
- Small validation sets produce high-variance estimates
- Holding out data also leaves less for fitting
- Average several splits to stabilize the estimate

</v-clicks>
</div>
</div>

<div v-click class="mt-8 text-center text-xl">Solution: <strong>k-fold cross-validation</strong></div>

<!--
This slide's whole point is a subtle but important idea: a validation score is itself an *estimate*, computed from a finite, randomly chosen sample of rows, and like any estimate it has variance — it would come out differently if a different random partition had been drawn. The two cards make this concrete rather than abstract: the exact same model fit on the exact same dataset gives MSE = 0.14 under one random partition (`random_state=7`) and MSE = 0.19 under a different partition (`random_state=19`) of the same data. Nothing about the model or the data changed between these two numbers — only which specific rows happened to land in the validation fold changed, and that alone moved the score by more than 30%.

Two forces drive this variance, both worth naming explicitly. First, small validation sets produce high-variance estimates for the same reason any statistic computed from a small sample is noisy: a validation set of 20 rows might happen to contain a few unusually easy or unusually hard examples purely by chance, and that luck shows up directly in the score. Second, there is a real tradeoff bound up in the split ratio itself: making the validation set larger to reduce this noise means making the training set smaller, which typically makes the fitted model itself worse (less data to learn from) — so you cannot fix the variance problem by simply growing the validation set indefinitely without cost.

The listed fix — average several splits to stabilize the estimate — is the entire idea behind k-fold cross-validation, introduced on the next slide: instead of relying on the luck of one particular train/validation partition, systematically create several different partitions, evaluate on each, and average the results. This directly reduces the variance of the final estimate (by the same averaging-reduces-variance logic covered in the Bagging deck) while still using every row for both training and validation across the different folds, rather than permanently sacrificing a chunk of data to a single validation split. Transition: the next slide shows exactly how the folds are constructed.
-->

---
glowSeed: 249
---

# Five-Fold Cross-Validation

<div class="grid grid-cols-[5rem_repeat(5,1fr)] gap-1.5 mt-3 text-center text-sm">
<div></div><div class="opacity-60">Fold 1</div><div class="opacity-60">Fold 2</div><div class="opacity-60">Fold 3</div><div class="opacity-60">Fold 4</div><div class="opacity-60">Fold 5</div>
<template v-for="row in 5" :key="row">
  <div class="py-1.5 font-bold">Fit {{ row }}</div>
  <div v-for="col in 5" :key="col" class="py-1.5 rounded" :class="row === col ? 'bg-orange-500/35 border-2 border-orange-600' : 'bg-teal-500/20 border-2 border-teal-800'">{{ row === col ? 'validate' : 'train' }}</div>
</template>
</div>

<div v-click class="mt-3" border="2 solid white/5" bg="white/5" rounded-lg py-1.5 px-3>

$\displaystyle \text{CV error}=\frac{1}{k}\sum_{i=1}^{k}\text{Error}_i$

</div>

<div v-click class="mt-2 text-center text-sm opacity-75">
Worked example, $k=5$, ridge regression: fold errors $[0.0176,\,0.0163,\,0.0144,\,0.0199,\,0.0161]$ → $\text{CV error}=\frac{0.0176+0.0163+0.0144+0.0199+0.0161}{5}\approx0.0169$
</div>

<div v-click class="mt-2 text-center text-sm opacity-80">Every row is validated once and used for training k − 1 times.</div>

<!--
Walk through the grid row by row: the data is first split into $k=5$ roughly equal-sized folds, and the procedure is run $k$ times ("Fit 1" through "Fit 5"). On each run, one fold (orange, "validate") is held out and the remaining $k-1$ folds (teal, "train") are used to fit the model; over the five runs, the orange fold rotates through every position, so every single example is used for validation exactly once and for training exactly $k-1=4$ times. This is the mechanism that both reduces variance (five different validation estimates get averaged instead of relying on one) and uses data efficiently (every row eventually contributes to both roles, unlike a static validation split where the validation rows are never used for training at all).

The formula $\text{CV error}=\frac{1}{k}\sum_{i=1}^{k}\text{Error}_i$ is exactly "average the five per-fold errors," and the worked example makes it concrete: five ridge-regression fold errors $[0.0176, 0.0163, 0.0144, 0.0199, 0.0161]$ sum to $0.0843$, and dividing by $k=5$ gives $\text{CV error}\approx0.0169$. Point out that this single averaged number is more trustworthy than any one of the five individual fold errors, and that the *spread* across the five values (roughly 0.0144 to 0.0199 here) is itself informative — a large spread signals a validation estimate that would have been noisy if only one fold had been used, echoing the point from the previous slide.

Five or ten folds are the most common defaults in practice: five folds is a reasonable balance of computational cost (the model must be refit $k$ times) against variance reduction, while ten folds gives a slightly more stable estimate at roughly double the compute. The extreme case, leave-one-out cross-validation ($k=n$, one fold per data point), is worth mentioning as existing but rarely used outside very small datasets, since it is computationally expensive and its per-fold estimates are highly correlated with each other. Transition: the next slide shows how little code this actually takes in scikit-learn.
-->

---
glowSeed: 250
---

# Cross-Validation in scikit-learn

```python {1-2|4-5|7-9|all}
from sklearn.model_selection import cross_val_score
from sklearn.linear_model import Ridge

X = rng.uniform(0, 1, (100, 3))
y = X @ np.array([1., -2., .5]) + rng.normal(scale=.1, size=100)

scores = cross_val_score(
    Ridge(alpha=1.0), X, y, cv=5,
    scoring='neg_mean_squared_error'
)

print(-scores)          # five held-out errors
print(-scores.mean())   # central estimate
print(scores.std())     # stability across folds
```

<div v-click class="mt-4" border="2 solid amber-800" bg="amber-800/20" rounded-lg px-5 py-3 text-center>
A large fold-to-fold spread is useful diagnostic information—not noise to hide.
</div>

<!--
`cross_val_score` automates exactly the five-fold procedure from the previous slide: pass it an unfitted model, the full feature matrix and labels, `cv=5`, and a scoring string, and it internally performs the fold rotation, fits the model five times, and returns an array of five per-fold scores. The `scoring='neg_mean_squared_error'` argument deserves a direct explanation, since the negative sign trips students up every time: scikit-learn's scoring API is designed so that for every metric, "higher returned value is always better," which lets the same generic machinery (grid search, cross-validation utilities) compare and rank models consistently regardless of whether the underlying metric is naturally "lower is better" (like MSE) or "higher is better" (like accuracy or $R^2$). Since MSE is naturally lower-is-better, scikit-learn negates it internally so that a smaller true MSE becomes a *larger* (less negative) score — `-scores` in the code simply flips the sign back to get interpretable, readable MSE values.

The three print statements build up the full picture a practitioner should report: `-scores` shows the five individual held-out errors (useful for spotting one anomalous fold); `-scores.mean()` gives the central estimate, the same averaging computed by hand on the previous slide; and `scores.std()` gives the spread across folds, which is a direct measurement of how much the score would plausibly change under a different random partition — the exact variance problem the "One Validation Split Is Noisy" slide raised, now quantified rather than just demonstrated with two examples.

The amber callout — a large fold-to-fold spread is useful diagnostic information, not noise to hide — is worth dwelling on: a high standard deviation across folds can indicate the dataset is small relative to model complexity, that certain folds contain unusually hard or easy subsets (which, combined with the next slide's stratified/grouped/time-aware splitting, might mean the folds themselves are not comparable), or that the model's performance is fundamentally unstable. Reporting only the mean and hiding the spread would misrepresent how confident anyone should be in that mean. Transition: cross-validation as shown here assumes a plain random shuffle is a valid way to build folds — the next slide covers when that assumption breaks.
-->

---
glowSeed: 251
---

# The Split Must Match the Data

<div class="grid grid-cols-3 gap-4 mt-5">
<div v-click border="2 solid teal-800" bg="teal-800/20" rounded-lg p-5>
<div class="text-2xl">⚖️</div><div class="font-bold mt-2">Stratified</div>
<div class="text-sm opacity-80 mt-3">Preserve class proportions, especially for imbalanced classification.</div>
</div>
<div v-click border="2 solid blue-800" bg="blue-800/20" rounded-lg p-5>
<div class="text-2xl">👥</div><div class="font-bold mt-2">Grouped</div>
<div class="text-sm opacity-80 mt-3">Keep every row from one patient or user in the same fold.</div>
</div>
<div v-click border="2 solid orange-800" bg="orange-800/20" rounded-lg p-5>
<div class="text-2xl">🕒</div><div class="font-bold mt-2">Time-aware</div>
<div class="text-sm opacity-80 mt-3">Train on the past and validate on the future. Never shuffle time.</div>
</div>
</div>

<div v-click class="mt-7">
<svg viewBox="0 0 800 160" class="w-full">
  <g style="font-size: 13px" text-anchor="middle"><rect x="40" y="30" width="220" height="35" rx="6" fill="#0f766e88"/><text x="150" y="52" fill="white">train: oldest observations</text><rect x="270" y="30" width="80" height="35" rx="6" fill="#ea580c88"/><text x="310" y="52" fill="white">val</text><rect x="40" y="78" width="360" height="35" rx="6" fill="#0f766e88"/><text x="220" y="100" fill="white">train window expands</text><rect x="410" y="78" width="80" height="35" rx="6" fill="#ea580c88"/><text x="450" y="100" fill="white">val</text><rect x="40" y="126" width="500" height="24" rx="6" fill="#0f766e88"/><rect x="550" y="126" width="80" height="24" rx="6" fill="#ea580c88"/></g>
</svg>
</div>

<!--
Every splitting technique shown so far implicitly assumed rows can be shuffled freely and independently — that assumption fails in three common real-world situations, each needing a different splitter. Stratified splitting addresses class imbalance: if a classification dataset is 95% negative and 5% positive, a plain random split could by bad luck put almost none of the rare positive class into the validation fold, making the validation score meaningless; `StratifiedKFold` instead guarantees each fold preserves (approximately) the same class proportions as the full dataset. Grouped splitting addresses shared identity: if a dataset contains multiple rows per patient, user, or device, a random split can put some of one patient's rows in training and others in validation — the model can then partly "recognize" that specific patient's characteristics rather than learning to generalize to genuinely new patients, silently inflating the validation score; `GroupKFold` instead guarantees every row belonging to one group stays entirely within one fold. Time-aware splitting addresses temporal order: for time-series data, a random split can put future rows in training and past rows in validation, letting the model implicitly "see the future" — `TimeSeriesSplit` instead always trains on a window of past data and validates on a subsequent, later window, mirroring how the model will actually be used in deployment (predicting forward from the past).

The SVG makes the time-aware case concrete: the training window expands forward through time while the validation window always sits just ahead of it, and the diagram's final expanded bar shows the pattern extending toward the full dataset — never shuffled, always ordered. Emphasize the diagnostic question to ask before picking any splitter: does this dataset have a natural order (time) or a shared identity (patient, user, device, session) that a naive random shuffle would violate? If the answer is yes to either, plain `KFold` or `train_test_split` risks silently leaking information across the train/validation boundary in exactly the same spirit as the preprocessing leakage covered earlier — the leak is structural, not a coding mistake, so it will not show up as an error, only as an optimistic score that fails to hold up once the model is deployed.

Transition: with the right splitter chosen and leakage-safe preprocessing in place, the final slide assembles every piece covered today into one end-to-end model-selection workflow.
-->

---
glowSeed: 252
---

# A Full Model-Selection Workflow

<div class="flex items-center gap-2 mt-9 text-sm text-center">
<div v-click class="flex-1 p-4 rounded-lg bg-white/5 border-2 border-white/10"><strong>Full data</strong></div>
<div class="text-2xl">→</div>
<div v-click class="flex-1 p-4 rounded-lg bg-orange-500/20 border-2 border-orange-700"><strong>Lock test</strong></div>
<div class="text-2xl">+</div>
<div v-click class="flex-[2] p-4 rounded-lg bg-teal-500/20 border-2 border-teal-700"><strong>CV on train pool</strong><br><span class="opacity-70">compare + tune</span></div>
<div class="text-2xl">→</div>
<div v-click class="flex-1 p-4 rounded-lg bg-blue-500/20 border-2 border-blue-700"><strong>Refit winner</strong></div>
<div class="text-2xl">→</div>
<div v-click class="flex-1 p-4 rounded-lg bg-orange-500/20 border-2 border-orange-700"><strong>Test once</strong></div>
</div>

```python {1-2|4-5|7-11|13-14|all}
from sklearn.model_selection import train_test_split, GridSearchCV
from sklearn.linear_model import Ridge

X_train, X_test, y_train, y_test = train_test_split(
    X, y, test_size=.2, random_state=0
)

search = GridSearchCV(
    Ridge(), {'alpha': [.01, .1, 1., 10.]},
    cv=5, scoring='neg_mean_squared_error'
)
search.fit(X_train, y_train)

print(search.best_params_)
print(search.score(X_test, y_test))  # exactly once
```

<!--
This slide assembles every idea from the deck into one concrete, correct workflow, and the diagram's five stages map directly onto the code below it. "Lock test" is the single `train_test_split` call, executed first and exactly once — everything to its right in the diagram operates only on `X_train`/`y_train`. "CV on train pool" is where `GridSearchCV` does its work: for each candidate hyperparameter setting in the grid (here, four candidate values of `alpha`), it runs full 5-fold cross-validation using only the training pool, producing a mean CV score per candidate — this is precisely the "compare model A with model B, tune a hyperparameter, repeat" iteration the validation-set slide described, now automated and using cross-validation's more stable estimate instead of a single validation split.

After comparing all candidates by their CV scores, `GridSearchCV` performs one more step worth calling out explicitly since it's easy to miss: it automatically refits the best-scoring configuration on the *entire* training pool (all of `X_train`, not just 4/5 of it as used during any individual CV fold) — this "Refit winner" stage recovers the data that had to be held out during cross-validation, so the final model benefits from every training row before ever touching the test set. Finally, `search.score(X_test, y_test)` computes the test score exactly once, after every hyperparameter decision has already been made and locked; the comment "exactly once" is not decorative, it is the rule the entire deck has been building toward.

Emphasize the fatal mistake this workflow prevents: if a student ran `search.score(X_test, y_test)`, didn't like the number, and went back to add more candidate values to the `alpha` grid, that second look at the test score has already violated the "touched once" rule — the test set has become, in effect, another validation set, and any number reported after that point is no longer an honest estimate of generalization. Transition: the final slide converts this discipline into a checklist a practitioner can run through before trusting any reported score.
-->

---
glowSeed: 253
---

# Before You Trust a Score

<v-clicks>
<div border="2 solid white/5" bg="white/5" rounded-lg flex items-center gap-4 px-5 py-3 mb-3><div class="text-2xl text-teal-300">✓</div><div>Test set was separated before exploration and tuning</div></div>
<div border="2 solid white/5" bg="white/5" rounded-lg flex items-center gap-4 px-5 py-3 mb-3><div class="text-2xl text-teal-300">✓</div><div>Preprocessing was fit inside the training folds</div></div>
<div border="2 solid white/5" bg="white/5" rounded-lg flex items-center gap-4 px-5 py-3 mb-3><div class="text-2xl text-teal-300">✓</div><div>Splitter respects classes, groups, and time order</div></div>
<div border="2 solid white/5" bg="white/5" rounded-lg flex items-center gap-4 px-5 py-3 mb-3><div class="text-2xl text-teal-300">✓</div><div>Hyperparameters were chosen by validation or CV</div></div>
<div border="2 solid white/5" bg="white/5" rounded-lg flex items-center gap-4 px-5 py-3><div class="text-2xl text-teal-300">✓</div><div>Test data was touched once, after decisions were locked</div></div>
</v-clicks>

<div v-click class="mt-7 text-xl text-center">Next: <strong>Overfitting and Regularization</strong></div>

<!--
This checklist is the deck's core deliverable — a concrete, five-item audit any student can run against their own project before trusting a reported number, and each item maps directly back to a slide already covered. "Test set was separated before exploration and tuning" reprises the two-way split and the danger of peeking. "Preprocessing was fit inside the training folds" reprises the Data Leakage slide's pipeline discipline. "Splitter respects classes, groups, and time order" reprises stratified/grouped/time-aware splitting. "Hyperparameters were chosen by validation or CV" reprises the three-way split and the GridSearchCV workflow. "Test data was touched once, after decisions were locked" reprises the discipline the entire deck has repeated in different forms — it is worth pointing out to students that this same rule appeared four times across the deck in different guises, because it is the single idea everything else serves.

Frame the deck's overall achievement plainly: we started by showing that training error is a systematically optimistic, essentially untrustworthy measure of generalization (the "Memorization" slide), and we have now built up a complete, leakage-resistant procedure — hold out a locked test set, use validation or cross-validation for every iterative decision, match the splitter to the data's actual structure — for measuring performance honestly instead. This checklist is exactly the tool that lets us trust the training–validation gap enough to *diagnose* a model's behavior, which is the explicit bridge to the next deck.

Transition: knowing how to measure the gap between training and validation performance honestly is a prerequisite for the next deck's actual subject — Overfitting and Regularization — which asks what to do when that gap is large (the model overfits) and shows techniques (L1/L2 penalties, early stopping) for deliberately shrinking it back down.
-->
