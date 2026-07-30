---
theme: default
highlighter: shiki
css: unocss
colorSchema: dark
title: 'Hyperparameter Tuning Strategies'
info: |
  ## Hyperparameter Tuning Strategies
  Spend a fixed search budget where it teaches you the most
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
glowSeed: 930
---

# Hyperparameter Tuning Strategies

### Spend a fixed search budget where it teaches you the most

<div class="pt-8 opacity-80 text-lg">Optimization in Practice · Foundations of Machine Learning</div>

<div class="mt-14 flex justify-center gap-4" aria-hidden="true">
<div class="w-28 h-3 rounded-full bg-teal-400/70"></div>
<div class="w-20 h-3 rounded-full bg-blue-400/60"></div>
<div class="w-14 h-3 rounded-full bg-violet-400/50"></div>
</div>

<!--
This deck follows directly from the gradient-descent-variants deck: we just spent an entire session on optimizer mechanics, and every one of those optimizers introduced its own hyperparameters — learning rate α, momentum coefficient β, Adam's β₁ and β₂, plus model hyperparameters like regularization strength, tree depth, number of hidden units, and batch size. A hyperparameter, to define it precisely, is any setting chosen before training that is not learned from data by the optimization procedure itself — contrast this with parameters (weights, coefficients), which gradient descent or a closed-form solver estimates directly from the training data.

Today's question is purely about search strategy: given a fixed compute budget, how do you spend it to find good hyperparameters? We will compare grid search (exhaustive but wasteful), random search (a surprisingly strong, cheap improvement), log-uniform sampling for multiplicative parameters, and Bayesian optimization (uses past trial outcomes to choose the next trial intelligently). We close with a practical broad-to-narrow workflow and a reminder about a discipline violation that silently invalidates your reported test accuracy: tuning on the test set.

Roadmap: search-space growth → grid search and its exhaustive-but-wasteful nature → random search and why it usually wins for the same budget → log-scale sampling → RandomizedSearchCV in practice → Bayesian optimization → a concrete workflow → the train/validation/test discipline that must hold throughout.
-->

---
glowSeed: 931
---

# Search Spaces Grow Combinatorially

<div class="grid grid-cols-2 gap-8 items-start">
<div>
<div class="space-y-3 mt-4">
<div v-click border="2 solid white/5" bg="white/5" rounded-lg px-4 py-3>
<span class="font-bold text-teal-300">Interactions</span>
<span class="text-sm opacity-85"> — The best learning rate can depend on batch size and regularization.</span>
</div>
<div v-click border="2 solid white/5" bg="white/5" rounded-lg px-4 py-3>
<span class="font-bold text-blue-300">Expensive trials</span>
<span class="text-sm opacity-85"> — Each candidate may require a full cross-validated fit.</span>
</div>
<div v-click border="2 solid white/5" bg="white/5" rounded-lg px-4 py-3>
<span class="font-bold text-amber-300">Grid explosion</span>
<span class="text-sm opacity-85"> — A few values across many dimensions become thousands of combinations.</span>
</div>
</div>
</div>
<div>
<div v-click class="mt-4" style="font-size: .9em" border="2 solid teal-800" bg="teal-800/20" rounded-lg px-4 py-3>

$$
N_{\mathrm{configurations}}=v^h
$$

</div>

</div>
</div>

<!--
Walk through the formula: N_configurations = v^h, where v is the number of candidate values tried per hyperparameter and h is the number of hyperparameters being tuned jointly. This is combinatorial growth, not linear — with v = 3 candidate values (say, "low," "medium," "high") across h = 10 hyperparameters, N = 3^10 = 59,049 configurations, and each one may require a full cross-validated model fit to evaluate honestly.

Interactions are the reason we cannot tune hyperparameters one at a time and expect the result to be optimal jointly. Concretely: the best learning rate for SGD with a large batch size can differ from the best learning rate for the same model with a small batch size, because a larger batch gives a less noisy gradient estimate, which tolerates a larger step. If you tune learning rate first (holding batch size fixed at some default) and then tune batch size second (holding the just-found learning rate fixed), you may land far from the true joint optimum, because you never explored the combinations where both differ from their defaults simultaneously.

Expensive trials compound the problem: with k-fold cross-validation, each "configuration" in the grid actually costs k model fits, so the grid-search slide's 4×4 example with 5-fold CV is 16 × 5 = 80 total fits, not 16. This cost is exactly what motivates every strategy in the rest of this deck — we are choosing where a fixed number of expensive trials will teach us the most about the search space.
-->

