---
theme: default
highlighter: shiki
css: unocss
colorSchema: dark
title: 'What Is Learning?'
info: |
  ## What Is Learning?
  Supervised, unsupervised, and reinforcement learning.
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
glowSeed: 201
---

<div class="relative z-10">

# What Is Learning?

### Supervised · Unsupervised · Reinforcement

<div class="pt-6 opacity-80 text-lg">
Topic 1 of Core ML Concepts
</div>

<div class="grid grid-cols-3 gap-4 mt-18 text-sm">
<div border="2 solid teal-800" bg="teal-800/20" rounded-lg p-4>🏷️ <strong>Labeled examples</strong></div>
<div border="2 solid blue-800" bg="blue-800/20" rounded-lg p-4>🧭 <strong>Hidden structure</strong></div>
<div border="2 solid orange-800" bg="orange-800/20" rounded-lg p-4>🎮 <strong>Rewards over time</strong></div>
</div>

</div>

<!--
This deck opens the Core ML Concepts module and marks a shift from the mathematical tools built up in Mathematical Foundations (calculus, linear algebra, probability) to the taxonomy of problems those tools get applied to. The three-card row previews the organizing distinction the entire deck develops: what kind of experience does the learning algorithm receive? Supervised learning receives labeled examples — every input comes paired with a known correct answer. Unsupervised learning receives only inputs and must discover hidden structure without being told what "correct" looks like. Reinforcement learning receives neither: instead it interacts with an environment over time and receives rewards, which are evaluative feedback about how good an action turned out to be, not a labeled correct action to imitate.

Frame this as a map that essentially every algorithm covered for the rest of the course will fit onto — Decision Trees, Logistic Regression, SVMs, and Ensemble Methods are all supervised; k-Means, GMMs, and PCA are all unsupervised — and be upfront that the course spends most of its time on supervised learning specifically because it has the cleanest mathematical formulation (a single, unambiguous notion of "correct") and the broadest practical deployment. Reinforcement learning is included here for a complete taxonomy but will only be touched briefly, since a serious treatment (Markov decision processes, temporal-difference learning, policy gradients) is its own course.

Transition: before drawing the three-way distinction in detail, the next slide pins down a precise, general definition of what "learning" even means — one that applies uniformly across all three paradigms.
-->

---
glowSeed: 202
---

# A Working Definition of Learning

<div class="text-lg opacity-80 mt-2">
A program learns when experience improves its performance on a task.
</div>

<div class="grid grid-cols-3 gap-4 mt-7">
<div v-click border="2 solid teal-800" bg="teal-800/20" rounded-lg p-4>
<div class="text-3xl font-bold text-teal-300">E</div>
<div class="font-bold mt-1">Experience</div>
<div class="text-sm opacity-80 mt-2">Examples, interactions, or observations</div>
</div>
<div v-click border="2 solid blue-800" bg="blue-800/20" rounded-lg p-4>
<div class="text-3xl font-bold text-blue-300">T</div>
<div class="font-bold mt-1">Task</div>
<div class="text-sm opacity-80 mt-2">Predict, discover, or decide</div>
</div>
<div v-click border="2 solid orange-800" bg="orange-800/20" rounded-lg p-4>
<div class="text-3xl font-bold text-orange-300">P</div>
<div class="font-bold mt-1">Performance</div>
<div class="text-sm opacity-80 mt-2">A measurable objective or reward</div>
</div>
</div>

<div v-click class="mt-7" border="2 solid white/5" bg="white/5" backdrop-blur-sm rounded-lg px-6 py-4>

$$\theta^\star = \arg\min_\theta\; \mathbb{E}_{(x,y)\sim\mathcal D}\!\left[\ell(f_\theta(x),y)\right]$$

<div class="text-sm opacity-75">Data supplies experience · loss measures performance · optimization changes the model</div>
</div>

<!--
This is Tom Mitchell's classic formal definition of learning, worth stating precisely: "a computer program is said to learn from experience E with respect to some task T and performance measure P, if its performance on T, as measured by P, improves with experience E." The three cards break this into its components: Experience (E) is whatever the algorithm is exposed to — labeled examples for supervised learning, raw observations for unsupervised learning, or interactions with an environment for reinforcement learning; Task (T) is what the algorithm is trying to accomplish — predict a value, discover structure, or decide on an action; Performance (P) is the measurable quantity that tells us whether the algorithm is getting better — a loss function, a clustering-quality score, or accumulated reward.

