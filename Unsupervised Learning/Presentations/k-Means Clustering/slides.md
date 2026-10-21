---
theme: default
highlighter: shiki
css: unocss
colorSchema: dark
title: 'k-Means Clustering'
info: |
  ## k-Means Clustering
  Finding groups when there are no labels to check against
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
glowSeed: 710
---

# k-Means Clustering

### Finding groups when there are no labels to check against

<div class="mt-6 max-w-3xl mx-auto">
<HeroClusters />
</div>

<div class="opacity-80 text-lg">Unsupervised Learning · Foundations of Machine Learning</div>

<!--
This is the first deck of the Unsupervised Learning unit. Until now every model had a target column y and we could measure error against it. From today, there is no y. We get a table of rows and we are asked: is there structure here?

The animation is the whole deck in miniature. Three hundred unlabeled points light up in three groups around three centers. Nobody told the algorithm there were three groups or which point belongs where; it found a center for each group and gave every point to its nearest center. By the end of today you will know exactly how it does that, why it works, when it fails, and how to use it on real data.

Roadmap: what changes without labels → the k-means objective → Lloyd's algorithm, watched step by step and done by hand → why initialization matters and k-means++ → choosing K with the elbow and silhouettes → scaling and the failure cases → three real datasets: customer segmentation, image colors, and depot placement → when to reach for k-means.

Color code for the whole deck: each cluster gets one color, centroids are the large circles with a cross, and shaded regions are the area each centroid "owns". Every number on these slides comes from scripts/make_data.py in the deck folder, run with fixed seeds.
-->

---
glowSeed: 711
---

# Same Points, Two Reasonable Answers

<div class="grid grid-cols-[1.3fr_1fr] gap-8 items-center mt-2">
<div>
<GroupingToggle />
</div>
<div class="space-y-4 text-left">
<div border="2 solid white/5" bg="white/5" rounded-lg px-4 py-3>
<div class="font-bold text-amber-300">No y, no test accuracy</div>
<div class="text-sm opacity-85 mt-1">In supervised learning, held-out error tells us which model is better. Here there is nothing to compare against.</div>
</div>
<div v-click="2" border="2 solid white/5" bg="white/5" rounded-lg px-4 py-3>
<div class="font-bold text-teal-300">"Good" depends on the use</div>
<div class="text-sm opacity-85 mt-1">Two broad customer tiers or three targeted campaigns? Both splits are defensible. The data constrains the answer; it does not pick it.</div>
</div>
<div v-click="3" border="2 solid teal-800" bg="teal-800/20" rounded-lg px-4 py-3>
<div class="text-sm">So we need: <b>(1)</b> a precise definition of a good grouping, <b>(2)</b> an algorithm to find one, <b>(3)</b> tools to judge it without labels.</div>
</div>
</div>
</div>

<!--
Here are 300 points with no grouping at all. [click] k-means with two clusters; [click] with three.

Which is right? If you were told "there are three species", K = 3. If you have the budget for two marketing campaigns, K = 2 is the useful answer. In supervised learning this question never came up, because held-out accuracy settled it. Without labels, there is no held-out accuracy.

So the goal of the grouping matters. The data limits which groupings are sensible: nobody would split the top blob down the middle. But within those limits, the purpose decides.

[click] That gives the plan for the deck. First, a precise objective: what number does a good clustering make small? Second, an algorithm that makes it small. Third, diagnostics that work without labels: the elbow, silhouettes, stability. Keep the three in mind; every section maps to one of them.
-->

---
glowSeed: 712
---

# Where Clustering Shows Up

<div class="grid grid-cols-3 gap-4 mt-6 text-left">
<div v-click border="2 solid teal-800" bg="teal-800/20" rounded-lg px-4 py-3>
<div class="i-carbon-user-multiple text-2xl text-teal-300" />
<div class="font-bold mt-1">Customer segments</div>
<div class="text-sm opacity-85">Group accounts by what they buy, then design one offer per group.</div>
</div>
<div v-click border="2 solid blue-800" bg="blue-800/20" rounded-lg px-4 py-3>
<div class="i-carbon-color-palette text-2xl text-blue-300" />
<div class="font-bold mt-1">Image compression</div>
<div class="text-sm opacity-85">Replace millions of colors with a palette of K representative ones.</div>
</div>
<div v-click border="2 solid amber-800" bg="amber-800/20" rounded-lg px-4 py-3>
<div class="i-carbon-location text-2xl text-amber-300" />
<div class="font-bold mt-1">Facility placement</div>
<div class="text-sm opacity-85">Put K depots, stores or cell towers close to the people they serve.</div>
</div>
<div v-click border="2 solid violet-800" bg="violet-800/20" rounded-lg px-4 py-3>
<div class="i-carbon-document text-2xl text-violet-300" />
<div class="font-bold mt-1">Grouping documents</div>
<div class="text-sm opacity-85">Cluster text embeddings to find topics in support tickets or reviews.</div>
</div>
<div v-click border="2 solid orange-800" bg="orange-800/20" rounded-lg px-4 py-3>
<div class="i-carbon-chart-cluster-bar text-2xl text-orange-300" />
<div class="font-bold mt-1">Feature engineering</div>
<div class="text-sm opacity-85">Use the cluster id, or distance to each centroid, as an input to a supervised model.</div>
</div>
<div v-click border="2 solid red-800" bg="red-800/20" rounded-lg px-4 py-3>
<div class="i-carbon-search text-2xl text-red-300" />
<div class="font-bold mt-1">Exploration</div>
<div class="text-sm opacity-85">A first look at a new dataset: what kinds of rows are in here?</div>
</div>
</div>

<!--
Before the math, where this gets used. Click through these six.

[click] Customer segmentation is the textbook case, and we will do it on real wholesale data later today.
[click] Image color quantization: every pixel is a point in color space, and k-means picks the K colors that represent the image best. We will see this one live too.
[click] Facility placement: if you minimize the squared distance from people to the nearest depot, that is exactly the k-means objective. Our third real example.
[click] Documents: modern pipelines turn text into embedding vectors, and clustering those vectors is a common way to discover topics.
[click] Feature engineering: the cluster id, or the distances to each centroid, can be fed into a supervised model as new features.
[click] And exploration: the first thing many analysts do with a new table is cluster it to see what kinds of rows exist.

The common thread: in every case, we want a small number of representative points, and every row is summarized by the representative it is closest to.
-->

---
glowSeed: 713
---

# The Idea: Summarize Each Group by a Center

<div class="grid grid-cols-[1.3fr_1fr] gap-8 items-center mt-2">
<div>
<LloydStage :steps="[9]" :panel="false" lines :trails="false" />
</div>
<div class="space-y-4 text-left">
<div v-click border="2 solid white/5" bg="white/5" rounded-lg px-4 py-3>
<div class="font-bold text-teal-300">K centroids</div>
<div class="text-sm opacity-85 mt-1">Pick K points μ₁, …, μ<sub>K</sub> in feature space. Each is the "prototype" of one group.</div>
</div>
<div v-click border="2 solid white/5" bg="white/5" rounded-lg px-4 py-3>
<div class="font-bold text-blue-300">Nearest centroid wins</div>
<div class="text-sm opacity-85 mt-1">Every point belongs to the centroid it is closest to. The shaded cells show who owns which part of the plane.</div>
</div>
<div v-click border="2 solid white/5" bg="white/5" rounded-lg px-4 py-3>
<div class="font-bold text-amber-300">Short lines = good clustering</div>
<div class="text-sm opacity-85 mt-1">A clustering is good when every point is close to its own centroid.</div>
</div>
</div>
</div>

