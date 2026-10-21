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
Bagging and random forests attacked variance: many deep trees, trained independently, averaged. This deck attacks the other term, bias. Boosting starts from a learner that is too simple, usually a one-split stump, and builds members one at a time, each aimed at what the ensemble so far still gets wrong. The members are added, not averaged.

Roadmap: why averaging cannot fix bias → the boosting idea, on the price example from Why Ensembles Work → gradient boosting by hand, round by round, on the same sine data as the bagging deck → overfitting and the learning rate → why it is called "gradient" boosting, and how the loss sets the target → AdaBoost, round by round, and where its formulas come from → AdaBoost as gradient boosting with exponential loss → tuning on the California data → a final comparison of every method in the unit.

Color code, continued from the bagging deck: amber is a single tree or stump, blue is bagging, teal is a random forest, violet is a boosted ensemble, dashed white is the truth, and red marks residuals and mistakes. Every number on these slides comes from scripts/make_data.py in the deck folder, run with fixed seeds.
-->

---
glowSeed: 641
---

# Where We Left Off: Averaging Cannot Fix Bias

<div class="grid grid-cols-[3fr_2fr] gap-8 items-start">
<div>
<FitPlot :curves="[{ key: 'stump', color: '#fbbf24' }, { key: 'bagStumps', color: '#60a5fa' }]" :legend="[{ label: 'one stump', color: '#fbbf24' }, { label: '50 bagged stumps', color: '#60a5fa' }]" title="Same 50 points as the bagging deck" title-color="#e2e8f0" />
</div>
<div class="space-y-3 mt-2">
<div v-click border="2 solid white/5" bg="white/5" rounded-lg px-4 py-3>
<span class="font-bold text-amber-300">A stump is too simple</span>
<span class="text-sm opacity-85"> — One split, two flat pieces. It can't bend to follow a sine wave.</span>
</div>
<div v-click border="2 solid white/5" bg="white/5" rounded-lg px-4 py-3>
<span class="font-bold text-blue-300">Bagging smooths it, but it still misses</span>
<span class="text-sm opacity-85"> — Over 200 datasets: bias² 0.074 → 0.071, variance 0.037 → 0.020.</span>
</div>
<div v-click border="2 solid amber-800" bg="amber-800/20" rounded-lg px-4 py-3>
<span class="font-bold text-amber-300">Today's question:</span>
<span class="text-sm opacity-85"> how do we combine weak learners so that bias goes down?</span>
</div>
</div>
</div>

<!--
Recall the bias slide from Why Ensembles Work: when members are identically trained, the average has the same bias as each member. Bagging is exactly that kind of average, so it only helps when the base learner's problem is variance.

Here is what happens when it isn't. Same 50 noisy sine points as the bagging deck. One stump (amber) makes a single cut and predicts a flat value on each side. Bagging 50 stumps (blue) smooths the jump, because different bootstrap samples put the cut in slightly different places, but the result is still essentially one step. It cannot represent a curve that goes up, then down, then up.

The numbers in the second card come from repeating the experiment on 200 fresh datasets of 50 points: bias squared barely moves, 0.074 to 0.071, while variance roughly halves. Bagging did its job, but its job was the wrong one. We will come back to these exact measurements at the end of the deck.
-->

---
glowSeed: 642
---

# Add, Don't Average

<div class="grid grid-cols-2 gap-8 items-start">
<div>
<Waterfall />
</div>
<div class="space-y-3 mt-2">
<div v-click border="2 solid white/5" bg="white/5" rounded-lg px-4 py-3>
<span class="font-bold text-amber-300">Each member fits what's left over</span>
<span class="text-sm opacity-85"> — Stump 2 never sees the price. It sees the leftover 50.</span>
</div>
<div v-click border="2 solid white/5" bg="white/5" rounded-lg px-4 py-3>
<span class="font-bold text-violet-300">Members are summed</span>
<span class="text-sm opacity-85"> — The prediction is the running total.</span>
</div>
<div v-click border="2 solid white/5" bg="white/5" rounded-lg px-4 py-3>
<span class="font-bold text-teal-300">Not identically trained</span>
<span class="text-sm opacity-85"> — Each member depends on the ones before, so the averaging argument no longer applies, and bias can fall.</span>
</div>
<div v-click class="mt-2" style="font-size: .85em" border="2 solid violet-800" bg="violet-800/20" rounded-lg px-4 py-1>

$$
F_M(x)=h_1(x)+h_2(x)+\cdots+h_M(x)
$$

</div>
</div>
</div>

<!--
This is the example previewed in Why Ensembles Work. A house sells for 300. The first stump predicts 250. The second stump is not trained on the price at all; it is trained on what is left over, 300 − 250 = 50, and predicts +40. The third is trained on the new leftover, 10, and predicts +8. The running total goes 250, 290, 298.

Two differences from bagging. First, the members are added, not averaged: each one is a correction, measured in the same units as the target. Second, they are built in sequence, each depending on the ones before. That breaks the "identically trained" condition from the bias slide, which is exactly why the bias can fall.

The formula is the whole model: F sub M is a sum of M small functions. Everything else in this deck is about how to choose each h, and how big a step to take with it.
-->

---
glowSeed: 643
---

# Fit the Residuals, Round by Round

<div class="text-sm opacity-85 mt-1">Start from the average of y. Each round, fit a stump to the residuals, then add it to the fit.</div>

<div class="grid grid-cols-3 gap-5 mt-3">
<div v-click><ResidualPanel :t="0" /></div>
<div v-click><ResidualPanel :t="1" /></div>
<div v-click><ResidualPanel :t="2" /></div>
</div>

<div v-click class="mt-3 text-sm text-center" border="2 solid white/5" bg="white/5" rounded-lg px-4 py-2>
Top: the fit so far <span class="text-violet-300 font-bold">F</span>. Bottom: what it still gets wrong, <span class="text-red-300 font-bold">y − F</span>, and the <span class="text-amber-300 font-bold">stump</span> fit to it. Adding that stump gives the next panel's <span class="text-violet-300 font-bold">F</span>.
</div>

<!--
Gradient boosting for regression, done by hand on the 50 sine points. Read each column top to bottom, then move right.

Column 1. The starting fit F zero is a flat line at the mean of y. Its residuals, bottom panel, are just the data shifted down: the sine wave itself. A stump fit to those residuals splits at x = 0.46: positive on the left, negative on the right. Training MSE starts at 0.595.

Column 2. Adding that stump gives a fit with one step. Training MSE drops to 0.208. The new residuals are smaller, and they have structure the first stump missed: the left edge, where the sine is still near zero, is now over-predicted. The second stump splits at x = 0.14 and pulls that region down.

Column 3. After two stumps, MSE is 0.168. The third stump finds the next biggest leftover pattern, around x = 0.68.

Each stump on its own is a terrible model of y. But each one is a good model of what is still wrong, and that is all it needs to be. These stumps keep at least 5 points on each side of the split, so no round is spent chasing a single point.
-->

---
glowSeed: 644
---

# The Ensemble Takes Shape

<div class="grid grid-cols-4 gap-3 mt-4">
<div v-click><FitPlot :curves="[{ key: 'snaps.1', color: '#a78bfa' }]" title="M = 1" :note="`train MSE 0.208`" :w="300" :h="300" /></div>
<div v-click><FitPlot :curves="[{ key: 'snaps.3', color: '#a78bfa' }]" title="M = 3" :note="`train MSE 0.148`" :w="300" :h="300" /></div>
<div v-click><FitPlot :curves="[{ key: 'snaps.20', color: '#a78bfa' }]" title="M = 20" :note="`train MSE 0.087`" :w="300" :h="300" /></div>
<div v-click><FitPlot :curves="[{ key: 'snaps.1000', color: '#a78bfa' }]" title="M = 1000" :note="`train MSE 0.027`" :w="300" :h="300" /></div>
</div>

