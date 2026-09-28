---
theme: default
highlighter: shiki
css: unocss
colorSchema: dark
title: 'Decision Trees'
info: |
  ## Decision Trees
  Classification by a sequence of interpretable threshold questions.
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
glowSeed: 461
---

# Decision Trees

### Classification via a sequence of questions

<div class="pt-5 opacity-80 text-lg">Supervised Learning · Classification</div>

<svg role="img" aria-label="A decision tree asks feature threshold questions and ends at class leaves" viewBox="0 0 760 260" class="w-full max-w-3xl mx-auto mt-7">
  <g stroke="#94a3b8" stroke-width="3"><line x1="380" y1="70" x2="235" y2="130"/><line x1="380" y1="70" x2="525" y2="130"/><line x1="235" y1="170" x2="150" y2="225"/><line x1="235" y1="170" x2="300" y2="225"/><line x1="525" y1="170" x2="455" y2="225"/><line x1="525" y1="170" x2="610" y2="225"/></g>
  <g text-anchor="middle" dominant-baseline="middle"><rect x="290" y="25" width="180" height="55" rx="12" fill="#0f766e88" stroke="#2dd4bf"/><text x="380" y="52.5" fill="white">x₁ &gt; 5?</text><rect x="160" y="125" width="150" height="50" rx="12" fill="#1e3a8a88" stroke="#60a5fa"/><text x="235" y="150" fill="white">x₂ &gt; 2?</text><rect x="450" y="125" width="150" height="50" rx="12" fill="#1e3a8a88" stroke="#60a5fa"/><text x="525" y="150" fill="white">x₃ &gt; 7?</text></g>
  <g text-anchor="middle" dominant-baseline="middle"><rect x="95" y="215" width="110" height="38" rx="8" fill="#ea580c88"/><rect x="250" y="215" width="110" height="38" rx="8" fill="#2563eb88"/><rect x="400" y="215" width="110" height="38" rx="8" fill="#ea580c88"/><rect x="555" y="215" width="110" height="38" rx="8" fill="#2563eb88"/><text x="150" y="234" fill="white">class 0</text><text x="305" y="234" fill="white">class 1</text><text x="455" y="234" fill="white">class 0</text><text x="610" y="234" fill="white">class 1</text></g>
</svg>

<!--
A decision tree classifies an example by asking a sequence of yes/no questions, each comparing one feature to a learned threshold, until it reaches a leaf that stores a class prediction. Unlike logistic regression or SVMs, a tree needs no probability model, no distance metric, and no gradient descent — it is built by a simple recursive greedy search over thresholds, so the resulting rules are directly human-readable: "if income > $50k and age > 30, predict class 1." That interpretability is a genuine practical strength in regulated domains like credit scoring or medicine, where a stakeholder can audit the exact decision path for any prediction.

Roadmap for today: how a tree partitions feature space, the impurity measures (Gini and entropy) used to score candidate splits, information gain as the greedy splitting criterion, why unconstrained trees overfit, pruning as the tree analogue of regularization, and regression trees. A single tree trained on slightly different data can look very different — that instability seems like a weakness here, but it becomes the key ingredient random forests and boosting exploit in the later Ensemble Methods unit, where averaging many unstable trees produces a stable, accurate model.
-->

---
glowSeed: 462
---

# A Tree Is Also a Partition of Space

<div class="grid grid-cols-2 gap-7 mt-3 items-center">
<div>
<v-clicks>

- Internal nodes test one feature against a threshold
- Follow matching branches from root to leaf
- Leaves hold class predictions
- Binary splits carve feature space into axis-aligned rectangles

</v-clicks>

