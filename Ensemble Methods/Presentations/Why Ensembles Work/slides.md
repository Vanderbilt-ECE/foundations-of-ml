---
theme: default
highlighter: shiki
css: unocss
colorSchema: dark
title: 'Why Ensembles Work'
info: |
  ## Why Ensembles Work
  Diversity turns many imperfect models into one stronger model
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
glowSeed: 670
---

# Why Ensembles Work

### Diversity turns many imperfect models into one stronger model

<div class="pt-8 opacity-80 text-lg">Ensemble Methods · Foundations of Machine Learning</div>

<div class="mt-14 flex justify-center gap-4" aria-hidden="true">
<div class="w-28 h-3 rounded-full bg-teal-400/70"></div>
<div class="w-20 h-3 rounded-full bg-blue-400/60"></div>
<div class="w-14 h-3 rounded-full bg-violet-400/50"></div>
</div>

<!--
This deck opens the ensemble unit. Before we meet any specific algorithm, we answer one question from first principles: why should combining several imperfect models ever beat the best of them?

Roadmap: a toy example where a crowd beats every individual → what an ensemble is, precisely → a short probability refresher (variance of a sum, covariance, correlation) → the variance of an average, first for two models, then for B models → the same story for classifiers, using majority voting → where this sits in the bias–variance picture, and what ensembling cannot fix. The next two decks, bagging and boosting, are concrete recipes built on the ideas here.
-->

---
glowSeed: 6701
---

# Five Guesses Beat the Best Guesser

<div class="grid grid-cols-2 gap-8 items-start">
<div>
<div class="space-y-3 mt-4">
<div v-click border="2 solid white/5" bg="white/5" rounded-lg px-4 py-3>
<span class="font-bold text-teal-300">The task</span>
<span class="text-sm opacity-85"> — Five people guess how many marbles are in a jar. The truth is 100.</span>
</div>
<div v-click border="2 solid white/5" bg="white/5" rounded-lg px-4 py-3>
<span class="font-bold text-blue-300">Individuals</span>
<span class="text-sm opacity-85"> — Errors of 18, 15, 6, 8, and 3. The best guesser is off by 3.</span>
</div>
<div v-click border="2 solid white/5" bg="white/5" rounded-lg px-4 py-3>
<span class="font-bold text-amber-300">The average</span>
<span class="text-sm opacity-85"> — (82 + 115 + 94 + 108 + 97) / 5 = 99.2, off by only 0.8.</span>
</div>
<div v-click border="2 solid teal-800" bg="teal-800/20" rounded-lg px-4 py-3>
<span class="font-bold text-teal-200">Why?</span>
<span class="text-sm opacity-85"> — Some guessed high, some low. The errors had different signs and cancelled.</span>
</div>
</div>
</div>
<svg role="img" aria-label="Number line from 75 to 125. Five guesses at 82, 94, 97, 108 and 115 scatter around the true value 100. Their average, 99.2, lands almost on the truth." viewBox="0 0 520 260" class="w-full mt-6">
  <line x1="60" y1="170" x2="470" y2="170" stroke="#64748b" stroke-width="2"/>
  <g fill="#cbd5e1" style="font-size:13px" text-anchor="middle"><text x="60" y="192">75</text><text x="162.5" y="192">87.5</text><text x="265" y="192">100</text><text x="367.5" y="192">112.5</text><text x="470" y="192">125</text></g>
  <line x1="265" y1="40" x2="265" y2="176" stroke="#2dd4bf" stroke-width="3" stroke-dasharray="7 5"/>
  <text x="265" y="30" fill="#5eead4" text-anchor="middle" style="font-size:15px">truth = 100</text>
  <g v-click>
    <g fill="#60a5fa"><circle cx="117.4" cy="150" r="8"/><circle cx="388" cy="150" r="8"/><circle cx="215.8" cy="150" r="8"/><circle cx="330.6" cy="150" r="8"/><circle cx="240.4" cy="150" r="8"/></g>
    <g fill="#93c5fd" style="font-size:13px" text-anchor="middle"><text x="117.4" y="132">82</text><text x="388" y="132">115</text><text x="215.8" y="132">94</text><text x="330.6" y="132">108</text><text x="240.4" y="132">97</text></g>
  </g>
  <g v-click>
    <polygon points="258.4,100 249.4,84 267.4,84" fill="#fbbf24"/>
    <text x="250" y="72" fill="#fbbf24" text-anchor="end" style="font-size:15px">average 99.2</text>
    <text x="265" y="235" fill="#e2e8f0" text-anchor="middle" style="font-size:15px">the average beats every individual guess</text>
  </g>
</svg>
</div>

<!--
Start with something everyone can check by hand. Five people guess the number of marbles in a jar holding 100. Their guesses are 82, 115, 94, 108 and 97, so their errors are 18, 15, 6, 8 and 3. Now average the guesses: 99.2. The crowd is off by 0.8, which beats even the best individual.

Ask the class why. Nobody in the crowd is especially good; what matters is that their mistakes point in different directions. Two guessed high and three guessed low, and the highs and lows cancelled. Keep this picture in mind: the whole deck is about when that cancellation happens and how much it can buy.

Contrast case to pose: if all five people had looked at the jar from the same bad angle and guessed 112, 114, 115, 113, 116, the average would be 114 — no better than a typical guess. Same number of people, no cancellation.
-->

---
glowSeed: 6702
---

# What Is an Ensemble?

<div class="grid grid-cols-2 gap-8 items-start">
<div>
<div class="space-y-3 mt-4">
<div v-click border="2 solid white/5" bg="white/5" rounded-lg px-4 py-3>
<span class="font-bold text-teal-300">Members</span>
<span class="text-sm opacity-85"> — B trained models f̂₁, …, f̂<sub>B</sub>, called base learners.</span>
</div>
<div v-click border="2 solid white/5" bg="white/5" rounded-lg px-4 py-3>
<span class="font-bold text-blue-300">A combination rule</span>
<span class="text-sm opacity-85"> — One fixed recipe that turns B predictions into one.</span>
</div>
<div v-click border="2 solid white/5" bg="white/5" rounded-lg px-4 py-3>
<span class="font-bold text-amber-300">The ensemble</span>
<span class="text-sm opacity-85"> — Is itself just a model: input x, output a prediction.</span>
</div>
</div>
</div>
<div class="space-y-3 mt-4" style="font-size: .85em">
<div v-click border="2 solid teal-800" bg="teal-800/20" rounded-lg px-4 py-1>
<span class="font-bold text-teal-200">Regression: average</span>

$$
\bar f(x)=\frac1B\sum_{b=1}^{B}\hat f_b(x)
$$

</div>
<div v-click border="2 solid blue-800" bg="blue-800/20" rounded-lg px-4 py-1>
<span class="font-bold text-blue-200">Classification: hard vote</span>

$$
\hat y(x)=\operatorname*{arg\,max}_{c}\ \#\{b:\hat f_b(x)=c\}
$$

</div>
<div v-click border="2 solid violet-800" bg="violet-800/20" rounded-lg px-4 py-1>
<span class="font-bold text-violet-200">Classification: soft vote</span>

$$
\hat y(x)=\operatorname*{arg\,max}_{c}\ \frac1B\sum_b \hat p_b(c\mid x)
$$

</div>
</div>
</div>

<!--
Fix the vocabulary before any math. An ensemble has two parts: a set of B trained models, which we call base learners or members, and a combination rule. The rule is fixed in advance; it is not learned per example.

For regression the rule is almost always an average, f-bar. For classification there are two common rules. A hard vote counts how many members predict each class and picks the most popular one. A soft vote averages the predicted class probabilities and picks the class with the highest average; it uses more information, because a member that is 51% sure counts for less than one that is 99% sure.

The marble example was a regression ensemble with B = 5 and the averaging rule. Point out that the ensemble is itself just another model — it takes x and returns a prediction — so everything we know about evaluating models applies to it unchanged.
-->

---
glowSeed: 6713
---

# Deriving the Ensemble Error

<div class="space-y-3 mt-4">
<div v-click class="grid grid-cols-[1fr_17rem] gap-6 items-center">
<div style="font-size: .8em" border="2 solid white/5" bg="white/5" rounded-lg px-4 py-1>

$$
\hat f_b-y=(\hat f_b-\bar f)+(\bar f-y)
$$

</div>
<div class="text-sm opacity-90"><span class="font-bold text-teal-300">1 · Add zero.</span> Split each member's error at the ensemble's prediction.</div>
</div>
<div v-click class="grid grid-cols-[1fr_17rem] gap-6 items-center">
<div style="font-size: .8em" border="2 solid white/5" bg="white/5" rounded-lg px-4 py-1>

$$
\frac1B\sum_b(\hat f_b-y)^2=\frac1B\sum_b(\hat f_b-\bar f)^2+2(\bar f-y)\underbrace{\frac1B\sum_b(\hat f_b-\bar f)}_{=\,\bar f-\bar f\,=\,0}+(\bar f-y)^2
$$

</div>
<div class="text-sm opacity-90"><span class="font-bold text-blue-300">2 · Square and average over b.</span> The cross term vanishes: deviations from an average sum to zero.</div>
</div>
<div v-click class="grid grid-cols-[1fr_17rem] gap-6 items-center">
<div style="font-size: .8em" border="2 solid teal-800" bg="teal-800/20" rounded-lg px-4 py-1>

$$
\underbrace{(\bar f-y)^2}_{\text{ensemble error}}=\underbrace{\frac1B\sum_b(\hat f_b-y)^2}_{\text{average member error}}-\underbrace{\frac1B\sum_b(\hat f_b-\bar f)^2}_{\text{disagreement}}
$$

</div>
<div class="text-sm opacity-90"><span class="font-bold text-amber-300">3 · Rearrange.</span> Move the disagreement term to the other side.</div>
</div>
</div>

<!--
Derive the identity before using it; it takes three lines and uses the same trick as the bias–variance decomposition. Fix one input x with true target y, and B member predictions f-hat-b whose average is f-bar.

Step 1: add and subtract f-bar inside each member's error. A member's error splits into how far it sits from the ensemble's prediction, plus how far the ensemble's prediction sits from the truth.