<div class="grid grid-cols-2 gap-4 mt-5">
<div v-click border="2 solid white/5" bg="white/5" rounded-lg px-4 py-3>
<span class="font-bold text-violet-300">Bias falls round by round</span>
<span class="text-sm opacity-85"> — By 20 stumps the step function traces the sine wave.</span>
</div>
<div v-click border="2 solid white/5" bg="white/5" rounded-lg px-4 py-3>
<span class="font-bold text-red-300">Then it keeps going</span>
<span class="text-sm opacity-85"> — By 1000 stumps it is fitting the noise. Nothing in the loop says stop.</span>
</div>
</div>

<!--
The same procedure, run for longer. Each panel is the fit after M stumps, with the dashed truth for reference. Learning rate is still 1: each stump is added at full size.

M = 1 is the single step from the last slide. By M = 3 there is a rough up-down shape. By M = 20 the sum of 20 stumps is a staircase that follows the sine wave well. That is bias reduction you can see: no single member can bend, but their sum can.

Now the warning. The loop never runs out of residuals, because the data contain noise and the noise is always "left over". By M = 1000 training MSE is 0.027, well below the noise variance of 0.09, which is only possible by memorizing noise. The staircase now has spikes toward individual points. Next slide: what that does to test error.
-->

---
glowSeed: 645
---

# More Rounds Can Hurt

<div class="grid grid-cols-[3fr_2fr] gap-8 items-start">
<div>
<RoundsChart src="oned" :keys="['1.0']" train />
</div>
<div class="space-y-3 mt-2">
<div v-click border="2 solid white/5" bg="white/5" rounded-lg px-4 py-3>
<span class="font-bold text-red-300">Training error only falls</span>
<span class="text-sm opacity-85"> — Every round fits more of what's left, signal or noise.</span>
</div>
<div v-click border="2 solid white/5" bg="white/5" rounded-lg px-4 py-3>
<span class="font-bold text-red-300">Test error turns around</span>
<span class="text-sm opacity-85"> — Lowest at M = 20 (0.160), then up to 0.237 at M = 1000.</span>
</div>
<div v-click border="2 solid amber-800" bg="amber-800/20" rounded-lg px-4 py-3>
<span class="font-bold text-amber-300">Unlike bagging,</span>
<span class="text-sm opacity-85"> the number of members is a knob that overfits. Choose it on held-out data.</span>
</div>
</div>
</div>

<!--
Same model as the last slide, stumps with learning rate 1, now scored on 5,000 fresh points from the same sine-plus-noise process. The x-axis is the number of rounds on a log scale. Solid is test error; dashed is training error. The gray dashed line is the noise variance, 0.09: no model can have expected test MSE below it.

Training error falls the whole way. Test error falls quickly at first, while the stumps are capturing the sine wave, bottoms out at 0.160 after 20 rounds, and then rises to 0.237 by round 1000 as the later stumps fit noise.

This is the promise from the bagging deck. Adding trees to a random forest cannot overfit, because the trees are independent draws and the average converges. Boosting rounds are not independent draws; each one is fit to the training residuals, so more of them means a closer fit to this particular training set. The number of rounds is a capacity knob, like polynomial degree, and must be chosen on held-out data.
-->

---
glowSeed: 646
---

# Shrinkage: Take Smaller Steps

<div class="grid grid-cols-[3fr_2fr] gap-8 items-start">
<div>
<RoundsChart src="oned" :keys="['1.0', '0.3', '0.1']" />
</div>
<div>
<div class="mt-1" style="font-size: .85em" border="2 solid violet-800" bg="violet-800/20" rounded-lg px-4 py-1>

$$
F_m(x)=F_{m-1}(x)+\eta\,h_m(x),\qquad 0<\eta\le1
$$

</div>
<div class="space-y-3 mt-3">
<div v-click border="2 solid white/5" bg="white/5" rounded-lg px-4 py-3>
<span class="font-bold text-violet-300">Add only part of each stump</span>
<span class="text-sm opacity-85"> — Later rounds get a chance to correct earlier ones.</span>
</div>
<div v-click border="2 solid white/5" bg="white/5" rounded-lg px-4 py-3>
<span class="font-bold text-violet-300">Slower, but safer</span>
<span class="text-sm opacity-85"> — η = 0.1 needs 156 rounds instead of 20, and rises only to 0.156 by M = 1000.</span>
</div>
<div v-click border="2 solid white/5" bg="white/5" rounded-lg px-4 py-3>
<span class="font-bold text-amber-300">Tune η and M together</span>
<span class="text-sm opacity-85"> — Smaller η, more rounds.</span>
</div>
</div>
</div>
</div>

<!--
The fix is the same idea as the learning rate in gradient descent: don't take the full step. Multiply each new stump by eta before adding it. With eta = 0.1, a stump that would correct a residual of 0.5 only corrects 0.05 this round, and the remaining 0.45 is left for later stumps to handle, possibly with a better split.

Read the three curves, all on the same data. Eta = 1 (red) is the curve from the last slide. Eta = 0.3 (orange) reaches its best test error, 0.140, at 39 rounds. Eta = 0.1 (violet) reaches the same 0.140 but needs 156 rounds. The payoff is the shape after the minimum: the curve is much flatter, so missing the best M by a factor of two or three costs almost nothing. At 1000 rounds, eta = 0.1 is at 0.156; eta = 1 is at 0.237.

On this small toy problem the smaller learning rate buys robustness more than a lower minimum. On the California data later in the deck it buys both. The practical rule: pick a small eta, then choose M on held-out data. Smaller eta always means more rounds, so the two are tuned together.
-->

---
glowSeed: 647
---

# Gradient Boosting in a Few Lines

<div class="grid grid-cols-[3fr_2fr] gap-6 items-start mt-2">
<div>

```python
eta = 0.1                           # learning rate
F0 = y.mean()                       # start from the average
F = np.full(len(y), F0)
trees = []
for m in range(100):
    residual = y - F                # what is still wrong
    tree = DecisionTreeRegressor(max_depth=1, min_samples_leaf=5)
    tree.fit(X, residual)
    F += eta * tree.predict(X)      # small step
    trees.append(tree)

def predict(X_new):
    return F0 + eta * sum(t.predict(X_new) for t in trees)
```

</div>
<div class="space-y-3">
<div v-click border="2 solid white/5" bg="white/5" rounded-lg px-4 py-3>
<span class="font-bold text-violet-300">Keep every tree</span>
<span class="text-sm opacity-85"> — The model is F₀ plus all M scaled trees, not the last one.</span>
</div>
<div v-click border="2 solid white/5" bg="white/5" rounded-lg px-4 py-3>
<span class="font-bold text-teal-300">The same model in scikit-learn</span>
<span class="text-sm opacity-85"> — <code>GradientBoostingRegressor</code> with the same η, rounds, depth and leaf size gives identical predictions.</span>
</div>
<div v-click border="2 solid white/5" bg="white/5" rounded-lg px-4 py-3>
<span class="font-bold text-amber-300">Sequential</span>
<span class="text-sm opacity-85"> — Tree m needs F from tree m − 1, so rounds can't run in parallel.</span>
</div>
</div>
</div>

<!--
This is the whole algorithm for squared error, and every slide so far is this loop. Start from the mean, the best constant prediction under squared error; scikit-learn does the same. Each round: compute residuals, fit a small tree to them, add eta times its predictions to the running fit, and keep the tree.

The predict function is the point students most often miss. The fitted model is not the last tree; it is F zero plus eta times the sum of every tree. To predict on new data you run all M trees and add them up.

The middle card is checked: run with the same settings, this loop and scikit-learn's GradientBoostingRegressor produce the same predictions at every round. Compare with the bagging deck's n_jobs=-1: bagged trees are independent, so they train in parallel. Boosting rounds cannot, because each needs the residuals left by the one before. Modern libraries parallelize within a round, when searching for splits, instead.
-->

---
glowSeed: 648
---

# Why Is It Called Gradient Boosting?

<div class="grid grid-cols-2 gap-8 items-start">
<div>
<div class="mt-1" style="font-size: .8em" border="2 solid white/5" bg="white/5" rounded-lg px-4 py-1>

$$
\begin{aligned}
\text{Gradient descent:}\quad \theta &\leftarrow \theta-\eta\,\nabla_\theta L\\
\text{Boosting:}\quad F(x_i) &\leftarrow F(x_i)-\eta\,\frac{\partial L}{\partial F(x_i)}
\end{aligned}
$$