---
glowSeed: 932
---

# Grid Search Is the Exhaustive Baseline

<div class="grid grid-cols-2 gap-8 items-start">
<div>
<div class="space-y-3 mt-4">
<div v-click border="2 solid white/5" bg="white/5" rounded-lg px-4 py-3>
<span class="font-bold text-teal-300">Strength</span>
<span class="text-sm opacity-85"> — Find the best point inside the stated grid.</span>
</div>
<div v-click border="2 solid white/5" bg="white/5" rounded-lg px-4 py-3>
<span class="font-bold text-blue-300">Weakness</span>
<span class="text-sm opacity-85"> — Spend equal compute on promising and useless regions.</span>
</div>
<div v-click border="2 solid white/5" bg="white/5" rounded-lg px-4 py-3>
<span class="font-bold text-amber-300">Hidden cost</span>
<span class="text-sm opacity-85"> — Configurations multiply again by the number of CV folds.</span>
</div>
</div>
</div>
<div>
<div role="img" aria-label="Two by two matrix for Grid Search Is the Exhaustive Baseline" class="mt-8 max-w-lg mx-auto">
<div class="grid grid-cols-[6rem_1fr_1fr] gap-2 text-center text-sm">
<div></div><div class="font-bold text-blue-300">Column A</div><div class="font-bold text-blue-300">Column B</div>
<div class="flex items-center justify-end pr-2 font-bold text-teal-300">Row A</div><div border="2 solid teal-800" bg="teal-800/20" rounded-lg p-5 class="text-2xl font-bold">✓</div><div border="2 solid red-800" bg="red-800/20" rounded-lg p-5 class="text-2xl font-bold">×</div>
<div class="flex items-center justify-end pr-2 font-bold text-teal-300">Row B</div><div border="2 solid red-800" bg="red-800/20" rounded-lg p-5 class="text-2xl font-bold">×</div><div border="2 solid teal-800" bg="teal-800/20" rounded-lg p-5 class="text-2xl font-bold">✓</div>
</div>
</div>

</div>
</div>

<!--
Grid search enumerates the Cartesian product of a fixed, discrete set of candidate values for every hyperparameter and evaluates every combination — in the 2×2 illustration on this slide, "Row" and "Column" stand in for two hyperparameter axes, and every cell of the grid is a configuration that gets fit and cross-validated. Its strength is exhaustiveness within the stated grid: it is guaranteed to find the best combination among the values you specified, with no randomness in which points get tried, which makes results perfectly reproducible.

Its weakness is exactly that guarantee's dual: it spends equal compute on every cell of the grid regardless of whether that region of the space looks promising, including cells that are obviously bad combinations (e.g., a huge learning rate paired with a huge batch size, likely to diverge). It also treats every hyperparameter as equally important, when in practice — this is a key empirical finding we will return to on the random-search slide — usually only a few hyperparameters actually drive most of the variance in performance, and grid search wastes disproportionate compute exploring fine gradations of the unimportant ones.

Concrete cost: a grid search with 4 values for one hyperparameter and 4 for a second (16 configurations) evaluated under 5-fold cross-validation requires 16 × 5 = 80 total model fits. Add a third hyperparameter with 4 values and you are at 4×4×4×5 = 320 fits. This is the exact combinatorial explosion from the previous slide, now made concrete with a fold multiplier on top.
-->

---
glowSeed: 933
---

# Random Search Covers Important Axes Better

