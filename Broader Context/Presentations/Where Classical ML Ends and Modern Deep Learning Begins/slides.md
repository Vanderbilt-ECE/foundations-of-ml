---
theme: default
highlighter: shiki
css: unocss
colorSchema: dark
title: 'Where Classical ML Ends and Modern Deep Learning Begins'
info: |
  ## Where Classical ML Ends and Modern Deep Learning Begins
  Choose tools from the problem—not from fashion
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
glowSeed: 1050
---

# Where Classical ML Ends and Modern Deep Learning Begins

### Choose tools from the problem—not from fashion

<div class="pt-8 opacity-80 text-lg">Broader Context · Foundations of Machine Learning</div>

<div class="mt-14 flex justify-center gap-4" aria-hidden="true">
<div class="w-28 h-3 rounded-full bg-teal-400/70"></div>
<div class="w-20 h-3 rounded-full bg-blue-400/60"></div>
<div class="w-14 h-3 rounded-full bg-violet-400/50"></div>
</div>

<!--
This closing deck of the technical curriculum steps back and asks a practical question you will face on nearly every real project: given everything covered this semester — linear and logistic regression, trees and ensembles, clustering and dimensionality reduction, and now the fairness and failure-mode material — when should you reach for one of those "classical" methods, and when does the added complexity of a deep neural network actually pay for itself? This is not an abstract debate; it directly affects cost, timeline, interpretability, and whether a project succeeds at all with the data actually available.

The deck moves through four ideas: first, that the classical/deep boundary is a convention rather than a sharp theoretical line — a small neural network and logistic regression are close cousins; second, concrete conditions under which classical methods remain the stronger default, especially for tabular data; third, the specific structural reasons deep learning changed the landscape for unstructured data like images, audio, and text; and fourth, a practical decision framework you can apply directly, plus the reminder that everything else you learned this semester — the mathematical foundations and methodology — transfers to both regimes without modification.
-->

---
glowSeed: 1051
---

# The Boundary Is Fuzzy

<div class="grid grid-cols-3 gap-4 mt-6">
<div v-click border="2 solid teal-800" bg="teal-800/20" rounded-lg p-4>
<div class="font-bold text-teal-300 mb-2">Classical ML</div>
<div class="text-sm leading-relaxed opacity-90">Linear/logistic regression, trees, SVMs, ensembles (random forests, gradient boosting), clustering, PCA — comparatively compact models, often with a handful to a few thousand parameters.</div>
</div>
<div v-click border="2 solid blue-800" bg="blue-800/20" rounded-lg p-4>
<div class="font-bold text-blue-300 mb-2">Deep learning</div>
<div class="text-sm leading-relaxed opacity-90">Composed neural networks — many layers of learned linear transformations plus nonlinearities — with learned internal representations and typically millions to billions of parameters.</div>
</div>
<div v-click border="2 solid amber-800" bg="amber-800/20" rounded-lg p-4>
<div class="font-bold text-amber-300 mb-2">Convention, not theorem</div>
<div class="text-sm leading-relaxed opacity-90">There is no formal threshold of "layers" or "parameters" that separates the two categories — the line is drawn by community usage, not mathematics.</div>
</div>
</div>

<div v-click class="mt-6" border="2 solid white/10" bg="white/5" rounded-lg px-4 py-3>

$$
\underbrace{\hat{y} = \sigma(w^\top x + b)}_{\text{logistic regression}} \qquad\Longleftrightarrow\qquad \underbrace{\hat{y} = \sigma(W_2\,\sigma(W_1 x + b_1) + b_2)}_{\text{one-hidden-layer neural network}}
$$

<div class="text-sm opacity-85 mt-2">A single-layer network with a sigmoid output <em>is</em> logistic regression. Add one hidden layer with a nonlinearity, and you already have a (shallow) neural network — the "classical" and "deep" labels are describing two ends of one continuous family, not two disconnected fields.</div>
</div>

