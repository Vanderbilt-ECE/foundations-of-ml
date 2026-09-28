---
theme: default
highlighter: shiki
css: unocss
colorSchema: dark
title: 'Naive Bayes'
info: |
  ## Naive Bayes
  Classification by modeling how each class generates features.
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
glowSeed: 441
---

# Naive Bayes

### Classification via Bayes’ theorem

<div class="pt-5 opacity-80 text-lg">Supervised Learning · Classification</div>

<div v-click class="mt-12 max-w-4xl mx-auto" border="2 solid teal-800" bg="teal-800/20" rounded-lg px-8 py-6>

$$P(\text{class}\mid\text{features})=\frac{P(\text{features}\mid\text{class})P(\text{class})}{P(\text{features})}$$

</div>

<div class="mt-7 opacity-75">generative probability · conditional independence · fast closed-form estimates</div>

<!--
Reconnect explicitly to the Bayes' theorem derivation from the probability unit: P(class | features) — the posterior, what we actually want to predict — equals P(features | class) — the likelihood, how features are distributed within each class — times P(class) — the prior, how common each class is overall — divided by P(features), a normalizing constant that does not depend on which class we are considering.

Naive Bayes is a generative classifier: rather than modeling P(y|x) directly, it models how each class generates its features, P(x|y), and a prior P(y), then inverts that relationship with Bayes' theorem to get the posterior P(y|x) needed for classification. This is a fundamentally different strategy from the other two covered in this module: logistic regression is discriminative and models P(y|x) directly by fitting a boundary, with no attempt to model how the features themselves are distributed; k-NN makes no probability model at all, just memorizing instances and voting geometrically. Today's roadmap: the classification form of Bayes' theorem, the conditional-independence ("naive") assumption that makes the joint likelihood tractable, Gaussian Naive Bayes for continuous features, and Multinomial/Bernoulli variants with Laplace smoothing for text and count data.
-->

---
glowSeed: 442
---

# Bayes’ Theorem for Classification

<div v-click border="2 solid blue-800" bg="blue-800/20" rounded-lg px-5 py-3>

$$P(y=k\mid x)=\frac{P(x\mid y=k)P(y=k)}{P(x)}\propto P(x\mid y=k)P(y=k)$$
$$\hat y=\arg\max_k P(x\mid y=k)P(y=k)$$

</div>

<div class="grid grid-cols-4 gap-3 mt-7 text-center text-sm">
<div v-click border="2 solid violet-800" bg="violet-800/20" rounded-lg p-4><strong>Prior</strong><br/><code>P(y=k)</code><div class="opacity-70 mt-2">class frequency</div></div>
<div v-click border="2 solid teal-800" bg="teal-800/20" rounded-lg p-4><strong>Likelihood</strong><br/><code>P(x | y=k)</code><div class="opacity-70 mt-2">feature model</div></div>
<div v-click border="2 solid blue-800" bg="blue-800/20" rounded-lg p-4><strong>Posterior</strong><br/><code>P(y=k | x)</code><div class="opacity-70 mt-2">class after evidence</div></div>
<div v-click border="2 solid white/10" bg="white/5" rounded-lg p-4><strong>Evidence</strong><br/><code>P(x)</code><div class="opacity-70 mt-2">same for every k</div></div>
</div>

<div v-click class="mt-7 text-center" border="2 solid amber-800" bg="amber-800/20" rounded-lg p-4>Drop <code>P(x)</code> only for the arg-max: it changes normalization, not the winning class.</div>

<!--
Walk through the four named terms: the prior P(y=k) is simply the fraction of training examples belonging to class k, estimated before looking at any features; the likelihood P(x|y=k) describes how features are distributed within class k, and is the piece we must choose a model for (Gaussian, Multinomial, or Bernoulli, covered on later slides); the posterior P(y=k|x) is what we actually want — the updated class probability after observing the evidence x; and the evidence P(x) is the marginal probability of observing these particular features at all, summed or integrated over every possible class.