<div class="grid grid-cols-2 gap-8 items-start">
<div>
<div class="space-y-3 mt-4">
<div v-click border="2 solid teal-800" bg="teal-800/20" rounded-lg px-4 py-3>
<span class="font-bold text-teal-300">Grid</span>
<span class="text-sm opacity-85"> — Repeats a small, fixed set of values along every axis.</span>
</div>
<div v-click border="2 solid blue-800" bg="blue-800/20" rounded-lg px-4 py-3>
<span class="font-bold text-blue-300">Random</span>
<span class="text-sm opacity-85"> — Samples a fresh value per axis on every trial, for the same budget.</span>
</div>
<div v-click border="2 solid amber-800" bg="amber-800/20" rounded-lg px-4 py-3>
<span class="font-bold text-amber-300">Why it wins</span>
<span class="text-sm opacity-85"> — Often only a few hyperparameters strongly control performance.</span>
</div>
</div>
</div>
<div>
<svg role="img" aria-label="9-point grid search versus 9-point random search when only the horizontal axis matters" viewBox="0 0 480 320" class="w-full max-w-lg mx-auto mt-4">
  <text x="10" y="20" fill="#94a3b8" style="font-size:13px">Grid: 3×3 = 9 trials, only 3 distinct x-values</text>
  <line x1="30" y1="130" x2="220" y2="130" stroke="#64748b" stroke-width="1.5"/>
  <line x1="30" y1="130" x2="30" y2="30" stroke="#64748b" stroke-width="1.5"/>
  <g fill="#2dd4bf">
    <circle cx="60" cy="50" r="5"/><circle cx="120" cy="50" r="5"/><circle cx="180" cy="50" r="5"/>
    <circle cx="60" cy="90" r="5"/><circle cx="120" cy="90" r="5"/><circle cx="180" cy="90" r="5"/>
    <circle cx="60" cy="115" r="5"/><circle cx="120" cy="115" r="5"/><circle cx="180" cy="115" r="5"/>
  </g>
  <text x="105" y="150" fill="#5eead4" style="font-size:12px" text-anchor="middle">unimportant axis (vertical)</text>

  <text x="260" y="20" fill="#94a3b8" style="font-size:13px">Random: 9 trials, 9 distinct x-values</text>
  <line x1="280" y1="130" x2="470" y2="130" stroke="#64748b" stroke-width="1.5"/>
  <line x1="280" y1="130" x2="280" y2="30" stroke="#64748b" stroke-width="1.5"/>
  <g fill="#60a5fa">
    <circle cx="300" cy="62" r="5"/><circle cx="318" cy="105" r="5"/><circle cx="340" cy="45" r="5"/>
    <circle cx="365" cy="88" r="5"/><circle cx="385" cy="120" r="5"/><circle cx="405" cy="55" r="5"/>
    <circle cx="425" cy="98" r="5"/><circle cx="445" cy="70" r="5"/><circle cx="460" cy="112" r="5"/>
  </g>
  <text x="375" y="150" fill="#93c5fd" style="font-size:12px" text-anchor="middle">unimportant axis (vertical)</text>

  <text x="30" y="200" fill="#cbd5e1" style="font-size:13px">If only the horizontal axis affects validation score:</text>
  <text x="30" y="222" fill="#5eead4" style="font-size:13px">grid search effectively tested only 3 useful settings,</text>
  <text x="30" y="244" fill="#93c5fd" style="font-size:13px">random search effectively tested 9 — same trial budget.</text>
</svg>
</div>
</div>

<!--
This is the Bergstra and Bengio (2012) argument, stated as a design picture rather than a citation to memorize. Suppose you have two hyperparameters and, unknown to you in advance, only one of them (say, the horizontal axis) actually affects validation performance — the other is nearly irrelevant across its whole range. A 3×3 grid tries only 3 distinct values along the important axis, because every value gets repeated 3 times (once for each value of the unimportant axis) — the repeated trials along the unimportant axis are wasted compute. A 9-trial random search, in contrast, draws 9 independent values along the important axis and 9 independent values along the unimportant one, so it tests 9 distinct settings of the axis that actually matters, three times denser coverage of the one dimension that mattered, for the identical trial budget.

This result generalizes: in real hyperparameter tuning, especially for neural networks, empirical studies consistently find that a small number of hyperparameters (often the learning rate, sometimes one or two regularization-related settings) dominate performance while several others matter little within a reasonable range. Random search's advantage grows as the number of unimportant axes grows, because grid search's redundancy compounds multiplicatively while random search's coverage per axis stays fixed at the trial budget regardless of dimensionality.

Common misconception: "random" does not mean "worse than grid because it might miss the best point." Random search will not find the *exact* optimum of a fixed grid any more reliably than that grid would, but for the same compute budget it explores a strictly wider range of settings along every individual axis, which is usually the more valuable property in high-dimensional search spaces where most axes barely matter.
-->

---
glowSeed: 934
---

# Sample Multiplicative Parameters on a Log Scale

