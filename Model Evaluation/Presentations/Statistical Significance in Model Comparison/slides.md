---
theme: default
highlighter: shiki
css: unocss
colorSchema: dark
title: 'Statistical Significance in Model Comparison'
info: |
  ## Statistical Significance in Model Comparison
  Is a measured improvement real—or sampling noise?
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
glowSeed: 550
---

# Statistical Significance in Model Comparison

### Is a measured improvement real—or sampling noise?

<div class="pt-8 opacity-80 text-lg">Model Evaluation · Foundations of Machine Learning</div>

<div class="mt-14 flex justify-center gap-4" aria-hidden="true">
<div class="w-28 h-3 rounded-full bg-teal-400/70"></div>
<div class="w-20 h-3 rounded-full bg-blue-400/60"></div>
<div class="w-14 h-3 rounded-full bg-violet-400/50"></div>
</div>

<!--
The last two decks built up a full toolkit of evaluation metrics — accuracy, precision, recall, F1, ROC-AUC, and the confusion matrix they all come from. This deck asks a question none of those tools answer by themselves: if model B scores 91% and model A scores 89% on the same test set, is B actually better, or did it just get a slightly easier random sample of test cases?

Roadmap: treat any test-set score as a random variable, then formalize "is this gap real" with the null-hypothesis significance-testing frame. We apply McNemar's test to paired classifier predictions, examine dependence in cross-validation comparisons, build a bootstrap interval for a metric difference, and separate statistical significance from practical significance. Along the way we add confidence intervals for a single score, Type I/II errors and statistical power, a guide to choosing the right test, and the multiple-comparisons trap.
-->

---
glowSeed: 551
---

# Performance Estimates Are Random Variables

<div class="grid grid-cols-2 gap-8 items-start">
<div>
<div class="space-y-3 mt-4">
<div v-click border="2 solid white/5" bg="white/5" rounded-lg px-4 py-3>
<span class="font-bold text-teal-300">A test score is a statistic</span>
<span class="text-sm opacity-85"> — It depends on which observations landed in the test set.</span>
</div>
<div v-click border="2 solid white/5" bg="white/5" rounded-lg px-4 py-3>
<span class="font-bold text-blue-300">Resample, remeasure</span>
<span class="text-sm opacity-85"> — A different split gives a different number for the same procedure.</span>
</div>
<div v-click border="2 solid white/5" bg="white/5" rounded-lg px-4 py-3>
<span class="font-bold text-amber-300">Implication</span>
<span class="text-sm opacity-85"> — "91% vs. 89%" is incomplete without a sense of uncertainty.</span>
</div>
</div>
</div>
<div>
<div v-click class="mt-4" style="font-size: .9em" border="2 solid teal-800" bg="teal-800/20" rounded-lg px-4 py-3>

$$
\widehat{\mathrm{Acc}}=\frac1n\sum_{i=1}^n\mathbf1[\hat y_i=y_i]
$$

</div>

</div>
</div>

<!--
Read the formula symbol by symbol: accuracy-hat is the mean, over the n test examples, of the indicator function 1[·], which equals 1 when the predicted label ŷ_i matches the true label y_i and 0 otherwise — literally "count how many predictions were right, divide by n." That makes accuracy-hat a sample mean, exactly like the sample mean of any other measured quantity, and every sample mean has a sampling distribution: if you drew a different random test set of the same size from the same underlying population, you would get a different accuracy-hat, purely from which examples happened to land in the sample. The n in the denominator directly controls how much this number bounces around — a 100-example test set produces a far noisier accuracy-hat than a 100,000-example one.

This connects directly to the sampling distribution of a sample mean, a concept from introductory statistics: just as a poll of 100 people gives an estimate of a population opinion with a margin of error, a test accuracy of 91% on 200 examples is an estimate with its own margin of error, not a platonic fact about the model. The implication for model comparison: seeing "91% vs. 89%" and declaring the 91% model the winner is exactly like seeing two polls, 51% vs. 49%, and declaring a landslide — the raw numbers alone cannot tell you whether the gap reflects a real difference or is well within the noise you would expect from resampling. The rest of this deck builds tools to make that judgment rigorously instead of by eyeballing two numbers.
-->

---
glowSeed: 5520
---

# What Are We Estimating?

<div class="grid grid-cols-2 gap-8 items-start">
<div>
<div class="space-y-3 mt-2">
<div v-click border="2 solid teal-800" bg="teal-800/20" rounded-lg px-4 py-3>
<span class="font-bold text-teal-200">p — true accuracy</span>
<span class="text-sm opacity-85"> — The fraction the model would get right on <em>all</em> data it could ever see. Fixed, but unknown.</span>
</div>
<div v-click border="2 solid blue-800" bg="blue-800/20" rounded-lg px-4 py-3>
<span class="font-bold text-blue-200">p̂ — measured accuracy</span>
<span class="text-sm opacity-85"> — The fraction right on our n test examples. We can compute it, but it depends on which examples we drew.</span>
</div>
<div v-click border="2 solid white/5" bg="white/5" rounded-lg px-4 py-3>
<span class="font-bold text-amber-300">Same model, different test sets</span>
<span class="text-sm opacity-85"> — Each draw gives a different p̂, scattered around p.</span>
</div>
<div v-click border="2 solid white/5" bg="white/5" rounded-lg px-4 py-3>
<span class="font-bold text-violet-300">The question</span>
<span class="text-sm opacity-85"> — How far is a typical p̂ from p? That spread is the standard error.</span>
</div>
</div>
</div>
<svg role="img" aria-label="Dot plot: eight different test sets give eight different measured accuracies scattered around the true accuracy of 0.90, marked by a dashed line" viewBox="0 0 520 330" class="w-full mt-2">
  <line x1="310" y1="30" x2="310" y2="280" stroke="#2dd4bf" stroke-width="3" stroke-dasharray="7 5"/>
  <text x="310" y="22" fill="#5eead4" text-anchor="middle" style="font-size:15px">true p (unknown)</text>
  <line x1="120" y1="282" x2="500" y2="282" stroke="#64748b" stroke-width="2"/>
  <g fill="#cbd5e1" style="font-size:13px" text-anchor="middle"><text x="183" y="302">0.86</text><text x="310" y="302">0.90</text><text x="437" y="302">0.94</text>
    <text x="310" y="324" fill="#e2e8f0" style="font-size:14px">measured accuracy p̂</text></g>
  <g v-click><circle cx="263" cy="58" r="7.5" fill="#60a5fa"/><text x="108" y="63" text-anchor="end" fill="#94a3b8" style="font-size:13px">test set 1</text><circle cx="358" cy="85" r="7.5" fill="#60a5fa"/><text x="108" y="90" text-anchor="end" fill="#94a3b8" style="font-size:13px">test set 2</text><circle cx="310" cy="112" r="7.5" fill="#60a5fa"/><text x="108" y="117" text-anchor="end" fill="#94a3b8" style="font-size:13px">test set 3</text><circle cx="199" cy="139" r="7.5" fill="#60a5fa"/><text x="108" y="144" text-anchor="end" fill="#94a3b8" style="font-size:13px">test set 4</text><circle cx="389" cy="166" r="7.5" fill="#60a5fa"/><text x="108" y="171" text-anchor="end" fill="#94a3b8" style="font-size:13px">test set 5</text><circle cx="278" cy="193" r="7.5" fill="#60a5fa"/><text x="108" y="198" text-anchor="end" fill="#94a3b8" style="font-size:13px">test set 6</text><circle cx="342" cy="220" r="7.5" fill="#60a5fa"/><text x="108" y="225" text-anchor="end" fill="#94a3b8" style="font-size:13px">test set 7</text><circle cx="421" cy="247" r="7.5" fill="#60a5fa"/><text x="108" y="252" text-anchor="end" fill="#94a3b8" style="font-size:13px">test set 8</text></g>
  <g v-click>
    <path d="M120.0 281 L120.0 277.4 L123.8 276.7 L127.6 276.0 L131.4 275.2 L135.2 274.2 L139.0 273.1 L142.8 271.9 L146.6 270.5 L150.4 268.9 L154.2 267.2 L158.0 265.2 L161.8 263.1 L165.6 260.6 L169.4 258.0 L173.2 255.1 L177.0 251.9 L180.8 248.4 L184.6 244.7 L188.4 240.6 L192.2 236.2 L196.0 231.5 L199.8 226.5 L203.6 221.2 L207.4 215.6 L211.2 209.7 L215.0 203.5 L218.8 197.0 L222.6 190.4 L226.4 183.4 L230.2 176.3 L234.0 169.1 L237.8 161.7 L241.6 154.3 L245.4 146.9 L249.2 139.4 L253.0 132.1 L256.8 124.9 L260.6 117.8 L264.4 111.0 L268.2 104.5 L272.0 98.4 L275.8 92.6 L279.6 87.3 L283.4 82.5 L287.2 78.3 L291.0 74.6 L294.8 71.5 L298.6 69.1 L302.4 67.4 L306.2 66.4 L310.0 66.0 L313.8 66.4 L317.6 67.4 L321.4 69.1 L325.2 71.5 L329.0 74.6 L332.8 78.3 L336.6 82.5 L340.4 87.3 L344.2 92.6 L348.0 98.4 L351.8 104.5 L355.6 111.0 L359.4 117.8 L363.2 124.9 L367.0 132.1 L370.8 139.4 L374.6 146.9 L378.4 154.3 L382.2 161.7 L386.0 169.1 L389.8 176.3 L393.6 183.4 L397.4 190.4 L401.2 197.0 L405.0 203.5 L408.8 209.7 L412.6 215.6 L416.4 221.2 L420.2 226.5 L424.0 231.5 L427.8 236.2 L431.6 240.6 L435.4 244.7 L439.2 248.4 L443.0 251.9 L446.8 255.1 L450.6 258.0 L454.4 260.6 L458.2 263.1 L462.0 265.2 L465.8 267.2 L469.6 268.9 L473.4 270.5 L477.2 271.9 L481.0 273.1 L484.8 274.2 L488.6 275.2 L492.4 276.0 L496.2 276.7 L500.0 277.4 L500.0 281 Z" fill="#fbbf24" fill-opacity=".14"/>
    <path d="M120.0 277.4 L123.8 276.7 L127.6 276.0 L131.4 275.2 L135.2 274.2 L139.0 273.1 L142.8 271.9 L146.6 270.5 L150.4 268.9 L154.2 267.2 L158.0 265.2 L161.8 263.1 L165.6 260.6 L169.4 258.0 L173.2 255.1 L177.0 251.9 L180.8 248.4 L184.6 244.7 L188.4 240.6 L192.2 236.2 L196.0 231.5 L199.8 226.5 L203.6 221.2 L207.4 215.6 L211.2 209.7 L215.0 203.5 L218.8 197.0 L222.6 190.4 L226.4 183.4 L230.2 176.3 L234.0 169.1 L237.8 161.7 L241.6 154.3 L245.4 146.9 L249.2 139.4 L253.0 132.1 L256.8 124.9 L260.6 117.8 L264.4 111.0 L268.2 104.5 L272.0 98.4 L275.8 92.6 L279.6 87.3 L283.4 82.5 L287.2 78.3 L291.0 74.6 L294.8 71.5 L298.6 69.1 L302.4 67.4 L306.2 66.4 L310.0 66.0 L313.8 66.4 L317.6 67.4 L321.4 69.1 L325.2 71.5 L329.0 74.6 L332.8 78.3 L336.6 82.5 L340.4 87.3 L344.2 92.6 L348.0 98.4 L351.8 104.5 L355.6 111.0 L359.4 117.8 L363.2 124.9 L367.0 132.1 L370.8 139.4 L374.6 146.9 L378.4 154.3 L382.2 161.7 L386.0 169.1 L389.8 176.3 L393.6 183.4 L397.4 190.4 L401.2 197.0 L405.0 203.5 L408.8 209.7 L412.6 215.6 L416.4 221.2 L420.2 226.5 L424.0 231.5 L427.8 236.2 L431.6 240.6 L435.4 244.7 L439.2 248.4 L443.0 251.9 L446.8 255.1 L450.6 258.0 L454.4 260.6 L458.2 263.1 L462.0 265.2 L465.8 267.2 L469.6 268.9 L473.4 270.5 L477.2 271.9 L481.0 273.1 L484.8 274.2 L488.6 275.2 L492.4 276.0 L496.2 276.7 L500.0 277.4" fill="none" stroke="#fbbf24" stroke-width="3.5"/>
    <line x1="244" y1="151" x2="244" y2="281" stroke="#fbbf24" stroke-width="1.5" stroke-dasharray="4 4"/>
    <line x1="377" y1="151" x2="377" y2="281" stroke="#fbbf24" stroke-width="1.5" stroke-dasharray="4 4"/>
    <text x="514" y="120" fill="#fbbf24" text-anchor="end" style="font-size:13px">spread of p̂</text>
    <text x="514" y="137" fill="#fbbf24" text-anchor="end" style="font-size:13px">(std. dev. = SE)</text>
  </g>
</svg>
</div>

<!--
Before any formula, be clear about what the symbols mean. p is the model's true accuracy: the probability that it classifies a randomly drawn example correctly, equivalently its accuracy on the entire population of data it will ever meet. It is a fixed number, but we never get to observe it. p-hat is what we do observe: the fraction correct on our particular n test examples.

The dot plot makes the gap concrete. Imagine the same model scored on eight independent test sets of 200 examples each. Each set gives a different p-hat — 86.5%, 89%, 93.5% — because each contains a different random mix of easy and hard cases. They scatter around the dashed line at the true p. The typical size of that scatter is called the standard error, and the next two slides derive it. Once we know it, we can say how far the p-hat from our one test set is likely to be from the true p.
-->

---
glowSeed: 5523
---

# Accuracy Is an Average of Coin Flips

<div class="grid grid-cols-2 gap-8 items-start">
<div>
<div class="space-y-2 mt-2" style="font-size: .8em">
<div v-click border="2 solid white/5" bg="white/5" rounded-lg px-4 py-1>
<span class="font-bold text-teal-300">One example</span><span class="text-xs opacity-85"> — 1 if the prediction is right, 0 if wrong</span>

$$
X_i\in\{0,1\},\qquad \Pr(X_i=1)=p
$$

</div>
<div v-click border="2 solid white/5" bg="white/5" rounded-lg px-4 py-1>
<span class="font-bold text-blue-300">Its mean and variance</span>

$$
E[X_i]=p,\qquad \mathrm{Var}(X_i)=p(1-p)
$$

</div>
<div v-click border="2 solid white/5" bg="white/5" rounded-lg px-4 py-1>
<span class="font-bold text-amber-300">Average of n independent examples</span>

$$
\hat p=\frac1n\sum_i X_i,\qquad \mathrm{Var}(\hat p)=\frac{n\,p(1-p)}{n^2}=\frac{p(1-p)}{n}
$$

</div>
<div v-click border="2 solid teal-800" bg="teal-800/20" rounded-lg px-4 py-1>
<span class="font-bold text-teal-200">Standard error (SE)</span><span class="text-xs opacity-85"> — std. dev. of p̂ across test sets</span>

$$
\mathrm{SE}=\sqrt{\frac{p(1-p)}{n}}
$$

</div>
</div>
</div>
<svg role="img" aria-label="A row of eleven squares, nine green ones labeled 1 for correct predictions and two red ones labeled 0 for mistakes, averaging to the measured accuracy" viewBox="0 0 520 250" class="w-full mt-6">
  <text x="20" y="40" fill="#cbd5e1" style="font-size:15px">each test example is a 0/1 outcome X<tspan style="font-size:11px" dy="3">i</tspan></text>
  <g v-click><rect x="20" y="60" width="36" height="36" rx="6" fill="#2dd4bf" fill-opacity=".85"/><text x="38" y="84" text-anchor="middle" fill="#0f172a" style="font-size:16px;font-weight:700">1</text><rect x="64" y="60" width="36" height="36" rx="6" fill="#2dd4bf" fill-opacity=".85"/><text x="82" y="84" text-anchor="middle" fill="#0f172a" style="font-size:16px;font-weight:700">1</text><rect x="108" y="60" width="36" height="36" rx="6" fill="#2dd4bf" fill-opacity=".85"/><text x="126" y="84" text-anchor="middle" fill="#0f172a" style="font-size:16px;font-weight:700">1</text><rect x="152" y="60" width="36" height="36" rx="6" fill="#2dd4bf" fill-opacity=".85"/><text x="170" y="84" text-anchor="middle" fill="#0f172a" style="font-size:16px;font-weight:700">1</text><rect x="196" y="60" width="36" height="36" rx="6" fill="#f87171" fill-opacity=".85"/><text x="214" y="84" text-anchor="middle" fill="#0f172a" style="font-size:16px;font-weight:700">0</text><rect x="240" y="60" width="36" height="36" rx="6" fill="#2dd4bf" fill-opacity=".85"/><text x="258" y="84" text-anchor="middle" fill="#0f172a" style="font-size:16px;font-weight:700">1</text><rect x="284" y="60" width="36" height="36" rx="6" fill="#2dd4bf" fill-opacity=".85"/><text x="302" y="84" text-anchor="middle" fill="#0f172a" style="font-size:16px;font-weight:700">1</text><rect x="328" y="60" width="36" height="36" rx="6" fill="#2dd4bf" fill-opacity=".85"/><text x="346" y="84" text-anchor="middle" fill="#0f172a" style="font-size:16px;font-weight:700">1</text><rect x="372" y="60" width="36" height="36" rx="6" fill="#f87171" fill-opacity=".85"/><text x="390" y="84" text-anchor="middle" fill="#0f172a" style="font-size:16px;font-weight:700">0</text><rect x="416" y="60" width="36" height="36" rx="6" fill="#2dd4bf" fill-opacity=".85"/><text x="434" y="84" text-anchor="middle" fill="#0f172a" style="font-size:16px;font-weight:700">1</text><rect x="460" y="60" width="36" height="36" rx="6" fill="#2dd4bf" fill-opacity=".85"/><text x="478" y="84" text-anchor="middle" fill="#0f172a" style="font-size:16px;font-weight:700">1</text></g>
  <g v-click>
    <line x1="20" y1="118" x2="496" y2="118" stroke="#64748b" stroke-width="2"/>
    <text x="258" y="152" fill="#e2e8f0" text-anchor="middle" style="font-size:18px">p̂ = (1+1+1+1+0+1+1+1+0+1+1) / 11 = 9/11 ≈ 0.82</text>
    <text x="258" y="190" fill="#94a3b8" text-anchor="middle" style="font-size:14px">more squares → the average moves less when any single one changes</text>
  </g>
</svg>
</div>

