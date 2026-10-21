---
theme: default
highlighter: shiki
css: unocss
colorSchema: dark
title: 'Bagging and Random Forests'
info: |
  ## Bagging and Random Forests
  Turn unstable trees into a stable ensemble
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
glowSeed: 610
---

# Bagging and Random Forests

### Turn unstable trees into a stable ensemble

<div class="pt-8 opacity-80 text-lg">Ensemble Methods · Foundations of Machine Learning</div>

<div class="mt-14 flex justify-center gap-4" aria-hidden="true">
<div class="w-28 h-3 rounded-full bg-teal-400/70"></div>
<div class="w-20 h-3 rounded-full bg-blue-400/60"></div>
<div class="w-14 h-3 rounded-full bg-violet-400/50"></div>
</div>

<!--
Why Ensembles Work ended with an open question: we have one training set, and we want many models whose errors are only weakly correlated. Where do they come from? This deck gives the two most widely used answers. Bagging resamples the rows. Random forests also resample the features.

Roadmap: a reminder of the variance formula → why a single deep tree is a good candidate → bootstrap sampling → bagging, shown on a toy problem and on a classifier → why bagged trees stay correlated → random forests and the choice of m → how many trees → out-of-bag evaluation → feature importance → practical defaults.

Color code for every chart in this deck: amber is a single tree, blue is bagging, teal is a random forest, and the dashed white line is the truth. Every number on these slides comes from a script in the deck folder, scripts/make_data.py, run with fixed seeds.
-->

---
glowSeed: 611
---

# Where We Left Off

<div class="grid grid-cols-2 gap-8 items-start">
<div>
<div class="mt-2" style="font-size: .85em" border="2 solid teal-800" bg="teal-800/20" rounded-lg px-4 py-1>

$$
\operatorname{Var}(\bar f)=\underbrace{\rho\sigma^2}_{\text{floor}}+\underbrace{\frac{1-\rho}{B}\,\sigma^2}_{\to\,0\text{ as }B\text{ grows}}
$$

</div>
<div class="space-y-3 mt-4">
<div v-click border="2 solid white/5" bg="white/5" rounded-lg px-4 py-3>
<span class="font-bold text-amber-300">σ²</span>
<span class="text-sm opacity-85"> — How much one member's prediction moves when the training data changes.</span>
</div>
<div v-click border="2 solid white/5" bg="white/5" rounded-lg px-4 py-3>
<span class="font-bold text-blue-300">B</span>
<span class="text-sm opacity-85"> — More members shrink the second term. Cheap, but it only reaches the floor.</span>
</div>
<div v-click border="2 solid white/5" bg="white/5" rounded-lg px-4 py-3>
<span class="font-bold text-teal-300">ρ</span>
<span class="text-sm opacity-85"> — Lower correlation lowers the floor itself.</span>
</div>
</div>
</div>
<div>
<FloorChart />
<div v-click class="mt-2 text-sm" border="2 solid amber-800" bg="amber-800/20" rounded-lg px-4 py-2>
<span class="font-bold text-amber-300">Today's question:</span> from one dataset, how do we build many members with small ρ?
</div>
</div>
</div>

<!--
This is the formula from Why Ensembles Work, unchanged. The variance of an average of B identically trained members, each with variance sigma squared and pairwise correlation rho, splits into a floor that does not depend on B and a term that vanishes as B grows. The chart is the same one from the last deck.

Read the three levers. Sigma squared is a property of one member; we will deliberately pick members where it is large, because there is a lot to remove. B is the easy lever: more members, more compute, but only down to the floor. Rho is the lever that moves the floor.

Bagging is a recipe for getting many members from one dataset. Random forests are a modification aimed squarely at rho. Keep the formula in view: every chart in this deck is a measurement of one of these three quantities.
-->

---
glowSeed: 612
---

# One Tree, Three Training Sets

<div class="text-sm opacity-85 mt-1">Same 50 points, resampled three times. Dot size = how many times a row was drawn. Red rings = rows left out. Amber = a fully grown tree fit to that sample.</div>

<div class="grid grid-cols-3 gap-4 mt-4">
<div v-click><OneDPlot :boot="0" :tree="0" truth title="Sample 1" /></div>
<div v-click><OneDPlot :boot="1" :tree="1" truth title="Sample 2" /></div>
<div v-click><OneDPlot :boot="2" :tree="2" truth title="Sample 3" /></div>
</div>

<div class="grid grid-cols-2 gap-4 mt-4">
<div v-click border="2 solid white/5" bg="white/5" rounded-lg px-4 py-3>
<span class="font-bold text-teal-300">Low bias</span>
<span class="text-sm opacity-85"> — Each tree follows the dashed truth on average, wherever there is data.</span>
</div>
<div v-click border="2 solid white/5" bg="white/5" rounded-lg px-4 py-3>
<span class="font-bold text-amber-300">High variance</span>
<span class="text-sm opacity-85"> — Each tree chases its own sample's noise. The spikes differ from panel to panel.</span>
</div>
</div>

<!--
The toy problem for the first half of the deck: 50 points from y = sin(2πx) plus Gaussian noise with standard deviation 0.3. The dashed curve is the truth.

Each panel is one bootstrap resample of the same 50 points, which we define properly on the next slide. For now: some rows were drawn more than once (bigger dots), and some were not drawn at all (red rings). We fit a decision tree with no depth limit to each sample. A fully grown tree keeps splitting until every leaf holds a single distinct x value, so it passes through every training point it saw.

Compare the three amber curves. They all follow the sine wave, which is the low bias. But they disagree in the details: a spike in one panel is missing in the next, because it came from one noisy point that the other sample happened to skip or repeat. That disagreement is sigma squared, and it is large. This is the member we want: accurate on average, unstable in the details. Averaging should remove the details and keep the average.
-->

---
glowSeed: 613
---

# Bootstrap Sampling

<div class="text-sm opacity-85 mt-1">Draw n rows from n rows, with replacement. Each draw picks any row with probability 1/n.</div>