```python
from sklearn.datasets import make_classification
from sklearn.tree import DecisionTreeClassifier

X, y = make_classification(
    n_samples=200, n_features=2,
    n_redundant=0, random_state=0)
tree = DecisionTreeClassifier(
    max_depth=3, random_state=0)
tree.fit(X, y)
```
</div>
<svg role="img" aria-label="A small tree and matching axis aligned rectangular regions in two dimensional feature space" viewBox="0 0 540 330" class="w-full">
  <rect x="20" y="30" width="210" height="260" fill="#0f766e22" stroke="#64748b"/><line x1="120" y1="30" x2="120" y2="290" stroke="#f8fafc" stroke-width="4"/><line x1="120" y1="155" x2="230" y2="155" stroke="#f8fafc" stroke-width="4"/><rect x="22" y="32" width="96" height="256" fill="#ea580c33"/><rect x="122" y="32" width="106" height="121" fill="#2563eb33"/><rect x="122" y="158" width="106" height="130" fill="#0f766e55"/>
  <text x="80" y="315" fill="#94a3b8">feature space</text>
  <g transform="translate(270,25)" stroke="#94a3b8" stroke-width="2"><line x1="100" y1="45" x2="45" y2="105"/><line x1="100" y1="45" x2="155" y2="105"/><line x1="155" y1="130" x2="110" y2="200"/><line x1="155" y1="130" x2="195" y2="200"/></g>
  <g transform="translate(270,25)"><rect x="45" y="20" width="110" height="45" rx="8" fill="#0f766e88"/><text x="72" y="48" fill="white">x₁ ≤ t₁?</text><rect x="5" y="95" width="80" height="35" rx="7" fill="#ea580c88"/><text x="22" y="118" fill="white">class 0</text><rect x="110" y="95" width="90" height="35" rx="7" fill="#1e3a8a88"/><text x="128" y="118" fill="white">x₂ ≤ t₂?</text><rect x="70" y="200" width="80" height="35" rx="7" fill="#2563eb88"/><text x="87" y="223" fill="white">class 1</text><rect x="160" y="200" width="80" height="35" rx="7" fill="#0f766e88"/><text x="177" y="223" fill="white">class 0</text></g>
</svg>
</div>

<!--
Trace one root-to-leaf path in plain English: start at the root, ask "is x1 greater than t1?", follow the matching branch, ask the next question at that node, and repeat until you land on a leaf holding a class label. Every internal node tests exactly one feature against one threshold, so geometrically each split is a straight cut perpendicular to one coordinate axis. The union of all splits along a root-to-leaf path carves feature space into an axis-aligned rectangle (a hyper-rectangle in higher dimensions), and the tree's full set of leaves partitions the space into disjoint rectangles, each assigned one predicted class.

Contrast the decision geometry across algorithms covered this module: logistic regression produces exactly one linear (or, with basis expansion, curved) boundary across the whole space; k-NN produces a Voronoi-like boundary that follows the local density of training points; decision trees produce boxy, axis-aligned regions because each split only ever looks at one feature at a time — a diagonal boundary requires many small steps to approximate. In practice, call `sklearn.tree.plot_tree(tree)` to render the learned structure live and let students match branches to rectangles themselves.
-->

---
glowSeed: 463
class: impurity-slide
---

# How Pure Is a Node?

<div class="grid grid-cols-2 gap-7 mt-3 items-center">
<div>
<div border="2 solid blue-800" bg="blue-800/20" rounded-lg p-4>

$$\operatorname{Gini}=1-\sum_{k=1}^{K}p_k^2$$
$$\operatorname{Entropy}=-\sum_{k=1}^{K}p_k\log_2p_k$$

</div>

```python
import numpy as np

def gini(p):
    return 1 - np.sum(np.asarray(p)**2)

def entropy(p):
    p = np.asarray(p); p = p[p > 0]
    return -np.sum(p * np.log2(p))

assert gini([1, 0]) == entropy([1, 0]) == 0
```
</div>
<div>
<div class="mt-4 text-sm opacity-85">
  <strong>Definition:</strong> <em>p</em><sub>k</sub> is the fraction of examples reaching this node that belong to class <em>k</em>.
</div>
<div class="mt-3 text-sm border-2 border-white/10 bg-white/5 rounded-lg p-3">
  <strong>Conceptually:</strong> low Gini means the node is nearly pure; high Gini means the node mixes classes and is harder to classify confidently.
</div>
<svg role="img" aria-label="Gini and entropy are zero at pure nodes and peak at an even class mixture" viewBox="0 0 470 315" class="w-full">
  <line x1="45" y1="270" x2="440" y2="270" stroke="#64748b"/><line x1="45" y1="270" x2="45" y2="25" stroke="#64748b"/>
  <path d="M45 270 Q245 35 440 270" fill="none" stroke="#2dd4bf" stroke-width="5"/><path d="M45 270 Q245 75 440 270" fill="none" stroke="#60a5fa" stroke-width="5"/>
  <line x1="245" y1="55" x2="245" y2="270" stroke="#f8fafc" stroke-dasharray="6 5"/><text x="225" y="295" fill="#94a3b8">p=.5</text><text x="310" y="65" fill="#5eead4">entropy</text><text x="310" y="105" fill="#93c5fd">Gini</text>
