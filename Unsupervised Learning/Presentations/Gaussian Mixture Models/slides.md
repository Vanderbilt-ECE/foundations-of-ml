---
theme: default
highlighter: shiki
css: unocss
colorSchema: dark
title: 'Gaussian Mixture Models'
info: |
  ## Gaussian Mixture Models
  Clusters as overlapping Gaussians, fit by Expectation–Maximization
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
glowSeed: 770
---

# Gaussian Mixture Models {.!text-5xl}

### Clusters as overlapping, probabilistic ellipses

<div class="mt-1 max-w-3xl mx-auto">
<HeroEM />
</div>

<div class="opacity-80 text-lg">Unsupervised Learning · Foundations of Machine Learning</div>

<!--
Two decks ago, k-means: every cluster is a center and every point belongs to exactly one center. Last deck: clusters without centers, trees and densities. Today: every cluster is a probability distribution, a Gaussian, and every point gets a probability of belonging to each cluster.

The animation is today's algorithm, Expectation–Maximization, running on 500 unlabeled points. The points start gray. Each beat alternates two moves: the points take on colors, blended where a point is shared between clusters, and then the ellipses move to fit the colored points. A dozen rounds and it settles on three ellipses of very different size, shape and tilt.

Roadmap: one Gaussian as the shape of one cluster → mixtures as a story of how data is generated → responsibilities, the soft labels → the EM algorithm, and why it works → choosing the number of components and the covariance type → real data: Old Faithful and iris, density estimation, anomaly detection and generating new data → and finally, k-means turns out to be a special case of today's model.

Every number on these slides comes from scripts/make_data.py in the deck folder, run with fixed seeds.
-->

---
glowSeed: 771
clicks: 2
---

# Where k-Means Left Off

<div class="grid grid-cols-2 gap-6 mt-1">
<div>
<ClusterPlot v-if="$clicks < 1" :pts="fixes.aniso.pts" :lab="fixes.aniso.km" :centroids="fixes.aniso.kmC" cells frame :w="420" :h="280" :r="2.6" label="k-means on two stretched clusters: the border cuts across both" />
<GmmPlot v-else :pts="fixes.aniso.pts" :mix="fixes.aniso.gmm" mode="soft" frame :w="420" :h="280" :r="2.6" label="GMM on two stretched clusters: one ellipse each" />
<div class="text-center text-sm font-mono mt-1">Stretched clusters · {{ $clicks < 1 ? `k-means ARI ${fixes.aniso.kmAri.toFixed(2)}` : `GMM ARI ${fixes.aniso.gmmAri.toFixed(2)}` }}</div>
</div>
<div>
<ClusterPlot v-if="$clicks < 1" :pts="fixes.unequal.pts" :lab="fixes.unequal.km" :centroids="fixes.unequal.kmC" cells frame :w="420" :h="280" :r="2.6" label="k-means on clusters of unequal size: the big one is split" />
<GmmPlot v-else :pts="fixes.unequal.pts" :mix="fixes.unequal.gmm" mode="soft" frame :w="420" :h="280" :r="2.6" label="GMM on clusters of unequal size" />
<div class="text-center text-sm font-mono mt-1">Unequal sizes · {{ $clicks < 1 ? `k-means ARI ${fixes.unequal.kmAri.toFixed(2)}` : `GMM ARI ${fixes.unequal.gmmAri.toFixed(2)}` }}</div>
</div>
</div>

<div class="reveal text-sm mt-3" :class="{ shown: $clicks >= 2 }" border="2 solid teal-800" bg="teal-800/20" rounded-lg px-4 py-2>
Replace each <b>center</b> with a <b>Gaussian</b> (its own mean, spread and tilt), and each <b>hard label</b> with a <b>probability</b> of membership.
</div>

<script setup>
import fixes from '@data/fixes.json'
</script>

<!--
Two of the failure cases from the k-means deck, same points.

Left: two long, parallel, tilted clusters. k-means puts two centers down and the border between their regions is the perpendicular bisector, a straight line that cuts across both clusters. ARI 0.01: no better than chance. Right: one big diffuse cluster and two small tight ones. k-means wants clusters of similar size, so it splits the big one and merges the small ones. ARI 0.28.

[click] Same data, a Gaussian mixture with two and three components. Each cluster gets its own ellipse: long and thin and tilted on the left; big and round next to small and tight on the right. ARI 1.00 and 0.97. Look at the colors on the right: where the big cluster overlaps the small ones, points are drawn in blended colors. They are genuinely uncertain, and the model says so.

[click] So two changes today. A cluster is no longer a point, it is a Gaussian distribution with a mean, a spread and an orientation. And membership is no longer yes/no, it is a probability. Both come out of one idea: model how the data could have been generated.
-->

---
glowSeed: 772
clicks: 5
---

# Today

<div class="grid grid-cols-2 gap-x-6 gap-y-3 mt-4 text-left">
<div border="2 solid teal-800" bg="teal-800/20" rounded-lg px-4 py-3>
<div class="font-bold text-teal-300">1 · One Gaussian = one cluster</div>
<div class="text-sm opacity-85 mt-1">Mean, covariance, and the ellipse they draw.</div>
</div>
<div class="reveal" :class="{ shown: $clicks >= 1 }" border="2 solid amber-800" bg="amber-800/20" rounded-lg px-4 py-3>
<div class="font-bold text-amber-300">2 · Mixtures and responsibilities</div>
<div class="text-sm opacity-85 mt-1">How the data was generated, and Bayes' rule for who generated each point.</div>
</div>
<div class="reveal" :class="{ shown: $clicks >= 2 }" border="2 solid violet-800" bg="violet-800/20" rounded-lg px-4 py-3>
<div class="font-bold text-violet-300">3 · Fitting with EM</div>
<div class="text-sm opacity-85 mt-1">Alternate soft labels and refits. Why it climbs, where it gets stuck.</div>
</div>
<div class="reveal" :class="{ shown: $clicks >= 3 }" border="2 solid blue-800" bg="blue-800/20" rounded-lg px-4 py-3>
<div class="font-bold text-blue-300">4 · Model choices</div>
<div class="text-sm opacity-85 mt-1">Covariance type and number of components, with BIC.</div>
</div>
<div class="reveal" :class="{ shown: $clicks >= 4 }" border="2 solid orange-800" bg="orange-800/20" rounded-lg px-4 py-3>
<div class="font-bold text-orange-300">5 · Real data, and what a density buys you</div>
<div class="text-sm opacity-85 mt-1">Old Faithful and iris · anomaly detection · generating new data.</div>
</div>
<div class="reveal" :class="{ shown: $clicks >= 5 }" border="2 solid red-800" bg="red-800/20" rounded-lg px-4 py-3>
<div class="font-bold text-red-300">6 · The big picture</div>
<div class="text-sm opacity-85 mt-1">k-means as a special case, and when to use which method.</div>
</div>
</div>

<!--
Six parts.

First, the building block: a single Gaussian, and how its covariance matrix describes the shape of a cluster.
[click] Second, a mixture of Gaussians as a recipe for generating data, and, running that recipe backwards with Bayes' rule, the soft labels called responsibilities.
[click] Third, how to fit the model when we never see which component produced each point: the Expectation–Maximization algorithm. We'll watch it run, see why it never goes downhill, and see two ways it can go wrong.
[click] Fourth, the modeling choices: how flexible each Gaussian may be, and how many components to use, chosen with information criteria.
[click] Fifth, real data, and the things a probability density gives you beyond clusters.
[click] Sixth, the closing connection: k-means is a GMM with the knobs turned all the way down, and a comparison of every clustering method in the unit.
-->

---
layout: center
class: text-center
glowSeed: 773
---

# Part 1 · One Cluster, One Gaussian

<div class="text-lg opacity-80 mt-3">A center is a point. A Gaussian is a center plus a shape.</div>

<!--
Part one: the Gaussian, the shape we will give each cluster. Most of this is review from the probability lecture, but we need it in two dimensions and we need to read the covariance matrix as geometry.
-->

---
glowSeed: 774
---

# The 1D Gaussian

<div class="grid grid-cols-[1.35fr_1fr] gap-6 items-center mt-2">
<div>
<Gauss1D />
</div>
<div class="space-y-4 text-left">
<div border="2 solid teal-800" bg="teal-800/20" rounded-lg px-4 py-1>

$$
\mathcal N(x\mid\mu,\sigma^2)=\frac{1}{\sqrt{2\pi}\,\sigma}\,\exp\!\Big(-\frac{(x-\mu)^2}{2\sigma^2}\Big)
$$

</div>
<div class="text-sm" border="2 solid white/5" bg="white/5" rounded-lg px-4 py-3>
<b class="text-amber-300">μ</b> moves the bell. <b class="text-violet-300">σ</b> widens it, and the peak drops so the area stays 1.
</div>
<div class="text-sm" border="2 solid white/5" bg="white/5" rounded-lg px-4 py-3>
68% of the mass within 1σ, 95% within 2σ. Density falls off with the <b>squared, standardized</b> distance from μ.
</div>
</div>
</div>

<!--
The normal distribution, now with motion. The mean μ, the amber marker, slides the bell left and right. The standard deviation σ, the violet arrow, sets its width. Watch the peak: when the bell widens it gets lower, because it is a density and its area is always exactly 1.

The shaded bands are μ ± 1σ, about 68% of the probability, and μ ± 2σ, about 95%.

The one thing to take from the formula: the exponent is minus one half of ((x − μ)/σ)², the squared distance from the mean measured in units of σ. A point two σ from the mean has the same density relative to the peak no matter what σ is. That standardized distance generalizes to the Mahalanobis distance in a few slides, and it is what will replace Euclidean distance in clustering.
-->