<div class="mt-4 space-y-1 max-w-3xl mx-auto">
<BootRow label="original" />
<div v-click><BootRow :sample="0" label="sample 1" /></div>
<div v-click><BootRow :sample="1" label="sample 2" /></div>
<div v-click><BootRow :sample="2" label="sample 3" /></div>
</div>

<div class="grid grid-cols-3 gap-4 mt-6">
<div v-click border="2 solid teal-800" bg="teal-800/20" rounded-lg p-4>
<div class="font-bold text-teal-300 mb-2">Same size</div>
<div class="text-sm leading-relaxed opacity-90">Every sample has n rows, so each tree trains on a dataset as large as the original.</div>
</div>
<div v-click border="2 solid blue-800" bg="blue-800/20" rounded-lg p-4>
<div class="font-bold text-blue-300 mb-2">Repeats and gaps</div>
<div class="text-sm leading-relaxed opacity-90">Dashed tiles are repeats. Rows never drawn are <span class="text-red-300">out-of-bag</span> for that sample.</div>
</div>
<div v-click border="2 solid amber-800" bg="amber-800/20" rounded-lg p-4>
<div class="font-bold text-amber-300 mb-2">A stand-in for new data</div>
<div class="text-sm leading-relaxed opacity-90">Each resample imitates a fresh training set drawn from the population.</div>
</div>
</div>

<!--
A bootstrap sample is n independent draws, with replacement, from the n rows you have. Here n = 10 and the tiles are row numbers. Walk through sample 1: row 1 was drawn three times, rows 5 and 7 twice, and rows 2, 4, 6 and 10 never. Those four are out-of-bag for sample 1. The other two samples miss different rows.

Why bother? In the bias–variance unit we imagined drawing many training sets from the population and refitting the model each time. We cannot do that: we have one dataset. The bootstrap treats the dataset as a stand-in for the population and draws "new" training sets from it. That only works as well as the dataset represents the population. If your data is biased or tiny, resampling it does not fix that.

Keep the out-of-bag rows in mind. They come back near the end of the deck as a free validation set.
-->

---
glowSeed: 614
---

# Why About 36.8% Are Left Out

<div class="grid grid-cols-2 gap-8 items-start">
<div>
<div class="space-y-3 mt-4">
<div v-click border="2 solid white/5" bg="white/5" rounded-lg px-4 py-3>
<span class="font-bold text-teal-300">One draw misses row i</span>
<span class="text-sm opacity-85"> — with probability 1 − 1/n.</span>
</div>
<div v-click border="2 solid white/5" bg="white/5" rounded-lg px-4 py-3>
<span class="font-bold text-blue-300">All n draws miss it</span>
<span class="text-sm opacity-85"> — The draws are independent, so multiply.</span>
</div>
</div>
<div v-click class="mt-4" style="font-size: .9em" border="2 solid teal-800" bg="teal-800/20" rounded-lg px-4 py-2>

$$
P(\text{out-of-bag})=\left(1-\frac1n\right)^n \longrightarrow e^{-1}\approx0.368
$$

</div>
<div v-click class="mt-4 text-sm" border="2 solid white/5" bg="white/5" rounded-lg px-4 py-3>
Worked example: with n = 1,000 rows, each sample still has 1,000 draws, but about 368 distinct rows never appear. The other ~632 rows fill all 1,000 draws, some of them more than once.
</div>
</div>
<div>
<OobLimit class="mt-4" />
</div>
</div>

<!--
Derive this on the board. Fix one row. On a single draw, the chance we pick some other row is 1 − 1/n. There are n draws and they are independent, so the chance that every one of them misses our row is (1 − 1/n) to the n. As n grows this converges to e to the minus 1, about 0.368. It is the same limit that defines e.

The chart shows how fast that happens. At n = 1 the single row is always drawn, so the probability is 0. At n = 2 it is 0.25. By n = 10 it is 0.349, and by n = 40 it is 0.363, within half a percentage point of the limit. For any realistic dataset you can treat it as 36.8%.

Two consequences. Each tree sees only about 63.2% of the distinct rows, which is part of why bootstrap trees differ from one another. And every row is left out of roughly a third of the trees, which is what makes out-of-bag evaluation possible later.
-->

---
glowSeed: 615
---

# Bagging = Bootstrap + Aggregate

<div class="grid grid-cols-[1fr_2rem_1fr_2rem_1fr] gap-2 items-start mt-4">
<div v-click>
<div class="text-center text-sm font-bold text-slate-300 mb-1">1 · One dataset</div>
<OneDPlot :axes="false" :h="236" />
</div>
<div v-click class="text-3xl text-center opacity-60 mt-24">→</div>
<div v-click class="space-y-1">
<div class="text-center text-sm font-bold text-amber-300 mb-1">2 · B samples, B deep trees</div>
<OneDPlot :boot="0" :tree="0" :axes="false" :h="110" />
<OneDPlot :boot="1" :tree="1" :axes="false" :h="110" />
<div class="text-center opacity-60 leading-none">⋮</div>
</div>
<div v-click class="text-3xl text-center opacity-60 mt-24">→</div>
<div v-click>
<div class="text-center text-sm font-bold text-blue-300 mb-1">3 · Average (or vote)</div>
<OneDPlot :points="false" avg truth :axes="false" :h="236" />
</div>
</div>

<div class="grid grid-cols-2 gap-6 mt-5 items-center">
<div v-click style="font-size: .9em" border="2 solid teal-800" bg="teal-800/20" rounded-lg px-4 py-1>

$$
\hat f_{\mathrm{bag}}(x)=\frac1B\sum_{b=1}^B\hat f_b(x)
$$

</div>
<div v-click class="text-sm" border="2 solid white/5" bg="white/5" rounded-lg px-4 py-3>
<span class="font-bold text-blue-300">Classification:</span> majority vote of the B trees, or average their predicted probabilities and take the largest.
</div>
</div>

<!--
Bagging is short for bootstrap aggregating, and the name is the whole recipe. Step 1: start from one dataset. Step 2: draw B bootstrap samples and fit the same learner, here a fully grown tree, to each one independently. Step 3: average the B predictions for regression, or vote for classification.

The trees never talk to each other. Each is fit on its own sample with no knowledge of the rest, so all B can be trained in parallel on different cores or machines. That independence is also what makes the variance formula apply: the members are identically trained, so they share one sigma squared, one rho and one bias.