<!--
It is tempting to treat "classical ML" and "deep learning" as two separate disciplines with a clean dividing line, but structurally that line does not exist. The equation makes this concrete: logistic regression is exactly a neural network with zero hidden layers — an input, a linear transformation, and a sigmoid. Add a single hidden layer with a nonlinearity, and you already have what the field calls a (shallow) neural network. Keep stacking layers, and at some informal, community-dependent point — usually somewhere past a handful of layers, or when learned intermediate representations start doing real work — people start calling it "deep learning." There is no theorem that draws this line; it is convention, shaped by historical usage as much as by any technical property.

Do not walk away from this course treating classical methods as disposable stepping stones on the way to "real" machine learning — they are not beginner exercises superseded by neural networks; they are often the objectively better engineering choice, for reasons the next slide makes concrete. The point of this slide is to reframe the classical/deep question away from "which is more advanced" (a status question) and toward "which is the better tool for this specific problem" (an engineering question) — which is the question the rest of this deck actually answers.
-->

---
glowSeed: 1052
---

# When Classical ML Is Often Better

<div class="grid grid-cols-2 gap-4 mt-6">
<div v-click border="2 solid teal-800" bg="teal-800/20" rounded-lg p-4>
<div class="font-bold text-teal-300 mb-2">Tabular data</div>
<div class="text-sm leading-relaxed opacity-90">Gradient-boosted trees (XGBoost, LightGBM) and random forests remain formidable, often winning defaults on structured spreadsheet-style data with heterogeneous feature types.</div>
</div>
<div v-click border="2 solid blue-800" bg="blue-800/20" rounded-lg p-4>
<div class="font-bold text-blue-300 mb-2">Small datasets</div>
<div class="text-sm leading-relaxed opacity-90">Lower-capacity methods need far fewer examples to generalize — recall the bias-variance tradeoff: a high-capacity deep network on a few hundred rows will overfit badly.</div>
</div>
<div v-click border="2 solid amber-800" bg="amber-800/20" rounded-lg p-4>
<div class="font-bold text-amber-300 mb-2">Interpretability requirements</div>
<div class="text-sm leading-relaxed opacity-90">Linear models and shallow trees can be read directly (recall the previous deck); this matters for regulated domains like lending and healthcare with legal explanation requirements.</div>
</div>
<div v-click border="2 solid violet-800" bg="violet-800/20" rounded-lg p-4>
<div class="font-bold text-violet-300 mb-2">Limited compute and iteration speed</div>
<div class="text-sm leading-relaxed opacity-90">Training and serving classical models is usually orders of magnitude cheaper, letting you run more experiments per day of engineering time.</div>
</div>
</div>

<!--
These four conditions are not a preference — they are a direct consequence of ideas already covered this semester. Tabular data (rows of heterogeneous numeric and categorical columns, like customer records or lab tests) tends to favor tree-based ensembles because trees naturally handle mixed feature types, ignore irrelevant features, and require little feature scaling, while neural networks generally need larger, more homogeneous input spaces (like pixel grids) to exploit their representation-learning advantage — this is a well-documented empirical pattern, not a hard theoretical guarantee, and is still an active area of research (some recent tabular-specific architectures narrow this gap).

Small datasets connect directly to the bias-variance tradeoff from Core ML Concepts: model capacity has to be matched to the amount of data available, and a deep network's very large parameter count is exactly the kind of high-capacity model that will memorize noise and overfit catastrophically on a few hundred or even a few thousand training rows, while a regularized linear model or a modestly sized random forest generalizes far better in that regime. Interpretability requirements are a direct callback to the previous deck: if you need to produce a legally defensible adverse-action notice for a loan denial, a model whose coefficients or tree splits ARE the explanation is a much easier compliance story than a deep network needing a separate post-hoc SHAP analysis layered on top. Limited compute is a practical, often underweighted factor: a gradient-boosted tree trains in seconds to minutes on a laptop, letting you iterate through many feature-engineering ideas per day, while a deep model may need specialized hardware and hours-to-days per training run — that iteration speed difference often matters more to a project's success than a small accuracy gap. Next, the flip side: where these classical advantages stop applying.
-->