Let students verify why the evidence term P(x) is the same constant for every class k when comparing classes for a fixed query x — it does not depend on k, so it cannot change which class has the largest posterior, only its numeric value. That justifies replacing the equals sign with proportionality and simply taking arg max over the unnormalized product P(x|y=k)P(y=k). One common misconception to flag: dropping P(x) still produces a correct class ranking and a correct arg-max decision, but the resulting scores are not automatically calibrated probabilities that sum to 1 across classes — if calibrated probabilities are needed, the scores must be explicitly renormalized (dividing by their sum), and even then, calibration can be poor if the underlying independence assumption is badly violated.
-->

---
glowSeed: 442.5
---

# Putting the Pieces Together

<div v-click class="mt-3 max-w-5xl mx-auto rounded-xl border-2 border-blue-700 bg-blue-800/20 p-4 text-center text-xl leading-snug">
The probability that an input belongs to a class, given its features, comes from the probability of seeing those features in that class (the <strong>feature model</strong>) multiplied by the <strong>prior probability</strong> of that class.
</div>

<div v-click class="mt-3 rounded-xl border-2 border-teal-700 bg-teal-800/20 p-2 text-center">

$$P(\text{class}\mid\text{features})=\frac{P(\text{features}\mid\text{class})\times P(\text{class})}{P(\text{features})}$$

</div>

<div class="grid grid-cols-3 gap-3 mt-3 text-center text-xs">
<div v-click class="rounded-lg bg-teal-800/20 p-2"><strong>Feature model</strong><br/><code>P(features | class)</code><br/>How well do these features fit the class?</div>
<div v-click class="rounded-lg bg-violet-800/20 p-2"><strong>Prior</strong><br/><code>P(class)</code><br/>Class frequency before seeing the features.</div>
<div v-click class="rounded-lg bg-amber-800/20 p-2"><strong>Normalize</strong><br/>Divide by <code>P(features)</code><br/>Makes class probabilities sum to 1.</div>
</div>

<div class="mt-3 text-center text-xs opacity-75">To choose the most likely class, compare feature model × prior; the normalization term is the same for each class.</div>

<!--
Translate Bayes' rule into the requested plain-language recipe. For a class C, first ask how likely the observed features would be if the input really belonged to C: that is the feature model, P(features | C). Multiply by the prior P(C), the class frequency before seeing this input. That product is an unnormalized score; divide by P(features) to get the exact posterior probability. When only choosing the winning class, P(features) is identical for all classes and can be omitted from the comparison. This distinction prevents the common mistake of claiming likelihood times prior is already a normalized probability.
-->

---
glowSeed: 443
---

# Feature Model

<div v-click class="mt-16 max-w-5xl mx-auto rounded-xl border-2 border-teal-700 bg-teal-800/20 px-10 py-12 text-3xl leading-relaxed text-center">
The feature model tells Naive Bayes how to calculate the probability of observing a feature given a particular class.
</div>

<div class="mt-8 text-center text-xl opacity-75">In probability notation: the likelihood of the features given the class.</div>

$$P(\text{features}\mid\text{class})$$

<!--
Define the feature model before explaining how Naive Bayes estimates it. Given a class label, the feature model answers: how likely are the observed feature values for an example from this class? In Bayesian classification this is the likelihood P(features | class). A key distinction to carry into the next slides: a model may describe the whole set of feature values jointly; Naive Bayes later makes a simplifying assumption that lets it calculate this joint likelihood from separate per-feature likelihoods.
-->

---
glowSeed: 443.1
---

# Example: A Fruit

<div class="mt-4 text-center text-xl">Suppose we describe each fruit with three features:</div>

<div class="grid grid-cols-3 gap-4 mt-5 text-center text-lg">
<div v-click class="rounded-lg border-2 border-blue-700 bg-blue-800/20 p-4"><strong>Weight</strong><br/>150 g</div>
<div v-click class="rounded-lg border-2 border-violet-700 bg-violet-800/20 p-4"><strong>Length</strong><br/>8 cm</div>
<div v-click class="rounded-lg border-2 border-teal-700 bg-teal-800/20 p-4"><strong>Round?</strong><br/>Yes</div>
</div>

<div class="mt-6 text-center text-xl">What is the probability this fruit is an apple, given its features?</div>

<div v-click class="mt-4 rounded-xl border-2 border-amber-700 bg-amber-800/20 p-3 text-center text-lg">