<!--
Here is the finished product on our three-blob data. Three centroids, the big circles. Every point has a line to the centroid it belongs to.

[click] The model is nothing more than K points in feature space. Each centroid is a prototype: one point that stands in for its whole group.

[click] Membership is the nearest-centroid rule. The shaded regions are called Voronoi cells: each one is the set of locations closer to that centroid than to any other. Notice that the borders are straight lines. That will matter later when we see where k-means fails.

[click] And quality: a good clustering is one where the lines are short. Every point is well represented by its prototype. The next slide turns "the lines are short" into a formula.

Connect to k-NN from the classification unit: there we compared a new point to every training point. Here we compare it to only K prototypes, which is why k-means scales to huge datasets.
-->

---
glowSeed: 714
clicks: 1
---

# Scoring a Clustering: The Objective J

<div class="grid grid-cols-[1.2fr_1fr] gap-8 items-center">
<div>
<ObjectiveCompare />
</div>
<div class="text-left space-y-4">
<div border="2 solid teal-800" bg="teal-800/20" rounded-lg px-4 py-1>

$$
J=\sum_{i=1}^{n}\big\lVert x_i-\mu_{c_i}\big\rVert^2
$$

</div>
<div class="text-sm space-y-2 opacity-90">
<div><b class="text-amber-300">cᵢ</b> ∈ {1, …, K}: which cluster point i is in</div>
<div><b class="text-teal-300">μₖ</b>: the centroid of cluster k</div>
<div>J is the total <b>squared length of all the lines</b>. Also called inertia or within-cluster sum of squares (WCSS).</div>
</div>
<div v-click border="2 solid white/5" bg="white/5" rounded-lg px-4 py-3 class="text-sm">
Two kinds of unknowns: the <b class="text-amber-300">assignments</b> cᵢ (discrete) and the <b class="text-teal-300">centroids</b> μₖ (continuous). We must choose both.
</div>
</div>
</div>

<!--
This is the k-means objective. For each point, take the squared distance to the centroid of its own cluster, and add them all up. Visually, J is the sum of the squared lengths of all these lines.

Right now the centroids are poor: this is a random starting configuration with every point assigned to its nearest centroid. J is about 4,433. [click] With the converged centroids, J drops to about 368. Same data, same K; the only difference is where the centroids sit.

Vocabulary: scikit-learn calls J inertia_, and you will also see within-cluster sum of squares, WCSS.

Point out the two kinds of unknowns. The assignments c_i are discrete: each point picks one of K labels. The centroids are continuous vectors. Minimizing J over both at once is hard; in fact, finding the exact global minimum is NP-hard in general. But each piece alone is easy, and that is the key to the algorithm. First, the centroid piece.
-->

---
glowSeed: 715
clicks: 2
---

# Why the Centroid Is the Mean

<div class="grid grid-cols-[1.25fr_1fr] gap-8 items-center">
<div>
<CenterCandidates />
</div>
<div class="text-left space-y-3">
<div class="text-sm opacity-85">Fix the members of one cluster. Where should its center go? There are three natural answers: the <b class="text-teal-300">mean</b> (average of each coordinate), the <b class="text-blue-300">median</b> (middle value of each coordinate), and the <b class="text-orange-300">middle</b> (center of the bounding box).</div>
<div v-click="2" class="text-sm opacity-90">Score each by the objective J, the total squared distance from every point to the center. The mean gives the smallest J, and no other point does as well.</div>
<div v-click="2" border="2 solid teal-800" bg="teal-800/20" rounded-lg px-4 py-1>

$$
\frac{dJ}{dc}=-2\sum_{i}(x_i-c)=0
\;\Rightarrow\;
c=\frac{1}{n}\sum_i x_i
$$

</div>
<div v-click="2" border="2 solid white/5" bg="white/5" rounded-lg px-4 py-2 class="text-xs opacity-80">
The median and the middle are not wrong, they just answer different questions: the median minimizes total <i>absolute</i> distance (k-medians), the middle minimizes the <i>largest</i> distance. Squared error is what k-means optimizes, so its center is the <b>mean vector</b>.
</div>
</div>
</div>

<!--
Fix which points are in a cluster. Where should we put its center?

Here is one lopsided cluster: a dense core with a tail. [click] Three candidates. The mean is the average of each coordinate. The median is the middle value of each coordinate, which resists outliers. The middle is the center of the box that contains the points, halfway between the extremes. They land in different places because this cluster is lopsided.

[click] Now score each with the k-means objective: the total squared distance from every point to the center. The mean has the smallest J. That is not luck: set the derivative of the sum of squares to zero and you get c equals the average. In d dimensions it works coordinate by coordinate, so the best centroid is the mean vector, which is where the name comes from.

The median and the middle are not bad centers. The median minimizes total absolute distance and gives k-medians, which is less sensitive to outliers. The middle minimizes the largest distance. They are optimal for different losses. k-means uses squared error, so its center is the mean.
-->

---
glowSeed: 716
---

# Lloyd's Algorithm: Alternate Two Easy Steps

<div class="grid grid-cols-[1fr_1.35fr] gap-6 mt-4 text-left">
<div class="space-y-4">
<div v-click border="2 solid amber-800" bg="amber-800/20" rounded-lg px-4 py-3>
<div class="font-bold text-amber-300">0 · Initialize</div>
<div class="text-sm opacity-85">Place K centroids, e.g. on K random data points.</div>
</div>
<div v-click border="2 solid blue-800" bg="blue-800/20" rounded-lg px-4 py-3>
<div class="font-bold text-blue-300">1 · Assign (fix μ, choose c)</div>
<div class="text-sm opacity-85">Each point joins its nearest centroid: c<sub>i</sub> = argmin<sub>k</sub> ‖x<sub>i</sub> − μ<sub>k</sub>‖².</div>
</div>
<div v-click border="2 solid teal-800" bg="teal-800/20" rounded-lg px-4 py-3>
<div class="font-bold text-teal-300">2 · Update (fix c, choose μ)</div>
<div class="text-sm opacity-85">Each centroid moves to the mean of its points.</div>
</div>
<div v-click border="2 solid white/5" bg="white/5" rounded-lg px-4 py-3>
<div class="font-bold">Repeat 1–2 until no point changes cluster</div>
</div>
</div>
<div v-click>

```python
import numpy as np

def kmeans(X, K, iters=100, seed=0):
    rng = np.random.default_rng(seed)
    mu = X[rng.choice(len(X), K, replace=False)]
    for _ in range(iters):
        # assign: squared distance to each centroid
        d = ((X[:, None, :] - mu[None]) ** 2).sum(-1)
        c = d.argmin(axis=1)
        # update: mean of each cluster
        new = np.array([X[c == k].mean(0) for k in range(K)])
        if np.allclose(new, mu):
            break
        mu = new
    return c, mu
```

</div>
</div>

<!--
Here is the trick. J has two kinds of unknowns, and we cannot easily optimize both at once. But if we fix one, the other is easy.

[click] Start by placing K centroids somewhere. The simplest choice: K randomly chosen data points.
[click] Assign step. Hold the centroids fixed and choose the assignments. Each point's term in J only depends on its own assignment, so each point independently picks its nearest centroid. That is the best possible assignment for these centroids.
[click] Update step. Hold the assignments fixed and choose the centroids. We just showed the best center for a fixed set of points is their mean.
[click] Repeat until the assignments stop changing.

