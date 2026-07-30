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

<div class="mt-12 max-w-4xl mx-auto" border="2 solid teal-800" bg="teal-800/20" rounded-lg px-8 py-6>

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

<div border="2 solid blue-800" bg="blue-800/20" rounded-lg px-5 py-3>

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
glowSeed: 443
---

# The “Naive” Assumption

<div class="grid grid-cols-2 gap-8 mt-3 items-center">
<div>
<div border="2 solid teal-800" bg="teal-800/20" rounded-lg p-4>

$$P(x_1,\ldots,x_d\mid y=k)\approx\prod_{j=1}^{d}P(x_j\mid y=k)$$
$$\hat y=\arg\max_k P(y=k)\prod_jP(x_j\mid y=k)$$

</div>
<v-clicks>

- Assume features are conditionally independent given the class
- Usually false—“New” and “York” clearly co-occur
- Yet class rankings can remain useful even when probabilities are distorted

</v-clicks>
</div>
<svg role="img" aria-label="General feature dependence compared with the Naive Bayes star graph where features connect only to class" viewBox="0 0 500 310" class="w-full">
  <text x="75" y="28" fill="#fb923c">general joint model</text><text x="330" y="28" fill="#2dd4bf">Naive Bayes</text>
  <g stroke="#fb923c" stroke-width="2"><line x1="125" y1="140" x2="70" y2="70"/><line x1="125" y1="140" x2="190" y2="70"/><line x1="125" y1="140" x2="70" y2="225"/><line x1="125" y1="140" x2="190" y2="225"/><line x1="70" y1="70" x2="190" y2="225"/><line x1="190" y1="70" x2="70" y2="225"/></g>
  <g stroke="#2dd4bf" stroke-width="3"><line x1="375" y1="140" x2="315" y2="70"/><line x1="375" y1="140" x2="435" y2="70"/><line x1="375" y1="140" x2="315" y2="225"/><line x1="375" y1="140" x2="435" y2="225"/></g>
  <g fill="#f8fafc"><circle cx="125" cy="140" r="24"/><circle cx="70" cy="70" r="15"/><circle cx="190" cy="70" r="15"/><circle cx="70" cy="225" r="15"/><circle cx="190" cy="225" r="15"/><circle cx="375" cy="140" r="24"/><circle cx="315" cy="70" r="15"/><circle cx="435" cy="70" r="15"/><circle cx="315" cy="225" r="15"/><circle cx="435" cy="225" r="15"/></g>
  <text x="115" y="147" fill="#0f172a">y</text><text x="365" y="147" fill="#0f172a">y</text>
</svg>
</div>

<!--
Be candid with students: conditional independence given the class is a modeling assumption chosen for tractability, not a theorem that is ever exactly true of real data. Without it, estimating the full joint P(x1,...,xd | y=k) requires exponentially many parameters as d grows — one probability for every possible combination of feature values within each class — which is infeasible to estimate from any realistic amount of data. The naive assumption factors that joint into a simple product of one-dimensional distributions, P(x_j | y=k) for each feature separately, which needs only a number of parameters that grows linearly in d, and each of those one-dimensional distributions can be estimated reliably from far less data.

The assumption is usually false in an obvious way — flag this explicitly as the classic misconception check: in text classification, the words "New" and "York" are strongly correlated (given the class "geography," seeing "New" makes "York" much more likely than its marginal frequency would suggest), yet Naive Bayes treats them as independent and multiplies their individual probabilities as if they were unrelated. Despite that, Naive Bayes remains a strong, fast, widely used baseline in practice — classification only requires the posterior ranking across classes to put the correct class on top, not for the individual probability values to be well-calibrated, and errors from violated independence often distort all classes' scores in a similar, partially self-cancelling way.
-->

---
glowSeed: 443.5
---

# A Worked Posterior by Hand

<div class="grid grid-cols-2 gap-7 mt-3 items-center">
<div>

<div border="2 solid white/10" bg="white/5" rounded-lg p-4 class="text-sm">
Email contains "free" ($x_1{=}1$) and "click" ($x_2{=}1$)
</div>

<div class="mt-3 text-sm">