<div class="grid grid-cols-2 gap-8 items-start">
<div>
<div class="space-y-3 mt-4">
<div v-click border="2 solid white/5" bg="white/5" rounded-lg px-4 py-3>
<span class="font-bold text-teal-300">Orders of magnitude</span>
<span class="text-sm opacity-85"> — 0.001 → 0.01 matters like 0.01 → 0.1.</span>
</div>
<div v-click border="2 solid white/5" bg="white/5" rounded-lg px-4 py-3>
<span class="font-bold text-blue-300">Linear sampling</span>
<span class="text-sm opacity-85"> — Overrepresents the high end of a wide interval.</span>
</div>
<div v-click border="2 solid white/5" bg="white/5" rounded-lg px-4 py-3>
<span class="font-bold text-amber-300">Log-uniform</span>
<span class="text-sm opacity-85"> — Gives each power-of-ten band equal attention.</span>
</div>
</div>
</div>
<div>
<svg role="img" aria-label="Conceptual chart for Sample Multiplicative Parameters on a Log Scale" viewBox="0 0 500 310" class="w-full max-w-xl mx-auto mt-7">
  <line x1="55" y1="260" x2="470" y2="260" stroke="#64748b" stroke-width="2"/><line x1="55" y1="35" x2="55" y2="260" stroke="#64748b" stroke-width="2"/>
  <path d="M60 235 C130 210,145 70,220 100 S320 210,465 55" fill="none" stroke="#2dd4bf" stroke-width="5"/>
  <path d="M60 245 C135 230,205 195,270 165 S385 110,465 95" fill="none" stroke="#60a5fa" stroke-width="4" stroke-dasharray="9 7"/>
  <g fill="#f59e0b"><circle cx="65" cy="230" r="6"/><circle cx="163" cy="185" r="6"/><circle cx="261" cy="110" r="6"/><circle cx="359" cy="150" r="6"/><circle cx="457" cy="65" r="6"/></g>
  <g fill="#cbd5e1" style="font-size: 12px" text-anchor="middle"><text x="65" y="285">10⁻⁴</text><text x="163" y="285">10⁻³</text><text x="261" y="285">10⁻²</text><text x="359" y="285">10⁻¹</text><text x="457" y="285">1</text></g>
  <g style="font-size: 12px"><text x="335" y="42" fill="#5eead4">primary signal</text><text x="335" y="82" fill="#93c5fd">comparison</text></g>
</svg>
<div v-click class="mt-4" style="font-size: .9em" border="2 solid teal-800" bg="teal-800/20" rounded-lg px-4 py-3>

$$
\log_{10}h\sim\mathcal U(-4,0)
$$

</div>
</div>
</div>

<!--
The core idea: for a hyperparameter that acts multiplicatively on model behavior — meaning doubling it or halving it has roughly the same-sized effect regardless of where you start — uniform sampling on the raw scale wastes most of its samples in the wrong region. Concretely, going from a learning rate of 0.001 to 0.01 (a 10x change) changes training behavior about as much as going from 0.01 to 0.1 (also 10x) — both are "one order of magnitude" changes with comparable practical impact, even though the second gap (0.09) is nine times larger in raw units than the first gap (0.009).

If you sample h uniformly on, say, [0.0001, 1], the overwhelming majority of draws land in [0.1, 1] simply because that interval is numerically enormous compared to [0.0001, 0.001] — you would rarely sample anything near 0.0001 even though small learning rates are often exactly the useful regime for fine-tuning or later training stages. The fix is to sample the exponent uniformly instead: log₁₀h ~ 𝒰(−4, 0), which is mathematically equivalent to sampling h itself from a log-uniform distribution. This puts equal sampling density in every order-of-magnitude band — [0.0001, 0.001], [0.001, 0.01], [0.01, 0.1], [0.1, 1] — each gets roughly a quarter of the trials.

Common multiplicative candidates for log-scale sampling: learning rate α, SVM's C (inverse regularization strength) and gamma (kernel coefficient), L1/L2 regularization strength λ, and Adam's ε in some sensitivity studies. Contrast with additive hyperparameters like tree depth or number of layers, where uniform sampling on the raw integer scale is usually appropriate because a change from depth 3 to 4 is comparable in effect to a change from depth 8 to 9.
-->

---
glowSeed: 935
---

# RandomizedSearchCV