Translate this abstract definition into the concrete machinery used throughout the rest of the course, shown in the boxed formula: data supplies the experience $\mathcal D$ (the pairs $(x,y)$ this deck will formalize for the supervised case), a parameterized model $f_\theta$ represents the hypothesis being learned, a loss function $\ell$ operationalizes the performance measure, and an optimization procedure (gradient descent or a closed-form solver) searches for the parameters $\theta^\star$ that minimize expected loss — this is exactly the empirical risk minimization framework from the Loss Functions deck, previewed here before it is built up in full.

The key point to land explicitly: the three paradigms introduced next are not three unrelated algorithm families, they are three different answers to "where does the performance signal (P) come from, and how is the experience (E) structured?" Supervised learning gets P directly, as a per-example labeled target. Unsupervised learning has no direct target at all — P must be defined implicitly, in terms of the discovered structure's usefulness. Reinforcement learning gets P as a delayed, cumulative reward rather than a per-decision label. Transition: start with supervised learning, since it is both the most common paradigm in practice and the clearest illustration of the E–T–P framework.
-->

---
glowSeed: 203
---

# Supervised Learning

<div class="grid grid-cols-2 gap-7 mt-4 items-center">

<div>
<div border="2 solid teal-800" bg="teal-800/20" rounded-lg p-4>

$$\mathcal D = \{(x_i,y_i)\}_{i=1}^{n}, \qquad f_\theta:\mathcal X\to\mathcal Y$$

</div>

<v-clicks>

- Every input arrives with a **known target**
- Learn a mapping that generalizes to unseen inputs
- **Regression:** continuous targets, such as price
- **Classification:** discrete targets, such as spam/not-spam

</v-clicks>
</div>

<div v-click>
<svg viewBox="0 0 420 300" class="w-full">
  <line x1="45" y1="255" x2="395" y2="255" stroke="#64748b" stroke-width="2" />
  <line x1="45" y1="255" x2="45" y2="25" stroke="#64748b" stroke-width="2" />
  <line x1="65" y1="230" x2="365" y2="55" stroke="#2dd4bf" stroke-width="4" />
  <g fill="#7dd3fc" stroke="#0c4a6e" stroke-width="2">
    <circle cx="80" cy="220" r="7"/><circle cx="125" cy="202" r="7"/><circle cx="175" cy="170" r="7"/>
    <circle cx="225" cy="145" r="7"/><circle cx="285" cy="115" r="7"/><circle cx="340" cy="72" r="7"/>
  </g>
  <line x1="260" y1="255" x2="260" y2="130" stroke="#f59e0b" stroke-width="2" stroke-dasharray="6 5" />
  <circle cx="260" cy="130" r="10" fill="#f59e0b" />
  <text x="275" y="145" fill="#fbbf24" style="font-size: 14px">prediction</text>
  <text x="170" y="292" fill="#94a3b8" style="font-size: 14px">house size</text>
  <text x="8" y="25" fill="#94a3b8" style="font-size: 14px">price</text>
</svg>
</div>

</div>

<!--
The formal setup, $\mathcal D=\{(x_i,y_i)\}_{i=1}^n$ with $f_\theta:\mathcal X\to\mathcal Y$, says precisely what "supervised" means: the training set is a collection of $n$ input-output pairs, and the goal is to learn a function mapping the input space $\mathcal X$ to the output space $\mathcal Y$. The defining feature, worth stating as plainly as possible, is that during training the correct answer $y_i$ is available for every $x_i$ — so the loss function can directly compare the model's prediction $f_\theta(x_i)$ against the known-correct $y_i$ and produce an unambiguous error signal. This is what makes supervised learning's objective so clean compared to the other two paradigms: there is never any doubt about what "correct" means for a training example.

The regression/classification split is about the type of $\mathcal Y$: regression targets are continuous (a price, a temperature, a measurement — any real number or vector of real numbers), while classification targets are discrete (spam/not-spam, one of several disease categories — a label drawn from a finite set). This distinction determines which loss functions and evaluation metrics apply later (squared error naturally fits continuous targets, cross-entropy/log-loss naturally fits discrete ones, both covered in the Loss Functions deck).