$$P(\text{class}=\text{apple}\mid w=150\text{ g},l=8\text{ cm},r=\text{yes})=$$

$$\frac{P(w=150\text{ g},l=8\text{ cm},r=\text{yes}\mid\text{class}=\text{apple})\times P(\text{class}=\text{apple})}{P(w=150\text{ g},l=8\text{ cm},r=\text{yes})}$$

</div>

<div class="mt-3 text-center opacity-75">The numerator combines the feature model and the prior; the denominator normalizes the result.</div>

<!--
Walk through the example literally: the observed input has three features—weight 150 g, length 8 cm, and roundness yes. We want the probability that its class is apple given these features. Bayes' rule combines the joint feature likelihood under the apple class with the prior probability of apple, then divides by the evidence (the probability of seeing this feature combination under any class). This is the full posterior before the next slide introduces the naive assumption that approximates the joint likelihood as separate per-feature probabilities.
-->

---
glowSeed: 443.2
---

# The Naive Assumption

<div v-click class="mt-5 max-w-5xl mx-auto rounded-xl border-2 border-teal-700 bg-teal-800/20 p-6 text-center text-2xl">
If we assume that the class is apple, treat the three feature values as independent of one another.
</div>

<div class="grid grid-cols-3 gap-4 mt-8 text-center">
<div v-click class="rounded-lg border border-blue-700 bg-blue-800/20 p-4"><strong>Weight</strong><br/><span class="text-sm opacity-75">considered on its own</span></div>
<div v-click class="rounded-lg border border-violet-700 bg-violet-800/20 p-4"><strong>Length</strong><br/><span class="text-sm opacity-75">considered on its own</span></div>
<div v-click class="rounded-lg border border-teal-700 bg-teal-800/20 p-4"><strong>Round?</strong><br/><span class="text-sm opacity-75">considered on its own</span></div>
</div>

<div v-click class="mt-8 text-center text-xl" border="2 solid white/10" bg="white/5" rounded-lg p-4><strong>“Naive” means</strong> we ignore relationships between features after conditioning on the class.</div>

<!--
Explain the condition carefully: the assumption is not that weight, length, and roundness are unrelated in all fruit. It says that once we compare only apples (the class is fixed), Naive Bayes treats the feature values as independent. In reality, weight and length could still be related among apples. The model deliberately ignores such feature-to-feature relationships; the next slide shows exactly what that lets us calculate.
-->

---
glowSeed: 443.3
---

# Multiply the Feature Probabilities

<div class="mt-4 text-center text-lg">With the naive assumption, estimate each likelihood separately, then multiply:</div>

<div v-click class="mt-5 rounded-xl border-2 border-teal-700 bg-teal-800/20 p-5 text-center text-xl leading-loose">

$$P(w=150\text{ g},l=8\text{ cm},r=\text{yes}\mid\text{apple})\approx$$

$$P(w=150\text{ g}\mid\text{apple})\times P(l=8\text{ cm}\mid\text{apple})\times P(r=\text{yes}\mid\text{apple})$$

</div>

<div class="grid grid-cols-3 gap-3 mt-5 text-center text-sm">
<div v-click class="rounded-lg bg-blue-800/20 p-3">probability an apple weighs 150 g</div>
<div v-click class="rounded-lg bg-violet-800/20 p-3">probability an apple is 8 cm long</div>
<div v-click class="rounded-lg bg-teal-800/20 p-3">probability an apple is round</div>
</div>

<div v-click class="mt-5 rounded-lg border-2 border-amber-700 bg-amber-800/20 p-4 text-center">
<strong>Why make this assumption?</strong> Weight and length may be related, so the product may only approximate the true joint probability. Treating features separately makes the model much easier to estimate. Naive Bayes makes this simplifying assumption even when it is not perfectly true.
</div>

<!--
Read the approximation from left to right. The left side asks for the probability of seeing the whole feature combination in an apple. Under conditional independence, Naive Bayes approximates that joint probability with a product of three simpler likelihoods, each estimated from the apples in the training data. Use an approximation sign: if heavier apples tend also to be longer, multiplying separate probabilities will not capture that relationship and may give a different value from the true joint probability. We make this simplifying assumption in Naive Bayes because estimating a full joint feature model becomes difficult as the number of features grows. This is a modeling tradeoff, not a fact about fruit; other models can represent dependencies.
-->