</svg>
</div>
</div>

<!--
Both formulas measure how "mixed" the class labels are at a node, using p_k, the fraction of training examples at that node belonging to class k, summed over all K classes. Gini impurity, 1 minus the sum of squared class proportions, has an intuitive reading: it is the probability that two randomly drawn examples from the node have different labels if you label each one by drawing from the node's class distribution. Entropy, the negative sum of p_k log2(p_k), comes from information theory and measures the average number of bits needed to encode a class label drawn from that distribution. Both are exactly zero when a node is pure — every example belongs to one class, so there is nothing left to disambiguate — and both peak at a 50/50 split for two classes, where uncertainty about the label is maximal.

Walk through the code: gini([1,0]) and entropy([1,0]) both evaluate to zero because one class proportion is 1 and the other is 0, so there is no impurity. In practice the two criteria produce very similar trees almost all of the time, since they are both concave functions that are zero at the extremes and peak in the middle. scikit-learn's `DecisionTreeClassifier` defaults to Gini (`criterion="gini"`) partly because it avoids computing a logarithm at every candidate split, which matters when evaluating thousands of thresholds during training. The choice between Gini and entropy is a minor implementation detail; what actually controls a tree's quality is depth and pruning, covered next.
-->

---
glowSeed: 464
---

# Information Gain Picks the Split

<div class="text-lg opacity-85 mb-4">Information gain measures how much a split reduces Gini impurity—from the parent to the weighted average of its children.</div>

<div class="grid grid-cols-2 gap-7 mt-2">
<div>
<div border="2 solid teal-800" bg="teal-800/20" rounded-lg p-4 text-sm>

$$IG=I(parent)-\left[\frac{n_L}{n}I(L)+\frac{n_R}{n}I(R)\right]$$

</div>
<div class="mt-5 flex items-center gap-3 text-center text-sm">
<div class="flex-1 p-4 rounded bg-white/5 border-2 border-white/10"><strong>parent</strong><br/>4 orange · 4 blue<br/>Gini = .5</div><div class="text-2xl">→</div><div class="flex-1"><div class="p-3 rounded bg-orange-500/20 border-2 border-orange-700">4 orange<br/>Gini = 0</div><div class="p-3 mt-2 rounded bg-blue-500/20 border-2 border-blue-700">4 blue<br/>Gini = 0</div></div>
</div>
<div v-click class="mt-4 text-center text-xl"><code>IG = .5 − [.5(0) + .5(0)] = .5</code></div>
</div>

```python
def information_gain(parent, left, right):
    def node_gini(labels):
        _, counts = np.unique(labels,
                              return_counts=True)
        return gini(counts / len(labels))
    n = len(parent)
    child = (len(left)/n)*node_gini(left)
    child += (len(right)/n)*node_gini(right)
    return node_gini(parent) - child

p = np.array([0]*4 + [1]*4)
assert information_gain(p, p[:4], p[4:]) == .5
```
</div>

<!--
Information gain, IG, measures how much a candidate split reduces impurity: it is the parent node's impurity I(parent) minus the weighted average impurity of the two children, where the weights n_L/n and n_R/n are the fraction of the parent's examples that land in the left and right child respectively. This example is the best possible case: the parent has an even 4/4 mix (Gini = .5, maximal uncertainty), and the split sends every orange point left and every blue point right, leaving both children perfectly pure (Gini = 0 each). Information gain is therefore the full parent impurity, .5 — nothing beats a perfect split.

The CART algorithm (Classification and Regression Trees, used by scikit-learn) builds a tree greedily: at each node, it enumerates every feature and every candidate threshold between adjacent sorted feature values, computes the information gain each split would produce, and picks the single split with the largest gain. It commits to that split immediately and never revisits the decision — there is no lookahead to see whether a locally worse split might enable better splits deeper in the tree. Finding the globally optimal decision tree is NP-hard, so this greedy heuristic is a practical necessity, not a design preference. The next slide on Ensemble Methods will show that averaging predictions from many such greedily built trees compensates for this myopia.
-->

---
glowSeed: 464.5
class: worked-split
---

# A Worked Example With an Imperfect Split