</div>
<div class="space-y-3 mt-3">
<div v-click border="2 solid white/5" bg="white/5" rounded-lg px-4 py-3>
<span class="font-bold text-red-300">The arrows are the negative gradient</span>
<span class="text-sm opacity-85"> — For ½(y − F)², −∂L/∂F = y − F: the residual.</span>
</div>
<div v-click border="2 solid white/5" bg="white/5" rounded-lg px-4 py-3>
<span class="font-bold text-amber-300">The tree generalizes the arrows</span>
<span class="text-sm opacity-85"> — Arrows exist only at training points. A tree fit to them gives a step at any x.</span>
</div>
<div v-click border="2 solid white/5" bg="white/5" rounded-lg px-4 py-3>
<span class="font-bold text-violet-300">Descent in function space</span>
<span class="text-sm opacity-85"> — Each round moves the predictions downhill on the loss.</span>
</div>
</div>
</div>
<div>
<FitPlot :curves="[{ key: 'rounds.1.Fg', color: '#a78bfa' }]" :arrows="1" :truth="false" title="F after one stump, and the arrows y − F" />
</div>
</div>

<!--
Connect this to gradient descent from the optimization unit. There, we had parameters theta and moved them a small step against the gradient of the loss. Here, think of the n training predictions F of x one through F of x n as the things we are optimizing. The loss is a sum over points, so its gradient with respect to F of x i involves only point i. For squared loss, one half y minus F squared, the derivative is minus y minus F, so the negative gradient is the residual. The red arrows in the plot are those negative gradients: at each point, the direction and size of the change that would reduce the loss.

We can't just move each prediction independently, because then we would have a model only of the training points. Instead we fit a tree to the arrows. The tree is a function of x, so it says how to move the prediction anywhere, including at new inputs, and it is forced to move nearby points together, which is what generalizes. Adding eta times the tree is one step of gradient descent, taken in the space of functions rather than parameters.

Why this framing matters: nothing here was special to squared loss. Replace the loss and the arrows change, but the loop doesn't. That is the next slide.
-->

---
glowSeed: 649
---

# Choose a Loss, Get a Target

<div class="grid grid-cols-2 gap-8 items-start">
<div>

<div class="text-sm">

| Loss | Each tree is fit to | Typical use |
|---|---|---|
| Squared, ½(y − F)² | y − F | regression |
| Absolute, \|y − F\| | sign(y − F) | regression with outliers |
| Log loss | y − p, where p = σ(F) | classification |
| Exponential, e<sup>−yF</sup> | reweighted labels | AdaBoost |

</div>

<div v-click class="mt-4" border="2 solid white/5" bg="white/5" rounded-lg px-4 py-3>
<span class="font-bold text-pink-300">Absolute loss caps each point's pull</span>
<span class="text-sm opacity-85"> — A residual of 3 and a residual of 0.3 both send an arrow of size 1.</span>
</div>
</div>
<div>
<FitPlot robust legend-pos="tr" :curves="[{ key: 'squared_error', color: '#a78bfa' }, { key: 'absolute_error', color: '#f472b6' }]" :legend="[{ label: 'squared loss: MSE vs truth 0.219', color: '#a78bfa' }, { label: 'absolute loss: MSE vs truth 0.050', color: '#f472b6' }]" title="Three labels corrupted" title-color="#fca5a5" />
</div>
</div>

<!--
The loop from two slides ago works for any differentiable loss. Only the target of each tree changes, and it is always the negative gradient, often called the pseudo-residual.

Squared loss gives the ordinary residual. Absolute loss gives only the sign of the residual: every point pulls with the same strength, however far off it is. Log loss for classification works on the log-odds scale: F is a score, p equals sigma of F is the predicted probability, and the negative gradient is y minus p, the gap between the 0/1 label and the predicted probability. That is what GradientBoostingClassifier fits. Exponential loss gives AdaBoost; we derive that in the next section.

The plot shows why the choice matters. Same 50 points, but three labels have been corrupted (red rings). With squared loss (violet), those three points have huge residuals, and since squared loss weights a residual by its size, several rounds get spent chasing them: the fit spikes toward the outliers. With absolute loss (pink), each outlier pulls no harder than any other point, and the fit stays close to the sine wave. Measured against the true curve, the MSE is 0.219 for squared loss and 0.050 for absolute loss. Huber loss is a compromise: squared for small residuals, absolute for large ones.
-->

---
glowSeed: 650
---

# AdaBoost: Reweight Instead of Refit

<div class="grid grid-cols-2 gap-8 items-start">
<div class="mt-2" role="img" aria-label="AdaBoost loop: equal weights, fit a stump, measure weighted error, compute its vote, upweight mistakes, repeat">
<div v-click class="flex items-center gap-3">
<div class="w-8 h-8 rounded-full bg-teal-500/20 border-2 border-teal-700 flex items-center justify-center text-sm font-bold">1</div>
<div class="flex-1 rounded-lg border-2 border-white/10 bg-white/5 px-3 py-2 text-sm"><b>Equal weights</b> on every example, wᵢ = 1/n</div>
</div>
<div class="ml-4 h-2 border-l-2 border-teal-400/50"></div>
<div v-click class="flex items-center gap-3">
<div class="w-8 h-8 rounded-full bg-amber-500/20 border-2 border-amber-700 flex items-center justify-center text-sm font-bold">2</div>
<div class="flex-1 rounded-lg border-2 border-white/10 bg-white/5 px-3 py-2 text-sm"><b>Fit a stump</b> hₜ to the weighted data</div>
</div>
<div class="ml-4 h-2 border-l-2 border-teal-400/50"></div>
<div v-click class="flex items-center gap-3">
<div class="w-8 h-8 rounded-full bg-red-500/20 border-2 border-red-700 flex items-center justify-center text-sm font-bold">3</div>
<div class="flex-1 rounded-lg border-2 border-white/10 bg-white/5 px-3 py-2 text-sm"><b>Weighted error</b> εₜ = total weight it gets wrong</div>
</div>
<div class="ml-4 h-2 border-l-2 border-teal-400/50"></div>
<div v-click class="flex items-center gap-3">
<div class="w-8 h-8 rounded-full bg-violet-500/20 border-2 border-violet-700 flex items-center justify-center text-sm font-bold">4</div>
<div class="flex-1 rounded-lg border-2 border-white/10 bg-white/5 px-3 py-2 text-sm"><b>Its vote</b> <span class="greek">α</span>ₜ: larger when εₜ is smaller</div>
</div>
<div class="ml-4 h-2 border-l-2 border-teal-400/50"></div>
<div v-click class="flex items-center gap-3">
<div class="w-8 h-8 rounded-full bg-blue-500/20 border-2 border-blue-700 flex items-center justify-center text-sm font-bold">5</div>
<div class="flex-1 rounded-lg border-2 border-white/10 bg-white/5 px-3 py-2 text-sm"><b>Reweight:</b> mistakes up, correct down. Back to 2.</div>
</div>
</div>
<div>
<div v-click class="mt-2" style="font-size: .8em" border="2 solid violet-800" bg="violet-800/20" rounded-lg px-4 py-1>

$$
\begin{aligned}
\alpha_t&=\tfrac12\ln\frac{1-\epsilon_t}{\epsilon_t}\\[2pt]
w_i&\leftarrow \frac{w_i\,e^{-\alpha_t y_i h_t(x_i)}}{Z_t}\\[2pt]
H(x)&=\operatorname{sign}\Big(\sum_t \alpha_t h_t(x)\Big)
\end{aligned}
$$

</div>
<div v-click class="mt-3 text-sm" border="2 solid white/5" bg="white/5" rounded-lg px-4 py-3>
Labels and stump outputs are ±1, so yᵢhₜ(xᵢ) = +1 when correct and −1 when wrong. Z<sub>t</sub> rescales the weights to sum to 1.
</div>
</div>
</div>

<!--
AdaBoost, from 1995, is the original practical boosting algorithm, and it came before the gradient view. It is built for binary classification, and instead of fitting residuals, it changes how much each training example counts.