This is called Lloyd's algorithm, from Stuart Lloyd at Bell Labs in 1957, though it was only published in 1982. When people say "k-means" they almost always mean this algorithm.

[click] The whole thing is about ten lines of NumPy. The distance line uses broadcasting to build an n-by-K matrix of squared distances in one shot. This version does not handle empty clusters; scikit-learn does. Next, let's watch it run.
-->

---
glowSeed: 717
clicks: 9
---

# Watch It Run

<LloydStage />

<!--
Same three-blob data. Each click advances one half-step. Keep an eye on the J chart on the right.

Start: three centroids dropped on random data points. This start is deliberately bad: two centroids landed close together in the bottom-right blob, one sits below everything, and the cell borders cut straight through the groups.

[click] Assign: every point takes the color of its nearest centroid. J is about 4,433.
[click] Update: each centroid jumps to the mean of its colored points. The dashed trails show where they came from. J drops to about 1,226 without any point changing color yet.
[click] Assign again: points near the moving borders switch color. J falls to about 901.
[click] Update, about 589. [click] Assign, about 420. [click] Update. [click] Assign. [click] Update. Notice the steps get smaller as the centroids settle into the middle of each blob.
[click] The final assign step changes nothing, so the algorithm stops. J is about 368, the best value we found with ten random restarts.

Point out the J chart: the curve only ever goes down, after every single half-step. The next slides show why that is guaranteed.
-->

---
glowSeed: 718
clicks: 4
---

# Worked Example: One Iteration by Hand

<HandExample />

<!--
Six points, K = 2. We start with the centroids on points A and D. Have students do this with you; it takes two minutes.

[click] Compute the distance from every point to both centroids. For example, C at (3, 3.5) is 3.20 from mu-1 and 4.03 from mu-2.
[click] Assign each point to the smaller distance: A, B and C go to cluster 1; D, E and F go to cluster 2. With these centroids J is 22.00.
[click] Update: each centroid moves to the mean of its points. Mu-1 becomes the mean of A, B, C, which is (1.83, 2.17). Mu-2 becomes the mean of D, E, F, which is (4.33, 5.67). J drops to 9.17.
[click] Assign again with the new centroids. C is now 1.77 from mu-1 and 2.54 from mu-2, so it stays in cluster 1. No point changes cluster. Converged after one iteration.

Point out that C moved closer to its own centroid. The update step did not just help the points that were already close; it pulled the centroid toward the middle of its group.
-->

---
glowSeed: 719
---

# Why Lloyd's Algorithm Always Stops

<div class="grid grid-cols-[1.2fr_1fr] gap-8 items-center mt-2">
<div>
<JBars />
</div>
<div class="space-y-3 text-left">
<div v-click border="2 solid blue-800" bg="blue-800/20" rounded-lg px-4 py-3>
<div class="font-bold text-blue-300">Assign can't raise J</div>
<div class="text-sm opacity-85">Each point switches only to a <i>closer</i> centroid.</div>
</div>
<div v-click border="2 solid teal-800" bg="teal-800/20" rounded-lg px-4 py-3>
<div class="font-bold text-teal-300">Update can't raise J</div>
<div class="text-sm opacity-85">The mean is the best center for a fixed group.</div>
</div>
<div v-click border="2 solid amber-800" bg="amber-800/20" rounded-lg px-4 py-3>
<div class="font-bold text-amber-300">Finitely many groupings</div>
<div class="text-sm opacity-85">J strictly drops until nothing changes, and no grouping can repeat, so the loop must end.</div>
</div>
<div v-click class="text-sm opacity-85">In practice: a handful of iterations. Typical cost per iteration: O(n·K·d).</div>
</div>
</div>

<!--
This chart is J after every half-step of the run we just watched. Blue bars are after an assign step, teal after an update step. Every bar is lower than or equal to the previous one. That is not luck.

[click] The assign step: each point either keeps its centroid or moves to a strictly closer one. Each term of J can only shrink.
[click] The update step: for a fixed group, the mean minimizes the sum of squared distances, so moving the centroid there can only lower that group's contribution.
[click] And there are only finitely many ways to split n points into K groups. Every time the assignments change, J strictly drops, so we can never come back to a grouping we had before. Eventually the assignments stop changing and the loop ends.

[click] In theory the number of iterations can be huge, but in practice it is a handful, usually under 20. Each iteration computes n times K distances in d dimensions, so k-means scales to millions of rows. That speed is a big part of why it is so popular.

But notice what we did not prove: that it finds the lowest J. Next slide.
-->

---
glowSeed: 720
clicks: 2
---

# But Only to a Local Minimum

<div class="text-sm opacity-85 -mt-1 mb-3">Six well-separated blobs, K = 6. Three random starts, each run until it stops:</div>

<InitShowcase :show="$clicks + 1" />

<div v-click="2" class="mt-4 text-sm" border="2 solid red-800" bg="red-800/20" rounded-lg px-4 py-2>
Stuck runs are stable: moving any one centroid a little would make J worse, so Lloyd's algorithm never escapes. The result depends on where you start.
</div>

<!--
Lloyd's algorithm only goes downhill, which means it stops at the bottom of whatever valley it starts in.

Six obvious blobs, K = 6. Three different random starts.
The first start finds the six groups, J about 1,145.
[click] The second gets stuck: one centroid is splitting a blob in two while another centroid is covering two blobs at once. J about 2,473, more than double.
[click] The third is worse still, about 5,496.

Why doesn't the algorithm fix itself? Look at the centroid covering two blobs. It sits in the gap between them, at their mean. The two centroids that share a blob each own half of it. No single assign or update step improves things; to escape, a centroid would have to jump across the plot, and Lloyd's algorithm only moves centroids to the mean of their current members.

So the answer depends on the starting point. Two standard fixes: start smarter, and start many times and keep the best. Both are next.
-->

---
glowSeed: 721
clicks: 5
---

# k-means++: Spread Out the Starting Centroids

<div class="grid grid-cols-[1.35fr_1fr] gap-8 items-center">
<div>
<KppSeeding />
</div>
<div class="text-left space-y-3">
<div border="2 solid white/5" bg="white/5" rounded-lg px-4 py-3 class="text-sm">
<div><b class="text-amber-300">1.</b> First centroid: a random data point.</div>
<div class="mt-1"><b class="text-amber-300">2.</b> Every point gets a weight D(x)²: its squared distance to the <i>nearest</i> centroid chosen so far.</div>
<div class="mt-1"><b class="text-amber-300">3.</b> Pick the next centroid at random with probability ∝ D(x)².</div>
<div class="mt-1"><b class="text-amber-300">4.</b> Repeat until there are K.</div>
</div>
<div border="2 solid teal-800" bg="teal-800/20" rounded-lg px-4 py-1>

$$
P(\text{pick } x)=\frac{D(x)^2}{\sum_{x'} D(x')^2}
$$

</div>
<div class="text-xs opacity-75">Bigger, brighter amber dots = more likely to be picked next. The dashed ring marks the point that was actually drawn.</div>
</div>
</div>

<!--
k-means++ (Arthur and Vassilvitskii, 2007) is a smarter way to place the starting centroids. It is the default in scikit-learn.