scikit-learn's BaggingClassifier and BaggingRegressor implement exactly this for any base learner. For trees, you will usually use RandomForestClassifier or RandomForestRegressor, which include bagging as a special case, as we will see.
-->

---
glowSeed: 616
---

# Averaging in Action

<div class="grid grid-cols-2 gap-8 mt-4">
<div v-click>
<OneDPlot :trees="25" :points="false" truth title="25 bootstrapped trees" />
<div class="mt-3 text-sm" border="2 solid white/5" bg="white/5" rounded-lg px-4 py-3>
<span class="font-bold text-amber-300">Individually</span>
<span class="opacity-85"> — Every tree is jagged, and each in its own places.</span>
</div>
</div>
<div v-click>
<OneDPlot avg truth title="Their average" color="#60a5fa" />
<div class="mt-3 text-sm" border="2 solid white/5" bg="white/5" rounded-lg px-4 py-3>
<span class="font-bold text-blue-300">Together</span>
<span class="opacity-85"> — The spikes point in different directions and largely cancel. The shape they share remains.</span>
</div>
</div>
</div>

<div v-click class="mt-5 text-center" border="2 solid white/10" bg="white/5" rounded-lg px-6 py-3>Averaging keeps what the trees agree on (the signal) and cancels what they disagree on (the noise).</div>

<!--
Left: 25 trees, each fit to its own bootstrap sample of the same 50 points, drawn faintly on top of one another. Where they all agree, the faint lines stack into a bright band; that is the sine wave. Where they disagree, the lines fan out.

Right: the pointwise average of those 25 curves. It is still made of steps, since an average of step functions is a step function, but the steps are small and the large spikes are gone. It tracks the dashed truth far better than any single tree on the left.

This is the "Five Guesses Beat the Best Guesser" slide from Why Ensembles Work, now with trees instead of people. The next slide measures exactly how much the variance fell.
-->

---
glowSeed: 617
---

# One Input, 400 Training Sets

<div class="text-sm opacity-85 mt-1">Draw a fresh 50-point dataset 400 times. Each time, record the prediction at x = 0.3 from one deep tree and from a bagged ensemble of 50 trees.</div>

<div class="grid grid-cols-[3fr_2fr] gap-8 items-start mt-3">
<div class="space-y-2">
<div v-click><PredHist which="single" /></div>
<div v-click><PredHist which="bagged" /></div>
</div>
<div class="space-y-3 mt-2">
<div v-click border="2 solid white/5" bg="white/5" rounded-lg px-4 py-3>
<span class="font-bold text-teal-300">Same center</span>
<span class="text-sm opacity-85"> — Mean prediction 0.928 vs 0.924. Truth is 0.951. Bias is essentially unchanged.</span>
</div>
<div v-click border="2 solid white/5" bg="white/5" rounded-lg px-4 py-3>
<span class="font-bold text-blue-300">Half the spread</span>
<span class="text-sm opacity-85"> — Variance 0.083 → 0.040.</span>
</div>
<div v-click border="2 solid white/5" bg="white/5" rounded-lg px-4 py-3>
<span class="font-bold text-amber-300">Why not 50× less?</span>
<span class="text-sm opacity-85"> — The implied ρ between bagged trees is 0.41. The floor ρσ² = 0.41 × 0.095 ≈ 0.039 is where we landed.</span>
</div>
</div>
</div>

<!--
This is the "a prediction is a random variable" picture from Why Ensembles Work, measured. We go back to the population, draw a brand-new 50-point dataset 400 times, and each time fit two things: one fully grown tree, and a bagged ensemble of 50 trees. We record both predictions at x = 0.3, where the truth is 0.951. The histograms show where those 400 predictions landed. The dashed line is the truth.

First card: the two histograms are centered in the same place. Bagging did not move the center, which is the bias, exactly as the theory says. Both sit slightly below the truth, because x = 0.3 is near the peak of the sine and a tree's leaves average in some lower neighbors.

Second card: the bagged histogram is about half as wide in variance.

Third card: half, not one-fiftieth. That is the floor. We can back out rho from the measurements: a single bootstrapped tree has variance 0.095, the bagged ensemble 0.040, and solving the variance formula with B = 50 gives rho ≈ 0.41. Fifty trees have already reached the floor of 0.039, so a thousand would not help. To do better we must lower rho, and that is the rest of the deck.

Why is rho so high here? With a single input feature, every tree has to split on x. All 50 trees are built from overlapping resamples of the same 50 points, so their noise-chasing is similar.
-->

---
glowSeed: 618
---

# Why Trees? Bagging Needs Variance to Remove

<div class="grid grid-cols-2 gap-8 mt-4">
<div v-click>
<OneDPlot :lins="25" truth title="25 bootstrapped linear fits" color="#a78bfa" />
<div class="mt-3 text-sm" border="2 solid violet-800" bg="violet-800/20" rounded-lg px-4 py-3>
<span class="font-bold text-violet-300">Linear regression: stable but biased</span>
<span class="opacity-85"> — The lines barely move. Averaging them gives the same wrong line. Bagging has nothing to cancel.</span>
</div>
</div>
<div v-click>
<OneDPlot :trees="25" truth title="25 bootstrapped deep trees" />
<div class="mt-3 text-sm" border="2 solid amber-800" bg="amber-800/20" rounded-lg px-4 py-3>
<span class="font-bold text-amber-300">Deep tree: accurate but unstable</span>
<span class="opacity-85"> — Right on average, wrong in different places each time. Exactly what averaging fixes.</span>
</div>
</div>
</div>

<div v-click class="mt-5 text-center" border="2 solid white/10" bg="white/5" rounded-lg px-6 py-3>Bag a learner when it is <span class="text-teal-300 font-bold">low bias</span> and <span class="text-amber-300 font-bold">high variance</span>. Deep trees are the textbook case.</div>

<!--
Why not bag everything? Same 25 bootstrap samples, two different learners.