---
glowSeed: 1053
---

# Where Deep Learning Changed the Landscape

<div class="grid grid-cols-2 gap-8 items-start">
<div>
<div class="space-y-2 mt-4 text-sm">
<div v-click border="2 solid white/5" bg="white/5" rounded-lg px-3 py-2>
<span class="font-bold text-teal-300">Unstructured input</span>
<span class="opacity-85"> — Images, audio, and text lack tabular structure; deep networks learn hierarchical features directly from raw pixels, waveforms, or tokens.</span>
</div>
<div v-click border="2 solid white/5" bg="white/5" rounded-lg px-3 py-2>
<span class="font-bold text-blue-300">Favorable scaling</span>
<span class="opacity-85"> — Larger networks trained on more data and compute keep improving well past the point where classical methods plateau.</span>
</div>
<div v-click border="2 solid white/5" bg="white/5" rounded-lg px-3 py-2>
<span class="font-bold text-amber-300">Less manual feature engineering</span>
<span class="opacity-85"> — Classical pipelines needed hand-designed features (edge detectors, n-grams); deep networks learn comparable features automatically.</span>
</div>
</div>
</div>
<div>
<svg role="img" aria-label="Line chart contrasting model accuracy versus dataset size: classical ML accuracy rises quickly then plateaus, while deep learning accuracy starts lower on small data but keeps rising and overtakes classical ML on large data" viewBox="0 0 500 310" class="w-full max-w-xl mx-auto mt-7">
  <line x1="55" y1="260" x2="470" y2="260" stroke="#64748b" stroke-width="2"/><line x1="55" y1="35" x2="55" y2="260" stroke="#64748b" stroke-width="2"/>
  <path d="M60 220 C110 120,160 90,220 82 S340 78,465 76" fill="none" stroke="#2dd4bf" stroke-width="5"/>
  <path d="M60 245 C150 220,230 150,300 100 S420 45,465 35" fill="none" stroke="#60a5fa" stroke-width="4" stroke-dasharray="9 7"/>
  <g fill="#cbd5e1" style="font-size: 12px" text-anchor="middle"><text x="65" y="285">small data</text><text x="261" y="285">medium data</text><text x="457" y="285">large data</text></g>
  <g style="font-size: 12px"><text x="345" y="70" fill="#5eead4">classical ML (plateaus)</text><text x="330" y="30" fill="#93c5fd">deep learning (keeps improving)</text></g>
</svg>
<div class="text-xs opacity-70 text-center mt-1">A domain-dependent empirical pattern for unstructured data — not a universal law.</div>
</div>
</div>

<!--
Unstructured data — images (grids of raw pixel values with no inherent column meaning), audio (raw waveforms), and text (sequences of tokens) — does not have the neat, independently-meaningful-column structure that tabular data has and that tree-based models exploit so effectively. Historically, applying classical ML to these domains required a human to hand-engineer features first: edge and corner detectors for images, spectral features for audio, bag-of-words or n-gram counts for text, and only then would a classical model like an SVM or logistic regression be applied on top of those engineered features. Deep learning's central technical contribution here is representation learning: convolutional and transformer-based architectures learn the useful intermediate features directly from raw input and labels, often discovering better features than humans hand-engineered, and removing an entire, labor-intensive stage of the traditional pipeline.

The chart captures a widely observed, domain-dependent empirical pattern rather than a universal law: on small datasets, classical methods often reach good performance quickly because their lower capacity is well matched to limited data (same bias-variance logic as the previous slide, just favoring the other regime once data is abundant), while deep networks may underperform on small data because they are undertrained. But as dataset size grows into the medium and large regime, classical methods' performance tends to plateau — a random forest run on 100x more data usually doesn't improve nearly as much as a neural network does — while deep networks continue improving, a pattern sometimes called a "scaling law" for domains with abundant labeled data (large image and language corpora being the paradigm case). Emphasize the "domain-dependent" qualifier explicitly: this crossover is well documented for unstructured data with very large public or proprietary corpora, but it does not automatically apply to every tabular business problem, where curated data volume is often much more limited and tree ensembles frequently still win. Next, turn these two slides' worth of tradeoffs into a decision procedure.
-->