The first centroid is a random data point. Every other point now gets a weight equal to its squared distance to the nearest chosen centroid. Look at the amber dots: points in the same blob as centroid 1 are tiny, because they are already covered. Points in far-away blobs are big and bright.

[click] The second centroid is drawn at random with probability proportional to those weights, so it almost always lands in an uncovered blob. Weights are recomputed: now two blobs are covered.
[click] Third. [click] Fourth. [click] Fifth. [click] Sixth: one centroid per blob, before Lloyd's algorithm has even started.

It is still random: a point in a covered blob can be picked, just rarely. That is the point. Pure "pick the farthest point" would always grab outliers; sampling by D-squared favors far-away regions that contain many points.

The guarantee: the expected J of a k-means++ start is within a factor of O(log K) of the optimum. Lloyd's algorithm then improves from there.
-->

---
glowSeed: 722
clicks: 1
---

# Random Starts vs. k-means++

<div class="grid grid-cols-[1.25fr_1fr] gap-8 items-center">
<div>
<InitOutcome :pp="$clicks >= 1" />
</div>
<div class="text-left space-y-3">
<div class="text-sm opacity-85">50 single runs each (n_init=1) on the six-blob data. Each bar splits those runs into ones that found the best solution and ones that got stuck.</div>

```python
from sklearn.cluster import KMeans

km = KMeans(
    n_clusters=6,
    init="k-means++",  # the default
    n_init=10,         # 10 starts, keep the lowest J
    random_state=0,
).fit(X)
km.inertia_            # J of the best run
```

<div class="text-xs opacity-75">The default n_init="auto" runs once with k-means++ and 10 times with random starts.</div>
</div>
</div>

<!--
Fifty independent runs with random initialization. 26 found the best solution, with J about 1,145; 24 got stuck in a local minimum.

[click] Now fifty runs with k-means++ seeding. All 50 reach the best solution. And they get there faster: about 3.1 iterations on average, versus about 7.5 for random starts, because the starting centroids are already close to the answer.

The second fix is restarts. n_init tells scikit-learn to run the whole algorithm several times from different starts and keep the run with the lowest J. That is cheap insurance; on hard real data, set it to 10 or more. Always set random_state when you need reproducible results, for example in a report.

A caution: on real data, even k-means++ with restarts does not guarantee the global optimum. It just makes bad local minima much rarer.
-->

---
glowSeed: 724
clicks: 3
---

# The Silhouette of One Point

<SilhouetteGeometry />

<!--
Choosing K needs a score we can compute without labels. One is J itself; the other is the silhouette. The silhouette asks, for each point: is it closer to its own cluster than to the next-best cluster?

Take this highlighted point on the edge of the blue cluster, right next to the teal one.
[click] a is its average distance to the other members of its own cluster, the blue lines.
[click] b is its average distance to the members of the nearest other cluster, the teal lines.
[click] The silhouette is b minus a, divided by the larger of the two. Here it is about 0.25: closer to its own cluster, but not by much.

Read the scale. Near +1: the point is far closer to its own cluster than to any other, so it is deep inside a well-separated cluster. Near 0: it sits on the border. Negative: it is closer, on average, to another cluster than to its own, so it was probably put in the wrong cluster.

The silhouette score of a whole clustering is the mean over all points; scikit-learn's silhouette_score. It costs O(n²) distance computations, so on big data compute it on a random sample.
-->

---
glowSeed: 723
clicks: 8
---

# Choosing K: The Elbow and the Silhouette

<KSweep />

<!--
Now the hardest practical question: how many clusters? K is a hyperparameter, and without labels we cannot cross-validate accuracy. We have the silhouette from the last slide; the other tool is the elbow, which is just the objective J plotted against K.

Each click adds one more cluster on the six-blob data. Watch the left panel and the two curves.

K = 1: everything in one cluster, J is enormous. [click] K = 2. [click] 3. [click] 4. [click] 5. Each new centroid takes over a blob that was being shared, and J falls a lot. [click] K = 6: each blob has its own centroid. [click] K = 7: the extra centroid has to split a blob that was already fine. J falls only a little. [click] K = 8, same story.

Top curve, the elbow: J always goes down as K grows, since with K = n every point is its own centroid and J = 0. So we cannot just minimize J. We look for the elbow: the K after which adding clusters stops paying off. Here it is clearly at 6.

Bottom curve, mean silhouette: the average of the per-point score we just defined, between -1 and 1, which does not automatically improve with K. It peaks at 6, at 0.686. [click] Both diagnostics agree here.

On real data the elbow is often much softer and the silhouette flatter. We will see that honestly in the customer example.
-->

---
glowSeed: 726
---

# Choosing K in Practice

<div class="grid grid-cols-2 gap-x-5 gap-y-3 mt-2 text-left items-start">
<div v-click>
<div border="2 solid amber-800" bg="amber-800/20" rounded-lg px-4 py-3>
<div class="font-bold text-amber-300">Elbow of J</div>
<div class="text-sm opacity-85">Quick and cheap. J always falls with K; look for where it stops falling fast. Often there is no sharp elbow.</div>
</div>
<div class="mt-2 px-6"><KCurve which="J" /></div>
</div>
<div v-click>
<div border="2 solid teal-800" bg="teal-800/20" rounded-lg px-4 py-3>
<div class="font-bold text-teal-300">Silhouette</div>
<div class="text-sm opacity-85">Mean score and the per-point plot. Favors compact, well-separated groups.</div>
</div>
<div class="mt-2 px-6"><KCurve which="sil" /></div>
</div>
<div v-click border="2 solid blue-800" bg="blue-800/20" rounded-lg px-4 py-3>
<div class="font-bold text-blue-300">Stability</div>
<div class="text-sm opacity-85">Refit with another seed or a bootstrap sample. Real structure comes back; noise moves around.</div>
</div>
<div v-click border="2 solid violet-800" bg="violet-800/20" rounded-lg px-4 py-3>
<div class="font-bold text-violet-300">The use case</div>
<div class="text-sm opacity-85">Can you name and act on each cluster? Three segments you can describe beat eight you can't.</div>
</div>
</div>

<div v-click class="mt-5 text-center text-sm" border="2 solid white/5" bg="white/5" rounded-lg px-4 py-2>
No method finds the "true" K. Use several, and report which K you chose and why.
</div>

<!--
Four tools, in roughly the order you would use them.

[click] The elbow of J: almost free to compute, since you get inertia_ from every fit. Its weakness is that the elbow is often a gentle curve, and two people will point to different K.
[click] The silhouette: more principled, and scikit-learn's silhouette_samples gives the per-point scores if you want to see which clusters are weak. Its weakness: it rewards round, well-separated clusters, which is the same assumption k-means makes, so it will not rescue you when that assumption is wrong.
[click] Stability: refit with different seeds or on bootstrap resamples and check whether the same clusters come back, for example with the adjusted Rand index between runs. We will use this on the real data.
[click] And the use case: a clustering is a tool for a decision. If you cannot describe a cluster in words or act on it differently, it probably should not be its own cluster.

[click] The honest summary: there is no true K to discover in most real data. Pick a K that the diagnostics support and the application can use, and say why.
-->

---
glowSeed: 727
clicks: 2
---

# Distance Is the Model: Scale Your Features