<div class="grid grid-cols-2 gap-4 mt-6">
<div v-click border="2 solid teal-800" bg="teal-800/20" rounded-lg p-4>
<div class="font-bold text-teal-300 mb-2">Fixed budget</div>
<div class="text-sm leading-relaxed opacity-90">n_iter controls the number of configurations.</div>
</div>
<div v-click border="2 solid blue-800" bg="blue-800/20" rounded-lg p-4>
<div class="font-bold text-blue-300 mb-2">Distributions</div>
<div class="text-sm leading-relaxed opacity-90">Describe ranges instead of enumerating every point.</div>
</div>
</div>

```python
from scipy.stats import loguniform
from sklearn.model_selection import RandomizedSearchCV

search = RandomizedSearchCV(
    SVC(),
    {"C": loguniform(1e-2, 1e2),
     "gamma": loguniform(1e-4, 1)},
    n_iter=20, cv=5, random_state=0,
)
search.fit(X, y)
```

<!--
Walk through the code: `loguniform(1e-2, 1e2)` and `loguniform(1e-4, 1)` from `scipy.stats` implement exactly the log-uniform sampling from the previous slide — calling `.rvs()` on them draws a value whose exponent is uniform, not the value itself. Passing these distribution objects (instead of explicit lists of candidate values, as `GridSearchCV` requires) is what lets `RandomizedSearchCV` sample from a continuous range rather than a small fixed set — you get finer-grained coverage of each axis without hand-picking discrete points.

`n_iter=20` is the entire budget control: exactly 20 configurations get sampled and evaluated, regardless of how many hyperparameters are being searched or how wide their distributions are. Combined with `cv=5`, this is 20 × 5 = 100 total model fits — compare this to grid search, where adding a third hyperparameter or finer grid resolution directly multiplies the fit count. Here the fit count is decoupled from the dimensionality and resolution of the search space entirely; you choose your compute budget once, independent of how many hyperparameters you are tuning.

`random_state=0` matters for reproducibility — without it, two runs of the same search would sample different configurations and could report different "best" hyperparameters, which makes debugging and comparing results across experiments unreliable. Always set it explicitly in coursework and shared research code.
-->

---
glowSeed: 936
---

# Bayesian Optimization Learns From Trials

<div class="grid grid-cols-2 gap-8 items-start">
<div>
<div class="space-y-3 mt-4">
<div v-click border="2 solid white/5" bg="white/5" rounded-lg px-4 py-3>
<span class="font-bold text-teal-300">Surrogate model</span>
<span class="text-sm opacity-85"> — Estimate performance and uncertainty across the search space.</span>
</div>
<div v-click border="2 solid white/5" bg="white/5" rounded-lg px-4 py-3>
<span class="font-bold text-blue-300">Acquisition</span>
<span class="text-sm opacity-85"> — Choose the next candidate where promise or uncertainty is high.</span>
</div>
<div v-click border="2 solid white/5" bg="white/5" rounded-lg px-4 py-3>
<span class="font-bold text-amber-300">Tradeoff</span>
<span class="text-sm opacity-85"> — Fewer expensive trials at the cost of a more complex search algorithm.</span>
</div>
</div>
</div>
<div>
<div class="mt-5" role="img" aria-label="Evaluate then Update surrogate then Choose next then Evaluate">
<div v-click class="flex items-center gap-3">
<div class="w-8 h-8 rounded-full bg-teal-500/20 border-2 border-teal-700 flex items-center justify-center text-sm font-bold">1</div>
<div class="flex-1 rounded-lg border-2 border-white/10 bg-white/5 px-3 py-2 text-sm font-bold">Evaluate</div>
</div>
<div class="ml-4 h-1 border-l-2 border-teal-400/50"></div>
<div v-click class="flex items-center gap-3">
<div class="w-8 h-8 rounded-full bg-blue-500/20 border-2 border-blue-700 flex items-center justify-center text-sm font-bold">2</div>
<div class="flex-1 rounded-lg border-2 border-white/10 bg-white/5 px-3 py-2 text-sm font-bold">Update surrogate</div>
</div>
<div class="ml-4 h-1 border-l-2 border-teal-400/50"></div>
<div v-click class="flex items-center gap-3">
<div class="w-8 h-8 rounded-full bg-amber-500/20 border-2 border-amber-700 flex items-center justify-center text-sm font-bold">3</div>
<div class="flex-1 rounded-lg border-2 border-white/10 bg-white/5 px-3 py-2 text-sm font-bold">Choose next</div>
</div>
<div class="ml-4 h-1 border-l-2 border-teal-400/50"></div>
<div v-click class="flex items-center gap-3">
<div class="w-8 h-8 rounded-full bg-violet-500/20 border-2 border-violet-700 flex items-center justify-center text-sm font-bold">4</div>
<div class="flex-1 rounded-lg border-2 border-white/10 bg-white/5 px-3 py-2 text-sm font-bold">Evaluate</div>
</div>
</div>