---
glowSeed: 1054
---

# A Practical Choice Map

<div class="grid grid-cols-2 gap-8 items-start">
<div>
<div class="space-y-3 mt-4">
<div v-click border="2 solid white/5" bg="white/5" rounded-lg px-4 py-3>
<span class="font-bold text-teal-300">1. Data structure</span>
<span class="text-sm opacity-85"> — Tabular (favor trees/ensembles) or unstructured — images, audio, text (favor deep learning)?</span>
</div>
<div v-click border="2 solid white/5" bg="white/5" rounded-lg px-4 py-3>
<span class="font-bold text-blue-300">2. Data volume</span>
<span class="text-sm opacity-85"> — Enough labeled examples to responsibly train a high-capacity model without overfitting?</span>
</div>
<div v-click border="2 solid white/5" bg="white/5" rounded-lg px-4 py-3>
<span class="font-bold text-amber-300">3. Constraints</span>
<span class="text-sm opacity-85"> — Interpretability requirements, latency budget, compute/serving cost, and who maintains this system after you leave the project?</span>
</div>
</div>
</div>
<div>
<div class="mt-5" role="img" aria-label="Decision flow: Problem, then Data plus scale, then Constraints, then Model family">
<div v-click class="flex items-center gap-3">
<div class="w-8 h-8 rounded-full bg-teal-500/20 border-2 border-teal-700 flex items-center justify-center text-sm font-bold">1</div>
<div class="flex-1 rounded-lg border-2 border-white/10 bg-white/5 px-3 py-2 text-sm font-bold">Problem</div>
</div>
<div class="ml-4 h-1 border-l-2 border-teal-400/50"></div>
<div v-click class="flex items-center gap-3">
<div class="w-8 h-8 rounded-full bg-blue-500/20 border-2 border-blue-700 flex items-center justify-center text-sm font-bold">2</div>
<div class="flex-1 rounded-lg border-2 border-white/10 bg-white/5 px-3 py-2 text-sm font-bold">Data + scale</div>
</div>
<div class="ml-4 h-1 border-l-2 border-teal-400/50"></div>
<div v-click class="flex items-center gap-3">
<div class="w-8 h-8 rounded-full bg-amber-500/20 border-2 border-amber-700 flex items-center justify-center text-sm font-bold">3</div>
<div class="flex-1 rounded-lg border-2 border-white/10 bg-white/5 px-3 py-2 text-sm font-bold">Constraints</div>
</div>
<div class="ml-4 h-1 border-l-2 border-teal-400/50"></div>
<div v-click class="flex items-center gap-3">
<div class="w-8 h-8 rounded-full bg-violet-500/20 border-2 border-violet-700 flex items-center justify-center text-sm font-bold">4</div>
<div class="flex-1 rounded-lg border-2 border-white/10 bg-white/5 px-3 py-2 text-sm font-bold">Model family</div>
</div>
</div>
<div v-click class="text-xs opacity-70 mt-2">Worked example: 5,000-row spreadsheet of loan applications, regulator requires an explanation for every denial → tabular + small + high interpretability need → gradient-boosted trees or logistic regression, not a neural network.</div>
</div>
</div>

