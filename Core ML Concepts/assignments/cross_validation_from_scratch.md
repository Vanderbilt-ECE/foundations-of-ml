# Assignment: Cross-Validation and Honest Model Selection, From Scratch

**Unit:** Core ML Concepts
**Decks this builds on:** *Train/Validation/Test Splits and Cross-Validation*, *Bias–Variance Tradeoff*
**Reference solution:** `cross_validation_from_scratch/` (run with `uv run solution.py`)

## Why this assignment

A validation score is itself an estimate computed from a finite, randomly chosen
set of rows. Like any estimate it has variance — it would come out differently
under a different random split. This assignment makes you feel that variance,
then build the machinery (k-fold cross-validation, leakage-safe pipelines, the
right splitter for the data) that gets an honest number out anyway.

By the end you should be able to say, from code you wrote:

- how much a reported score moves when only the random split changes;
- why averaging folds stabilizes the estimate, and *which* quantity actually
  shrinks (it is not the spread across folds);
- why data leakage produces an optimistic score with no error message;
- the difference between a hyperparameter and a parameter, and why the test set
  gets touched exactly once.

Implement `train_test_split`, the k-fold index logic, and `cross_val_score`
yourself. You may use `scikit-learn` for the *models* (`Ridge`, `LinearRegression`)
and for the planted-leak preprocessing objects in Part 3.

---

## Part 1 — One split is noisy

Use a 1-D dataset of about 100 points with a smooth non-linear truth plus noise
(e.g. `y = sin(1.5πx) + noise`).

1. Implement `train_test_split(X, y, test_frac, seed)` from scratch (shuffle the
   indices, slice them).
2. Fix one model (say a degree-4 polynomial). For 200 different seeds, split, fit
   on train, record mean squared error on the held-out part.
3. Plot a histogram of the 200 held-out errors. Report the mean and the standard
   deviation, and state how large the spread is *relative to* the mean.

---

## Part 2 — k-fold cross-validation from scratch

1. Implement `kfold_indices(n, k)` returning `k` disjoint arrays of row indices
   whose union is `0..n-1`. No `sklearn.model_selection`.
2. Implement `cross_val_score(make_model, X, y, k)` that fits `k` times, each time
   holding out one fold, and returns the `k` fold errors.
3. **Worked example.** With `k = 5` and a ridge model, print the 5 fold errors and
   their average, in the same style as the deck's worked example.
4. **What actually stabilizes.** Be careful here — the spread of errors *across
   folds* does **not** shrink as `k` grows; with more folds each fold is smaller
   and therefore noisier, and at `k = n` (leave-one-out) each "fold error" is a
   single squared residual. What shrinks is the variance of the **cross-validation
   estimate itself** across different random partitions of the data.

   Demonstrate this: for `k` in `{2, 5, 10, n}`, repeat the whole k-fold procedure
   for 100 different random shuffles of the data, record the CV mean each time, and
   plot `std(CV means)` against `k`. This should decrease.

   Separately, report the fold-to-fold spread for each `k` and note that it moves
   the *other* way. Explain in one sentence why. (The deck's "a large fold-to-fold
   spread is useful diagnostic information" callout is the hint.)
5. **Bias–variance callback.** Sweep polynomial degree 1–12. For each degree,
   compute the 5-fold CV error. Plot CV error vs degree and mark the minimum — you
   should recover the U-shaped curve from the Bias–Variance deck, but now measured
   with cross-validation instead of a single held-out set.

---

## Part 3 — The leakage lab

You are given (in the solution, and you will rebuild it) a script that reports a
suspiciously high score. It contains three planted leaks. The dataset has ~100
rows and a large number of **pure-noise** feature columns in addition to a few
real ones.

The three leaks:

1. **Feature scaling fit on the full dataset** before the train/test split.
2. **Feature selection (`SelectKBest`) run on all rows**, using `y`, before the
   split.
3. **Target-derived imputation:** a feature column has missing entries that
   someone "filled in" using the target column `y` (a real and common bug —
   `df[col].fillna(df[target])` and friends).

For each leak:

- explain the mechanism by which it lets information from the held-out rows reach
  the model;
- fix it by moving that step *inside* the cross-validation loop (fit the
  transformer on the training fold only, then apply it to the validation fold);
- report the CV score before and after the fix.

Note which leak barely moves the score and which ones move it a lot. A leak that
costs you almost nothing on this dataset is **still a leak** — be ready to explain
why it is wrong to do even when it looks harmless.

---

## Part 4 — The split must match the data

1. **Grouped data.** Build a dataset with 20 "patients", 5 rows each. Give each
   patient a random per-patient offset that shows up in the features (so rows from
   the same patient look nearly identical). Show that plain k-fold gives an
   inflated score because the model recognizes individual patients, and that a
   group-aware split (every patient entirely in one fold) gives a realistic score.
2. **Time-ordered data.** Build a series with a trend plus seasonality. Show that
   shuffled k-fold lets the model "see the future" and inflates the score, and that
   a forward-chaining split (train on the past, validate on the next block) gives a
   realistic one.

For each: one sentence naming what real-world deployment the naive split secretly
assumes.

---

## Part 5 — The full model-selection workflow

Assemble the deck's end-to-end picture by hand:

1. Split off a test set once and set it aside.
2. On the training pool only, grid-search the ridge penalty `α` over a few values
   using your own `cross_val_score`.
3. Refit the best `α` on the entire training pool.
4. Score the test set **exactly once** and report that number.

Then demonstrate the failure mode in a comment or printout: "look at the test
score, dislike it, widen the `α` grid, score again." Explain why every number
reported after that first peek is no longer an honest estimate of generalization.

---

## What to submit

```
cross_validation_from_scratch/
  solution.py        # single script, run with: uv run solution.py
  README.md          # "What to expect" section with YOUR run's numbers
  *.html / *.png     # histogram (Part 1), std-vs-k and U-curve (Part 2),
                     #   leak comparison (Part 3), grouped/time comparison (Part 4)
```

Also complete the deck's **"Before You Trust a Score"** checklist against your
Part 5 run and include it in the README:

- [ ] Test set separated before any exploration or tuning
- [ ] Preprocessing fit inside the training folds only
- [ ] Splitter respects classes, groups, and time order
- [ ] Hyperparameters chosen by validation / CV, never on the test set
- [ ] Test set touched once, after all decisions were locked

## Grading

| Criterion | Weight |
|---|---|
| Correct from-scratch split, k-fold, and `cross_val_score` | 35% |
| Part 2 measures the *right* quantity (variance of the CV estimate) | 15% |
| Leakage fixes are correct (transformer fit on training fold only) | 25% |
| Written explanations describe the *mechanism* | 15% |
| Code runs cleanly via `uv run` and is readable | 10% |