<!--
Now derive where the spread comes from. Each test example contributes one outcome: X_i equals 1 if the model got it right and 0 if wrong, and it is right with probability p. That is a Bernoulli coin flip with a biased coin. A Bernoulli variable has mean p and variance p times one-minus-p; you can check the variance directly: the squared deviation is (1−p)² with probability p and p² with probability 1−p, which sums to p(1−p).

Accuracy is just the average of n of these outcomes — the picture shows eleven for illustration. When independent variables are added, their variances add, so the sum has variance n·p(1−p). Dividing by n to form the average divides the variance by n squared, leaving p(1−p)/n. Taking the square root gives the standard error. Notice what the formula says: the spread is largest when p is near one half, where p(1−p) peaks, and it shrinks like one over root n as the test set grows.

Independence is doing real work here; if test rows are duplicates or come in correlated clusters, the true variance is larger than this formula says.
-->

---
glowSeed: 5524
---

# From Standard Error to an Interval

<div class="grid grid-cols-2 gap-8 items-start">
<div>
<div class="space-y-2 mt-2" style="font-size: .9em">
<div v-click border="2 solid white/5" bg="white/5" rounded-lg px-4 py-2>
<span class="font-bold text-teal-300">Central limit theorem</span>
<span class="text-sm opacity-85"> — For large n, p̂ is approximately Normal, centered at p with spread SE.</span>
</div>
<div v-click border="2 solid white/5" bg="white/5" rounded-lg px-4 py-2>
<span class="font-bold text-blue-300">95% rule</span>
<span class="text-sm opacity-85"> — A Normal puts 95% of its mass within 1.96 SE of its center.</span>
</div>
<div v-click border="2 solid white/5" bg="white/5" rounded-lg px-4 py-2>
<span class="font-bold text-amber-300">Plug in p̂ for the unknown p</span>
<span class="text-sm opacity-85"> — So the SE formula uses what we measured.</span>
</div>
<div v-click border="2 solid teal-800" bg="teal-800/20" rounded-lg px-4 py-2 style="font-size: .9em">

$$
\hat p\;\pm\;1.96\sqrt{\frac{\hat p\,(1-\hat p)}{n}}
$$

</div>
</div>
</div>
<svg role="img" aria-label="Bell curve centered at the true accuracy p. The middle region within 1.96 standard errors either side is shaded and labeled 95 percent, and the two outer tails are labeled 2.5 percent each." viewBox="0 0 520 300" class="w-full mt-4">
  <line x1="20" y1="230" x2="500" y2="230" stroke="#64748b" stroke-width="2"/>
  <path v-click d="M138.5 230 L138.5 210.7 L141.5 208.8 L144.6 206.7 L147.6 204.6 L150.6 202.2 L153.7 199.7 L156.7 197.1 L159.7 194.4 L162.8 191.5 L165.8 188.5 L168.9 185.3 L171.9 182.0 L174.9 178.6 L178.0 175.1 L181.0 171.5 L184.1 167.8 L187.1 164.1 L190.1 160.2 L193.2 156.4 L196.2 152.5 L199.2 148.6 L202.3 144.6 L205.3 140.8 L208.4 136.9 L211.4 133.2 L214.4 129.5 L217.5 126.0 L220.5 122.5 L223.5 119.2 L226.6 116.1 L229.6 113.2 L232.7 110.5 L235.7 108.1 L238.7 105.9 L241.8 103.9 L244.8 102.2 L247.8 100.9 L250.9 99.8 L253.9 99.0 L257.0 98.5 L260.0 98.3 L263.0 98.5 L266.1 99.0 L269.1 99.8 L272.2 100.9 L275.2 102.2 L278.2 103.9 L281.3 105.9 L284.3 108.1 L287.3 110.5 L290.4 113.2 L293.4 116.1 L296.5 119.2 L299.5 122.5 L302.5 126.0 L305.6 129.5 L308.6 133.2 L311.6 136.9 L314.7 140.8 L317.7 144.6 L320.8 148.6 L323.8 152.5 L326.8 156.4 L329.9 160.2 L332.9 164.1 L335.9 167.8 L339.0 171.5 L342.0 175.1 L345.1 178.6 L348.1 182.0 L351.1 185.3 L354.2 188.5 L357.2 191.5 L360.3 194.4 L363.3 197.1 L366.3 199.7 L369.4 202.2 L372.4 204.6 L375.4 206.7 L378.5 208.8 L381.5 210.7 L381.5 230 Z" fill="#2dd4bf" fill-opacity=".28"/>
  <path v-click d="M36.8 230 L36.8 229.8 L39.3 229.8 L41.9 229.7 L44.4 229.7 L47.0 229.6 L49.5 229.6 L52.1 229.5 L54.6 229.5 L57.1 229.4 L59.7 229.3 L62.2 229.2 L64.8 229.1 L67.3 228.9 L69.8 228.8 L72.4 228.6 L74.9 228.5 L77.5 228.3 L80.0 228.1 L82.6 227.8 L85.1 227.5 L87.6 227.2 L90.2 226.9 L92.7 226.5 L95.3 226.1 L97.8 225.7 L100.3 225.2 L102.9 224.7 L105.4 224.1 L108.0 223.5 L110.5 222.8 L113.1 222.1 L115.6 221.3 L118.1 220.4 L120.7 219.5 L123.2 218.4 L125.8 217.4 L128.3 216.2 L130.9 215.0 L133.4 213.6 L135.9 212.2 L138.5 210.7 L138.5 230 Z" fill="#f87171" fill-opacity=".7"/>
  <path v-click d="M381.5 230 L381.5 210.7 L384.1 212.2 L386.6 213.6 L389.1 215.0 L391.7 216.2 L394.2 217.4 L396.8 218.4 L399.3 219.5 L401.9 220.4 L404.4 221.3 L406.9 222.1 L409.5 222.8 L412.0 223.5 L414.6 224.1 L417.1 224.7 L419.6 225.2 L422.2 225.7 L424.7 226.1 L427.3 226.5 L429.8 226.9 L432.4 227.2 L434.9 227.5 L437.4 227.8 L440.0 228.1 L442.5 228.3 L445.1 228.5 L447.6 228.6 L450.2 228.8 L452.7 228.9 L455.2 229.1 L457.8 229.2 L460.3 229.3 L462.9 229.4 L465.4 229.5 L467.9 229.5 L470.5 229.6 L473.0 229.6 L475.6 229.7 L478.1 229.7 L480.7 229.8 L483.2 229.8 L483.2 230 Z" fill="#f87171" fill-opacity=".7"/>
  <path d="M36.8 229.8 L42.4 229.7 L48.0 229.6 L53.5 229.5 L59.1 229.3 L64.7 229.1 L70.3 228.8 L75.9 228.4 L81.4 227.9 L87.0 227.3 L92.6 226.6 L98.2 225.6 L103.8 224.5 L109.3 223.1 L114.9 221.5 L120.5 219.5 L126.1 217.2 L131.7 214.5 L137.2 211.5 L142.8 207.9 L148.4 203.9 L154.0 199.5 L159.6 194.6 L165.1 189.2 L170.7 183.3 L176.3 177.1 L181.9 170.5 L187.5 163.6 L193.0 156.5 L198.6 149.4 L204.2 142.2 L209.8 135.2 L215.4 128.4 L220.9 122.0 L226.5 116.2 L232.1 111.0 L237.7 106.6 L243.3 103.1 L248.8 100.5 L254.4 98.9 L260.0 98.3 L265.6 98.9 L271.2 100.5 L276.7 103.1 L282.3 106.6 L287.9 111.0 L293.5 116.2 L299.1 122.0 L304.6 128.4 L310.2 135.2 L315.8 142.2 L321.4 149.4 L327.0 156.5 L332.5 163.6 L338.1 170.5 L343.7 177.1 L349.3 183.3 L354.9 189.2 L360.4 194.6 L366.0 199.5 L371.6 203.9 L377.2 207.9 L382.8 211.5 L388.3 214.5 L393.9 217.2 L399.5 219.5 L405.1 221.5 L410.7 223.1 L416.2 224.5 L421.8 225.6 L427.4 226.6 L433.0 227.3 L438.6 227.9 L444.1 228.4 L449.7 228.8 L455.3 229.1 L460.9 229.3 L466.5 229.5 L472.0 229.6 L477.6 229.7 L483.2 229.8" fill="none" stroke="#2dd4bf" stroke-width="3.5"/>
  <line x1="260" y1="64" x2="260" y2="236" stroke="#94a3b8" stroke-width="2" stroke-dasharray="5 5"/>
  <g fill="#cbd5e1" style="font-size:15px" text-anchor="middle">
    <text x="260" y="256">p</text>
    <text x="138" y="256" fill="#fbbf24">p − 1.96·SE</text>
    <text x="382" y="256" fill="#fbbf24">p + 1.96·SE</text>
    <text x="260" y="42" fill="#5eead4">distribution of p̂ across test sets</text>
  </g>
  <g v-click style="font-size:18px;font-weight:700" text-anchor="middle">
    <text x="260" y="170" fill="#e2e8f0">95%</text>
    <text x="86" y="200" fill="#fca5a5" style="font-size:13px">2.5%</text>
    <text x="434" y="200" fill="#fca5a5" style="font-size:13px">2.5%</text>
  </g>
</svg>
</div>

<!--
We now know the spread of p-hat, but a confidence interval needs its shape too. By the central limit theorem, an average of many independent variables is approximately Normally distributed, so across hypothetical test sets p-hat is approximately Normal with mean p and standard deviation equal to the SE we just derived. That is the bell curve.

A Normal distribution has a familiar property: about 95% of its mass lies within 1.96 standard deviations of the center, leaving 2.5% in each tail. So for 95% of test sets, p-hat lands within 1.96 SE of the true p. The same statement read backwards says the true p lies within 1.96 SE of the p-hat we got, which is the interval. The last wrinkle is that SE contains p, which we do not know, so we substitute p-hat. That substitution is harmless when n is large.

Be careful with the interpretation: the 95% describes the procedure — 95% of intervals built this way cover the true p — not the probability that p lies in the one interval you computed.
-->

---
glowSeed: 5525
---

# What the Interval Tells You

<div class="grid grid-cols-2 gap-8 items-start">
<div>
<div class="space-y-3 mt-2">
<div v-click border="2 solid teal-800" bg="teal-800/20" rounded-lg px-4 py-2 style="font-size: .85em">

$$
\hat p\;\pm\;1.96\sqrt{\frac{\hat p\,(1-\hat p)}{n}}
$$

</div>
<div v-click border="2 solid white/5" bg="white/5" rounded-lg px-4 py-3>
<span class="font-bold text-blue-300">√n scaling</span>
<span class="text-sm opacity-85"> — Four times the test data halves the interval; precision is expensive.</span>
</div>
<div v-click border="2 solid white/5" bg="white/5" rounded-lg px-4 py-3>
<span class="font-bold text-amber-300">Revisit 91% vs. 89%</span>
<span class="text-sm opacity-85"> — At n = 200 each score carries about ±4 points, so the intervals overlap heavily.</span>
</div>
</div>
</div>
<div style="height: 360px">
<CiVsN />
</div>
</div>

<!--
The previous three slides derived the interval; this one shows what it implies. Recall that multiplying the standard error by 1.96 gives an approximate 95% interval; this is the normal approximation, which is fine when n·p and n·(1−p) are both comfortably above about ten, and for small n or extreme accuracies you should prefer a Wilson or exact Clopper–Pearson interval.

Read the chart: the curve shows the half-width of that interval for a model at 90% accuracy. At n = 100 it is about ±6 points, at n = 1,000 about ±2, and at n = 10,000 under ±1. The square-root scaling is the key message: halving the uncertainty costs four times the labeled data. Now return to the opening example. A 91% and an 89% model evaluated on 200 examples each have intervals of roughly ±4 points, so the two intervals overlap almost completely.

One caution to plant for later slides: overlapping intervals are only a rough guide. Both models were scored on the same test examples, so their errors are correlated, and a paired test such as McNemar's can detect a difference that two separate intervals would hide.
-->

---
glowSeed: 5526
---

# Which Model Is Better?