<div class="split-example">
  <div class="split-parent split-card">
    <div><strong>Parent · 10 examples</strong><div class="split-counts">6 positive · 4 negative</div></div>
    <div class="split-equation">Gini = 1 − (0.6² + 0.4²) = <strong>0.48</strong></div>
  </div>
  <div class="split-branches" aria-hidden="true"><span>↙ 5 examples</span><span>5 examples ↘</span></div>
  <div class="split-children">
    <div v-click="1" class="split-card split-left">
      <strong>Left child</strong>
      <div class="split-counts">4 positive · 1 negative</div>
      <div class="split-equation">Gini = 1 − (0.8² + 0.2²) = <strong>0.32</strong></div>
    </div>
    <div v-click="2" class="split-card split-right">
      <strong>Right child</strong>
      <div class="split-counts">2 positive · 3 negative</div>
      <div class="split-equation">Gini = 1 − (0.4² + 0.6²) = <strong>0.48</strong></div>
    </div>
  </div>
  <div v-click="3" class="split-weighted split-card">
    <strong>Weighted child impurity</strong>
    <span>½ × 0.32 + ½ × 0.48 = <strong>0.40</strong></span>
  </div>
  <div v-click="4" class="split-result split-card">
    <div><div class="split-counts">Information gain = parent − weighted children</div><div class="split-answer">0.48 − 0.40 = <strong>0.08</strong></div></div>
    <span>A modest reduction in impurity.</span>
  </div>
</div>

<!--
Most real splits are not as clean as the perfect example on the previous slide, so walk through this messier one by hand. The parent node has 10 examples, 6 positive and 4 negative, giving class proportions .6 and .4 and a Gini impurity of 1 − (.36 + .16) = .48 — fairly impure, as expected when classes are reasonably balanced. Suppose a candidate threshold sends 5 examples left (4 positive, 1 negative) and 5 right (2 positive, 3 negative). The left child is fairly pure, Gini = 1 − (.64 + .04) = .32, while the right child is nearly as impure as the parent, Gini = 1 − (.16 + .36) = .48.

Combine the two children with the weighted-average formula from the previous slide: since each child holds exactly half the parent's examples, the weighted child impurity is .5(.32) + .5(.48) = .40. Information gain is then .48 − .40 = .08, positive but modest — this split makes real progress by isolating a mostly-positive left group, but it is far weaker than the earlier example that achieved perfect separation with gain .5. CART would compare this .08 against the information gain of every other candidate threshold on every other feature, and greedily choose whichever single split scores highest.
-->

---
glowSeed: 464.75
class: cart-slide
---

# CART: How a Decision Tree Is Fitted

<div class="text-lg opacity-80 mt-2">Classification and Regression Trees · greedy, recursive binary splitting</div>

<div class="grid grid-cols-2 gap-6 mt-5">
<div class="cart-steps">
  <div v-click="1" class="cart-step"><span class="cart-number">1</span><div><strong>Search candidate splits</strong><div>At the current node, try features and thresholds: xⱼ ≤ t versus xⱼ &gt; t.</div></div></div>
  <div v-click="2" class="cart-step"><span class="cart-number">2</span><div><strong>Choose the largest impurity reduction</strong><div>Score valid splits using weighted child impurity. Keep the best feature and threshold.</div></div></div>
  <div v-click="3" class="cart-step"><span class="cart-number">3</span><div><strong>Repeat in each child</strong><div>Send examples left or right, then search again using only that child’s examples.</div></div></div>
  <div v-click="4" class="cart-step"><span class="cart-number">4</span><div><strong>Stop and store a prediction</strong><div>Stop at pure nodes, depth/sample limits, or no valid split. A class leaf predicts its majority class.</div></div></div>
</div>
<div>
<div class="cart-objective">
  <strong>At each node, choose (j, t) to maximize</strong>

$$I(\text{parent})-\left[\frac{n_L}{n}I(L)+\frac{n_R}{n}I(R)\right]$$

  <div class="text-sm opacity-80">The previous slide’s gain of <strong>0.08</strong> is one candidate score. CART compares it with the other valid splits.</div>
</div>

```python
tree = DecisionTreeClassifier(
    criterion="gini",
    max_depth=3,
    min_samples_leaf=5,
    random_state=0,
)
tree.fit(X, y)  # learn splits from training data
```

<div class="cart-caution"><strong>Greedy:</strong> choose the best split now; do not search all possible future trees.</div>
</div>
</div>