Left: ordinary least-squares lines. They hardly move from sample to sample: sigma squared is small, so there is little variance to remove. And all of them miss the sine wave in the same way, because a straight line cannot bend. Averaging 25 nearly identical, equally wrong lines gives the same wrong line. That is the "averaging leaves bias unchanged" result from the last deck, made visible.

Right: the deep trees from before. Large sigma squared, small bias. Averaging has a lot to work with.

The rule students should be able to apply: bagging pays off when the base learner is flexible enough to be accurate on average and that same flexibility makes it unstable. Fully grown trees are both. Shallow trees and linear models are neither; if your learner's problem is bias, look to boosting, the next deck.
-->

---
glowSeed: 619
---

# Two Moons: A Noisy Classification Problem

<div class="text-sm opacity-85 mt-1">300 training points from two interleaving half-moons, with label noise. Blue and amber are the two classes.</div>

<div class="grid grid-cols-2 gap-8 mt-3">
<div><BoundaryMap model="data" /></div>
<div v-click><BoundaryMap model="tree" /></div>
</div>

<div class="grid grid-cols-2 gap-8 mt-3">
<div class="text-sm" border="2 solid white/5" bg="white/5" rounded-lg px-4 py-2>
<span class="font-bold text-slate-300">The data</span>
<span class="opacity-85"> — The classes overlap where the noise pushes points across the curve. No straight line separates them.</span>
</div>
<div v-click class="text-sm" border="2 solid white/5" bg="white/5" rounded-lg px-4 py-2>
<span class="font-bold text-amber-300">One deep tree</span>
<span class="opacity-85"> — Axis-aligned rectangles, every region fully confident. Small islands around single noisy points.</span>
</div>
</div>

<!--
Before we bag anything, here is the problem. The data are two interleaving half-moons with label noise, 300 training points, generated with scikit-learn's make_moons. Blue and amber are the two classes. The noise is large enough that the crescents overlap, so some points sit on the wrong side of the curve.

Click: a single fully grown tree fit to those points. Each cell of the background is shaded by the tree's predicted probability of amber. A fully grown tree has pure leaves, so every region is solid, 100% confident. It is a patchwork of axis-aligned rectangles, and it carves small islands around individual noisy points. That is the overfitting we expect from a high-variance learner. On 5,000 fresh points it scores 83.4%.
-->

---
glowSeed: 6190
---

# Bagging Classifiers: Smoother Boundaries

<div class="text-sm opacity-85 mt-1">Same data. Shading = predicted probability of the amber class. Accuracy on 5,000 fresh points.</div>

<div class="grid grid-cols-2 gap-8 mt-3">
<div><BoundaryMap model="tree" /></div>
<div v-click><BoundaryMap model="bag" /></div>
</div>

<div class="grid grid-cols-2 gap-8 mt-3">
<div class="text-sm" border="2 solid white/5" bg="white/5" rounded-lg px-4 py-2>
<span class="font-bold text-amber-300">One tree</span>
<span class="opacity-85"> — Every region is fully confident. Small islands around single points.</span>
</div>
<div v-click class="text-sm" border="2 solid white/5" bg="white/5" rounded-lg px-4 py-2>
<span class="font-bold text-blue-300">Bagged</span>
<span class="opacity-85"> — Averaging 300 trees' probabilities. Pale bands mark where trees disagree.</span>
</div>
</div>

<!--
The same idea for classification. Left: the single tree from the last slide. Click: 300 bagged trees, averaging their predicted probabilities. Solid amber or solid blue means confident, pale means close to 50/50.

An island that appears in one tree only gets outvoted by the trees whose sample skipped that point, so its probability gets pulled toward the middle. The pale bands are honest uncertainty where the trees disagree. This is the classification version of "same center, less spread": a single tree's boundary jumps around from sample to sample, and averaging stabilizes it.

Notice the bagged map is not yet a classification. It is a probability. The next slide applies the decision rule.
-->

---
glowSeed: 6191
---

# Applying the Threshold

<div class="text-sm opacity-85 mt-1">A classifier has to pick a label. Predict amber where the bagged probability is at least 0.5, blue otherwise.</div>

<div class="grid grid-cols-2 gap-8 mt-3">
<div><BoundaryMap model="tree" /></div>
<div><BoundaryMap model="bag" hard /></div>
</div>

<div class="grid grid-cols-2 gap-8 mt-3">
<div class="text-sm" border="2 solid white/5" bg="white/5" rounded-lg px-4 py-2>
<span class="font-bold text-amber-300">One tree</span>
<span class="opacity-85"> — Already 0 or 1 everywhere, so thresholding changes nothing. The islands stay.</span>
</div>
<div v-click class="text-sm" border="2 solid white/5" bg="white/5" rounded-lg px-4 py-2>
<span class="font-bold text-blue-300">Bagged</span>
<span class="opacity-85"> — Most islands were outvoted below 0.5, so they vanish. The boundary is the 0.5 contour, and it follows the moons.</span>
</div>
</div>

<!--
Same two models, now as actual classifiers. The bagged map is the previous slide's probabilities cut at 0.5: at least 0.5 is amber, below is blue, with no shading in between. The accuracy, 88.3%, is computed from these hard labels.

The single tree is already 0 or 1 in every cell, so thresholding does nothing to it. The islands around noisy points stay. In the bagged version, an island that only a few trees drew has an averaged probability under 0.5, so it flips to the surrounding class and disappears. What is left is the 0.5 contour, a hard boundary but a smoother, more curved one.

You could get the same labels by majority vote: each tree casts a hard vote and the class with more than half wins. Averaging probabilities and voting usually agree; averaging also gives the pale bands on the previous slide.
-->

---
glowSeed: 620
---

# The Correlation Problem

<div class="text-sm opacity-85 mt-1">California housing: predict median house value from 8 features, 2,000 training rows. Which feature does each bagged tree split on first?</div>