$$P(\text{spam})=.4,\quad P(\text{ham})=.6$$
$$P(x_1{=}1\mid\text{spam})=.7,\ P(x_1{=}1\mid\text{ham})=.1$$
$$P(x_2{=}1\mid\text{spam})=.6,\ P(x_2{=}1\mid\text{ham})=.2$$

</div>

<v-clicks>

- spam score $=.4\times.7\times.6=.168$
- ham score $=.6\times.1\times.2=.012$
- normalize: $.168+.012=.18$
- $P(\text{spam}\mid x)=.168/.18\approx.933$

</v-clicks>

</div>

```python
p_spam, p_ham = 0.4, 0.6
lik_spam = 0.7 * 0.6      # P(x1|spam) * P(x2|spam)
lik_ham = 0.1 * 0.2       # P(x1|ham)  * P(x2|ham)

score_spam = p_spam * lik_spam   # 0.168
score_ham = p_ham * lik_ham      # 0.012

total = score_spam + score_ham   # 0.18
posterior_spam = score_spam / total
assert round(posterior_spam, 3) == 0.933
```

</div>

<!--
Make the abstract arg-max formula from the previous two slides completely concrete with real numbers. Priors: 40% of training emails are spam, 60% are ham (not spam). Likelihoods, estimated from training data separately per class: among spam emails, "free" appears in 70% and "click" appears in 60%; among ham emails, "free" appears in only 10% and "click" in 20%. The naive assumption lets us multiply these two per-word likelihoods together within each class instead of needing the joint probability of "free" and "click" co-occurring.

Unnormalized spam score: P(spam) × P(free|spam) × P(click|spam) = .4 × .7 × .6 = .168. Unnormalized ham score: P(ham) × P(free|ham) × P(click|ham) = .6 × .1 × .2 = .012. Spam's score is larger, so the model predicts spam even before normalizing — that arg-max decision is all classification strictly requires. To report a calibrated probability, divide each score by their sum, .18: P(spam|x) = .168/.18 ≈ .933 and P(ham|x) = .012/.18 ≈ .067. Point out how the two moderately-informative words compound multiplicatively into a confident 93% posterior — this is exactly why Naive Bayes can be a surprisingly strong spam filter with very little training data.
-->

---
glowSeed: 444
---

# Gaussian Naive Bayes · Continuous Features

<div class="grid grid-cols-2 gap-7 mt-3 items-center">
<div>
<div border="2 solid blue-800" bg="blue-800/20" rounded-lg p-4>

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
  <path d="M45 267 C115 260 125 75 205 75 C280 75 285 260 340 267" fill="none" stroke="#fb923c" stroke-width="5"/>
  <path d="M150 267 C220 258 240 45 325 45 C405 45 410 255 440 267" fill="none" stroke="#60a5fa" stroke-width="5"/>
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
<div class="mt-4" border="2 solid amber-800" bg="amber-800/20" rounded-lg p-4>

$$P(x_j=v\mid y=k)=\frac{\operatorname{count}(x_j=v,y=k)+\alpha}{\operatorname{count}(y=k)+\alpha|V|}$$

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
<div class="text-right pr-2 font-bold">Models</div><div class="p-3 rounded bg-teal-500/20"><code>P(x | y)</code> then Bayes</div><div class="p-3 rounded bg-blue-500/20"><code>P(y | x)</code> directly</div>
<div class="text-right pr-2 font-bold">Type</div><div class="p-3 rounded bg-teal-500/20">generative</div><div class="p-3 rounded bg-blue-500/20">discriminative</div>
<div class="text-right pr-2 font-bold">Fit</div><div class="p-3 rounded bg-teal-500/20">closed-form statistics</div><div class="p-3 rounded bg-blue-500/20">iterative optimization</div>
<div class="text-right pr-2 font-bold">Thrives on</div><div class="p-3 rounded bg-teal-500/20">small, sparse, high-d data</div><div class="p-3 rounded bg-blue-500/20">correlated predictive features</div>
<div class="text-right pr-2 font-bold">Risk</div><div class="p-3 rounded bg-teal-500/20">independence distorts probabilities</div><div class="p-3 rounded bg-blue-500/20">more data and fitting time</div>
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