<!--
CART stands for Classification and Regression Trees. Start with all training examples at the root. For a numeric feature, sort the distinct values present at this node and consider thresholds between adjacent values; each candidate creates two groups, x_j <= t and x_j > t. Reject splits that violate constraints such as min_samples_leaf, then compare the weighted impurity reduction of the remaining candidates. The worked example gave a gain of .08, but that split is selected only if it is the best valid candidate at this node, subject to any configured impurity threshold.

Store the winning feature index and threshold, partition the training examples, and repeat the same procedure independently in each child. Each child can choose a different feature or reuse a feature at a different threshold. Stop when a node is pure, a depth or sample limit is reached, or no valid split remains. For classification, store class proportions in the leaf and predict the majority class. For regression with squared-error loss, use variance/MSE reduction to score splits and store the mean target in each leaf.

The fit call carries out this recursive search; the depth and sample settings constrain growth. Greedy means each split is chosen for its immediate improvement, without looking ahead to the best complete tree. A zero-gain split can still permit useful splits farther down, so do not equate a zero immediate gain with proof that further growth is useless. CART also supports cost-complexity pruning after growth, covered shortly. Transition to the next slide: if we keep subdividing without useful limits, even noisy examples can end up in pure leaves, which explains why unconstrained trees overfit.
-->

---
glowSeed: 465
class: capacity-slide
---

# Unconstrained Trees Overfit

<div class="grid grid-cols-3 gap-4 mt-4 text-center text-sm">
<div v-click border="2 solid blue-800" bg="blue-800/20" rounded-lg p-3><strong>depth = 1</strong><svg role="img" aria-label="One straight tree split underfits" viewBox="0 0 200 130" class="w-full mt-2"><line x1="100" y1="10" x2="100" y2="120" stroke="#60a5fa" stroke-width="5"/><g fill="#f8fafc"><circle cx="45" cy="30" r="5"/><circle cx="70" cy="90" r="5"/><circle cx="145" cy="35" r="5"/><circle cx="160" cy="100" r="5"/></g></svg>high bias</div>
<div v-click border="2 solid teal-800" bg="teal-800/20" rounded-lg p-3><strong>depth = 5</strong><svg role="img" aria-label="A few rectangular tree regions fit useful structure" viewBox="0 0 200 130" class="w-full mt-2"><path d="M65 10 V70 H120 V120 M120 70 H185" fill="none" stroke="#2dd4bf" stroke-width="5"/><g fill="#f8fafc"><circle cx="45" cy="30" r="5"/><circle cx="70" cy="90" r="5"/><circle cx="145" cy="35" r="5"/><circle cx="160" cy="100" r="5"/></g></svg>useful structure</div>
<div v-click border="2 solid orange-800" bg="orange-800/20" rounded-lg p-3><strong>depth = None</strong><svg role="img" aria-label="Many tiny rectangular tree regions isolate noisy points" viewBox="0 0 200 130" class="w-full mt-2"><path d="M25 10 V120 M50 10 V70 H85 V120 M110 10 V45 H140 V95 H175 V120 M140 95 H195" fill="none" stroke="#fb923c" stroke-width="4"/><g fill="#f8fafc"><circle cx="45" cy="30" r="5"/><circle cx="70" cy="90" r="5"/><circle cx="145" cy="35" r="5"/><circle cx="160" cy="100" r="5"/></g></svg>high variance</div>
</div>

```python
from sklearn.model_selection import cross_val_score

for depth in [1, 3, 5, None]:
    tree = DecisionTreeClassifier(
        max_depth=depth, random_state=0)
    score = cross_val_score(tree, X, y, cv=5).mean()
    print(depth, score)
```

<div v-click class="mt-4 text-center text-sm opacity-80">Capacity knobs: <code>max_depth</code>, <code>min_samples_split</code>, and <code>min_samples_leaf</code>.</div>

<!--
A tree's depth is its capacity knob, exactly like the degree of a polynomial in linear regression or k in k-NN. At depth 1 (a "decision stump"), the model can only ask one question total, so it draws a single straight cut through feature space — this underfits whenever the true boundary needs more than one split, producing high bias. At depth 5 the tree can carve out several rectangular regions and captures the useful structure in this toy dataset. With unlimited depth (max_depth=None), CART keeps splitting until every leaf is pure or has one example, which means the tree can literally memorize the training set, including its noise — this is high variance: the model changes drastically if you retrain on a slightly different sample, and it generalizes poorly to unseen data.

