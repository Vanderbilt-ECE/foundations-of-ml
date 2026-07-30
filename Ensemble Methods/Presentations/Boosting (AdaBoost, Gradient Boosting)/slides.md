---
theme: default
highlighter: shiki
css: unocss
colorSchema: dark
title: 'Boosting: AdaBoost and Gradient Boosting'
info: |
  ## Boosting: AdaBoost and Gradient Boosting
  Build strength by learning from mistakes
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
glowSeed: 640
---

# Boosting: AdaBoost and Gradient Boosting

### Build strength by learning from mistakes

<div class="pt-8 opacity-80 text-lg">Ensemble Methods · Foundations of Machine Learning</div>

<div class="mt-14 flex justify-center gap-4" aria-hidden="true">
<div class="w-28 h-3 rounded-full bg-teal-400/70"></div>
<div class="w-20 h-3 rounded-full bg-blue-400/60"></div>
<div class="w-14 h-3 rounded-full bg-violet-400/50"></div>
</div>

<!--
The previous deck was about bagging: train many deep, unstable trees independently and in parallel, then average away their variance while their bias stays essentially fixed. This deck is about boosting, which attacks the opposite problem with the opposite structure. Where bagging starts from a low-bias, high-variance base learner and cancels variance, boosting starts from a high-bias, low-variance base learner — typically a stump, a tree of depth one — and sequentially, deliberately reduces bias by building each new learner to correct the mistakes the ensemble has made so far.

Roadmap: the boosting idea in general (sequential, corrective, weighted combination) → AdaBoost, the original and most teachable instance, including a full derivation of where its famous weight-update formula comes from and why → a runnable scikit-learn example → gradient boosting, which generalizes AdaBoost's idea to arbitrary differentiable loss functions by fitting each new learner to the negative gradient of the loss ("function-space gradient descent") → the learning-rate/number-of-rounds tradeoff, including boosting's characteristic overfitting risk that bagging does not share → a direct bagging-vs-boosting comparison to close the loop with the previous deck.
-->

---
glowSeed: 641
---

# The Boosting Idea

<div class="grid grid-cols-2 gap-8 items-start">
<div>
<div class="space-y-3 mt-4">
<div v-click border="2 solid white/5" bg="white/5" rounded-lg px-4 py-3>
<span class="font-bold text-teal-300">Weak learners</span>
<span class="text-sm opacity-85"> — Use shallow trees that are only slightly better than guessing.</span>
</div>
<div v-click border="2 solid white/5" bg="white/5" rounded-lg px-4 py-3>
<span class="font-bold text-blue-300">Sequential focus</span>
<span class="text-sm opacity-85"> — Each round pays more attention to what the ensemble still gets wrong.</span>
</div>
<div v-click border="2 solid white/5" bg="white/5" rounded-lg px-4 py-3>
<span class="font-bold text-amber-300">Weighted combination</span>
<span class="text-sm opacity-85"> — Many small corrections become one strong predictor.</span>
</div>
</div>
</div>
<div>
<div class="mt-5" role="img" aria-label="Weak model 1 then Residual mistakes then Weak model 2 then Strong ensemble">
<div v-click class="flex items-center gap-3">
<div class="w-8 h-8 rounded-full bg-teal-500/20 border-2 border-teal-700 flex items-center justify-center text-sm font-bold">1</div>
<div class="flex-1 rounded-lg border-2 border-white/10 bg-white/5 px-3 py-2 text-sm font-bold">Weak model 1</div>
</div>
<div class="ml-4 h-1 border-l-2 border-teal-400/50"></div>
<div v-click class="flex items-center gap-3">
<div class="w-8 h-8 rounded-full bg-blue-500/20 border-2 border-blue-700 flex items-center justify-center text-sm font-bold">2</div>
<div class="flex-1 rounded-lg border-2 border-white/10 bg-white/5 px-3 py-2 text-sm font-bold">Residual mistakes</div>
</div>
<div class="ml-4 h-1 border-l-2 border-teal-400/50"></div>
<div v-click class="flex items-center gap-3">
<div class="w-8 h-8 rounded-full bg-amber-500/20 border-2 border-amber-700 flex items-center justify-center text-sm font-bold">3</div>
<div class="flex-1 rounded-lg border-2 border-white/10 bg-white/5 px-3 py-2 text-sm font-bold">Weak model 2</div>
</div>
<div class="ml-4 h-1 border-l-2 border-teal-400/50"></div>
<div v-click class="flex items-center gap-3">
<div class="w-8 h-8 rounded-full bg-violet-500/20 border-2 border-violet-700 flex items-center justify-center text-sm font-bold">4</div>
<div class="flex-1 rounded-lg border-2 border-white/10 bg-white/5 px-3 py-2 text-sm font-bold">Strong ensemble</div>
</div>
</div>