<div class="grid grid-cols-2 gap-8 items-start mt-3">
<div v-click>
<RootTally model="bag" />
</div>
<div class="space-y-3">
<div v-click border="2 solid white/5" bg="white/5" rounded-lg px-4 py-3>
<span class="font-bold text-blue-300">300 of 300 on MedInc</span>
<span class="text-sm opacity-85"> — Median income is so predictive that every bootstrap sample picks it first.</span>
</div>
<div v-click border="2 solid white/5" bg="white/5" rounded-lg px-4 py-3>
<span class="font-bold text-amber-300">Same top, similar trees</span>
<span class="text-sm opacity-85"> — The first split shapes everything below it, so the trees share much of their structure.</span>
</div>
<div v-click border="2 solid white/5" bg="white/5" rounded-lg px-4 py-3>
<span class="font-bold text-teal-300">Shared structure, shared mistakes</span>
<span class="text-sm opacity-85"> — ρ is higher than it needs to be, and so is the floor, however many trees we add.</span>
</div>
</div>
</div>

<!--
Switch to a real dataset for the rest of the deck: California housing, from the 1990 census. Each row is a district; the target is median house value in units of $100,000; the 8 features are median income, house age, average rooms, average bedrooms, population, average occupancy, latitude and longitude. We train on 2,000 rows.

Fit 300 bagged trees and look only at the root split of each. All 300 split on MedInc. Bootstrapping changes which rows a tree sees, but it does not change the fact that median income is by far the best single split on almost any sample of this data.

That matters because the root decides how the rest of the tree is built. Trees with the same root tend to make similar second and third splits, so they share structure, and trees that share structure tend to make the same mistakes. In the language of the formula, rho is higher than it needs to be, and the floor rho sigma squared stays where it is however large B gets. Plain bagging has no mechanism to fix this. Higher than what? The next two slides measure it.
-->

---
glowSeed: 621
---

# Random Forests: Random Features per Split

<div class="grid grid-cols-2 gap-8 items-start">
<div>
<div class="space-y-3 mt-4">
<div v-click border="2 solid white/5" bg="white/5" rounded-lg px-4 py-3>
<span class="font-bold text-teal-300">At every node</span>
<span class="text-sm opacity-85"> — Draw m of the d features at random. Search for the best split among those m only.</span>
</div>
<div v-click border="2 solid white/5" bg="white/5" rounded-lg px-4 py-3>
<span class="font-bold text-blue-300">The dominant feature is sometimes unavailable</span>
<span class="text-sm opacity-85"> — Then the tree must split on something else. Different roots, different trees.</span>
</div>
<div v-click border="2 solid white/5" bg="white/5" rounded-lg px-4 py-3>
<span class="font-bold text-amber-300">Random forest = bagging + this</span>
<span class="text-sm opacity-85"> — With m = d it is exactly bagging.</span>
</div>
</div>
<div v-click class="mt-4 text-sm" border="2 solid teal-800" bg="teal-800/20" rounded-lg px-4 py-3>
Common starting points: <code>m = √d</code> for classification, <code>m ≈ d/3</code> for regression. Tune it.
</div>
</div>
<div>
<div v-click><FeatureSubset class="mt-2" /></div>
</div>
</div>

<!--
Random forests, introduced by Leo Breiman in 2001, make one change to how each tree is grown. At every node, before searching for the best split, draw a random subset of m features out of the d available. Only those m are candidates at that node. The next node draws a fresh subset. The rows are still bootstrapped exactly as in bagging.

The diagram shows three nodes of one tree with d = 8 and m = 3. The root happened to draw MedInc, so it splits on MedInc. The left child drew HouseAge, AveRooms and Latitude and split on Latitude. The right child did not draw MedInc either, and split on AveOccup. In plain bagging all three nodes would have searched all 8 features.

When the dominant feature is not drawn at the root, the tree has to start elsewhere. That makes the trees more different from one another, which is exactly a lower rho.

Note that m = d recovers bagging, so bagging is the special case of a random forest with no feature subsampling. The defaults: square root of d is the classical choice for classification, and roughly d/3 for regression. A caution on scikit-learn: RandomForestRegressor's default is max_features = 1.0, meaning all features, which is plain bagging. Set it yourself.
-->

---
glowSeed: 622
---

# Decorrelation, Measured

<div class="grid grid-cols-2 gap-8 items-start mt-2">
<div>
<div v-click><RootTally model="rf" /></div>
<div v-click class="mt-3 text-sm" border="2 solid white/5" bg="white/5" rounded-lg px-4 py-3>
MedInc is in the root's draw with probability 3/8. Expected 112.5 of 300 trees; observed 110.
</div>
</div>
<div>
<div v-click class="mt-2" border="2 solid white/5" bg="white/5" rounded-lg px-4 py-3>
<div class="font-bold text-teal-300 mb-2">Measured over 20 training sets</div>
<table class="text-sm w-full">
<thead><tr><th></th><th>σ² (one tree)</th><th>ρ</th><th>floor ρσ²</th></tr></thead>
<tbody>
<tr><td class="text-blue-300 font-bold">Bagging, m = 8</td><td>0.411</td><td>0.075</td><td>0.031</td></tr>
<tr><td class="text-teal-300 font-bold">Forest, m = 3</td><td>0.440</td><td>0.040</td><td>0.018</td></tr>
</tbody>
</table>
</div>
<div v-click class="mt-4 text-sm" border="2 solid amber-800" bg="amber-800/20" rounded-lg px-4 py-3>
<span class="font-bold text-amber-300">The trade:</span> each tree got a little worse (σ² up 7%), but the trees got much less alike (ρ down 47%). The floor drops by about 43%.
</div>
</div>
</div>

<!--
Same data, same 300 trees, but now each node may consider only m = 3 of the 8 features. The root tally spreads out: MedInc still leads, but AveRooms, Latitude and AveOccup each start a substantial share of the trees.

The small card is a check that the mechanism works the way we said. MedInc can only be chosen at the root if it is among the 3 features drawn there, which happens with probability 3/8. When it is drawn it essentially always wins, so we expect 300 × 3/8 = 112.5 trees rooted on MedInc. We got 110.

The table puts numbers on the formula. We drew 20 fresh 2,000-row training sets from the full dataset, fit both ensembles to each, and measured at 2,000 held-out districts. Sigma squared is the variance of one tree's prediction; rho comes from the variance of the 200-tree ensemble, solved from the formula exactly as on the 400-training-set slide. Restricting the features made each tree slightly worse, since it sometimes cannot use the best feature, so sigma squared rose a little. But rho almost halved, so the floor fell from 0.031 to 0.018.