Before running the cross-validation loop, ask students to predict the pattern: accuracy should rise from depth 1 to some intermediate depth, then plateau or fall as the tree starts fitting noise. max_depth, min_samples_split (minimum examples required to consider splitting a node), and min_samples_leaf (minimum examples required in each resulting leaf) are all structural regularizers — they limit how finely the tree can carve up space, playing the same role that the regularization strength lambda plays for ridge or lasso regression, and the same role k plays in k-NN.
-->

---
glowSeed: 466
class: pruning-slide
---

# Regularizing a Decision Tree

<div class="text-lg opacity-80 mt-2">Allow a little more training impurity to avoid fitting noise.</div>

<div class="tree-regularization">
  <div v-click="1" class="regularization-card">
    <div class="text-teal-300 text-sm">1 · LIMIT GROWTH</div>
    <h2>Stop the tree getting too complex</h2>
    <p>Restrict which splits the tree is allowed to make.</p>
    <div class="regularization-setting"><code>max_depth</code><span>Lower → shallower trees</span></div>
    <div class="regularization-setting"><code>min_samples_leaf</code><span>Higher → fewer tiny leaves</span></div>
    <div class="regularization-label">Pre-pruning: constraints during fitting</div>
  </div>
  <div v-click="2" class="regularization-card regularization-prune">
    <div class="text-violet-300 text-sm">2 · PRUNE AFTER GROWING</div>
    <h2>Remove branches that add little</h2>
    <p>Replace a subtree with a leaf when its extra complexity is not worth the improvement in fit.</p>
    <div class="regularization-setting"><code>ccp_alpha</code><span>Higher → stronger pruning</span></div>
    <div class="regularization-label">Post-pruning: penalize extra leaves</div>
  </div>
</div>

<div v-click="3" class="regularization-objective">
  <strong>Pruning minimizes:</strong> weighted leaf impurity + α × number of leaves
  <div>Choose strength by cross-validation: too little overfits; too much underfits.</div>
</div>

<!--
In scikit-learn's cost-complexity pruning formulation, R(T) is total sample-weighted leaf impurity, not a separate misclassification-error measure. For the unweighted training examples used here, each leaf's weight is n_leaf/N, where N counts all training examples. With sample weights, replace counts by weight sums. I(leaf) uses the fitted criterion, Gini in this example. A pure-leaf tree has R(T)=0 even if it overfits.

Connect this directly to growth: splitting a node containing n examples with local information gain IG reduces whole-tree R(T) by (n/N)IG. The complexity term is used in post-pruning, not added to each greedy split score during growth. For a fixed alpha, seek the pruned subtree minimizing R_alpha(T)=R(T)+alpha times the number of leaves. Weakest-link pruning generates a nested sequence of subtrees; it removes branches rather than searching for alternative feature thresholds at retained nodes.

Teach this as two functional approaches to regularization. First, constrain the model: max_depth limits the number of successive questions and min_samples_leaf prevents splitting off tiny groups. Second, penalize complexity: grow a tree, then remove branches whose impurity reduction does not justify their extra leaves. These approaches can be combined. The shared aim is to trade some training fit for better generalization; validation performance determines how much regularization is useful.

Keep the two optimization decisions distinct: minimize penalized training impurity to select a subtree for a fixed alpha, then use cross-validation performance to choose alpha. In code, DecisionTreeClassifier(ccp_alpha=alpha).fit(X, y) grows and prunes the tree; cost_complexity_pruning_path exposes candidate alphas and corresponding leaf impurities. Pre-pruning settings such as max_depth and min_samples_leaf constrain growth before this pruning stage.
-->

---
glowSeed: 467
---

# Trees Also Regress

<div class="grid grid-cols-2 gap-7 mt-3 items-center">
<div>
<v-clicks>

- `DecisionTreeRegressor` predicts the mean target in each leaf
- Splits reduce within-node variance or MSE
- Predictions are piecewise constant—always a staircase
- The same overfitting and pruning controls apply

</v-clicks>