The scatter plot makes the regression case visual: house size (x-axis) versus price (y-axis), with the teal line representing the learned function $f_\theta$ and the orange dashed line showing how a new, unseen house size (which was never one of the labeled training points) gets mapped to a predicted price by reading off the fitted line. Emphasize the economic reality behind "label collection is often more expensive than model training": getting the labels $y_i$ — actual sale prices, confirmed diagnoses, human-annotated categories — frequently requires real-world measurement, expert judgment, or manual annotation, and can dominate a project's total cost even though fitting the model itself might take seconds. Transition: the next slide turns this formal setup into five lines of runnable code.
-->

---
glowSeed: 204
---

# Supervised Learning — A Tiny Regressor

```python {1|3-4|6|7|all}
from sklearn.linear_model import LinearRegression
import numpy as np

X = np.array([[1200], [1500], [1800], [2200]])  # square feet
y = np.array([300000, 340000, 400000, 480000]) # sale price

model = LinearRegression().fit(X, y)
print(model.predict([[2000]]))
```

<div v-click class="mt-7 grid grid-cols-3 gap-4 text-center">
<div border="2 solid teal-800" bg="teal-800/20" rounded-lg p-3><strong>Examples</strong><br><span class="text-sm opacity-75">labeled houses</span></div>
<div border="2 solid blue-800" bg="blue-800/20" rounded-lg p-3><strong>Fit</strong><br><span class="text-sm opacity-75">learn slope + intercept</span></div>
<div border="2 solid orange-800" bg="orange-800/20" rounded-lg p-3><strong>Generalize</strong><br><span class="text-sm opacity-75">price a new house</span></div>
</div>

<!--
Walk through this line by line — it is small enough to trace completely. `X` holds four labeled examples' inputs (square footage, as a column vector — scikit-learn expects 2D input even for a single feature, hence the nested brackets), and `y` holds the corresponding known sale prices. `LinearRegression().fit(X, y)` is where learning happens: the model searches for a slope and intercept that best fit these four (input, output) pairs, exactly the parameter-fitting step from the E-T-P framework. `model.predict([[2000]])` is the payoff — asking for a price prediction on 2000 square feet, an input that never appeared in the training data at all.

This tiny example contains the entire supervised workflow in five lines: labeled examples (E), a task of predicting price from size (T), and an implicit performance measure the `.fit()` call is optimizing (P, squared error by default for `LinearRegression`). The three cards below name each stage explicitly — Examples, Fit, Generalize — and "Generalize" is the one to dwell on, because it is the actual point of the whole exercise.

The central question this example is designed to provoke, and worth asking students directly: is the interesting thing here that the fitted line passes reasonably close to these four specific houses? No — with only four points, almost any reasonable line will look fine. The interesting question is whether the line's prediction for the *new* input (2000 sq ft, never seen during training) is trustworthy, and that question cannot be answered by looking at training performance alone — it requires the entire measurement discipline built up in the Train-Validation-Test Splits deck. Transition: having seen supervised learning's labeled-data structure, contrast it directly with unsupervised learning, where no such label exists at all.
-->

---
glowSeed: 205
---

# Unsupervised Learning

<div class="grid grid-cols-2 gap-7 mt-4 items-center">

<div>
<div border="2 solid blue-800" bg="blue-800/20" rounded-lg p-4>

$$\mathcal D = \{x_i\}_{i=1}^{n} \qquad \text{no labels}$$

</div>

<v-clicks>

- Discover structure rather than predict known targets
- **Clustering:** find groups
- **Dimensionality reduction:** compress while preserving structure
- **Density estimation:** model where data is likely to occur
- Evaluation is task-dependent because there may be no single “correct” answer

</v-clicks>
</div>