Step 2: square both sides and average over the B members. Squaring a sum gives the two squares plus twice the cross term. The second piece, f-bar minus y, is the same for every member, so it comes outside the average. What is left inside is the average of f-hat-b minus f-bar, which is f-bar minus f-bar, zero. This is the step to slow down on: the deviations of any set of numbers from their own mean always sum to zero.

Step 3: move the disagreement term across. The ensemble's squared error equals the members' average squared error minus their average squared distance from the ensemble. This is often called the ambiguity decomposition. Point out what was not used: no expectations, no independence, no distribution. It is algebra about B numbers and a target, so it holds at every input for any set of members.
-->

---
glowSeed: 6703
---

# What the Ensemble Error Identity Tells Us

<div class="grid grid-cols-2 gap-8 items-start">
<div>
<div class="mt-4 text-center" style="font-size: .95em" border="2 solid teal-800" bg="teal-800/20" rounded-lg px-4 py-3>
ensemble error = average member error − <span class="text-teal-300 font-bold">disagreement</span>
</div>
<div class="space-y-3 mt-4">
<div v-click border="2 solid white/5" bg="white/5" rounded-lg px-4 py-3>
<span class="font-bold text-blue-300">Always true</span>
<span class="text-sm opacity-85"> — Exact algebra, for every input, with no assumptions.</span>
</div>
<div v-click border="2 solid white/5" bg="white/5" rounded-lg px-4 py-3>
<span class="font-bold text-amber-300">Never worse than average</span>
<span class="text-sm opacity-85"> — Disagreement is ≥ 0, so the ensemble matches or beats the members' average error.</span>
</div>
</div>
</div>
<div>
<div v-click class="mt-4 text-sm" border="2 solid violet-800" bg="violet-800/20" rounded-lg px-4 py-3>
The gain from ensembling <em>is</em> the disagreement. Members that agree perfectly give zero gain.
</div>
<div v-click class="mt-4" border="2 solid white/5" bg="white/5" rounded-lg px-4 py-3>
<span class="font-bold text-red-300">Not a promise to beat the best</span>
<span class="text-sm opacity-85"> — That depends on how the errors cancel, which the rest of the deck quantifies.</span>
</div>
</div>
</div>

<!--
Now read the identity. It says the squared error of the averaged prediction equals the members' average squared error, minus how much the members disagree with one another.

Three consequences. First, it is always true, because the derivation used no assumptions. Second, disagreement can never be negative, so the ensemble is never worse than the members' average error. Third, and most important, the improvement is exactly the disagreement: copies of one model never disagree, so they gain nothing.

Be clear about what the identity does not promise. It does not say the ensemble beats the best member. Whether that happens in general depends on how the members' errors are correlated, which is what the rest of the deck quantifies.
-->

---
glowSeed: 6716
---

# Regression: How Much Does Averaging Help?

<div class="text-sm opacity-80 -mt-2">Numeric predictions, combined by averaging</div>

<div class="grid grid-cols-2 gap-8 items-start">
<div class="space-y-3 mt-4">
<div v-click border="2 solid white/5" bg="white/5" rounded-lg px-4 py-3>
<span class="font-bold text-teal-300">What we know</span>
<span class="text-sm opacity-85"> — The gain from averaging is exactly the members' disagreement.</span>
</div>
<div v-click border="2 solid white/5" bg="white/5" rounded-lg px-4 py-3>
<span class="font-bold text-red-300">What we don't</span>
<span class="text-sm opacity-85"> — The identity is bookkeeping: it measures the gain once the models exist. It can't predict how big the gain will be, how it grows with B, or what limits it.</span>
</div>
<div v-click class="text-sm [&_p]:my-0" border="2 solid amber-800" bg="amber-800/20" rounded-lg px-4 py-3>

<span class="font-bold text-amber-300">The setup:</span> fix one input x₀. Train B models, each on a random draw of the training data, and average their predictions: $\bar f(x_0)=\frac1B\sum_b \hat f_b(x_0)$.

</div>
</div>
<div class="space-y-3 mt-4">
<div v-click class="font-bold text-blue-300">Three questions to answer</div>
<div v-click border="2 solid white/5" bg="white/5" rounded-lg px-4 py-3>
<span class="font-bold text-teal-300">1.</span>
<span class="text-sm opacity-85"> What does averaging do to <b>bias</b>?</span>
</div>
<div v-click border="2 solid white/5" bg="white/5" rounded-lg px-4 py-3>
<span class="font-bold text-blue-300">2.</span>
<span class="text-sm opacity-85"> How much does it cut <b>variance</b>, and how does that depend on B?</span>
</div>
<div v-click border="2 solid white/5" bg="white/5" rounded-lg px-4 py-3>
<span class="font-bold text-violet-300">3.</span>
<span class="text-sm opacity-85"> What stops the error from shrinking all the way to zero?</span>
</div>
</div>
</div>

<!--
Pause here and set up the next stretch of the lecture. We are working with regression: each model outputs a number, and the ensemble averages those numbers.

The ensemble error identity told us that the gain from averaging is exactly the disagreement among members. That is a true statement, but it is bookkeeping: you can only compute it once the models are trained and you can compare their predictions to the truth. It does not predict how big the gain will be, how it grows with the number of models, or what limits it. An analogy: profit = revenue − cost is always true, but it won't tell you next quarter's revenue.

To answer that, we need a model of where the members' predictions come from. Fix one input x0. Each member is trained on a random draw of the training data, so its prediction at x0 is random: retrain on a different draw and you get a different number. The ensemble prediction is the average of B of these random numbers.

Write the three questions on the board and come back to them. Question 1 is answered by the bias slide: averaging leaves bias unchanged. Question 2 is answered by the variance formula: rho sigma squared plus (1 − rho) sigma squared over B. Question 3 is the floor: correlation between members, rho sigma squared, which no number of models removes. First we need two pieces of probability: what bias and variance mean for a prediction, and the rule for the variance of a sum.
-->

---
glowSeed: 6704
---

# A Prediction Is a Random Variable

<div class="grid grid-cols-2 gap-8 items-start">
<div>
<div class="space-y-3 mt-4">
<div v-click border="2 solid white/5" bg="white/5" rounded-lg px-4 py-3>
<span class="font-bold text-teal-300">The training set is random</span>
<span class="text-sm opacity-85"> — A different sample of data gives a different fitted model.</span>
</div>
<div v-click border="2 solid white/5" bg="white/5" rounded-lg px-4 py-3>
<span class="font-bold text-blue-300">So is the prediction</span>
<span class="text-sm opacity-85"> — At a fixed input x₀, the predicted value changes from one fit to the next.</span>
</div>
<div v-click border="2 solid white/5" bg="white/5" rounded-lg px-4 py-3>
<span class="font-bold text-amber-300">Two summaries</span>
<span class="text-sm opacity-85"> — Where it centers (bias) and how much it wobbles (variance).</span>
</div>
</div>
</div>
<div>
<div v-click class="mt-4" style="font-size: .85em" border="2 solid teal-800" bg="teal-800/20" rounded-lg px-4 py-2>

$$
\begin{aligned}
\text{Bias}&=\mathbb E[\hat f(x_0)]-f(x_0)\\
\sigma^2&=\operatorname{Var}\big(\hat f(x_0)\big)
\end{aligned}
$$

</div>
<div v-click class="mt-4 text-sm" border="2 solid amber-800" bg="amber-800/20" rounded-lg px-4 py-3>
<span class="font-bold text-amber-300">Notation:</span> in this unit σ² is one model's <em>prediction</em> variance. Label noise, Var(ε), is written σ²<sub>ε</sub>.
</div>
</div>
</div>

<!--
Now move from the marble jar to machine learning. Recall from the bias–variance deck that a fitted model depends on its training set, and the training set is a random sample. Fit the same algorithm to a different sample and you get a different model, so at any fixed input x-naught the prediction f-hat of x-naught is a random variable.

We summarize it with two numbers. Bias is how far its average lands from the true function value. Variance is how much it wobbles around that average from fit to fit. A deep decision tree is the standard example of low bias and high variance: on average it is close to right, but any one tree can be far off.

Flag the notation clash now so it does not cause confusion later. In the bias–variance deck, sigma squared was the noise variance. In this unit, following the bagging deck, sigma squared means the variance of one model's prediction. When we need the noise, we will write sigma-epsilon squared.
-->

---
glowSeed: 6705
---

# Toolkit: Variance of a Sum

<div class="grid grid-cols-2 gap-8 items-start">
<div class="space-y-2 mt-2" style="font-size: .85em">
<div v-click border="2 solid white/5" bg="white/5" rounded-lg px-4 py-1>
<span class="font-bold text-teal-300">Expectation is linear</span>

$$
\mathbb E[aX+bY]=a\,\mathbb E[X]+b\,\mathbb E[Y]
$$

</div>
<div v-click border="2 solid white/5" bg="white/5" rounded-lg px-4 py-1>
<span class="font-bold text-blue-300">Scaling squares the factor</span>

$$
\operatorname{Var}(aX)=a^2\operatorname{Var}(X)
$$

</div>
<div v-click border="2 solid white/5" bg="white/5" rounded-lg px-4 py-1>
<span class="font-bold text-amber-300">Variances add, plus a cross term</span>

$$
\operatorname{Var}(X+Y)=\operatorname{Var}X+\operatorname{Var}Y+2\operatorname{Cov}(X,Y)
$$

</div>
</div>
<div class="space-y-2 mt-2" style="font-size: .85em">
<div v-click border="2 solid white/5" bg="white/5" rounded-lg px-4 py-1>
<span class="font-bold text-violet-300">Covariance: do they move together?</span>

$$
\operatorname{Cov}(X,Y)=\mathbb E\big[(X-\mathbb E X)(Y-\mathbb E Y)\big]
$$

</div>
<div v-click border="2 solid teal-800" bg="teal-800/20" rounded-lg px-4 py-1>
<span class="font-bold text-teal-200">Correlation: covariance on a −1 to 1 scale</span>

$$
\rho=\frac{\operatorname{Cov}(X,Y)}{\sigma_X\,\sigma_Y}\in[-1,1]
$$

</div>
<div v-click class="text-sm" border="2 solid white/5" bg="white/5" rounded-lg px-4 py-2>
ρ = 1: errors identical · ρ = 0: unrelated · ρ = −1: errors exactly opposite
</div>
</div>
</div>

