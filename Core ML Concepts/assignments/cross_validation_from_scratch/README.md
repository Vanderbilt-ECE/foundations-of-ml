# Cross-Validation From Scratch — Reference Solution

Single script. Run with:

```
uv run solution.py
```

First run builds the environment automatically. The script prints tables for all
five parts and writes five figures:

| file | part | shows |
|------|------|-------|
| `part1_split_histogram.html` | 1 | 200 held-out MSE scores for one model on one dataset |
| `part2_stability_vs_k.html` | 2 | std of the CV estimate (shrinks with `k`) vs fold-to-fold spread (grows) |
| `part2_cv_ucurve.html` | 2 | 5-fold CV error vs polynomial degree |
| `part3_leakage.html` | 3 | CV error dropping as each data leak is added |
| `part4_splitters.html` | 4 | naive vs group-aware / time-aware splits |

## What to expect (numbers from a clean run)

### Part 1 — one split is noisy

Degree-4 polynomial, 200 different 75/25 splits of the *same* 100 points:

```
held-out MSE  mean = 0.0395   std = 0.0084   min = 0.0199   max = 0.0644
```

The standard deviation is ~21% of the mean. Nothing changed but the split seed.

### Part 2 — k-fold

Worked example, `k = 5`, ridge on degree-4 features:

```
fold errors = [0.1396, 0.1424, 0.1370, 0.1267, 0.1233]
CV error (their average) = 0.1338
```

**What stabilises** (100 random partitions per `k`):

```
   k   std(CV means)    avg fold-to-fold std
   2       0.00804              0.01342
   5       0.00288              0.02906
  10       0.00185              0.04449
 100       0.00000              0.15563
```

`std(CV means)` — the variance of the CV *estimate* — falls as `k` grows; at
`k = n` it is exactly 0 because leave-one-out has no random partition. The
spread *across folds* goes the other way: smaller folds are noisier, and at
`k = n` each fold error is a single squared residual.

**U-curve** — 5-fold CV error by polynomial degree, minimum at degree 4–5:

```
degree  1  0.2512     degree  5  0.0415  <- min
degree  2  0.0930     degree  8  0.0434
degree  3  0.0498     degree 11  0.0501
degree  4  0.0415     degree 12  0.0470
```

### Part 3 — the leakage lab

CV MSE as each leak is switched on (a *lower* number here means we are fooling
ourselves):

```
no leaks (all per-fold, NaNs imputed by train mean)   0.4459
+ target-derived imputation baked into the data       0.3739
+ feature selector fit on the whole dataset           0.2213
+ scaler fit on the whole dataset (all 3 leaks)       0.2213
```

- **Target-derived imputation** is the big one — and note that refitting the
  pipeline per fold does *not* rescue you: `y` is literally in the feature
  values, so the leak lives in the data, not the procedure. The fix is to not
  impute from the target at all.
- **Feature selection on the whole dataset** knocks off another big chunk: with
  400 pure-noise columns, the selector finds ones that happen to correlate with
  `y` on the validation rows too.
- **The global scaler** barely moves the number here — but it is still wrong:
  in deployment there are no future rows to compute the mean/std from, so the
  reported score is answering the wrong question.

### Part 4 — the split must match the data

```
grouped data (k-NN model):
  naive 5-fold  CV MSE = 0.252     (same patient in train and val)
  group 5-fold  CV MSE = 0.668     (a patient is entirely in or out)

time-ordered data (k-nearest-in-time predictor):
  shuffled 5-fold    CV MSE = 0.097     (model sees past and future)
  forward-chaining   CV MSE = 1.397     (train on past, predict forward)
```

Naive k-fold is 2–14× too optimistic. It silently assumes deployment on
patients already seen in training / the ability to train on the future.

### Part 5 — the full workflow

```
alpha = 0.001   CV MSE = 0.0386      <- best by CV
alpha = 0.01    CV MSE = 0.0402
alpha = 0.1     CV MSE = 0.0533
alpha = 1.0     CV MSE = 0.1049
alpha = 10.0    CV MSE = 0.1379

TEST MSE (reported once, after all decisions locked) = 0.0488
```

The test set is scored exactly once. If you then dislike `0.0488`, widen the
`alpha` grid and re-score, the test set has become a second validation set and
every number after that is optimistic.

## "Before you trust a score" checklist, applied to Part 5

- [x] Test set separated before any exploration or tuning (`train_test_split`, seed 0, first)
- [x] Preprocessing fit inside the training folds only (ridge has none; the polynomial features are a fixed transform)
- [x] Splitter respects classes / groups / time order (plain k-fold is valid — this data is i.i.d. sine + noise)
- [x] Hyperparameter (`alpha`) chosen by 5-fold CV on the training pool, never on the test set
- [x] Test set touched once, after `best_alpha` was locked

## Reading guide

`train_test_split`, `kfold_indices`, `cross_val_score`, `group_kfold_indices`
and `time_series_folds` are all a few lines of numpy each. A "fitted model" is
represented as a `predict(x)` function returned by a `fit_*` function, so the
cross-validation loop is the same three lines regardless of the model. The
script follows the assignment part by part.