<div class="grid grid-cols-2 gap-8 items-start">
<div>
<div class="space-y-3 mt-2" style="font-size: .92em">
<div v-click="1" border="2 solid white/5" bg="white/5" rounded-lg px-4 py-3>
<span class="font-bold text-amber-300">The setup</span>
<span class="text-sm opacity-85"> — Model A scores 89%, Model B scores 91%, each on n = 200 test examples. Is B really better?</span>
</div>
<div v-click="2" border="2 solid white/5" bg="white/5" rounded-lg px-4 py-3>
<span class="font-bold text-blue-300">Standard errors</span>
<span class="text-sm opacity-85"> — SE<sub>A</sub> = √(0.89·0.11 / 200) ≈ 2.2 pts, SE<sub>B</sub> = √(0.91·0.09 / 200) ≈ 2.0 pts.</span>
</div>
<div v-click="3" border="2 solid white/5" bg="white/5" rounded-lg px-4 py-3>
<span class="font-bold text-teal-300">95% intervals (± 1.96 SE)</span>
<span class="text-sm opacity-85"> — A: 84.7–93.3%. B: 87.0–95.0%. They overlap from 87.0% to 93.3%.</span>
</div>
<div v-click="4" border="2 solid amber-800" bg="amber-800/20" rounded-lg px-4 py-3>
<span class="font-bold text-amber-300">Takeaway</span>
<span class="text-sm opacity-85"> — On a fresh test set the order could flip: A′ 91.5% vs B′ 89.5%. If the models were really this far apart, that happens about 1 time in 4.</span>
</div>
</div>
</div>
<svg role="img" aria-label="Sampling distributions of Model A at 89 percent and Model B at 91 percent accuracy. Both bell curves overlap heavily, and the 95 percent intervals below overlap from 87 to 93 percent." viewBox="0 0 540 330" class="w-full mt-2">
  <line x1="40" y1="190" x2="500" y2="190" stroke="#64748b" stroke-width="2"/>
  <g fill="#cbd5e1" style="font-size:13px" text-anchor="middle"><text x="40" y="209">80%</text><text x="155" y="209">85%</text><text x="270" y="209">90%</text><text x="385" y="209">95%</text><text x="500" y="209">100%</text>
    <text x="270" y="326" fill="#e2e8f0" style="font-size:14px">accuracy</text></g>
  <g v-click="1">
    <line x1="247" y1="40" x2="247" y2="190" stroke="#60a5fa" stroke-width="2" stroke-dasharray="5 5"/>
    <line x1="293" y1="40" x2="293" y2="190" stroke="#2dd4bf" stroke-width="2" stroke-dasharray="5 5"/>
    <text x="241" y="34" fill="#93c5fd" text-anchor="end" style="font-size:15px;font-weight:700">A: 89%</text>
    <text x="299" y="34" fill="#5eead4" text-anchor="start" style="font-size:15px;font-weight:700">B: 91%</text>
  </g>
  <g v-click="2">
    <path d="M40.0 190 L40.0 190.0 L43.8 190.0 L47.7 189.9 L51.5 189.9 L55.3 189.9 L59.2 189.9 L63.0 189.8 L66.8 189.8 L70.7 189.7 L74.5 189.6 L78.3 189.5 L82.2 189.3 L86.0 189.1 L89.8 188.9 L93.7 188.6 L97.5 188.3 L101.3 187.9 L105.2 187.4 L109.0 186.8 L112.8 186.0 L116.7 185.2 L120.5 184.2 L124.3 183.0 L128.2 181.6 L132.0 180.0 L135.8 178.2 L139.7 176.2 L143.5 173.8 L147.3 171.2 L151.2 168.3 L155.0 165.0 L158.8 161.5 L162.7 157.6 L166.5 153.4 L170.3 148.8 L174.2 144.0 L178.0 138.9 L181.8 133.6 L185.7 128.1 L189.5 122.4 L193.3 116.6 L197.2 110.7 L201.0 104.9 L204.8 99.2 L208.7 93.6 L212.5 88.2 L216.3 83.2 L220.2 78.6 L224.0 74.4 L227.8 70.7 L231.7 67.6 L235.5 65.2 L239.3 63.4 L243.2 62.3 L247.0 62.0 L250.8 62.3 L254.7 63.4 L258.5 65.2 L262.3 67.6 L266.2 70.7 L270.0 74.4 L273.8 78.6 L277.7 83.2 L281.5 88.2 L285.3 93.6 L289.2 99.2 L293.0 104.9 L296.8 110.7 L300.7 116.6 L304.5 122.4 L308.3 128.1 L312.2 133.6 L316.0 138.9 L319.8 144.0 L323.7 148.8 L327.5 153.4 L331.3 157.6 L335.2 161.5 L339.0 165.0 L342.8 168.3 L346.7 171.2 L350.5 173.8 L354.3 176.2 L358.2 178.2 L362.0 180.0 L365.8 181.6 L369.7 183.0 L373.5 184.2 L377.3 185.2 L381.2 186.0 L385.0 186.8 L388.8 187.4 L392.7 187.9 L396.5 188.3 L400.3 188.6 L404.2 188.9 L408.0 189.1 L411.8 189.3 L415.7 189.5 L419.5 189.6 L423.3 189.7 L427.2 189.8 L431.0 189.8 L434.8 189.9 L438.7 189.9 L442.5 189.9 L446.3 189.9 L450.2 190.0 L454.0 190.0 L457.8 190.0 L461.7 190.0 L465.5 190.0 L469.3 190.0 L473.2 190.0 L477.0 190.0 L480.8 190.0 L484.7 190.0 L488.5 190.0 L492.3 190.0 L496.2 190.0 L500.0 190.0 L500.0 190 Z" fill="#60a5fa" fill-opacity=".18"/><path d="M40.0 190.0 L43.8 190.0 L47.7 189.9 L51.5 189.9 L55.3 189.9 L59.2 189.9 L63.0 189.8 L66.8 189.8 L70.7 189.7 L74.5 189.6 L78.3 189.5 L82.2 189.3 L86.0 189.1 L89.8 188.9 L93.7 188.6 L97.5 188.3 L101.3 187.9 L105.2 187.4 L109.0 186.8 L112.8 186.0 L116.7 185.2 L120.5 184.2 L124.3 183.0 L128.2 181.6 L132.0 180.0 L135.8 178.2 L139.7 176.2 L143.5 173.8 L147.3 171.2 L151.2 168.3 L155.0 165.0 L158.8 161.5 L162.7 157.6 L166.5 153.4 L170.3 148.8 L174.2 144.0 L178.0 138.9 L181.8 133.6 L185.7 128.1 L189.5 122.4 L193.3 116.6 L197.2 110.7 L201.0 104.9 L204.8 99.2 L208.7 93.6 L212.5 88.2 L216.3 83.2 L220.2 78.6 L224.0 74.4 L227.8 70.7 L231.7 67.6 L235.5 65.2 L239.3 63.4 L243.2 62.3 L247.0 62.0 L250.8 62.3 L254.7 63.4 L258.5 65.2 L262.3 67.6 L266.2 70.7 L270.0 74.4 L273.8 78.6 L277.7 83.2 L281.5 88.2 L285.3 93.6 L289.2 99.2 L293.0 104.9 L296.8 110.7 L300.7 116.6 L304.5 122.4 L308.3 128.1 L312.2 133.6 L316.0 138.9 L319.8 144.0 L323.7 148.8 L327.5 153.4 L331.3 157.6 L335.2 161.5 L339.0 165.0 L342.8 168.3 L346.7 171.2 L350.5 173.8 L354.3 176.2 L358.2 178.2 L362.0 180.0 L365.8 181.6 L369.7 183.0 L373.5 184.2 L377.3 185.2 L381.2 186.0 L385.0 186.8 L388.8 187.4 L392.7 187.9 L396.5 188.3 L400.3 188.6 L404.2 188.9 L408.0 189.1 L411.8 189.3 L415.7 189.5 L419.5 189.6 L423.3 189.7 L427.2 189.8 L431.0 189.8 L434.8 189.9 L438.7 189.9 L442.5 189.9 L446.3 189.9 L450.2 190.0 L454.0 190.0 L457.8 190.0 L461.7 190.0 L465.5 190.0 L469.3 190.0 L473.2 190.0 L477.0 190.0 L480.8 190.0 L484.7 190.0 L488.5 190.0 L492.3 190.0 L496.2 190.0 L500.0 190.0" fill="none" stroke="#60a5fa" stroke-width="3"/>
    <path d="M40.0 190 L40.0 190.0 L43.8 190.0 L47.7 190.0 L51.5 190.0 L55.3 190.0 L59.2 190.0 L63.0 190.0 L66.8 190.0 L70.7 190.0 L74.5 190.0 L78.3 190.0 L82.2 190.0 L86.0 190.0 L89.8 190.0 L93.7 190.0 L97.5 190.0 L101.3 190.0 L105.2 190.0 L109.0 189.9 L112.8 189.9 L116.7 189.9 L120.5 189.9 L124.3 189.8 L128.2 189.7 L132.0 189.6 L135.8 189.5 L139.7 189.4 L143.5 189.2 L147.3 189.0 L151.2 188.7 L155.0 188.3 L158.8 187.8 L162.7 187.2 L166.5 186.5 L170.3 185.7 L174.2 184.6 L178.0 183.4 L181.8 181.9 L185.7 180.2 L189.5 178.2 L193.3 175.9 L197.2 173.2 L201.0 170.2 L204.8 166.7 L208.7 162.9 L212.5 158.6 L216.3 153.9 L220.2 148.8 L224.0 143.3 L227.8 137.5 L231.7 131.2 L235.5 124.7 L239.3 118.0 L243.2 111.1 L247.0 104.1 L250.8 97.1 L254.7 90.3 L258.5 83.6 L262.3 77.3 L266.2 71.4 L270.0 66.1 L273.8 61.4 L277.7 57.4 L281.5 54.2 L285.3 51.9 L289.2 50.5 L293.0 50.0 L296.8 50.5 L300.7 51.9 L304.5 54.2 L308.3 57.4 L312.2 61.4 L316.0 66.1 L319.8 71.4 L323.7 77.3 L327.5 83.6 L331.3 90.3 L335.2 97.1 L339.0 104.1 L342.8 111.1 L346.7 118.0 L350.5 124.7 L354.3 131.2 L358.2 137.5 L362.0 143.3 L365.8 148.8 L369.7 153.9 L373.5 158.6 L377.3 162.9 L381.2 166.7 L385.0 170.2 L388.8 173.2 L392.7 175.9 L396.5 178.2 L400.3 180.2 L404.2 181.9 L408.0 183.4 L411.8 184.6 L415.7 185.7 L419.5 186.5 L423.3 187.2 L427.2 187.8 L431.0 188.3 L434.8 188.7 L438.7 189.0 L442.5 189.2 L446.3 189.4 L450.2 189.5 L454.0 189.6 L457.8 189.7 L461.7 189.8 L465.5 189.9 L469.3 189.9 L473.2 189.9 L477.0 189.9 L480.8 190.0 L484.7 190.0 L488.5 190.0 L492.3 190.0 L496.2 190.0 L500.0 190.0 L500.0 190 Z" fill="#2dd4bf" fill-opacity=".18"/><path d="M40.0 190.0 L43.8 190.0 L47.7 190.0 L51.5 190.0 L55.3 190.0 L59.2 190.0 L63.0 190.0 L66.8 190.0 L70.7 190.0 L74.5 190.0 L78.3 190.0 L82.2 190.0 L86.0 190.0 L89.8 190.0 L93.7 190.0 L97.5 190.0 L101.3 190.0 L105.2 190.0 L109.0 189.9 L112.8 189.9 L116.7 189.9 L120.5 189.9 L124.3 189.8 L128.2 189.7 L132.0 189.6 L135.8 189.5 L139.7 189.4 L143.5 189.2 L147.3 189.0 L151.2 188.7 L155.0 188.3 L158.8 187.8 L162.7 187.2 L166.5 186.5 L170.3 185.7 L174.2 184.6 L178.0 183.4 L181.8 181.9 L185.7 180.2 L189.5 178.2 L193.3 175.9 L197.2 173.2 L201.0 170.2 L204.8 166.7 L208.7 162.9 L212.5 158.6 L216.3 153.9 L220.2 148.8 L224.0 143.3 L227.8 137.5 L231.7 131.2 L235.5 124.7 L239.3 118.0 L243.2 111.1 L247.0 104.1 L250.8 97.1 L254.7 90.3 L258.5 83.6 L262.3 77.3 L266.2 71.4 L270.0 66.1 L273.8 61.4 L277.7 57.4 L281.5 54.2 L285.3 51.9 L289.2 50.5 L293.0 50.0 L296.8 50.5 L300.7 51.9 L304.5 54.2 L308.3 57.4 L312.2 61.4 L316.0 66.1 L319.8 71.4 L323.7 77.3 L327.5 83.6 L331.3 90.3 L335.2 97.1 L339.0 104.1 L342.8 111.1 L346.7 118.0 L350.5 124.7 L354.3 131.2 L358.2 137.5 L362.0 143.3 L365.8 148.8 L369.7 153.9 L373.5 158.6 L377.3 162.9 L381.2 166.7 L385.0 170.2 L388.8 173.2 L392.7 175.9 L396.5 178.2 L400.3 180.2 L404.2 181.9 L408.0 183.4 L411.8 184.6 L415.7 185.7 L419.5 186.5 L423.3 187.2 L427.2 187.8 L431.0 188.3 L434.8 188.7 L438.7 189.0 L442.5 189.2 L446.3 189.4 L450.2 189.5 L454.0 189.6 L457.8 189.7 L461.7 189.8 L465.5 189.9 L469.3 189.9 L473.2 189.9 L477.0 189.9 L480.8 190.0 L484.7 190.0 L488.5 190.0 L492.3 190.0 L496.2 190.0 L500.0 190.0" fill="none" stroke="#2dd4bf" stroke-width="3"/>
  </g>
  <g v-click="3">
    <rect x="202" y="238" width="145" height="62" fill="#fbbf24" fill-opacity=".16"/>
    <line x1="147" y1="258" x2="347" y2="258" stroke="#60a5fa" stroke-width="5" stroke-linecap="round"/>
    <line x1="202" y1="282" x2="384" y2="282" stroke="#2dd4bf" stroke-width="5" stroke-linecap="round"/>
    <text x="139" y="263" fill="#93c5fd" text-anchor="end" style="font-size:14px;font-weight:700">A</text>
    <text x="194" y="287" fill="#5eead4" text-anchor="end" style="font-size:14px;font-weight:700">B</text>
    <text x="357" y="252" fill="#fbbf24" text-anchor="start" style="font-size:13px">overlap</text>
  </g>
  <g v-click="4">
    <circle cx="304" cy="230" r="0" fill="none"/>
    <circle cx="304" cy="190" r="8" fill="none" stroke="#60a5fa" stroke-width="3"/>
    <circle cx="258" cy="190" r="8" fill="none" stroke="#2dd4bf" stroke-width="3"/>
    <line x1="253" y1="180" x2="166" y2="130" stroke="#2dd4bf" stroke-width="1.5"/>
    <line x1="310" y1="180" x2="396" y2="130" stroke="#60a5fa" stroke-width="1.5"/>
    <text x="166" y="122" fill="#5eead4" text-anchor="middle" style="font-size:13px;font-weight:700">B′ 89.5%</text>
    <text x="396" y="122" fill="#93c5fd" text-anchor="middle" style="font-size:13px;font-weight:700">A′ 91.5%</text>
  </g>
</svg>
</div>

<!--
Start with a concrete question before any theory. Model A scores 89% and Model B scores 91%, each on 200 test examples. Most people would say B is better. Let's check how much those two numbers can be trusted, using the standard error from the last few slides.

Model A: the standard error is the square root of 0.89 times 0.11 over 200, about 2.2 points. Model B: the square root of 0.91 times 0.09 over 200, about 2.0 points. The bell curves show the spread of the accuracy we would see across different test sets of this size, centered on each measured score. They overlap heavily.

The 95% intervals make the same point: A runs from roughly 84.7% to 93.3%, B from 87.0% to 95.0%. Everything from 87% to 93.3% is plausible for both models, so the data cannot separate them with any confidence.

The takeaway is about reproducibility. Draw a new test set and each score will move by a couple of points, so we could easily see A at 91.5% and B at 89.5%, with the ranking reversed. If the true accuracies really were 89% and 91% and the two test sets were independent, the chance of that reversal is about 25%, since the difference of the two scores has a standard deviation of roughly 3 points against an observed gap of 2. In practice both models are scored on the same examples, which makes their errors correlated and the comparison sharper; that is exactly what the paired tests later in the deck exploit. But the question this raises is general: how big does a gap have to be before we believe it? The next slide introduces the formal framework for answering that.
-->

---
glowSeed: 552
---

# The Null-Hypothesis Frame

<div class="grid grid-cols-2 gap-8 items-start">
<div>
<div class="space-y-3 mt-4">
<div v-click border="2 solid white/5" bg="white/5" rounded-lg px-4 py-3>
<span class="font-bold text-teal-300">H₀</span>
<span class="text-sm opacity-85"> — The models have equal true performance; the observed gap Δ is noise.</span>
</div>
<div v-click border="2 solid white/5" bg="white/5" rounded-lg px-4 py-3>
<span class="font-bold text-blue-300">p-value</span>
<span class="text-sm opacity-85"> — Probability of a gap at least this large, if H₀ were exactly true.</span>
</div>
<div v-click border="2 solid white/5" bg="white/5" rounded-lg px-4 py-3>
<span class="font-bold text-amber-300">Not what it means</span>
<span class="text-sm opacity-85"> — p = P(gap this large | H₀), not P(H₀ | gap). The reverse is a Bayesian posterior and needs a prior.</span>
</div>
</div>
</div>
<div>
<svg role="img" aria-label="Bell-shaped null distribution of the performance gap centered at zero, with shaded tails beyond the observed gap marking the p-value" viewBox="0 0 500 310" class="w-full max-w-xl mx-auto mt-6">
  <line x1="55" y1="260" x2="470" y2="260" stroke="#64748b" stroke-width="2"/>
  <path d="M60 255 C140 255 195 60 262 60 C330 60 385 255 465 255" fill="none" stroke="#2dd4bf" stroke-width="4"/>
  <line x1="150" y1="255" x2="150" y2="70" stroke="#f59e0b" stroke-width="2" stroke-dasharray="5 5"/>
  <line x1="378" y1="255" x2="378" y2="70" stroke="#f59e0b" stroke-width="2" stroke-dasharray="5 5"/>
  <line x1="262" y1="260" x2="262" y2="245" stroke="#94a3b8" stroke-width="2"/>
  <g fill="#cbd5e1" style="font-size: 16px" text-anchor="middle">
    <text x="262" y="280">0</text>
    <text x="150" y="280" fill="#fbbf24">−Δ<tspan style="font-size: 11px">obs</tspan></text>
    <text x="378" y="280" fill="#fbbf24">+Δ<tspan style="font-size: 11px">obs</tspan></text>
  </g>
  <g style="font-size: 16px">
    <text x="262" y="42" fill="#5eead4" text-anchor="middle">sampling distribution of the gap under H₀</text>
    <text x="105" y="235" fill="#fbbf24" text-anchor="middle">tail</text>
    <text x="420" y="235" fill="#fbbf24" text-anchor="middle">tail</text>
  </g>
</svg>

</div>
</div>

<!--
Return to the 89% vs 91% example: the intervals overlapped, so how do we decide whether the gap is real? Formalize "is the gap real" with the standard hypothesis-testing recipe. The null hypothesis H₀ states that the two models have equal true performance, so any gap you observed in one experiment is attributable entirely to sampling noise — this is the curve on the slide, the distribution of gaps you would see across many hypothetical resamples if H₀ were exactly correct; it is centered at zero because under H₀ the expected gap is zero. You then compute a p-value: the probability, under that null distribution, of seeing a gap at least as extreme as the one you actually observed, Δ_obs — visualized here as the combined area in the two shaded tails beyond ±Δ_obs. A small p-value means your observed gap would be surprising if the models were truly equal, which is evidence (not proof) against H₀.

Two misconceptions to name explicitly. First, the p-value is not "the probability that H₀ is true" — it is a statement about how surprising the data is, assuming H₀, not a statement about how likely H₀ is given the data; those are different conditional probabilities and confusing them is one of the most common statistical errors. Second, the conventional threshold of 0.05 is exactly that — a convention, not a law of nature or a sharp cliff between "true" and "false." A p-value of 0.04 and a p-value of 0.06 reflect nearly identical evidence; treat significance as a continuum and always report the effect size (the actual magnitude of Δ) alongside the p-value, not the p-value in isolation. The next slide applies this frame to the specific case of two classifiers evaluated on the same test set.
-->

---
glowSeed: 5527
---

# How Wide Is the Gap's Noise?

<div class="grid grid-cols-2 gap-8 items-start">
<div>
<div class="space-y-2 mt-2" style="font-size: .8em">
<div v-click="1" border="2 solid white/5" bg="white/5" rounded-lg px-4 py-2>
<span class="font-bold text-blue-300">Each score is noisy</span><span class="text-xs opacity-85"> — the 89% vs. 91% example, n = 200: SE<sub>A</sub> ≈ 2.2 pts, SE<sub>B</sub> ≈ 2.0 pts</span>
</div>
<div v-click="2" border="2 solid white/5" bg="white/5" rounded-lg px-4 py-1>
<span class="font-bold text-amber-300">Variances of independent scores add</span>

$$
\mathrm{Var}(\hat p_B-\hat p_A)=\mathrm{SE}_A^2+\mathrm{SE}_B^2
$$

</div>
<div v-click="3" border="2 solid teal-800" bg="teal-800/20" rounded-lg px-4 py-1>
<span class="font-bold text-teal-200">So the gap has its own standard error</span>

$$
\mathrm{SE}_{\text{gap}}=\sqrt{\mathrm{SE}_A^2+\mathrm{SE}_B^2}=\sqrt{2.2^2+2.0^2}\approx 3.0\text{ pts}
$$