</div>
</div>

<!--
Define "weak learner" precisely, because the term is used loosely elsewhere: a weak learner is any model whose accuracy is only slightly better than random guessing — for binary classification, slightly better than 50%. A decision stump (a tree with exactly one split, depth 1) is the canonical weak learner: on its own it is a bad classifier, but that is by design, not a flaw. Contrast this immediately and explicitly with bagging's base learner: bagging wants deep, low-bias, high-variance trees because it plans to cancel variance by averaging. Boosting wants shallow, high-bias, low-variance learners because variance is not the thing it plans to fix — bias is, and it fixes bias by sequential correction rather than by parallel averaging.

Walk through the diagram left to right as the core loop: fit weak model 1 on the data, look at which examples it still gets wrong (its "residual mistakes" — for classification this is realized as up-weighting misclassified examples, for regression it is realized as literally fitting a residual y − prediction), fit weak model 2 with extra emphasis on exactly those hard cases, and repeat. After enough rounds, combine every weak model's prediction into one final vote, but not with equal weight — each weak learner's vote is scaled by how good it was (this weighting is exactly what AdaBoost's alpha, derived on the next slide, computes). The remarkable empirical and theoretical fact, which the "Why Ensembles Work" deck will revisit, is that a sequence of learners individually barely better than chance can be combined into an ensemble with arbitrarily low training error, given enough rounds — "many small corrections become one strong predictor" is not just a slogan, it is a provable statement for AdaBoost under mild conditions.
-->

---
glowSeed: 642
---

# Deriving AdaBoost's Alpha

<div class="grid grid-cols-2 gap-8 items-start">
<div>
<div class="space-y-3 mt-4">
<div v-click border="2 solid white/5" bg="white/5" rounded-lg px-4 py-3>
<span class="font-bold text-teal-300">Setup</span>
<span class="text-sm opacity-85"> — Labels and predictions live in {−1, +1}; minimize weighted exponential loss round by round.</span>
</div>
<div v-click border="2 solid white/5" bg="white/5" rounded-lg px-4 py-3>
<span class="font-bold text-blue-300">Split by correctness</span>
<span class="text-sm opacity-85"> — Correct examples contribute e<sup>−α</sup>, mistakes contribute e<sup>α</sup>, weighted by ε<sub>t</sub>.</span>
</div>
<div v-click border="2 solid white/5" bg="white/5" rounded-lg px-4 py-3>
<span class="font-bold text-amber-300">Minimize and normalize</span>
<span class="text-sm opacity-85"> — Set the derivative to zero for α<sub>t</sub>; renormalize weights with Z<sub>t</sub> so they stay a distribution.</span>
</div>
</div>
</div>
<div>
<div v-click class="mt-3" style="font-size: .78em" border="2 solid teal-800" bg="teal-800/20" rounded-lg px-4 py-3>

$$
\begin{aligned}
L_t(\alpha) &= (1-\epsilon_t)\,e^{-\alpha} + \epsilon_t\, e^{\alpha}
\end{aligned}
$$

</div>
<div v-click class="mt-3" style="font-size: .78em" border="2 solid blue-800" bg="blue-800/20" rounded-lg px-4 py-3>

$$
\frac{dL_t}{d\alpha}=0 \ \Longrightarrow\ \alpha_t=\frac12\ln\frac{1-\epsilon_t}{\epsilon_t}
$$

</div>
<div v-click class="mt-3" style="font-size: .78em" border="2 solid amber-800" bg="amber-800/20" rounded-lg px-4 py-3>

$$
w_i^{(t+1)}=\frac{w_i^{(t)}\,e^{-\alpha_t y_i h_t(x_i)}}{Z_t}
$$

</div>
</div>
</div>

<!--
This derivation is worth doing in full because the formula on the next slide otherwise looks like it fell from the sky. AdaBoost minimizes, round by round, the weighted exponential loss of the ensemble built so far. Two setup facts make the algebra work: labels y_i and each weak learner's output h_t(x_i) both live in {−1, +1}, not {0, 1} — this matters because the product y_i·h_t(x_i) equals +1 exactly when the prediction is correct and −1 exactly when it is wrong, turning "correct or incorrect" into a clean sign. At round t, we already have example weights w_i^(t) from the previous round (uniform, 1/n each, at t = 1). Split the weighted loss contributed by adding α·h_t into two groups: examples h_t gets right contribute weight·e^(−α) each, and examples h_t gets wrong contribute weight·e^(+α) each. Summing the "wrong" group's weights defines the weighted error rate ε_t (a number between 0 and 1), so the total loss as a function of α alone is L_t(α) = (1 − ε_t)e^(−α) + ε_t·e^α — the first card on this slide.

Now minimize: differentiate L_t with respect to α, giving −(1 − ε_t)e^(−α) + ε_t·e^α, set it to zero, and solve. Rearranging gives e^(2α) = (1 − ε_t)/ε_t, and taking the log and dividing by 2 gives α_t = ½·ln[(1 − ε_t)/ε_t] — exactly the formula from the "AdaBoost Reweights Examples" slide. This is not an arbitrary weighting scheme; it is the unique α that minimizes the weighted exponential loss given how good h_t currently is.

Finally, the weight update. Having chosen α_t, AdaBoost updates every example's weight by w_i^(t+1) ∝ w_i^(t)·e^(−α_t·y_i·h_t(x_i)) — because y_i·h_t(x_i) is +1 for correct predictions, their weight shrinks by a factor of e^(−α_t); because it is −1 for mistakes, their weight grows by a factor of e^(+α_t). Bigger α_t (a more accurate weak learner) produces a bigger reweighting swing. One detail the earlier slide's formula omits and this one restores: the raw update does not automatically keep the weights summing to 1, so every round divides by a normalizing constant Z_t (the sum of the un-normalized updated weights) to keep w^(t+1) a valid probability distribution over examples — without renormalization the weights would drift and the weighted-error calculation at the next round would no longer mean what it's supposed to mean.
-->

---
glowSeed: 643
---

# AdaBoost Reweights Examples

<div class="grid grid-cols-2 gap-8 items-start">
<div>
<div class="space-y-3 mt-4">
<div v-click border="2 solid white/5" bg="white/5" rounded-lg px-4 py-3>
<span class="font-bold text-teal-300">Weighted error</span>
<span class="text-sm opacity-85"> — Measure a stump using the current example weights.</span>
</div>
<div v-click border="2 solid white/5" bg="white/5" rounded-lg px-4 py-3>
<span class="font-bold text-blue-300">Learner weight</span>
<span class="text-sm opacity-85"> — More accurate stumps receive a larger final vote.</span>
</div>
<div v-click border="2 solid white/5" bg="white/5" rounded-lg px-4 py-3>
<span class="font-bold text-amber-300">Example update</span>
<span class="text-sm opacity-85"> — Increase weights on mistakes; decrease them on correct cases.</span>
</div>
</div>
</div>
<div>
<div v-click class="mt-4" style="font-size: .9em" border="2 solid teal-800" bg="teal-800/20" rounded-lg px-4 py-3>

$$
\alpha_t=\frac12\log\frac{1-\epsilon_t}{\epsilon_t},\qquad w_i^{(t+1)}=w_i^{(t)}e^{-\alpha_t y_i h_t(x_i)}
$$

</div>

</div>
</div>

<div class="grid grid-cols-3 gap-3 mt-5">
<div v-click border="2 solid teal-800" bg="teal-800/20" rounded-lg p-3 text-sm>
<span class="font-bold text-teal-300">ε = 0.01</span> → α ≈ 2.30 — a near-perfect stump gets a dominant vote.
</div>
<div v-click border="2 solid blue-800" bg="blue-800/20" rounded-lg p-3 text-sm>
<span class="font-bold text-blue-300">ε = 0.3</span> → α ≈ 0.42 — a mediocre stump still gets a modest, positive say.
</div>
<div v-click border="2 solid amber-800" bg="amber-800/20" rounded-lg p-3 text-sm>
<span class="font-bold text-amber-300">ε = 0.5</span> → α = 0 — no better than a coin flip, so it is effectively ignored.
</div>
</div>

<!--
This slide is the compact reference version of the previous slide's derivation, plus a worked numeric table that shows how α_t behaves at the extremes. Plug in ε_t near zero: with ε = 0.01, α_t = ½·ln(0.99/0.01) = ½·ln(99) ≈ 2.30, a large positive weight — an almost-always-correct stump dominates the final vote, as it should. Plug in ε_t = 0.5, exactly chance-level: α_t = ½·ln(1) = 0, so that stump contributes nothing to the final prediction, which is exactly right, since a coin-flip learner carries no information. Push ε_t above 0.5 (a learner that is worse than random) and α_t goes negative — the formula would flip that learner's votes and use it "backwards" — though in practice AdaBoost's search for the best stump at each round should never select something worse than chance when better options exist.

Now trace the weight-update consequence, which is the part students most often get backwards: y_i·h_t(x_i) = +1 for correctly classified points, so their new weight is the old weight times e^(−α_t) — strictly less than 1 for any α_t > 0, so correct examples' weights shrink. For misclassified points, y_i·h_t(x_i) = −1, so the weight multiplies by e^(+α_t) — strictly greater than 1, so mistakes' weights grow. The net effect across rounds: examples the ensemble keeps getting wrong accumulate larger and larger weight, forcing the next weak learner to prioritize fitting exactly those hard cases, while easy, already-correct examples fade in influence. This is the concrete mechanism behind "sequential focus" from the previous slide — it is implemented entirely through this one multiplicative reweighting rule.
-->

---
glowSeed: 644
---

# AdaBoost in scikit-learn

<div class="grid grid-cols-2 gap-4 mt-6">
<div v-click border="2 solid teal-800" bg="teal-800/20" rounded-lg p-4>
<div class="font-bold text-teal-300 mb-2">Base learner</div>
<div class="text-sm leading-relaxed opacity-90">A depth-1 decision stump.</div>
</div>
<div v-click border="2 solid blue-800" bg="blue-800/20" rounded-lg p-4>
<div class="font-bold text-blue-300 mb-2">Ensemble</div>
<div class="text-sm leading-relaxed opacity-90">One hundred adaptive rounds.</div>
</div>
</div>

```python
from sklearn.ensemble import AdaBoostClassifier
from sklearn.tree import DecisionTreeClassifier
from sklearn.model_selection import cross_val_score

stump = DecisionTreeClassifier(max_depth=1)
ada = AdaBoostClassifier(
    estimator=stump, n_estimators=100, random_state=0,
)
print(cross_val_score(ada, X, y, cv=5).mean())
```

<!--
This is the practical version of everything just derived. estimator=stump fixes the base learner to a depth-1 decision tree — a single split, exactly the weak learner from the theory slides, deliberately kept simple because strength is supposed to come from the boosting sequence, not from any one learner's individual power. Naming the argument matters here as a version note: recent scikit-learn releases use estimator=, while older releases (roughly before 1.2) used base_estimator= for the same role — if this line throws a TypeError about an unexpected keyword, that mismatch is the most likely cause, and checking sklearn.__version__ is the fastest diagnostic.

n_estimators=100 sets the number of sequential rounds t = 1 … 100: at each round, AdaBoost computes the weighted error ε_t of the best stump under the current example weights, computes α_t from the closed-form formula on the previous slides, and updates every example's weight before the next round's stump is fit. cross_val_score(ada, X, y, cv=5) wraps the whole 100-round boosting procedure inside 5-fold cross-validation, refitting all 100 rounds from scratch on each of the 5 training folds — this is computationally more expensive than cross-validating a single tree, but it is the statistically valid way to estimate how well this AdaBoost configuration generalizes, since evaluating on the same data used to fit would optimistically overstate performance.

Live-demo note: run this against a random forest of comparable size on the same X, y and compare cross_val_score means — on many tabular datasets AdaBoost with stumps is competitive with, though rarely dramatically better than, a random forest; the goal of the comparison is not to crown a winner but to make the bias/variance tradeoff between the two families tangible with real numbers.
-->

---
glowSeed: 645
---

# Gradient Boosting Fits What Is Still Wrong

<div class="grid grid-cols-2 gap-8 items-start">
<div>
<div class="space-y-3 mt-4">
<div v-click border="2 solid white/5" bg="white/5" rounded-lg px-4 py-3>
<span class="font-bold text-teal-300">General loss</span>
<span class="text-sm opacity-85"> — Fit each new learner to the negative gradient of the current loss.</span>
</div>
<div v-click border="2 solid white/5" bg="white/5" rounded-lg px-4 py-3>
<span class="font-bold text-blue-300">Squared error</span>
<span class="text-sm opacity-85"> — The negative gradient is simply the residual y − F(x).</span>
</div>
<div v-click border="2 solid white/5" bg="white/5" rounded-lg px-4 py-3>
<span class="font-bold text-amber-300">Function-space descent</span>
<span class="text-sm opacity-85"> — Add a small learned function instead of moving one parameter vector.</span>
</div>
</div>
</div>
<div>
<div v-click class="mt-4" style="font-size: .9em" border="2 solid teal-800" bg="teal-800/20" rounded-lg px-4 py-3>

$$
\begin{aligned}F_t(x)&=F_{t-1}(x)+\eta h_t(x)\\-\frac{\partial}{\partial F}\frac12(y-F)^2&=y-F\end{aligned}
$$

</div>

</div>
</div>

<!--
Gradient boosting generalizes AdaBoost's core idea — "fit the next learner to whatever is currently wrong" — to any differentiable loss function, not just exponential loss on ±1 labels. The trick is to view the ensemble's running prediction F(x) not as a set of parameters to optimize directly, but as a function that can be updated by adding a small new function to it at each step, and to choose that new function by gradient descent — except the "gradient" is now a gradient with respect to the predictions F(x_i) at each training point, not with respect to a parameter vector. That is why this is called function-space gradient descent: ordinary gradient descent takes a step −η∇L(θ) in parameter space; gradient boosting takes a step in the space of functions, and the "step direction" happens to be well-approximated by fitting a small tree h_t to the negative gradient values at each training point.

Work the squared-error case concretely, since it is the clearest possible instance and the one most students will implement first. With loss ½(y − F)², the derivative with respect to F is −(y − F), so the negative gradient is exactly y − F — the ordinary residual. This is the beautiful special case: "fit the next tree to the negative gradient of squared error" reduces to "fit the next tree to whatever the current ensemble still gets wrong, in the most literal sense" (the leftover residual). For other losses (log loss for classification, quantile loss, Huber loss for robust regression) the negative gradient is a different, loss-specific quantity, but the algorithm's structure — fit a tree to the negative gradient, add it in with a small learning rate — stays identical. That uniformity is gradient boosting's main theoretical advantage over AdaBoost, which is derived specifically for exponential loss.

The update rule F_t(x) = F_{t−1}(x) + η·h_t(x) is worth connecting explicitly to gradient descent as taught in the optimization unit: η here plays exactly the role of the learning rate there, controlling how large a step is taken in the direction the new tree points. Small η means slow, cautious, well-regularized progress that typically needs more rounds to converge; this tradeoff is the subject of the next two slides.
-->

---
glowSeed: 646
---

# A Minimal Gradient-Boosting Loop

<div class="grid grid-cols-2 gap-4 mt-6">
<div v-click border="2 solid teal-800" bg="teal-800/20" rounded-lg p-4>
<div class="font-bold text-teal-300 mb-2">Predict</div>
<div class="text-sm leading-relaxed opacity-90">Start with a simple running prediction.</div>
</div>
<div v-click border="2 solid blue-800" bg="blue-800/20" rounded-lg p-4>
<div class="font-bold text-blue-300 mb-2">Correct</div>
<div class="text-sm leading-relaxed opacity-90">Fit a shallow tree to residuals.</div>
</div>
</div>

```python
pred = np.zeros(len(y_reg))
trees = []
for _ in range(50):
    residual = y_reg - pred
    tree = DecisionTreeRegressor(max_depth=2)
    tree.fit(X_reg, residual)
    pred += 0.1 * tree.predict(X_reg)
    trees.append(tree)
```

<!--
This loop is gradient boosting for squared-error regression, written out by hand instead of called from GradientBoostingRegressor, specifically so the mechanics from the previous slide are visible line by line. pred starts at all zeros — the crudest possible running prediction, equivalent to F_0(x) = 0. Each of the 50 rounds computes residual = y_reg − pred, which, per the previous slide's derivation, is exactly the negative gradient of squared error; fits a shallow regression tree (max_depth=2, deliberately weak — a depth-2 tree is still close to the "weak learner" spirit even though gradient boosting's theory does not strictly require weakness the way AdaBoost's does) to predict that residual from the features; then updates the running prediction by adding 0.1 times that tree's output — the 0.1 is the learning rate η, and shrinking the tree's contribution before adding it in is what keeps any single round from overcorrecting.

Live-demo instruction: after running this, plot pred against y_reg at rounds 1, 10, 25, and 50 (or compute mean squared error at each checkpoint) so students can watch the running prediction visibly tighten around the true y_reg values as rounds accumulate — this is the residual-correction story made visible rather than asserted. Point out that trees is being kept explicitly (rather than discarded after each round) because the final prediction function is the sum of the initial zero prediction plus 0.1 times every tree's output added together — reproducing a prediction on new data means running every one of the 50 trees and summing, not just using the last one.

Note for students reading this as a template for their own code: a production implementation (and scikit-learn's own GradientBoostingRegressor) adds early stopping, per-round loss tracking, and validation-based tuning of both the learning rate and the number of rounds — this loop is intentionally the minimal version that isolates the core update rule.
-->

---
glowSeed: 647
---

# Learning Rate and Number of Rounds

<div class="grid grid-cols-2 gap-8 items-start">
<div>
<div class="space-y-3 mt-4">
<div v-click border="2 solid white/5" bg="white/5" rounded-lg px-4 py-3>
<span class="font-bold text-teal-300">Small η</span>
<span class="text-sm opacity-85"> — Slower, finer corrections; usually needs more estimators.</span>
</div>
<div v-click border="2 solid white/5" bg="white/5" rounded-lg px-4 py-3>
<span class="font-bold text-blue-300">Large η</span>
<span class="text-sm opacity-85"> — Fast progress but greater risk of chasing noise.</span>
</div>
<div v-click border="2 solid white/5" bg="white/5" rounded-lg px-4 py-3>
<span class="font-bold text-amber-300">Unlike bagging</span>
<span class="text-sm opacity-85"> — Too many boosting rounds can overfit.</span>
</div>
</div>
</div>
<div>
<svg role="img" aria-label="Training error decreasing monotonically while validation error decreases then rises, showing overfitting past the optimal round count" viewBox="0 0 500 310" class="w-full max-w-xl mx-auto mt-7">
  <line x1="55" y1="260" x2="470" y2="260" stroke="#64748b" stroke-width="2"/>
  <line x1="55" y1="35" x2="55" y2="260" stroke="#64748b" stroke-width="2"/>
  <polyline points="65,63 163,159 261,221 359,249 457,257" fill="none" stroke="#2dd4bf" stroke-width="4"/>
  <polyline points="65,80 163,148 261,176 359,153 457,91" fill="none" stroke="#60a5fa" stroke-width="4" stroke-dasharray="9 7"/>
  <g fill="#2dd4bf"><circle cx="65" cy="63" r="5"/><circle cx="163" cy="159" r="5"/><circle cx="261" cy="221" r="5"/><circle cx="359" cy="249" r="5"/><circle cx="457" cy="257" r="5"/></g>
  <g fill="#60a5fa"><circle cx="65" cy="80" r="5"/><circle cx="163" cy="148" r="5"/><circle cx="261" cy="176" r="5"/><circle cx="359" cy="153" r="5"/><circle cx="457" cy="91" r="5"/></g>
  <line x1="261" y1="35" x2="261" y2="260" stroke="#f59e0b" stroke-width="2" stroke-dasharray="4 4"/>
  <g fill="#cbd5e1" style="font-size: 12px" text-anchor="middle"><text x="65" y="285">20</text><text x="163" y="285">50</text><text x="261" y="285">100</text><text x="359" y="285">200</text><text x="457" y="285">400</text></g>
  <text x="260" y="300" fill="#fbbf24" style="font-size: 12px" text-anchor="middle">n_estimators</text>
  <g style="font-size: 12px"><text x="335" y="42" fill="#5eead4">train error</text><text x="335" y="60" fill="#93c5fd">validation error</text></g>
</svg>

</div>
</div>

<!--
This chart is the concrete evidence behind the three cards, and it is worth reading as a genuine diagnostic plot rather than decoration — this is the classic learning-curve overfitting pattern for boosting. The teal training-error curve falls steadily and keeps falling as n_estimators grows from 20 to 400: with a small learning rate, each additional round fits more of the residual, so training error can in principle be driven arbitrarily close to zero if you add enough rounds — boosting has essentially unlimited capacity to memorize the training set given enough estimators. The blue dashed validation-error curve tells a different story: it falls alongside training error at first (rounds 20 to 100), because early rounds are fixing genuine, generalizable signal, but then it turns and rises again from round 100 onward, because later rounds increasingly fit noise specific to the training set rather than real structure. The amber dashed vertical line marks that turning point — the number of rounds that minimizes validation error, and therefore the point early stopping should target.

This is precisely the sense in which n_estimators is an active tuning choice for boosting, and it draws the sharpest possible contrast with the previous deck: adding more bagged trees essentially never hurts generalization (the variance floor from correlated errors is the only limit, and it's approached from above, never crossed), so n_estimators in a random forest is "more is fine, with diminishing returns." Adding more boosting rounds can actively hurt generalization past some point, because boosting has no mechanism analogous to averaging-away noise — it is actively, greedily chasing whatever residual remains, including the part of the residual that is just sampling noise in this particular training set. Small η (top-left card) trades speed for safety: finer corrections per round mean the validation-error upturn happens later and is gentler, which is why learning rate and number of rounds are always tuned together, typically via a validation curve exactly like this one or via early stopping with a held-out validation split.
-->

---
glowSeed: 648
---

# Bagging vs. Boosting

<div class="grid grid-cols-3 gap-4 mt-6">
<div v-click border="2 solid teal-800" bg="teal-800/20" rounded-lg p-4>
<div class="font-bold text-teal-300 mb-2">Bagging</div>
<div class="text-sm leading-relaxed opacity-90">Parallel deep trees; bootstrap diversity; primarily reduces variance.</div>
</div>
<div v-click border="2 solid blue-800" bg="blue-800/20" rounded-lg p-4>
<div class="font-bold text-blue-300 mb-2">Boosting</div>
<div class="text-sm leading-relaxed opacity-90">Sequential shallow trees; corrective updates; primarily reduces bias.</div>
</div>
<div v-click border="2 solid amber-800" bg="amber-800/20" rounded-lg p-4>
<div class="font-bold text-amber-300 mb-2">Practical reality</div>
<div class="text-sm leading-relaxed opacity-90">Gradient-boosted trees are exceptionally strong on structured data.</div>
</div>
</div>


<!--
Make students articulate why deep versus shallow base learners fit each strategy, rather than just reading the cards. Bagging needs its base learner to already have low bias and high variance, because its entire value proposition is variance cancellation through averaging independent-ish fits — start from a deep tree (low bias, high variance) and average away the instability, and you're left with something close to the tree's best-case accuracy but far more stable. Boosting needs the opposite: a base learner that is stable and simple (a stump or a very shallow tree — high bias, low variance) because its value proposition is sequential bias reduction — averaging many identical stumps wouldn't fix anything (there's no variance to cancel and no correction mechanism), but adding many stumps together, each targeted at the current residual, drives bias down round by round. Using a deep tree as boosting's base learner is a common mistake: a sufficiently deep tree can nearly zero out the residual in one round, leaving nothing for subsequent rounds to correct and inviting severe overfitting almost immediately — one reason gradient boosting implementations default to shallow trees (often depth 3–6, sometimes even depth 1 stumps).

The "practical reality" card deserves an honest caveat: gradient-boosted trees (XGBoost, LightGBM, CatBoost, and scikit-learn's own HistGradientBoosting variants) are frequently the strongest off-the-shelf method on structured/tabular data in practice, often outperforming random forests and usually outperforming plain AdaBoost — but "exceptionally strong" comes with a cost: boosting requires more careful tuning (learning rate, number of rounds, tree depth, regularization) than a random forest, which is comparatively forgiving of its main hyperparameter (more trees rarely hurts). A random forest with default-ish settings is a very reasonable first baseline; a well-tuned gradient boosting model is often the thing that wins the competition, but "well-tuned" is doing real work in that sentence.
-->

---
glowSeed: 649
---

# Boosting in One View

<div class="mt-8"><div class="grid grid-cols-3 gap-4 mt-6">
<div v-click border="2 solid teal-800" bg="teal-800/20" rounded-lg p-4>
<div class="font-bold text-teal-300 mb-2">AdaBoost</div>
<div class="text-sm leading-relaxed opacity-90">Reweight hard examples.</div>
</div>
<div v-click border="2 solid blue-800" bg="blue-800/20" rounded-lg p-4>
<div class="font-bold text-blue-300 mb-2">Gradient boosting</div>
<div class="text-sm leading-relaxed opacity-90">Fit negative gradients.</div>
</div>
<div v-click border="2 solid amber-800" bg="amber-800/20" rounded-lg p-4>
<div class="font-bold text-amber-300 mb-2">Tune</div>
<div class="text-sm leading-relaxed opacity-90">Balance η against rounds.</div>
</div>
</div></div>

<div v-click class="mt-10 text-center text-lg" border="2 solid white/10" bg="white/5" rounded-lg px-6 py-4>Next: a formal explanation of why diverse ensembles work.</div>

<!--
Emphasize sequential correction as the unifying idea across both algorithms covered today: AdaBoost implements it by reweighting examples (derived in full — exponential loss, α_t = ½ln[(1−ε_t)/ε_t], multiplicative weight updates, renormalization by Z_t), and gradient boosting implements the same underlying idea — fit the next learner to what's currently wrong — far more generally, by fitting each new tree to the negative gradient of an arbitrary differentiable loss function, which specializes to plain residual-fitting for squared error. Both are additive models built one weak piece at a time; the difference is entirely in how "what's currently wrong" gets translated into a target for the next learner.

The practical takeaway to leave on the board: boosting's power comes with a tuning responsibility bagging mostly doesn't have — the learning rate and number of rounds must be balanced against each other and validated, because unlike adding more bagged trees, adding more boosting rounds can make test performance worse, not just plateau.

Transition to the final deck of this unit: everything covered in both decks so far has been a specific recipe — bootstrap-and-average, or sequential-reweight-and-combine — without formally justifying why combining models helps at all, or precisely how much it helps as a function of how similar the models' errors are to each other. "Why Ensembles Work" makes that argument rigorous: it derives the variance-of-an-average formula in terms of pairwise correlation ρ, explains why that formula sets a hard floor on how much bagging and random forests can help, reframes both bagging and boosting through a single bias–variance lens, and states plainly what ensembling cannot fix — irreducible noise, latency, and interpretability. Take questions on the alpha derivation or the gradient-boosting update before moving on, since both are frequently revisited in later units on gradient-based methods.
-->