```python
from sklearn.tree import DecisionTreeRegressor

rng = np.random.default_rng(0)
Xr = np.linspace(0, 10, 100)[:, None]
yr = np.sin(Xr[:, 0]) + rng.normal(0, .1, 100)
model = DecisionTreeRegressor(
    max_depth=4, random_state=0)
model.fit(Xr, yr)
assert np.isfinite(model.predict(Xr)).all()
```
</div>
<svg role="img" aria-label="A regression tree produces staircase predictions over noisy sine data" viewBox="0 0 470 310" class="w-full">
  <line x1="35" y1="270" x2="445" y2="270" stroke="#64748b"/>
  <g fill="#f8fafc" opacity=".7"><circle cx="50" cy="190" r="4"/><circle cx="80" cy="115" r="4"/><circle cx="115" cy="75" r="4"/><circle cx="150" cy="105" r="4"/><circle cx="190" cy="185" r="4"/><circle cx="230" cy="235" r="4"/><circle cx="275" cy="190" r="4"/><circle cx="315" cy="95" r="4"/><circle cx="360" cy="70" r="4"/><circle cx="410" cy="150" r="4"/></g>
  <path d="M40 190 H85 V110 H140 V80 H185 V165 H235 V230 H280 V185 H330 V90 H385 V75 H440 V150" fill="none" stroke="#2dd4bf" stroke-width="5"/>
</svg>
</div>

<!--
Everything about trees generalizes cleanly from classification to regression. Instead of predicting a class, `DecisionTreeRegressor` predicts a continuous number, computed as the mean target value of the training examples that land in each leaf. Instead of Gini or entropy, splits are chosen to minimize within-node variance (equivalently, mean squared error) — the regression analogue of impurity, since a leaf with low variance means its examples' target values are all close together, so predicting their mean is a good summary. The resulting prediction function is piecewise constant: it looks like a staircase, flat within each leaf's region and jumping at each split boundary, which is visibly different from the smooth curves produced by polynomial regression.

Keep this slide brief but make the connection explicit, since it matters for the rest of the course: regression trees are the base learner used inside gradient boosting (e.g., XGBoost, LightGBM) and random forest regressors, covered in the Ensemble Methods unit. A single regression tree's staircase looks crude, but averaging predictions from many such trees — each trained on a resampled or reweighted version of the data — smooths the staircase into a much more flexible and accurate function, exactly as averaging many unstable classification trees produces a stable classifier.
-->

---
layout: center
class: text-center
glowSeed: 468
---

# Four Classification Strategies

<div class="grid grid-cols-4 gap-3 mt-7 text-left text-sm">
<div v-click border="2 solid blue-800" bg="blue-800/20" rounded-lg p-4><strong>Logistic</strong><div class="opacity-75 mt-2">discriminative optimization</div></div>
<div v-click border="2 solid teal-800" bg="teal-800/20" rounded-lg p-4><strong>k-NN</strong><div class="opacity-75 mt-2">instance-based geometry</div></div>
<div v-click border="2 solid violet-800" bg="violet-800/20" rounded-lg p-4><strong>Naive Bayes</strong><div class="opacity-75 mt-2">generative probability</div></div>
<div v-click border="2 solid orange-800" bg="orange-800/20" rounded-lg p-4><strong>Trees</strong><div class="opacity-75 mt-2">interpretable rules</div></div>
</div>

<div v-click class="mt-8" border="2 solid white/10" bg="white/5" rounded-lg p-4>Splits greedily maximize impurity reduction; depth limits and pruning control variance.</div>

<div v-click class="mt-7 text-lg"><strong>Next:</strong> Model Evaluation · <span class="opacity-70">Later:</span> Ensemble Methods build many trees.</div>

<!--
Close the four-algorithm comparison for this module: logistic regression fits a discriminative linear model by optimizing a convex loss; k-NN makes no explicit model at all, just geometry over stored examples; Naive Bayes fits a generative probability model per class using a simplifying independence assumption; decision trees greedily carve feature space into axis-aligned rules. Each has a different notion of "capacity control" — regularization strength, k, smoothing, and depth/pruning respectively — but the same bias-variance story underlies all four.

Restate the core mechanism: trees pick splits greedily by maximizing information gain (impurity reduction), and depth limits or cost-complexity pruning control the resulting variance. A single tree is refreshingly interpretable — you can literally read off the decision rules — but it is also unstable: a small change in the training data can flip which feature gets picked at the root and cascade into a completely different tree structure. That instability sounds like a flaw, but it is exactly the property random forests and gradient boosting exploit in the Ensemble Methods unit, where averaging many differently-grown trees converts instability into robustness. Before we get there, the next unit covers Model Evaluation — precision, recall, F1, and ROC/AUC — the tools needed to compare classifiers fairly, especially when classes are imbalanced.
-->