Walk the loop. Every example starts with equal weight. Fit a stump that minimizes weighted error, so heavily weighted examples matter more when choosing the split. Its weighted error epsilon t is the total weight of the examples it gets wrong. From epsilon, compute the stump's vote, alpha t. Then reweight: multiply each wrong example's weight by e to the alpha, each correct one's by e to the minus alpha, and rescale so the weights sum to 1. The next stump is fit to the new weights, so it is pushed toward the examples the ensemble so far finds hard.

The final classifier is a weighted vote: the sign of the sum of alpha t times h t. The labels-in-plus-or-minus-one convention is what makes the update formula compact: y i times h t of x i is +1 for a correct prediction and −1 for a mistake. Next slide: three rounds of this on 12 points.
-->

---
glowSeed: 651
---

# AdaBoost, Round by Round

<div class="text-sm opacity-85 mt-1">12 points, two classes. Dot area = example weight. Red ring = this round's stump gets it wrong.</div>

<div class="grid grid-cols-4 gap-4 mt-3">
<div v-click><AdaPanel :round="0" /></div>
<div v-click><AdaPanel :round="1" /></div>
<div v-click><AdaPanel :round="2" /></div>
<div v-click><AdaPanel /></div>
</div>

<div class="grid grid-cols-2 gap-4 mt-3">
<div v-click border="2 solid white/5" bg="white/5" rounded-lg px-4 py-2>
<span class="font-bold text-red-300">Mistakes grow</span>
<span class="text-sm opacity-85"> — After round 1, its 3 mistakes weigh 1/6 each and the rest 1/18. The mistakes now hold half the weight.</span>
</div>
<div v-click border="2 solid white/5" bg="white/5" rounded-lg px-4 py-2>
<span class="font-bold text-violet-300">No stump is right, the vote is</span>
<span class="text-sm opacity-85"> — Each stump misses 3 to 6 points. The weighted vote classifies all 12 correctly.</span>
</div>
</div>

<!--
Three rounds of AdaBoost on 12 points, computed exactly. Amber is class +1, blue is class −1. The tinted halves show what each stump predicts; the dashed white line is its split.

Round 1. All weights are 1/12. The best stump splits on the horizontal axis at 0.45: amber on the left, blue on the right. It misses three amber points in the lower right. Weighted error 0.25, so alpha is one half log 3, about 0.55.

Round 2. Those three mistakes have grown, and everything else has shrunk. A useful fact you can check: after reweighting, the previous stump's mistakes always hold exactly half the total weight, so the previous stump is now no better than a coin flip on the new weights. That forces the next stump to be different. The best stump now splits horizontally at 0.185, calling the bottom strip amber, which gets the three heavy points right. It misses three amber points on the left, above the strip; weighted error 0.167, alpha 0.80.

Round 3. The weights shift again. This stump misses six points, half the data, but they are all light, so its weighted error is only 0.2 and alpha is 0.69. Fewer mistakes is not the goal; mistakes on the heavy points are what count.

Final panel: the vote 0.55 h1 + 0.80 h2 + 0.69 h3. None of the three stumps is right everywhere, but their weighted sum classifies all 12 points correctly, with a boundary no single stump could draw.
-->

---
glowSeed: 652
---

# How Much Say Does a Stump Get?

<div class="grid grid-cols-[3fr_2fr] gap-8 items-start">
<div>
<AlphaCurve />
</div>
<div class="space-y-3 mt-2">
<div v-click border="2 solid white/5" bg="white/5" rounded-lg px-4 py-3>
<span class="font-bold text-violet-300">Accurate stumps vote louder</span>
<span class="text-sm opacity-85"> — ε = 0.01 gives <span class="greek">α</span> = 2.30. The example's stumps get 0.55 to 0.80.</span>
</div>
<div v-click border="2 solid white/5" bg="white/5" rounded-lg px-4 py-3>
<span class="font-bold text-red-300">A coin flip gets no vote</span>
<span class="text-sm opacity-85"> — ε = 0.5 gives <span class="greek">α</span> = 0. The weak learner must beat chance, as Why Ensembles Work showed for voting.</span>
</div>
<div v-click border="2 solid white/5" bg="white/5" rounded-lg px-4 py-3>
<span class="font-bold text-blue-300"><span class="greek">α</span> also sets the reweighting</span>
<span class="text-sm opacity-85"> — Round 1: <span class="greek">α</span> = 0.55, so mistakes × e<sup>0.55</sup> = 1.73 and correct × 0.58, before rescaling.</span>
</div>
</div>
</div>

<!--
The formula for alpha, plotted. Small weighted error, large vote: at epsilon 0.01, alpha is about 2.3. The three stumps from the example are the violet dots, all in the useful middle range.

At epsilon one half, alpha is zero. A stump that is right half the time, by weight, carries no information and gets no say. This is the condition from the voting slides in Why Ensembles Work: majority voting helps only when each voter beats chance, and adding worse-than-chance voters makes things worse. AdaBoost builds that requirement into the weights. In the red region the formula gives a negative alpha, which would flip the stump's predictions; in practice the best stump on any round has epsilon at most one half, because flipping a worse-than-chance stump gives a better-than-chance one.

The same alpha drives the reweighting. In round 1, alpha is 0.55: each mistake's weight is multiplied by e to the 0.55, about 1.73, each correct example's by about 0.58, and then everything is rescaled to sum to 1. That turns 1/12 into 1/6 for mistakes and 1/18 for the rest, the numbers on the previous slide.
-->

---
glowSeed: 656
---

# Learning Rate and Rounds on Real Data

<div class="grid grid-cols-[3fr_2fr] gap-8 items-start">
<div>
<RoundsChart src="eta" :keys="['1.0', '0.3', '0.1', '0.03']" />
</div>
<div class="space-y-3 mt-2">
<div v-click border="2 solid white/5" bg="white/5" rounded-lg px-4 py-3>
<span class="font-bold text-red-300">η = 1 overfits fast</span>
<span class="text-sm opacity-85"> — Best 0.396 at 41 rounds, 0.481 by 2000. Worse than the random forest throughout.</span>
</div>
<div v-click border="2 solid white/5" bg="white/5" rounded-lg px-4 py-3>
<span class="font-bold text-violet-300">η = 0.1 gives the lowest error</span>
<span class="text-sm opacity-85"> — 0.282 at 325 rounds, and the curve stays low.</span>
</div>
<div v-click border="2 solid white/5" bg="white/5" rounded-lg px-4 py-3>
<span class="font-bold text-fuchsia-300">Smaller still costs time</span>
<span class="text-sm opacity-85"> — η = 0.03 needs 1,123 rounds to reach 0.284.</span>
</div>
</div>
</div>

<!--
Back to California housing, with the same 2,000 training rows and 2,000 held-out districts as the bagging deck, so the teal reference line is the random forest's 0.310 from there. Each curve is one gradient-boosting fit with depth-3 trees, scikit-learn's default, scored after every round. Dots mark each curve's minimum.

Eta = 1 (red) drops fast, bottoms out at 0.396 after 41 rounds, then climbs to 0.481: full-size steps of depth-3 trees memorize 2,000 rows quickly. It never beats the random forest. Eta = 0.3 does much better, 0.291 at 164 rounds. Eta = 0.1 gives the best result, 0.282 at 325 rounds, and climbs only slowly after that, to 0.297 at 2,000. Eta = 0.03 reaches 0.284 but needs 1,123 rounds to get there.

Unlike the toy example, here the smaller learning rate gives a genuinely lower minimum, not just a flatter curve. The usual recipe: fix eta around 0.05 to 0.1, and let held-out data pick the number of rounds. Going smaller mostly costs training time.
-->

---
glowSeed: 657
---

# Tree Depth Controls Interactions