---
glowSeed: 443.5
---

# Fitting the Likelihood Model

<div class="mt-3 text-center text-lg">Use the training data to estimate how each feature behaves <strong>within each class</strong>.</div>

<div class="grid grid-cols-3 gap-4 mt-4 items-stretch">
<div v-click class="rounded-xl border-2 border-blue-700 bg-blue-800/20 p-4 text-base leading-snug">
<div class="text-center text-lg font-bold text-blue-300">Continuous</div>
<div class="mt-3"><strong>Choose a distribution</strong><br/>Often Gaussian, or another suitable continuous probability distribution.</div>
<div class="mt-3"><strong>Fit it to training values</strong><br/>For a Gaussian, estimate the mean and variance for each feature in each class.</div>
</div>
<div v-click class="rounded-xl border-2 border-violet-700 bg-violet-800/20 p-4 text-base leading-snug">
<div class="text-center text-lg font-bold text-violet-300">Binary</div>
<div class="mt-3"><strong>Use a Bernoulli model</strong></div>
<div class="mt-2">For each class, estimate the fraction of its training examples where this feature is 1.</div>
</div>
<div v-click class="rounded-xl border-2 border-teal-700 bg-teal-800/20 p-4 text-base leading-snug">
<div class="text-center text-lg font-bold text-teal-300">Counts</div>
<div class="mt-3"><strong>Use a Multinomial model</strong></div>
<div class="mt-2">For each class, estimate word or event probabilities from their training counts. Smoothing gives unseen words a small nonzero probability.</div>
</div>
</div>

<div v-click class="mt-4 rounded-lg border-2 border-white/10 bg-white/5 p-3 text-center text-base">The likelihood model is learned from training data; then it scores how likely a new input’s features are under each class.</div>

<!--
Answer how the feature model is obtained: select a distribution that matches the feature type, then estimate its parameters from training data, separately within each class. For continuous measurements, Gaussian Naive Bayes estimates a mean and variance for each feature and class; a different continuous density can be used when more appropriate. For binary values, Bernoulli Naive Bayes estimates the fraction of examples in each class where the feature is 1. For count vectors such as word counts, Multinomial Naive Bayes estimates per-class word probabilities from counts, typically with additive smoothing so an unseen word does not get likelihood zero. This is model fitting; the fitted distributions are then used to calculate likelihoods for new examples.
-->

---
glowSeed: 444
---

# Gaussian Naive Bayes · Continuous Features

<div class="grid grid-cols-2 gap-7 mt-3 items-center">
<div>
<div v-click border="2 solid blue-800" bg="blue-800/20" rounded-lg p-4 class="text-base">

$$P(x_j\mid y=k)=\frac{1}{\sqrt{2\pi\sigma_{jk}^2}}\exp\!\left[-\frac{(x_j-\mu_{jk})^2}{2\sigma_{jk}^2}\right]$$
$$\hat\mu_{jk}=\frac1{n_k}\sum_{i:y_i=k}x_{ij},\quad \hat\sigma_{jk}^2=\frac1{n_k}\sum_{i:y_i=k}(x_{ij}-\hat\mu_{jk})^2$$

</div>

```python
from sklearn.datasets import make_classification
from sklearn.naive_bayes import GaussianNB

X, y = make_classification(
    n_samples=200, n_features=4,
    n_informative=3, n_redundant=0,
    random_state=0)
model = GaussianNB().fit(X, y)
print(model.theta_, model.var_)
print(model.predict_proba(X[:3]))
```
</div>
<svg role="img" aria-label="Two Gaussian likelihood curves for one feature and a query where the blue class has higher likelihood" viewBox="0 0 470 310" class="w-full">
  <line x1="35" y1="270" x2="445" y2="270" stroke="#64748b"/>
  <path d="M60 267 C125 267 125 95 190 95 C255 95 255 267 320 267" fill="none" stroke="#fb923c" stroke-width="5"/>
  <path d="M205 267 C267.5 267 267.5 60 330 60 C392.5 60 392.5 267 455 267" fill="none" stroke="#60a5fa" stroke-width="5"/>
  <line x1="300" y1="35" x2="300" y2="270" stroke="#f8fafc" stroke-dasharray="7 5"/><text x="308" y="35" fill="#f8fafc">query xⱼ</text>
  <text x="90" y="55" fill="#fdba74">class 0</text><text x="350" y="80" fill="#93c5fd">class 1</text>