<div class="grid grid-cols-[1.1fr_1fr] gap-6 items-center">
<div>
<ScalingMorph />
</div>
<div class="text-left space-y-3 text-sm">
<div border="2 solid white/5" bg="white/5" rounded-lg px-4 py-3>
<b class="text-red-300">Raw units.</b> Proline spans ~1,400 units, flavanoids ~5. Euclidean distance is almost all proline, so k-means just slices along the proline axis.
</div>
<div v-click="1" border="2 solid white/5" bg="white/5" rounded-lg px-4 py-3>
<b class="text-amber-300">Standardized view, same clusters.</b> The raw clusters are vertical bands: flavanoids was ignored.
</div>
<div v-click="2" border="2 solid teal-800" bg="teal-800/20" rounded-lg px-4 py-3>
<b class="text-teal-300">Re-cluster after scaling.</b> Both features count, and the clusters line up much better with the three grape varieties.
</div>
</div>
</div>

<!--
Remember from k-NN: any distance-based method depends on feature scale. k-means is no exception, and here is how dramatic it can be.

Two features from the wine dataset. Proline ranges from about 278 to 1,680. Flavanoids ranges from about 0.3 to 5. In this first view both axes use the same units, which is what Euclidean distance actually sees: the data is a flat line. k-means with K = 3 cuts that line into three pieces along proline. Agreement with the true grape variety, measured by the adjusted Rand index, is 0.37.

[click] Same points, same colors, now plotted after standardizing each feature to mean 0 and standard deviation 1. The raw clusters are vertical bands. Flavanoids played no role.

[click] Now re-run k-means on the standardized data. The clusters use both features, and agreement with the grape varieties rises to 0.60.

The rule: standardize before k-means unless the features are already in comparable units, like latitude and longitude, or the RGB channels of a pixel. The labels here are only used to check; k-means never saw them.
-->

---
glowSeed: 728
clicks: 4
---

# Where k-Means Fails

<FailureGallery :show="$clicks + 1" :truth="$clicks >= 4" />

<div class="mt-4 text-sm text-center opacity-90">
<span v-if="$clicks < 4">k-means result with its cells. ARI = agreement with the true groups (1 = perfect).</span>
<span v-else class="text-teal-300">The true groups: what k-means should have found.</span>
</div>

<!--
k-means makes strong assumptions, and when the data violates them it fails quietly: you still get K neat clusters, just the wrong ones.

Curved shapes, the two moons. k-means cuts straight across both moons. Adjusted Rand index about 0.23.
[click] Unequal spread: one wide cluster and two small tight ones. k-means splits the wide cluster in half and lumps the two tight ones together, because that lowers J more: the wide cluster contributes most of the squared distance, so spending two centroids on it pays off. ARI about 0.28.
[click] Stretched clusters: two long parallel ellipses. k-means assumes every direction counts the same, so it cuts across them, ARI about 0.01.
[click] Outliers: the three blobs plus 15 scattered points, with K = 4. The fourth centroid is wasted on a handful of outliers, and outliers also drag centroids, because the mean is sensitive to extreme values.

[click] And here are the true groups for comparison.

The common thread: k-means works best when clusters are compact, roughly round, similar in size and spread, and the data has few outliers. The next slide shows why straight borders are unavoidable.
-->

---
glowSeed: 729
---

# Why: Every Border Is a Straight Line

<div class="grid grid-cols-[1fr_1fr] gap-6 items-center">
<div>
<ClusterPlot v-bind="moons" cells frame :w="500" :h="340" :r="3" label="k-means on two moons: a single straight border between the two centroids" />
</div>
<div class="text-left space-y-3">
<div class="text-sm opacity-85">Every point goes to its nearest centroid. So the border between two clusters is the set of points <b>exactly as far from one centroid as from the other</b>.</div>
<div v-click class="text-sm opacity-90">That set is a <b class="text-teal-300">straight line</b>: the perpendicular bisector of the two centroids. It passes through their midpoint at a right angle.</div>
<div v-click class="text-sm opacity-90">A cluster is everything on its own side of each of its borders, so it is always a <b class="text-amber-300">convex</b> region. No placement of centroids can wrap k-means around a moon.</div>
<div v-click border="2 solid white/5" bg="white/5" rounded-lg px-4 py-2 class="text-xs opacity-85">Next deck: hierarchical and density-based clustering define clusters by connectivity instead, and can follow curved shapes.</div>
</div>
</div>

<script setup>
import fails from './data/fails.json'
const moons = { pts: fails.moons.pts, lab: fails.moons.frames[0].lab, centroids: fails.moons.frames[0].c }
</script>

<!--
Why the failures on the last slide were unavoidable.

k-means gives every point to its nearest centroid. So where does one cluster stop and the next start? At the points that are exactly as far from one centroid as from the other. Picture two centroids: the set of points equally far from both is a straight line, the perpendicular bisector. It crosses the midpoint between the centroids at a right angle. (If you want the algebra: expand the two squared distances, the x-squared terms cancel, and what is left is linear in x.)

[click] So the border between any two clusters is a straight line in 2D, a flat plane in higher dimensions.
[click] Each cluster is the set of points on the right side of all its borders, an intersection of half-planes, and that is always convex. A moon is not convex. However you place the centroids, k-means cannot carve out a moon.

This is the same story as linear classifiers in the classification unit: the decision boundary is linear in the original features.

[click] Next deck picks up exactly here: methods that define clusters by who is connected to whom, rather than by distance to a center.
-->

---
layout: center
glowSeed: 730
class: text-center
---

# k-Means on Real Data

<div class="opacity-80 text-lg mt-2">Three datasets where k-means is a good fit</div>

<div class="grid grid-cols-3 gap-6 mt-10 text-left max-w-4xl mx-auto">
<div border="2 solid amber-800" bg="amber-800/20" rounded-lg px-4 py-3>
<div class="i-carbon-shopping-cart text-2xl text-amber-300" />
<div class="font-bold mt-1">Customer segments</div>
<div class="text-sm opacity-85">440 wholesale clients, 6 spending categories</div>
</div>
<div border="2 solid blue-800" bg="blue-800/20" rounded-lg px-4 py-3>
<div class="i-carbon-image text-2xl text-blue-300" />
<div class="font-bold mt-1">Image colors</div>
<div class="text-sm opacity-85">153,600 pixels in RGB space</div>
</div>
<div border="2 solid teal-800" bg="teal-800/20" rounded-lg px-4 py-3>
<div class="i-carbon-map text-2xl text-teal-300" />
<div class="font-bold mt-1">Depot placement</div>
<div class="text-sm opacity-85">20,640 California locations</div>
</div>
</div>

<!--
Now three real examples. They were chosen because they are cases where k-means is a good tool, and each shows a different practical lesson.

Customer segmentation: real business data, skewed and messy, where preprocessing and choosing K are the hard parts, and where there is no single right answer.

Image colors: a case where the k-means objective is exactly the goal, since we want K colors that minimize the squared color error.

Depot placement: geographic coordinates, where Euclidean distance has a real meaning in kilometers and the centroids are literal locations.

Before the data, one slide of scikit-learn so the code on the next slides reads easily.
-->

---
glowSeed: 731
---

# k-Means in scikit-learn

```python {6-9|10|11|12|13|all}
from sklearn.cluster import KMeans
from sklearn.pipeline import make_pipeline
from sklearn.preprocessing import StandardScaler

# X: (n_rows, n_features) numeric array or DataFrame, no labels
model = make_pipeline(
    StandardScaler(),
    KMeans(n_clusters=4, n_init=10, random_state=0),
)
labels = model.fit_predict(X)      # cluster id (0..3) for every row
km = model[-1]; km.inertia_        # J, measured on the scaled data
centers = model[0].inverse_transform(km.cluster_centers_)  # back to original units
model.predict(X_new)               # nearest centroid for new rows
```