<div class="grid grid-cols-[3fr_2fr] gap-8 items-start">
<div>
<RoundsChart src="depth" :keys="['1', '3', '6']" />
</div>
<div class="space-y-3 mt-2">
<div v-click border="2 solid white/5" bg="white/5" rounded-lg px-4 py-3>
<span class="font-bold text-amber-300">Stumps build an additive model</span>
<span class="text-sm opacity-85"> — Each stump uses one feature, so the sum is f₁(x₁) + f₂(x₂) + ⋯ with no interactions. Best 0.354.</span>
</div>
<div v-click border="2 solid white/5" bg="white/5" rounded-lg px-4 py-3>
<span class="font-bold text-violet-300">Depth d allows d-way interactions</span>
<span class="text-sm opacity-85"> — Depth 3 reaches 0.282, depth 6 reaches 0.288.</span>
</div>
<div v-click border="2 solid white/5" bg="white/5" rounded-lg px-4 py-3>
<span class="font-bold text-teal-300">Still weak learners</span>
<span class="text-sm opacity-85"> — Shallow, high-bias trees. Boosting supplies the rest.</span>
</div>
</div>
</div>

<!--
The second knob is how big each tree is. Same data, eta = 0.1, three depths.

Stumps (amber) are still improving at 2,000 rounds and get to 0.354, worse than the random forest. The reason is structural. A stump splits on one feature, so a sum of stumps is a sum of one-feature functions: an additive model. It can learn that price rises with income and with being near the coast, but not that the effect of income depends on location. House prices have interactions like that, so stumps carry bias that no number of rounds removes.

A depth-d tree can combine up to d features along a path, so it can represent d-way interactions. Depth 3 reaches 0.282 at 325 rounds. Depth 6 is a little worse, 0.288, and reaches its best sooner: bigger trees fit faster, and overfit faster.

So "weak learner" doesn't have to mean stump. In practice gradient boosting uses trees of depth about 3 to 8: still shallow and high-bias, far from the fully grown trees of the bagging deck.
-->

---
glowSeed: 658
---

# Early Stopping in Practice

<div class="grid grid-cols-[3fr_2fr] gap-6 items-start mt-2">
<div>

```python
from sklearn.ensemble import HistGradientBoostingRegressor

gb = HistGradientBoostingRegressor(
    learning_rate=0.1,
    max_iter=2000,             # an upper limit on rounds
    early_stopping=True,       # 'auto' is off below 10,000 rows
    validation_fraction=0.1,
    n_iter_no_change=10,
    random_state=0,
).fit(X_train, y_train)

print(gb.n_iter_)              # 89 rounds used
mse = ((gb.predict(X_test) - y_test) ** 2).mean()   # 0.269
```

</div>
<div class="space-y-3">
<div v-click border="2 solid white/5" bg="white/5" rounded-lg px-4 py-3>
<span class="font-bold text-violet-300">Let validation pick M</span>
<span class="text-sm opacity-85"> — Hold out 10% of the training rows. Stop after 10 rounds with no improvement.</span>
</div>
<div v-click border="2 solid white/5" bg="white/5" rounded-lg px-4 py-3>
<span class="font-bold text-red-300">No out-of-bag rows</span>
<span class="text-sm opacity-85"> — Every round trains on all the rows, so the validation set has to be carved out.</span>
</div>
<div v-click border="2 solid white/5" bg="white/5" rounded-lg px-4 py-3>
<span class="font-bold text-teal-300">Histogram-based</span>
<span class="text-sm opacity-85"> — Bins each feature into at most 255 values. Much faster on large data.</span>
</div>
</div>
</div>

<!--
In practice, you don't scan a curve by eye; you let the library stop when held-out error stops improving. HistGradientBoostingRegressor is scikit-learn's modern implementation, in the same family as LightGBM. It bins each feature into at most 255 values before training, which makes split-finding very fast.

Set max_iter high as an upper limit. With early_stopping on, it holds out 10% of the training rows, scores them after each round, and stops once 10 rounds in a row fail to improve. Here it stopped at 89 rounds, and test MSE on the 2,000 held-out districts was 0.269.

One trap: the default is early_stopping='auto', which turns early stopping on only above 10,000 rows. With 2,000 rows you must pass True explicitly, or it simply runs max_iter rounds.

The middle card is the promise from the bagging deck. Bagged trees each skip about a third of the rows, which gave us free out-of-bag validation. Boosting fits every round to all the training rows, so nothing is left out; the validation set has to be split off on purpose. Note too that HistGradientBoosting grows trees by number of leaves, 31 by default, rather than by depth, which is part of why its result differs from the depth-3 curve on the last slide.
-->

---
glowSeed: 659
---

# The Scoreboard: California Housing

<div class="grid grid-cols-[3fr_2fr] gap-8 items-start">
<div class="mt-4">
<Scoreboard />
<div class="text-xs opacity-70 mt-2 text-center">Test MSE on 2,000 held-out districts. Same 2,000 training rows for every model.</div>
</div>
<div class="space-y-3 mt-2">
<div v-click border="2 solid white/5" bg="white/5" rounded-lg px-4 py-3>
<span class="font-bold text-blue-300">Averaging</span>
<span class="text-sm opacity-85"> — Bagging and random forests cut a deep tree's error by almost half.</span>
</div>
<div v-click border="2 solid white/5" bg="white/5" rounded-lg px-4 py-3>
<span class="font-bold text-violet-300">Correcting</span>
<span class="text-sm opacity-85"> — Gradient boosting goes further, 0.269. Boosted stumps can't model interactions, 0.354.</span>
</div>
<div v-click border="2 solid amber-800" bg="amber-800/20" rounded-lg px-4 py-3>
<span class="font-bold text-amber-300">The usual pattern on tables:</span>
<span class="text-sm opacity-85"> a tuned boosted model wins; a random forest is close with almost no tuning.</span>
</div>
</div>
</div>

<!--
Every model in the unit on one dataset. These are the same 2,000 training rows and 2,000 held-out districts used throughout the bagging deck, and the first three bars repeat its numbers: one deep tree 0.586, bagging 0.338, random forest 0.310.

Boosted stumps, the stump curve from two slides ago at 2,000 rounds, land at 0.354: far better than one deep tree, but behind the forest, held back by the lack of interactions. Gradient boosting with early stopping, from the last slide, is the best model in the unit at 0.269.

The amber card is the honest summary of practice on tabular data. Well-tuned gradient boosting usually wins, and libraries like XGBoost, LightGBM and CatBoost dominate tabular competitions. But it has more knobs, and a bad learning rate gave 0.396 here, worse than the forest. A random forest with defaults is rarely far behind and rarely goes badly wrong. A good workflow is to start with a forest as a baseline, then see how much a tuned boosted model adds.
-->

---
glowSeed: 660
---

# Who Reduces What

<div class="grid grid-cols-[3fr_2fr] gap-8 items-start">
<div class="mt-2">
<BiasVarBars />
<div class="text-xs opacity-70 mt-1 text-center">Sine toy, 200 fresh 50-point datasets. Averaged over x. Noise (0.09) not included.</div>
</div>
<div class="space-y-3 mt-2">
<div v-click border="2 solid white/5" bg="white/5" rounded-lg px-4 py-3>
<span class="font-bold text-blue-300">Bagging cuts variance</span>
<span class="text-sm opacity-85"> — Deep trees: 0.094 → 0.046. Bias stays put, for stumps and deep trees alike.</span>
</div>
<div v-click border="2 solid white/5" bg="white/5" rounded-lg px-4 py-3>
<span class="font-bold text-violet-300">Boosting cuts bias</span>
<span class="text-sm opacity-85"> — Stumps: bias² 0.074 → 0.011.</span>
</div>
<div v-click border="2 solid amber-800" bg="amber-800/20" rounded-lg px-4 py-3>
<span class="font-bold text-amber-300">Match the method to the problem.</span>
<span class="text-sm opacity-85"> Name the base learner's weak spot first.</span>
</div>
</div>
</div>

<!--
The unit's main idea, measured. On the sine toy we know the true curve, so we can split error exactly. For each learner we drew 200 fresh 50-point datasets, fit the learner to each, and measured how far its average prediction is from the truth (bias squared, orange) and how much its predictions vary across datasets (variance, sky blue), both averaged over x. The noise, 0.09, would add the same amount to every bar.

Top group, starting from stumps. One stump is mostly bias, 0.074. Bagging 50 stumps cuts its variance but leaves the bias at 0.071: the first slide of this deck. Boosting 100 stumps with eta 0.1 cuts bias to 0.011, and its variance, 0.024, is still lower than a single stump's.