---
glowSeed: 775
clicks: 2
---

# The 2D Gaussian Is a Hill

<div class="grid grid-cols-[1.3fr_1fr] gap-6 items-center">
<div>
<Gauss3D :mode="$clicks" />
</div>
<div class="space-y-3 text-left">
<div class="cv" :class="{ on: $clicks === 0 }" border="2 solid white/5" bg="white/5" rounded-lg px-4 py-2>

**Spherical** $\;\Sigma=I$ · circles

</div>
<div class="cv" :class="{ on: $clicks === 1 }" border="2 solid white/5" bg="white/5" rounded-lg px-4 py-2>

**Diagonal** $\;\Sigma=\mathrm{diag}(2.4,\,0.45)$ · axis-aligned

</div>
<div class="cv" :class="{ on: $clicks === 2 }" border="2 solid white/5" bg="white/5" rounded-lg px-4 py-2>

**Full** $\;\Sigma=\left[\begin{smallmatrix}1.8&1.1\\1.1&1.2\end{smallmatrix}\right]$ · tilted

</div>
<div style="font-size: .78em" border="2 solid teal-800" bg="teal-800/20" rounded-lg px-3>

$$
\mathcal N(\mathbf x\mid\boldsymbol\mu,\Sigma)=\frac{\exp\!\big(-\tfrac12(\mathbf x-\boldsymbol\mu)^{\!\top}\Sigma^{-1}(\mathbf x-\boldsymbol\mu)\big)}{(2\pi)^{d/2}\,|\Sigma|^{1/2}}
$$

</div>
</div>
</div>

<style>
.cv { opacity: 0.4; transition: opacity 0.4s ease, border-color 0.4s ease; }
.cv.on { opacity: 1; border-color: rgba(251, 191, 36, 0.7) !important; }
</style>

<!--
In two dimensions the Gaussian is a hill over the plane. Height is density. The rings projected on the floor are contour lines: curves of equal density. For a Gaussian those contours are always ellipses, and the shape of the ellipses is set entirely by the covariance matrix Σ.

Spherical: Σ is the identity. Same spread in every direction; the hill is round and the contours are circles. This is the shape k-means implicitly assumes.

[click] Diagonal: different variances on the two axes, zero off the diagonal. The hill stretches into a ridge along x₁, and the contours are ellipses aligned with the axes.

[click] Full: nonzero off-diagonal entries. The ridge turns: when x₁ is high, x₂ tends to be high too. The off-diagonal entry is the covariance between the two features, and it is what produces the tilt.

The formula in the card is the same as in 1D: a normalizing constant, times e to the minus one half of a squared distance. In 1D that distance was ((x − μ)/σ)². Here it is (x − μ)ᵀ Σ⁻¹ (x − μ): the inverse covariance plays the role of 1/σ². The determinant |Σ| is the d-dimensional version of σ², it measures the volume of the ellipse and keeps the total probability at 1.

The 3D view rotates on its own; you can also drag it.
-->

---
glowSeed: 776
---

# Covariance Is Geometry

<CovEllipse />

<div class="text-sm mt-2" border="2 solid teal-800" bg="teal-800/20" rounded-lg px-4>

$$
\Sigma = V\Lambda V^{\top}=\lambda_1\mathbf v_1\mathbf v_1^{\top}+\lambda_2\mathbf v_2\mathbf v_2^{\top}\qquad\text{axes } \mathbf v_j,\ \ \text{radii } \sqrt{\lambda_j}
$$

</div>

<!--
How to read any covariance matrix as an ellipse. These 200 points are fixed standard-normal draws pushed through Σ, so as Σ changes, the cloud turns and stretches with it. The solid ellipse is the 1-Mahalanobis-distance contour, the dashed one is 2.

The eigendecomposition from the linear algebra lecture does all the work. Σ = V Λ Vᵀ. The eigenvectors v₁ and v₂ point along the ellipse's axes: the amber arrow is the direction of greatest spread, the violet one is perpendicular to it. The eigenvalues are the variances along those axes, so the ellipse's radii are their square roots. That is why the arrows are drawn as √λ times v.

Watch the live matrix as the ellipse rotates. The diagonal entries are the spreads along x₁ and x₂. The off-diagonal entry, highlighted, is positive when the ellipse tilts up to the right, zero when it lines up with an axis, and negative when it tilts down. The correlation ρ is that entry divided by the two standard deviations.

So when we fit a Gaussian to a cluster, we learn a center and an ellipse. For d features, Σ is d by d, with d(d+1)/2 free numbers. Keep that count in mind; it comes back when we choose the covariance type.
-->

---
glowSeed: 777
---

# Distance the Gaussian Way: Mahalanobis

<Mahalanobis />

<div class="grid grid-cols-[1.2fr_1fr] gap-4 mt-2 items-center text-sm text-left">
<div border="2 solid teal-800" bg="teal-800/20" rounded-lg px-4>

$$
d_M(\mathbf x)=\sqrt{(\mathbf x-\boldsymbol\mu)^{\top}\Sigma^{-1}(\mathbf x-\boldsymbol\mu)},\qquad \mathcal N\propto e^{-d_M^2/2}
$$

</div>
<div border="2 solid white/5" bg="white/5" rounded-lg px-4 py-2>
Distance measured in standard deviations <b>along each direction</b>. Equal-density curves are ellipses, not circles.
</div>
</div>

<!--
The exponent of the Gaussian has a name. d_M, the Mahalanobis distance, is the distance from the mean measured in standard deviations in each direction. Contours of equal Mahalanobis distance are exactly the ellipses: d_M = 1, 2, 3 here.

The dashed circle is every point at Euclidean distance 1.5 from the mean. Click anywhere on the plot (or drag) to move the amber probe; the panel shows its Euclidean and Mahalanobis distances and its density. Walk it around the dashed circle: the Euclidean distance stays at 1.5, but the Mahalanobis distance swings from under 1 to almost 3, and the density bar swings with it. Then try a point far out along the long axis and a closer one across the short axis: the farther point can be the more typical one.

A and B make it concrete. Both are 1.5 from the mean. A lies along the long axis, where the cloud is spread out: d_M = 0.87, density 69% of the peak, a perfectly typical point. B lies along the short axis, where the cloud is thin: d_M = 2.74, density 2.4% of the peak. B is an unusual point for this cluster, even though it is just as close as A in Euclidean terms.

This is the key change from k-means. k-means assigns by Euclidean distance to the center, as if every cluster were round and the same size. A Gaussian measures each cluster's distance in that cluster's own shape.
-->

---
layout: center
class: text-center
glowSeed: 778
---

# Part 2 · Mixtures and Responsibilities

<div class="text-lg opacity-80 mt-3">A story for how the data was made, and Bayes' rule to read it backwards</div>

<!--
Part two. One Gaussian describes one cluster. A dataset with several clusters needs several Gaussians, combined in a specific way: a mixture.
-->

---
glowSeed: 779
clicks: 2
---

# A Mixture Is a Generative Story

<GenerativeStory :step="$clicks" />

<div class="grid grid-cols-[1.2fr_1fr] gap-4 mt-1 text-left text-sm items-center">
<div border="2 solid teal-800" bg="teal-800/20" rounded-lg px-4>

$$
z_i\sim\text{Categorical}(\pi_1,\dots,\pi_K),\qquad \mathbf x_i\mid z_i=k\ \sim\ \mathcal N(\boldsymbol\mu_k,\Sigma_k)
$$

</div>
<div border="2 solid white/5" bg="white/5" rounded-lg px-4 py-2 style="min-height: 3.2em">
{{ ['Spin, then draw. The wheel is the weights πₖ, which sum to 1.', 'All 500 points of our running example were made exactly this way.', 'We only see x. The labels z are hidden (latent): recovering them is the clustering problem.'][$clicks] }}
</div>
</div>

<!--
A Gaussian mixture model is a recipe for producing data, a generative story, exactly like the one behind Naive Bayes.

Step 1: spin a wheel whose slices are the mixing weights π_k. Here 0.45, 0.35 and 0.20. The slice it lands on is the component, written z. Step 2: draw the point from that component's Gaussian, with its own mean and covariance. The point flies from the wheel to where it was drawn.

[click] Speed it up. These are the real 500 points of the example we will use all lecture; make_data.py generated them with exactly this recipe. The big tilted component gets about 45% of the points, the round small one about 20%.

[click] Now the important part: what we actually get to see. Not the colors, not the ellipses, just gray points. The component z of each point is hidden; statisticians call it a latent variable. Clustering with a GMM means running this story backwards: from the gray points, recover the weights, means and covariances, and for each point, which slice of the wheel probably produced it.
-->

---
glowSeed: 780
clicks: 3
---

# Adding Up Weighted Bells

<div class="max-w-3xl mx-auto -mt-2">
<Mixture1D :step="$clicks" />
</div>
<div class="grid grid-cols-[1fr_1.3fr] gap-5 items-center text-left text-sm mt-1">
<div border="2 solid white/5" bg="white/5" rounded-lg px-4 py-2 style="min-height: 3em">
{{ ['Three components, each a density with area 1.', 'Scale each by its weight πₖ: now their areas are 0.3, 0.5, 0.2.', 'Add them up: one density with three peaks, area 1.', '600 samples from the story land right on it.'][$clicks] }}
</div>
<div class="reveal" :class="{ shown: $clicks >= 2 }" border="2 solid teal-800" bg="teal-800/20" rounded-lg px-4>