<div class="grid grid-cols-2 gap-4 mt-4 text-sm text-left">
<div v-click border="2 solid white/5" bg="white/5" rounded-lg px-4 py-2>
<b class="text-teal-300">Big data:</b> <code>MiniBatchKMeans</code> updates centroids from small random batches. Much faster, slightly higher J.
</div>
<div v-click border="2 solid white/5" bg="white/5" rounded-lg px-4 py-2>
<b class="text-amber-300">Not a classifier:</b> cluster ids are arbitrary names. Cluster 2 in one run may be cluster 0 in the next.
</div>
</div>

<!--
The scikit-learn API in one block.

Put the scaler and KMeans in a pipeline. Scaling is part of the model: new data must be scaled with the same means and standard deviations. n_init=10 runs ten k-means++ starts and keeps the best; random_state makes it reproducible.
[click] fit_predict returns the cluster id for every row.
[click] inertia_ is J, measured on the scaled data, not the original units.
[click] The centroids live in scaled space. To describe a cluster in original units, which is what a stakeholder wants, undo the scaling with the scaler's inverse_transform.
[click] predict assigns new rows to the nearest centroid. That is how you use a segmentation in production: fit once, then label new customers as they arrive.
[click] And the whole block together: about eight lines from raw table to segments.

[click] For millions of rows, MiniBatchKMeans updates centroids from small random batches. It is often an order of magnitude faster, at the cost of a slightly higher J.
[click] And remember the ids are arbitrary. Never compare cluster 2 across two runs without matching them first.
-->

---
glowSeed: 732
clicks: 1
---

# Example 1: Wholesale Customers

<div class="grid grid-cols-[1.35fr_1fr] gap-6 items-center">
<div>
<SkewMorph :log="$clicks >= 1" />
</div>
<div class="text-left space-y-3 text-sm">
<div border="2 solid white/5" bg="white/5" rounded-lg px-4 py-3>
440 clients of a Portuguese food distributor. One row per client: <b>annual spend</b> on 6 product categories. Also a <b class="text-amber-300">Channel</b> column (hotel/restaurant/café vs. retail) that we <b>hide from k-means</b> and keep for checking.
</div>
<div border="2 solid red-800" bg="red-800/20" rounded-lg px-4 py-3>
<b class="text-red-300">Raw spend is heavily skewed.</b> A few huge accounts would dominate every distance.
</div>
<div v-click border="2 solid teal-800" bg="teal-800/20" rounded-lg px-4 py-3>
<b class="text-teal-300">log(1 + spend), then standardize.</b> Now "twice as much" counts the same at every scale.
</div>
</div>
</div>

<!--
Our first real dataset: the Wholesale Customers data from the UCI repository. 440 clients of a food distributor in Portugal. Each row is one client's annual spending, in monetary units, on six categories: fresh food, milk, grocery, frozen, detergents and paper, and delicatessen.

There is also a Channel column: whether the client is a hotel, restaurant or café, or a retailer. We will not give that to k-means. We keep it aside to check, afterwards, whether the clusters mean something.

Each row of dots is one category, one dot per client, scaled to the largest account. Raw spending is extremely skewed: most clients are bunched near zero and a few giant accounts stretch the axis. In Euclidean distance, those giants would dominate everything.

[click] Take the log of one plus spending, and the dots spread out into roughly symmetric clouds. On a log scale, a client who spends twice as much as another is the same distance away whether we are talking about 1,000 versus 2,000 or 10,000 versus 20,000. After the log, we standardize as usual.

This preprocessing step is the biggest single decision in most real clustering work.
-->

---
glowSeed: 733
---

# Wholesale: How Many Segments?

<div class="grid grid-cols-[1fr_1.15fr] gap-8 items-center">
<div>
<WholesaleSweep />
</div>
<div class="text-left space-y-3">

```python
import numpy as np, pandas as pd
from sklearn.preprocessing import FunctionTransformer

df = pd.read_csv("wholesale_customers.csv")
spend = df.drop(columns=["Channel", "Region"])
model = make_pipeline(
    FunctionTransformer(np.log1p), StandardScaler(),
    KMeans(n_clusters=4, n_init=10, random_state=0))
df["segment"] = model.fit_predict(spend)
```

<div v-click border="2 solid white/5" bg="white/5" rounded-lg px-4 py-2 class="text-sm">
<b class="text-amber-300">No sharp elbow</b>, and the silhouette peaks at <b>K = 2</b> (0.29), far below the toy data. Real customers form overlapping groups.
</div>
<div v-click border="2 solid teal-800" bg="teal-800/20" rounded-lg px-4 py-2 class="text-sm">
We pick <b>K = 4</b> for the marketing use, and check that it is <b>stable</b>: the median agreement across 20 single-start refits is ARI 0.83.
</div>
</div>
</div>

<!--
Here is what choosing K looks like on real data, and it is much less tidy than the six blobs.

The code: a FunctionTransformer applies log1p, then the scaler, then k-means, all in one pipeline. We drop Channel and Region so k-means never sees them.

[click] The J curve on the left bends gently with no clear elbow. The mean silhouette is highest at K = 2, at 0.29, and hovers near 0.19 to 0.26 after that. For comparison, the dashed line is our three-blob toy data at 0.557. That is typical: real customers do not form separate blobs; they form a continuum with denser regions.

[click] So the metrics alone do not decide. K = 2 is the most compact split. We will look at it on the next slide. For a marketing team, four segments are more useful, so we try K = 4 and check stability: refitting with 20 different seeds, each with a single start, the median agreement with our solution is an adjusted Rand index of 0.83. The worst seed only reached 0.36, which is exactly why we use n_init=10.

This is the honest workflow: metrics narrow the range, the use case chooses within it, and stability checks keep you from building on noise.
-->

---
glowSeed: 734
clicks: 1
---

# Wholesale: The Segments in 3D

<div class="grid grid-cols-[1.2fr_1fr] gap-6 items-center">
<div>
<WholesaleCloud :by="$clicks >= 1 ? 'channel' : 'cluster'" :width="470" :height="380" />
</div>
<div class="text-left space-y-3 text-sm">
<div class="text-xs opacity-70">3 of the 6 features, log scale. Drag to rotate, hover for values.</div>
<div border="2 solid white/5" bg="white/5" rounded-lg px-4 py-3 style="min-height: 7.2em">
<span v-if="$clicks < 1"><b>Colored by k-means segment</b> (K = 4). The segments are regions of one continuous cloud, not separate islands.</span>
<span v-else><b>Colored by Channel</b>, which k-means never saw: <span class="text-amber-300 font-bold">hotel/restaurant/café</span> vs <span class="text-blue-300 font-bold">retail</span>.</span>
</div>
<div v-click border="2 solid teal-800" bg="teal-800/20" rounded-lg px-4 py-3>
K = 2 recovers the channel split for <b class="text-teal-300">85.9%</b> of clients: 244 + 134 of 440, without ever seeing that column.
</div>
</div>
</div>

<!--
Here are the 440 clients in three of the six dimensions, all on a log scale: fresh, grocery, and detergents and paper. The cloud orbits slowly; drag to rotate it yourself, and hover any point to see that client's actual spending.

Colored by the four k-means segments. Notice there are no gaps between the colors. The segments are regions of one continuous cloud. k-means will always draw borders, even when the data has no gaps. That is a feature for segmentation and a warning for interpretation.