Bottom group, starting from deep trees. One deep tree is almost all variance, 0.094. Bagging halves it to 0.046, with bias still near zero: the bagging deck.

Boosted stumps have the lowest total here, but that is a fact about this problem, not a law. The rule to take away is the one from Why Ensembles Work: identify whether your base learner's problem is bias or variance, then pick the ensemble that attacks it.
-->

---
glowSeed: 661
---

# Practical Defaults

<div class="text-sm defaults-table">

| Knob | What it controls | Starting point |
|---|---|---|
| `learning_rate` η | Step size | 0.05–0.1. Smaller needs more rounds. |
| `max_iter` / `n_estimators` | Rounds M | Set high; let early stopping choose. |
| `max_depth` / `max_leaf_nodes` | Interactions | Depth 3–8, or about 31 leaves. |
| `loss` | What counts as wrong | Squared; absolute or Huber† for outliers; log loss for classes. |
| `subsample`† | Rows per round | 0.5–0.8 adds randomness, can cut variance. |
| `min_samples_leaf`, `l2_regularization`‡ | Leaf size and values | Raise them if the model overfits. |

</div>

<div class="mt-3 grid grid-cols-2 gap-4">
<div border="2 solid teal-800" bg="teal-800/20" rounded-lg px-4 py-2 text-sm>
<span class="font-bold text-teal-300">In scikit-learn:</span> <code>HistGradientBoosting*</code> for most work. † <code>GradientBoosting*</code> only. ‡ <code>Hist*</code> only.
</div>
<div border="2 solid violet-800" bg="violet-800/20" rounded-lg px-4 py-2 text-sm>
<span class="font-bold text-violet-300">Beyond it:</span> XGBoost, LightGBM and CatBoost use the same ideas, with more speed and regularization options.
</div>
</div>

<style>
.defaults-table td, .defaults-table th {
  padding-top: 0.4rem;
  padding-bottom: 0.4rem;
}
</style>

<!--
A starting configuration that rarely goes wrong. Learning rate 0.05 to 0.1. A generous cap on rounds, with early stopping deciding the actual number. Trees of depth 3 to 8, or about 31 leaves in the histogram implementation. Pick the loss to match what counts as an error: squared error by default, absolute or Huber when the data have outliers, log loss for classification.

The table marks the parameters that exist on only one family. subsample, in GradientBoostingRegressor and GradientBoostingClassifier but not the histogram estimators, fits each round on a random fraction of rows. This is called stochastic gradient boosting. It borrows bagging's idea to add some variance reduction, and it makes each round cheaper. Regularizing the leaves, with a minimum leaf size or (in the histogram estimators) an L2 penalty on leaf values, is the next thing to try if the model overfits. Huber loss is available only in GradientBoostingRegressor; the histogram regressor offers absolute and quantile losses instead.

On libraries: in scikit-learn, the histogram-based estimators are the ones to use for real work. AdaBoostClassifier is mostly of historical and teaching interest today. XGBoost, LightGBM and CatBoost implement the same gradient-boosting idea with faster training, native handling of missing values and categorical features, and more regularization options. Everything in this deck carries over.
-->

---
glowSeed: 663
---

# What XGBoost, LightGBM and CatBoost Add

<div class="text-sm libs-table">

| Library | Signature idea | Categorical inputs |
|---|---|---|
| scikit-learn `HistGradientBoosting*` | Histogram bins, built-in early stopping | `categorical_features=`, up to 255 categories |
| XGBoost | Penalizes leaf values (L1, L2); uses the loss's curvature as well as its slope | `enable_categorical=True` |
| LightGBM | Histogram bins; grows the leaf with the biggest gain first | Native: finds the best group of categories to split off |
| CatBoost | Ordered boosting; every node at a level shares one split | Native: encodes a category using earlier rows only |

</div>

<div class="mt-4 grid grid-cols-2 gap-4">
<div v-click border="2 solid violet-800" bg="violet-800/20" rounded-lg px-4 py-3>
<span class="font-bold text-violet-300">Same loop underneath</span>
<span class="text-sm opacity-85"> — Fit a tree to the negative gradient, add η times it, stop early. Everything in this deck carries over.</span>
</div>
<div v-click border="2 solid amber-800" bg="amber-800/20" rounded-lg px-4 py-3>
<span class="font-bold text-amber-300">When to reach for them</span>
<span class="text-sm opacity-85"> — Large data, many categorical columns, or GPU training. Otherwise <code>HistGradientBoosting</code> is a sound default.</span>
</div>
</div>

<style>
.libs-table td, .libs-table th {
  padding-top: 0.45rem;
  padding-bottom: 0.45rem;
}
</style>

<!--
The three libraries implement the same gradient-boosting loop from this deck. What they add is engineering and a few modeling choices.

scikit-learn's histogram estimators are modeled on LightGBM: bin each feature into at most 255 values, then search over bin boundaries. They are the baseline.

XGBoost adds an explicit penalty on the leaf values, L2 and optionally L1, plus a minimum gain to make a split. It also uses the second derivative of the loss, the curvature, alongside the gradient, which is like taking a Newton step instead of a plain gradient step. Of the three, it is the one most people met first.

LightGBM grows trees leaf-wise: at each step it splits whichever leaf gives the biggest loss reduction, not every leaf at a given depth. That reaches a low loss with fewer splits, which is why its main size control is the number of leaves, the same parameter the histogram estimators in scikit-learn expose.

CatBoost is built around categorical features and a problem called target leakage. It processes the rows in a random order and encodes each row's category using only the rows before it, so a row's own label never leaks into its feature. Its trees are symmetric: all nodes at the same level use the same split.

The last column leads into the next slide. How each library handles a categorical input is one of the biggest practical differences between them.
-->

---
glowSeed: 664
---

# Categorical vs Continuous Inputs

<div class="grid grid-cols-[2fr_3fr] gap-8 items-start">
<div class="space-y-4 mt-2">
<div border="2 solid white/5" bg="white/5" rounded-lg px-4 py-3>
<div class="font-bold text-amber-300 mb-2">Continuous: one cut</div>
<div class="text-sm opacity-85 mb-2">Is income &lt; 3.5?</div>
<div class="flex gap-1 items-center text-sm">
<span class="px-2 py-1 rounded bg-amber-500/20 border border-amber-700">1.2</span>
<span class="px-2 py-1 rounded bg-amber-500/20 border border-amber-700">2.0</span>
<span class="px-2 py-1 rounded bg-amber-500/20 border border-amber-700">3.1</span>
<span class="px-1 font-bold text-white/70">|</span>
<span class="px-2 py-1 rounded bg-blue-500/20 border border-blue-700">4.8</span>
<span class="px-2 py-1 rounded bg-blue-500/20 border border-blue-700">6.2</span>
</div>
</div>
<div border="2 solid white/5" bg="white/5" rounded-lg px-4 py-3>
<div class="font-bold text-violet-300 mb-2">Categorical: a group</div>
<div class="text-sm opacity-85 mb-2">Is county in the left group?</div>
<div class="flex gap-1 items-center text-sm flex-wrap">
<span class="px-2 py-1 rounded bg-amber-500/20 border border-amber-700">Marin</span>
<span class="px-2 py-1 rounded bg-amber-500/20 border border-amber-700">Orange</span>
<span class="px-1 font-bold text-white/70">|</span>
<span class="px-2 py-1 rounded bg-blue-500/20 border border-blue-700">Kern</span>
<span class="px-2 py-1 rounded bg-blue-500/20 border border-blue-700">Yuba</span>
</div>
</div>
</div>
<div class="space-y-3 mt-2">
<div v-click border="2 solid white/5" bg="white/5" rounded-lg px-4 py-3>
<span class="font-bold text-amber-300">A threshold needs an order</span>
<span class="text-sm opacity-85"> — Categories have none, so a split sends a whole group left. With k categories there are 2<sup>k−1</sup> − 1 groupings: 511 at k = 10, over 500 million at k = 30.</span>
</div>
<div v-click border="2 solid white/5" bg="white/5" rounded-lg px-4 py-3>
<span class="font-bold text-violet-300">Three ways to encode a category</span>
<span class="text-sm opacity-85"> — One-hot: k columns, and each split isolates one category. Integer codes: an invented order the tree must cut into runs. Native: sort the categories by their average target, then cut that order like a number.</span>
</div>
<div v-click border="2 solid red-800" bg="red-800/20" rounded-lg px-4 py-3>
<span class="font-bold text-red-300">High cardinality overfits</span>
<span class="text-sm opacity-85"> — A zip code with three rows can be split off to fit those rows exactly. Merge rare categories, or require a minimum group size.</span>
</div>
</div>
</div>