<!--
Four facts from the probability deck carry the whole derivation, so put them on the board.

Expectation is linear, with no conditions at all. Scaling a random variable by a scales its variance by a squared, because variance is measured in squared units. The variance of a sum is the sum of the variances plus twice the covariance. That cross term is the hero of this deck: when two quantities tend to move together it is positive and the sum wobbles more; when they tend to move in opposite directions it is negative and they partly cancel.

Covariance has awkward units, so we rescale it into the correlation rho, which always lies between −1 and 1. Interpret it for models: let X and Y be two models' prediction errors at the same input. rho = 1 means they make literally the same mistakes; rho = 0 means one model's mistake tells you nothing about the other's; rho = −1 means whenever one overshoots, the other undershoots by a matching amount — exactly the marble-jar situation in its most extreme form.
-->

---
glowSeed: 6714
---

# Picturing Correlation Between Errors

<div class="text-sm opacity-85 mt-1">Each dot is one random draw of the training data. Fit model A and model B on it, then record both errors at the same input x₀.</div>

<div class="grid grid-cols-3 gap-6 mt-2">
<div v-click>
<ErrorScatter :rho="1" color="#f87171" />
<div class="text-sm" border="2 solid white/5" bg="white/5" rounded-lg px-3 py-2>
<span class="font-bold text-red-300">Same mistakes</span>
<span class="opacity-85"> — When A overshoots, B overshoots too. Averaging cancels nothing.</span>
</div>
</div>
<div v-click>
<ErrorScatter :rho="0" color="#60a5fa" />
<div class="text-sm" border="2 solid white/5" bg="white/5" rounded-lg px-3 py-2>
<span class="font-bold text-blue-300">Unrelated mistakes</span>
<span class="opacity-85"> — A's error says nothing about B's. Averaging cancels some.</span>
</div>
</div>
<div v-click>
<ErrorScatter :rho="-1" color="#2dd4bf" />
<div class="text-sm" border="2 solid white/5" bg="white/5" rounded-lg px-3 py-2>
<span class="font-bold text-teal-300">Opposite mistakes</span>
<span class="opacity-85"> — A's overshoot is B's undershoot. Averaging cancels all of it.</span>
</div>
</div>
</div>

<!--
This slide makes rho concrete. Fix one input x0. Each dot is one possible training set: draw it, fit model A and model B on it, and record how far each prediction lands from the truth. Repeat many times and you get a cloud. The dashed lines mark zero error, so the center of each plot is "both models exactly right".

Follow the amber dot across the three panels. It is the same training draw every time, the one where model A overshoots the most.

rho = 1: the dots fall on a rising line. On the amber draw, B overshoots by just as much as A. The two models make the same mistakes, so averaging them gives the same mistake back. That is the rho = 1 row of the two-model table coming up: no variance reduction at all.

rho = 0: a round cloud. Knowing A overshot tells you nothing about B; on the amber draw B happens to be wherever it is. Sometimes their errors partly cancel and sometimes they add, and on average the variance of the average is cut in half.

rho = −1: the dots fall on a falling line. Whenever A overshoots, B undershoots by the same amount, so the average lands exactly on the truth. This is the marble jar in its most extreme form.

One honest caveat: rho measures how the errors move together around their own averages. rho = 1 means lockstep, which is "the same mistakes" when, as in this unit, both models have the same bias and the same variance.
-->

---
glowSeed: 6706
---

# Averaging Leaves Bias Unchanged

<div class="text-sm mt-2 opacity-90" border="2 solid amber-800" bg="amber-800/20" rounded-lg px-4 py-2>
<span class="font-bold text-amber-300">Assumption:</span> every f̂<sub>b</sub> comes from the same model/algorithm (same hyperparameters), each fit to a different random draw of the training data.
</div>

<div class="grid grid-cols-2 gap-8 items-start">
<div>
<div v-click class="mt-4" style="font-size: .9em" border="2 solid teal-800" bg="teal-800/20" rounded-lg px-4 py-2>

$$
\mathbb E[\bar f(x_0)]=\frac1B\sum_{b=1}^{B}\mathbb E[\hat f_b(x_0)]
$$

</div>
<div class="space-y-3 mt-4">
<div v-click border="2 solid white/5" bg="white/5" rounded-lg px-4 py-3>
<span class="font-bold text-teal-300">Ensemble bias = average member bias</span>
<span class="text-sm opacity-85"> — Always true, by linearity of expectation.</span>
</div>
<div v-click border="2 solid white/5" bg="white/5" rounded-lg px-4 py-3>
<span class="font-bold text-blue-300">Identically trained members share one bias β</span>
<span class="text-sm opacity-85"> — Same algorithm, same randomization: the average also has bias β.</span>
</div>
</div>
</div>
<div>
<div v-click class="mt-4" border="2 solid white/5" bg="white/5" rounded-lg px-4 py-3>
<span class="font-bold text-amber-300">So the gain must be variance</span>
<span class="text-sm opacity-85"> — Averaging identically trained learners can only reduce variance.</span>
</div>
<div v-click class="mt-4 text-sm" border="2 solid white/5" bg="white/5" rounded-lg px-4 py-3>
<div class="font-bold text-teal-300 mb-2">Consequence for design</div>
Pick members that are already <em>unbiased but noisy</em>, then average away the noise. Deep trees fit that description.
</div>
<div v-click class="mt-4 text-sm" border="2 solid violet-800" bg="violet-800/20" rounded-lg px-4 py-3>
<div class="font-bold text-violet-300 mb-2">The other route</div>
To lower bias, members must not be identically trained. Boosting builds each one to correct the others; mixing algorithms averages different biases.
</div>
</div>
</div>

<!--
Apply the first tool, linearity of expectation, to the averaged prediction. The expected ensemble prediction is the average of the members' expected predictions; subtract the true value f(x0) from both sides and you get the general fact on the first card: the ensemble's bias is the average of the members' biases. That needs no assumptions.

The second card adds one. When the members are identically trained — same algorithm, same hyperparameters, each fit to a training set drawn the same random way (a fresh sample, a bootstrap resample, a different seed) — nothing distinguishes member 1 from member 7 before training. Each prediction at x0 has the same distribution, so the same expected value, so the same bias beta. Averaging B copies of beta gives beta. For ensembles of this kind, which include bagging and random forests, averaging does nothing to bias.

One subtlety worth a sentence: a tree fit to a bootstrap sample sees only about 63% of the distinct rows, so its bias can differ slightly from a tree fit to the full data. Averaging preserves the bootstrap tree's bias. That is why the bagging deck says bias is "essentially" unchanged.

That is a strong design hint. If simple averaging is going to help, the help has to come from variance. So we should average members that are close to right on average but individually noisy: low bias, high variance. Deep, unpruned decision trees are the textbook case, which is why the next deck, bagging, averages deep trees.

The violet card previews the third deck. If your base learner is biased — say a one-split stump — averaging many independent stumps gives you a smoother but equally biased stump. To reduce bias the members must not be identically trained. Boosting builds them in sequence, each aimed at what the others still get wrong. Combining different algorithms can also help: if a tree leans high at some input and a linear model leans low, the average of their biases is smaller than either one's. That is the first card at work.
-->

---
glowSeed: 6707
---

# Two Models: How Much Does Averaging Help?

<div class="grid grid-cols-2 gap-8 items-start">
<div>
<div v-click class="mt-2" style="font-size: .8em" border="2 solid white/5" bg="white/5" rounded-lg px-4 py-1>

$$
\begin{aligned}
\operatorname{Var}\!\Big(\tfrac{f_1+f_2}{2}\Big)&=\tfrac14\big(\sigma^2+\sigma^2+2\rho\sigma^2\big)\\
&=\frac{1+\rho}{2}\,\sigma^2
\end{aligned}
$$

</div>
<div v-click class="mt-4 text-sm" border="2 solid white/5" bg="white/5" rounded-lg px-4 py-3>
Two models, each with prediction variance σ² = 4 and correlation ρ between their errors.
</div>
</div>
<div v-click class="mt-2 text-sm" border="2 solid teal-800" bg="teal-800/20" rounded-lg px-4 py-3>
<table class="w-full">
<thead><tr><th class="text-left">correlation ρ</th><th class="text-right">Var of average</th><th class="text-left pl-4">what happened</th></tr></thead>
<tbody>
<tr><td class="text-amber-300">1</td><td class="text-right">4</td><td class="pl-4">no help at all</td></tr>
<tr><td class="text-blue-300">0.5</td><td class="text-right">3</td><td class="pl-4">some help</td></tr>
<tr><td class="text-teal-300">0</td><td class="text-right">2</td><td class="pl-4">variance halved</td></tr>
<tr><td class="text-violet-300">−1</td><td class="text-right">0</td><td class="pl-4">errors cancel exactly</td></tr>
</tbody>
</table>
</div>
</div>

<!--
Use the toolkit on the smallest possible ensemble: two models, each with prediction variance sigma squared, correlated with coefficient rho. The average is one half times the sum. Pull out the one half — it comes out squared, as a quarter. The variance of the sum is sigma squared plus sigma squared plus twice the covariance, and the covariance is rho times sigma squared by definition of correlation. Simplify and you get one plus rho over two, times sigma squared.

Now read the table with sigma squared = 4. If rho = 1 the two models are clones; the average is just as noisy as either one. If rho = 0.5 we get some help. If they are uncorrelated, averaging two halves the variance. If they are perfectly anti-correlated, the errors cancel exactly and the average has zero variance. That last row is the marble jar taken to the limit.

The lesson that the next slide names: the number of models matters less than how differently they err.
-->

---
glowSeed: 671
---

# Diversity Is the Essential Ingredient

<div class="grid grid-cols-2 gap-6 mt-6">
<div v-click border="2 solid teal-800" bg="teal-800/20" rounded-lg p-4>
<div class="font-bold text-teal-300 mb-2">Identical errors</div>
<div class="text-sm leading-relaxed opacity-90">Perfectly correlated models fail on the same cases. 100 copies of one model cost 100× the compute and give the same answer.</div>
</div>
<div v-click border="2 solid blue-800" bg="blue-800/20" rounded-lg p-4>
<div class="font-bold text-blue-300 mb-2">Different errors</div>
<div class="text-sm leading-relaxed opacity-90">Less-correlated mistakes partially cancel when predictions are combined. Each member's error is diluted by the others.</div>
</div>
</div>