</div>
</div>

<!--
Bayesian optimization treats hyperparameter search itself as an optimization problem, and — crucially, unlike grid or random search — it uses the outcome of every past trial to inform the choice of the next one, rather than sampling all trials independently in advance. The core loop has two models working together: a surrogate model (commonly a Gaussian process, though tree-based surrogates like in TPE/Hyperopt are also common) that predicts expected validation performance and, importantly, its own uncertainty at any untested point in the hyperparameter space, given all trials observed so far; and an acquisition function that scores every candidate point by combining the surrogate's predicted performance with its uncertainty, then picks the next configuration to actually evaluate.

Walk the four-step loop shown: (1) evaluate a configuration, getting one real, expensive data point; (2) update the surrogate model with that new observation, refining its beliefs about the whole space; (3) the acquisition function chooses the next candidate — usually balancing exploitation (regions the surrogate predicts are good) against exploration (regions the surrogate is still uncertain about, which could hide a surprise); (4) evaluate that new candidate, and repeat.

The tradeoff to state plainly: Bayesian optimization is worth its algorithmic complexity specifically when each trial is very expensive — training a large neural network for hours or days — because it typically finds a good configuration in noticeably fewer trials than random search. It is usually not worth the overhead when trials are cheap (a small scikit-learn model that trains in seconds), because random search's simplicity and full parallelizability outweigh the modest reduction in trial count; Bayesian optimization's sequential nature (each trial depends on the last) also makes it harder to parallelize across many machines than random search, which is embarrassingly parallel.
-->

---
glowSeed: 937
---

# A Practical Broad-to-Narrow Workflow

<div class="grid grid-cols-2 gap-8 items-start">
<div>
<div class="space-y-3 mt-4">
<div v-click border="2 solid white/5" bg="white/5" rounded-lg px-4 py-3>
<span class="font-bold text-teal-300">Start broad</span>
<span class="text-sm opacity-85"> — Random search over wide, sensible ranges.</span>
</div>
<div v-click border="2 solid white/5" bg="white/5" rounded-lg px-4 py-3>
<span class="font-bold text-blue-300">Narrow</span>
<span class="text-sm opacity-85"> — Refine around promising regions.</span>
</div>
<div v-click border="2 solid white/5" bg="white/5" rounded-lg px-4 py-3>
<span class="font-bold text-amber-300">Lock decisions</span>
<span class="text-sm opacity-85"> — Select the final configuration with validation or CV.</span>
</div>
<div v-click border="2 solid white/5" bg="white/5" rounded-lg px-4 py-3>
<span class="font-bold text-violet-300">Test once</span>
<span class="text-sm opacity-85"> — Use the untouched test set only at the end.</span>
</div>
</div>
</div>
<div>
<div class="mt-5" role="img" aria-label="Wide random search then Focused search then Final model then One test">
<div v-click class="flex items-center gap-3">
<div class="w-8 h-8 rounded-full bg-teal-500/20 border-2 border-teal-700 flex items-center justify-center text-sm font-bold">1</div>
<div class="flex-1 rounded-lg border-2 border-white/10 bg-white/5 px-3 py-2 text-sm font-bold">Wide random search</div>
</div>
<div class="ml-4 h-1 border-l-2 border-teal-400/50"></div>
<div v-click class="flex items-center gap-3">
<div class="w-8 h-8 rounded-full bg-blue-500/20 border-2 border-blue-700 flex items-center justify-center text-sm font-bold">2</div>
<div class="flex-1 rounded-lg border-2 border-white/10 bg-white/5 px-3 py-2 text-sm font-bold">Focused search</div>
</div>
<div class="ml-4 h-1 border-l-2 border-teal-400/50"></div>
<div v-click class="flex items-center gap-3">
<div class="w-8 h-8 rounded-full bg-amber-500/20 border-2 border-amber-700 flex items-center justify-center text-sm font-bold">3</div>
<div class="flex-1 rounded-lg border-2 border-white/10 bg-white/5 px-3 py-2 text-sm font-bold">Final model</div>
</div>
<div class="ml-4 h-1 border-l-2 border-teal-400/50"></div>
<div v-click class="flex items-center gap-3">
<div class="w-8 h-8 rounded-full bg-violet-500/20 border-2 border-violet-700 flex items-center justify-center text-sm font-bold">4</div>
<div class="flex-1 rounded-lg border-2 border-white/10 bg-white/5 px-3 py-2 text-sm font-bold">One test</div>
</div>
</div>