<!--
So far every feature in this deck has been a number: income, house age, latitude. A split on a number is a threshold, and a threshold works because numbers are ordered.

A category such as county has no order, so a split has to say which group of categories goes left. The number of possible groups is 2 to the k minus 1, minus 1. At 10 categories that is 511 candidates for one split on one feature; at 30 it is over 500 million. A tree cannot search that naively, so libraries take shortcuts.

The three shortcuts. One-hot encoding turns a category with k values into k yes/no columns. It is simple and works with any library, but each split can only isolate one category, so a high-cardinality feature needs many splits and its signal is spread thin across many sparse columns. Integer codes give each category a number. That invents an order, but a tree can still isolate a category with two cuts, so it often works acceptably, especially with deeper trees. Native handling, as in LightGBM, CatBoost, XGBoost with enable_categorical, and scikit-learn's histogram estimators with categorical_features, sorts the categories by a statistic of the target in each one, such as the mean residual, and then cuts that ordering like a number. For squared error this finds the best possible grouping without trying them all, a classic result for regression trees.

The risk is overfitting. A category with only a few rows can be split off to fit those rows perfectly, the same memorizing problem as a tree grown too deep. The fixes are to merge rare categories, require a minimum number of rows per group, or, in CatBoost, encode each row from earlier rows only so its own label cannot leak in.

Tie back to the previous slide: this is why the libraries differ most in their categorical column.
-->

---
glowSeed: 665
---

# Which Features Does the Model Use?

<div class="grid grid-cols-[3fr_2fr] gap-8 items-start">
<div>
<ImportanceBars src="noise" />
<div class="text-xs opacity-70 mt-1 text-center">California housing, depth-3 trees, η = 0.1, 325 rounds, plus one pure-noise column. Permutation: mean of 10 shuffles on the 2,000 held-out rows.</div>
</div>
<div class="space-y-3 mt-2">
<div v-click border="2 solid white/5" bg="white/5" rounded-lg px-4 py-3>
<span class="font-bold text-violet-300">Impurity: free, from training</span>
<span class="text-sm opacity-85"> — How much each feature's splits cut training error. The noise column still gets 1.1%.</span>
</div>
<div v-click border="2 solid white/5" bg="white/5" rounded-lg px-4 py-3>
<span class="font-bold text-teal-300">Permutation: shuffle, then score</span>
<span class="text-sm opacity-85"> — Shuffle one held-out column and see how much test MSE rises. The noise column: 0.000.</span>
</div>
<div v-click border="2 solid amber-800" bg="amber-800/20" rounded-lg px-4 py-3>
<span class="font-bold text-amber-300">They can disagree</span>
<span class="text-sm opacity-85"> — Impurity puts MedInc first (53%) and Latitude and Longitude at 8% and 10%. Shuffling them costs 1.83 and 1.58, against 0.91 for MedInc.</span>
</div>
</div>
</div>

<!--
After fitting a boosted model, the first question is which features it relies on. A single tree is easy to read; 325 of them are not, so we summarize.

Left panel, impurity importance. Every split reduced the training error by some amount; add those reductions up per feature and divide by the total. It comes free with the fitted model, in scikit-learn as feature_importances_. Two weaknesses. It is computed on the training data, so it measures what helped fit the training set, noise included. And it favors features with many possible split points. To show this, we added a column of uniform random numbers, which is unrelated to price by construction. It still gets 1.1% of the credit, about as much as a real feature such as AveBedrms at 1.6%.

Right panel, permutation importance. Take the held-out rows, shuffle one column so its values no longer line up with the rows, and score the model again. The rise in test MSE is how much the model was relying on that column. The noise column scores 0.000, because shuffling a column the model ignores changes nothing. Because it uses held-out data, it asks what matters for predictions on new rows.

The two methods also rank the features differently. Impurity puts median income far ahead, at 53%, with latitude and longitude at 8% and 10%. Permutation reverses that: shuffling latitude raises test MSE by 1.83, longitude by 1.58, and median income by 0.91. The model leans heavily on location. Latitude and longitude are strongly correlated here, which the next slide returns to, so shuffling one produces locations that do not exist and that may inflate the number. Treat the ranking as a question to investigate, not a final answer.

Rule of thumb: prefer permutation importance on held-out data, and treat impurity importance as a quick look.
-->

---
glowSeed: 666
---

# Reading Importances Carefully

<div class="grid grid-cols-[3fr_2fr] gap-8 items-start">
<div>
<ImportanceBars src="copy" />
<div class="text-xs opacity-70 mt-1 text-center">Same model setup, but the extra column is a noisy copy of MedInc (MedInc plus noise, sd 0.2). Latitude and Longitude correlation: −0.93.</div>
</div>
<div class="space-y-3 mt-2">
<div v-click border="2 solid white/5" bg="white/5" rounded-lg px-4 py-3>
<span class="font-bold text-red-300">Correlated features share credit</span>
<span class="text-sm opacity-85"> — With a copy added, MedInc falls from 53% to 44% in impurity and the copy takes 9%.</span>
</div>
<div v-click border="2 solid white/5" bg="white/5" rounded-lg px-4 py-3>
<span class="font-bold text-amber-300">Shuffling can create impossible rows</span>
<span class="text-sm opacity-85"> — Shuffling Latitude pairs it with Longitudes it never occurs with, which may overstate it.</span>
</div>
<div v-click border="2 solid white/5" bg="white/5" rounded-lg px-4 py-3>
<span class="font-bold text-teal-300">The model, not the world</span>
<span class="text-sm opacity-85"> — It shows what this model relied on, not what causes prices. Treat close ranks as ties.</span>
</div>
</div>
</div>

<!--
Three cautions before anyone writes importance into a report.

First, correlated features split the credit. We added a copy of median income with some noise on top. The copy carries no new information, yet it takes 9% of the impurity importance, and median income falls from 53% to 44%. In permutation importance, median income stays at 0.86 and the copy gets only 0.03. The two methods split the credit differently, and neither split is wrong. When two columns say the same thing, the question "which one matters" has no clean answer. If you need one, shuffle the whole group together, or drop one and refit.

Second, permutation importance shuffles a column independently of the others. When columns are correlated, shuffling one can create rows that never occur, such as a latitude and longitude pairing that falls in the ocean. The model is then scored on inputs it was never trained on, and the rise in error may reflect that, not real reliance on the feature. Latitude and longitude have a correlation of −0.93 in this data, so the large location numbers on the previous slide should be read with that in mind.

Third, importance describes the fitted model. It is not causal. A feature can rank high because it is a stand-in for something else, such as location standing in for neighborhood income. It also changes with the model, the data split and the random seed, so repeat the shuffles and do not read much into small gaps.

Next step beyond this unit: SHAP values explain individual predictions, and for tree ensembles they can be computed efficiently. We stop here, but if students want to explain one prediction to a stakeholder, that is where to look.
-->

---
glowSeed: 667
---

# The Meta-Model: Combining the Base Models

<div class="text-sm opacity-85 mt-1">Stacking and blending fit a second model on the base models' held-out predictions. Stacking gets those predictions from 5-fold cross-validation, blending from one 20% holdout.</div>

<div class="grid grid-cols-[2fr_3fr] gap-8 items-start mt-3">
<div>
<div class="font-bold text-violet-300 mb-1">What it is</div>
<div class="text-sm">