</div>
<div v-click="4" border="2 solid white/5" bg="white/5" rounded-lg px-4 py-2>
<span class="font-bold text-violet-300">From width to probability</span><span class="text-xs opacity-85"> — If the models were truly equal, how often would a test set show a gap of 2 points or more, in either direction? That is the shaded area: about 50% of the time (p ≈ 0.50). A 2-point gap is only 0.67 SE from zero, so it is not surprising.</span>
</div>
</div>
</div>
<svg role="img" aria-label="Bell curve labeled H0 centered at a gap of zero. Its width, one standard error of the gap, is about 3 points. The observed gap of 2 points sits well inside the curve, and the shaded tails beyond plus or minus 2 points hold about half of the area, so p is about 0.50." viewBox="0 0 540 300" class="w-full mt-2">
  <line x1="30" y1="200" x2="510" y2="200" stroke="#64748b" stroke-width="2"/>
  <g fill="#cbd5e1" style="font-size:13px" text-anchor="middle"><text x="63" y="220">−9</text><text x="132" y="220">−6</text><text x="201" y="220">−3</text><text x="270" y="220">0</text><text x="339" y="220">+3</text><text x="408" y="220">+6</text><text x="477" y="220">+9</text><text x="63" y="238" fill="#fbbf24">−3 SE</text><text x="132" y="238" fill="#fbbf24">−2 SE</text><text x="201" y="238" fill="#fbbf24">−1 SE</text><text x="270" y="238" fill="#fbbf24">0</text><text x="339" y="238" fill="#fbbf24">+1 SE</text><text x="408" y="238" fill="#fbbf24">+2 SE</text><text x="477" y="238" fill="#fbbf24">+3 SE</text>
    <text x="270" y="290" fill="#e2e8f0" style="font-size:15px">gap size (accuracy points, B − A)</text></g>
  <g v-click="3">
    <path d="M40.0 199.4 L42.9 199.3 L45.8 199.2 L48.6 199.1 L51.5 199.0 L54.4 198.9 L57.2 198.7 L60.1 198.5 L63.0 198.3 L65.9 198.1 L68.8 197.9 L71.6 197.6 L74.5 197.3 L77.4 197.0 L80.2 196.6 L83.1 196.2 L86.0 195.7 L88.9 195.2 L91.8 194.7 L94.6 194.1 L97.5 193.4 L100.4 192.7 L103.2 191.9 L106.1 191.1 L109.0 190.1 L111.9 189.1 L114.8 188.1 L117.6 186.9 L120.5 185.7 L123.4 184.3 L126.2 182.9 L129.1 181.3 L132.0 179.7 L134.9 178.0 L137.8 176.1 L140.6 174.1 L143.5 172.1 L146.4 169.9 L149.2 167.6 L152.1 165.1 L155.0 162.6 L157.9 159.9 L160.8 157.2 L163.6 154.3 L166.5 151.3 L169.4 148.2 L172.2 145.0 L175.1 141.7 L178.0 138.3 L180.9 134.9 L183.8 131.3 L186.6 127.7 L189.5 124.0 L192.4 120.3 L195.2 116.6 L198.1 112.8 L201.0 109.0 L203.9 105.2 L206.8 101.5 L209.6 97.7 L212.5 94.0 L215.4 90.4 L218.2 86.8 L221.1 83.3 L224.0 79.9 L226.9 76.6 L229.8 73.5 L232.6 70.5 L235.5 67.6 L238.4 65.0 L241.2 62.5 L244.1 60.2 L247.0 58.1 L249.9 56.2 L252.8 54.6 L255.6 53.2 L258.5 52.1 L261.4 51.2 L264.2 50.5 L267.1 50.1 L270.0 50.0 L272.9 50.1 L275.8 50.5 L278.6 51.2 L281.5 52.1 L284.4 53.2 L287.2 54.6 L290.1 56.2 L293.0 58.1 L295.9 60.2 L298.8 62.5 L301.6 65.0 L304.5 67.6 L307.4 70.5 L310.2 73.5 L313.1 76.6 L316.0 79.9 L318.9 83.3 L321.8 86.8 L324.6 90.4 L327.5 94.0 L330.4 97.7 L333.2 101.5 L336.1 105.2 L339.0 109.0 L341.9 112.8 L344.8 116.6 L347.6 120.3 L350.5 124.0 L353.4 127.7 L356.2 131.3 L359.1 134.9 L362.0 138.3 L364.9 141.7 L367.8 145.0 L370.6 148.2 L373.5 151.3 L376.4 154.3 L379.2 157.2 L382.1 159.9 L385.0 162.6 L387.9 165.1 L390.8 167.6 L393.6 169.9 L396.5 172.1 L399.4 174.1 L402.2 176.1 L405.1 178.0 L408.0 179.7 L410.9 181.3 L413.8 182.9 L416.6 184.3 L419.5 185.7 L422.4 186.9 L425.2 188.1 L428.1 189.1 L431.0 190.1 L433.9 191.1 L436.8 191.9 L439.6 192.7 L442.5 193.4 L445.4 194.1 L448.2 194.7 L451.1 195.2 L454.0 195.7 L456.9 196.2 L459.8 196.6 L462.6 197.0 L465.5 197.3 L468.4 197.6 L471.2 197.9 L474.1 198.1 L477.0 198.3 L479.9 198.5 L482.8 198.7 L485.6 198.9 L488.5 199.0 L491.4 199.1 L494.2 199.2 L497.1 199.3 L500.0 199.4" fill="none" stroke="#2dd4bf" stroke-width="3.5"/>
    <text x="120.5" y="62" fill="#5eead4" text-anchor="middle" style="font-size:17px;font-weight:700">H₀: no real gap</text>
    <line x1="201" y1="109" x2="339" y2="109" stroke="#fbbf24" stroke-width="2.5"/>
    <line x1="201" y1="103" x2="201" y2="115" stroke="#fbbf24" stroke-width="2.5"/>
    <line x1="339" y1="103" x2="339" y2="115" stroke="#fbbf24" stroke-width="2.5"/>
    <text x="191" y="96" fill="#fbbf24" text-anchor="end" style="font-size:13px">width = SE(gap)</text>
    <text x="191" y="112" fill="#fbbf24" text-anchor="end" style="font-size:13px">≈ 3.0 pts</text>
  </g>
  <g v-click="4">
    <path d="M316.0 200 L316.0 79.9 L319.7 84.2 L323.4 88.8 L327.0 93.4 L330.7 98.2 L334.4 103.0 L338.1 107.8 L341.8 112.7 L345.4 117.5 L349.1 122.3 L352.8 127.0 L356.5 131.6 L360.2 136.1 L363.8 140.5 L367.5 144.7 L371.2 148.8 L374.9 152.8 L378.6 156.5 L382.2 160.1 L385.9 163.4 L389.6 166.6 L393.3 169.6 L397.0 172.4 L400.6 175.0 L404.3 177.4 L408.0 179.7 L411.7 181.8 L415.4 183.7 L419.0 185.4 L422.7 187.0 L426.4 188.5 L430.1 189.8 L433.8 191.0 L437.4 192.1 L441.1 193.1 L444.8 193.9 L448.5 194.7 L452.2 195.4 L455.8 196.0 L459.5 196.5 L463.2 197.0 L466.9 197.4 L470.6 197.8 L474.2 198.1 L477.9 198.4 L481.6 198.6 L485.3 198.8 L489.0 199.0 L492.6 199.2 L496.3 199.3 L500.0 199.4 L500.0 200 Z" fill="#fbbf24" fill-opacity=".35"/><path d="M40.0 200 L40.0 199.4 L43.7 199.3 L47.4 199.2 L51.0 199.0 L54.7 198.8 L58.4 198.6 L62.1 198.4 L65.8 198.1 L69.4 197.8 L73.1 197.4 L76.8 197.0 L80.5 196.5 L84.2 196.0 L87.8 195.4 L91.5 194.7 L95.2 193.9 L98.9 193.1 L102.6 192.1 L106.2 191.0 L109.9 189.8 L113.6 188.5 L117.3 187.0 L121.0 185.4 L124.6 183.7 L128.3 181.8 L132.0 179.7 L135.7 177.4 L139.4 175.0 L143.0 172.4 L146.7 169.6 L150.4 166.6 L154.1 163.4 L157.8 160.1 L161.4 156.5 L165.1 152.8 L168.8 148.8 L172.5 144.7 L176.2 140.5 L179.8 136.1 L183.5 131.6 L187.2 127.0 L190.9 122.3 L194.6 117.5 L198.2 112.7 L201.9 107.8 L205.6 103.0 L209.3 98.2 L213.0 93.4 L216.6 88.8 L220.3 84.2 L224.0 79.9 L224.0 200 Z" fill="#fbbf24" fill-opacity=".35"/>
    <path d="M40.0 199.4 L42.9 199.3 L45.8 199.2 L48.6 199.1 L51.5 199.0 L54.4 198.9 L57.2 198.7 L60.1 198.5 L63.0 198.3 L65.9 198.1 L68.8 197.9 L71.6 197.6 L74.5 197.3 L77.4 197.0 L80.2 196.6 L83.1 196.2 L86.0 195.7 L88.9 195.2 L91.8 194.7 L94.6 194.1 L97.5 193.4 L100.4 192.7 L103.2 191.9 L106.1 191.1 L109.0 190.1 L111.9 189.1 L114.8 188.1 L117.6 186.9 L120.5 185.7 L123.4 184.3 L126.2 182.9 L129.1 181.3 L132.0 179.7 L134.9 178.0 L137.8 176.1 L140.6 174.1 L143.5 172.1 L146.4 169.9 L149.2 167.6 L152.1 165.1 L155.0 162.6 L157.9 159.9 L160.8 157.2 L163.6 154.3 L166.5 151.3 L169.4 148.2 L172.2 145.0 L175.1 141.7 L178.0 138.3 L180.9 134.9 L183.8 131.3 L186.6 127.7 L189.5 124.0 L192.4 120.3 L195.2 116.6 L198.1 112.8 L201.0 109.0 L203.9 105.2 L206.8 101.5 L209.6 97.7 L212.5 94.0 L215.4 90.4 L218.2 86.8 L221.1 83.3 L224.0 79.9 L226.9 76.6 L229.8 73.5 L232.6 70.5 L235.5 67.6 L238.4 65.0 L241.2 62.5 L244.1 60.2 L247.0 58.1 L249.9 56.2 L252.8 54.6 L255.6 53.2 L258.5 52.1 L261.4 51.2 L264.2 50.5 L267.1 50.1 L270.0 50.0 L272.9 50.1 L275.8 50.5 L278.6 51.2 L281.5 52.1 L284.4 53.2 L287.2 54.6 L290.1 56.2 L293.0 58.1 L295.9 60.2 L298.8 62.5 L301.6 65.0 L304.5 67.6 L307.4 70.5 L310.2 73.5 L313.1 76.6 L316.0 79.9 L318.9 83.3 L321.8 86.8 L324.6 90.4 L327.5 94.0 L330.4 97.7 L333.2 101.5 L336.1 105.2 L339.0 109.0 L341.9 112.8 L344.8 116.6 L347.6 120.3 L350.5 124.0 L353.4 127.7 L356.2 131.3 L359.1 134.9 L362.0 138.3 L364.9 141.7 L367.8 145.0 L370.6 148.2 L373.5 151.3 L376.4 154.3 L379.2 157.2 L382.1 159.9 L385.0 162.6 L387.9 165.1 L390.8 167.6 L393.6 169.9 L396.5 172.1 L399.4 174.1 L402.2 176.1 L405.1 178.0 L408.0 179.7 L410.9 181.3 L413.8 182.9 L416.6 184.3 L419.5 185.7 L422.4 186.9 L425.2 188.1 L428.1 189.1 L431.0 190.1 L433.9 191.1 L436.8 191.9 L439.6 192.7 L442.5 193.4 L445.4 194.1 L448.2 194.7 L451.1 195.2 L454.0 195.7 L456.9 196.2 L459.8 196.6 L462.6 197.0 L465.5 197.3 L468.4 197.6 L471.2 197.9 L474.1 198.1 L477.0 198.3 L479.9 198.5 L482.8 198.7 L485.6 198.9 L488.5 199.0 L491.4 199.1 L494.2 199.2 L497.1 199.3 L500.0 199.4" fill="none" stroke="#2dd4bf" stroke-width="3.5"/>
    <line x1="316" y1="40" x2="316" y2="200" stroke="#f59e0b" stroke-width="2.5" stroke-dasharray="6 5"/>
    <line x1="224" y1="40" x2="224" y2="200" stroke="#f59e0b" stroke-width="2.5" stroke-dasharray="6 5"/>
    <text x="322" y="48" fill="#fbbf24" style="font-size:13px">observed +2 pts</text>
    <text x="442.5" y="150" fill="#fbbf24" text-anchor="middle" style="font-size:15px;font-weight:700">shaded: p ≈ 0.50</text>
  </g>
</svg>
</div>

<!--
This slide derives the width of the H₀ curve from slide 8, so we can finally say how likely an observed gap is. We know from the 89% vs 91% example that each model's score is noisy: about 2.2 points for A and 2.0 for B at n = 200. The gap between them is a difference of two noisy quantities, and the key fact is that for independent quantities, variances add, even when you subtract. So the variance of the gap is the sum of the two squared standard errors, and its standard error is the square root: about 3.0 points. The difference is noisier than either score on its own, which is why a 2-point gap is not impressive.

Now connect that to the picture. If H₀ is true, the true gap is zero, and across different test sets the observed gap would form a bell curve centered at zero whose standard deviation is exactly that SE of the gap: about 3 points. The amber bracket shows plus or minus one SE; the second row of axis labels counts distance in SE units. Our observed gap of 2 points is only 0.67 SE from zero, deep inside the curve.

The p-value is the area under the curve at least that far from zero in either direction, the shaded tails. Because 2 points is small relative to the 3-point width, those tails hold about half of the area, so p is about 0.50. Even if the models were identical, we would see a gap this large about half the time. For comparison, to reach p = 0.05 the gap would have to be about 1.96 SE, or roughly 5.9 points.

Caveat: this version treats the two scores as independent. When both models are scored on the same test set the errors are correlated, and the paired SE from McNemar's test, which depends only on the disagreements, is smaller. That is the next slide.
-->

---
glowSeed: 5529
---

# Same Test Set, Correlated Errors

<div class="grid grid-cols-2 gap-8 items-start">
<div>
<div class="space-y-2 mt-2" style="font-size: .85em">
<div v-click="1" border="2 solid white/5" bg="white/5" rounded-lg px-4 py-2>
<span class="font-bold text-amber-300">The problem</span><span class="text-sm opacity-85"> — Both models see the same examples, so hard cases are hard for both and their errors are correlated. Adding SE<sub>A</sub>² + SE<sub>B</sub>² as if independent overstates the noise.</span>
</div>
<div v-click="2" border="2 solid white/5" bg="white/5" rounded-lg px-4 py-2>
<span class="font-bold text-blue-300">The idea</span><span class="text-sm opacity-85"> — Score the <em>difference per example</em>: +1 if only B is right, −1 if only A is right, 0 if they agree. Agreements add no noise.</span>
</div>
<div v-click="3" border="2 solid teal-800" bg="teal-800/20" rounded-lg px-4 py-1>
<span class="font-bold text-teal-200">Paired standard error</span>

$$
\mathrm{SE}_{\text{gap}}\approx\sqrt{\frac{q}{n}},\qquad q=\frac{\text{disagreements}}{n}
$$