<div>
<svg viewBox="0 0 420 300" class="w-full">
  <rect x="12" y="18" width="190" height="250" rx="12" fill="#ffffff08" stroke="#ffffff20" />
  <rect x="218" y="18" width="190" height="250" rx="12" fill="#ffffff08" stroke="#ffffff20" />
  <text x="72" y="48" fill="#cbd5e1" style="font-size: 16px">before</text>
  <text x="285" y="48" fill="#cbd5e1" style="font-size: 16px">after</text>
  <g fill="#94a3b8">
    <circle cx="55" cy="95" r="7"/><circle cx="75" cy="120" r="7"/><circle cx="95" cy="85" r="7"/><circle cx="118" cy="115" r="7"/>
    <circle cx="145" cy="205" r="7"/><circle cx="165" cy="185" r="7"/><circle cx="130" cy="175" r="7"/><circle cx="175" cy="220" r="7"/>
  </g>
  <g fill="#2dd4bf"><circle cx="255" cy="95" r="7"/><circle cx="275" cy="120" r="7"/><circle cx="295" cy="85" r="7"/><circle cx="318" cy="115" r="7"/></g>
  <g fill="#60a5fa"><circle cx="345" cy="205" r="7"/><circle cx="365" cy="185" r="7"/><circle cx="330" cy="175" r="7"/><circle cx="375" cy="220" r="7"/></g>
</svg>
</div>

</div>

<!--
Contrast this directly and explicitly with the previous slide: the dataset is now just $\mathcal D=\{x_i\}_{i=1}^n$ — no labels, no $y_i$ at all. This single change has a large consequence: since there is no known-correct answer for any input, the algorithm cannot be told "you were off by this much" the way a supervised loss function can. Instead, the goal shifts from prediction to discovery — finding structure that was implicitly present in the data all along, without any external signal saying what that structure "should" look like.

The three bulleted subtypes correspond to three different notions of "structure." Clustering asks "which points naturally group together?" (illustrated by the before/after diagram: unlabeled gray points on the left resolve into two colored groups on the right after an algorithm identifies which points are close to each other). Dimensionality reduction asks "can this data be described with fewer numbers while preserving what matters?" (the subject of the PCA/t-SNE/UMAP deck later in the course). Density estimation asks "where in the input space is data likely to occur, and where is it rare?" — useful for anomaly detection, among other things.

The closing point is worth dwelling on since it is genuinely different from supervised learning's clean setup: evaluation is task-dependent because there may be no single "correct" clustering or "correct" compression — a clustering that groups customers by purchasing behavior might be excellent for a marketing use case and useless for a logistics use case, using the exact same data. This ambiguity is a real cost of giving up labels, not a minor technicality. Transition: the next slide makes clustering concrete with a runnable k-means example.
-->

---
glowSeed: 206
---

# Unsupervised Learning — Discovering Groups

```python {1-2|4|6|7-8|all}
from sklearn.cluster import KMeans
import numpy as np

X = np.array([[1, 2], [1.5, 1.8], [1, 0.6],
              [8, 8], [9, 11], [8.5, 10]])

model = KMeans(n_clusters=2, n_init='auto', random_state=0).fit(X)
print(model.labels_)           # assignments discovered from geometry
print(model.cluster_centers_)
```

<div v-click class="mt-7" border="2 solid amber-800" bg="amber-800/20" rounded-lg px-6 py-4 text-lg>
The algorithm invents cluster IDs; <strong>humans still decide whether the grouping is useful.</strong>
</div>

<!--
Trace the code: six 2D points are given with no labels attached, `KMeans(n_clusters=2, ...)` is told only how many groups to look for (2), and `.fit(X)` runs the clustering algorithm purely on the geometric positions of the points — three points near $(1,1)$-ish coordinates and three points near $(8,9)$-ish coordinates, visibly two separated blobs. `model.labels_` then reports which of the two discovered groups each point was assigned to, and `model.cluster_centers_` reports the centroid (mean position) of each discovered group — the algorithm essentially found "these three points are close together, and those three are close together, and far from the first three."

The critical point, and the amber callout states it directly: the algorithm invents cluster IDs (arbitrary integers like 0 and 1) purely from geometric proximity; humans still decide whether the grouping is useful and what it means. This is the practical version of the previous slide's "no single correct answer" point. Cluster label "0" and cluster label "1" carry no intrinsic meaning whatsoever — the algorithm has discovered a geometric partition of the data, nothing more. It is a human who might later look at cluster 0's typical purchasing pattern and decide to call it "budget shoppers," or look at cluster 1 and call it "premium customers" — that naming and interpretation step is entirely outside what k-means computed, and re-running k-means with a different random seed could easily produce label 0 and label 1 swapped, or even a different partition altogether if the true cluster structure is ambiguous.

Transition: unsupervised learning discovers structure without any external feedback signal at all; reinforcement learning, covered next, sits at the opposite extreme — it does get feedback, but that feedback is a delayed, evaluative reward rather than a per-example label.
-->