</svg>
</div>

<!--
For continuous features, Gaussian Naive Bayes models P(x_j | y=k) as a normal distribution with its own mean mu_jk and variance sigma_jk^2 for every combination of feature j and class k. Fitting this model is just the Gaussian maximum-likelihood estimate from the probability unit, repeated independently for each class and feature: mu_jk is the sample mean of feature j among training examples in class k, and sigma_jk^2 is the sample variance of feature j within that same class. There is no iterative optimization at all — these are closed-form statistics computed in a single pass over the data, which is why fitting Naive Bayes is so much faster than fitting logistic regression.

Inspect `model.theta_` (the per-class, per-feature means) and `model.var_` (the per-class, per-feature variances) live after fitting, and emphasize that these are simple, directly interpretable summary statistics — not abstract gradient-learned weights whose meaning requires the model's full context to interpret. To classify a new point, evaluate the Gaussian density formula for each feature under each class's fitted mean and variance, multiply those per-feature likelihoods together (the naive independence assumption in action) and by the class prior, and pick the class with the largest resulting score, exactly as in the arg-max formula from two slides ago.
-->


---
glowSeed: 445
---

# Counts, Binary Features, and Smoothing

<div class="grid grid-cols-2 gap-7 mt-2">
<div>
<div class="grid grid-cols-2 gap-3 text-sm">
<div v-click border="2 solid violet-800" bg="violet-800/20" rounded-lg p-4><strong>Multinomial NB</strong><br/>word or event counts</div>
<div v-click border="2 solid blue-800" bg="blue-800/20" rounded-lg p-4><strong>Bernoulli NB</strong><br/>presence / absence</div>
</div>
<div v-click class="mt-4" border="2 solid amber-800" bg="amber-800/20" rounded-lg p-4>

$$\begin{gathered}P(x_j=v\mid y=k)=\\\frac{\operatorname{count}(x_j=v,y=k)+\alpha}{\operatorname{count}(y=k)+\alpha|V|}\end{gathered}$$

</div>
<div v-click class="mt-4 text-sm" border="2 solid red-800" bg="red-800/20" rounded-lg p-4><strong>Without smoothing:</strong> one unseen word gives probability 0, collapsing the entire product.</div>
</div>

```python
from sklearn.feature_extraction import text
from sklearn.naive_bayes import MultinomialNB

docs = ["free money click", "project meeting",
        "win free prize", "project deadline"]
y = [1, 0, 1, 0]
vectorizer = text.CountVectorizer()
X = vectorizer.fit_transform(docs)
model = MultinomialNB(alpha=1).fit(X, y)
new = vectorizer.transform(["free prize click"])
print(model.predict(new), model.predict_proba(new))
```
</div>

<!--
Two more Naive Bayes variants handle discrete features instead of continuous ones. Multinomial NB models P(x_j=v | y=k) from counts — how often word or event v occurs in documents of class k — and is the standard choice for text classification represented as word-count vectors (a bag-of-words model). Bernoulli NB instead models simple presence/absence of each feature, ignoring how many times it occurs, which suits binary indicator features. Both need an estimate of P(x_j=v | y=k) built from counts in the training data: count how often value v occurs with class k, divide by the total count for class k.

Demonstrate zero-probability collapse numerically first: without smoothing, if a word never appeared in any spam-labeled training document, its estimated P(word | spam) is exactly 0, and because Naive Bayes multiplies per-feature likelihoods together, that single zero collapses the entire product to zero regardless of how strongly every other word points toward spam — one unseen word can silently veto an otherwise confident prediction. Laplace (additive) smoothing fixes this by adding a small pseudo-count alpha to every count before dividing, and adding alpha times the vocabulary size |V| to the denominator so the probabilities still sum to 1; alpha=1 behaves as if every vocabulary item had already been seen once in every class, guaranteeing no probability is ever exactly zero. Text spam filtering, as demonstrated in the code, is the canonical application of Multinomial NB and the historical reason Naive Bayes became popular.
-->