</div>
<div v-click="4" border="2 solid white/5" bg="white/5" rounded-lg px-4 py-2>
<span class="font-bold text-violet-300">The payoff</span><span class="text-sm opacity-85"> — With 20 disagreements in 200 (q = 0.10), SE ≈ 2.2 pts, not 3.0. The 2-pt gap is now 0.89 SE from zero (p ≈ 0.37). Fewer disagreements shrink SE further.</span>
</div>
</div>
</div>
<svg role="img" aria-label="Top: 200 test examples drawn as small squares, 180 gray where the models agree, 12 teal where only B is right, 8 red where only A is right. Bottom: two bell curves for the gap under the null, a wide gray one for the unpaired standard error of 3.0 points and a narrower teal one for the paired standard error of 2.2 points, with the observed 2-point gap marked." viewBox="0 0 540 350" class="w-full mt-1">
  <g v-click="1">
    <g><rect x="30" y="30" width="10" height="10" rx="2" fill="#475569" fill-opacity=".55"/><rect x="42" y="30" width="10" height="10" rx="2" fill="#475569" fill-opacity=".55"/><rect x="54" y="30" width="10" height="10" rx="2" fill="#475569" fill-opacity=".55"/><rect x="90" y="30" width="10" height="10" rx="2" fill="#475569" fill-opacity=".55"/><rect x="114" y="30" width="10" height="10" rx="2" fill="#475569" fill-opacity=".55"/><rect x="126" y="30" width="10" height="10" rx="2" fill="#475569" fill-opacity=".55"/><rect x="138" y="30" width="10" height="10" rx="2" fill="#475569" fill-opacity=".55"/><rect x="150" y="30" width="10" height="10" rx="2" fill="#475569" fill-opacity=".55"/><rect x="162" y="30" width="10" height="10" rx="2" fill="#475569" fill-opacity=".55"/><rect x="174" y="30" width="10" height="10" rx="2" fill="#475569" fill-opacity=".55"/><rect x="198" y="30" width="10" height="10" rx="2" fill="#475569" fill-opacity=".55"/><rect x="210" y="30" width="10" height="10" rx="2" fill="#475569" fill-opacity=".55"/><rect x="222" y="30" width="10" height="10" rx="2" fill="#475569" fill-opacity=".55"/><rect x="234" y="30" width="10" height="10" rx="2" fill="#475569" fill-opacity=".55"/><rect x="246" y="30" width="10" height="10" rx="2" fill="#475569" fill-opacity=".55"/><rect x="258" y="30" width="10" height="10" rx="2" fill="#475569" fill-opacity=".55"/><rect x="270" y="30" width="10" height="10" rx="2" fill="#475569" fill-opacity=".55"/><rect x="282" y="30" width="10" height="10" rx="2" fill="#475569" fill-opacity=".55"/><rect x="294" y="30" width="10" height="10" rx="2" fill="#475569" fill-opacity=".55"/><rect x="306" y="30" width="10" height="10" rx="2" fill="#475569" fill-opacity=".55"/><rect x="318" y="30" width="10" height="10" rx="2" fill="#475569" fill-opacity=".55"/><rect x="330" y="30" width="10" height="10" rx="2" fill="#475569" fill-opacity=".55"/><rect x="342" y="30" width="10" height="10" rx="2" fill="#475569" fill-opacity=".55"/><rect x="354" y="30" width="10" height="10" rx="2" fill="#475569" fill-opacity=".55"/><rect x="390" y="30" width="10" height="10" rx="2" fill="#475569" fill-opacity=".55"/><rect x="402" y="30" width="10" height="10" rx="2" fill="#475569" fill-opacity=".55"/><rect x="414" y="30" width="10" height="10" rx="2" fill="#475569" fill-opacity=".55"/><rect x="426" y="30" width="10" height="10" rx="2" fill="#475569" fill-opacity=".55"/><rect x="438" y="30" width="10" height="10" rx="2" fill="#475569" fill-opacity=".55"/><rect x="450" y="30" width="10" height="10" rx="2" fill="#475569" fill-opacity=".55"/><rect x="462" y="30" width="10" height="10" rx="2" fill="#475569" fill-opacity=".55"/><rect x="474" y="30" width="10" height="10" rx="2" fill="#475569" fill-opacity=".55"/><rect x="486" y="30" width="10" height="10" rx="2" fill="#475569" fill-opacity=".55"/><rect x="498" y="30" width="10" height="10" rx="2" fill="#475569" fill-opacity=".55"/><rect x="30" y="42" width="10" height="10" rx="2" fill="#475569" fill-opacity=".55"/><rect x="54" y="42" width="10" height="10" rx="2" fill="#475569" fill-opacity=".55"/><rect x="66" y="42" width="10" height="10" rx="2" fill="#475569" fill-opacity=".55"/><rect x="78" y="42" width="10" height="10" rx="2" fill="#475569" fill-opacity=".55"/><rect x="90" y="42" width="10" height="10" rx="2" fill="#475569" fill-opacity=".55"/><rect x="102" y="42" width="10" height="10" rx="2" fill="#475569" fill-opacity=".55"/><rect x="114" y="42" width="10" height="10" rx="2" fill="#475569" fill-opacity=".55"/><rect x="126" y="42" width="10" height="10" rx="2" fill="#475569" fill-opacity=".55"/><rect x="138" y="42" width="10" height="10" rx="2" fill="#475569" fill-opacity=".55"/><rect x="150" y="42" width="10" height="10" rx="2" fill="#475569" fill-opacity=".55"/><rect x="162" y="42" width="10" height="10" rx="2" fill="#475569" fill-opacity=".55"/><rect x="174" y="42" width="10" height="10" rx="2" fill="#475569" fill-opacity=".55"/><rect x="186" y="42" width="10" height="10" rx="2" fill="#475569" fill-opacity=".55"/><rect x="198" y="42" width="10" height="10" rx="2" fill="#475569" fill-opacity=".55"/><rect x="210" y="42" width="10" height="10" rx="2" fill="#475569" fill-opacity=".55"/><rect x="222" y="42" width="10" height="10" rx="2" fill="#475569" fill-opacity=".55"/><rect x="234" y="42" width="10" height="10" rx="2" fill="#475569" fill-opacity=".55"/><rect x="246" y="42" width="10" height="10" rx="2" fill="#475569" fill-opacity=".55"/><rect x="258" y="42" width="10" height="10" rx="2" fill="#475569" fill-opacity=".55"/><rect x="270" y="42" width="10" height="10" rx="2" fill="#475569" fill-opacity=".55"/><rect x="282" y="42" width="10" height="10" rx="2" fill="#475569" fill-opacity=".55"/><rect x="294" y="42" width="10" height="10" rx="2" fill="#475569" fill-opacity=".55"/><rect x="306" y="42" width="10" height="10" rx="2" fill="#475569" fill-opacity=".55"/><rect x="330" y="42" width="10" height="10" rx="2" fill="#475569" fill-opacity=".55"/><rect x="342" y="42" width="10" height="10" rx="2" fill="#475569" fill-opacity=".55"/><rect x="366" y="42" width="10" height="10" rx="2" fill="#475569" fill-opacity=".55"/><rect x="378" y="42" width="10" height="10" rx="2" fill="#475569" fill-opacity=".55"/><rect x="390" y="42" width="10" height="10" rx="2" fill="#475569" fill-opacity=".55"/><rect x="402" y="42" width="10" height="10" rx="2" fill="#475569" fill-opacity=".55"/><rect x="414" y="42" width="10" height="10" rx="2" fill="#475569" fill-opacity=".55"/><rect x="426" y="42" width="10" height="10" rx="2" fill="#475569" fill-opacity=".55"/><rect x="438" y="42" width="10" height="10" rx="2" fill="#475569" fill-opacity=".55"/><rect x="462" y="42" width="10" height="10" rx="2" fill="#475569" fill-opacity=".55"/><rect x="474" y="42" width="10" height="10" rx="2" fill="#475569" fill-opacity=".55"/><rect x="486" y="42" width="10" height="10" rx="2" fill="#475569" fill-opacity=".55"/><rect x="498" y="42" width="10" height="10" rx="2" fill="#475569" fill-opacity=".55"/><rect x="30" y="54" width="10" height="10" rx="2" fill="#475569" fill-opacity=".55"/><rect x="54" y="54" width="10" height="10" rx="2" fill="#475569" fill-opacity=".55"/><rect x="66" y="54" width="10" height="10" rx="2" fill="#475569" fill-opacity=".55"/><rect x="78" y="54" width="10" height="10" rx="2" fill="#475569" fill-opacity=".55"/><rect x="90" y="54" width="10" height="10" rx="2" fill="#475569" fill-opacity=".55"/><rect x="114" y="54" width="10" height="10" rx="2" fill="#475569" fill-opacity=".55"/><rect x="126" y="54" width="10" height="10" rx="2" fill="#475569" fill-opacity=".55"/><rect x="138" y="54" width="10" height="10" rx="2" fill="#475569" fill-opacity=".55"/><rect x="150" y="54" width="10" height="10" rx="2" fill="#475569" fill-opacity=".55"/><rect x="162" y="54" width="10" height="10" rx="2" fill="#475569" fill-opacity=".55"/><rect x="174" y="54" width="10" height="10" rx="2" fill="#475569" fill-opacity=".55"/><rect x="186" y="54" width="10" height="10" rx="2" fill="#475569" fill-opacity=".55"/><rect x="210" y="54" width="10" height="10" rx="2" fill="#475569" fill-opacity=".55"/><rect x="222" y="54" width="10" height="10" rx="2" fill="#475569" fill-opacity=".55"/><rect x="234" y="54" width="10" height="10" rx="2" fill="#475569" fill-opacity=".55"/><rect x="246" y="54" width="10" height="10" rx="2" fill="#475569" fill-opacity=".55"/><rect x="258" y="54" width="10" height="10" rx="2" fill="#475569" fill-opacity=".55"/><rect x="270" y="54" width="10" height="10" rx="2" fill="#475569" fill-opacity=".55"/><rect x="282" y="54" width="10" height="10" rx="2" fill="#475569" fill-opacity=".55"/><rect x="306" y="54" width="10" height="10" rx="2" fill="#475569" fill-opacity=".55"/><rect x="318" y="54" width="10" height="10" rx="2" fill="#475569" fill-opacity=".55"/><rect x="342" y="54" width="10" height="10" rx="2" fill="#475569" fill-opacity=".55"/><rect x="354" y="54" width="10" height="10" rx="2" fill="#475569" fill-opacity=".55"/><rect x="366" y="54" width="10" height="10" rx="2" fill="#475569" fill-opacity=".55"/><rect x="378" y="54" width="10" height="10" rx="2" fill="#475569" fill-opacity=".55"/><rect x="390" y="54" width="10" height="10" rx="2" fill="#475569" fill-opacity=".55"/><rect x="402" y="54" width="10" height="10" rx="2" fill="#475569" fill-opacity=".55"/><rect x="414" y="54" width="10" height="10" rx="2" fill="#475569" fill-opacity=".55"/><rect x="426" y="54" width="10" height="10" rx="2" fill="#475569" fill-opacity=".55"/><rect x="438" y="54" width="10" height="10" rx="2" fill="#475569" fill-opacity=".55"/><rect x="450" y="54" width="10" height="10" rx="2" fill="#475569" fill-opacity=".55"/><rect x="462" y="54" width="10" height="10" rx="2" fill="#475569" fill-opacity=".55"/><rect x="474" y="54" width="10" height="10" rx="2" fill="#475569" fill-opacity=".55"/><rect x="486" y="54" width="10" height="10" rx="2" fill="#475569" fill-opacity=".55"/><rect x="498" y="54" width="10" height="10" rx="2" fill="#475569" fill-opacity=".55"/><rect x="54" y="66" width="10" height="10" rx="2" fill="#475569" fill-opacity=".55"/><rect x="66" y="66" width="10" height="10" rx="2" fill="#475569" fill-opacity=".55"/><rect x="78" y="66" width="10" height="10" rx="2" fill="#475569" fill-opacity=".55"/><rect x="90" y="66" width="10" height="10" rx="2" fill="#475569" fill-opacity=".55"/><rect x="102" y="66" width="10" height="10" rx="2" fill="#475569" fill-opacity=".55"/><rect x="114" y="66" width="10" height="10" rx="2" fill="#475569" fill-opacity=".55"/><rect x="126" y="66" width="10" height="10" rx="2" fill="#475569" fill-opacity=".55"/><rect x="138" y="66" width="10" height="10" rx="2" fill="#475569" fill-opacity=".55"/><rect x="150" y="66" width="10" height="10" rx="2" fill="#475569" fill-opacity=".55"/><rect x="162" y="66" width="10" height="10" rx="2" fill="#475569" fill-opacity=".55"/><rect x="174" y="66" width="10" height="10" rx="2" fill="#475569" fill-opacity=".55"/><rect x="186" y="66" width="10" height="10" rx="2" fill="#475569" fill-opacity=".55"/><rect x="198" y="66" width="10" height="10" rx="2" fill="#475569" fill-opacity=".55"/><rect x="210" y="66" width="10" height="10" rx="2" fill="#475569" fill-opacity=".55"/><rect x="222" y="66" width="10" height="10" rx="2" fill="#475569" fill-opacity=".55"/><rect x="234" y="66" width="10" height="10" rx="2" fill="#475569" fill-opacity=".55"/><rect x="246" y="66" width="10" height="10" rx="2" fill="#475569" fill-opacity=".55"/><rect x="258" y="66" width="10" height="10" rx="2" fill="#475569" fill-opacity=".55"/><rect x="270" y="66" width="10" height="10" rx="2" fill="#475569" fill-opacity=".55"/><rect x="282" y="66" width="10" height="10" rx="2" fill="#475569" fill-opacity=".55"/><rect x="294" y="66" width="10" height="10" rx="2" fill="#475569" fill-opacity=".55"/><rect x="306" y="66" width="10" height="10" rx="2" fill="#475569" fill-opacity=".55"/><rect x="318" y="66" width="10" height="10" rx="2" fill="#475569" fill-opacity=".55"/><rect x="330" y="66" width="10" height="10" rx="2" fill="#475569" fill-opacity=".55"/><rect x="342" y="66" width="10" height="10" rx="2" fill="#475569" fill-opacity=".55"/><rect x="354" y="66" width="10" height="10" rx="2" fill="#475569" fill-opacity=".55"/><rect x="366" y="66" width="10" height="10" rx="2" fill="#475569" fill-opacity=".55"/><rect x="378" y="66" width="10" height="10" rx="2" fill="#475569" fill-opacity=".55"/><rect x="390" y="66" width="10" height="10" rx="2" fill="#475569" fill-opacity=".55"/><rect x="402" y="66" width="10" height="10" rx="2" fill="#475569" fill-opacity=".55"/><rect x="414" y="66" width="10" height="10" rx="2" fill="#475569" fill-opacity=".55"/><rect x="426" y="66" width="10" height="10" rx="2" fill="#475569" fill-opacity=".55"/><rect x="438" y="66" width="10" height="10" rx="2" fill="#475569" fill-opacity=".55"/><rect x="450" y="66" width="10" height="10" rx="2" fill="#475569" fill-opacity=".55"/><rect x="462" y="66" width="10" height="10" rx="2" fill="#475569" fill-opacity=".55"/><rect x="486" y="66" width="10" height="10" rx="2" fill="#475569" fill-opacity=".55"/><rect x="498" y="66" width="10" height="10" rx="2" fill="#475569" fill-opacity=".55"/><rect x="30" y="78" width="10" height="10" rx="2" fill="#475569" fill-opacity=".55"/><rect x="42" y="78" width="10" height="10" rx="2" fill="#475569" fill-opacity=".55"/><rect x="54" y="78" width="10" height="10" rx="2" fill="#475569" fill-opacity=".55"/><rect x="66" y="78" width="10" height="10" rx="2" fill="#475569" fill-opacity=".55"/><rect x="78" y="78" width="10" height="10" rx="2" fill="#475569" fill-opacity=".55"/><rect x="90" y="78" width="10" height="10" rx="2" fill="#475569" fill-opacity=".55"/><rect x="102" y="78" width="10" height="10" rx="2" fill="#475569" fill-opacity=".55"/><rect x="114" y="78" width="10" height="10" rx="2" fill="#475569" fill-opacity=".55"/><rect x="138" y="78" width="10" height="10" rx="2" fill="#475569" fill-opacity=".55"/><rect x="150" y="78" width="10" height="10" rx="2" fill="#475569" fill-opacity=".55"/><rect x="162" y="78" width="10" height="10" rx="2" fill="#475569" fill-opacity=".55"/><rect x="174" y="78" width="10" height="10" rx="2" fill="#475569" fill-opacity=".55"/><rect x="186" y="78" width="10" height="10" rx="2" fill="#475569" fill-opacity=".55"/><rect x="198" y="78" width="10" height="10" rx="2" fill="#475569" fill-opacity=".55"/><rect x="210" y="78" width="10" height="10" rx="2" fill="#475569" fill-opacity=".55"/><rect x="222" y="78" width="10" height="10" rx="2" fill="#475569" fill-opacity=".55"/><rect x="234" y="78" width="10" height="10" rx="2" fill="#475569" fill-opacity=".55"/><rect x="246" y="78" width="10" height="10" rx="2" fill="#475569" fill-opacity=".55"/><rect x="258" y="78" width="10" height="10" rx="2" fill="#475569" fill-opacity=".55"/><rect x="270" y="78" width="10" height="10" rx="2" fill="#475569" fill-opacity=".55"/><rect x="282" y="78" width="10" height="10" rx="2" fill="#475569" fill-opacity=".55"/><rect x="294" y="78" width="10" height="10" rx="2" fill="#475569" fill-opacity=".55"/><rect x="306" y="78" width="10" height="10" rx="2" fill="#475569" fill-opacity=".55"/><rect x="318" y="78" width="10" height="10" rx="2" fill="#475569" fill-opacity=".55"/><rect x="330" y="78" width="10" height="10" rx="2" fill="#475569" fill-opacity=".55"/><rect x="342" y="78" width="10" height="10" rx="2" fill="#475569" fill-opacity=".55"/><rect x="354" y="78" width="10" height="10" rx="2" fill="#475569" fill-opacity=".55"/><rect x="366" y="78" width="10" height="10" rx="2" fill="#475569" fill-opacity=".55"/><rect x="378" y="78" width="10" height="10" rx="2" fill="#475569" fill-opacity=".55"/><rect x="390" y="78" width="10" height="10" rx="2" fill="#475569" fill-opacity=".55"/><rect x="402" y="78" width="10" height="10" rx="2" fill="#475569" fill-opacity=".55"/><rect x="414" y="78" width="10" height="10" rx="2" fill="#475569" fill-opacity=".55"/><rect x="426" y="78" width="10" height="10" rx="2" fill="#475569" fill-opacity=".55"/><rect x="438" y="78" width="10" height="10" rx="2" fill="#475569" fill-opacity=".55"/><rect x="450" y="78" width="10" height="10" rx="2" fill="#475569" fill-opacity=".55"/><rect x="474" y="78" width="10" height="10" rx="2" fill="#475569" fill-opacity=".55"/><rect x="486" y="78" width="10" height="10" rx="2" fill="#475569" fill-opacity=".55"/><rect x="498" y="78" width="10" height="10" rx="2" fill="#475569" fill-opacity=".55"/></g>
    <text x="30" y="20" fill="#cbd5e1" style="font-size:13px">200 test examples, one square each</text>
  </g>
  <g v-click="2"><rect x="66" y="30" width="10" height="10" rx="2" fill="#f87171"/><rect x="78" y="30" width="10" height="10" rx="2" fill="#2dd4bf"/><rect x="102" y="30" width="10" height="10" rx="2" fill="#f87171"/><rect x="186" y="30" width="10" height="10" rx="2" fill="#2dd4bf"/><rect x="366" y="30" width="10" height="10" rx="2" fill="#2dd4bf"/><rect x="378" y="30" width="10" height="10" rx="2" fill="#f87171"/><rect x="42" y="42" width="10" height="10" rx="2" fill="#2dd4bf"/><rect x="318" y="42" width="10" height="10" rx="2" fill="#2dd4bf"/><rect x="354" y="42" width="10" height="10" rx="2" fill="#f87171"/><rect x="450" y="42" width="10" height="10" rx="2" fill="#f87171"/><rect x="42" y="54" width="10" height="10" rx="2" fill="#2dd4bf"/><rect x="102" y="54" width="10" height="10" rx="2" fill="#2dd4bf"/><rect x="198" y="54" width="10" height="10" rx="2" fill="#f87171"/><rect x="294" y="54" width="10" height="10" rx="2" fill="#2dd4bf"/><rect x="330" y="54" width="10" height="10" rx="2" fill="#f87171"/><rect x="30" y="66" width="10" height="10" rx="2" fill="#2dd4bf"/><rect x="42" y="66" width="10" height="10" rx="2" fill="#2dd4bf"/><rect x="474" y="66" width="10" height="10" rx="2" fill="#2dd4bf"/><rect x="126" y="78" width="10" height="10" rx="2" fill="#2dd4bf"/><rect x="462" y="78" width="10" height="10" rx="2" fill="#f87171"/>
    <text x="510" y="102" fill="#94a3b8" text-anchor="end" style="font-size:13px">180 agree (no information)</text>
    <text x="30" y="102" fill="#5eead4" style="font-size:13px;font-weight:700">12 B only</text>
    <text x="115" y="102" fill="#fca5a5" style="font-size:13px;font-weight:700">8 A only</text>
  </g>
  <g v-click="4">
    <line x1="30" y1="300" x2="510" y2="300" stroke="#64748b" stroke-width="2"/>
    <g fill="#cbd5e1" style="font-size:12px" text-anchor="middle"><text x="63" y="318">−9</text><text x="132" y="318">−6</text><text x="201" y="318">−3</text><text x="270" y="318">0</text><text x="339" y="318">+3</text><text x="408" y="318">+6</text><text x="477" y="318">+9</text>
      <text x="270" y="338" fill="#e2e8f0" style="font-size:14px">gap size under H₀ (accuracy points)</text></g>
    <path d="M40.0 299.7 L42.9 299.6 L45.8 299.6 L48.6 299.5 L51.5 299.5 L54.4 299.4 L57.2 299.3 L60.1 299.2 L63.0 299.1 L65.9 299.0 L68.8 298.9 L71.6 298.7 L74.5 298.5 L77.4 298.4 L80.2 298.2 L83.1 297.9 L86.0 297.7 L88.9 297.4 L91.8 297.1 L94.6 296.8 L97.5 296.5 L100.4 296.1 L103.2 295.6 L106.1 295.2 L109.0 294.7 L111.9 294.2 L114.8 293.6 L117.6 293.0 L120.5 292.3 L123.4 291.6 L126.2 290.8 L129.1 290.0 L132.0 289.1 L134.9 288.1 L137.8 287.1 L140.6 286.1 L143.5 285.0 L146.4 283.8 L149.2 282.6 L152.1 281.3 L155.0 279.9 L157.9 278.5 L160.8 277.0 L163.6 275.4 L166.5 273.8 L169.4 272.1 L172.2 270.4 L175.1 268.7 L178.0 266.8 L180.9 265.0 L183.8 263.1 L186.6 261.1 L189.5 259.2 L192.4 257.2 L195.2 255.1 L198.1 253.1 L201.0 251.1 L203.9 249.0 L206.8 247.0 L209.6 245.0 L212.5 243.0 L215.4 241.0 L218.2 239.1 L221.1 237.2 L224.0 235.4 L226.9 233.6 L229.8 232.0 L232.6 230.3 L235.5 228.8 L238.4 227.4 L241.2 226.0 L244.1 224.8 L247.0 223.7 L249.9 222.7 L252.8 221.8 L255.6 221.1 L258.5 220.4 L261.4 220.0 L264.2 219.6 L267.1 219.4 L270.0 219.3 L272.9 219.4 L275.8 219.6 L278.6 220.0 L281.5 220.4 L284.4 221.1 L287.2 221.8 L290.1 222.7 L293.0 223.7 L295.9 224.8 L298.8 226.0 L301.6 227.4 L304.5 228.8 L307.4 230.3 L310.2 232.0 L313.1 233.6 L316.0 235.4 L318.9 237.2 L321.8 239.1 L324.6 241.0 L327.5 243.0 L330.4 245.0 L333.2 247.0 L336.1 249.0 L339.0 251.1 L341.9 253.1 L344.8 255.1 L347.6 257.2 L350.5 259.2 L353.4 261.1 L356.2 263.1 L359.1 265.0 L362.0 266.8 L364.9 268.7 L367.8 270.4 L370.6 272.1 L373.5 273.8 L376.4 275.4 L379.2 277.0 L382.1 278.5 L385.0 279.9 L387.9 281.3 L390.8 282.6 L393.6 283.8 L396.5 285.0 L399.4 286.1 L402.2 287.1 L405.1 288.1 L408.0 289.1 L410.9 290.0 L413.8 290.8 L416.6 291.6 L419.5 292.3 L422.4 293.0 L425.2 293.6 L428.1 294.2 L431.0 294.7 L433.9 295.2 L436.8 295.6 L439.6 296.1 L442.5 296.5 L445.4 296.8 L448.2 297.1 L451.1 297.4 L454.0 297.7 L456.9 297.9 L459.8 298.2 L462.6 298.4 L465.5 298.5 L468.4 298.7 L471.2 298.9 L474.1 299.0 L477.0 299.1 L479.9 299.2 L482.8 299.3 L485.6 299.4 L488.5 299.5 L491.4 299.5 L494.2 299.6 L497.1 299.6 L500.0 299.7" fill="none" stroke="#94a3b8" stroke-width="3" stroke-dasharray="7 5"/>
    <path d="M40.0 300.0 L42.9 300.0 L45.8 300.0 L48.6 300.0 L51.5 300.0 L54.4 300.0 L57.2 300.0 L60.1 300.0 L63.0 300.0 L65.9 300.0 L68.8 299.9 L71.6 299.9 L74.5 299.9 L77.4 299.9 L80.2 299.9 L83.1 299.9 L86.0 299.8 L88.9 299.8 L91.8 299.7 L94.6 299.7 L97.5 299.6 L100.4 299.5 L103.2 299.4 L106.1 299.3 L109.0 299.2 L111.9 299.0 L114.8 298.9 L117.6 298.7 L120.5 298.4 L123.4 298.1 L126.2 297.8 L129.1 297.5 L132.0 297.0 L134.9 296.6 L137.8 296.0 L140.6 295.4 L143.5 294.7 L146.4 294.0 L149.2 293.1 L152.1 292.2 L155.0 291.1 L157.9 290.0 L160.8 288.7 L163.6 287.3 L166.5 285.7 L169.4 284.0 L172.2 282.2 L175.1 280.3 L178.0 278.2 L180.9 275.9 L183.8 273.5 L186.6 270.9 L189.5 268.2 L192.4 265.4 L195.2 262.4 L198.1 259.2 L201.0 256.0 L203.9 252.6 L206.8 249.2 L209.6 245.7 L212.5 242.1 L215.4 238.4 L218.2 234.8 L221.1 231.1 L224.0 227.5 L226.9 223.9 L229.8 220.3 L232.6 216.9 L235.5 213.6 L238.4 210.4 L241.2 207.4 L244.1 204.6 L247.0 202.1 L249.9 199.7 L252.8 197.7 L255.6 195.9 L258.5 194.4 L261.4 193.3 L264.2 192.4 L267.1 191.9 L270.0 191.8 L272.9 191.9 L275.8 192.4 L278.6 193.3 L281.5 194.4 L284.4 195.9 L287.2 197.7 L290.1 199.7 L293.0 202.1 L295.9 204.6 L298.8 207.4 L301.6 210.4 L304.5 213.6 L307.4 216.9 L310.2 220.3 L313.1 223.9 L316.0 227.5 L318.9 231.1 L321.8 234.8 L324.6 238.4 L327.5 242.1 L330.4 245.7 L333.2 249.2 L336.1 252.6 L339.0 256.0 L341.9 259.2 L344.8 262.4 L347.6 265.4 L350.5 268.2 L353.4 270.9 L356.2 273.5 L359.1 275.9 L362.0 278.2 L364.9 280.3 L367.8 282.2 L370.6 284.0 L373.5 285.7 L376.4 287.3 L379.2 288.7 L382.1 290.0 L385.0 291.1 L387.9 292.2 L390.8 293.1 L393.6 294.0 L396.5 294.7 L399.4 295.4 L402.2 296.0 L405.1 296.6 L408.0 297.0 L410.9 297.5 L413.8 297.8 L416.6 298.1 L419.5 298.4 L422.4 298.7 L425.2 298.9 L428.1 299.0 L431.0 299.2 L433.9 299.3 L436.8 299.4 L439.6 299.5 L442.5 299.6 L445.4 299.7 L448.2 299.7 L451.1 299.8 L454.0 299.8 L456.9 299.9 L459.8 299.9 L462.6 299.9 L465.5 299.9 L468.4 299.9 L471.2 299.9 L474.1 300.0 L477.0 300.0 L479.9 300.0 L482.8 300.0 L485.6 300.0 L488.5 300.0 L491.4 300.0 L494.2 300.0 L497.1 300.0 L500.0 300.0" fill="none" stroke="#2dd4bf" stroke-width="3.5"/>
    <line x1="316" y1="128" x2="316" y2="300" stroke="#f59e0b" stroke-width="2.5" stroke-dasharray="6 5"/>
    <text x="322" y="136" fill="#fbbf24" style="font-size:13px">observed +2 pts</text>
    <text x="187.2" y="160" fill="#cbd5e1" text-anchor="end" style="font-size:13px">unpaired: SE ≈ 3.0</text>
    <text x="187.2" y="178" fill="#5eead4" text-anchor="end" style="font-size:13px;font-weight:700">paired: SE ≈ 2.2</text>
  </g>