$$
p(\mathbf x)=\sum_{k=1}^{K}\pi_k\,\mathcal N(\mathbf x\mid\boldsymbol\mu_k,\Sigma_k),\qquad \pi_k\ge0,\ \sum_k\pi_k=1
$$

</div>
</div>

<!--
The same story in one dimension, so we can see the densities.

Three Gaussians: means −2, 1.5 and 5, standard deviations 0.8, 1.2 and 0.6. On their own, each has area 1.

[click] Scale each by its mixing weight, 0.3, 0.5 and 0.2. The curves shrink; their areas are now the weights.

[click] Add them. The white curve is the mixture density p(x): three peaks, and since the weights sum to 1, total area 1. It is a legitimate probability density, and a far more flexible one than any single Gaussian. The formula sums over components because a point could have come from any of them: it is the probability of each slice times the density from that slice, added up. That is the law of total probability, with the hidden z summed out.

[click] And a histogram of 600 points generated by the spin-then-draw recipe follows the white curve. Generating data with the story and evaluating p(x) are two views of the same model.

Notice where the peaks overlap, between −2 and 1.5: a point there could plausibly have come from either component. That ambiguity is what responsibilities quantify.
-->

---
glowSeed: 781
---

# The Mixture as a Landscape

<div class="grid grid-cols-[1.4fr_1fr] gap-6 items-center">
<div>
<Mixture3D />
</div>
<div class="space-y-3 text-left text-sm">
<div border="2 solid white/5" bg="white/5" rounded-lg px-4 py-3>
One hill per component. A heavy weight or a small covariance makes a tall hill.
</div>
<div border="2 solid teal-800" bg="teal-800/20" rounded-lg px-4 py-3>
<div class="font-bold text-teal-300 mb-1">Everything to learn</div>
θ = { π<sub>k</sub>, μ<sub>k</sub>, Σ<sub>k</sub> } for k = 1…K
<div class="opacity-80 mt-1">Here: 2 weights + 6 means + 9 covariance entries = <b>17 numbers</b></div>
</div>
<div border="2 solid white/5" bg="white/5" rounded-lg px-4 py-3>
A density for <b>any</b> point x, not just a label for the training points.
</div>
</div>
</div>

<!--
The running example's true mixture density, in 3D. Three hills on the plane: the wide tilted ridge on the left is component 1, weight 0.45; the moderate hill on the right is component 2; the sharp peak at the bottom is component 3. Component 3 has the smallest weight, 0.20, but the tallest peak, because its covariance is small: all its probability is packed into a small area. The 500 sampled points sit on the floor in their component colors.

Everything a GMM learns is in this list: K weights, K means, K covariance matrices. With K = 3 in 2D that is 2 free weights (the third is 1 minus the others), 6 mean coordinates, and 3 numbers per covariance matrix, 9: 17 parameters. We'll meet that 17 again in scikit-learn's BIC.

The last card is a big difference from every method so far: a GMM is a density model. It assigns a probability density to every point in the space, including points we have never seen. That is what later lets us flag anomalies and sample new data.
-->

---
glowSeed: 782
clicks: 2
---

# Responsibilities: Bayes' Rule for Membership

<RespSweep :step="$clicks" />

<div class="grid grid-cols-[1.3fr_1fr] gap-4 mt-2 items-center text-left">
<div border="2 solid teal-800" bg="teal-800/20" rounded-lg px-4 style="font-size: .9em">

$$
\gamma_{ik}=P(z_i=k\mid\mathbf x_i)=\frac{\pi_k\,\mathcal N(\mathbf x_i\mid\boldsymbol\mu_k,\Sigma_k)}{\sum_{j}\pi_j\,\mathcal N(\mathbf x_i\mid\boldsymbol\mu_j,\Sigma_j)}
$$

</div>
<div class="text-sm" border="2 solid white/5" bg="white/5" rounded-lg px-4 py-2 style="min-height: 3.2em">
{{ ['Prior × likelihood, normalized. Near a mean: γ ≈ 1. In between: a smooth hand-off.', 'At x = 1.5: γ₁ ≈ 0.88. Closer to μ₁ = 0, but not certain.', 'Raise the prior π₁ to 0.8: same x, now γ₁ ≈ 0.97, and the 50/50 point moves right.'][$clicks] }}
</div>
</div>

<!--
Running the story backwards for one point: given x, which component produced it? That is Bayes' rule, the same computation as the Naive Bayes posterior. Prior: π_k, how common component k is. Likelihood: the density of x under component k. Multiply them, and divide by the sum over all components so the K numbers add to 1. The result γ_ik is called the responsibility of component k for point i.

The top panel draws the two products, π₁N₁ in teal and π₂N₂ in amber, for components at 0 and 4 with σ = 1 and equal weights. Drag the vertical line across (or click anywhere on the plot). At any x the responsibility is just the teal height's share of the two heights. The bottom panel stacks γ₁ and γ₂: near 0, almost all teal; near 4, almost all amber; and in between a smooth S-shaped hand-off, crossing 50/50 at the midpoint, 2.

[click] The probe jumps to x = 1.5, next slide's worked example (it stays draggable). Teal height 0.0648, amber 0.0088, so γ₁ = 0.88 and γ₂ = 0.12. The point is closer to component 1, but the model keeps a 12% doubt.

[click] Now change only the prior: π₁ = 0.8. Every teal height scales up, so the hand-off moves right: the 50/50 point is now at 2.35, and the same x = 1.5 gets γ₁ = 0.97. If component 1 is more common overall, an ambiguous point is more likely to be one of its points. k-means has no notion of this; a GMM learns the weights from data.
-->

---
glowSeed: 783
---

# Worked Example: One Responsibility by Hand

<div class="grid grid-cols-2 gap-7 mt-3 items-center">
<div class="text-left">

<div border="2 solid white/10" bg="white/5" rounded-lg px-4 class="text-sm">

Two 1D components: $\pi_1=\pi_2=0.5$, $\;\mathcal N(0,1)$ and $\mathcal N(4,1)$. Point $x=1.5$.

</div>

<div class="text-sm">

<v-clicks>

- $\mathcal N(1.5\mid 0,1)=\frac{1}{\sqrt{2\pi}}e^{-1.5^2/2}\approx0.1295$
- $\mathcal N(1.5\mid 4,1)=\frac{1}{\sqrt{2\pi}}e^{-2.5^2/2}\approx0.0175$
- prior × likelihood: $0.5(0.1295)=0.0648$ and $0.5(0.0175)=0.0088$
- $\gamma_{1}=\dfrac{0.0648}{0.0648+0.0088}\approx0.880,\quad \gamma_{2}\approx0.120$

</v-clicks>

</div>

</div>

```python
import numpy as np
from scipy.stats import norm

x = 1.5
pi = np.array([0.5, 0.5])
lik = norm.pdf(x, loc=[0, 4], scale=1)
unnorm = pi * lik      # [0.0648 0.0088]
gamma = unnorm / unnorm.sum()
print(gamma.round(3))  # [0.88 0.12]
```

</div>

<!--
The same numbers by hand, the computation the E-step does for every point.

[click] Density of x = 1.5 under component 1: it is 1.5 standard deviations from 0, so e^(−1.125)/√(2π) ≈ 0.1295.
[click] Under component 2: 2.5 standard deviations from 4, deeper in the tail, ≈ 0.0175.
[click] Multiply by the priors, 0.5 each: 0.0648 and 0.0088. Equal priors don't change the ratio here.
[click] Normalize: γ₁ = 0.0648 / 0.0736 ≈ 0.880, γ₂ ≈ 0.120.

At the midpoint x = 2, symmetry would give exactly 0.5 and 0.5. Practical note: in code, real implementations work with log densities and the log-sum-exp trick, because in high dimensions the densities themselves underflow to zero.
-->

---
glowSeed: 784
clicks: 2
---

# Soft Labels on the Running Example

<div class="grid grid-cols-[1.4fr_1fr] gap-6 items-center">
<div>
<SoftHard :step="$clicks" />
</div>
<div class="space-y-3 text-left text-sm">
<div border="2 solid white/5" bg="white/5" rounded-lg px-4 py-3>
<b class="text-teal-300">Soft:</b> each point's color is a blend of the component colors, weighted by its γ.
</div>
<div class="reveal" :class="{ shown: $clicks >= 1 }" border="2 solid white/5" bg="white/5" rounded-lg px-4 py-3>
<b class="text-amber-300">Hard:</b> keep only the largest γ, <code>predict</code>. The boundary points snap to one side.
</div>
<div class="reveal" :class="{ shown: $clicks >= 2 }" border="2 solid teal-800" bg="teal-800/20" rounded-lg px-4 py-3>
<b>{{ em.nUnsure }} of {{ em.pts.length }}</b> points have no component above 0.9. They sit where ellipses overlap, which is exactly where a hard label would be a guess.
</div>
</div>
</div>

<script setup>
import em from '@data/em.json'
</script>

<!--
The fitted model on the running example, with every point colored by its responsibilities. Deep in a cluster, a point's color is pure teal, amber or violet. Where the big teal component overlaps the amber one, colors blend toward yellow-green: those points are partly each.

[click] The hard version: take the component with the largest responsibility, which is what scikit-learn's predict returns. The picture looks cleaner, but it is hiding information. A point at 0.51/0.49 and a point at 0.99/0.01 get the same label.

[click] Soft again, and now ringing the points whose largest responsibility is below 0.9: 59 of the 500. They all sit in the overlap zones. When you report clusters, or feed cluster labels to another model, those are the points whose labels you should not trust, and a GMM tells you which they are. k-means cannot.
-->