<!--
This four-step map is meant to be walked through explicitly at the start of any new project, in this order, because later steps depend on the earlier answers. First, look at the raw data structure — is it naturally tabular (rows and columns with independently meaningful fields) or unstructured (pixels, waveforms, free text)? This alone rules out a large fraction of the space. Second, given the structure, look at data volume relative to problem complexity — recall the bias-variance framing: do you have enough labeled examples to responsibly fit a high-capacity model, or would a smaller model generalize better with what's actually available? Third, list the operating constraints that don't show up in an accuracy number at all: does a regulator or a business requirement demand that you can explain individual decisions (favoring classical models, per the previous deck's interpretability discussion); what is the acceptable inference latency and serving cost at the expected traffic volume; and who will maintain this system long after the original team has moved on, which often favors simpler, better-understood model families.

The worked example ties all three questions together on a realistic scenario: a 5,000-row loan-application dataset with a legal requirement to justify every denial is tabular (step 1 → favors trees/linear models), too small to safely support a large neural network without overfitting (step 2 → reinforces the same conclusion), and has a hard interpretability constraint (step 3 → rules out deep learning outright regardless of any accuracy gain it might offer). All three considerations point the same direction here, which is common — the "choice" is often not close once you actually walk through the framework, rather than defaulting to whichever method is currently most discussed. The final answer in step 4 — "model family" — is the output of this whole process, not an input chosen in advance by fashion or habit.
-->

---
glowSeed: 1055
---

# The Mathematical Foundations Do Not Change

<div class="grid grid-cols-2 gap-8 items-start">
<div>
<div class="space-y-2 mt-4 text-sm">
<div v-click border="2 solid white/5" bg="white/5" rounded-lg px-3 py-2>
<span class="font-bold text-teal-300">Linear algebra</span>
<span class="opacity-85"> — Data, weights, and layer computations are still vectors, matrices, and matrix multiplications.</span>
</div>
<div v-click border="2 solid white/5" bg="white/5" rounded-lg px-3 py-2>
<span class="font-bold text-blue-300">Probability and statistics</span>
<span class="opacity-85"> — Uncertainty, likelihood-based losses (e.g., cross-entropy), and evaluation metrics carry over unchanged.</span>
</div>
<div v-click border="2 solid white/5" bg="white/5" rounded-lg px-3 py-2>
<span class="font-bold text-amber-300">Calculus</span>
<span class="opacity-85"> — Backpropagation is literally the multivariate chain rule applied layer by layer.</span>
</div>
<div v-click border="2 solid white/5" bg="white/5" rounded-lg px-3 py-2>
<span class="font-bold text-violet-300">Methodology</span>
<span class="opacity-85"> — Generalization, validation discipline, and this module's fairness/failure-mode habits apply to any model family.</span>
</div>
</div>
</div>
<div>
<div class="mt-5" role="img" aria-label="Timeline: Foundations, then Classical ML, then Deep learning, then Future models, all resting on the same base">
<div v-click class="flex items-center gap-3">
<div class="w-8 h-8 rounded-full bg-teal-500/20 border-2 border-teal-700 flex items-center justify-center text-sm font-bold">1</div>
<div class="flex-1 rounded-lg border-2 border-white/10 bg-white/5 px-3 py-2 text-sm font-bold">Foundations</div>
</div>
<div class="ml-4 h-1 border-l-2 border-teal-400/50"></div>
<div v-click class="flex items-center gap-3">
<div class="w-8 h-8 rounded-full bg-blue-500/20 border-2 border-blue-700 flex items-center justify-center text-sm font-bold">2</div>
<div class="flex-1 rounded-lg border-2 border-white/10 bg-white/5 px-3 py-2 text-sm font-bold">Classical ML</div>
</div>
<div class="ml-4 h-1 border-l-2 border-teal-400/50"></div>
<div v-click class="flex items-center gap-3">
<div class="w-8 h-8 rounded-full bg-amber-500/20 border-2 border-amber-700 flex items-center justify-center text-sm font-bold">3</div>
<div class="flex-1 rounded-lg border-2 border-white/10 bg-white/5 px-3 py-2 text-sm font-bold">Deep learning</div>
</div>
<div class="ml-4 h-1 border-l-2 border-teal-400/50"></div>
<div v-click class="flex items-center gap-3">
<div class="w-8 h-8 rounded-full bg-violet-500/20 border-2 border-violet-700 flex items-center justify-center text-sm font-bold">4</div>
<div class="flex-1 rounded-lg border-2 border-white/10 bg-white/5 px-3 py-2 text-sm font-bold">Future models</div>
</div>
</div>

</div>
</div>

<!--
Every model family covered this semester — and every model family that will be invented after this course ends — is built on the same three mathematical pillars covered in Mathematical Foundations. A transformer's attention mechanism is still matrix multiplications and softmax normalization; a convolutional network's convolution is still a structured linear operation; training any of these networks by gradient descent still requires computing a gradient via calculus, and backpropagation specifically is nothing more than the multivariate chain rule applied systematically layer by layer, exactly the chain rule covered in Calculus for Optimization, just applied to a deeper composition of functions. None of this is a new branch of mathematics — it is the same linear algebra, calculus, and probability, composed into deeper, more expressive function classes.

Methodology transfers just as completely: the train/validation/test discipline, the bias-variance tradeoff, and the danger of data leakage from model evaluation apply identically whether you are cross-validating a ridge regression's regularization strength or tuning a neural network's learning rate — a neural network can overfit a small dataset exactly as a high-degree polynomial can, for exactly the same variance reasons. And the fairness, distribution-shift, feedback-loop, and interpretability material from this module's first two decks applies with equal force to a deep model deployed in production — a neural network can encode label bias or drift with the world exactly as a logistic regression can, and arguably needs more deliberate interpretability tooling (like the SHAP approach from the previous deck) precisely because it lacks a naturally readable structure. The message is not "deep learning is just classical ML in disguise" — architectures genuinely differ in capability — but that everything else you spent this semester learning to do carefully continues to matter, unchanged, no matter which model family you eventually choose.
-->

---
glowSeed: 1056
---

# One Field, Many Useful Tools

<div class="mt-4"><div class="grid grid-cols-3 gap-4 mt-6">
<div v-click border="2 solid teal-800" bg="teal-800/20" rounded-lg p-4>
<div class="font-bold text-teal-300 mb-2">Classical</div>
<div class="text-sm leading-relaxed opacity-90">Strong default for tabular data, small datasets, tight interpretability or compute constraints.</div>
</div>
<div v-click border="2 solid blue-800" bg="blue-800/20" rounded-lg p-4>
<div class="font-bold text-blue-300 mb-2">Deep</div>
<div class="text-sm leading-relaxed opacity-90">Strong on unstructured data (images, audio, text) at scale, where representation learning beats hand-engineered features.</div>
</div>
<div v-click border="2 solid amber-800" bg="amber-800/20" rounded-lg p-4>
<div class="font-bold text-amber-300 mb-2">Foundations</div>
<div class="text-sm leading-relaxed opacity-90">Linear algebra, probability, calculus, and validation methodology transfer to both, and to whatever comes next.</div>
</div>
</div></div>

<div v-click class="mt-10 text-center text-lg" border="2 solid white/10" bg="white/5" rounded-lg px-6 py-4>Next: the capstone applies the complete pipeline — modeling, evaluation, and ethical review — independently.</div>

<!--
This deck closes the technical curriculum with a deliberately practical, non-ideological takeaway: classical machine learning and deep learning are not rival philosophies where one is objectively superior, they are two regions of one continuous methodological space, each with clear conditions under which it is the stronger engineering choice — tabular data, limited examples, and strict interpretability or compute budgets favor the classical toolkit covered across most of this course; large volumes of unstructured data where representation learning has room to pay off favor deep architectures. The practical choice map from earlier in this deck is the reusable artifact: walk through data structure, data volume, and constraints, in that order, on every new project, rather than defaulting to whichever approach is currently most discussed.

What genuinely does not change, and what this entire course was actually building toward underneath the specific algorithms, is the mathematical and methodological foundation: the linear algebra, calculus, and probability from Mathematical Foundations; the bias-variance, cross-validation, and evaluation discipline from Core ML Concepts; and the fairness, failure-mode, and interpretability habits from this module's first two decks. Those transfer to any model you will ever be asked to build, evaluate, or audit, including architectures that do not exist yet. The capstone project that follows is the place to demonstrate all of it together on one real problem: choosing a model family deliberately, validating it honestly, and reviewing it — using this module's checklists — for how it could fail and whom it could affect, independently and without a course scaffold telling you which step comes next.
-->