---
glowSeed: 207
---

# Reinforcement Learning

<div class="grid grid-cols-2 gap-8 mt-3 items-center">

<div>
<v-clicks>

- An **agent** chooses actions inside an **environment**
- The environment returns a new state and a reward
- Learn a **policy** that maximizes cumulative reward
- Feedback is evaluative, often delayed—not a labeled correct action

</v-clicks>

<div v-click class="mt-5" border="2 solid orange-800" bg="orange-800/20" rounded-lg p-4>

$$\pi^\star=\arg\max_\pi\;\mathbb E\!\left[\sum_{t=0}^{T}\gamma^t r_t\mid\pi\right]$$

</div>
</div>

<div v-click>
<svg viewBox="0 0 430 300" class="w-full">
  <defs><marker id="rlArrow" markerWidth="8" markerHeight="8" refX="7" refY="4" orient="auto"><path d="M0,0 L8,4 L0,8 Z" fill="#cbd5e1"/></marker></defs>
  <rect x="25" y="95" width="135" height="95" rx="14" fill="#0f766e55" stroke="#2dd4bf" stroke-width="3"/>
  <text x="65" y="150" fill="#f8fafc" style="font-size: 20px" font-weight="bold">Agent</text>
  <rect x="270" y="95" width="135" height="95" rx="14" fill="#9a341255" stroke="#fb923c" stroke-width="3"/>
  <text x="287" y="150" fill="#f8fafc" style="font-size: 20px" font-weight="bold">Environment</text>
  <path d="M160 115 C205 65, 235 65, 270 115" fill="none" stroke="#cbd5e1" stroke-width="3" marker-end="url(#rlArrow)"/>
  <text x="185" y="65" fill="#cbd5e1" style="font-size: 14px">action aₜ</text>
  <path d="M270 175 C235 230, 200 230, 160 175" fill="none" stroke="#cbd5e1" stroke-width="3" marker-end="url(#rlArrow)"/>
  <text x="155" y="255" fill="#cbd5e1" style="font-size: 14px">state sₜ₊₁, reward rₜ</text>
</svg>
</div>

</div>

<!--
Reinforcement learning's setup is fundamentally different from both previous paradigms, and the diagram's agent-environment loop makes the difference concrete: an agent chooses an action $a_t$ at each time step; the environment responds with a new state $s_{t+1}$ and a scalar reward $r_t$; the agent's goal is to learn a policy $\pi$ — a rule for choosing actions given states — that maximizes cumulative reward over time, not just the immediate next reward. The boxed formula $\pi^\star=\arg\max_\pi\mathbb E[\sum_{t=0}^T \gamma^t r_t \mid \pi]$ states this precisely: sum up rewards over the whole trajectory (time steps $0$ through $T$), discount future rewards by $\gamma^t$ (a discount factor between 0 and 1, so rewards further in the future count less than immediate ones — reflecting both uncertainty about the future and, in many settings, a genuine preference for sooner reward), and find the policy that maximizes the expected value of that discounted sum.

The chess example makes the "feedback is evaluative, often delayed" bullet concrete: a chess-playing agent is never told "move 14 was the correct move" the way a supervised classifier is told "this email is spam" — it may only receive a single win/loss signal at the very end of a 40-move game. This creates the credit-assignment problem, worth naming explicitly: given only a final win or loss, which of the 40 individual moves actually deserved credit or blame for that outcome? A move made early in the game might have set up a decisive advantage 20 moves later, and the algorithm has to somehow work backward from the delayed outcome to individual decisions — a fundamentally harder inference problem than supervised learning's direct per-example feedback.

Be explicit that this course recognizes reinforcement learning as the third major paradigm and shows its defining structure here, but does not cover its algorithms (Q-learning, policy gradients, actor-critic methods) in depth — that material belongs in a dedicated reinforcement-learning course. Transition: having covered all three primary paradigms in isolation, the next slide covers hybrid approaches that blend them.
-->

---
glowSeed: 208
---

# Between the Big Three

<div class="grid grid-cols-2 gap-7 mt-6">