---
glowSeed: 785
---

# Curved Borders Instead of Straight Ones

<Borders />

<div class="grid grid-cols-2 gap-5 mt-3 text-left text-sm">
<div border="2 solid white/5" bg="white/5" rounded-lg px-4 py-2>
k-means: nearest center by Euclidean distance. Borders are perpendicular bisectors, always <b>straight</b>.
</div>
<div border="2 solid teal-800" bg="teal-800/20" rounded-lg px-4>

GMM: largest $\pi_k\mathcal N(\mathbf x\mid\boldsymbol\mu_k,\Sigma_k)$. Comparing two quadratic exponents gives **quadratic** borders: ellipses, parabolas, hyperbolas.

</div>
</div>

<!--
Where does each method draw the line between clusters? Left, k-means on the same 500 points: three Voronoi cells with straight borders. Right, the regions where each GMM component has the largest responsibility, shaded lighter where the hand-off is gradual.

The GMM borders curve. The border curves around the small violet component: just outside its tight cloud the bigger components win, even at points closer to the violet center. And the border between teal and amber bends with the tilt of the big component.

Why curves: the border between components j and k is where π_j N_j = π_k N_k. Take logs and each side is a quadratic function of x, the Mahalanobis term, plus constants. Setting two different quadratics equal gives a conic section. If all components shared one covariance matrix, the quadratic terms would cancel and the borders would be straight lines again; if that shared covariance were a multiple of the identity with equal weights, they would be exactly k-means' bisectors. Hold on to that; it is the last slide's punchline.

Agreement with the true components: k-means 0.80, GMM 0.88. Most of the difference is in the overlap between the two big components, where the tilt matters.
-->

---
layout: center
class: text-center
glowSeed: 786
---

# Part 3 · Fitting a Mixture with EM

<div class="text-lg opacity-80 mt-3">Guess the labels, fit the Gaussians, repeat</div>

<!--
Part three. We can compute responsibilities if we know the parameters. But the parameters are what we need to learn, from gray points. How?
-->

---
glowSeed: 787
---

# Maximum Likelihood, and Why It's Hard

<div class="grid grid-cols-2 gap-6 mt-4 text-left">
<div border="2 solid red-800" bg="red-800/20" rounded-lg px-4 py-3>
<div class="font-bold text-red-300">What we can observe: x only</div>
<div style="font-size: .82em">

$$
\log L(\theta)=\sum_{i=1}^{n}\log\sum_{k=1}^{K}\pi_k\,\mathcal N(\mathbf x_i\mid\boldsymbol\mu_k,\Sigma_k)
$$

</div>
<div class="text-sm opacity-90">A <b>log of a sum</b>: the log can't reach the Gaussians. Setting the gradient to zero gives equations where every μₖ depends on all the others. No closed form.</div>
</div>
<div border="2 solid teal-800" bg="teal-800/20" rounded-lg px-4 py-3>
<div class="font-bold text-teal-300">If we also knew z</div>
<div style="font-size: .82em">

$$
\log L_c(\theta)=\sum_{i=1}^{n}\sum_{k=1}^{K}z_{ik}\big[\log\pi_k+\log\mathcal N(\mathbf x_i\mid\boldsymbol\mu_k,\Sigma_k)\big]
$$

</div>

<div class="text-sm opacity-90">A <b>sum of logs</b>: it splits into K separate problems. Each Gaussian is fit to its own points: sample mean, sample covariance, fraction of points.</div>
</div>
</div>

<div class="mt-5 text-sm" border="2 solid white/5" bg="white/5" rounded-lg px-4 py-1>

EM's trick: we don't know $z_{ik}\in\{0,1\}$, so replace it with its **expected value** under the current guess, $\mathbb E[z_{ik}]=\gamma_{ik}$, then solve the easy problem.

</div>

<!--
The principled way to fit is maximum likelihood, as for logistic regression: choose the parameters that make the observed data most probable. The log-likelihood is on the left: for each point, the log of the mixture density.

The problem is the log of a sum. For a single Gaussian, the log cancels the exponential and you get a quadratic you can minimize by hand, giving the sample mean and covariance. Here the log sits outside the sum over components and can't get at the Gaussians. If you take the derivative with respect to μ_k and set it to zero, you get μ_k = a weighted average of the points where the weights are the responsibilities, which themselves depend on μ_k and all the other parameters. Circular, no closed form. We could use gradient ascent, with constraints for the weights and to keep Σ valid, but there is something much nicer.

Right: suppose we also knew each point's component, written as an indicator z_ik that is 1 for the true component. Then the log-likelihood is a sum of logs and splits apart: each Gaussian's parameters only appear in the terms of its own points. Fitting is trivial: fraction, mean and covariance of each group.

EM uses the right-hand form with z replaced by its expected value given the current parameters. The expected value of a 0/1 indicator is its probability, which is exactly the responsibility. That is the E in EM, expectation. Then maximize the now-easy objective: the M. Next slide shows this as a picture.
-->

---
glowSeed: 788
clicks: 2
---

# A Chicken-and-Egg Problem

<ChickenEgg :step="$clicks" />

<div class="text-sm mt-3 text-center" border="2 solid white/5" bg="white/5" rounded-lg px-4 py-2 style="min-height: 2.4em">
{{ ['Labels → Gaussians is easy.', 'Gaussians → labels is easy.', 'Neither is known. Guess one, then alternate: each half-step uses the other’s latest answer.'][$clicks] }}
</div>

<!--
Here is the same idea as pictures.

Left: if we knew which component produced each point, colors given, fitting is easy: each ellipse is just its group's sample mean and covariance, and each weight is the group's share of the points.

[click] Right: if we knew the Gaussians, assigning points is easy: Bayes' rule, the responsibilities from Part 2.

[click] We know neither. So start with a guess for one of them, and go around the loop: compute responsibilities from the current Gaussians, refit the Gaussians from the current responsibilities, again and again. This is exactly the structure of Lloyd's algorithm for k-means, assign then update, but with soft assignments and with shapes as well as centers.
-->

---
glowSeed: 789
clicks: 2
---

# The EM Algorithm

<div class="grid grid-cols-2 gap-6 mt-2 text-left">
<div border="2 solid teal-800" bg="teal-800/20" rounded-lg px-4 py-2>
<div class="font-bold text-teal-300">E-step · soft labels</div>

$$
\gamma_{ik}\leftarrow\frac{\pi_k\,\mathcal N(\mathbf x_i\mid\boldsymbol\mu_k,\Sigma_k)}{\sum_j\pi_j\,\mathcal N(\mathbf x_i\mid\boldsymbol\mu_j,\Sigma_j)}
$$

<div class="text-sm opacity-85">Parameters fixed. Bayes' rule for every point and component: an n × K table.</div>
</div>
<div class="reveal" :class="{ shown: $clicks >= 1 }" border="2 solid amber-800" bg="amber-800/20" rounded-lg px-4 py-2>
<div class="font-bold text-amber-300">M-step · weighted refits</div>

$$
\begin{aligned}
N_k&=\textstyle\sum_i\gamma_{ik},\qquad \pi_k=N_k/n\\
\boldsymbol\mu_k&=\tfrac{1}{N_k}\textstyle\sum_i\gamma_{ik}\,\mathbf x_i\\
\Sigma_k&=\tfrac{1}{N_k}\textstyle\sum_i\gamma_{ik}(\mathbf x_i-\boldsymbol\mu_k)(\mathbf x_i-\boldsymbol\mu_k)^{\top}
\end{aligned}
$$

</div>
</div>

<div class="reveal mt-4 grid grid-cols-3 gap-3 text-sm text-left" :class="{ shown: $clicks >= 2 }">
<div border="2 solid white/5" bg="white/5" rounded-lg px-3 py-2><b>Initialize</b> means (scikit-learn: from k-means), covariances, equal weights.</div>
<div border="2 solid white/5" bg="white/5" rounded-lg px-3 py-2><b>Repeat</b> E, M until log L improves by less than <code>tol</code> per point (1e-3).</div>
<div border="2 solid white/5" bg="white/5" rounded-lg px-4 py-2><b>Cost</b> per iteration: O(n K d²) for full covariances (plus K matrix inversions).</div>
</div>

<!--
The two steps written out.

E-step: hold the parameters fixed and compute every responsibility, a table with one row per point and one column per component, each row summing to 1.

[click] M-step: hold the responsibilities fixed and refit. N_k, the sum of component k's column, is the effective number of points it owns: 500 points might split as 218, 179 and 103, not necessarily whole numbers. The new weight is N_k over n. The new mean is the responsibility-weighted average of all points. The new covariance is the responsibility-weighted average of the outer products of the centered points: the weighted sample covariance.

These are the "if we knew the labels" formulas from two slides back with every 0/1 indicator replaced by a responsibility. And if you force every γ to be 0 or 1, the mean update is literally k-means' update.

[click] Around it: initialize, by default scikit-learn runs k-means first and starts from its clusters; repeat until the average log-likelihood per point changes by less than tol, 10⁻³ by default. Each iteration touches every point and component once, and full covariances cost d² per point, so it scales linearly in n: fine for millions of points in low dimension.
-->

---
glowSeed: 790
clicks: 2
---

# The M-Step Up Close: Weighted Votes

<MStepWeights :k="$clicks" />

<!--
A closer look at one M-step, early in the run (after three iterations), one component at a time. Each point is drawn with size and brightness equal to its responsibility for the selected component.