| Forest | Booster | Linear | Meta-model | True |
|---|---|---|---|---|
| 280 | 310 | 240 | 301 | 300 |
| 150 | 190 | 200 | 178 | 170 |
| 410 | 380 | 330 | 389 | 400 |

</div>
<div class="text-sm opacity-85 mt-2">Inputs: base predictions. Label: true target. Illustrative numbers, weights 0.3 / 0.7 / 0.</div>
<div v-click class="mt-3 text-sm" border="2 solid violet-800" bg="violet-800/20" rounded-lg px-4 py-2>
<span class="font-bold text-violet-300">In this deck</span> — a non-negative linear regression. It learned weights 0.68 boosting, 0.35 forest, 0.01 linear.
</div>
</div>
<div class="space-y-3">
<div v-click border="2 solid white/5" bg="white/5" rounded-lg px-4 py-3>
<span class="font-bold text-teal-300">Linear or ridge regression</span>
<span class="text-sm opacity-85"> — A weighted sum of the base predictions. The usual default for regression; ridge or non-negative weights steady it when the inputs are highly correlated.</span>
</div>
<div v-click border="2 solid white/5" bg="white/5" rounded-lg px-4 py-3>
<span class="font-bold text-amber-300">Logistic regression</span>
<span class="text-sm opacity-85"> — The same idea for classification. Its inputs are the base models' predicted probabilities.</span>
</div>
<div v-click border="2 solid white/5" bg="white/5" rounded-lg px-4 py-3>
<span class="font-bold text-red-300">Boosted trees or a small neural network</span>
<span class="text-sm opacity-85"> — Can learn when to trust which model. Needs more data and overfits easily, because there are few inputs and they are highly correlated.</span>
</div>
</div>
</div>

<!--
The meta-model is the second model in stacking and blending. The base models, here a random forest, the boosted model and a linear regression, each make a prediction for every training row, using only predictions made on rows that model did not train on. The meta-model is trained on a table where each row is a training example, the columns are those predictions, and the label is the true target.

The left table shows the idea with made-up numbers. The first three columns are base predictions, the fourth is what a meta-model with weights 0.3, 0.7 and 0 outputs, and the last is the true price. In the first row, 0.3 times 280 plus 0.7 times 310 is 301, against a true price of 300.

Stacking and blending differ only in where the held-out predictions come from. Stacking uses 5-fold cross-validation: each base model predicts each row using a copy trained on the other four folds, and the base models are refit on all rows afterward for new data. Blending holds out 20% of the training rows, fits the base models on the other 80%, and fits the meta-model on the base models' predictions for the held-out 20%.

Common meta-models. Linear regression is the default for regression: its coefficients are the weights, so you can read how much each base model counts. Non-negative weights or a ridge penalty keep the weights stable when two base models are almost the same. For classification, logistic regression on the predicted probabilities is the same idea. A boosted-tree or small neural-network meta-model can learn more complicated rules, such as trusting the forest in one region and the booster in another, but with a handful of correlated inputs it overfits easily and needs a lot of data. Start simple, and check that the stack beats both the best single base model and the plain average.

In this deck the meta-model is a non-negative linear regression, and the next slide shows what it learned: weights of 0.68 on boosting, 0.35 on the forest and 0.01 on linear.
-->

---
glowSeed: 668
---

# Does Stacking Help? California Housing

<div class="grid grid-cols-[3fr_2fr] gap-8 items-start">
<div>
<StackBars />
<div class="text-xs opacity-70 mt-1 text-center">Test MSE on 2,000 held-out districts. Same 2,000 training rows; blending fits its base models on 1,600 of them.</div>
</div>
<div class="space-y-3 mt-2">
<div v-click border="2 solid white/5" bg="white/5" rounded-lg px-4 py-3>
<span class="font-bold text-teal-300">Learned weights beat equal weights</span>
<span class="text-sm opacity-85"> — The meta-model gave boosting 0.68, the forest 0.35 and linear 0.01. A plain average, 0.297, trusts all three equally.</span>
</div>
<div v-click border="2 solid white/5" bg="white/5" rounded-lg px-4 py-3>
<span class="font-bold text-pink-300">Blending trains on less</span>
<span class="text-sm opacity-85"> — Its base models see 1,600 rows and its meta-model 400. Result: 0.283, worse than boosting alone.</span>
</div>
<div v-click border="2 solid amber-800" bg="amber-800/20" rounded-lg px-4 py-3>
<span class="font-bold text-amber-300">Not a free win</span>
<span class="text-sm opacity-85"> — Stacking, 0.269, only ties boosting alone. It pays when the bases are diverse and similarly good.</span>
</div>
</div>
</div>

<!--
Same setup as the scoreboard: a random forest, the early-stopped boosted model, and a linear regression, all fit on the same 2,000 California rows and scored on the same 2,000 held-out districts.

The three base models score 0.481, 0.310 and 0.269. A plain average of the three gets 0.297: the weak linear model drags it above boosting alone. Stacking learns to give the linear model almost no weight, 0.01, puts 0.68 on boosting and 0.35 on the forest, and reaches 0.269, a tie with boosting by itself. Here, stacking mostly protects against a bad average and does not beat the best base model.

Blending lands at 0.283. Its base models trained on 1,600 rows and the meta-model on the other 400, so every piece is weaker than in stacking, and the result is worse than boosting alone.

That is typical. Stacking gains come when the base models make different mistakes and are similarly accurate. The forest and the booster are both tree ensembles, so their errors overlap a lot. Models from other families, such as a nearest-neighbor model or a neural network, would add more diversity. The costs are more training time and a pipeline that is harder to explain, so many practitioners start with one well-tuned boosted model and stack only when the last bit of accuracy matters.
-->

---
glowSeed: 662
---

# Ensemble Methods in One View

<div class="grid grid-cols-3 gap-4 mt-6">
<div v-click border="2 solid blue-800" bg="blue-800/20" rounded-lg p-4>
<div class="font-bold text-blue-300 mb-2">Average</div>
<div class="text-sm leading-relaxed opacity-90">Bagging: deep trees on bootstrap samples. Cuts variance toward ρσ².</div>
</div>
<div v-click border="2 solid teal-800" bg="teal-800/20" rounded-lg p-4>
<div class="font-bold text-teal-300 mb-2">Decorrelate</div>
<div class="text-sm leading-relaxed opacity-90">Random forests: random features per split. Lowers ρ, so the floor drops.</div>
</div>
<div v-click border="2 solid violet-800" bg="violet-800/20" rounded-lg p-4>
<div class="font-bold text-violet-300 mb-2">Correct</div>
<div class="text-sm leading-relaxed opacity-90">Boosting: shallow trees in sequence, each fit to the negative gradient. Cuts bias.</div>
</div>
</div>

<div class="grid grid-cols-2 gap-4 mt-5">
<div v-click border="2 solid white/5" bg="white/5" rounded-lg px-4 py-3>
<span class="font-bold text-red-300">Boosting can overfit</span>
<span class="text-sm opacity-85"> — Tune η and M together, and stop early on held-out data.</span>
</div>
<div v-click border="2 solid white/5" bg="white/5" rounded-lg px-4 py-3>
<span class="font-bold text-amber-300">Nothing beats the noise</span>
<span class="text-sm opacity-85"> — Every method here works on bias or variance. None touches σ²<sub>ε</sub>.</span>
</div>
</div>

<!--
Close the unit with the three verbs. Average: bagging takes a learner with low bias and high variance, a deep tree, and averages many bootstrap copies; variance falls toward the floor rho sigma squared from Why Ensembles Work. Decorrelate: random forests restrict each split to a random subset of features, which lowers rho and so lowers the floor itself. Correct: boosting takes a learner with high bias, a shallow tree, and adds members in sequence, each fit to the negative gradient of the loss, which for squared error is just the residual; AdaBoost is the special case with exponential loss.

The two cautions. Boosting is the one ensemble method where more members can hurt, so the learning rate and number of rounds are chosen together, with early stopping on held-out data. And no ensemble removes irreducible noise: if identical inputs carry different labels, a thousand trees can't predict it away.

If students remember one thing from this unit: before choosing an ensemble, ask whether the base learner's problem is bias or variance. That question tells you which recipe to use.
-->