<div v-click border="2 solid violet-800" bg="violet-800/20" rounded-lg overflow-hidden>
<div bg="violet-800/40" px-5 py-3 font-bold>🧪 Semi-supervised</div>
<div px-5 py-5>
Combine a <strong>small labeled set</strong> with a much larger pool of unlabeled data.
<div class="mt-4 flex gap-2 justify-center">
<span v-for="n in 3" :key="`l${n}`" class="h-8 w-8 rounded-full bg-violet-400" />
<span v-for="n in 9" :key="`u${n}`" class="h-8 w-8 rounded-full bg-slate-600" />
</div>
</div>
</div>

<div v-click border="2 solid teal-800" bg="teal-800/20" rounded-lg overflow-hidden>
<div bg="teal-800/40" px-5 py-3 font-bold>🧩 Self-supervised</div>
<div px-5 py-5>
Create targets from the data itself—such as predicting a <strong>masked word</strong> from context.
<div class="mt-5 text-lg">The model reads the <span class="px-3 py-1 rounded bg-teal-500/30 text-teal-200">[MASK]</span>.</div>
</div>
</div>

</div>

<div v-click class="mt-8 text-center text-lg opacity-85">
Modern systems often combine paradigms: <strong>self-supervised pretraining → supervised fine-tuning</strong>
</div>

<!--
These two hybrid terms appear constantly in modern ML discussion and are worth defining precisely, since they are often conflated with each other and with the three primary paradigms. Semi-supervised learning is a direct hybrid: it combines a small labeled set (the violet dots) with a much larger pool of unlabeled data (the gray dots) — exploiting the fact that labels are expensive to collect (as flagged on the Supervised Learning slide) but unlabeled data is often cheap and abundant. The intuition is that the unlabeled data's overall structure (which points cluster near which) can help the algorithm generalize better from the few labels it does have, essentially borrowing unsupervised learning's structure-discovery to boost supervised learning's label-efficiency.

Self-supervised learning is a different idea, despite the similar name: it creates its own labels directly from the unlabeled data's structure, requiring no human annotation at all. The masked-word example is the canonical case: take an ordinary sentence, hide one word, and train a model to predict the hidden word from its surrounding context — the "label" (the hidden word) was never manually annotated by a human, it was mechanically carved out of naturally occurring text. This is precisely why self-supervision powers much of large language model pretraining: given a large enough corpus of text, this masked/next-word-prediction task generates effectively unlimited free training examples.

The closing line names the pattern that has become dominant in modern deep learning: self-supervised pretraining (learn general-purpose representations from a huge unlabeled corpus using a self-generated task like masked-word prediction) followed by supervised fine-tuning (adapt that pretrained model to a specific labeled task with comparatively few labeled examples). This is worth flagging as a preview of ideas the Neural Networks and Deep Learning Basics module will return to. Transition: with all five categories (three primary, two hybrid) now on the table, the next slide compares the three primary paradigms side by side in a single table.
-->

---
glowSeed: 209
---

# Comparing the Paradigms

<div class="grid grid-cols-[8rem_1fr_1fr_1fr] gap-2 mt-5 text-sm">
<div></div>
<div class="p-3 font-bold text-teal-300" border="2 solid teal-800" bg="teal-800/20" rounded-lg>Supervised</div>
<div class="p-3 font-bold text-blue-300" border="2 solid blue-800" bg="blue-800/20" rounded-lg>Unsupervised</div>
<div class="p-3 font-bold text-orange-300" border="2 solid orange-800" bg="orange-800/20" rounded-lg>Reinforcement</div>

<div class="p-3 font-bold opacity-70">Data</div><div class="p-3" bg="white/5" rounded>(x, y) pairs</div><div class="p-3" bg="white/5" rounded>x only</div><div class="p-3" bg="white/5" rounded>interaction stream</div>
<div class="p-3 font-bold opacity-70">Feedback</div><div class="p-3" bg="white/5" rounded>direct labels</div><div class="p-3" bg="white/5" rounded>none inherent</div><div class="p-3" bg="white/5" rounded>rewards</div>
<div class="p-3 font-bold opacity-70">Goal</div><div class="p-3" bg="white/5" rounded>predict</div><div class="p-3" bg="white/5" rounded>discover structure</div><div class="p-3" bg="white/5" rounded>choose actions</div>
<div class="p-3 font-bold opacity-70">Example</div><div class="p-3" bg="white/5" rounded>linear regression</div><div class="p-3" bg="white/5" rounded>k-means</div><div class="p-3" bg="white/5" rounded>Q-learning</div>
<div class="p-3 font-bold opacity-70">Use case</div><div class="p-3" bg="white/5" rounded>price prediction</div><div class="p-3" bg="white/5" rounded>customer segments</div><div class="p-3" bg="white/5" rounded>robot control</div>
</div>