Component 1: the big tilted one. Points deep in it are large and bright and pull hard on its new mean and shape. Points in the other clusters are tiny dots that barely count. The dashed white ellipse is where the component was before this step; the solid one is the weighted covariance it moves to. N_k, the effective number of points, need not be a whole number.

[click] Component 2. Notice the points in the overlap with component 1: they are medium-sized in both views. A point at 0.6/0.4 contributes 60% of itself to one refit and 40% to the other. Nothing is double counted: each point's responsibilities sum to 1.

[click] Component 3, the small one: about 108 effective points, a fifth of the data, and its covariance is estimated from those. Small components have noisy covariance estimates, a theme we'll return to.

All three of these refits are computed independently from the same responsibility table; that is the decoupling from the "sum of logs" slide.
-->

---
glowSeed: 791
clicks: 1
---

# Watch EM Run

<EMRun :play="$clicks >= 1" />

<!--
Now the whole algorithm on the running example. Starting point: three randomly chosen data points as means, one broad covariance for all three, equal weights. The points are gray: no responsibilities yet. This is a deliberately poor start so there is something to watch.

[click] Play. Each beat is one half-step. E-step: points recolor according to the current ellipses; the teal phase label lights up. M-step: the ellipses move to the weighted fit of those colors; amber label.

Things to watch. In the first iterations, colors change a lot and ellipses jump. The big component discovers its tilt, the small one shrinks onto the tight cluster. The weights move from a third each to 0.43, 0.36, 0.21 by iteration 15; the truth was 0.45, 0.35, 0.20. On the right, log-likelihood climbs from −2086 to −1690 and every step is upward. By iteration 7 it improves by less than 0.001 per point, scikit-learn's stopping rule, and the last iterations are invisible.

These frames were recorded by a hand-written EM in make_data.py, which the script checks against scikit-learn's GaussianMixture started from the same parameters: identical to six decimals.
-->

---
glowSeed: 792
clicks: 3
---

# Why EM Never Goes Downhill

<div class="grid grid-cols-[1.45fr_1fr] gap-6 items-center">
<div>
<BoundClimb :step="$clicks" />
</div>
<div class="space-y-3 text-left text-sm">
<div border="2 solid white/5" bg="white/5" rounded-lg px-4 py-2>
<b>E-step</b> builds a simpler curve, a <b>lower bound</b> on log L, that <b>touches</b> it at the current θ.
</div>
<div border="2 solid white/5" bg="white/5" rounded-lg px-4 py-2>
<b>M-step</b> jumps to the top of that bound. log L there is ≥ the bound ≥ log L before.
</div>
<div border="2 solid teal-800" bg="teal-800/20" rounded-lg px-4 py-2 style="min-height: 3.6em">
{{ ['Start at μ₁ = −3, far from the peak.', 'First bound: jump to μ₁ = −0.50.', 'Second bound: μ₁ = 0.00. Each bound fits more snugly.', 'Third: 0.07. Steps shrink as EM nears the peak.'][$clicks] }}
</div>
</div>
</div>

<!--
Why does log-likelihood only go up? A one-parameter example so we can draw it: 200 points from two Gaussians at 0 and 4, everything fixed except μ₁. The white curve is the log-likelihood as a function of μ₁; its peak is at about 0.08. Start far away, at −3.

[click] The E-step computes responsibilities at the current μ₁. Using them, define the teal curve: the expected complete-data log-likelihood plus a constant. Two facts, which follow from Jensen's inequality because log is concave: it is never above the white curve, and it touches the white curve exactly at the current μ₁. And it is easy, here a simple parabola, because it is a sum of logs. The M-step jumps to its maximum: μ₁ = −0.50. Since the bound touched at the old point and is below the white curve everywhere, the white curve at the new point is at least as high as the bound's top, which is at least as high as where we were.

[click] New E-step at −0.50: a new amber bound, touching there. Its top is at 0.00.
[click] Then 0.07, then 0.078 and 0.079, converging.

That is the general proof that EM never decreases the likelihood, called minorize–maximize. It also shows the limitation: EM climbs to the top of whatever hill it starts on. If the white curve had two peaks, EM would find the nearest one, a local maximum. Next slide.
-->

---
glowSeed: 793
clicks: 1
---

# Local Optima: Restart and Keep the Best

<Restarts :show="$clicks >= 1" />

<div class="grid grid-cols-2 gap-4 mt-3 text-sm text-left">
<div border="2 solid white/5" bg="white/5" rounded-lg px-4 py-2>
<code>n_init=10</code> runs EM from 10 starts and keeps the highest likelihood. Default is 1.
</div>
<div border="2 solid amber-800" bg="amber-800/20" rounded-lg px-4 py-2>
The default k-means start can inherit k-means' mistake: on the stretched clusters, GMM from one k-means start scores ARI <b>{{ fixes.aniso.kmInitAri.toFixed(2) }}</b>; 20 random starts, <b>{{ fixes.aniso.gmmAri.toFixed(2) }}</b>.
</div>
</div>

<script setup>
import fixes from '@data/fixes.json'
</script>

<!--
EM guarantees uphill, not the summit. Five well-separated blobs, K = 5, and 12 runs of EM, each started from 5 random data points as means. Every curve rises, every curve flattens, but at different heights.

Four of the 12 reach −1543, the best value. Seven get stuck around −1610: two components sharing one blob while another component straddles two blobs. One run ends at −1775.

[click] The best and worst final fits. Best: one ellipse per blob, ARI 1.00 against the true blobs. Worst: one component sprawls across three blobs, ARI 0.37. EM converged in both cases; it just converged to different hills.

The fix is the same as for k-means: several starts, keep the one with the highest likelihood. In scikit-learn that is n_init, and the default is 1, so set it. Because likelihood is the objective, comparing runs is easy and objective.

The second card is a trap worth knowing. scikit-learn initializes EM from a k-means solution by default. On the stretched clusters from the start of the lecture, k-means is wrong, and a GMM started from that k-means answer stays in it: ARI 0.03. Twenty starts from random data points (init_params="random_from_data") find the right answer, ARI 1.00, with a much higher likelihood: −930 versus −1156. Always check more than one start.
-->

---
glowSeed: 794
clicks: 1
---

# When the Likelihood Blows Up

<Collapse :floor="$clicks >= 1" />

<div class="text-sm mt-2" border="2 solid white/5" bg="white/5" rounded-lg px-4 py-2 style="min-height: 2.6em">
<span v-if="$clicks < 1">A component on one point: its density there is 1/(2πσ²) → ∞ as σ → 0. The "best" fit is a degenerate spike.</span>
<span v-else><code>reg_covar</code> (default 1e-6) adds a floor to every variance, so Σ stays invertible and the spike stays finite. Floor exaggerated here.</span>
</div>

<!--
A strange property of the Gaussian mixture likelihood: it has no maximum. Take the converged three-component fit and add a fourth component centered exactly on one data point, the most isolated one, ringed. Now shrink its σ.

The density of that component at its own point is 1 over 2πσ². Each time σ shrinks tenfold, the density grows a hundredfold, and that point's log-likelihood term grows by about 4.6. All the other points are still explained by the other three components. So the total log-likelihood climbs forever: off the chart, toward infinity. The "best" model is a spike of zero width, which is useless.

In practice EM wanders into this when a component ends up owning very few points, more likely with many components, high dimension, duplicated points, or a bad start. The symptom: a covariance becomes singular and the code crashes or warns.

[click] The remedy in scikit-learn is reg_covar: a small constant, 10⁻⁶ by default, added to the diagonal of every covariance after each M-step. Variances can never go below it, so the spike's height is capped and Σ stays invertible. Here the floor is drawn much larger than 10⁻⁶ so you can see it stop. If you still get warnings about ill-defined covariances, increase reg_covar, reduce K, or use a more constrained covariance type, our next topic.
-->

---
layout: center
class: text-center
glowSeed: 795
---

# Part 4 · Model Choices

<div class="text-lg opacity-80 mt-3">How flexible is each Gaussian, and how many are there?</div>

<!--
Part four. A GMM has two big modeling decisions: the shape constraints on each covariance matrix, and the number of components K. Both trade fit against number of parameters, so we'll treat them together.
-->

---
glowSeed: 796
clicks: 4
---

# Four Covariance Types

<CovTypes :hl="$clicks - 1" />

<div class="text-sm mt-3 text-center" border="2 solid white/5" bg="white/5" rounded-lg px-4 py-2 style="min-height: 2.4em">
{{ ['Same data, K = 3, four constraints on Σₖ. p = free parameters. Lower BIC is better.', 'spherical: round blobs of different sizes. Closest to k-means.', 'diag: stretched, but only along the axes. Fast and common in high dimension.', 'tied: one shape shared by all components. Straight borders.', 'full: each component its own ellipse. Best BIC here, and the default.'][$clicks] }}
</div>

<!--
The covariance_type parameter constrains every Σ_k. Same 500 points, K = 3, all four types. The badges: p is the number of free parameters, then BIC, which we'll define in two slides (lower is better), and ARI against the true components.

[click] spherical: each component has a single variance, σ_k² times the identity. Circles, but of different sizes, unlike k-means. 11 parameters. It can't capture the tilt, so it carves the tilted cluster badly: ARI 0.81.

[click] diag: a separate variance per feature, no covariances. Ellipses, but only axis-aligned. 14 parameters. Popular in high dimension because it grows linearly in d. Here: no better than spherical, 0.81, because the real clusters are tilted.