---
glowSeed: 446
---

# Naive Bayes vs. Logistic Regression

<div class="grid grid-cols-[10rem_1fr_1fr] gap-2 mt-5 text-sm">
<div></div><div class="font-bold text-teal-300">Naive Bayes</div><div class="font-bold text-blue-300">Logistic Regression</div>
<div class="text-right pr-2 font-bold">Models</div><div v-click class="p-3 rounded bg-teal-500/20"><code>P(x | y)</code> then Bayes</div><div v-click class="p-3 rounded bg-blue-500/20"><code>P(y | x)</code> directly</div>
<div class="text-right pr-2 font-bold">Type</div><div v-click class="p-3 rounded bg-teal-500/20">generative</div><div v-click class="p-3 rounded bg-blue-500/20">discriminative</div>
<div class="text-right pr-2 font-bold">Fit</div><div v-click class="p-3 rounded bg-teal-500/20">closed-form statistics</div><div v-click class="p-3 rounded bg-blue-500/20">iterative optimization</div>
<div class="text-right pr-2 font-bold">Thrives on</div><div v-click class="p-3 rounded bg-teal-500/20">small, sparse, high-d data</div><div v-click class="p-3 rounded bg-blue-500/20">correlated predictive features</div>
<div class="text-right pr-2 font-bold">Risk</div><div v-click class="p-3 rounded bg-teal-500/20">independence distorts probabilities</div><div v-click class="p-3 rounded bg-blue-500/20">more data and fitting time</div>
</div>

<div v-click class="mt-7 text-center" border="2 solid white/10" bg="white/5" rounded-lg p-4>Under certain Gaussian assumptions, both converge to the same boundary with abundant data—but reach it differently and behave differently when data is scarce.</div>

<!--
Consolidate the generative/discriminative distinction introduced at the start of this deck. Naive Bayes models P(x|y) then inverts with Bayes' rule (generative); logistic regression models P(y|x) directly by fitting a boundary (discriminative). Naive Bayes fits via closed-form statistics — means, variances, or counts — computed in one pass, while logistic regression fits via iterative gradient-based optimization of a convex loss. Naive Bayes tends to thrive on small, sparse, high-dimensional data (like text with a huge vocabulary but few documents) precisely because its per-feature estimates need little data each; logistic regression tends to do better when features are meaningfully correlated and there is enough data to estimate their joint interactions.

A classical asymptotic result (Ng & Jordan, 2001) states that under certain Gaussian generative assumptions, Naive Bayes and logistic regression converge to the exact same decision boundary as training data grows without bound — but they get there differently and behave very differently when data is scarce: Naive Bayes typically reaches its (higher-bias, lower-variance) asymptotic error rate with far fewer examples, while logistic regression needs more data but usually achieves a better asymptotic error rate, especially when the independence assumption is badly violated. Plant this generative-versus-discriminative vocabulary now — it recurs for every generative model encountered later in the course, including generative approaches in unsupervised learning.
-->

---
layout: center
class: text-center
glowSeed: 447
---

# Naive Bayes in One View

<div class="grid grid-cols-2 gap-4 mt-7 text-left">
<div v-click border="2 solid teal-800" bg="teal-800/20" rounded-lg p-5><strong>Invert</strong><div class="text-sm opacity-80 mt-2">likelihood × prior becomes posterior ranking</div></div>
<div v-click border="2 solid violet-800" bg="violet-800/20" rounded-lg p-5><strong>Factor</strong><div class="text-sm opacity-80 mt-2">conditional independence makes the joint tractable</div></div>
<div v-click border="2 solid blue-800" bg="blue-800/20" rounded-lg p-5><strong>Match the variant</strong><div class="text-sm opacity-80 mt-2">Gaussian, Multinomial, or Bernoulli</div></div>
<div v-click border="2 solid amber-800" bg="amber-800/20" rounded-lg p-5><strong>Smooth</strong><div class="text-sm opacity-80 mt-2">avoid zero-probability collapse</div></div>
</div>

<div v-click class="mt-8 text-lg">Next: <strong>Decision Trees</strong> — interpretable if/else rules with no probability model or distance metric.</div>