</svg>
</div>

<!--
The previous slide derived a standard error of 3.0 points for the gap in the 89% vs 91% example. That calculation added the two models' variances, which is only valid if their errors are independent. They are not: both models are evaluated on the very same 200 examples, and an example that is hard — ambiguous, mislabeled, out-of-distribution — tends to be missed by both. Correlated errors mean the noise in the gap is smaller than the unpaired formula says.

The way to exploit this is to look at the difference one example at a time. For each test example, record +1 if only B is right, −1 if only A is right, and 0 if the models agree. The gap is just the average of these numbers. The picture shows the idea: of the 200 squares, 180 are grey agreements that contribute exactly zero to every term, and only the 20 coloured squares, 12 where B wins and 8 where A wins, carry any information. This is the same averaging argument as for accuracy: the variance of the average is the variance of a single term over n, and a single term is nonzero only when the models disagree, so the standard error is the square root of q over n, where q is the disagreement rate.

With 20 disagreements out of 200, q is 0.10 and the SE is about 2.2 points rather than 3.0. The teal curve is narrower than the dashed grey one, so the observed 2-point gap sits further into the tail: 0.89 standard errors from zero instead of 0.67. The p-value moves from about 0.50 to about 0.37; still not significant with so few disagreements, but the test has become more sensitive, and with fewer disagreements the effect is larger. That square-root-of-q-over-n calculation, written in terms of counts, is the heart of McNemar's test, which we reach after setting up the decision rule and its two kinds of error.
-->

---
glowSeed: 5528
---

# A Test Is a Decision Rule

<div class="grid grid-cols-2 gap-8 items-start">
<div>
<div class="space-y-3 mt-2" style="font-size: .92em">
<div v-click="1" border="2 solid white/5" bg="white/5" rounded-lg px-4 py-3>
<span class="font-bold text-teal-300">1 · Make a rule</span>
<span class="text-sm opacity-85"> — Call the gap significant if it is larger than a cutoff, the critical value.</span>
</div>
<div v-click="2" border="2 solid white/5" bg="white/5" rounded-lg px-4 py-3>
<span class="font-bold text-amber-300">2 · The rule can fail two ways</span>
<span class="text-sm opacity-85"> — A false alarm when the models are equal, or a miss when B is truly better.</span>
</div>
<div v-click="3" border="2 solid white/5" bg="white/5" rounded-lg px-4 py-3>
<span class="font-bold text-blue-300">3 · One cutoff, two errors</span>
<span class="text-sm opacity-85"> — Moving the cutoff only trades one error for the other.</span>
</div>
<div v-click="4" border="2 solid teal-800" bg="teal-800/20" rounded-lg px-4 py-3>
<span class="font-bold text-teal-200">4 · Choose α first</span>
<span class="text-sm opacity-85"> — We pick the false-alarm rate we accept (usually 0.05), which fixes the critical value. Power follows from it. Only more data shrinks both errors.</span>
</div>
</div>
</div>
<div v-click="2" role="img" aria-label="Two by two table of test outcomes. If the null is true and we reject it, that is a Type I error. If the null is false and we do not reject it, that is a Type II error. The other two cells are correct decisions." class="mt-6">
<div class="grid grid-cols-[7rem_1fr_1fr] gap-2 text-center text-xs">
<div></div><div class="font-bold text-blue-300">Reject H₀<div class="font-normal opacity-70">call B better</div></div><div class="font-bold text-blue-300">Don't reject H₀<div class="font-normal opacity-70">no verdict</div></div>
<div class="flex flex-col items-end justify-center pr-2 font-bold text-teal-300">H₀ true<div class="font-normal opacity-70">models equal</div></div>
<div border="2 solid red-800" bg="red-800/20" rounded-lg p-4><div class="text-lg font-bold text-red-300">Type I (α)</div><div class="text-xs opacity-75">false alarm</div></div>
<div border="2 solid white/10" bg="white/5" rounded-lg p-4><div class="text-lg font-bold">Correct</div><div class="text-xs opacity-60">1 − α</div></div>
<div class="flex flex-col items-end justify-center pr-2 font-bold text-teal-300">H₀ false<div class="font-normal opacity-70">B truly better</div></div>
<div border="2 solid teal-800" bg="teal-800/20" rounded-lg p-4><div class="text-lg font-bold text-teal-200">Correct</div><div class="text-xs opacity-75">power = 1 − β</div></div>
<div border="2 solid blue-800" bg="blue-800/20" rounded-lg p-4><div class="text-lg font-bold text-blue-300">Type II (β)</div><div class="text-xs opacity-75">missed improvement</div></div>
</div>
</div>
</div>

<!--
Before drawing the picture on the next slide, state the logic in words. A significance test is a decision rule: we decide in advance that if the observed gap is larger than some cutoff, the critical value, we will call it significant and declare a winner. Otherwise we make no claim.

Any rule like this can fail in two ways, and the table lays out all four combinations of reality and decision. Reality is either that the models are equal (H₀ true) or that B is genuinely better (H₀ false). Our decision is either to reject H₀ or not. Two cells are correct. If H₀ is true and we reject it, that is a Type I error, a false alarm. If H₀ is false and we fail to reject it, that is a Type II error, a missed improvement. The bottom-left cell, rejecting a false H₀, is the good outcome whose probability is called power.

Both errors are produced by the same cutoff. Raise it and false alarms become rarer but real improvements are missed more often; lower it and the reverse happens. So moving the cutoff only trades one error for the other.

The standard practice is to choose α first, the false-alarm rate we are willing to accept, usually 0.05. That choice determines the critical value; we do not search for a good cutoff in the data. Power then follows from the cutoff, the size of the true gap, and the noise in the measurement. The only way to reduce both errors together is to reduce the noise, which means a larger test set. The next slide shows this picture, and a later slide quantifies how much data is needed.
-->

---
glowSeed: 5522
---

# Type I and Type II Errors, Graphically

<div class="grid grid-cols-2 gap-8 items-start">
<div>
<div class="space-y-3 mt-2">
<div v-click border="2 solid red-800" bg="red-800/20" rounded-lg px-4 py-3>
<span class="font-bold text-red-300">Type I error (α)</span>
<span class="text-sm opacity-85"> — Declare a winner when the models are truly equal. A false alarm; we fix α, usually 0.05.</span>
</div>
<div v-click border="2 solid blue-800" bg="blue-800/20" rounded-lg px-4 py-3>
<span class="font-bold text-blue-300">Type II error (β)</span>
<span class="text-sm opacity-85"> — Miss a real improvement because the test set was too noisy to show it.</span>
</div>
<div v-click border="2 solid teal-800" bg="teal-800/20" rounded-lg px-4 py-3>
<span class="font-bold text-teal-300">Power = 1 − β</span>
<span class="text-sm opacity-85"> — The chance a test detects a gap that is really there. Aim for 80% or more.</span>
</div>
</div>
</div>
<div class="mt-10">
<TypeErrorsSvg :step="$clicks" />
</div>
</div>

<!--
Every test can fail in two directions. A Type I error, controlled by the significance level α, is a false alarm: the models are equal but the sampled test set happened to produce a gap at least as extreme as the one we saw, so we reject H₀. By choosing α = 0.05 we accept being fooled about one time in twenty when nothing is going on — that is the small red tail of the grey null curve in the picture.

A Type II error, probability β, is the opposite: the improvement is real, so the true gap sits where the teal curve is centered, but our measurement is noisy enough that the observed gap often lands to the left of the critical value and we fail to reject. The blue region is that mass. Power is the remaining teal area to the right of the critical line, the probability that we do detect the improvement.

The takeaway for this module: a non-significant result is only informative if the test had enough power to see a gap of the size you care about. The picture also shows the lever you actually control — a bigger test set makes both curves narrower, which separates them and raises power without changing α. The next section of the deck quantifies exactly how much data that takes.
-->

---
glowSeed: 553
---

# McNemar's Test Uses Paired Disagreements

<div class="grid grid-cols-2 gap-8 items-start">
<div>
<div class="space-y-3 mt-4">
<div v-click border="2 solid white/5" bg="white/5" rounded-lg px-4 py-3>
<span class="font-bold text-teal-300">Same test examples</span>
<span class="text-sm opacity-85"> — Each row has predictions from A and B on the identical case, so their errors are correlated.</span>
</div>
<div v-click border="2 solid white/5" bg="white/5" rounded-lg px-4 py-3>
<span class="font-bold text-blue-300">Only discordant cells matter</span>
<span class="text-sm opacity-85"> — n₀₁ = A wrong / B right; n₁₀ = A right / B wrong.</span>
</div>
<div v-click border="2 solid white/5" bg="white/5" rounded-lg px-4 py-3>
<span class="font-bold text-amber-300">Ignore agreements</span>
<span class="text-sm opacity-85"> — Both-right (n₁₁) and both-wrong (n₀₀) add no noise to the gap and do not distinguish the models.</span>
</div>
<div border="2 solid red-800" bg="red-800/20" rounded-lg px-4 py-3 class="text-sm">
<div><span class="font-bold text-red-300">n₀₁</span>: Only model B got it right</div>
<div><span class="font-bold text-red-300">n₁₀</span>: Only model A got it right</div>
</div>
</div>
</div>
<div>
<div role="img" aria-label="McNemar agreement table: rows model A correct or wrong, columns model B correct or wrong, cells n11 n10 n01 n00" class="mt-4 max-w-lg mx-auto">
<div class="grid grid-cols-[6.5rem_1fr_1fr] gap-2 text-center text-xs">
<div></div><div class="font-bold text-blue-300">B correct</div><div class="font-bold text-blue-300">B wrong</div>
<div class="flex items-center justify-end pr-2 font-bold text-teal-300">A correct</div><div border="2 solid white/10" bg="white/5" rounded-lg p-4><div class="text-lg font-bold">n₁₁</div><div class="text-xs opacity-60">both right</div></div><div border="2 solid red-800" bg="red-800/20" rounded-lg p-4><div class="text-lg font-bold">n₁₀</div><div class="text-xs opacity-60">A only</div></div>
<div class="flex items-center justify-end pr-2 font-bold text-teal-300">A wrong</div><div border="2 solid red-800" bg="red-800/20" rounded-lg p-4><div class="text-lg font-bold">n₀₁</div><div class="text-xs opacity-60">B only</div></div><div border="2 solid white/10" bg="white/5" rounded-lg p-4><div class="text-lg font-bold">n₀₀</div><div class="text-xs opacity-60">both wrong</div></div>
</div>
</div>
<div v-click class="mt-4" style="font-size: .9em" border="2 solid teal-800" bg="teal-800/20" rounded-lg px-4 py-3>

$$
\chi^2=\frac{(|n_{01}-n_{10}|-1)^2}{n_{01}+n_{10}}
$$

</div>
<div v-click class="mt-3 text-sm" border="2 solid amber-800" bg="amber-800/20" rounded-lg px-4 py-3>
<span class="font-bold text-amber-300">Decision rule</span> — Reject H₀ if χ² &gt; 3.84 (= 1.96², the critical value for α = 0.05). If the models are equal, this false alarm happens only 5% of the time.
</div>
</div>
</div>

<!--
This table is a genuinely different object from the confusion matrix in the previous deck: that matrix cross-tabulated actual label against predicted label for one model; this one cross-tabulates model A's correctness against model B's correctness on the same set of test examples, so it says nothing about which class each example belongs to, only about which model got which examples right. n₁₁ is examples both models got right; n₀₀ is examples both got wrong; these two "agreement" cells carry no information about which model is better, because they happen regardless of any real skill difference. The action is entirely in the two discordant cells: n₁₀ is examples A got right and B got wrong (evidence for A), n₀₁ is examples A got wrong and B got right (evidence for B).

The last card ties McNemar back to the decision rule from the previous two slides: the critical value 3.84 is 1.96 squared, so rejecting when χ² exceeds 3.84 is the same as rejecting when the gap is more than 1.96 standard errors from zero, which gives a Type I error rate of 5%. McNemar's test asks: under H₀ (the two models are equally likely to be the one that's right when they disagree), n₀₁ and n₁₀ should each be about half of the total disagreements n₀₁+n₁₀. The χ² statistic formalizes that: (|n₀₁ − n₁₀| − 1)² in the numerator measures the squared imbalance between the two discordant counts (the −1 is a continuity correction, since a discrete count is being approximated by a continuous χ² distribution), divided by n₀₁+n₁₀, the total number of disagreements, which sets the scale of noise you'd expect from that many coin flips. This statistic follows a χ² distribution with 1 degree of freedom under H₀, so a p-value follows immediately by comparing against that reference distribution. Next slide works this out with real numbers.

McNemar's test reduces each prediction to correct or incorrect, so it tests an accuracy-like question. It does not directly test a difference in AUC, F1, calibration, or application-specific cost. Those quantities need uncertainty procedures designed for the metric itself.
-->

---
glowSeed: 554.5
---

# What Does McNemar’s χ² Measure?

<div class="flex items-center gap-5 mt-2 mb-1">
  <div class="rounded-lg border border-white/10 bg-white/5 px-4 py-2 whitespace-nowrap">

$\chi^2=\dfrac{(|n_{01}-n_{10}|-1)^2}{n_{01}+n_{10}}$

</div>
  <div class="rounded-lg border border-teal-800 bg-teal-800/20 px-4 py-2 text-sm"><span class="font-bold text-teal-200">In words:</span> χ² measures how far the two models’ wins among disagreements depart from an equal split.</div>
</div>
<div class="text-sm opacity-75 mb-0">Height is χ²; the white line marks equal wins; above the amber plane (χ² = 3.84) we reject H₀. Drag to rotate.</div>
<div style="height: 400px; margin-top: -40px">
<McNemarSurface />
</div>

<!--
The horizontal axes are the two kinds of paired disagreement: n₀₁ counts cases B gets right that A misses; n₁₀ counts cases A gets right that B misses. The statistic is small along the highlighted valley, where the models win about equally often. Moving away from the valley means the split becomes more imbalanced; increasing the total number of disagreements makes that imbalance stronger evidence against the equal-performance null. The height is the continuity-corrected χ² value, which is compared with a chi-squared distribution with one degree of freedom to obtain a p-value. The displayed ranges are 0 to 30 for each count.
-->

---
glowSeed: 554
---

# Worked Example: McNemar's Test