[click] tied: all components share one full covariance matrix. So every component has the same shape and orientation, and the borders between components are straight lines, like LDA if you've seen it. 11 parameters. Our clusters have very different shapes, so it does worst: BIC 3811, ARI 0.79.

[click] full: every component has its own unrestricted covariance. 17 parameters, the most flexible, and by far the best BIC, 3485, and ARI, 0.88. It is scikit-learn's default.

The constrained types are not useless; they are regularization. Next slide shows why you might need it.
-->

---
glowSeed: 797
---

# Flexibility Costs Parameters

<div class="grid grid-cols-[1.5fr_1fr] gap-6 items-center">
<div>
<ParamCount />
</div>
<div class="space-y-3 text-left text-sm">
<div border="2 solid teal-800" bg="teal-800/20" rounded-lg px-4 py-2>
<b class="text-teal-300">full</b> grows like K·d²/2: each component needs d(d+1)/2 covariances. 64 features, 3 components: <b>6,434</b> parameters.
</div>
<div border="2 solid white/5" bg="white/5" rounded-lg px-4 py-2>
Few points per component + many parameters → noisy or <b>singular</b> covariances, overfitting.
</div>
<div border="2 solid white/5" bg="white/5" rounded-lg px-4 py-2>
<b>diag</b> / <b>spherical</b> act as regularization: less flexible, far fewer numbers to estimate. Or reduce d first (next deck).
</div>
</div>
</div>

<!--
The price of flexibility. Free parameters of a three-component mixture as the number of features grows. At d = 2, these are the 11, 14, 11 and 17 from the last slide.

Spherical and diag grow linearly in d. Tied adds one full matrix, so it grows quadratically but only once. Full grows quadratically for every component: at 30 features, 1,487 parameters. At 64 features, the size of an 8×8 digit image, 6,434.

Why it matters: each component's covariance is estimated from roughly N_k points. A d×d covariance estimated from fewer than d points is singular: there are directions in which the component has seen no variation at all, which is exactly the collapse from a few slides ago. Even with more points than that, estimates are noisy and the model overfits, the same bias–variance story as polynomial regression.

So in high dimension: use diag or spherical, which are a form of regularization; increase reg_covar; or reduce the dimension first with PCA, which is the next deck.
-->

---
glowSeed: 798
clicks: 5
---

# Choosing K: Penalize the Parameters

<BicChoose :k="[1, 2, 3, 4, 6, 8][$clicks]" />

<div class="grid grid-cols-[1.2fr_1fr] gap-4 mt-2 items-center text-left">
<div border="2 solid teal-800" bg="teal-800/20" rounded-lg px-4 style="font-size: .88em">

$$
\mathrm{BIC}=-2\log\hat L+p\log n,\qquad \mathrm{AIC}=-2\log\hat L+2p
$$

</div>
<div class="text-sm" border="2 solid white/5" bg="white/5" rounded-lg px-4 py-2 style="min-height: 3em">
{{ ['K = 1: one big ellipse. Poor fit.', 'K = 2: two clusters merged.', 'K = 3: big drop in −2 log L. BIC and AIC both minimal.', 'K = 4: slightly better fit, but 6 more parameters. BIC rises.', 'K = 6: extra components split clusters. Fit barely improves.', 'K = 8: −2 log L still falling; BIC clearly worse.'][$clicks] }}
</div>
</div>

<!--
How many components? Likelihood alone always says "more": a model with K + 1 components can do anything the K-component model can. The gray dashed line, −2 log L, falls at every K, same as k-means' inertia.

Information criteria add a penalty for the number of parameters p. AIC adds 2 per parameter; BIC adds log n per parameter, here log 500 ≈ 6.2, so BIC penalizes complexity more and prefers smaller models. For both, lower is better.

K = 1: one ellipse for everything, BIC 4142.
[click] K = 2: two components; the two big clusters get merged. 3944.
[click] K = 3: the fit improves enormously, −2 log L drops by about 500, for 6 more parameters. BIC 3485, the minimum, and AIC agrees.
[click] K = 4: the fit improves by only 4, the penalty grows by 6 parameters times 6.2. BIC up to 3519.
[click] K = 6, [click] K = 8: −2 log L keeps creeping down, BIC keeps climbing.

In code: loop over K, fit, call gmm.bic(X), take the smallest. Use n_init > 1 inside the loop so each K gets its best fit. Rule of thumb: BIC when you want the number of real groups; AIC tends to pick more components, which is fine when you want the best density estimate, for anomaly detection or generation. We'll see them disagree on Old Faithful.
-->

---
glowSeed: 799
---

# Choose K and Covariance Type Together

<div class="grid grid-cols-[1.6fr_1fr] gap-6 items-center">
<div>
<BicGrid />
</div>
<div class="space-y-3 text-left text-sm">
<div border="2 solid teal-800" bg="teal-800/20" rounded-lg px-4 py-2>
<b class="text-teal-300">full, K = 3</b> wins: BIC {{ bic.sweep.full[2].bic.toFixed(0) }}.
</div>
<div border="2 solid white/5" bg="white/5" rounded-lg px-4 py-2>
Constrained shapes want <b>more components</b>: K = {{ bic.best.spherical }}–{{ bic.best.diag }}, stacking small round or axis-aligned blobs to imitate tilted ellipses.
</div>
<div border="2 solid white/5" bg="white/5" rounded-lg px-4 py-2>
Grid over both, keep the lowest BIC. Number of components ≠ number of "real" clusters when shapes are wrong.
</div>
</div>
</div>

<script setup>
import bic from '@data/bic.json'
</script>

<!--
The two choices interact. BIC for every covariance type and every K from 1 to 8. Rings mark each type's best K.

Full covariance has the lowest BIC overall, at K = 3, the true number. But look at the others: spherical's best is K = 6, diag's K = 7, tied's K = 6. When each component can't tilt, the best the model can do is tile the tilted cluster with several smaller components. Their best BICs, around 3540 to 3575, are still well above full at K = 3.

The lesson: in a GMM the number of components is not automatically the number of clusters. If the shape assumption is too rigid, extra components are spent approximating shapes. The practical recipe, straight from the scikit-learn documentation: grid-search covariance_type and n_components together and keep the lowest BIC.
-->

---
glowSeed: 800
---

# Gaussian Mixtures in scikit-learn

<div class="grid grid-cols-[1.45fr_1fr] gap-6">
<div>

```python
from sklearn.mixture import GaussianMixture

gmm = GaussianMixture(n_components=3, covariance_type="full",
                      n_init=1, random_state=0)  # init: k-means
gmm.fit(X)                     # X: (500, 2), no labels
gmm.converged_, gmm.n_iter_    # (True, 6)
gmm.weights_.round(2)          # [0.43 0.37 0.21]
gmm.means_.round(2)            # [[0.06 0.06] [4.34 1.27] [2.56 -2.54]]

P = gmm.predict_proba(X)       # (500, 3) responsibilities
P[[0, 1, 423]].round(2)        # [[0.07 0.93 0.  ]
                               #  [0.   0.   1.  ]
                               #  [0.54 0.46 0.  ]]
gmm.predict(X[[0, 1, 423]])    # [1 2 0]   argmax of each row
gmm.bic(X), gmm.aic(X)         # (3485.2, 3413.5)
gmm.score_samples(X[:2])       # log p(x): [-3.1 -3.71]
```

</div>
<div class="space-y-3 text-sm text-left">
<div border="2 solid white/5" bg="white/5" rounded-lg px-4 py-2>
<code>predict_proba</code>: the γ table. Row 423 is a boundary point: <b>0.54 / 0.46</b>.
</div>
<div border="2 solid white/5" bg="white/5" rounded-lg px-4 py-2>
<code>score_samples</code>: log-density of each point, for anomalies. <code>sample(n)</code>: new data.
</div>
<div border="2 solid amber-800" bg="amber-800/20" rounded-lg px-4 py-2>
Set <code>n_init</code> &gt; 1. Scale features first: a Gaussian's shape is in the units you give it, though full Σ absorbs per-feature scale better than k-means.
</div>
</div>
</div>

<!--
All of it in scikit-learn. GaussianMixture with n_components and covariance_type; fit on unlabeled X. These are the actual outputs on the running example.

It converged in 6 iterations, from a k-means start, which is why it is so much faster than our deliberately bad start. The weights 0.43, 0.37, 0.21 and the means are close to the true 0.45/0.35/0.20 and (0,0), (4.2,1.4), (2.6,−2.6).

predict_proba returns the responsibility table. Point 0 is 93% component 2. Point 1 is certainly component 3. Point 423 sits between the two big components and is split 0.54/0.46. predict returns the argmax of each row: 1, 2, 0, using Python's 0-based component numbers.

bic and aic for model selection, as on the previous slides. score_samples gives the log density log p(x) of each point under the whole mixture, which we use next for anomaly detection, and sample(n) generates new points from the fitted story.

On scaling: a full covariance matrix adapts to features in different units much better than k-means does, since it learns a variance per feature. But numerical stability and the reg_covar floor still work best with standardized features, so scale anyway unless the units are meaningful together.
-->

---
layout: center
class: text-center
glowSeed: 801
---

# Part 5 · Real Data, and What a Density Buys You

<div class="text-lg opacity-80 mt-3">A geyser, a garden, and two moons</div>

<!--
Part five: two real datasets, the uses of a density model beyond clustering, and one case where a GMM is the wrong tool.
-->

---
glowSeed: 802
clicks: 2
---

# Old Faithful: Two Kinds of Eruption

<Faithful :step="$clicks" />

<!--
Old Faithful, the geyser in Yellowstone, a classic dataset: 272 eruptions, each with its duration and the waiting time before it, both in minutes.