Notice that both rhos are far smaller than the 0.41 from the one-feature toy. With 8 features and 2,000 rows, deep trees already differ quite a lot. Random forests push that further.
-->

---
glowSeed: 623
---

# Choosing m: Strength vs. Diversity

<div class="grid grid-cols-2 gap-8 items-start mt-2">
<div v-click>
<MTradeoff panel="parts" />
</div>
<div>
<div v-click><MTradeoff panel="mse" /></div>
</div>
</div>

<div class="grid grid-cols-3 gap-4 mt-3">
<div v-click class="text-sm" border="2 solid amber-800" bg="amber-800/20" rounded-lg px-3 py-2>
<span class="font-bold text-amber-300">Small m</span>
<span class="opacity-85"> — Very diverse trees, but each one is weak.</span>
</div>
<div v-click class="text-sm" border="2 solid blue-800" bg="blue-800/20" rounded-lg px-3 py-2>
<span class="font-bold text-blue-300">Large m</span>
<span class="opacity-85"> — Strong trees, but they all look alike.</span>
</div>
<div v-click class="text-sm" border="2 solid teal-800" bg="teal-800/20" rounded-lg px-3 py-2>
<span class="font-bold text-teal-300">In between</span>
<span class="opacity-85"> — The best m depends on the data. Tune it with OOB or CV.</span>
</div>
</div>

<!--
Now sweep m from 1 to 8, again averaging over 20 training sets of 2,000 rows each.

Left, top: sigma squared, the variance of a single tree, rises as m shrinks. A tree that must often split on a weak feature is a noisier, worse predictor. Left, bottom: rho falls as m shrinks, from 0.075 at m = 8 to 0.019 at m = 1. Fewer candidate features means trees that agree less.

Right: the forest's test error on 2,000 held-out districts. It is U-shaped. At m = 1 every split is on a random feature, the trees are very diverse but individually weak, and the error is worst at 0.364. At m = 8, plain bagging, the trees are strong but correlated, 0.325. The best is m = 3 at 0.305, about 6% lower than bagging. With d = 8, d/3 ≈ 2.7, so the regression rule of thumb lands right next to the minimum here.

The error is not the variance alone; it also includes bias and the irreducible noise in house prices. The honest message is that m controls a tradeoff between how good each tree is and how different the trees are, and the best setting is found empirically. It is the most important random-forest hyperparameter to tune.
-->

---
glowSeed: 624
---

# How Many Trees?

<div class="grid grid-cols-[3fr_2fr] gap-8 items-start mt-2">
<div v-click>
<NTreesChart />
</div>
<div class="space-y-3 mt-2">
<div v-click border="2 solid white/5" bg="white/5" rounded-lg px-4 py-3>
<span class="font-bold text-teal-300">Steep, then flat</span>
<span class="text-sm opacity-85"> — The (1 − ρ)σ²/B term vanishes fast. Most of the gain comes in the first ~50 trees.</span>
</div>
<div v-click border="2 solid white/5" bg="white/5" rounded-lg px-4 py-3>
<span class="font-bold text-blue-300">Different plateaus</span>
<span class="text-sm opacity-85"> — Bagging levels off near 0.338, the forest near 0.31. The gap comes mostly from ρ, not B.</span>
</div>
<div v-click border="2 solid white/5" bg="white/5" rounded-lg px-4 py-3>
<span class="font-bold text-amber-300">More trees never hurt accuracy</span>
<span class="text-sm opacity-85"> — Only time and memory. Unlike boosting rounds, B is not a knob that overfits.</span>
</div>
</div>
</div>

<!--
One training set of 2,000 rows, a test set of 2,000 held-out districts, and the number of trees B on a log axis. The dashed amber line is a single fully grown tree, with test MSE 0.586.

At B = 1 both curves start above the dashed line, around 0.73: one bootstrapped tree sees only about 63% of the distinct rows, so it is worse than a tree fit to all of them. Then they fall steeply, passing the single full tree within two or three trees. By around 50 trees most of the improvement has happened; from 100 to 500 the curves are nearly flat. That is the shape of the floor chart from the start of the deck: the second term shrinks like 1/B and leaves the floor behind.

The two plateaus differ: bagging ends near 0.338, the random forest near 0.310. Adding trees cannot close that gap. Most of it comes from the floor, rho sigma squared, which does not depend on B: across 20 training sets the forest's variance was 0.013 lower than bagging's, out of a 0.020 difference in test MSE. Only changing m moved it.

A practical point to stress: adding more trees to a bagged ensemble or a random forest does not cause overfitting. Each tree is an independent draw, and the average converges as B grows. The cost is training time, memory and prediction latency. Boosting, next deck, is different: there, more rounds can make test error worse.
-->

---
glowSeed: 625
---

# Out-of-Bag Evaluation

<div class="grid grid-cols-[3fr_2fr] gap-8 items-start mt-2">
<div v-click>
<OobGrid :row="1" />
</div>
<div class="space-y-3 mt-2">
<div v-click border="2 solid white/5" bg="white/5" rounded-lg px-4 py-3>
<span class="font-bold text-teal-300">For each training row</span>
<span class="text-sm opacity-85"> — Predict it using only the trees that never saw it.</span>
</div>
<div v-click border="2 solid white/5" bg="white/5" rounded-lg px-4 py-3>
<span class="font-bold text-blue-300">Score all rows that way</span>
<span class="text-sm opacity-85"> — The result is an estimate of test error, with no held-out split.</span>
</div>
<div v-click border="2 solid white/5" bg="white/5" rounded-lg px-4 py-3>
<span class="font-bold text-amber-300">How many voters?</span>
<span class="text-sm opacity-85"> — About 36.8% of B. With 200 trees, ~74 per row.</span>
</div>
</div>
</div>

<!--
The out-of-bag rows from the start of the deck pay off here. The grid shows 8 training rows and 10 trees. A number says how many times that row was drawn into that tree's bootstrap sample. A red cell means the row is out-of-bag for that tree: the tree never trained on it.