<div class="grid grid-cols-2 gap-6 items-start">
<div>
<div role="img" aria-label="McNemar table with n11 400, n10 8, n01 22, n00 70" class="mt-2 max-w-md mx-auto">
<div class="grid grid-cols-[6rem_1fr_1fr] gap-2 text-center text-xs">
<div></div><div class="font-bold text-blue-300">B correct</div><div class="font-bold text-blue-300">B wrong</div>
<div class="flex items-center justify-end pr-1 font-bold text-teal-300">A correct</div><div border="2 solid white/10" bg="white/5" rounded-lg p-4><div class="text-lg font-bold">400</div></div><div border="2 solid red-800" bg="red-800/20" rounded-lg p-4><div class="text-lg font-bold">8</div></div>
<div class="flex items-center justify-end pr-1 font-bold text-teal-300">A wrong</div><div border="2 solid red-800" bg="red-800/20" rounded-lg p-4><div class="text-lg font-bold">22</div></div><div border="2 solid white/10" bg="white/5" rounded-lg p-4><div class="text-lg font-bold">70</div></div>
</div>
</div>
<div class="text-xs opacity-75 mt-3">500 shared test examples. B corrects 22 cases A misses; A corrects only 8 cases B misses.</div>
<svg role="img" aria-label="Bell curve of the gap in standard errors under the null hypothesis. Dashed lines mark the critical values at plus and minus 1.96 and the observed value at plus and minus 2.37. The tiny tails beyond 2.37 are shaded and labeled p about 0.018." viewBox="0 0 540 205" class="w-full mt-1">
  <line x1="30" y1="150" x2="510" y2="150" stroke="#64748b" stroke-width="2"/>
  <path d="M30.0 150.0 L34.0 150.0 L38.0 149.9 L42.0 149.9 L46.0 149.9 L50.0 149.9 L54.0 149.8 L58.0 149.8 L62.0 149.7 L66.0 149.7 L70.0 149.6 L74.0 149.5 L78.0 149.3 L82.0 149.2 L86.0 149.0 L90.0 148.8 L94.0 148.5 L98.0 148.2 L102.0 147.8 L106.0 147.4 L110.0 146.9 L114.0 146.3 L118.0 145.6 L122.0 144.7 L126.0 143.8 L130.0 142.8 L134.0 141.6 L138.0 140.2 L142.0 138.7 L146.0 137.0 L150.0 135.1 L154.0 133.0 L158.0 130.7 L162.0 128.2 L166.0 125.5 L170.0 122.6 L174.0 119.4 L178.0 116.0 L182.0 112.5 L186.0 108.7 L190.0 104.8 L194.0 100.7 L198.0 96.5 L202.0 92.1 L206.0 87.7 L210.0 83.3 L214.0 78.8 L218.0 74.4 L222.0 70.1 L226.0 65.9 L230.0 61.9 L234.0 58.1 L238.0 54.6 L242.0 51.3 L246.0 48.5 L250.0 45.9 L254.0 43.8 L258.0 42.2 L262.0 41.0 L266.0 40.2 L270.0 40.0 L274.0 40.2 L278.0 41.0 L282.0 42.2 L286.0 43.8 L290.0 45.9 L294.0 48.5 L298.0 51.3 L302.0 54.6 L306.0 58.1 L310.0 61.9 L314.0 65.9 L318.0 70.1 L322.0 74.4 L326.0 78.8 L330.0 83.3 L334.0 87.7 L338.0 92.1 L342.0 96.5 L346.0 100.7 L350.0 104.8 L354.0 108.7 L358.0 112.5 L362.0 116.0 L366.0 119.4 L370.0 122.6 L374.0 125.5 L378.0 128.2 L382.0 130.7 L386.0 133.0 L390.0 135.1 L394.0 137.0 L398.0 138.7 L402.0 140.2 L406.0 141.6 L410.0 142.8 L414.0 143.8 L418.0 144.7 L422.0 145.6 L426.0 146.3 L430.0 146.9 L434.0 147.4 L438.0 147.8 L442.0 148.2 L446.0 148.5 L450.0 148.8 L454.0 149.0 L458.0 149.2 L462.0 149.3 L466.0 149.5 L470.0 149.6 L474.0 149.7 L478.0 149.7 L482.0 149.8 L486.0 149.8 L490.0 149.9 L494.0 149.9 L498.0 149.9 L502.0 149.9 L506.0 150.0 L510.0 150.0" fill="none" stroke="#2dd4bf" stroke-width="3"/>
  <g fill="#cbd5e1" style="font-size:12px" text-anchor="middle">
    <text x="90" y="166">−3</text><text x="270" y="166">0</text><text x="450" y="166">+3</text>
    <text x="270" y="186" fill="#e2e8f0" style="font-size:13px">gap size in standard errors (z)</text>
  </g>
  <text x="270" y="30" fill="#5eead4" text-anchor="middle" style="font-size:14px;font-weight:700">H₀</text>
  <g v-click="1">
    <line x1="412" y1="60" x2="412" y2="150" stroke="#f59e0b" stroke-width="2.5" stroke-dasharray="6 5"/>
    <line x1="128" y1="60" x2="128" y2="150" stroke="#f59e0b" stroke-width="2.5" stroke-dasharray="6 5"/>
    <text x="418" y="66" fill="#fbbf24" style="font-size:12px">observed z = 2.37</text>
  </g>
  <g v-click="2">
    <path d="M412.4 150 L412.4 143.4 L414.8 144.0 L417.2 144.6 L419.7 145.1 L422.1 145.6 L424.6 146.0 L427.0 146.4 L429.5 146.8 L431.9 147.1 L434.3 147.4 L436.8 147.7 L439.2 147.9 L441.7 148.2 L444.1 148.4 L446.5 148.5 L449.0 148.7 L451.4 148.9 L453.9 149.0 L456.3 149.1 L458.7 149.2 L461.2 149.3 L463.6 149.4 L466.1 149.5 L468.5 149.5 L470.9 149.6 L473.4 149.6 L475.8 149.7 L478.3 149.7 L480.7 149.8 L483.2 149.8 L485.6 149.8 L488.0 149.9 L490.5 149.9 L492.9 149.9 L495.4 149.9 L497.8 149.9 L500.2 149.9 L502.7 149.9 L505.1 149.9 L507.6 150.0 L510.0 150.0 L510.0 150 Z" fill="#fbbf24" fill-opacity=".8"/><path d="M30.0 150 L30.0 150.0 L32.4 150.0 L34.9 149.9 L37.3 149.9 L39.8 149.9 L42.2 149.9 L44.6 149.9 L47.1 149.9 L49.5 149.9 L52.0 149.9 L54.4 149.8 L56.8 149.8 L59.3 149.8 L61.7 149.7 L64.2 149.7 L66.6 149.6 L69.1 149.6 L71.5 149.5 L73.9 149.5 L76.4 149.4 L78.8 149.3 L81.3 149.2 L83.7 149.1 L86.1 149.0 L88.6 148.9 L91.0 148.7 L93.5 148.5 L95.9 148.4 L98.3 148.2 L100.8 147.9 L103.2 147.7 L105.7 147.4 L108.1 147.1 L110.5 146.8 L113.0 146.4 L115.4 146.0 L117.9 145.6 L120.3 145.1 L122.8 144.6 L125.2 144.0 L127.6 143.4 L127.6 150 Z" fill="#fbbf24" fill-opacity=".8"/>
    <text x="422" y="132" fill="#fbbf24" style="font-size:14px;font-weight:700">p ≈ 0.018</text>
    <text x="422" y="146" fill="#fbbf24" style="font-size:11px">(both tails)</text>
  </g>
  <g v-click="3">
    <line x1="388" y1="90" x2="388" y2="150" stroke="#94a3b8" stroke-width="2" stroke-dasharray="3 4"/>
    <line x1="152" y1="90" x2="152" y2="150" stroke="#94a3b8" stroke-width="2" stroke-dasharray="3 4"/>
    <text x="382" y="100" fill="#cbd5e1" text-anchor="end" style="font-size:12px">critical ±1.96</text>
  </g>
</svg>
</div>
<div>
<div class="space-y-2 mt-1" style="font-size: .85em">
<div v-click="1" border="2 solid white/5" bg="white/5" rounded-lg px-4 py-1>
<span class="font-bold text-blue-300">1 · The statistic</span><span class="text-xs opacity-85"> — from n₀₁ = 22 and n₁₀ = 8</span>

$$
\chi^2=\frac{(|22-8|-1)^2}{22+8}=\frac{169}{30}=5.63
$$

<div class="text-xs opacity-85 pb-1">z = √5.63 ≈ 2.37 standard errors from zero.</div>
</div>
<div v-click="2" border="2 solid white/5" bg="white/5" rounded-lg px-4 py-2>
<span class="font-bold text-amber-300">2 · The p-value is a tail area</span><span class="text-xs opacity-85"> — If the models were equal, how often would the gap be 2.37 SEs or more from zero, in either direction? The shaded tails: p ≈ 0.018.</span>
</div>
<div v-click="3" border="2 solid teal-800" bg="teal-800/20" rounded-lg px-4 py-2>
<span class="font-bold text-teal-200">3 · The decision</span><span class="text-xs opacity-85"> — 5.63 &gt; 3.84 (z beyond ±1.96): reject H₀ at α = 0.05, with only a 5% false-alarm rate.</span>
</div>
<div v-click="4" border="2 solid white/5" bg="white/5" rounded-lg px-4 py-2>
<span class="font-bold text-violet-300">Sanity check</span><span class="text-xs opacity-85"> — If the models were equal, the 30 disagreements are fair coin flips; 22+ B-wins (or ≤ 8) has exact probability ≈ 0.016.</span>
</div>
</div>
</div>
</div>

<!--
On the χ² scale, the p-value is the tail beyond 5.63 of a chi-squared distribution with 1 degree of freedom (the distribution of one squared standard normal, which is why it matches the two normal tails). The key to reading the result is the picture: the bell curve is the distribution of the gap in standard errors if H₀ is true, the p-value is the area in the shaded tails beyond the observed z, and the decision rule compares the observed value with the critical value 1.96 (3.84 on the χ² scale). Plug the discordant counts from this table into the formula from the previous slide: n₀₁ = 22 (B right, A wrong) and n₁₀ = 8 (A right, B wrong), so χ² = (|22−8|−1)² / (22+8) = 13² / 30 = 169/30 ≈ 5.63. Comparing that to a χ² distribution with 1 degree of freedom gives p ≈ 0.018 — verified directly against scipy.stats.chi2. Because 22+8 = 30 is a fairly small number of disagreements, it is worth cross-checking with the exact test: under H₀, n₀₁ should be Binomial(n₀₁+n₁₀, 0.5) = Binomial(30, 0.5), and the exact two-sided binomial test on observing 22 (or fewer than 8, the symmetric tail) gives p ≈ 0.016 — close to the χ² approximation and confirming the same conclusion. As a rule of thumb, prefer the exact binomial test over the χ² approximation whenever the number of discordant pairs is small, roughly under 25, since the χ² approximation can be unreliable in that regime; here they happen to agree closely.

Both p-values are below the conventional 0.05 threshold, so we reject H₀: it is unlikely that models A and B are truly equally good and this 22-vs-8 split in their disagreements arose by chance alone. Practically, this means model B's advantage over model A, observed on these 500 shared test examples, is probably a real difference in skill and not sampling noise — though remember from the previous slide that "statistically significant" is a claim about surprise under H₀, not a guarantee about the true size of the gap or whether that gap is large enough to matter operationally, which is exactly the distinction the "statistical vs. practical significance" slide later in this deck will sharpen.
-->

---
glowSeed: 5541
---

# How Much Test Data Do You Need?

<div class="grid grid-cols-2 gap-8 items-start">
<div>
<div class="mt-1" style="font-size: .85em" border="2 solid teal-800" bg="teal-800/20" rounded-lg px-4 py-2>

$$
n\approx\frac{7.84\,q}{\delta^{2}}
$$

<div class="text-xs opacity-80 -mt-2">80% power, α = 0.05 · q = disagreement rate · δ = accuracy gap</div>
</div>
<div class="space-y-2 mt-3">
<div v-click border="2 solid white/5" bg="white/5" rounded-lg px-4 py-2><span class="font-bold text-teal-300">5-point gap</span><span class="text-sm opacity-85"> — about 310 examples</span></div>
<div v-click border="2 solid white/5" bg="white/5" rounded-lg px-4 py-2><span class="font-bold text-blue-300">3-point gap</span><span class="text-sm opacity-85"> — about 870 examples</span></div>
<div v-click border="2 solid white/5" bg="white/5" rounded-lg px-4 py-2><span class="font-bold text-violet-300">2-point gap</span><span class="text-sm opacity-85"> — about 1,960 examples</span></div>
<div v-click border="2 solid white/5" bg="white/5" rounded-lg px-4 py-2><span class="font-bold text-amber-300">1-point gap</span><span class="text-sm opacity-85"> — about 7,840 examples</span></div>
</div>
</div>
<div style="height: 350px">
<PowerCurve :step="$clicks" />
</div>
</div>

<!--
This is the planning-side companion to McNemar's test. For a paired comparison, only the disagreements carry information, so the sample size you need depends on two quantities: δ, the accuracy gap you want to detect, and q, the fraction of test examples on which the two models disagree. Under H₁ the McNemar z-statistic is centered near δ·√(n/q), so power is approximately Φ(δ√(n/q) − 1.96). Setting power to 80% gives the rule of thumb n ≈ 7.84·q/δ².

The chart uses q = 10%, a plausible figure for two reasonably similar classifiers. Reveal the curves one at a time. A 5-point gap is detected reliably with a few hundred examples. A 3-point gap needs a bit under a thousand. A 2-point gap needs about two thousand. A 1-point gap needs nearly eight thousand, because n grows with the inverse square of the gap: halve the gap and you need four times the data.

Two practical points. First, if q is smaller — the models are very similar — you need fewer examples, because there is less disagreement noise; estimate q from a pilot run. Second, this is why a small validation set can never settle a one-point difference: the experiment simply cannot see it, and a non-significant result there says nothing about whether the difference exists.
-->

---
glowSeed: 555
---

# Comparisons Across Cross-Validation Runs

<div class="grid grid-cols-2 gap-8 items-start">
<div>
<div class="space-y-3 mt-4">
<div v-click border="2 solid white/5" bg="white/5" rounded-lg px-4 py-3>
<span class="font-bold text-teal-300">Use the same splits</span>
<span class="text-sm opacity-85"> — Both models must face the same training and validation partitions.</span>
</div>
<div v-click border="2 solid white/5" bg="white/5" rounded-lg px-4 py-3>
<span class="font-bold text-blue-300">Repeat the experiment</span>
<span class="text-sm opacity-85"> — Repeated CV measures how the performance gap changes across several partitions.</span>
</div>
<div v-click border="2 solid white/5" bg="white/5" rounded-lg px-4 py-3>
<span class="font-bold text-amber-300">Account for dependence</span>
<span class="text-sm opacity-85"> — Scores from ordinary k-fold CV are correlated because their training sets overlap.</span>
</div>
</div>
</div>
<div>
<div v-click class="mt-4" style="font-size: .9em" border="2 solid teal-800" bg="teal-800/20" rounded-lg px-4 py-3>

$$
d_{r,f}=\mathrm{score}_{A,r,f}-\mathrm{score}_{B,r,f}
$$

</div>
<div v-click class="mt-3 text-xs opacity-75">
Use a corrected resampled test, a 5×2cv paired test, or a paired bootstrap suited to the metric and evaluation design.
</div>
</div>
</div>

<!--
When models are compared through cross-validation, keep the splits paired: model A and model B should use the same rows in every training and validation partition. Repeating cross-validation with several random partitions provides more information about how stable the gap is than a single k-fold run.

Do not apply an ordinary paired t-test to the k fold scores as though they were independent observations. Their training sets overlap, so the differences are correlated and the usual standard error is too small. Methods such as the corrected resampled t-test and the 5×2cv paired test explicitly address this design. A paired bootstrap can estimate uncertainty when predictions can be resampled in a way that respects the data structure. The correct method depends on what is being estimated and whether observations are independent, grouped, or ordered in time.
-->

---
glowSeed: 5551
---

# Bootstrap the Performance Difference

<div class="grid grid-cols-2 gap-8 items-start">
<div>
<div class="space-y-3 mt-4">
<div v-click border="2 solid white/5" bg="white/5" rounded-lg px-4 py-3><span class="font-bold text-teal-300">Resample cases</span><span class="text-sm opacity-85"> — Draw test observations with replacement and keep both models' predictions paired.</span></div>
<div v-click border="2 solid white/5" bg="white/5" rounded-lg px-4 py-3><span class="font-bold text-blue-300">Recompute the gap</span><span class="text-sm opacity-85"> — Calculate accuracy, recall, AUC, or another metric for both models in each resample.</span></div>
<div v-click border="2 solid white/5" bg="white/5" rounded-lg px-4 py-3><span class="font-bold text-amber-300">Read the interval</span><span class="text-sm opacity-85"> — The bootstrap distribution shows plausible values and the stability of the improvement.</span></div>
</div>
</div>
<div>
<div v-click class="mt-5" border="2 solid teal-800" bg="teal-800/20" rounded-lg px-4 py-3>

$$
\Delta_b=M_A(D_b)-M_B(D_b),\quad b=1,\ldots,B
$$

</div>
<div v-click class="mt-4 text-sm opacity-85">A percentile interval uses the 2.5th and 97.5th percentiles of the bootstrap gaps for an approximate 95% interval.</div>
</div>
</div>

<!--
The paired bootstrap turns the recommendation to report an interval into a concrete procedure. Sample test observations with replacement. For every bootstrap sample, keep each observation's true label and both models' predictions together, then recompute the metric difference. The resulting distribution describes how much the observed gap changes under resampling.

This basic case bootstrap assumes observations are exchangeable. If several rows belong to the same patient or user, resample whole groups. For time series, use a time-aware block method rather than shuffling individual rows. Bootstrap intervals complement effect sizes; they do not repair a biased test set or a model selected on that same test set.
-->

---
glowSeed: 5552
---

# Choosing the Right Test