Even gray, two groups are obvious: short eruptions after short waits, and long eruptions after long waits. But both groups are tilted ellipses, and the bottom-left group is much smaller.

[click] Fit GMMs with K = 1 to 6, ten starts each. BIC is lowest at K = 2: 2322, against 2335 for K = 3. The two components: short eruptions of about 2.0 minutes after a 54-minute wait, 36% of eruptions; long ones of about 4.3 minutes after an 80-minute wait, 64%. Both ellipses are tilted: within each type, a longer wait goes with a longer eruption. Only one eruption has its largest responsibility below 0.9: the two types barely overlap.

For comparison, AIC reaches its minimum at K = 6. That is the BIC/AIC difference from before: AIC is happy to add components that improve the density a little; BIC asks whether they are worth it.

[click] Now use the density itself. score_samples gives every eruption's log-density under the model. Flag the lowest 2%: 6 eruptions below log p = −7.3. They are mostly mid-length eruptions, 2.4 to 3.4 minutes, in the sparse zone between the two types. The model says these are unusual eruptions; a geologist might want to look at them. That is anomaly detection with a GMM: fit the density, flag low-density points. Choosing the 2% cutoff is a decision, like a classification threshold.
-->

---
glowSeed: 803
---

# The Density Landscape and Its Anomalies

<div class="grid grid-cols-[1.45fr_1fr] gap-6 items-center">
<div>
<Faithful3D />
</div>
<div class="space-y-3 text-left text-sm">
<div border="2 solid white/5" bg="white/5" rounded-lg px-4 py-2>
Two ridges, one per eruption type. Each eruption is lifted to its own density.
</div>
<div border="2 solid red-800" bg="red-800/20" rounded-lg px-4 py-2>
<b class="text-red-300">Red plane:</b> the density threshold. The 6 red points fall below it.
</div>

```python
logp = gmm.score_samples(X)
cut = np.percentile(logp, 2)
anomalies = X[logp < cut]
```

</div>
</div>

<!--
The same fitted model as a landscape. The surface is the GMM density over the plane of (duration, wait): two tilted ridges, the long-eruption one taller since it holds 64% of the eruptions. Every eruption is drawn at the height of its own density, so typical eruptions ride on the ridges.

The translucent red plane is the 2% threshold. The six anomalies are the red points below it, down in the valley between the ridges. That is all anomaly detection with a density model is: anything that falls below the waterline is unusual.

This only works because a GMM is a full probability model. k-means could give "distance to nearest center", but that ignores that one cluster is wide and another tight; DBSCAN gives noise labels but no graded score. A GMM's log-density is a single, comparable score for any new point, which is why GMMs are a standard baseline for anomaly detection when the normal data looks like a few blobs.
-->

---
glowSeed: 804
---

# A GMM Can Generate New Data

<FaithfulSample />

<div class="grid grid-cols-[1fr_1.3fr] gap-5 mt-3 items-center text-left">

```python
X_new, comp = gmm.sample(272)
```

<div class="text-sm" border="2 solid white/5" bg="white/5" rounded-lg px-4 py-2>
Run the generative story forward: spin the wheel, draw from that Gaussian. Synthetic data with the same structure, the simplest <b>generative model</b>.
</div>
</div>

<!--
Because a GMM is a story of how data is generated, we can run the story forward. gmm.sample(272) spins the wheel 272 times with the fitted weights and draws each point from the chosen Gaussian. It returns the points and which component made each one.

Left, the real eruptions. Right, synthetic ones appearing as they are drawn. Same two groups, same tilt, same proportions. Not the same points: new, plausible eruptions.

Two honest caveats. The samples are only as good as the model: if the real clusters were curved, the samples would still be ellipses. And this is the simplest member of a big family. Modern generative models for images and text are vastly more flexible, but the idea, learn a probability distribution and then sample from it, is the same. Some of them literally use Gaussian mixtures inside.
-->

---
glowSeed: 805
clicks: 2
---

# Iris in 3D: Ellipsoids vs. Spheres

<div class="grid grid-cols-[1.35fr_1fr] gap-6 items-center">
<div>
<Iris3D :by="['species', 'km', 'gmm'][$clicks]" />
</div>
<div class="space-y-3 text-left text-sm">
<div border="2 solid white/5" bg="white/5" rounded-lg px-4 py-2>
150 flowers · petal length, petal width, sepal length (cm). Colors: <b>{{ ['true species (hidden from both methods)', 'k-means, K = 3', 'GMM, K = 3, full covariance'][$clicks] }}</b>
</div>
<div class="reveal" :class="{ shown: $clicks >= 1 }" border="2 solid red-800" bg="red-800/20" rounded-lg px-4 py-2>
<b class="text-red-300">k-means</b> · ARI {{ iris.kmAri.toFixed(2) }}. Cuts the two overlapping species with a flat plane.
</div>
<div class="reveal" :class="{ shown: $clicks >= 2 }" border="2 solid teal-800" bg="teal-800/20" rounded-lg px-4 py-2>
<b class="text-teal-300">GMM</b> · ARI {{ iris.gmmAri.toFixed(2) }}. Elongated, tilted ellipsoids follow each species. (All 4 features: {{ iris.gmmAri4.toFixed(2) }} vs. {{ iris.kmAri4.toFixed(2) }}.)
</div>
</div>
</div>

<script setup>
import iris from '@data/iris.json'
</script>

<!--
Fisher's iris data in three of its four measurements. The colors here are the three species, which neither method sees. Setosa, small petals, is far off on its own. Versicolor and virginica overlap, and both are elongated: bigger flowers are bigger in every measurement, so each species is a stretched, tilted cloud.

[click] k-means with K = 3. Setosa is perfect, but between the other two it draws a flat plane, the perpendicular bisector, which cuts across their stretched clouds at the wrong angle. ARI 0.73.

[click] GMM with full covariance. The translucent shells are each component's ellipsoid at Mahalanobis distance 2. Each one lines up with its species' elongated cloud, and the border between versicolor and virginica follows their shapes. ARI 0.94. With all four features, GMM 0.90 against k-means 0.73. The plot rotates; drag it to look along the long axes.
-->

---
glowSeed: 806
clicks: 2
---

# Where GMM Fails: Shapes That Aren't Ellipses

<div class="grid grid-cols-3 gap-4 mt-2">
<div>
<GmmPlot :pts="moons.pts" :mix="moons.k2" mode="soft" frame :w="280" :h="210" :r="2.2" label="Two Gaussians on two moons" />
<div class="text-sm text-center mt-1"><b>K = 2</b> · ARI {{ moons.k2.ari.toFixed(2) }}</div>
</div>
<div class="reveal" :class="{ shown: $clicks >= 1 }">
<GmmPlot :pts="moons.pts" :mix="moons.k10" mode="hard" field="density" :levels="[1]" :means="false" frame :w="280" :h="210" :r="2.2" label="Ten Gaussians tile the moons" />
<div class="text-sm text-center mt-1"><b>K = 10</b> · density fits · as clusters, ARI {{ moons.k10.ari.toFixed(2) }}</div>
</div>
<div class="reveal" :class="{ shown: $clicks >= 2 }">
<GmmPlot :pts="moons.synth" mode="gray" frame :w="280" :h="210" :r="2.2" :domain="{ x: [-1.35, 2.35], y: [-0.75, 1.25] }" label="300 points sampled from the ten-component GMM" />
<div class="text-sm text-center mt-1"><b>Samples</b> from K = 10 look like moons</div>
</div>
</div>

<div class="text-sm mt-4" border="2 solid white/5" bg="white/5" rounded-lg px-4 py-2>
A Gaussian is convex. Curved clusters → use DBSCAN/HDBSCAN for labels; a many-component GMM is still a fine <b>density</b>.
</div>

<script setup>
import moons from '@data/moons.json'
</script>

<!--
The honest limitation, promised at the end of the last deck: the two moons. A Gaussian's contours are ellipses, convex, so one Gaussian can't follow a curved moon. With K = 2, each component covers half of both moons: ARI 0.46. Better than k-means' 0.23, because soft, tilted ellipses fit a bit better, but wrong.

[click] Give it more components. BIC's choice on the moons is K = 8; here K = 10. The mixture now tiles each moon with small ellipses, and the shaded density follows the moons beautifully. But as a clustering it is worse: ten components are ten clusters, each moon chopped into pieces, ARI 0.21. Components are not clusters.

[click] Yet as a density model, it is good: 300 points sampled from the ten-component GMM trace out two moons.

So: for clusters with curved or irregular shapes, use the density-based methods from last time. A GMM remains useful there as a density estimator, for scoring and sampling, and you can merge its components into clusters afterwards, but that merging is a separate step.
-->

---
layout: center
class: text-center
glowSeed: 807
---

# Part 6 · The Big Picture

<div class="text-lg opacity-80 mt-3">k-means was a Gaussian mixture all along</div>

<!--
Last part. Two decks ago we met k-means. It turns out we could have derived it from today's model.
-->

---
glowSeed: 808
---

# k-Means Is a GMM with the Knobs Turned Down

<KmeansLimit />

<div class="grid grid-cols-[1.7fr_1fr] gap-4 mt-1 items-center text-left">
<div border="2 solid teal-800" bg="teal-800/20" rounded-lg px-3 style="font-size: .72em">