Follow row 2. It is out-of-bag for trees 1, 2, 3 and 9. Those four trees have never seen row 2, so their prediction on it is an honest held-out prediction. Average them (or let them vote) to get row 2's out-of-bag prediction, and compare it with row 2's true label. Do the same for every row and aggregate the errors. That is the out-of-bag error.

It estimates the same thing as a validation set or cross-validation, generalization error, but comes for free with training. No rows are held back, and no extra models are fit.

Two caveats. Each row's out-of-bag prediction uses only about a third of the forest, so it is a slightly pessimistic estimate for small B. And it only exists for bootstrap ensembles. Boosting fits every learner to the full (reweighted) dataset, so no learner is left out for any row.
-->

---
glowSeed: 6260
---

# What Out-of-Bag Does and Doesn't Mean

<div class="text-sm opacity-85 mt-1">Out-of-bag error is not "train on everything, test on a leftover 36%." Two details matter.</div>

<div class="grid grid-cols-2 gap-8 mt-4">
<div v-click border="2 solid amber-800" bg="amber-800/20" rounded-lg p-4>
<div class="font-bold text-amber-300 mb-2">No model sees all the data</div>
<div class="text-sm leading-relaxed opacity-90">Each tree trains on only about 63% of the distinct rows. The forest as a whole has seen every row, but any one row is scored only by the trees that left it out.</div>
</div>
<div v-click border="2 solid blue-800" bg="blue-800/20" rounded-lg p-4>
<div class="font-bold text-blue-300 mb-2">A smaller ensemble is scoring</div>
<div class="text-sm leading-relaxed opacity-90">Each row's out-of-bag prediction uses about a third of the forest, so the estimate is slightly pessimistic for small B. The full forest is a little better than its OOB error says.</div>
</div>
</div>

<div v-click class="mt-5 text-center" border="2 solid white/10" bg="white/5" rounded-lg px-6 py-3>The 36.8% is a fraction of <span class="text-teal-300 font-bold">trees per row</span>, not a fixed set of rows held back.</div>

<!--
A common misreading of out-of-bag evaluation is that it reserves about a third of the data as a test set while still training on everything. It does not work that way.

First card: there is no fixed held-out chunk. Each tree leaves out a different ~36.8% of rows, so no single model is trained on the full dataset; each sees about 63% of the distinct rows. Every row is out-of-bag for roughly a third of the trees, and only those trees score it.

Second card: because each row is scored by only a third of the forest, the out-of-bag prediction comes from a smaller ensemble than the one you would deploy. A smaller ensemble has a higher variance term, so the out-of-bag error runs a little high, most noticeably when B is small. With a few hundred trees the gap is small.

Bottom line: out-of-bag error is a free, roughly unbiased estimate of test error that lets you fit on all your data. It is a good default for tuning m and the number of trees. For a final comparison between models, a separate test set is still cleaner.
-->

---
glowSeed: 626
---

# Out-of-Bag in Practice

<div class="grid grid-cols-2 gap-8 items-start mt-2">
<div>

```python
from sklearn.ensemble import RandomForestRegressor

rf = RandomForestRegressor(
    n_estimators=500, max_features=3,
    oob_score=True, n_jobs=-1, random_state=0,
)
rf.fit(X_train, y_train)

print(rf.oob_score_)  # R² of the OOB predictions
oob_mse = ((rf.oob_prediction_ - y_train) ** 2).mean()
```

<div v-click class="mt-4 text-sm" border="2 solid white/5" bg="white/5" rounded-lg px-4 py-3>
<span class="font-bold text-teal-300">Use it</span> to choose <code>max_features</code> or to check that B is large enough, without spending data on a validation split.
</div>
</div>
<div>
<div v-click><NTreesChart oob /></div>
<div v-click class="mt-2 text-sm" border="2 solid white/5" bg="white/5" rounded-lg px-4 py-3>
At 500 trees: out-of-bag MSE 0.311, test MSE 0.310. Out-of-bag is a little high for small B, when each row has few voters.
</div>
</div>
</div>

<!--
In scikit-learn, pass oob_score=True. After fitting, oob_score_ holds the out-of-bag version of the model's default score, which is R squared for a regressor and accuracy for a classifier, and oob_prediction_ (or oob_decision_function_ for classifiers) holds the per-row out-of-bag predictions, from which you can compute any metric you like. n_jobs=-1 trains the trees on all CPU cores, which works because the trees are independent.

The chart is the random forest from the "How Many Trees?" slide. The solid teal line is error on the 2,000 held-out districts; the dashed red line is the out-of-bag error, computed only from the training rows. Out-of-bag error is not defined for very small B, because some rows are in every tree's sample, so the red line starts at B = 20. At first it sits above the test error, because each row is being predicted by only a third of a small forest. By 500 trees the two agree to within 0.001.

A healthy habit: on a new problem, compare oob_score_ with a 5-fold cross-validation score once. If they roughly agree, use the out-of-bag score for tuning from then on, since it is much cheaper.
-->

---
glowSeed: 627
---

# Feature Importance: Useful, Not Causal

<div class="text-sm opacity-85 mt-1">Same forest, plus a <span class="text-red-300 font-bold">RowID</span> column: a random row number with no relationship to price.</div>

<div class="grid grid-cols-[3fr_2fr] gap-8 items-start mt-3">
<div v-click>
<ImportanceBars />
</div>
<div class="space-y-3">
<div v-click border="2 solid violet-800" bg="violet-800/20" rounded-lg px-4 py-3>
<span class="font-bold text-violet-300">Impurity (MDI)</span>
<span class="text-sm opacity-85"> — Total split improvement per feature, on the training data. Fast, but RowID gets 2.9%.</span>
</div>
<div v-click border="2 solid teal-800" bg="teal-800/20" rounded-lg px-4 py-3>
<span class="font-bold text-teal-300">Permutation</span>
<span class="text-sm opacity-85"> — Shuffle one column on held-out data and measure how much error rises. RowID gets 0.</span>
</div>
<div v-click border="2 solid amber-800" bg="amber-800/20" rounded-lg px-4 py-3>
<span class="font-bold text-amber-300">Neither is causal</span>
<span class="text-sm opacity-85"> — Both describe what this model relies on. Correlated features split the credit.</span>
</div>
</div>
</div>