<!--
Use this table as an active-recall exercise rather than just reading it aloud: cover the cells and ask students to fill in each row from memory before revealing it, since reconstructing the distinctions is a much stronger test of understanding than recognizing them. Each row corresponds to one piece of the E-T-P framework from earlier in the deck. "Data" is the form of experience E: labeled pairs versus unlabeled inputs versus an interaction stream. "Feedback" is where the performance signal P comes from: direct per-example labels versus no inherent signal versus delayed rewards. "Goal" is the task T: predict a value, discover latent structure, or choose a sequence of actions.

The "Example" and "Use case" rows ground the abstract framework in concrete algorithms and applications that recur throughout the rest of the course: linear regression (supervised, predicting a continuous price) will be covered in depth in Supervised Learning - Regression; k-means (unsupervised, discovering customer segments) is covered in Unsupervised Learning; Q-learning (reinforcement, robot control) is named for completeness but, as established on the reinforcement learning slide, not covered in depth in this course.

The deepest point to land here: the three paradigms are defined less by which specific algorithm is used and more by the structure of the experience and feedback available — the same underlying mathematical machinery (a parameterized model, an objective function, an optimizer) gets reused across all three, but what changes is what data looks like and where the "how good was that?" signal comes from. Transition: with the taxonomy fully mapped, the final slide previews exactly how much of the remaining course time each paradigm will get.
-->

---
glowSeed: 210
---

# Where This Course Focuses

<div class="grid grid-cols-3 gap-4 mt-7">
<div v-click class="col-span-2" border="2 solid teal-800" bg="teal-800/20" rounded-lg p-6>
<div class="text-5xl font-bold text-teal-300">Most</div>
<div class="text-xl font-bold mt-2">Supervised learning</div>
<div class="text-sm opacity-80 mt-2">Regression, classification, trees, SVMs, and neural networks</div>
</div>
<div v-click border="2 solid blue-800" bg="blue-800/20" rounded-lg p-6>
<div class="text-3xl font-bold text-blue-300">A unit</div>
<div class="text-lg font-bold mt-2">Unsupervised</div>
<div class="text-sm opacity-80 mt-2">Clustering, PCA, and mixture models</div>
</div>
<div v-click class="col-span-3" border="2 solid orange-800" bg="orange-800/20" rounded-lg px-6 py-4 flex items-center gap-5>
<div class="text-3xl">👀</div><div><strong>Reinforcement learning:</strong> recognize the structure; a deep treatment belongs in its own course.</div>
</div>
</div>

<div v-click class="mt-8 text-xl">
Next: <strong>Bias–Variance Tradeoff</strong> — why fitting the data is not the same as learning the pattern.
</div>

<!--
Be transparent with students about the semester's actual shape, since it helps set expectations for what's coming. Supervised learning gets the large majority of course time ("Most") because, as established across this deck, it has the clearest mathematical story (an unambiguous per-example loss) and the broadest practical deployment (regression, classification, trees, SVMs, ensembles, and neural networks are all supervised methods, spanning several later modules). Unsupervised learning gets one dedicated unit — enough to cover clustering, PCA, and mixture models properly, but not the sprawling depth given to supervised methods. Reinforcement learning gets acknowledgment of its structure (the agent-environment loop, policy, reward) but no dedicated algorithmic treatment, consistent with what the reinforcement learning slide already said.

The immediate next four lectures — Bias-Variance Tradeoff, Loss Functions and Empirical Risk Minimization, Overfitting and Regularization, and Train-Validation-Test Splits and Cross-Validation — all develop concepts that apply to *every* supervised method covered later, regardless of which specific algorithm: they are about how to measure whether a model has actually learned versus merely memorized, not about any one algorithm's mechanics. This is worth stating explicitly so students understand why the course pauses on foundational concepts before reaching named algorithms.

Transition: the very next deck, Bias-Variance Tradeoff, opens by asking a question this deck has only gestured at — what does it actually mean for a model to have "learned the pattern" rather than just fit the specific training data closely? That question turns out to have a precise mathematical decomposition, which is exactly where the next lecture begins.
-->
