# Assignment: Bias–Variance Tradeoff, By Resampling

**Unit:** Core ML Concepts
**Decks this builds on:** *Bias–Variance Tradeoff*
**Reference solution:** `bias_variance/` (run with `uv run bias_variance.py`)

## Why this assignment

A model's error has two very different sources: being *systematically wrong*
(bias) and being *unstable across training sets* (variance). You can't see
either one from a single fit on a single dataset — you have to refit the same
model on many different random samples of the same underlying process and watch
what moves.

By the end you should be able to say, from a plot you produced yourself:

- why a low-degree (simple) polynomial gives nearly the same wrong answer no
  matter which sample it's trained on — low variance, high bias;
- why a high-degree (complex) polynomial gives a very different answer each
  time — low bias, high variance;
- why total error is U-shaped in model complexity, with a sweet spot in
  between.

You may use `numpy`, `scikit-learn` (`PolynomialFeatures`, `LinearRegression`),
and a plotting library of your choice.

---

## Part 1 — Same model, many samples

Pick a true function that isn't itself a polynomial, e.g. `f(x) = sin(1.5πx)`,
so no degree fits it perfectly. Fix a sample size (e.g. 20 points of `x`
drawn uniformly from `[0, 1]`) and a noise level (e.g. `y = f(x) + noise`,
`noise ~ N(0, 0.2²)`).

1. Pick one **low-degree** polynomial (degree 1) and one **high-degree**
   polynomial (degree 10).
2. For each degree: draw 30 *fresh* random training samples (same size and
   noise level each time), fit the polynomial to each, and predict across a
   fixed test grid `x_test = linspace(0, 1, 100)`.
3. Make one plot per degree: the true function plus all 30 fitted curves
   overlaid (use a low `alpha` so overlapping lines are visible as a band).

   You should see the degree-1 curves land in nearly the same wrong place
   every time, while the degree-10 curves fan out wildly and disagree with
   each other — even though both were fit on data from the *same* underlying
   process.

---

## Part 2 — Put a number on it

1. At the single test point `x = 0.5`, collect the 30 predictions from each
   degree (from Part 1) and compute:
   - **bias** — how far the *average* prediction is from the true `f(0.5)`
   - **variance** — how spread out the 30 predictions are around their own
     average

   Confirm in words: degree 1 has small variance / larger bias, degree 10 has
   small bias / larger variance.

2. **Sweep degree 1–10.** Repeat the resampling procedure (this time across
   the whole test grid, not just one point) for every degree, and compute
   bias², variance, and total error (`mean squared error against the true
   function, averaged over samples`) at each degree. Plot all three against
   degree on one set of axes.

   You should see bias² fall smoothly, variance rise (steeply past some
   degree), and total error trace a U-shape with a minimum somewhere in the
   middle — the "sweet spot" where the model is complex enough to capture the
   shape but not so complex that it chases noise.

---

## What to submit

```
bias_variance/
  solution.py        # your script, run with: uv run solution.py
  README.md          # "What to expect" section with the numbers YOUR run produced
  *.html / *.png     # the overlay plots from Part 1 and the bias/variance/error
                      #   curve from Part 2
```

In one or two sentences each, answer in your README or a short `writeup.md`:

- Which of the two degree-1 vs degree-10 models would you trust more if you
  only got to train on one dataset and never got to check the true function?
  Why?
- Point to the degree in your sweep where total error is minimized. Is it
  closer to the low-bias end or the low-variance end?

## Stretch (optional)

- Repeat the whole experiment with a larger training-sample size (e.g. 100
  instead of 20) and describe how the variance curve changes. This is the
  "more data tames variance" idea from the deck.
- Repeat with a lower noise level and describe which curve (bias² or
  variance) is unaffected.