</div>
</div>

<!--
This workflow combines everything in the deck into one practical procedure. Step 1, wide random search: start with random search over deliberately wide, log-scaled ranges for every hyperparameter you suspect might matter — the goal here is coverage, not precision, so use a moderate trial budget to find the rough neighborhood of good settings and identify which axes actually move the validation score. Step 2, focused search: once you see which region of the space looks promising, narrow the ranges around it and search again, more densely — at this stage either random search with tighter bounds or Bayesian optimization if trials are expensive enough to justify it are both reasonable choices.

Step 3, lock decisions: after narrowing, pick a single final hyperparameter configuration using validation performance (or cross-validated performance if the dataset is small enough that a single validation split is noisy) — this is the last point in the workflow where hyperparameter choices are allowed to change. Step 4, test once: evaluate the final, fully-configured model on the held-out test set exactly once, and report that number.

The critical discipline point, worth stating explicitly because it is the most common real-world mistake in applied ML: the test set must never influence any hyperparameter decision, not even indirectly by "just checking" test performance for a few candidate configurations and picking the best one. Doing so turns the test set into a second validation set, and the reported test accuracy becomes an optimistic, biased estimate of true generalization — often by a small but real and hard-to-detect margin. If you need more tuning iterations than a single validation split can reliably support, use cross-validation or a dedicated tuning/validation split, but the test set stays untouched until the very last evaluation.
-->

---
glowSeed: 938
---

# Tune Systematically

<div class="mt-8"><div class="grid grid-cols-3 gap-4 mt-6">
<div v-click border="2 solid teal-800" bg="teal-800/20" rounded-lg p-4>
<div class="font-bold text-teal-300 mb-2">Budget</div>
<div class="text-sm leading-relaxed opacity-90">Count evaluations.</div>
</div>
<div v-click border="2 solid blue-800" bg="blue-800/20" rounded-lg p-4>
<div class="font-bold text-blue-300 mb-2">Scale</div>
<div class="text-sm leading-relaxed opacity-90">Use log ranges when appropriate.</div>
</div>
<div v-click border="2 solid amber-800" bg="amber-800/20" rounded-lg p-4>
<div class="font-bold text-amber-300 mb-2">Discipline</div>
<div class="text-sm leading-relaxed opacity-90">Never tune on test.</div>
</div>
</div></div>

<div v-click class="mt-10 text-center text-lg" border="2 solid white/10" bg="white/5" rounded-lg px-6 py-4>Next: broader context—fairness, interpretability, and responsible deployment.</div>

<!--
Recap the three practical habits this deck should leave you with. Budget: before searching, decide how many total model fits you can afford (trials × CV folds), because that number — not the size of the hyperparameter space — determines which strategy makes sense; grid search only makes sense when the budget comfortably covers the full Cartesian product, which is rare once you have more than two or three hyperparameters. Scale: sample multiplicative hyperparameters (learning rate, regularization strength, kernel coefficients) log-uniformly rather than linearly, so your trial budget is not wasted overrepresenting one order of magnitude. Discipline: never let the test set influence a hyperparameter decision, directly or indirectly — this is not a suggestion, it is the difference between a valid and an invalid estimate of generalization performance.

These three habits generalize past this specific deck: every hyperparameter introduced anywhere else in this course — the optimizer's learning rate and momentum coefficients from the previous deck, a tree's max depth, a regularization penalty's strength, a neural network's width and depth, the number of clusters in k-means — gets tuned using exactly this playbook. There is no separate "how to tune k in k-means" lecture; it is the same random-search-then-narrow workflow with an appropriate range and scale for that specific parameter.

Transition to next topic: we have now covered how models learn (optimization) and how to configure the process that governs learning (hyperparameter tuning). The next module steps back to broader context — fairness, interpretability, and responsible deployment — questions that matter once a well-tuned model is ready to affect real decisions.
-->