<div v-click class="mt-8 text-center text-lg" border="2 solid white/10" bg="white/5" rounded-lg px-6 py-4>
Members do not need to be individually better. They need to be <span class="text-teal-300 font-bold">wrong in different ways</span>.
</div>

<!--
Name the principle we have now seen three times — in the marble jar, in the ambiguity identity, and in the two-model table. Suppose you train 100 copies of the same deterministic model on the same data. Every copy makes the same predictions and the same mistakes, so the average is identical to any single copy. You paid 100 times the compute for nothing. That is the rho = 1 row.

The flip side is the actual mechanism. If two models tend to be wrong on different examples, combining them lets each one's mistake get diluted or outvoted by the other's correct answer. Stress the banner: this is not about making each member more accurate. A collection of mediocre but differently-wrong models can beat a collection of good but identically-wrong ones.

The practical problem this leaves us with: if we only have one training set and one algorithm, how do we get members that disagree? Keep that question open; we answer it after the general formula.
-->

---
glowSeed: 6715
---

# B Models: Setting Up the Problem

<div v-click class="text-sm mt-2 [&_p]:my-0" border="2 solid amber-800" bg="amber-800/20" rounded-lg px-4 py-2>

<span class="font-bold text-amber-300">Goal:</span> find $\operatorname{Var}(\bar f)$ for the average of B identically trained models, $\bar f=\frac1B\sum_b \hat f_b$, where every model has variance σ² and every pair has correlation ρ.

</div>

<div class="grid grid-cols-2 gap-8 items-start">
<div class="space-y-2 mt-3" style="font-size: .85em">
<div v-click border="2 solid white/5" bg="white/5" rounded-lg px-4 py-1>
<span class="font-bold text-teal-300">What we know</span>

$$
\operatorname{Var}(\hat f_b)=\sigma^2,\qquad \operatorname{Cov}(\hat f_i,\hat f_j)=\rho\,\sigma\cdot\sigma=\rho\sigma^2
$$

</div>
<div v-click border="2 solid white/5" bg="white/5" rounded-lg px-4 py-1>
<span class="font-bold text-blue-300">Step 1: pull out the 1/B</span>

$$
\operatorname{Var}(\bar f)=\operatorname{Var}\Big(\frac1B\sum_b\hat f_b\Big)=\frac{1}{B^2}\operatorname{Var}\Big(\sum_b\hat f_b\Big)
$$

</div>
<div v-click class="text-sm" border="2 solid teal-800" bg="teal-800/20" rounded-lg px-4 py-2>
So the real work is the <span class="font-bold text-teal-200">variance of the sum</span>.
</div>
</div>
<div class="space-y-2 mt-3" style="font-size: .8em">
<div v-click border="2 solid white/5" bg="white/5" rounded-lg px-4 py-1>
<span class="font-bold text-amber-300">Step 2: the sum rule from the toolkit</span>

$$
\operatorname{Var}(X+Y)=\operatorname{Var}X+\operatorname{Var}Y+2\operatorname{Cov}(X,Y)
$$

</div>
<div v-click border="2 solid white/5" bg="white/5" rounded-lg px-4 py-1>
<span class="font-bold text-violet-300">Same rule, as a 2 × 2 grid: add all four cells</span>

$$
\begin{array}{cc} \boxed{\operatorname{Var}X} & \operatorname{Cov}(X,Y)\\[2pt] \operatorname{Cov}(Y,X) & \boxed{\operatorname{Var}Y} \end{array}
$$

</div>
<div v-click border="2 solid white/5" bg="white/5" rounded-lg px-4 py-1>
<span class="font-bold text-teal-300">B models: a B × B grid</span>

$$
\operatorname{Var}\Big(\sum_b\hat f_b\Big)=\sum_{i=1}^{B}\sum_{j=1}^{B}\operatorname{Cov}(\hat f_i,\hat f_j)
$$

</div>
</div>
</div>

<!--
The two-model slide was a warm-up. Now state the real problem before doing any algebra. We have B identically trained models: same algorithm, each fit to a different random draw of the data. By the symmetry argument from the bias slide, every model's prediction has the same variance sigma squared, and every pair of models has the same correlation rho. We want the variance of their average, f-bar.

What we know: the variance of each model is sigma squared. The covariance of any two models is rho times sigma times sigma, which is just the definition of correlation from the toolkit slide, turned around.

Step 1: the average is one over B times a sum. Scaling comes out squared, so the variance of the average is one over B squared times the variance of the sum. That reduces the problem to one question: what is the variance of a sum of B correlated variables?