<!--
Random forests come with two common ways to summarize which features matter, and they disagree in an instructive way.

Impurity-based importance, also called mean decrease in impurity or MDI, is what feature_importances_ returns. Every time a split uses a feature, record how much it reduced the squared error, weighted by how many training rows reached that node; sum per feature over all trees; normalize to 1. It is free, since it falls out of training. But it is computed on the training data, and deep trees keep splitting until leaves are pure, so they find "useful" splits on noise too. Our deliberately meaningless RowID column, a random number from 0 to 1,999, gets 2.9% of the importance, comparable to real features like Population. Features with many distinct values give the tree more split points to exploit, and get inflated.

Permutation importance is computed on held-out data. Take one column, shuffle it so its link to the target is destroyed, and measure how much the model's error goes up. If the model never really needed the feature, nothing changes. RowID drops to zero, and so do AveBedrms and Population, nearly. Use sklearn.inspection.permutation_importance. It costs extra predictions but is far more trustworthy.

Both methods measure what this particular model leans on, not what causes house prices. Latitude and Longitude illustrate another trap: when features are correlated, the forest can use either one, and the credit is split between them, so each looks less important than the pair is together. Shuffling one of a correlated pair also creates unrealistic rows. Treat importance as a debugging and communication tool, not as an explanation of the world.
-->

---
glowSeed: 628
---

# Practical Defaults

<div class="mt-2 text-sm">

| Hyperparameter | Controls | Starting point |
| --- | --- | --- |
| `n_estimators` | Number of trees B | A few hundred. Increase until OOB error stops falling. |
| `max_features` | m, decorrelation | Classifier: `"sqrt"` (default). Regressor: an integer near d/3; the default `1.0` is plain bagging. |
| `min_samples_leaf` | How deep each tree grows | Fully grown (defaults). Raise `min_samples_leaf` for very noisy data. |
| `oob_score` | Free validation estimate | `True` while tuning. |
| `n_jobs` | Parallel training | `-1`, all cores. |

</div>

<div class="grid grid-cols-2 gap-4 mt-4">
<div v-click border="2 solid teal-800" bg="teal-800/20" rounded-lg px-4 py-3>
<div class="font-bold text-teal-300 mb-1">A strong first baseline</div>
<div class="text-sm leading-relaxed opacity-90">Works on tabular data with little preprocessing: no scaling, and it tolerates irrelevant features.</div>
</div>
<div v-click border="2 solid amber-800" bg="amber-800/20" rounded-lg px-4 py-3>
<div class="font-bold text-amber-300 mb-1">Forgiving to tune</div>
<div class="text-sm leading-relaxed opacity-90">Tune m first. B only needs to be large enough.</div>
</div>
</div>

<!--
What to actually type. n_estimators is B: the default of 100 is often fine, a few hundred is safer, and the "How Many Trees?" curve tells you when to stop. max_features is m and is the hyperparameter worth tuning. For classifiers scikit-learn defaults to the square root of d. For regressors the default is 1.0, all features, which is bagging, not a random forest. Pass an integer near d/3. A float such as 1/3 is also accepted and is read as a fraction of the features, but scikit-learn rounds it down: with d = 8 that gives int(8/3) = 2, not 3.

min_samples_leaf (and max_depth) limit how deep each tree grows. Random forests normally use fully grown trees, since averaging takes care of the variance. On very noisy data, a minimum leaf size of 5 or so can help a little, and it makes the trees smaller and faster.

Why random forests are a standard first baseline for tabular data: trees do not care about feature scale, so there is no standardization step; they handle nonlinearity and interactions automatically; and feature subsampling plus averaging makes them fairly robust to irrelevant features. Compared with boosting, they are forgiving: reasonable defaults rarely go badly wrong, and adding trees never overfits.
-->

---
glowSeed: 629
---

# Bagging and Random Forests

<div class="mt-8"><div class="grid grid-cols-3 gap-4 mt-6">
<div v-click border="2 solid teal-800" bg="teal-800/20" rounded-lg p-4>
<div class="font-bold text-teal-300 mb-2">Bootstrap</div>
<div class="text-sm leading-relaxed opacity-90">Resample rows to get many training sets from one. ~36.8% of rows are left out of each.</div>
</div>
<div v-click border="2 solid blue-800" bg="blue-800/20" rounded-lg p-4>
<div class="font-bold text-blue-300 mb-2">Bagging</div>
<div class="text-sm leading-relaxed opacity-90">Average deep trees. Variance falls to the floor ρσ²; bias stays put.</div>
</div>
<div v-click border="2 solid amber-800" bg="amber-800/20" rounded-lg p-4>
<div class="font-bold text-amber-300 mb-2">Random forest</div>
<div class="text-sm leading-relaxed opacity-90">Sample m features per split. Lower ρ, lower floor. Tune m; out-of-bag error comes free.</div>
</div>
</div></div>

<div v-click class="mt-10 text-center text-lg" border="2 solid white/10" bg="white/5" rounded-lg px-6 py-4>Next: boosting trains weak learners sequentially, each correcting what remains wrong.</div>

<!--
Have students reproduce the chain in their own words, one problem and one fix per card. Bootstrap: we have one dataset and need many; resampling rows manufactures them, and leaves about a third of the rows out of each. Bagging: fit a low-bias, high-variance learner to each and average; variance falls until it hits the floor rho sigma squared, and bias does not move. Random forest: bagged trees stay correlated because they all choose the same strong splits; sampling m features per split lowers rho and so lowers the floor, at a small cost in each tree's accuracy, which is why m needs tuning. The out-of-bag rows give a free estimate of test error along the way.

Bridge to boosting. Everything in this deck was parallel and independent: B trees, each grown without knowledge of the others, combined only at the end, attacking variance. Boosting reverses all of that. It uses shallow, high-bias trees, grows them one after another, and builds each one to fix what the ensemble so far still gets wrong. Its target is bias. Keep the variance-versus-bias framing: boosting is bagging's mirror image on exactly that axis.
-->