$$
\pi_k=\tfrac1K,\ \Sigma_k=\sigma^2 I:\quad \gamma_{ik}=\frac{e^{-\lVert\mathbf x_i-\boldsymbol\mu_k\rVert^2/2\sigma^2}}{\sum_j e^{-\lVert\mathbf x_i-\boldsymbol\mu_j\rVert^2/2\sigma^2}}\ \xrightarrow{\ \sigma^2\to0\ }\ \mathbb 1\big[k=\arg\min_j\lVert\mathbf x_i-\boldsymbol\mu_j\rVert\big]
$$

</div>
<div class="text-sm" border="2 solid white/5" bg="white/5" rounded-lg px-4 py-2>
E → nearest center. M → plain means. <b>EM = Lloyd's algorithm.</b>
</div>
</div>

<!--
The three blobs from the k-Means deck, with the k-means centroids. Make three restrictions on a GMM: equal weights, every covariance the same sphere σ²I, and σ² not learned but fixed. Then shrink σ².

With equal weights and a shared spherical covariance, the responsibilities depend only on Euclidean distances to the means: the formula in the card. The background regions are already exactly k-means' Voronoi cells, for every σ², because all the quadratic terms cancel. What changes is how sharp the hand-off is. On the right, the responsibility along the segment between the two closest centers: at large σ² a gentle S-curve; as σ² shrinks, a step at the midpoint.

Watch the points. At large σ², most points are blended colors, and the counter of points with no component above 0.99 is in the hundreds. As σ² goes to zero, every point snaps to its nearest center's color: the softmax becomes an argmax. The E-step has become k-means' assignment step. And with 0/1 responsibilities, the M-step mean is the plain average of the assigned points: k-means' update step. EM in this limit is exactly Lloyd's algorithm.

That explains everything about k-means in one sentence: k-means is a GMM that assumes equal-size, equally weighted, round clusters, and hard assignments. Every k-means failure we saw is one of those assumptions being false. Every GMM fix is one of them being relaxed: full covariance for shape, weights for size, responsibilities for uncertainty.
-->

---
glowSeed: 809
---

# Choosing a Clustering Method

<table class="choose">
<thead><tr><th /><th>Cluster shape</th><th>Needs</th><th>Membership</th><th>Scales to</th><th>Reach for it when</th></tr></thead>
<tbody>
<tr><td class="text-blue-300">k-means</td><td>round, similar size</td><td>K</td><td>hard</td><td>millions</td><td>you need K prototypes or a fast partition</td></tr>
<tr><td class="text-violet-300">Hierarchical</td><td>depends on linkage</td><td>linkage, cut</td><td>hard</td><td>~10⁴</td><td>the tree is the answer, or a custom distance</td></tr>
<tr><td class="text-amber-300">DBSCAN / HDBSCAN</td><td>any shape</td><td>ε, minPts / min size</td><td>hard + noise</td><td>~10⁶</td><td>curved shapes, outliers, varying density</td></tr>
<tr class="hl"><td class="text-teal-300">GMM</td><td>ellipses, any size/tilt</td><td>K, covariance type</td><td><b>probabilities</b></td><td>millions (low d)</td><td>overlapping clusters, uncertainty, a density for scoring or sampling</td></tr>
</tbody>
</table>

<div class="text-sm mt-4 text-left" border="2 solid white/5" bg="white/5" rounded-lg px-4 py-2>
GMM's extra costs: more parameters (watch d), local optima (use <code>n_init</code>), and K chosen by BIC rather than read from the data.
</div>

<style>
.choose { width: 100%; border-collapse: separate; border-spacing: 0 4px; font-size: 0.85rem; margin-top: 0.5rem; }
.choose th { font-size: 0.72rem; text-transform: uppercase; letter-spacing: 0.05em; opacity: 0.6; text-align: left; padding: 2px 8px; }
.choose td { background: rgba(255, 255, 255, 0.05); padding: 8px; text-align: left; }
.choose td:first-child { font-weight: 700; border-radius: 6px 0 0 6px; }
.choose td:last-child { border-radius: 0 6px 6px 0; }
.choose tr.hl td { background: rgba(45, 212, 191, 0.12); }
</style>

<!--
The table from the end of last deck, with the GMM row filled in.

k-means: round, similar-size clusters, hard labels, extremely fast. Hierarchical: a tree, any distance, small data. DBSCAN and HDBSCAN: any shape, noise, but hard labels and no density you can evaluate at new points.

GMM: ellipses of any size and orientation, overlapping allowed; you choose K and the covariance type, ideally both by BIC; and membership is a probability. It scales linearly in n, but quadratically in d with full covariances. Reach for it when clusters overlap and you care about how sure each assignment is, or when you want a density: anomaly scores, synthetic data.

Its costs, from today: parameter count in high dimension, local optima, and the need to pick K. The shape limitation too: ellipses only.
-->

---
glowSeed: 810
clicks: 6
---

# Summary

<div class="grid grid-cols-3 gap-4 mt-6 text-left">
<div class="reveal" :class="{ shown: $clicks >= 1 }" border="2 solid teal-800" bg="teal-800/20" rounded-lg px-4 py-3>
<div class="font-bold text-teal-300">A cluster is a Gaussian</div>
<div class="text-sm opacity-85 mt-1">Mean = center; covariance = an ellipse. Distance is Mahalanobis, in the cluster's own shape.</div>
</div>
<div class="reveal" :class="{ shown: $clicks >= 2 }" border="2 solid amber-800" bg="amber-800/20" rounded-lg px-4 py-3>
<div class="font-bold text-amber-300">Mixture = generative story</div>
<div class="text-sm opacity-85 mt-1">Pick k with probability πₖ, draw from its Gaussian. Responsibilities γ = Bayes' rule, read backwards.</div>
</div>
<div class="reveal" :class="{ shown: $clicks >= 3 }" border="2 solid violet-800" bg="violet-800/20" rounded-lg px-4 py-3>
<div class="font-bold text-violet-300">EM</div>
<div class="text-sm opacity-85 mt-1">E: soft labels. M: weighted means, covariances, weights. Likelihood never drops; local optima → n_init.</div>
</div>
<div class="reveal" :class="{ shown: $clicks >= 4 }" border="2 solid blue-800" bg="blue-800/20" rounded-lg px-4 py-3>
<div class="font-bold text-blue-300">Model choice</div>
<div class="text-sm opacity-85 mt-1">Covariance type trades flexibility for parameters. Pick K (and type) by lowest BIC.</div>
</div>
<div class="reveal" :class="{ shown: $clicks >= 5 }" border="2 solid orange-800" bg="orange-800/20" rounded-lg px-4 py-3>
<div class="font-bold text-orange-300">A density, not just labels</div>
<div class="text-sm opacity-85 mt-1">score_samples for anomalies, sample for new data. Components ≠ clusters for curved shapes.</div>
</div>
<div class="reveal" :class="{ shown: $clicks >= 6 }" border="2 solid red-800" bg="red-800/20" rounded-lg px-4 py-3>
<div class="font-bold text-red-300">k-means is a special case</div>
<div class="text-sm opacity-85 mt-1">Equal weights, shared σ²I, σ² → 0: EM becomes Lloyd's algorithm.</div>
</div>
</div>

<!--
Six takeaways.

[click] A GMM models each cluster as a Gaussian: a center plus a covariance matrix, which is an ellipse whose axes are its eigenvectors. Points are judged by Mahalanobis distance, in the cluster's own shape.
[click] The mixture is a generative story: choose a component with probability π_k, then draw from it. Reading it backwards with Bayes' rule gives responsibilities, soft labels that say how sure we are.
[click] EM fits it: E-step computes responsibilities, M-step refits each Gaussian with responsibility weights. The likelihood never decreases, but EM finds local optima, so use several starts. Watch for collapsing components; reg_covar guards against them.
[click] Covariance type is a flexibility/parameter trade-off, quadratic in d for full. Choose the number of components and the type by BIC.
[click] A GMM is a density model: anomaly scores with score_samples, synthetic data with sample. For curved clusters its components are pieces, not clusters.
[click] And k-means is the special case with equal weights, a shared shrinking sphere, and hard assignments.
-->

---
glowSeed: 811
---

# Next: Dimensionality Reduction

<div class="grid grid-cols-[1.2fr_1fr] gap-8 items-center mt-2">
<div>
<DimTeaser />
</div>
<div class="text-left space-y-4">
<div border="2 solid white/5" bg="white/5" rounded-lg px-4 py-3 class="text-sm">
<b class="text-red-300">The problem:</b> full-covariance GMMs need ~d²/2 numbers per component, and distances lose meaning in high dimension.
</div>
<div border="2 solid teal-800" bg="teal-800/20" rounded-lg px-4 py-3 class="text-sm">
<b class="text-teal-300">Next deck:</b> these 3D points really live on a tilted plane. PCA finds the few directions that matter, and its axes are the <b>eigenvectors of a covariance matrix</b>, today's ellipse axes. Then t-SNE and UMAP for visualizing structure.
</div>
</div>
</div>

<!--
Every method in this unit so far has worked on the raw features, and in high dimensions that gets hard. For GMMs especially: a full covariance needs about d²/2 numbers per component, and in a few hundred dimensions you never have enough points per component to estimate them. Distance-based methods suffer the curse of dimensionality from the k-NN lecture.

The plot is a hint of the fix. Three coordinates per point, but rotate it and you'll see all the points lie close to one tilted plane: two directions carry all the structure, the third is noise. Next deck, PCA finds those directions, and it does it with exactly today's tool: the eigenvectors of the data's covariance matrix, the axes of its ellipse. Then t-SNE and UMAP, for visualizing high-dimensional structure in 2D. In practice, reducing dimension first and then clustering, often with a GMM, is a very common pipeline.
-->