[click] Now colored by Channel instead, the column we held out. Retailers, in blue, sit high on grocery and detergents; hotels, restaurants and cafés sit high on fresh. The structure k-means found lines up with a real business distinction.

Quantify it: with K = 2, one cluster contains 244 food-service clients and 8 retailers, the other 134 retailers and 54 food-service clients. That is 85.9% agreement with Channel, from spending alone. This is the right way to use labels with clustering: as an after-the-fact sanity check, never as an input.
-->

---
glowSeed: 735
clicks: 2
---

# Wholesale: Naming the Segments

<WholesaleProfiles :show="$clicks >= 1 ? 4 : 0" :channel="$clicks >= 2" />

<div class="grid grid-cols-3 gap-4 mt-4 text-xs text-left opacity-90">
<div><span class="inline-block w-3 h-3 rounded mr-1" style="background: rgba(45,212,191,.7)" /> above-average spend (standardized log)</div>
<div><span class="inline-block w-3 h-3 rounded mr-1" style="background: rgba(248,113,113,.7)" /> below-average spend</div>
<div>numbers = median annual spend (m.u.)</div>
</div>

<!--
A clustering is only useful once you can describe each cluster. The standard tool is a profile table: one row per cluster, one column per feature. Cell color is the cluster's average standardized log spend, teal above average and red below; the number is the median spend in the original units.

[click] Reading the rows, which are ordered by total spend:
- 132 clients spend little on everything except fresh and frozen. Small food-service accounts.
- 61 clients spend almost nothing on fresh and frozen but a lot on grocery, milk and detergents: small grocery-type shops.
- 129 clients are the big fresh-food buyers, with high frozen and deli too: restaurants and hotels.
- 118 clients spend heavily on grocery, milk and detergents, and fair amounts on fresh: big grocery retailers.

The names are ours. k-means gives numbers; a human gives meaning, and should check that the name fits the data.

[click] The last column checks the names against the held-out Channel. The food-service segments are almost entirely hotels, restaurants and cafés, 131 of 132 and 122 of 129. The big retail segment is 94 of 118 retail. The small-shop segment is mixed, 40 retail and 21 food-service, which is a useful finding in itself: some cafés buy like small shops.

Action: each row can now get its own pricing, delivery schedule or sales contact.
-->

---
glowSeed: 736
clicks: 1
---

# Example 2: Pixels Are Points in Color Space

<div class="grid grid-cols-[1.25fr_1fr] gap-6 items-center">
<div>
<PixelCloud :quantized="$clicks >= 1" :width="470" :height="400" />
</div>
<div class="text-left space-y-3 text-sm">
<div border="2 solid white/5" bg="white/5" rounded-lg px-4 py-3>
Every pixel is a 3D point: <span class="text-red-300 font-bold">R</span>, <span class="text-green-300 font-bold">G</span>, <span class="text-blue-300 font-bold">B</span>. Here, 2,500 pixels of a photo, each drawn in its own color.
</div>
<div v-click border="2 solid teal-800" bg="teal-800/20" rounded-lg px-4 py-3>
<b class="text-teal-300">k-means with K = 8:</b> the large spheres are the centroids. Each pixel is redrawn in its centroid's color.
</div>
<div class="text-xs opacity-75">Why it fits: all three features share one unit (0–255), so no scaling, and squared color error is exactly what we want to minimize.</div>
</div>
</div>

<!--
Second example: color quantization. Take a photo. Every pixel has a red, green and blue value between 0 and 255, so every pixel is a point in a 3D cube. Here are 2,500 pixels from scikit-learn's sample photo of a Chinese temple, each drawn in its own color. Most pixels lie along the gray diagonal from black to white: dark foliage and shadows at the bottom, pale sky and haze at the top. The orange-red roof tiles branch off toward high red. Drag to rotate.

[click] Run k-means with K = 8. The large spheres are the eight centroids, and each pixel is now drawn in the color of its centroid. Eight colors now stand in for the whole photo.

Why is this a good k-means problem? First, all three features are in the same units, so there is no scaling question. Second, the objective is exactly right: J is the total squared color error between the original pixel and its replacement. Minimizing J is literally making the compressed image look as close as possible to the original. Third, there is a lot of data, and k-means scales.
-->

---
glowSeed: 737
clicks: 5
---

# Color Quantization: K Colors for 153,600 Pixels

<QuantizeGallery />

```python
from sklearn.utils import shuffle
img = load_sample_image("china.jpg") / 255         # (427, 640, 3)
pixels = img.reshape(-1, 3)                        # one row per pixel
sample = shuffle(pixels, random_state=0, n_samples=5000)
km = KMeans(n_clusters=16, n_init=4, random_state=0).fit(sample)
quantized = km.cluster_centers_[km.predict(pixels)].reshape(img.shape)
```

<!--
Here is the full picture, downsized to 480 by 320 pixels.

[click] K = 2: two colors, light and dark, so each pixel needs only 1 bit to say which color it is, instead of 24. You can still recognize the scene.
[click] K = 4: the lake and haze separate from the sky, but there is still no red: all four centroids sit near the gray diagonal where most pixels are.
[click] K = 8: the orange roof finally gets its own centroid. Already a convincing poster.
[click] K = 16: hard to tell from the original at this size.
[click] K = 32: the error keeps falling but each doubling of K helps less. That is the elbow curve again, now with a visible meaning.

The swatch bar shows the palette, with each color's width proportional to how many pixels use it.

The code: reshape the image into a table with one row per pixel and three columns. Fit on a random sample of 5,000 pixels for speed, since that is plenty to place 16 centroids. Then predict all pixels, and index the centroid array with the labels to rebuild the image. GIF images and many PNG files work this way: a palette of at most 256 colors plus one index per pixel.
-->

---
glowSeed: 738
clicks: 6
---

# Example 3: Where to Put 8 Depots?

<CaliforniaDepots />

<!--
Third example: placing facilities. The California housing data has the location of each of 20,640 census block groups, and block groups are designed to hold similar numbers of people, roughly 600 to 3,000. So the points are a rough map of where people live; 3,000 are shown.

Suppose we must open 8 depots and want people to be close to their nearest one. Minimizing the squared distance from each block group to its nearest depot is exactly the k-means objective, so the centroids are the depot locations. Coordinates were converted to kilometers east and north so that distance means distance.

We start from 8 random block groups. [click] One iteration: the depots move toward the population they own. [click] [click] Watch the depots and their shaded service areas reorganize. [click] [click] Later iterations are fine adjustments. [click] Converged: the depots sit in Los Angeles, San Diego, the Bay Area, San Jose, Sacramento, Fresno, between Santa Barbara and Bakersfield, and up north near Redding.

The mean squared distance fell from about 5,217 to about 2,878 square kilometers, and on average a block group is 43 km from its depot. Note the unequal sizes: the Los Angeles depot serves 8,755 block groups. k-means minimizes distance, not workload; if capacity matters, you need a constrained method.

A caveat worth saying: the data script tried random starts until one reached the best known solution, and only one of the first 35 seeds did. On real data, always use k-means++ with several restarts.
-->

---
glowSeed: 739
---

# When Is k-Means a Good Choice?