<!--
Close the three-strategy progression covered across this module so far: discriminative optimization (logistic regression, fitting a boundary directly), instance-based memorization (k-NN, voting among stored neighbors), and generative probability (Naive Bayes, modeling how each class generates features and inverting with Bayes' rule). Recap the four-step recipe on screen: invert the likelihood-times-prior into a posterior ranking via Bayes' theorem; factor the joint likelihood into a tractable product using the conditional independence assumption; match the variant (Gaussian for continuous features, Multinomial for counts, Bernoulli for presence/absence) to the data type; and smooth the count-based estimates to avoid zero-probability collapse from unseen feature values.

Preview the next deck, Decision Trees: a completely different, rule-based strategy that needs no probability model, no distance metric, and no optimization — just a sequence of interpretable if/else questions on individual features. Also flag ahead that a single decision tree, despite being simple and interpretable, will later serve as the base learner inside random forests and gradient boosting in the Ensemble Methods unit, much as Gaussian Naive Bayes' simple per-feature statistics make it fast enough to serve as a baseline for almost any classification problem.
-->

---
glowSeed: 447.5
---

# Spam Detection Setup

<div class="mt-4 text-center text-lg">Classes: <strong>spam</strong> and <strong>not spam</strong></div>

<div class="grid grid-cols-3 gap-3 mt-5 text-center text-base">
<div v-click class="rounded-lg border-2 border-blue-700 bg-blue-800/20 p-4"><strong>free</strong><br/>word appears</div>
<div v-click class="rounded-lg border-2 border-violet-700 bg-violet-800/20 p-4"><strong>prize</strong><br/>word appears</div>
<div v-click class="rounded-lg border-2 border-teal-700 bg-teal-800/20 p-4"><strong>meeting</strong><br/>word appears</div>
</div>

<div v-click class="mt-6 rounded-xl border-2 border-white/10 bg-white/5 p-5 text-center text-xl">
New message: <strong>“free prize”</strong>
</div>

<div class="mt-6 text-center text-lg">Estimate a score for each class:</div>

<div class="text-center text-xl"><code>score(class) = P(message | class) × P(class)</code></div>

<div class="mt-3 text-center text-sm opacity-75">The class with the larger score is the prediction. Normalize the scores if you want probabilities.</div>

<!--
Set up one message and use it for both event models. The vocabulary has three possible words. The new message contains free and prize, but not meeting. We will compare the spam and not-spam scores. The two examples use the same Bayes recipe but represent the message differently: Multinomial NB uses counts, while Bernoulli NB uses presence and absence.
-->

---
glowSeed: 447.6
---

# Spam Detection Recipe: Build Likelihoods

<div class="mt-3 text-center text-lg">Extract the likelihoods from the training messages, separately for each class.</div>

<div class="grid grid-cols-2 gap-5 mt-5 items-stretch">
<div v-click class="rounded-xl border-2 border-violet-700 bg-violet-800/20 p-5 text-base leading-snug">
<div class="text-center text-xl font-bold text-violet-300">Multinomial NB</div>
<div class="mt-4"><strong>Count tokens</strong><br/>For each class, count how many times each word appears in all of its messages.</div>
<div class="mt-4"><strong>Divide by all tokens</strong><br/><code>P(free | spam) = free tokens in spam ÷ all spam tokens</code></div>
<div class="mt-4 text-sm opacity-80">Repeated words count repeatedly.</div>
</div>
<div v-click class="rounded-xl border-2 border-teal-700 bg-teal-800/20 p-5 text-base leading-snug">
<div class="text-center text-xl font-bold text-teal-300">Bernoulli NB</div>
<div class="mt-4"><strong>Count messages</strong><br/>For each class, count how many messages contain each word at least once.</div>
<div class="mt-4"><strong>Divide by messages</strong><br/><code>P(free | spam) = spam messages containing free ÷ all spam messages</code></div>
<div class="mt-4 text-sm opacity-80">Repeated words still count as one present feature.</div>
</div>
</div>

<div v-click class="mt-5 rounded-lg border-2 border-amber-700 bg-amber-800/20 p-4 text-center text-lg">These class-specific feature probabilities are the likelihood pieces of Naive Bayes. Add smoothing when a count is zero.</div>

<!--
This is the first recipe step. Use the training data, separated by class. Multinomial NB treats every token occurrence as an event, so its denominator is the total number of tokens in that class. Bernoulli NB treats each message as a set of yes/no indicators, so its denominator is the number of messages in that class. In both cases, the result is a likelihood such as P(free | spam), which tells us how compatible a feature is with a class.
-->

---
glowSeed: 447.7
---

# Spam Detection Recipe: Extract Priors

<div class="mt-4 text-center text-lg">The prior is the class probability before looking at a new message.</div>

<div class="grid grid-cols-2 gap-5 mt-6 text-center">
<div v-click class="rounded-xl border-2 border-red-700 bg-red-800/20 p-6">
<div class="text-xl font-bold text-red-300">Spam</div>
<div class="mt-4 text-2xl"><code>40 spam messages</code></div>
<div class="mt-3 text-xl"><code>P(spam) = 40 ÷ 100 = .40</code></div>
</div>
<div v-click class="rounded-xl border-2 border-blue-700 bg-blue-800/20 p-6">
<div class="text-xl font-bold text-blue-300">Not spam</div>
<div class="mt-4 text-2xl"><code>60 not-spam messages</code></div>
<div class="mt-3 text-xl"><code>P(not spam) = 60 ÷ 100 = .60</code></div>
</div>
</div>

<div v-click class="mt-7 rounded-lg border-2 border-white/10 bg-white/5 p-4 text-center text-lg"><code>prior(class) = number of training messages in the class ÷ total training messages</code></div>

<div class="mt-4 text-center text-sm opacity-75">The prior reflects class balance. It is estimated once from the training labels and does not depend on the new message’s words.</div>

<!--
This is the second recipe step. Count the labels in the training set, regardless of which words appear. If 40 of 100 training messages are spam, the spam prior is .40; if 60 are not spam, that prior is .60. Priors matter because a class that is common before seeing the message gets a larger starting score.
-->

---
glowSeed: 447.8
---

# Spam Detection Recipe: Combine and Classify

<div class="mt-3 text-center text-lg">For the new message “free prize,” multiply its likelihood by each class prior.</div>

<div class="grid grid-cols-2 gap-5 mt-5 text-sm">
<div v-click class="rounded-xl border-2 border-red-700 bg-red-800/20 p-5">
<div class="text-center text-xl font-bold text-red-300">Spam score</div>
<div class="mt-4 text-center"><code>P(free | spam) × P(prize | spam) × P(spam)</code></div>
<div class="mt-3 text-center text-xl"><code>.30 × .20 × .40 = .024</code></div>
</div>
<div v-click class="rounded-xl border-2 border-blue-700 bg-blue-800/20 p-5">
<div class="text-center text-xl font-bold text-blue-300">Not-spam score</div>
<div class="mt-4 text-center"><code>P(free | not spam) × P(prize | not spam) × P(not spam)</code></div>
<div class="mt-3 text-center text-xl"><code>.05 × .01 × .60 = .0003</code></div>
</div>
</div>

<div v-click class="mt-5 rounded-xl border-2 border-teal-700 bg-teal-800/20 p-5 text-center text-lg">
<strong>Normalize the scores:</strong><br/>
<code>P(spam | message) = .024 ÷ (.024 + .0003) ≈ .988</code><br/>
<code>P(not spam | message) ≈ .012</code>
</div>

<div class="mt-4 text-center text-lg">The larger posterior wins: classify the message as <strong>spam</strong>.</div>

<!--
This is the final recipe step. For each class, multiply the feature likelihoods and the prior to get an unnormalized score. The scores are .024 for spam and .0003 for not spam, so spam wins. To turn scores into probabilities, divide each by their sum. This is Bayes' rule in action: likelihood times prior, followed by normalization. Bernoulli NB follows the same steps, but includes the probabilities of both present and absent words instead of using word counts.
-->

---
layout: center
class: text-center
glowSeed: 448
---

# Questions?

<div class="mt-6 text-xl opacity-80">Naive Bayes: model the class, factor the features, then apply Bayes’ theorem.</div>

<div class="mt-10 text-sm opacity-60">Next: Decision Trees</div>