<div class="space-y-3 mt-4 text-sm">
<div v-click class="grid grid-cols-[1fr_3rem_1fr] items-center gap-2">
<div border="2 solid white/5" bg="white/5" rounded-lg px-4 py-3><span class="font-bold text-teal-300">One test set, right/wrong labels</span><div class="opacity-80 text-xs mt-1">Two classifiers scored on the same examples</div></div>
<svg viewBox="0 0 48 24" class="w-full" aria-hidden="true"><path d="M2 12H38M30 4l10 8-10 8" fill="none" stroke="#2dd4bf" stroke-width="3" stroke-linecap="round" stroke-linejoin="round"/></svg>
<div border="2 solid teal-800" bg="teal-800/20" rounded-lg px-4 py-3><span class="font-bold text-teal-200">McNemar's test</span><div class="opacity-80 text-xs mt-1">Exact binomial when disagreements are few (&lt; 25)</div></div>
</div>
<div v-click class="grid grid-cols-[1fr_3rem_1fr] items-center gap-2">
<div border="2 solid white/5" bg="white/5" rounded-lg px-4 py-3><span class="font-bold text-blue-300">One test set, continuous scores</span><div class="opacity-80 text-xs mt-1">Per-example loss, squared error, log-loss</div></div>
<svg viewBox="0 0 48 24" class="w-full" aria-hidden="true"><path d="M2 12H38M30 4l10 8-10 8" fill="none" stroke="#60a5fa" stroke-width="3" stroke-linecap="round" stroke-linejoin="round"/></svg>
<div border="2 solid blue-800" bg="blue-800/20" rounded-lg px-4 py-3><span class="font-bold text-blue-200">Paired t-test, Wilcoxon, or paired bootstrap</span><div class="opacity-80 text-xs mt-1">Bootstrap for AUC, F1 and other non-additive metrics</div></div>
</div>
<div v-click class="grid grid-cols-[1fr_3rem_1fr] items-center gap-2">
<div border="2 solid white/5" bg="white/5" rounded-lg px-4 py-3><span class="font-bold text-violet-300">Scores from repeated CV</span><div class="opacity-80 text-xs mt-1">Shared splits, overlapping training sets</div></div>
<svg viewBox="0 0 48 24" class="w-full" aria-hidden="true"><path d="M2 12H38M30 4l10 8-10 8" fill="none" stroke="#a78bfa" stroke-width="3" stroke-linecap="round" stroke-linejoin="round"/></svg>
<div border="2 solid violet-800" bg="violet-800/20" rounded-lg px-4 py-3><span class="font-bold text-violet-200">Corrected resampled t-test or 5×2cv</span><div class="opacity-80 text-xs mt-1">Not the plain paired t-test on fold scores</div></div>
</div>
<div v-click class="grid grid-cols-[1fr_3rem_1fr] items-center gap-2">
<div border="2 solid white/5" bg="white/5" rounded-lg px-4 py-3><span class="font-bold text-amber-300">Many datasets, one score each</span><div class="opacity-80 text-xs mt-1">Does model A win across problems?</div></div>
<svg viewBox="0 0 48 24" class="w-full" aria-hidden="true"><path d="M2 12H38M30 4l10 8-10 8" fill="none" stroke="#fbbf24" stroke-width="3" stroke-linecap="round" stroke-linejoin="round"/></svg>
<div border="2 solid amber-800" bg="amber-800/20" rounded-lg px-4 py-3><span class="font-bold text-amber-200">Wilcoxon signed-rank (2 models) or Friedman (3+)</span><div class="opacity-80 text-xs mt-1">Treats each dataset as one observation</div></div>
</div>
</div>

<!--
Use this slide as a lookup table. The test you choose should match what you actually measured and how the measurements depend on each other.

If you have right-or-wrong labels for two classifiers on one shared test set, McNemar's test is the standard choice, with the exact binomial version when there are fewer than about twenty-five disagreements. If you have continuous per-example quantities such as squared error, take the per-example differences and use a paired t-test when they look roughly normal, the Wilcoxon signed-rank test when they do not, or a paired bootstrap. The bootstrap is also the practical route for metrics like AUC and F1, which are not simple averages of per-example terms.

For scores from repeated cross-validation, remember the earlier warning: the training sets overlap, so use a corrected resampled t-test or the 5×2cv test rather than treating folds as independent. Finally, when the unit of analysis is a dataset — one benchmark score per problem — use the Wilcoxon signed-rank test for two models or Friedman's test with a post-hoc procedure for three or more. These are the recommendations from Demšar's widely cited 2006 comparison paper. In every row the common thread is the same: pair the measurements, and make the test's independence assumption match reality.
-->

---
glowSeed: 556
---

# Statistical vs. Practical Significance

<div class="grid grid-cols-3 gap-4 mt-6">
<div v-click border="2 solid teal-800" bg="teal-800/20" rounded-lg p-4>
<div class="font-bold text-teal-300 mb-2">Statistically significant</div>
<div class="text-sm leading-relaxed opacity-90">The observed effect is unlikely under the null model — a claim about surprise, not size.</div>
</div>
<div v-click border="2 solid blue-800" bg="blue-800/20" rounded-lg p-4>
<div class="font-bold text-blue-300 mb-2">Practically meaningful</div>
<div class="text-sm leading-relaxed opacity-90">The effect is large enough to justify added complexity, cost, latency, or risk.</div>
</div>
<div v-click border="2 solid amber-800" bg="amber-800/20" rounded-lg p-4>
<div class="font-bold text-amber-300 mb-2">Report both</div>
<div class="text-sm leading-relaxed opacity-90">Give the effect size and an interval, not only a p-value.</div>
</div>
</div>


<!--
A p-value answers "how surprising is this gap if the models were truly equal," and nothing more — it does not tell you how big the gap is. With enough test examples, an utterly trivial improvement, say 0.1 percentage points of accuracy, can produce a tiny p-value and get flagged "statistically significant," because sample size shrinks the standard error in the denominator of any test statistic, making even minuscule effects detectable. This is the flip side of the small-sample caveat from earlier slides: small samples make real effects hard to detect; large samples make tiny, worthless effects easy to detect.

So statistical significance and practical significance are separate questions that both need answering. Statistical significance asks whether the gap is probably real. Practical significance asks whether the gap is big enough to be worth acting on — worth the added training cost, the added inference latency, the added maintenance burden of a more complex model, or the risk of deploying something new. A model that is "significantly" better by 0.1% accuracy at ten times the inference cost is very likely not worth shipping. The professional habit that follows: never report a p-value alone; report the effect size (the actual measured gap) and, where possible, a confidence interval around it, so a reader can judge both questions — is this real, and does it matter — for themselves.
-->

---
glowSeed: 5561
---

# Reading an Interval: Significant, Meaningful, or Both?

<div class="mt-2">
<svg role="img" aria-label="Forest plot of four accuracy-gap confidence intervals against a zero line and a shaded region marking practically meaningful gaps of one point or more" viewBox="0 0 760 360" class="w-full max-w-4xl mx-auto">
  <rect x="510" y="30" width="210" height="260" fill="#2dd4bf" fill-opacity=".10"/>
  <text x="615.0" y="22" fill="#5eead4" text-anchor="middle" style="font-size:14px">practically meaningful (≥ +1 pt)</text>
  <line x1="300" y1="296" x2="720" y2="296" stroke="#64748b" stroke-width="2"/>
  <line x1="440" y1="40" x2="440" y2="296" stroke="#e2e8f0" stroke-width="2.5" stroke-dasharray="6 5"/>
  <g fill="#cbd5e1" style="font-size:14px" text-anchor="middle"><text x="300" y="318">−2</text><text x="370" y="318">−1</text><text x="440" y="318">0</text><text x="510" y="318">+1</text><text x="580" y="318">+2</text><text x="650" y="318">+3</text><text x="720" y="318">+4</text>
    <text x="510.0" y="346" fill="#e2e8f0">accuracy gap, B − A (percentage points), with 95% CI</text>
  </g>
  <g v-click>
    <text x="8" y="77" fill="#fbbf24" style="font-size:17px;font-weight:700">Inconclusive</text>
    <text x="8" y="96" fill="#cbd5e1" style="font-size:13px">includes 0 and meaningful gaps</text>
    <line x1="384" y1="80" x2="622" y2="80" stroke="#fbbf24" stroke-width="5" stroke-linecap="round"/>
    <circle cx="503" cy="80" r="8" fill="#fbbf24"/>
  </g>
  <g v-click>
    <text x="8" y="137" fill="#60a5fa" style="font-size:17px;font-weight:700">Significant, but trivial</text>
    <text x="8" y="156" fill="#cbd5e1" style="font-size:13px">excludes 0, stays below +1</text>
    <line x1="454" y1="140" x2="482" y2="140" stroke="#60a5fa" stroke-width="5" stroke-linecap="round"/>
    <circle cx="468" cy="140" r="8" fill="#60a5fa"/>
  </g>
  <g v-click>
    <text x="8" y="197" fill="#2dd4bf" style="font-size:17px;font-weight:700">Significant and meaningful</text>
    <text x="8" y="216" fill="#cbd5e1" style="font-size:13px">worth acting on</text>
    <line x1="545" y1="200" x2="671" y2="200" stroke="#2dd4bf" stroke-width="5" stroke-linecap="round"/>
    <circle cx="608" cy="200" r="8" fill="#2dd4bf"/>
  </g>
  <g v-click>
    <text x="8" y="257" fill="#a78bfa" style="font-size:17px;font-weight:700">Tight around zero</text>
    <text x="8" y="276" fill="#cbd5e1" style="font-size:13px">evidence of no meaningful gap</text>
    <line x1="412" y1="260" x2="468" y2="260" stroke="#a78bfa" stroke-width="5" stroke-linecap="round"/>
    <circle cx="440" cy="260" r="8" fill="#a78bfa"/>
  </g>
</svg>
</div>

<!--
Here is the practical summary of the last two slides in one picture. Each row is an observed accuracy gap with its 95% confidence interval. The dashed white line is zero, and the shaded teal band is a threshold you choose in advance: the smallest gap that would justify switching models, which I have set at one point for illustration.

Reveal the rows one at a time. The amber interval crosses zero but also extends well into the meaningful band — the data cannot tell us whether the models are equal or whether B is meaningfully better; this is a power problem, not a verdict, and the fix is more data. The blue interval excludes zero, so it is statistically significant, but even its upper end stays below the meaningful threshold; this is the classic large-test-set outcome where a real but trivial gain is not worth shipping. The teal interval excludes zero and lies inside the band, the only case where both kinds of significance agree.

The violet interval is the subtle one. It is not significant, yet it is not 'no evidence' either: its narrow width, wholly inside plus-or-minus half a point, positively supports the claim that any difference is too small to matter. Absence of significance with a wide interval is ambiguity; with a tight interval it is informative. Reporting the interval makes all four cases distinguishable, whereas a bare p-value would lump the amber and violet rows together.
-->

---
glowSeed: 5571
---

# The Multiple-Comparisons Trap

<div class="grid grid-cols-2 gap-8 items-start">
<div>
<div class="mt-1" style="font-size: .85em" border="2 solid red-800" bg="red-800/20" rounded-lg px-4 py-2>

$$
\Pr(\text{≥1 false win})=1-(1-\alpha)^m
$$

</div>
<div class="space-y-2 mt-3">
<div v-click border="2 solid white/5" bg="white/5" rounded-lg px-4 py-2><span class="font-bold text-amber-300">20 comparisons</span><span class="text-sm opacity-85"> — a 64% chance that at least one "significant" win is pure luck.</span></div>
<div v-click border="2 solid white/5" bg="white/5" rounded-lg px-4 py-2><span class="font-bold text-teal-300">Bonferroni</span><span class="text-sm opacity-85"> — test each at α/m. Simple and safe, but conservative.</span></div>
<div v-click border="2 solid white/5" bg="white/5" rounded-lg px-4 py-2><span class="font-bold text-blue-300">Holm</span><span class="text-sm opacity-85"> — step-down version with the same guarantee and more power; prefer it.</span></div>
</div>
</div>
<div style="height: 350px">
<FamilywiseError :step="$clicks" />
</div>
</div>

<!--
Every test run at α = 0.05 has a one-in-twenty chance of a false positive when nothing is going on. Run m independent tests and the probability that at least one is a false positive is one minus 0.95 to the m. At m = 20 that is already 64%, and by m = 50 it is over 90% — the red curve. This is what happens when someone trains twenty hyperparameter configurations or compares against twenty baselines or reports twenty metrics, and then publishes the one comparison that cleared p < 0.05.

The classic fix is the Bonferroni correction: require p < α/m for each individual test. That keeps the family-wise error rate at or just under α regardless of m, shown by the flat teal curve near 5%. The cost is lower power, since each individual test is held to a much stricter standard. The Holm step-down procedure gives the same family-wise guarantee but is uniformly more powerful: sort the p-values, compare the smallest to α/m, the next to α/(m−1), and so on, stopping at the first failure. There is no reason to prefer plain Bonferroni when Holm is available.

Note that independence is not required for either correction, which is what makes them safe defaults. A complementary strategy is procedural rather than statistical: decide the comparisons before looking at results, and keep a final test set you touch once.
-->

---
glowSeed: 5572
---

# Ways to Fool Yourself

<div class="grid grid-cols-2 gap-4 mt-6">
<div v-click border="2 solid red-800" bg="red-800/20" rounded-lg p-4>
<div class="font-bold text-red-300 mb-2">Forking paths</div>
<div class="text-sm leading-relaxed opacity-90">Trying other metrics, splits, or preprocessing until something crosses p &lt; 0.05 — and reporting only that.</div>
</div>
<div v-click border="2 solid amber-800" bg="amber-800/20" rounded-lg p-4>
<div class="font-bold text-amber-300 mb-2">Peeking</div>
<div class="text-sm leading-relaxed opacity-90">Collecting more data or re-running the test until it becomes significant inflates the false-positive rate.</div>
</div>
<div v-click border="2 solid blue-800" bg="blue-800/20" rounded-lg p-4>
<div class="font-bold text-blue-300 mb-2">Winner's curse</div>
<div class="text-sm leading-relaxed opacity-90">The best of many models on a test set is optimistically biased. Pick on validation data; test the winner once.</div>
</div>
<div v-click border="2 solid violet-800" bg="violet-800/20" rounded-lg p-4>
<div class="font-bold text-violet-300 mb-2">"Not significant" ≠ "equal"</div>
<div class="text-sm leading-relaxed opacity-90">A wide interval means the test could not tell. Look at the interval and the power, not only the p-value.</div>
</div>
</div>

<!--
Four habits that quietly invalidate otherwise correct statistics. Forking paths: every analytic choice you can make after seeing the data — which metric, which split, which outlier rule — is another implicit test, so the nominal 5% no longer applies; the remedy is to fix the evaluation protocol before running it. Peeking, or optional stopping: checking the p-value as data arrive and stopping when it dips below 0.05 will eventually succeed even for identical models, so the sample size must be decided in advance or a sequential method used.

The winner's curse is the selection version of the multiple-comparisons problem: whichever model scores best on a test set is partly best because of favorable noise, so its test score overstates its true performance. Select on a validation set and spend the test set exactly once on the winner. This ties directly into the data-leakage deck that follows.

Finally, do not read a non-significant result as proof of equality. A wide interval or low power means the experiment was uninformative, as in the amber row on the interval slide. Equivalence claims need the interval to sit entirely inside a pre-specified margin.
-->

---
glowSeed: 557
---

# Model Comparison Checklist

<div class="grid grid-cols-2 gap-4 mt-6">
<div v-click border="2 solid teal-800" bg="teal-800/20" rounded-lg p-4>
<div class="font-bold text-teal-300 mb-2">Pair observations</div>
<div class="text-sm leading-relaxed opacity-90">Exploit shared test examples or shared resampling splits, and preserve groups or time structure.</div>
</div>
<div v-click border="2 solid blue-800" bg="blue-800/20" rounded-lg p-4>
<div class="font-bold text-blue-300 mb-2">Quantify uncertainty</div>
<div class="text-sm leading-relaxed opacity-90">Report a p-value or confidence interval, not just two point estimates.</div>
</div>
<div v-click border="2 solid amber-800" bg="amber-800/20" rounded-lg p-4>
<div class="font-bold text-amber-300 mb-2">Control multiplicity</div>
<div class="text-sm leading-relaxed opacity-90">Do not cherry-pick one winner from many tested models or metrics.</div>
</div>
<div v-click border="2 solid violet-800" bg="violet-800/20" rounded-lg p-4>
<div class="font-bold text-violet-300 mb-2">Judge value</div>
<div class="text-sm leading-relaxed opacity-90">Weigh the effect size against deployment cost and risk.</div>
</div>
</div>


<!--
Turn the whole deck into a checklist before claiming one model beats another. Pair observations whenever possible: use McNemar's test for per-example correctness on a shared test set, or use paired resampling with a method that accounts for dependence when comparing cross-validation results. Quantify uncertainty rather than judging two point estimates by eye.

Control multiplicity: if you evaluate 20 candidate models or 20 different metrics against a baseline and report only the one comparison that came out significant, you have effectively run 20 tests and cherry-picked the lucky one — at the conventional 0.05 threshold, roughly one comparison in twenty will look "significant" by pure chance even if nothing is actually different. This is directly analogous to repeatedly touching the test set during model development, a leakage-adjacent failure the next deck covers in depth. Finally, judge value: even a real, statistically defensible gap has to be weighed against what it costs to capture — more parameters, more inference time, more engineering complexity — before it justifies replacing a simpler, working model.
-->

---
glowSeed: 558
---

# Trustworthy Comparisons

<div class="mt-8"><div class="grid grid-cols-3 gap-4 mt-6">
<div v-click border="2 solid teal-800" bg="teal-800/20" rounded-lg p-4>
<div class="font-bold text-teal-300 mb-2">Scores vary</div>
<div class="text-sm leading-relaxed opacity-90">One number is one sample from a distribution.</div>
</div>
<div v-click border="2 solid blue-800" bg="blue-800/20" rounded-lg p-4>
<div class="font-bold text-blue-300 mb-2">Pair wisely</div>
<div class="text-sm leading-relaxed opacity-90">Use shared examples or splits and a method that matches their dependence.</div>
</div>
<div v-click border="2 solid amber-800" bg="amber-800/20" rounded-lg p-4>
<div class="font-bold text-amber-300 mb-2">Size matters</div>
<div class="text-sm leading-relaxed opacity-90">Practical significance ≠ statistical significance.</div>
</div>
</div></div>

<div v-click class="mt-10 text-center text-lg" border="2 solid white/10" bg="white/5" rounded-lg px-6 py-4>Next: common evaluation failures — leakage and class imbalance.</div>

<!--
A trustworthy comparison recognizes that a test score is a sample rather than a fixed truth, preserves pairing when the models face the same examples or splits, and uses an uncertainty method that matches the dependence in the data. It also separates evidence that a gap is real from the decision that the gap is large enough to justify deployment.

This closes the rigor thread of the module: we now have precise metrics (accuracy, precision, recall, F1, ROC-AUC), a diagnostic tool for reading exactly how a model fails (the confusion matrix), and a way to decide whether an observed difference between two models is real. None of these tools mean anything, though, if the evaluation itself was set up incorrectly — if the test set was contaminated by information it shouldn't have had, or if the metric quietly hid a rare class's failure. The next deck covers exactly those setup failures: data leakage and class imbalance, worked through concrete, end-to-end examples of how each one silently inflates a model's apparent performance.
-->