<div class="grid grid-cols-2 gap-6 mt-4 text-left">
<div>
<div class="font-bold text-teal-300 text-lg mb-2">Works well when…</div>
<v-clicks>
<div border="2 solid teal-800" bg="teal-800/20" rounded-lg px-4 py-2 mb-2 class="text-sm">Features are <b>numeric</b> and Euclidean distance is meaningful (after scaling)</div>
<div border="2 solid teal-800" bg="teal-800/20" rounded-lg px-4 py-2 mb-2 class="text-sm">Groups are <b>compact and roughly round</b>, of similar size and spread</div>
<div border="2 solid teal-800" bg="teal-800/20" rounded-lg px-4 py-2 mb-2 class="text-sm">You want <b>prototypes</b>: a palette, depot sites, a typical customer</div>
<div border="2 solid teal-800" bg="teal-800/20" rounded-lg px-4 py-2 mb-2 class="text-sm">Data is <b>large</b>: millions of rows, O(n·K·d) per iteration</div>
</v-clicks>
</div>
<div>
<div class="font-bold text-red-300 text-lg mb-2">Reach for something else when…</div>
<v-clicks>
<div border="2 solid red-800" bg="red-800/20" rounded-lg px-4 py-2 mb-2 class="text-sm">Clusters are <b>curved, nested or stretched</b> → DBSCAN, hierarchical (next deck), GMM</div>
<div border="2 solid red-800" bg="red-800/20" rounded-lg px-4 py-2 mb-2 class="text-sm">Densities or sizes <b>differ a lot</b> → HDBSCAN, GMM</div>
<div border="2 solid red-800" bg="red-800/20" rounded-lg px-4 py-2 mb-2 class="text-sm"><b>Outliers</b> matter → k-medoids, DBSCAN, or remove them first</div>
<div border="2 solid red-800" bg="red-800/20" rounded-lg px-4 py-2 mb-2 class="text-sm">Features are <b>categorical</b> → k-modes, or a different distance</div>
</v-clicks>
</div>
</div>

<!--
To close the practical part, a checklist.

Works well:
[click] Numeric features where straight-line distance means something, possibly after scaling or a log transform. Spending amounts, sensor readings, coordinates, color values, embedding vectors.
[click] Groups that are compact blobs of similar size, which is what the objective implicitly assumes.
[click] Problems where you want prototypes as the output: the palette, the depot sites, the "typical customer" of each segment.
[click] And big data: k-means is one of the few clustering methods that scales linearly in n.

Reach for something else:
[click] Curved, ring-shaped or stretched clusters: density-based or hierarchical methods, coming next, or Gaussian mixtures for stretched ellipses.
[click] Very different densities or sizes: HDBSCAN or Gaussian mixtures.
[click] Outliers that matter: k-medoids, which uses actual data points as centers and is more robust, or DBSCAN, which labels outliers as noise.
[click] Categorical features: averaging categories does not make sense. k-modes, or a method that takes a custom distance.

Examples of data that suits k-means: customer spend or usage metrics after log and scaling, pixel colors, geographic coordinates within a region, and text or image embeddings for topic grouping.
-->

---
glowSeed: 740
---

# Summary

<div class="grid grid-cols-3 gap-4 mt-6 text-left">
<div v-click border="2 solid teal-800" bg="teal-800/20" rounded-lg px-4 py-3>
<div class="font-bold text-teal-300">Objective</div>
<div class="text-sm opacity-85 mt-1">Minimize J = Σ‖xᵢ − μ<sub>cᵢ</sub>‖². Centroids are means; borders are straight lines.</div>
</div>
<div v-click border="2 solid blue-800" bg="blue-800/20" rounded-lg px-4 py-3>
<div class="font-bold text-blue-300">Algorithm</div>
<div class="text-sm opacity-85 mt-1">Lloyd: assign, update, repeat. J never rises, but only reaches a local minimum.</div>
</div>
<div v-click border="2 solid amber-800" bg="amber-800/20" rounded-lg px-4 py-3>
<div class="font-bold text-amber-300">Initialization</div>
<div class="text-sm opacity-85 mt-1">k-means++ seeding plus n_init restarts. Fix random_state.</div>
</div>
<div v-click border="2 solid violet-800" bg="violet-800/20" rounded-lg px-4 py-3>
<div class="font-bold text-violet-300">Choosing K</div>
<div class="text-sm opacity-85 mt-1">Elbow, silhouette, stability, and the use case. No true K.</div>
</div>
<div v-click border="2 solid orange-800" bg="orange-800/20" rounded-lg px-4 py-3>
<div class="font-bold text-orange-300">Preprocessing</div>
<div class="text-sm opacity-85 mt-1">Distance is the model: log skewed features, then standardize.</div>
</div>
<div v-click border="2 solid red-800" bg="red-800/20" rounded-lg px-4 py-3>
<div class="font-bold text-red-300">Limits</div>
<div class="text-sm opacity-85 mt-1">Convex, similar-size groups only; sensitive to outliers.</div>
</div>
</div>

<!--
Six takeaways.

[click] The objective: the sum of squared distances to the assigned centroid. That one choice forces the centroid to be the mean and the borders to be straight.
[click] The algorithm: alternate assign and update. Each half-step can only lower J, so it always stops, but at a local minimum.
[click] So initialization matters: k-means++ spreads the starts out, and n_init restarts keep the best run.
[click] Choosing K takes several diagnostics and a decision about the use case. Say which K you chose and why.
[click] Preprocessing often decides the result: k-means sees only distances, so transform and scale features to make distance mean what you intend.
[click] And know the limits: compact, convex, similar-size clusters, and few outliers.
-->

---
glowSeed: 741
clicks: 1
---

# Next: Clusters Without Centroids

<div class="grid grid-cols-[1.3fr_1fr] gap-8 items-center mt-2">
<div>
<ClusterPlot v-bind="moonsNext" :lab="$clicks >= 1 ? moonsTruth : moonsNext.lab" :centroids="$clicks >= 1 ? null : moonsNext.centroids" :cells="$clicks < 1" frame :w="500" :h="330" :r="3.2" label="Two moons: k-means cuts across them; the goal is to follow each moon" />
</div>
<div class="text-left space-y-4">
<div border="2 solid white/5" bg="white/5" rounded-lg px-4 py-3 class="text-sm">
<b class="text-red-300">k-means:</b> a cluster is the region around a center. Straight borders cut the moons in half.
</div>
<div v-click border="2 solid teal-800" bg="teal-800/20" rounded-lg px-4 py-3 class="text-sm">
<b class="text-teal-300">Next deck:</b> a cluster is a set of points <b>connected</b> through dense neighborhoods. <b>Hierarchical clustering</b>, <b>DBSCAN</b> and <b>HDBSCAN</b> can follow shapes like these and label outliers as noise.
</div>
</div>
</div>

<script setup>
import failsNext from './data/fails.json'
const moonsNext = { pts: failsNext.moons.pts, lab: failsNext.moons.frames[0].lab, centroids: failsNext.moons.frames[0].c }
const moonsTruth = failsNext.moons.truth
</script>

<!--
We end where k-means breaks. On the two moons, k-means can only draw a straight border between two centers, so it cuts each moon in half.

[click] The grouping we actually want follows each moon. To get it, we need a different definition of a cluster: not "the points near a center" but "points connected to each other through dense regions".

That is the next deck, Hierarchical and Density-Based Clustering: building clusters by merging nearest neighbors into a tree, and DBSCAN and HDBSCAN, which grow clusters outward through dense regions and can label isolated points as noise, solving the outlier problem from today as well.
-->