Step 2: we already have the rule for two variables. Rewrite it so the pattern is visible. Variance X is the covariance of X with itself, and the 2 Cov(X, Y) term is really two terms, Cov(X, Y) and Cov(Y, X). So the variance of a sum of two variables is the sum of four covariances: every pair, in both orders, including each variable with itself. The violet card lays them out as a 2-by-2 grid: the boxed diagonal holds the two variances (a variable's covariance with itself), the off-diagonal holds the two copies of the covariance. With B variables the same rule gives a B-by-B grid, one covariance per cell. The next slide adds up that grid.
-->

---
glowSeed: 6708
---

# B Models: Add Up the Grid

<div class="grid grid-cols-2 gap-8 items-start">
<div>
<div class="space-y-3 mt-4">
<div v-click border="2 solid white/5" bg="white/5" rounded-lg px-4 py-3>
<span class="font-bold text-teal-300">Diagonal</span>
<span class="text-sm opacity-85"> — B cells, each Cov(f̂<sub>b</sub>, f̂<sub>b</sub>) = Var(f̂<sub>b</sub>) = σ².</span>
</div>
<div v-click border="2 solid white/5" bg="white/5" rounded-lg px-4 py-3>
<span class="font-bold text-blue-300">Off-diagonal</span>
<span class="text-sm opacity-85"> — B(B − 1) cells, each Cov(f̂<sub>i</sub>, f̂<sub>j</sub>) = ρσ².</span>
</div>
<div v-click style="font-size: .85em" border="2 solid teal-800" bg="teal-800/20" rounded-lg px-4 py-1>

$$
\operatorname{Var}\Big(\sum_b\hat f_b\Big)=B\sigma^2+B(B-1)\rho\sigma^2
$$

</div>
<div v-click class="text-sm" border="2 solid amber-800" bg="amber-800/20" rounded-lg px-4 py-3>
<span class="font-bold text-amber-300">Next:</span> divide by B² to get Var(f̄), the variance of the average.
</div>
</div>
</div>
<div class="mt-2 max-w-sm mx-auto">
<CovGrid :B="5" />
</div>
</div>

<!--
Here is the grid for B = 5. Every cell would normally hold its own covariance, but our members are identically trained, so there are only two kinds of cells. The B diagonal cells are each model's covariance with itself, which is its variance, sigma squared. The remaining B times B minus 1 cells — 20 of them when B is 5 — are each rho sigma squared.

Add them up and you have the variance of the sum. Have students count the cells on the picture to confirm the B(B−1). Note how quickly the off-diagonal cells dominate: there are B of one kind and roughly B squared of the other, which is why correlation ends up controlling the result for large B.

Remind them this is still the variance of the sum, not the goal. The next slide finishes Step 1 by dividing by B squared.
-->

---
glowSeed: 672
---

# Variance of an Averaged Ensemble

<div class="grid grid-cols-2 gap-8 items-start">
<div>
<div v-click class="mt-2" style="font-size: .8em" border="2 solid white/5" bg="white/5" rounded-lg px-4 py-1>

$$
\begin{aligned}
\operatorname{Var}(\bar f)&=\frac{1}{B^2}\Big[B\sigma^2+B(B-1)\rho\sigma^2\Big]\\
&=\frac{\sigma^2}{B}+\frac{B-1}{B}\,\rho\sigma^2\\
&=\rho\sigma^2+\frac{1-\rho}{B}\,\sigma^2
\end{aligned}
$$

</div>
<div class="space-y-3 mt-4">
<div v-click border="2 solid white/5" bg="white/5" rounded-lg px-4 py-3>
<span class="font-bold text-teal-300">Independent (ρ = 0)</span>
<span class="text-sm opacity-85"> — σ²/B: variance keeps shrinking with B.</span>
</div>
<div v-click border="2 solid white/5" bg="white/5" rounded-lg px-4 py-3>
<span class="font-bold text-blue-300">Correlated (ρ &gt; 0)</span>
<span class="text-sm opacity-85"> — ρσ² does not depend on B. It is a floor.</span>
</div>
</div>
</div>
<div>
<div v-click class="mt-2 text-sm" border="2 solid teal-800" bg="teal-800/20" rounded-lg px-4 py-3>
<div class="font-bold text-teal-300 mb-2">Worked example</div>
σ² = 4, ρ = 0.2<br>
B = 50: &nbsp; 0.2·4 + 0.8·4/50 = 0.8 + 0.064 = <b>0.864</b><br>
B = 500: 0.2·4 + 0.8·4/500 = 0.8 + 0.0064 = <b>0.806</b>
</div>
<div v-click class="mt-4 text-sm" border="2 solid amber-800" bg="amber-800/20" rounded-lg px-4 py-3>
<span class="font-bold text-amber-300">Design implication</span> — once B is moderately large, lowering ρ matters more than adding members.
</div>
</div>
</div>

<!--
Finish Step 1: divide the grid sum by B squared, because the average is one over B times the sum and scaling comes out squared. Line two splits it into the diagonal part, sigma squared over B, and the off-diagonal part, (B−1)/B times rho sigma squared. Line three is the same quantity rearranged: write (B−1)/B as 1 − 1/B and collect terms. This is an exact identity for every B, not a large-B approximation.

The rearranged form has two named pieces. The second term, (1−rho) sigma squared over B, shrinks as you add members. The first term, rho sigma squared, has no B in it at all — it is a floor that no number of members can push through.

Two limits. With rho = 0 the floor vanishes and you get sigma squared over B, which is the same one-over-n shrinkage as the standard error of a sample mean from the model evaluation unit. With rho > 0, variance shrinks toward rho sigma squared, not toward zero.

Work the example. With sigma squared = 4 and rho = 0.2, fifty members give 0.864 and five hundred give 0.806. Ten times the compute bought less than a 7% improvement, because we were already close to the floor of 0.8. Once B is moderate, the way to make progress is to lower rho.
-->

---
glowSeed: 673
---

# Correlation Sets the Variance Floor

<div class="grid grid-cols-2 gap-8 items-start">
<div>
<div class="mt-2" style="font-size: .85em" border="2 solid teal-800" bg="teal-800/20" rounded-lg px-4 py-1>

$$
\operatorname{Var}(\bar f)=\underbrace{\rho\sigma^2}_{\text{floor}}+\underbrace{\frac{1-\rho}{B}\,\sigma^2}_{\to\,0\text{ as }B\text{ grows}}
$$

</div>
<div class="space-y-3 mt-4">
<div v-click border="2 solid white/5" bg="white/5" rounded-lg px-4 py-3>
<span class="font-bold text-teal-300">ρ = 0</span>
<span class="text-sm opacity-85"> — Variance keeps falling toward zero.</span>
</div>
<div v-click border="2 solid white/5" bg="white/5" rounded-lg px-4 py-3>
<span class="font-bold text-blue-300">ρ = 0.2</span>
<span class="text-sm opacity-85"> — More models help, then flatten near 0.2σ².</span>
</div>
<div v-click border="2 solid white/5" bg="white/5" rounded-lg px-4 py-3>
<span class="font-bold text-amber-300">ρ = 0.5</span>
<span class="text-sm opacity-85"> — A highly correlated ensemble has little room to improve.</span>
</div>
</div>
</div>
<div>
<svg role="img" aria-label="Ensemble variance as a fraction of sigma squared versus number of models B on a log scale from 1 to 500. The rho equals 0 curve falls toward 0; the rho equals 0.2 and 0.5 curves level off at dashed floor lines at 0.2 and 0.5." viewBox="0 0 500 310" class="w-full max-w-xl mx-auto mt-7">
  <line x1="60.0" y1="35" x2="60.0" y2="260" stroke="#334155" stroke-width="1"/>
  <line x1="103.5" y1="35" x2="103.5" y2="260" stroke="#334155" stroke-width="1"/>
  <line x1="161.0" y1="35" x2="161.0" y2="260" stroke="#334155" stroke-width="1"/>
  <line x1="204.5" y1="35" x2="204.5" y2="260" stroke="#334155" stroke-width="1"/>
  <line x1="248.0" y1="35" x2="248.0" y2="260" stroke="#334155" stroke-width="1"/>
  <line x1="305.5" y1="35" x2="305.5" y2="260" stroke="#334155" stroke-width="1"/>
  <line x1="349.0" y1="35" x2="349.0" y2="260" stroke="#334155" stroke-width="1"/>
  <line x1="392.5" y1="35" x2="392.5" y2="260" stroke="#334155" stroke-width="1"/>
  <line x1="450.0" y1="35" x2="450.0" y2="260" stroke="#334155" stroke-width="1"/>
  <line x1="60" y1="260" x2="450" y2="260" stroke="#64748b" stroke-width="2"/>
  <line x1="60" y1="35" x2="60" y2="260" stroke="#64748b" stroke-width="2"/>
  <line x1="60" y1="215.0" x2="450" y2="215.0" stroke="#60a5fa" stroke-width="1.5" stroke-dasharray="6 5" opacity="0.8"/>
  <text x="454" y="219.0" fill="#93c5fd" style="font-size: 12px">floor 0.2</text>
  <line x1="60" y1="147.5" x2="450" y2="147.5" stroke="#f59e0b" stroke-width="1.5" stroke-dasharray="6 5" opacity="0.8"/>
  <text x="454" y="151.5" fill="#fbbf24" style="font-size: 12px">floor 0.5</text>
  <polyline points="60.0,35.0 63.2,46.4 66.5,57.1 69.8,67.4 73.0,77.1 76.2,86.3 79.5,95.1 82.8,103.4 86.0,111.3 89.2,118.8 92.5,125.9 95.8,132.7 99.0,139.1 102.2,145.2 105.5,151.0 108.8,156.5 112.0,161.8 115.2,166.7 118.5,171.4 121.8,175.9 125.0,180.1 128.2,184.2 131.5,188.0 134.8,191.6 138.0,195.1 141.2,198.4 144.5,201.5 147.8,204.4 151.0,207.2 154.2,209.9 157.5,212.4 160.8,214.8 164.0,217.1 167.2,219.3 170.5,221.3 173.8,223.3 177.0,225.1 180.2,226.9 183.5,228.6 186.8,230.1 190.0,231.7 193.2,233.1 196.5,234.4 199.8,235.7 203.0,237.0 206.2,238.1 209.5,239.2 212.8,240.3 216.0,241.3 219.2,242.2 222.5,243.1 225.8,244.0 229.0,244.8 232.2,245.5 235.5,246.3 238.8,247.0 242.0,247.6 245.2,248.2 248.5,248.8 251.8,249.4 255.0,249.9 258.2,250.4 261.5,250.9 264.8,251.4 268.0,251.8 271.2,252.2 274.5,252.6 277.8,253.0 281.0,253.4 284.2,253.7 287.5,254.0 290.8,254.3 294.0,254.6 297.2,254.9 300.5,255.1 303.8,255.4 307.0,255.6 310.2,255.8 313.5,256.0 316.8,256.2 320.0,256.4 323.2,256.6 326.5,256.8 329.8,256.9 333.0,257.1 336.2,257.2 339.5,257.4 342.8,257.5 346.0,257.6 349.2,257.8 352.5,257.9 355.8,258.0 359.0,258.1 362.2,258.2 365.5,258.3 368.8,258.4 372.0,258.4 375.2,258.5 378.5,258.6 381.7,258.7 385.0,258.7 388.3,258.8 391.5,258.9 394.7,258.9 398.0,259.0 401.3,259.0 404.5,259.1 407.7,259.1 411.0,259.2 414.2,259.2 417.5,259.2 420.7,259.3 424.0,259.3 427.2,259.4 430.5,259.4 433.7,259.4 437.0,259.4 440.3,259.5 443.5,259.5 446.8,259.5 450.0,259.6" fill="none" stroke="#2dd4bf" stroke-width="4" stroke-linejoin="round"/>
  <polyline points="60.0,35.0 63.2,44.1 66.5,52.7 69.8,60.9 73.0,68.7 76.2,76.1 79.5,83.1 82.8,89.7 86.0,96.1 89.2,102.1 92.5,107.8 95.8,113.2 99.0,118.3 102.2,123.2 105.5,127.8 108.8,132.2 112.0,136.4 115.2,140.4 118.5,144.1 121.8,147.7 125.0,151.1 128.2,154.3 131.5,157.4 134.8,160.3 138.0,163.1 141.2,165.7 144.5,168.2 147.8,170.5 151.0,172.8 154.2,174.9 157.5,176.9 160.8,178.9 164.0,180.7 167.2,182.4 170.5,184.1 173.8,185.6 177.0,187.1 180.2,188.5 183.5,189.8 186.8,191.1 190.0,192.3 193.2,193.5 196.5,194.6 199.8,195.6 203.0,196.6 206.2,197.5 209.5,198.4 212.8,199.2 216.0,200.0 219.2,200.8 222.5,201.5 225.8,202.2 229.0,202.8 232.2,203.4 235.5,204.0 238.8,204.6 242.0,205.1 245.2,205.6 248.5,206.1 251.8,206.5 255.0,207.0 258.2,207.4 261.5,207.7 264.8,208.1 268.0,208.5 271.2,208.8 274.5,209.1 277.8,209.4 281.0,209.7 284.2,209.9 287.5,210.2 290.8,210.4 294.0,210.7 297.2,210.9 300.5,211.1 303.8,211.3 307.0,211.5 310.2,211.7 313.5,211.8 316.8,212.0 320.0,212.1 323.2,212.3 326.5,212.4 329.8,212.6 333.0,212.7 336.2,212.8 339.5,212.9 342.8,213.0 346.0,213.1 349.2,213.2 352.5,213.3 355.8,213.4 359.0,213.5 362.2,213.5 365.5,213.6 368.8,213.7 372.0,213.8 375.2,213.8 378.5,213.9 381.7,213.9 385.0,214.0 388.3,214.0 391.5,214.1 394.7,214.1 398.0,214.2 401.3,214.2 404.5,214.3 407.7,214.3 411.0,214.3 414.2,214.4 417.5,214.4 420.7,214.4 424.0,214.5 427.2,214.5 430.5,214.5 433.7,214.5 437.0,214.6 440.3,214.6 443.5,214.6 446.8,214.6 450.0,214.6" fill="none" stroke="#60a5fa" stroke-width="4" stroke-linejoin="round"/>
  <polyline points="60.0,35.0 63.2,40.7 66.5,46.1 69.8,51.2 73.0,56.0 76.2,60.7 79.5,65.0 82.8,69.2 86.0,73.2 89.2,76.9 92.5,80.5 95.8,83.9 99.0,87.1 102.2,90.1 105.5,93.0 108.8,95.8 112.0,98.4 115.2,100.9 118.5,103.2 121.8,105.4 125.0,107.6 128.2,109.6 131.5,111.5 134.8,113.3 138.0,115.0 141.2,116.7 144.5,118.2 147.8,119.7 151.0,121.1 154.2,122.4 157.5,123.7 160.8,124.9 164.0,126.1 167.2,127.1 170.5,128.2 173.8,129.1 177.0,130.1 180.2,130.9 183.5,131.8 186.8,132.6 190.0,133.3 193.2,134.0 196.5,134.7 199.8,135.4 203.0,136.0 206.2,136.6 209.5,137.1 212.8,137.6 216.0,138.1 219.2,138.6 222.5,139.1 225.8,139.5 229.0,139.9 232.2,140.3 235.5,140.6 238.8,141.0 242.0,141.3 245.2,141.6 248.5,141.9 251.8,142.2 255.0,142.5 258.2,142.7 261.5,143.0 264.8,143.2 268.0,143.4 271.2,143.6 274.5,143.8 277.8,144.0 281.0,144.2 284.2,144.3 287.5,144.5 290.8,144.7 294.0,144.8 297.2,144.9 300.5,145.1 303.8,145.2 307.0,145.3 310.2,145.4 313.5,145.5 316.8,145.6 320.0,145.7 323.2,145.8 326.5,145.9 329.8,146.0 333.0,146.0 336.2,146.1 339.5,146.2 342.8,146.3 346.0,146.3 349.2,146.4 352.5,146.4 355.8,146.5 359.0,146.5 362.2,146.6 365.5,146.6 368.8,146.7 372.0,146.7 375.2,146.8 378.5,146.8 381.7,146.8 385.0,146.9 388.3,146.9 391.5,146.9 394.7,147.0 398.0,147.0 401.3,147.0 404.5,147.0 407.7,147.1 411.0,147.1 414.2,147.1 417.5,147.1 420.7,147.1 424.0,147.2 427.2,147.2 430.5,147.2 433.7,147.2 437.0,147.2 440.3,147.2 443.5,147.3 446.8,147.3 450.0,147.3" fill="none" stroke="#f59e0b" stroke-width="4" stroke-linejoin="round"/>
  <g fill="#cbd5e1" style="font-size: 12px" text-anchor="end"><text x="53" y="39">1</text><text x="53" y="152">0.5</text><text x="53" y="264">0</text></g>
  <text x="20" y="150" fill="#94a3b8" style="font-size: 12px" text-anchor="middle" transform="rotate(-90 20 150)">Var(f̄) / σ²</text>
  <g fill="#cbd5e1" style="font-size: 12px" text-anchor="middle"><text x="60.0" y="280">1</text><text x="103.5" y="280">2</text><text x="161.0" y="280">5</text><text x="204.5" y="280">10</text><text x="248.0" y="280">20</text><text x="305.5" y="280">50</text><text x="349.0" y="280">100</text><text x="392.5" y="280">200</text><text x="450.0" y="280">500</text></g>
  <text x="255" y="303" fill="#94a3b8" style="font-size: 12px" text-anchor="middle">B (number of models, log scale)</text>
  <g style="font-size: 13px"><text x="330" y="50" fill="#5eead4">ρ = 0</text><text x="330" y="68" fill="#93c5fd">ρ = 0.2</text><text x="330" y="86" fill="#fbbf24">ρ = 0.5</text></g>
</svg>

</div>
</div>

<!--
The equation at the top is the result from the last slide. The first term, rho sigma squared, has no B in it: that is the floor. The second term shrinks to zero as B grows. The chart plots this formula divided by sigma squared: Var(f-bar)/sigma squared = rho + (1−rho)/B, for three correlation levels. The horizontal axis is on a log scale, so each gridline step multiplies the number of models rather than adding to it. All three curves start at 1, since a single model's average is itself. The dashed lines are the floors, rho sigma squared, which read as 0.2 and 0.5 on this scale.

The teal rho = 0 curve keeps falling; at B = 500 it is 0.002. The blue rho = 0.2 curve drops fast from 1 to 10 members, then flattens near 0.2 and gains almost nothing from 50 to 500. The amber rho = 0.5 curve flattens even earlier and higher.

Have students recognize the shape: a steep drop, then a plateau. Real random forests behave exactly like this. Going from 10 to 100 trees usually helps noticeably; going from 500 to 5,000 barely registers. The height of the plateau is set by rho, which is why the next deck spends so much effort decorrelating trees.
-->

---
glowSeed: 6709
---

# Where Does Diversity Come From?

<div class="grid grid-cols-2 gap-4 mt-6">
<div v-click border="2 solid teal-800" bg="teal-800/20" rounded-lg p-4>
<div class="font-bold text-teal-300 mb-2">Different rows</div>
<div class="text-sm leading-relaxed opacity-90">Train each member on a bootstrap resample of the data. <span class="opacity-70">→ bagging</span></div>
</div>
<div v-click border="2 solid blue-800" bg="blue-800/20" rounded-lg p-4>
<div class="font-bold text-blue-300 mb-2">Different features</div>
<div class="text-sm leading-relaxed opacity-90">Let each split see only a random subset of features. <span class="opacity-70">→ random forests</span></div>
</div>
<div v-click border="2 solid amber-800" bg="amber-800/20" rounded-lg p-4>
<div class="font-bold text-amber-300 mb-2">Different focus</div>
<div class="text-sm leading-relaxed opacity-90">Build each member to fix what the ensemble still gets wrong. <span class="opacity-70">→ boosting</span></div>
</div>
<div v-click border="2 solid violet-800" bg="violet-800/20" rounded-lg p-4>
<div class="font-bold text-violet-300 mb-2">Different algorithms</div>
<div class="text-sm leading-relaxed opacity-90">Combine a tree, a logistic regression, and a k-NN. <span class="opacity-70">→ voting and stacking</span></div>
</div>
</div>

<!--
Back to the question we left open: with one dataset, how do we manufacture members that disagree? Every method in this unit is an answer.

Different rows: resample the training data with replacement, so each member sees a slightly different dataset. That is bagging, the subject of the next deck. Different features: also restrict which features each split may use, which pushes rho down further when one strong feature would otherwise make every tree look alike. That is a random forest. Different focus: rather than independent members, build them in sequence, each concentrating on the examples the ensemble so far gets wrong. That is boosting, and its diversity is deliberate specialization rather than randomness. Different algorithms: models with different inductive biases tend to make different kinds of mistakes, so simply combining a tree, a linear model and a nearest-neighbor model can work well.

Frame the whole unit this way: underneath the mechanics, every ensemble method is a way of manufacturing useful disagreement.
-->

---
glowSeed: 6717
---

# Classification: Ensembles That Vote

<div class="text-sm opacity-80 -mt-2">Class labels, combined by majority vote</div>

<div class="grid grid-cols-2 gap-8 items-start">
<div class="space-y-3 mt-4">
<div v-click border="2 solid teal-800" bg="teal-800/20" rounded-lg px-4 py-3>
<span class="font-bold text-teal-300">The regression answer</span>
<span class="text-sm opacity-85"> — Averaging leaves bias unchanged and cuts variance toward the floor ρσ². Low correlation is what matters.</span>
</div>
<div v-click border="2 solid amber-800" bg="amber-800/20" rounded-lg px-4 py-3>
<span class="font-bold text-amber-300">The new problem</span>
<span class="text-sm opacity-85"> — Classifiers output labels. You can't average "spam" and "not spam", so the ensemble takes a majority vote.</span>
</div>
<div v-click border="2 solid white/5" bg="white/5" rounded-lg px-4 py-3>
<span class="font-bold text-blue-300">New tool</span>
<span class="text-sm opacity-85"> — Instead of variance, count: what is the probability that most votes are correct?</span>
</div>
</div>
<div class="space-y-3 mt-4">
<div v-click class="font-bold text-blue-300">Three questions to answer</div>
<div v-click border="2 solid white/5" bg="white/5" rounded-lg px-4 py-3>
<span class="font-bold text-teal-300">1.</span>
<span class="text-sm opacity-85"> When is the vote more accurate than each voter?</span>
</div>
<div v-click border="2 solid white/5" bg="white/5" rounded-lg px-4 py-3>
<span class="font-bold text-blue-300">2.</span>
<span class="text-sm opacity-85"> Does adding voters always help?</span>
</div>
<div v-click border="2 solid white/5" bg="white/5" rounded-lg px-4 py-3>
<span class="font-bold text-violet-300">3.</span>
<span class="text-sm opacity-85"> What plays the role of the correlation ρ?</span>
</div>
</div>
</div>

<!--
Mark the switch out loud: everything so far has been regression, where predictions are numbers and the ensemble averages them. Summarize the answer we got. Averaging identically trained models leaves bias alone, cuts variance, and the variance can't fall below rho sigma squared, so low correlation between members is the key ingredient.

Now the problem changes. A classifier outputs a label. There is no meaningful average of "spam" and "not spam", so the standard way to combine classifiers is a majority vote: predict whatever label most members predict. (Soft voting, which averages predicted probabilities, is closer to the regression story; here we focus on hard votes.)

Because the output is right-or-wrong, the natural tool is counting rather than variance: if each voter is right with some probability, what is the probability that more than half of them are right?

Pose the three questions. Question 1: the coin-flip model shows the vote beats each voter when voters are independent and better than chance. Question 2: no — the "only above 50%" slide shows that voters worse than chance make the vote worse as you add them. Question 3: independence of errors plays the role of rho = 0, and the error-pattern slide shows what happens when errors line up.
-->

---
glowSeed: 6710
---

# Classification: Each Vote Is a Coin Flip

<div class="grid grid-cols-2 gap-8 items-start">
<div>
<div class="space-y-3 mt-4">
<div v-click border="2 solid white/5" bg="white/5" rounded-lg px-4 py-3>
<span class="font-bold text-teal-300">One voter</span>
<span class="text-sm opacity-85"> — Correct with probability p: a Bernoulli trial.</span>
</div>
<div v-click border="2 solid white/5" bg="white/5" rounded-lg px-4 py-3>
<span class="font-bold text-blue-300">B independent voters</span>
<span class="text-sm opacity-85"> — The number correct is Binomial(B, p).</span>
</div>
<div v-click style="font-size: .85em" border="2 solid teal-800" bg="teal-800/20" rounded-lg px-4 py-1>

$$
P(k\text{ correct})=\underbrace{\binom{B}{k}}_{\text{ways}}\;\underbrace{p^k(1-p)^{B-k}}_{\text{one pattern}}
$$

</div>
<div v-click border="2 solid white/5" bg="white/5" rounded-lg px-4 py-3>
<span class="font-bold text-amber-300">Majority vote is right</span>
<span class="text-sm opacity-85"> — When more than half of the votes are correct.</span>
</div>
</div>
</div>
<div v-click class="mt-4 text-sm" border="2 solid teal-800" bg="teal-800/20" rounded-lg px-4 py-3>
<div class="font-bold text-teal-300 mb-2">B = 3, p = 0.7: list every outcome</div>
<table class="w-full">
<thead><tr><th class="text-left">correct votes</th><th class="text-right">ways</th><th class="text-right">probability</th></tr></thead>
<tbody>
<tr class="text-teal-300"><td>3</td><td class="text-right">1</td><td class="text-right">0.7³ = 0.343</td></tr>
<tr class="text-teal-300"><td>2</td><td class="text-right">3</td><td class="text-right">3 · 0.7² · 0.3 = 0.441</td></tr>
<tr class="opacity-70"><td>1</td><td class="text-right">3</td><td class="text-right">3 · 0.7 · 0.3² = 0.189</td></tr>
<tr class="opacity-70"><td>0</td><td class="text-right">1</td><td class="text-right">0.3³ = 0.027</td></tr>
<tr class="font-bold"><td>majority right</td><td></td><td class="text-right">0.343 + 0.441 = 0.784</td></tr>
</tbody>
</table>
</div>
</div>

<!--
Variance is the natural language for regression. For classification there is a parallel argument that uses counting instead.

Treat each classifier's answer on a given example as a coin flip that comes up "correct" with probability p. If the B classifiers are independent, the number of correct votes is a Binomial random variable with parameters B and p. A majority vote is right exactly when more than half of the votes are correct.

The teal card is the binomial formula for exactly k correct votes. It has two pieces. One specific right/wrong pattern with k right and B − k wrong has probability p to the k times (1 − p) to the B − k, because independent probabilities multiply. B-choose-k counts how many such patterns there are, that is, which k voters are the right ones.

Enumerate the smallest interesting case by hand: three voters, each 70% accurate. There are eight possible right/wrong patterns. All three right happens with probability 0.343. Exactly two right can happen three ways — RRW, RWR, WRR, so 3-choose-2 = 3 — each with probability 0.7 squared times 0.3, so 0.441 in total. Those two rows are the majority-correct outcomes, summing to 0.784. Check the table sums to one: 0.343 + 0.441 + 0.189 + 0.027 = 1.

So three independent 70% classifiers vote their way to 78.4%, better than any one of them.
-->

---
glowSeed: 674
---

# Majority Vote Beats Any Single Voter

<div class="grid grid-cols-2 gap-8 items-start">
<div>
<div class="space-y-3 mt-4">
<div v-click border="2 solid white/5" bg="white/5" rounded-lg px-4 py-3>
<span class="font-bold text-teal-300">Setup</span>
<span class="text-sm opacity-85"> — B independent classifiers (B odd), each correct with probability p &gt; 0.5.</span>
</div>
<div v-click border="2 solid white/5" bg="white/5" rounded-lg px-4 py-3>
<span class="font-bold text-blue-300">Majority correct</span>
<span class="text-sm opacity-85"> — Sum the Binomial(B, p) upper tail, from ⌊B/2⌋ + 1 correct votes.</span>
</div>
<div v-click border="2 solid white/5" bg="white/5" rounded-lg px-4 py-3>
<span class="font-bold text-amber-300">B → ∞</span>
<span class="text-sm opacity-85"> — Majority-vote accuracy converges to 1, however small the edge over chance.</span>
</div>
</div>
</div>
<div>
<div v-click class="mt-4" style="font-size: .82em" border="2 solid teal-800" bg="teal-800/20" rounded-lg px-4 py-3>

$$
P(\text{majority correct})=\sum_{k=\lfloor B/2\rfloor+1}^{B}\binom{B}{k}p^k(1-p)^{B-k}
$$

</div>
<div v-click class="mt-4 text-sm" border="2 solid white/5" bg="white/5" rounded-lg px-4 py-3>
p = 0.7: &nbsp; B = 1 → 0.70 · B = 3 → 0.784 · B = 5 → 0.837 · B = 11 → 0.922 · B = 21 → 0.974
</div>
</div>
</div>

<!--
Generalize the table. With B voters, an odd number so there are no ties, the majority is right when at least floor(B/2) + 1 votes are correct. Each count k has B-choose-k arrangements, each with probability p to the k times (1−p) to the B−k. Summing over the upper tail gives the formula. For B = 3 this is exactly the two rows we added by hand.

Read off the numbers for p = 0.7. One voter, 70%. Three, 78.4%. Five, 83.7%. Eleven, 92.2%. Twenty-one, 97.4%. In the limit the accuracy goes to 1. This result is the Condorcet jury theorem, from 18th-century voting theory, and it holds for any p above one half, however slight the edge.

Immediately flag the assumption it leans on hardest: independence. Real ensemble members are trained on overlapping data and are correlated, so the clean convergence to 1 does not literally happen in practice. The next two slides show both how sensitive the result is to p, and what correlation does to it. Note too that this is the same idea as the variance formula, told for votes instead of averages.
-->

---
glowSeed: 6711
---

# More Voters Help Only Above 50%

<div class="grid grid-cols-2 gap-8 items-start">
<div>
<div class="space-y-3 mt-4">
<div v-click border="2 solid white/5" bg="white/5" rounded-lg px-4 py-3>
<span class="font-bold text-teal-300">p = 0.7</span>
<span class="text-sm opacity-85"> — Above 97% by B = 21.</span>
</div>
<div v-click border="2 solid white/5" bg="white/5" rounded-lg px-4 py-3>
<span class="font-bold text-blue-300">p = 0.55</span>
<span class="text-sm opacity-85"> — A weak edge still grows, slowly: 76% at B = 51.</span>
</div>
<div v-click border="2 solid white/5" bg="white/5" rounded-lg px-4 py-3>
<span class="font-bold text-red-300">p = 0.45</span>
<span class="text-sm opacity-85"> — Worse than chance: voting amplifies the error, down to 24%.</span>
</div>
<div v-click border="2 solid amber-800" bg="amber-800/20" rounded-lg px-4 py-3>
<span class="font-bold text-amber-300">Takeaway</span>
<span class="text-sm opacity-85"> — Voting magnifies whichever side of 50% the members are on.</span>
</div>
</div>
</div>
<svg role="img" aria-label="Majority-vote accuracy versus number of independent voters from 1 to 51. Curves for p equal 0.7, 0.6 and 0.55 rise toward 1; the curve for p equal 0.45 falls toward 0." viewBox="0 0 500 310" class="w-full mt-6">
  <line x1="60" y1="260" x2="470" y2="260" stroke="#64748b" stroke-width="2"/>
  <line x1="60" y1="30" x2="60" y2="260" stroke="#64748b" stroke-width="2"/>
  <line x1="60" y1="173.8" x2="470" y2="173.8" stroke="#64748b" stroke-width="1" stroke-dasharray="4 5"/>
  <g fill="#cbd5e1" style="font-size: 12px" text-anchor="end"><text x="52" y="264">0.2</text><text x="52" y="206">0.4</text><text x="52" y="149">0.6</text><text x="52" y="91">0.8</text><text x="52" y="34">1.0</text></g>
  <g fill="#cbd5e1" style="font-size: 12px" text-anchor="middle"><text x="60" y="280">1</text><text x="142" y="280">11</text><text x="224" y="280">21</text><text x="306" y="280">31</text><text x="388" y="280">41</text><text x="470" y="280">51</text></g>
  <text x="265" y="302" fill="#94a3b8" style="font-size: 12px" text-anchor="middle">B (number of independent voters)</text>
  <text x="18" y="145" fill="#94a3b8" style="font-size: 12px" text-anchor="middle" transform="rotate(-90 18 145)">majority-vote accuracy</text>
  <polyline points="60,116 76,92 93,77 109,66 126,58 142,52 158,48 175,44 191,42 208,39 224,38 240,36 257,35 273,34 290,33 306,33 322,32 339,32 355,32 372,31 388,31 404,31 421,31 437,31 454,30 470,30" fill="none" stroke="#2dd4bf" stroke-width="3.5"/>
  <polyline points="60,145 76,131 93,121 109,113 126,107 142,101 158,96 175,91 191,87 208,84 224,80 240,77 257,74 273,72 290,69 306,67 322,65 339,63 355,61 372,59 388,58 404,56 421,55 437,54 454,52 470,51" fill="none" stroke="#a78bfa" stroke-width="3.5" stroke-dasharray="9 6"/>
  <polyline points="60,159 76,152 93,147 109,143 126,139 142,135 158,132 175,130 191,127 208,125 224,122 240,120 257,118 273,116 290,114 306,112 322,111 339,109 355,108 372,106 388,105 404,103 421,102 437,100 454,99 470,98" fill="none" stroke="#60a5fa" stroke-width="3.5" stroke-dasharray="3 5"/>
  <polyline points="60,188 76,195 93,201 109,205 126,209 142,212 158,215 175,218 191,220 208,223 224,225 240,227 257,229 273,231 290,233 306,235 322,237 339,238 355,240 372,242 388,243 404,244 421,246 437,247 454,248 470,250" fill="none" stroke="#f87171" stroke-width="3.5"/>
  <g style="font-size: 13px" text-anchor="end"><text x="466" y="22" fill="#5eead4">p = 0.7</text><text x="466" y="68" fill="#c4b5fd">p = 0.6</text><text x="466" y="90" fill="#93c5fd">p = 0.55</text><text x="466" y="240" fill="#fca5a5">p = 0.45</text></g>
  <text x="74" y="168" fill="#94a3b8" style="font-size: 11px">chance (0.5)</text>
</svg>
</div>

<!--
This chart plots the majority-vote formula for B from 1 to 51 at four member accuracies. The dashed line is chance, 0.5.

The teal p = 0.7 curve shoots up and is essentially at 1 by B = 31. The violet p = 0.6 curve reaches about 93% at B = 51. The blue p = 0.55 curve shows that even a weak edge compounds, but slowly: 76% at 51 voters.

The red curve is the warning. Members that are 45% accurate — slightly worse than chance on a binary problem — get worse when you add more of them: 24% at B = 51, heading to zero. Voting does not create skill; it magnifies whatever the members have, in whichever direction. This is why boosting insists on weak learners being at least slightly better than chance, a condition you will see written into AdaBoost.
-->

---
glowSeed: 6712
---

# Same Accuracy, Different Error Patterns

<div class="grid grid-cols-3 gap-6 mt-4">
<div v-click><VoteGrid title="Identical errors" color="text-amber-300" :rows="['1111110000','1111110000','1111110000']" /></div>
<div v-click><VoteGrid title="Spread-out errors" color="text-teal-300" :rows="['1111110000','1110001110','0001111110']" /></div>
<div v-click><VoteGrid title="Wasted agreement" color="text-red-300" :rows="['1111110000','1111001100','1111000011']" /></div>
</div>

<div v-click class="mt-6 text-sm" border="2 solid white/5" bg="white/5" rounded-lg px-4 py-3>
Three classifiers, ten test examples, every classifier 60% accurate. Majority vote ranges from <b class="text-red-300">40%</b> to <b class="text-teal-300">90%</b>. If the errors were independent, it would average <b>64.8%</b>.
</div>

<!--
The jury theorem assumed independence. This slide shows how much that assumption is worth, using an example small enough to check by eye. Each grid has three classifiers, A, B and C, scored on the same ten test examples. Teal is correct, red is wrong. Every row has exactly six teal cells, so every classifier is 60% accurate in all three panels. The bottom row is the majority vote.

Left: the three classifiers make identical mistakes, so the vote is just the same 60%. Middle: the mistakes are spread out so that on nine of the ten examples exactly two classifiers are right. The vote gets 90%. Right: the classifiers all agree on the four easy examples, and each one is alone in getting a different two of the rest. Their correct votes are wasted, and the vote falls to 40%, worse than any member.

So with members of identical accuracy, the ensemble can land anywhere from 40% to 90% depending only on how the errors line up. Independent errors would give 3 × 0.36 × 0.4 + 0.216 = 64.8% on average. Accuracy alone tells you nothing about how good an ensemble will be; the pattern of agreement does.
-->

---
glowSeed: 675
---

# Bias–Variance, Revisited

<div class="grid grid-cols-2 gap-8 items-start">
<div>
<div v-click class="mt-4" style="font-size: .85em" border="2 solid white/5" bg="white/5" rounded-lg px-4 py-2>

$$
\text{Expected error}=\text{Bias}^2+\text{Variance}+\sigma_\varepsilon^2
$$

</div>
<div class="space-y-3 mt-4">
<div v-click border="2 solid white/5" bg="white/5" rounded-lg px-4 py-3>
<span class="font-bold text-teal-300">Averaging (bagging, forests)</span>
<span class="text-sm opacity-85"> — Start with low-bias, high-variance deep trees; cut variance toward ρσ².</span>
</div>
<div v-click border="2 solid white/5" bg="white/5" rounded-lg px-4 py-3>
<span class="font-bold text-blue-300">Correcting (boosting)</span> <span class="text-xs uppercase tracking-wide text-blue-200 opacity-80">preview</span>
<span class="text-sm opacity-85"> — Train models in sequence; each fits what the ensemble still gets wrong, and the models are added, not averaged. Starts from high-bias stumps and cuts bias. Covered in the third deck.</span>
</div>
<div v-click border="2 solid white/5" bg="white/5" rounded-lg px-4 py-3>
<span class="font-bold text-red-300">Nothing touches σ²<sub>ε</sub></span>
<span class="text-sm opacity-85"> — Label noise is a property of the data, not the model.</span>
</div>
</div>
</div>
<div>
<div class="mt-5" role="img" aria-label="Base learner then Manufacture diversity then Combine then Lower test error">
<div v-click class="flex items-center gap-3">
<div class="w-8 h-8 rounded-full bg-teal-500/20 border-2 border-teal-700 flex items-center justify-center text-sm font-bold">1</div>
<div class="flex-1 rounded-lg border-2 border-white/10 bg-white/5 px-3 py-2 text-sm font-bold">Choose a base learner</div>
</div>
<div class="ml-4 h-1 border-l-2 border-teal-400/50"></div>
<div v-click class="flex items-center gap-3">
<div class="w-8 h-8 rounded-full bg-blue-500/20 border-2 border-blue-700 flex items-center justify-center text-sm font-bold">2</div>
<div class="flex-1 rounded-lg border-2 border-white/10 bg-white/5 px-3 py-2 text-sm font-bold">Manufacture diversity</div>
</div>
<div class="ml-4 h-1 border-l-2 border-teal-400/50"></div>
<div v-click class="flex items-center gap-3">
<div class="w-8 h-8 rounded-full bg-amber-500/20 border-2 border-amber-700 flex items-center justify-center text-sm font-bold">3</div>
<div class="flex-1 rounded-lg border-2 border-white/10 bg-white/5 px-3 py-2 text-sm font-bold">Combine</div>
</div>
<div class="ml-4 h-1 border-l-2 border-teal-400/50"></div>
<div v-click class="flex items-center gap-3">
<div class="w-8 h-8 rounded-full bg-violet-500/20 border-2 border-violet-700 flex items-center justify-center text-sm font-bold">4</div>
<div class="flex-1 rounded-lg border-2 border-white/10 bg-white/5 px-3 py-2 text-sm font-bold">Lower test error</div>
</div>
</div>

</div>
</div>

<!--
Put the deck back into the bias–variance decomposition from the core concepts unit: expected error is bias squared plus variance plus noise. Note the noise term is written sigma-epsilon squared, to keep it separate from the prediction variance sigma squared we have used all deck.

The two upcoming decks attack different terms from opposite corners. Bagging and random forests start with a low-bias, high-variance learner — a deep tree — because averaging leaves bias alone and cuts variance toward the rho sigma squared floor. Boosting is new here, so define it briefly and flag it as a preview: we have not derived anything about it in this deck. It starts with a high-bias, low-variance learner — a stump — and builds members in sequence. Each new member is trained on what the ensemble still gets wrong (for regression, the remaining errors), and the members are added up rather than averaged, so bias falls round by round. A quick example: predict a price of 300; the first stump says 250, the second is trained on the leftover +50 and says +40, the third on the leftover +10 and says +8, and the running sum is 250, 290, 298. This works where averaging cannot because the members are not identically trained — the other route from the bias slide. The third deck develops it properly. Neither touches noise: if identical inputs genuinely carry different labels, no model can predict that away.

Walk the four-step pipeline as the shape both methods share: pick a base learner whose weak spot you intend to fix, manufacture diversity suited to that goal, combine, and end with lower test error. If students keep one idea from this deck, make it this: name where the base learner sits in the bias–variance tradeoff, and you can predict which ensembling strategy suits it.
-->

---
glowSeed: 676
---

# The Limits of Ensembling

<div class="grid grid-cols-2 gap-4 mt-6">
<div v-click border="2 solid teal-800" bg="teal-800/20" rounded-lg p-4>
<div class="font-bold text-teal-300 mb-2">Noise floor</div>
<div class="text-sm leading-relaxed opacity-90">No ensemble can remove irreducible uncertainty in the data.</div>
</div>
<div v-click border="2 solid blue-800" bg="blue-800/20" rounded-lg p-4>
<div class="font-bold text-blue-300 mb-2">Diminishing returns</div>
<div class="text-sm leading-relaxed opacity-90">Additional estimators eventually add little accuracy.</div>
</div>
<div v-click border="2 solid amber-800" bg="amber-800/20" rounded-lg p-4>
<div class="font-bold text-amber-300 mb-2">Latency and compute</div>
<div class="text-sm leading-relaxed opacity-90">Hundreds of models cost more to train and query than one.</div>
</div>
<div v-click border="2 solid violet-800" bg="violet-800/20" rounded-lg p-4>
<div class="font-bold text-violet-300 mb-2">Interpretability</div>
<div class="text-sm leading-relaxed opacity-90">A forest is harder to explain than a single tree.</div>
</div>
</div>


<!--
Close the theory with what ensembling cannot do. Noise floor: every technique in this unit works on bias or variance. None touches sigma-epsilon squared. If two patients with identical measured features respond differently to the same treatment for reasons not in the data, a thousand trees will not resolve it. This floor is separate from, and in addition to, the rho sigma squared correlation floor.

Diminishing returns follows from the variance-floor chart: past the steep part of the curve, extra members buy almost nothing. For averaging methods that wastes compute; you will see in the boosting deck that for boosting, extra rounds can actively hurt.

Latency and compute: an ensemble of 500 trees runs 500 models for every prediction, which matters a lot for real-time or on-device use even when it does not matter for offline scoring.

Interpretability: one tree can be drawn on a page and read like a flowchart. Five hundred cannot. Feature importances and tools like SHAP values are useful summaries of an ensemble's behavior, but they are summaries, not the decision logic itself. Accuracy is only one axis; weigh cost and explainability before reaching for an ensemble by default.
-->

---
glowSeed: 677
---

# Why Ensembles Work

<div class="mt-8"><div class="grid grid-cols-3 gap-4 mt-6">
<div v-click border="2 solid teal-800" bg="teal-800/20" rounded-lg p-4>
<div class="font-bold text-teal-300 mb-2">Diversity</div>
<div class="text-sm leading-relaxed opacity-90">The gain from averaging is exactly the members' disagreement.</div>
</div>
<div v-click border="2 solid blue-800" bg="blue-800/20" rounded-lg p-4>
<div class="font-bold text-blue-300 mb-2">Correlation</div>
<div class="text-sm leading-relaxed opacity-90">Var = ρσ² + (1 − ρ)σ²/B. ρ sets the floor; B only approaches it.</div>
</div>
<div v-click border="2 solid amber-800" bg="amber-800/20" rounded-lg p-4>
<div class="font-bold text-amber-300 mb-2">Tradeoffs</div>
<div class="text-sm leading-relaxed opacity-90">Noise, cost, and opacity remain.</div>
</div>
</div></div>

<div v-click class="mt-10 text-center text-lg" border="2 solid white/10" bg="white/5" rounded-lg px-6 py-4>Next: Bagging and Random Forests — manufacturing diversity from one dataset.</div>

<!--
Have students restate the three cards in their own words. Diversity: the ambiguity identity says the ensemble's improvement over a typical member is exactly how much the members disagree, so identical members gain nothing. Correlation: the variance of an average is rho sigma squared plus (1−rho) sigma squared over B; adding members only approaches the floor, and lowering rho lowers the floor itself. For classifiers, the same story appears as majority voting, which helps only when members beat chance and err independently. Tradeoffs: even a perfect ensemble leaves noise untouched, costs more to run, and is harder to explain.

Bridge to the next deck with the open practical question: we have one training set and want many members whose errors are only weakly correlated. Bagging answers it by resampling the rows, and random forests go further by resampling features. Keep the variance formula handy; the next deck will keep pointing back to it.
-->
