---
theme: default
highlighter: shiki
css: unocss
colorSchema: dark
title: 'Hierarchical and Density-Based Clustering'
info: |
  ## Hierarchical and Density-Based Clustering
  Clusters without centroids: trees of merges, and islands of density
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
glowSeed: 750
---

# Hierarchical and Density-Based Clustering {.!text-5xl}

### Clusters without centroids

<div class="mt-1 max-w-3xl mx-auto">
<HeroGrow />
</div>

<div class="opacity-80 text-lg">Unsupervised Learning · Foundations of Machine Learning</div>

<!--
Last time, k-means: every cluster is a center, and every point belongs to its nearest center. Today we drop the centers.

The animation is DBSCAN, one of today's main algorithms. It picks a point in a dense region and spreads outward to every point that is close enough and has enough neighbors, like a flood fill. It traces the two moons and the two rings exactly, shapes that k-means cannot represent at all, and the scattered points it never reaches stay gray: they are labeled noise rather than forced into a cluster.

Roadmap: why we need a different definition of a cluster → hierarchical clustering, which builds a whole tree of merges → density-based clustering with DBSCAN and HDBSCAN → three real datasets: an animal taxonomy, the world's earthquakes, and California's cities → how to compare clusterings and choose a method.

Every number on these slides comes from scripts/make_data.py in the deck folder, run with fixed seeds.
-->

---
glowSeed: 751
clicks: 2
---

# Where k-Means Left Off

<div class="grid grid-cols-[1.3fr_1fr] gap-8 items-center mt-2">
<div>
<ClusterPlot v-bind="$clicks >= 1 ? { pts: moons.pts, lab: moons.db } : { pts: moons.pts, lab: moons.km, centroids: moons.kmC, cells: true }" frame :w="500" :h="340" :r="3.2" label="Two moons: k-means cuts across them; DBSCAN follows each moon" />
<div class="text-center text-sm font-mono mt-1" style="min-height: 1.5em">{{ $clicks >= 1 ? `DBSCAN · ARI ${moons.dbAri.toFixed(2)}` : `k-means, K = 2 · ARI ${moons.kmAri.toFixed(2)}` }}</div>
</div>
<div class="space-y-4 text-left">
<div border="2 solid red-800" bg="red-800/20" rounded-lg px-4 py-3>
<div class="font-bold text-red-300">Centroid-based</div>
<div class="text-sm opacity-85 mt-1">A cluster is the region closest to a center. Borders are straight, so curved shapes get cut.</div>
</div>
<div class="reveal" :class="{ shown: $clicks >= 1 }" border="2 solid teal-800" bg="teal-800/20" rounded-lg px-4 py-3>
<div class="font-bold text-teal-300">Connectivity- and density-based</div>
<div class="text-sm opacity-85 mt-1">A cluster is a set of points <b>linked to each other</b> through close neighbors or dense regions. Any shape is allowed.</div>
</div>
<div class="reveal text-sm" :class="{ shown: $clicks >= 2 }" border="2 solid white/5" bg="white/5" rounded-lg px-4 py-3>
Two consequences: there is <b>no center</b> to summarize a cluster, and a point need not belong to any cluster at all. It can be <b>noise</b>.
</div>
</div>
</div>

<script setup>
import moons from '@data/moons.json'
</script>

<!--
This is where the k-means deck ended: the two moons. k-means with K = 2 puts two centers down and splits the plane with a straight line between them, so each moon is cut in half. The adjusted Rand index, agreement with the true moons, is 0.23.

The problem is not the algorithm, it is the definition. In k-means a cluster is "the points closest to a center", and that definition can only produce convex regions with straight borders.

[click] Change the definition: a cluster is a set of points that are linked to each other, each one close to another, through regions where points are dense. Under that definition the moons are obvious: you can walk along each moon taking small steps without ever crossing an empty gap. DBSCAN with that idea gets both moons exactly, ARI 1.00.

[click] Two consequences to keep in mind all lecture. There is no centroid: a cluster is just a set of points, so there is no single prototype to report. And clustering no longer has to be a partition: a point in an empty region can be left unassigned and labeled noise. That turns out to be very useful on real data.
-->

---
glowSeed: 752
clicks: 3
---

# Today: Three Ways to Cluster Without Centroids

<div class="grid grid-cols-3 gap-5 mt-6">
<div class="reveal text-left" :class="{ shown: $clicks >= 1 }" border="2 solid teal-800" bg="teal-800/20" rounded-lg px-4 py-3>
<ClusterPlot :pts="grid.moons.pts" :lab="grid.moons.single.lab" :w="260" :h="150" :r="2" label="Single-linkage hierarchical clustering on two moons" />
<div class="font-bold text-teal-300 mt-2">Hierarchical</div>
<div class="text-sm opacity-85 mt-1">Repeatedly merge the two closest clusters. The output is a <b>tree</b>; cut it to get any number of clusters.</div>
</div>
<div class="reveal text-left" :class="{ shown: $clicks >= 2 }" border="2 solid blue-800" bg="blue-800/20" rounded-lg px-4 py-3>
<ClusterPlot :pts="gallery.circles.pts" :lab="gallery.circles.db" :w="260" :h="150" :r="2" label="DBSCAN on two rings" />
<div class="font-bold text-blue-300 mt-2">DBSCAN</div>
<div class="text-sm opacity-85 mt-1">Grow clusters through <b>dense neighborhoods</b> of radius ε. Points in sparse regions become noise.</div>
</div>
<div class="reveal text-left" :class="{ shown: $clicks >= 3 }" border="2 solid violet-800" bg="violet-800/20" rounded-lg px-4 py-3>
<ClusterPlot :pts="varied.pts" :lab="varied.hdb" :w="260" :h="150" :r="1.8" label="HDBSCAN on clusters of two different densities" />
<div class="font-bold text-violet-300 mt-2">HDBSCAN</div>
<div class="text-sm opacity-85 mt-1">DBSCAN at <b>every ε at once</b>, keeping the clusters that persist. Handles clusters of different densities.</div>
</div>
</div>

<div class="mt-5 text-sm opacity-80">Then: three real datasets, and how to compare clusterings when there is no test accuracy.</div>

<script setup>
import grid from '@data/linkgrid.json'
import gallery from '@data/gallery.json'
import varied from '@data/varied.json'
</script>

<!--
Three methods today, each building on the last.

[click] Hierarchical clustering. Start with every point as its own cluster and repeatedly merge the two closest. You get a whole tree of nested clusterings, and you choose the number of clusters afterwards by cutting the tree. With "single linkage" it already solves the moons.

[click] DBSCAN. Pick a radius ε. Points with many neighbors within ε are dense; clusters grow outward through dense points; points with no dense neighborhood are noise. Here it separates two rings, one inside the other, which no centroid method can do.

[click] HDBSCAN. DBSCAN needs one ε for the whole dataset, and that fails when clusters have different densities. HDBSCAN effectively runs DBSCAN for every ε and keeps the clusters that last the longest. Here it finds two tight blobs and one sparse disk at once.

Then we apply them to real data and finish with how to evaluate a clustering without labels.
-->

---
layout: center
class: text-center
glowSeed: 753
---

# Part 1 · Hierarchical Clustering

<div class="text-lg opacity-80 mt-3">Build every clustering at once, as a tree</div>

<!--
Part one: hierarchical clustering. The key idea is that instead of producing one partition into K groups, it produces a nested family of partitions, one for every K from n down to 1, organized as a tree.
-->

---
glowSeed: 754
clicks: 7
---

# Agglomerative Clustering: Merge the Closest Pair

<div class="text-sm opacity-85 -mt-2 mb-2">Start with every point alone · merge the two closest clusters · repeat until one cluster is left</div>

<MergeSteps />

<!--
The algorithm is called agglomerative, bottom-up, clustering. Eight points, A through H. We start with eight clusters of one point each. We need a distance between clusters; for now use the simplest: the distance between their closest points. That is called single linkage.

[click] The closest pair overall is A and B, 0.85 apart: merge them. On the right, the dendrogram records the merge as a link at height equal to the merge distance.
[click] Next closest: D and E, at 0.89.
[click] Then F joins DE, at 1.00.
[click] C joins AB, at 1.14. Notice the dendrogram heights keep increasing: each merge is at least as far as the last.
[click] Now G joins the DEF group, at 1.71.
[click] Then the two big groups merge: ABC with DEFG, at 3.54. That link sits much higher: a big jump.
[click] Finally H, the isolated point on the right, joins last, at 3.88, the top of the tree.

Two things to notice. First, we never chose K. The tree contains every clustering from 8 clusters down to 1; picking K means picking a height to cut at, next slides. Second, the lines drawn on the left are exactly the closest pairs used for each merge. With single linkage these edges form the minimum spanning tree of the points, the shortest network connecting them all. Single linkage clustering is the same thing as building a minimum spanning tree and then cutting its longest edges.
-->

---
glowSeed: 755
clicks: 5
---

# Worked Example: Single Linkage by Hand

<HandMerge />

<div class="mt-1 text-sm text-center opacity-85">

After merging A and B: $\;d(AB,\,C)=\min\{d(A,C),\,d(B,C)\}$ for single linkage, $\;\max\{\cdot\}$ for complete linkage.

</div>

<!--
Let's do it by hand on five points on a number line: A at 1, B at 2, C at 4.5, D at 8, E at 9.5. On the right is the matrix of distances between the current clusters. The amber cell is the smallest one, the next merge.

[click] A and B are 1 apart: merge them, bracket at height 1. Now update the table: the distance from AB to C, with single linkage, is the smaller of d(A,C) = 3.5 and d(B,C) = 2.5, so 2.5. That one rule, take the min, is all single linkage needs.
[click] D and E are 1.5 apart: merge at 1.5.
[click] Now the smallest entry is AB to C at 2.5: merge.
[click] Finally ABC to DE: closest pair is C at 4.5 and D at 8, distance 3.5. Merge heights for single linkage: 1, 1.5, 2.5, 3.5.

[click] Complete linkage uses the farthest pair instead, the max in the update rule. The dashed amber brackets: the first two merges are the same, then ABC forms at 3.5 (A to C), and the final merge is at 8.5, the distance from A to E. Same tree shape here, very different heights. Complete linkage says "these two groups are only close if every member is close", so the final merge looks much less convincing. On other data the shape of the tree changes too, as we'll see.

Cost: each step scans the table for the minimum, so the naive algorithm is cubic in n. Libraries use cleverer updates, but memory for the full distance table is still quadratic.
-->

---
glowSeed: 756
clicks: 3
---

# Reading a Dendrogram: Cut the Tree

<DendroCut />

<div class="mt-2 text-sm text-center opacity-85" style="min-height: 1.5em">
<span class="reveal" :class="{ shown: $clicks >= 1 }">Long vertical branches = groups that stay separate for a long time. Cut across the longest ones.</span>
</div>

<!--
Here is a real dendrogram: Ward linkage on all 300 points of the three-blob data from the k-means deck. Leaves are at the bottom, too many to label; the height of each link is the merge height.

To get a flat clustering, cut the tree with a horizontal line. Every branch the line crosses becomes one cluster. Here the cut crosses two branches: K = 2.

[click] Lower the cut: three branches, K = 3, and these are the three blobs. Look at how long those three vertical branches are: from about 10 up to 30, nothing happens. Long branches mean these groups stay separate over a wide range of distances: a well-separated, natural grouping. That is the dendrogram's version of the elbow.
[click] Lower again: K = 4. One blob splits, but that split sits at a height just under 10, barely above the merges inside the blobs. A short branch, from about 9.7: weak evidence.
[click] K = 6: now we are cutting through the dense lower part of the tree, splitting blobs into arbitrary pieces.

The practical point: you fit once and then can look at every K. A big gap between consecutive merge heights suggests a natural K.
-->

---
glowSeed: 757
clicks: 3
---

# Linkage: How Far Apart Are Two Clusters?

<div class="grid grid-cols-[1.1fr_1fr] gap-6 items-center">
<div>
<LinkageDemo :mode="$clicks" />
</div>
<div class="space-y-2 text-left text-sm">
<div class="lk" :class="{ on: $clicks === 0 }" border="2 solid white/5" bg="white/5" rounded-lg px-3 py-1>

**Single** · closest pair $\;\min_{a\in A,\,b\in B}\lVert a-b\rVert$

</div>
<div class="lk" :class="{ on: $clicks === 1 }" border="2 solid white/5" bg="white/5" rounded-lg px-3 py-1>

**Complete** · farthest pair $\;\max_{a\in A,\,b\in B}\lVert a-b\rVert$

</div>
<div class="lk" :class="{ on: $clicks === 2 }" border="2 solid white/5" bg="white/5" rounded-lg px-3 py-1>

**Average** · all pairs $\;\frac{1}{|A||B|}\sum_{a\in A}\sum_{b\in B}\lVert a-b\rVert$

</div>
<div class="lk" :class="{ on: $clicks === 3 }" border="2 solid white/5" bg="white/5" rounded-lg px-3 py-1>

**Ward** · growth in squared error $\;\frac{|A||B|}{|A|+|B|}\lVert\mu_A-\mu_B\rVert^2$

</div>
</div>
</div>

<style>
.lk { opacity: 0.4; transition: opacity 0.4s ease, border-color 0.4s ease; }
.lk.on { opacity: 1; border-color: rgba(251, 191, 36, 0.7) !important; }
</style>

<!--
The merge loop needs a distance between two clusters, and the choice, called the linkage, is the main modeling decision in hierarchical clustering. Four standard choices, shown on the same two groups.

Single linkage: the distance between the closest pair, one point from each group. Optimistic: two clusters are close if any two members are close.
[click] Complete linkage: the farthest pair. Pessimistic: close only if every member of one is close to every member of the other. Favors compact, round clusters of similar diameter.
[click] Average linkage: the mean over all 42 pairs here. A compromise between the two.
[click] Ward: merge the pair whose union increases the within-cluster sum of squared distances the least. The formula is the increase in exactly the k-means objective J. So Ward is the hierarchical cousin of k-means, with the same preference for compact, similar-size, roughly spherical clusters, and it is the default in scikit-learn.

Single, complete and average work with any distance, even a precomputed one; Ward needs Euclidean distance, because it uses means.
-->

---
glowSeed: 758
clicks: 3
---

# Linkage Changes the Answer

<LinkageGrid :hl="[[], ['moons:single'], ['blobs3:single', 'outliers:single'], ['blobs3:ward', 'outliers:ward']][$clicks]" />

<div class="text-sm text-center mt-2" border="2 solid white/5" bg="white/5" rounded-lg px-4 py-1 style="min-height: 2.4em">
{{ ['Same data, same K, four linkages. ARI = agreement with the true groups.', 'Single linkage follows chains of close points: perfect on the moons.', 'The same chaining is a weakness: one bridge of points or one outlier and almost everything ends up in one cluster.', 'Ward behaves like k-means: compact blobs, good on blobs, bad on moons.'][$clicks] }}
</div>

<!--
Here are the four linkages on three datasets, each cut at the true number of groups. The badge is the adjusted Rand index against the true groups: 1 is perfect, 0 is chance.

[click] Single linkage on the moons: ARI 1.00. Because it only needs one close pair to merge, it walks along each moon point by point. No other linkage gets it: complete 0.20, average 0.43, Ward 0.30.

[click] But the same property is single linkage's weakness, called chaining. On the three blobs, two of the blobs nearly touch, a few points bridge the gap, and single linkage merges through the bridge: 298 points in one cluster and two lone points as the other "clusters". ARI 0.00. With outliers it is the same story: the outliers are the last things to merge, so they become the "clusters".

[click] Ward is the opposite: on the blobs 0.93, on blobs with outliers 0.86, but on the moons it cuts across just like k-means. Average linkage matches Ward on the blobs but collapses with outliers.

Takeaway: the linkage is an assumption about cluster shape. Single linkage = elongated, connected shapes, but needs clean gaps. Ward and complete = compact blobs. Choose it based on what you expect clusters to look like, and check the result.
-->

---
glowSeed: 759
---

# Hierarchical Clustering in Code

<div class="grid grid-cols-[1.25fr_1fr] gap-6">
<div>

```python
from sklearn.cluster import AgglomerativeClustering
from scipy.cluster.hierarchy import linkage, fcluster, dendrogram

# flat labels, like any scikit-learn clusterer
agg = AgglomerativeClustering(n_clusters=3, linkage="ward")
labels = agg.fit_predict(X)

# the whole tree: one row per merge
Z = linkage(X, method="ward")    # [child a, child b, height, size]
print(Z.shape)                   # (299, 4)
print(Z[-4:, 2].round(1))        # [ 9.2  9.7 30.4 41.6]

labels3 = fcluster(Z, t=3, criterion="maxclust")  # cut at K = 3
dendrogram(Z, truncate_mode="lastp", p=12)        # draw the top
```

</div>
<div class="space-y-3 text-sm text-left">
<div border="2 solid white/5" bg="white/5" rounded-lg px-4 py-3>
<b class="text-teal-300">scikit-learn</b> gives labels for one K, or one cut height with <code>distance_threshold=</code>.
</div>
<div border="2 solid white/5" bg="white/5" rounded-lg px-4 py-3>
<b class="text-blue-300">SciPy</b> gives the full tree <code>Z</code> to plot and cut many ways. Both agree: here ARI between them is 1.0.
</div>
<div border="2 solid white/5" bg="white/5" rounded-lg px-4 py-3>
The last merge heights jump from <b>9.7</b> to <b>30.4</b>: a big gap, so K = 3 is the natural cut.
</div>
</div>
</div>

<!--
In code there are two entry points.

scikit-learn's AgglomerativeClustering behaves like every other scikit-learn clusterer: choose the linkage and either n_clusters or a distance_threshold, call fit_predict, get labels.

When you want the tree itself, use SciPy. linkage returns Z, a matrix with one row per merge: the two clusters merged, the height, and the size of the new cluster. 300 points means 299 merges. fcluster cuts the tree, here into 3 clusters, and dendrogram draws it; truncate_mode lastp shows only the top 12 branches, which is how you keep a dendrogram of a large dataset readable.

Look at the last four merge heights: 9.2, 9.7, then 30.4 and 41.6. The last two merges are the ones that join the three blobs. The jump from 9.7 to 30.4 is the big gap we saw in the dendrogram, the evidence for K = 3.

Like k-means, all of this runs on distances, so the k-means deck's advice applies: scale features first.
-->

---
glowSeed: 760
---

# Cost and When to Use It

<div class="grid grid-cols-[1fr_1.1fr] gap-8 items-start mt-2">
<div>
<div class="text-sm opacity-80 mb-2 text-left">Memory for all pairwise distances (8-byte floats, n(n−1)/2 pairs)</div>
<div v-for="r in memRows" :key="r.n" class="grid grid-cols-[7rem_1fr_4.5rem] gap-3 items-center my-3 text-sm">
<div class="text-right opacity-85">{{ r.n }}</div>
<div class="h-4 rounded-full overflow-hidden" style="background: rgba(148,163,184,0.18)"><div class="h-full rounded-full" :style="{ width: r.w + '%', background: r.c }" /></div>
<div class="font-mono">{{ r.t }}</div>
</div>
<div class="text-xs opacity-70 mt-2 text-left">Bar length on a log scale. Time is between O(n²) and O(n³) depending on the linkage.</div>
</div>
<div class="space-y-3 text-left">
<div border="2 solid teal-800" bg="teal-800/20" rounded-lg px-4 py-3>
<div class="font-bold text-teal-300">Use it when</div>
<div class="text-sm opacity-90 mt-1">n is up to roughly ten thousand · the <b>tree itself</b> is the answer (taxonomies, gene families, document topics) · you want any distance, even a precomputed one · you don't know K yet</div>
</div>
<div border="2 solid red-800" bg="red-800/20" rounded-lg px-4 py-3>
<div class="font-bold text-red-300">Watch out for</div>
<div class="text-sm opacity-90 mt-1">Quadratic memory · merges are greedy and never undone · single linkage chains, Ward assumes blobs</div>
</div>
</div>
</div>

<script setup>
// n(n-1)/2 pairs x 8 bytes; bar width on a log scale (each factor of 100 adds a third)
const memRows = [
  { n: 'n = 1,000', w: 33, t: '4 MB', c: '#2dd4bf' },
  { n: 'n = 10,000', w: 66, t: '400 MB', c: '#fbbf24' },
  { n: 'n = 100,000', w: 100, t: '40 GB', c: '#f87171' },
]
</script>

<!--
The cost. Hierarchical clustering needs the distance between every pair of points: n(n−1)/2 numbers. For a thousand points that is 4 megabytes. For ten thousand, 400 megabytes, still fine on a laptop. For a hundred thousand, 40 gigabytes, and the time grows even faster: quadratic for single linkage with clever algorithms, up to cubic for the naive loop. So this is a method for small and medium datasets. (scikit-learn can reduce memory with a connectivity constraint, for example only merging k-nearest neighbors, which also enforces spatial contiguity.)

When is it the right tool? When the hierarchy itself is the deliverable: biologists build trees of species and gene families this way, and libraries build topic hierarchies. When you have a custom distance, say edit distance between strings: single, complete and average linkage accept a precomputed distance matrix. And when you don't know K: fit once, look at the tree, then decide.

Watch out for: the memory wall, greediness (a merge is never undone, so one early mistake propagates up the tree), and the shape assumptions of each linkage we just saw.
-->

---
layout: center
class: text-center
glowSeed: 761
---

# Part 2 · Density-Based Clustering

<div class="text-lg opacity-80 mt-3">Clusters are dense regions, separated by sparse regions</div>

<!--
Part two. Hierarchical clustering with single linkage could follow shapes, but it was fragile: one bridge of points or one outlier broke it. Density-based methods fix that by asking not just "is there a close point?" but "is there a dense crowd of close points?".
-->

---
glowSeed: 762
clicks: 2
---

# Clusters Are Islands of Density

<DensityLandscape :level="$clicks" />

<!--
Here is the mental picture for the whole second half. Take a dataset and estimate how dense the points are everywhere: you get a landscape. This one is for a dataset with two tight blobs side by side at the bottom and one wide, sparse disk at the top. Peaks are where points crowd together.

Now flood the landscape with water. A cluster is an island: a connected region of land above the water level. At this high water level, only the two sharp peaks stick out: two islands, the two tight blobs. The sparse disk is completely under water.

[click] Lower the water. The two tight peaks are close together, and the saddle between them is still quite dense, so they are now connected: one island. The disk is still under water.

[click] Lower it more. The sparse disk finally appears as its own island, but by now the two tight blobs have long since merged.

That is a preview of the main difficulty in this half of the lecture: the right water level for the tight blobs is not the right level for the disk. DBSCAN, next, is essentially one water level. HDBSCAN looks at all of them.

The 3D view spins; you can drag it.
-->

---
glowSeed: 763
clicks: 6
---

# DBSCAN: Core, Border, Noise

<div class="grid grid-cols-[1.45fr_1fr] gap-6 items-center">
<div>
<DbscanAnatomy />
</div>
<div class="space-y-2 text-left text-sm">
<div border="2 solid white/5" bg="white/5" rounded-lg px-3 py-2>
Two settings: a radius <b class="text-teal-300">ε = 1</b> and a count <b class="text-teal-300">minPts = 4</b> (the point itself counts).
</div>
<div class="reveal" :class="{ shown: $clicks >= 3 }" border="2 solid teal-800" bg="teal-800/20" rounded-lg px-3 py-2>
<b class="text-teal-300">Core:</b> at least minPts points within ε.
</div>
<div class="reveal" :class="{ shown: $clicks >= 4 }" border="2 solid amber-800" bg="amber-800/20" rounded-lg px-3 py-2>
<b class="text-amber-300">Border:</b> not core, but within ε of a core point.
</div>
<div class="reveal" :class="{ shown: $clicks >= 5 }" border="2 solid red-800" bg="red-800/20" rounded-lg px-3 py-2>
<b class="text-red-300">Noise:</b> neither. Labeled −1.
</div>
<div class="reveal" :class="{ shown: $clicks >= 6 }" border="2 solid white/5" bg="white/5" rounded-lg px-3 py-2>
<b>Cluster:</b> core points within ε of each other, chained together, plus their border points.
</div>
</div>
</div>

<!--
DBSCAN, density-based spatial clustering of applications with noise, from 1996. It has two settings: a radius ε and a count minPts. In scikit-learn minPts is called min_samples, and it counts the point itself.

[click] Density at a point is measured by counting: draw a ball of radius ε around it and count the points inside. This point has the most neighbors in the set; the count includes itself.

[click] Do that for every point. Here are all the ε-balls and every point's count.

[click] Any point whose count is at least minPts = 4 is a core point, in teal: it sits in a dense region.

[click] A point that is not core but lies within ε of a core point is a border point, in amber, with a dashed line to its core neighbor. Border points are on the edge of a dense region: they belong to the cluster but are not dense themselves.

[click] Everything else is noise, in red: not dense and not near anything dense. DBSCAN gives these the label −1.

[click] Finally the clusters: core points that are within ε of each other are linked, chains of links form a cluster, and each border point joins the cluster of a core point near it. Here: two clusters, and the three isolated points are noise.

Notice what we did not specify: K. The number of clusters comes out of ε and minPts.
-->

---
glowSeed: 764
clicks: 3
---

# How DBSCAN Grows a Cluster

<DbscanGrow />

<!--
Here is the algorithm in motion: the moons plus 14 scattered points, ε = 0.2, minPts = 5.

DBSCAN scans the points. The first time it finds an unvisited core point, it starts a new cluster there, the seed.

[click] Then it is a breadth-first search: add every point within ε of the seed; for each newly added core point, add its ε-neighbors too; and so on. The faint circles show the ε-balls of the newest wave, the frontier. Filled dots are core points and keep the expansion going; rings are border points: they join, but expansion stops at them. The first moon fills up in 17 waves after the seed.

[click] When the search runs out, the cluster is done; DBSCAN continues scanning, finds the next unvisited core point, and grows cluster 2 the same way.

[click] Whatever is never reached is noise: here 6 of the 14 scattered points. The other 8 landed close enough to a moon to be border or even core points of it.

Cost: one ε-neighborhood query per point. With a spatial index like a k-d tree that is roughly n log n in low dimensions, so DBSCAN scales to millions of points, unlike hierarchical clustering. One subtlety: a border point within ε of two different clusters goes to whichever reaches it first, so border assignment can depend on the order of the data. Core points and noise never do.
-->

---
glowSeed: 765
clicks: 3
---

# DBSCAN on k-Means' Failure Cases

<DbscanGallery :show="$clicks" />

<!--
Back to the k-means deck's failure gallery. Top row, k-means: it cuts the moons, cuts the rings into halves (ARI essentially 0), and on blobs plus outliers it has to put the outliers somewhere.

[click] DBSCAN on the moons: ARI 1.00, no noise.
[click] On the two rings: also 1.00. A ring is a perfectly good cluster under the density definition: dense along the ring, empty in the gap.

[click] Blobs plus 15 outliers, with minPts = 10. Here I want to be honest. 13 of the 15 outliers are flagged as noise, which is what we wanted. But DBSCAN also flags 48 points on the thin edges of the blobs as noise, because two of these blobs nearly touch: any ε small enough to separate them is too small for their sparse edges. ARI 0.69, lower than k-means' 0.85 on this one.

Lesson: DBSCAN needs clusters separated by a drop in density. When clusters are compact blobs that touch, k-means can be the better tool. We'll put all of this in one table later.

ARI here treats each noise point as its own singleton cluster, so labeling a point noise is never "free".
-->

---
glowSeed: 766
---

# DBSCAN in scikit-learn

<div class="grid grid-cols-[1.25fr_1fr] gap-6">
<div>

```python
from sklearn.cluster import DBSCAN
from sklearn.neighbors import NearestNeighbors

db = DBSCAN(eps=0.2, min_samples=5).fit(X)
labels = db.labels_                  # cluster ids, -1 = noise
print(labels.max() + 1,              # 2 clusters
      (labels == -1).sum(),          # 0 noise points
      len(db.core_sample_indices_))  # 299 core points

# choosing eps: distance to the 4th nearest other point
d, _ = NearestNeighbors(n_neighbors=5).fit(X).kneighbors(X)
kdist = np.sort(d[:, -1])            # plot it, look for the knee
```

</div>
<div class="space-y-3 text-sm text-left">
<div border="2 solid white/5" bg="white/5" rounded-lg px-4 py-3>
<b class="text-teal-300">Scale first.</b> ε is a distance in feature units. Use <code>make_pipeline(StandardScaler(), DBSCAN(...))</code>.
</div>
<div border="2 solid white/5" bg="white/5" rounded-lg px-4 py-3>
<b class="text-amber-300">No predict().</b> New points need a refit, or assign them to the cluster of their nearest core point yourself.
</div>
<div border="2 solid white/5" bg="white/5" rounded-lg px-4 py-3>
<b class="text-blue-300">Any metric.</b> <code>metric="haversine"</code> for latitude and longitude, <code>"cosine"</code> for text embeddings, or <code>"precomputed"</code>.
</div>
</div>
</div>

<!--
The scikit-learn API: DBSCAN with eps and min_samples, fit, read labels_. Noise is −1, so the number of clusters is labels.max() + 1, and noise is the count of −1 labels. On the moons: 2 clusters, no noise, 299 of 300 points are core. core_sample_indices_ lists the core points.

The last three lines compute the k-distance curve that we will use on the next slide to choose ε. Note the off-by-one: kneighbors on the training data returns the point itself as its own nearest neighbor, so n_neighbors = 5 gives the distance to the 4th other point, which is exactly the radius a point needs to have 5 points in its ε-ball, counting itself.

Three practical notes. ε is a distance in the units of your features, so scale first, just like k-means. There is no predict method: DBSCAN describes the data it was given. To label new points, either refit or give each new point the label of its nearest core point if it is within ε. And DBSCAN accepts any distance metric, which matters for real data: haversine for map coordinates, which we use for earthquakes, cosine for embeddings, or a precomputed matrix.
-->

---
glowSeed: 767
clicks: 2
---

# Choosing ε: The k-Distance Plot

<KDistance />

<!--
How to choose ε. Compute for every point the distance to its 4th-nearest other point, with minPts = 5, and sort. That curve is on the left. A point is a core point exactly when this distance is at most ε, so a horizontal line at ε splits the points: below the line are core, above are not.

Start with ε too small, 0.08. Only the densest points are core, so the moons break into 13 fragments and 142 points are noise.

[click] ε too large, 0.5: every point is core, including the scattered ones, and they chain everything into one cluster.

[click] Look for the bend. Most points sit in dense regions and have small k-distances: the long, slowly rising part. The scattered points have much larger k-distances: the sharp rise at the right. Put ε just past the bend, here 0.2, and the dense points become core while the scattered ones become noise: two moons, 6 noise points. The shaded band shows every ε that gives exactly the two moons: 0.18 to 0.28. A wide band like that is reassuring: the answer does not hinge on the exact value.

Honest caveat: "the knee" is a judgment call. A common automatic rule, the point farthest from the straight line joining the curve's ends, picks 0.15 on this gradual curve, and at 0.15 one moon splits at its thinnest point into two clusters. So read the plot, try a few values around the bend, and look at the results. For minPts, a common rule is twice the number of features; larger minPts gives smoother, more conservative clusters and more noise.
-->

---
glowSeed: 768
clicks: 3
---

# Where DBSCAN Fails: Clusters of Different Density

<EpsDilemma />

<!--
DBSCAN's real limitation: one ε for the whole dataset. Here is the landscape data again: two tight blobs close together, and one wide sparse disk. Left: ARI against the true groups for every ε from 0.05 to 1.6. Right: the clustering at the marked ε.

ε = 0.15: the two tight blobs are found perfectly, but the disk is too sparse for any of its points to be core, so all 200 of its points are noise.

[click] ε = 0.3: the disk starts to have core points, but only in patches, so it shatters into fragments. 16 clusters.

[click] ε = 0.6: now the disk holds together as one cluster, but the gap between the tight blobs is smaller than 0.6, so they merge into one.

The curve tells the story: the best ε anywhere gives ARI 0.70, and that is the merged-blobs answer. No single ε separates the tight pair and keeps the disk, because the gap between the tight blobs is smaller than the spacing inside the disk. This is the water-level picture: no water level gives three islands.

[click] HDBSCAN gets all three groups, ARI 0.96, with 13 noise points. How it does this is the next two slides.
-->

---
glowSeed: 769
clicks: 2
---

# HDBSCAN, Step 1: Measure Density Point by Point

<CoreDistance>
<div class="text-sm" border="2 solid teal-800" bg="teal-800/20" rounded-lg px-3 py-1>

$$
d_{\text{mreach}}(a,b)=\max\{\text{core}_k(a),\,\text{core}_k(b),\,d(a,b)\}
$$

</div>
</CoreDistance>

<!--
HDBSCAN, hierarchical DBSCAN, from 2013. The first step replaces the fixed ε-ball with a density measured point by point.

[click] The core distance of a point is the distance to its k-th nearest neighbor; k here is 25. Draw it as a circle around each point, every fifth point shown. In the tight blobs the circles are tiny: 25 neighbors are very close. In the sparse disk they are large. The core distance is a local density estimate: small means dense.

[click] Then HDBSCAN replaces ordinary distance with the mutual reachability distance: the largest of the two points' core distances and their actual distance. For two neighbors inside a tight blob, both core distances are small, so the mutual reachability distance is close to the real distance. For two neighbors in the sparse disk, the distance gets stretched up to their core distance.

Why do this? It pushes sparse points away from everything, so a few stray points can no longer act as a bridge between clusters, the chaining problem from single linkage. Then HDBSCAN does what we did in Part 1: single-linkage hierarchical clustering, but with mutual reachability distance. Density-based and hierarchical clustering meet here.
-->

---
glowSeed: 770
clicks: 3
---

# HDBSCAN, Step 2: Keep the Clusters That Last

<CondensedTree />

<!--
Step two: the tree. HDBSCAN builds the single-linkage tree on the mutual reachability distance and then condenses it: splits that just shed a few points are ignored, and only splits into two groups of at least min_cluster_size points, here 25, count as real splits.

The vertical axis is λ, one over the distance, so going down means going to denser levels. At the top, everything is one cluster. At λ about 0.7 it splits into the sparse disk, right, and the tight pair, left. Each branch gets thinner as points drop out of it. The disk's points all drop out by λ about 1.2. The tight pair splits into its two blobs at λ about 2.5, and those survive much further down.

[click] DBSCAN with one ε is a horizontal cut through this tree: everything crossed by the line is a cluster, the rest is noise. A cut at ε = 1.25 crosses the disk and the still-merged tight pair: two clusters.
[click] A cut at ε = 0.25 crosses the two separate tight blobs, but by that level the disk has dissolved: all of it is noise. Same dilemma as before, now visible as geometry: the branches we want live at different heights.

[click] HDBSCAN does not cut horizontally. It scores every branch by how long it lasts and how many points it holds, its "excess of mass", and picks the best set of non-overlapping branches. The disk is chosen high up, the two blobs further down. ARI 0.96.

The only main parameter is min_cluster_size: the smallest group you would call a cluster. That is much easier to reason about than ε.
-->

---
glowSeed: 771
---

# HDBSCAN in scikit-learn

<div class="grid grid-cols-[1.25fr_1fr] gap-6">
<div>

```python
from sklearn.cluster import HDBSCAN

hdb = HDBSCAN(min_cluster_size=25).fit(X)
labels = hdb.labels_            # -1 = noise
np.unique(labels, return_counts=True)
# (array([-1, 0, 1, 2]), array([ 13, 200, 117, 110]))

hdb.probabilities_              # strength of membership, 0 to 1
# a DBSCAN-style flat cut of the same tree:
hdb.dbscan_clustering(cut_distance=0.25, min_cluster_size=25)
```

</div>
<div class="space-y-3 text-sm text-left">
<div border="2 solid violet-800" bg="violet-800/20" rounded-lg px-4 py-3>
<b class="text-violet-300">min_cluster_size</b>: the smallest group worth calling a cluster. The main setting.
</div>
<div border="2 solid white/5" bg="white/5" rounded-lg px-4 py-3>
<b>min_samples</b> (defaults to min_cluster_size): the k in the core distance. Larger = more conservative, more noise.
</div>
<div border="2 solid white/5" bg="white/5" rounded-lg px-4 py-3>
<b>probabilities_</b>: points near a cluster's core score near 1, points at its fringe lower.
</div>
</div>
</div>

<!--
In scikit-learn since version 1.3, HDBSCAN is in sklearn.cluster. On the varied-density data: three clusters of 200, 117 and 110 points, the disk and the two blobs, plus 13 noise points.

Settings. min_cluster_size is the one to think about: the smallest group you would care about. min_samples is the k used for the core distance; by default it equals min_cluster_size. Raise it to be more conservative, so more points are declared noise.

probabilities_ says how strongly each point belongs to its cluster: points that stay in the branch until deep in the tree score near 1, fringe points lower. Keep that in mind; the next deck turns that idea into actual probabilities.

And dbscan_clustering gives you the DBSCAN-style horizontal cut of the same tree at any distance, without refitting. The cut at 0.25 gives the two blobs and leaves the disk as noise, exactly as on the tree slide.

Like DBSCAN, there is no predict. If you need to label new points, look at the separate hdbscan package, which supports approximate prediction.
-->

---
layout: center
class: text-center
glowSeed: 772
---

# Part 3 · Real Data

<div class="text-lg opacity-80 mt-3">An animal taxonomy, the world's earthquakes, and California's cities</div>

<!--
Part three: three real datasets, each chosen because it suits one of today's methods.

The zoo: a hierarchy is the natural answer, so hierarchical clustering. Earthquakes: clusters are long curved chains with lots of scattered events in between, so DBSCAN. California: cities of very different size and density, so HDBSCAN.
-->

---
glowSeed: 773
clicks: 2
---

# Example 1: A Family Tree for 101 Animals

<ZooTree />

<!--
The UCI Zoo dataset: 101 animals described by 16 traits: hair, feathers, eggs, milk, airborne, aquatic, predator, toothed, backbone, breathes air, venomous, fins, number of legs, tail, domestic, and cat-size or bigger. All yes/no except legs, which I rescaled from 0–8 to 0–1 so it counts about as much as one trait. Distance: the number of traits two animals disagree on, Manhattan distance. Average linkage.

The algorithm never sees the class column: mammal, bird, fish and so on. It is drawn as the strip on the right only to check the result. The tree is drawn sideways: the root on the left, the animals on the right.

Cut into 2: the 41 mammals on one side, all 60 other animals on the other (the largest class there, birds, is only a third of it). The algorithm found the mammal/non-mammal split by itself.

[click] Cut into 4: mammals; birds plus one tortoise (feathers aside, a tortoise lays eggs, breathes air, has a backbone and a tail and no teeth, a lot like a bird in this table); a cold-blooded backboned group of fish, amphibians and reptiles; and the insects and other invertebrates.

[click] Cut into 7: ARI 0.95 against the true classes. Mammals 100% pure; birds 95%; fish 93% (the sea snake joins the fish: aquatic, no legs, backbone); a small group mixing amphibians and reptiles; insects plus slugs and worms; sea invertebrates like octopus, crab and lobster; and the scorpion on its own. Note the mistakes are sensible: they reflect the traits, not errors in the method.

This is the classic use of hierarchical clustering: the tree is the result, and biologists read it as a hypothesis about relatedness.
-->

---
glowSeed: 774
clicks: 1
---

# Zoo: Why These Groups?

<div class="grid grid-cols-[1.05fr_1fr] gap-6 items-center">
<div>
<ZooHeatmap :hl="$clicks >= 1" />
</div>
<div class="space-y-3 text-left">

```python
zoo = pd.read_csv("zoo.data", header=None)
traits = zoo.iloc[:, 1:17].to_numpy(float)
traits[:, 12] /= 8          # legs 0-8 -> 0-1
Z = linkage(traits, method="average",
            metric="cityblock")
groups = fcluster(Z, t=7, criterion="maxclust")
pd.crosstab(groups, zoo[17])   # column 17 = true type
```

<div class="reveal text-sm" :class="{ shown: $clicks >= 1 }" border="2 solid amber-800" bg="amber-800/20" rounded-lg px-4 py-3>
The traits that differ most between the seven groups: <b>{{ zooKey }}</b>. Blocks of shared traits line up with the tree's branches.
</div>
</div>
</div>

<script setup>
import zoo from '@data/zoo.json'
const zooKey = zoo.keyTraits.map(j => zoo.traits[j]).join(', ')
</script>

<!--
Why did the tree split this way? Reorder the original data table by the dendrogram's leaf order. Each row is an animal, each column a trait; teal means yes, and legs is shaded by count. The left band is the 7-cluster cut, the right band the true class.

Because similar animals are now next to each other, the table shows blocks: the mammals at the top all share hair, milk, teeth, backbone, breathing air, and most have a tail. The birds share feathers, eggs, two legs. The fish: aquatic, fins, no legs, eggs.

[click] The traits whose averages differ most between the seven groups, outlined: these are the traits that actually drive the clustering. Reordering a data matrix by a dendrogram is called a clustered heatmap, and it is a standard way to present hierarchical clustering in biology, for example for gene expression data.

The code is five lines: scale the legs column, average linkage with cityblock distance, cut into 7, and cross-tabulate against the true type to check. The crosstab is how I got the purity numbers on the previous slide.
-->

---
glowSeed: 775
---

# Example 2: Earthquakes Trace the Plate Boundaries

<div class="grid grid-cols-[1.15fr_1fr] gap-6 items-center">
<div>
<QuakeGlobe />
</div>
<div class="space-y-3 text-left">
<div border="2 solid white/5" bg="white/5" rounded-lg px-4 py-3>
<div class="text-sm opacity-80">Every M4.5+ earthquake in 2024 (USGS)</div>
<div class="text-sm mt-1"><b class="font-mono text-xl text-teal-300">{{ quakes.n.toLocaleString() }}</b> events → <b class="font-mono text-xl text-teal-300">{{ quakes.k }}</b> clusters + <b class="font-mono text-xl">{{ quakes.noise.toLocaleString() }}</b> noise ({{ Math.round(quakes.noise / quakes.n * 100) }}%)</div>
<div class="text-xs opacity-70 mt-1">DBSCAN, great-circle distance, ε = {{ quakes.epsKm }} km, minPts = {{ quakes.minPts }}</div>
</div>
<div border="2 solid white/5" bg="white/5" rounded-lg px-4 py-2>
<div class="text-xs uppercase tracking-wider opacity-60 mb-1">Largest clusters</div>
<div v-for="t in quakes.top.slice(0, 6)" :key="t.region" class="flex justify-between text-sm"><span>{{ t.region }}</span><span class="font-mono opacity-80">{{ t.n }}</span></div>
</div>
</div>
</div>

<script setup>
import quakes from '@data/quakes.json'
</script>

<!--
Second example: every earthquake of magnitude 4.5 or more recorded worldwide in 2024, from the US Geological Survey's public catalog: 6,397 events, each with a latitude and longitude.

Earthquakes cluster along plate boundaries, which are long, thin, curved lines: exactly the shapes k-means cannot represent. And many quakes happen away from the main belts, which we would rather call noise than force into a cluster.

DBSCAN with ε = 150 km and minPts = 10, using great-circle distance, finds 60 clusters, and 22% of events are noise, shown gray. The largest clusters are the major subduction zones: Tonga–Fiji (which crosses the 180° meridian, more on that in a moment), the Philippines and Molucca Sea, the Izu–Bonin and Mariana arcs south of Japan, Vanuatu, Taiwan, which had a large earthquake sequence in April 2024, and New Guinea.

The globe spins; drag it to look around, and hover over a point to see its magnitude and depth. Regions are named by the most common location in the USGS description of each cluster's events.
-->

---
glowSeed: 776
clicks: 2
---

# Earthquakes: k-Means vs. DBSCAN

<QuakeMap :stage="$clicks" />

<div class="text-sm text-center mt-2" border="2 solid white/5" bg="white/5" rounded-lg px-4 py-1 style="min-height: 2.4em">
{{ ['6,397 events on a map centered on the Pacific, so the Ring of Fire is in one piece.', 'k-means, K = 20: compact regions that chop each arc into pieces and absorb every isolated event.', 'DBSCAN: clusters follow each arc for thousands of kilometers; isolated events are noise.'][$clicks] }}
</div>

<!--
The same data on a flat map, centered on the Pacific so the Ring of Fire is not split at the map's edge.

[click] k-means with K = 20, run on 3D unit vectors so that distances wrap around the globe correctly. It does what k-means does: it tiles the world into 20 compact regions of roughly similar size. Long arcs like the Andes or the Indonesian arc are chopped into pieces, while every isolated quake in the middle of a plate is forced into the nearest region.

[click] DBSCAN instead follows each arc as far as the quakes keep coming, sometimes for thousands of kilometers, separates arcs where there is a gap in activity, and leaves isolated events as noise. For a seismologist the DBSCAN map is the useful one: each cluster is a seismically active zone.

Is DBSCAN perfect here? No: the activity along an arc is not uniform, so a quieter stretch of the same plate boundary can be split off, or become noise. This is where HDBSCAN or a tuned ε would be the next step. And with only one year of data, some clusters are single earthquake sequences, an aftershock swarm, rather than a whole boundary.
-->

---
glowSeed: 777
---

# Earthquakes in Code: Distance on a Sphere

<div class="grid grid-cols-[1.3fr_1fr] gap-6">
<div>

```python
eq = pd.read_csv("usgs_m45_2024.csv")
# haversine expects [latitude, longitude] in radians
X = np.radians(eq[["latitude", "longitude"]].to_numpy())
R = 6371.0                                     # Earth radius, km

db = DBSCAN(eps=150 / R, min_samples=10,
            metric="haversine", algorithm="ball_tree").fit(X)
eq["cluster"] = db.labels_
eq["cluster"].value_counts().head(4)
# -1    1381
#  1     896
#  4     680
#  0     547
```

</div>
<div class="space-y-3 text-sm text-left">
<div border="2 solid red-800" bg="red-800/20" rounded-lg px-4 py-3>
<b class="text-red-300">Raw latitude/longitude is wrong:</b> 179°E and 179°W are 358 apart in degrees but 220 km apart on Earth. Tonga–Fiji would be cut in two.
</div>
<div border="2 solid teal-800" bg="teal-800/20" rounded-lg px-4 py-3>
<b class="text-teal-300">Haversine</b> is great-circle distance on a unit sphere, so ε in km is ε / 6371. The k-distance plot works the same way.
</div>
</div>
</div>

<!--
How this was computed. The point to take away is the distance: on a sphere, Euclidean distance on raw latitude and longitude is wrong in two ways. A degree of longitude shrinks toward the poles, and the map wraps around: 179° east and 179° west look 358 degrees apart, but they are about 220 km apart near the equator. The Tonga–Fiji zone sits right on that line and would be cut in two.

scikit-learn's haversine metric computes great-circle distance on a unit sphere. It expects latitude first, then longitude, in radians. Because distances come out in radians, ε in kilometers is divided by Earth's radius, 6371 km. The ball tree index supports haversine, so this runs in a few hundred milliseconds.

The output: 1,381 noise points, then the largest clusters. This is the general lesson of the first deck again: distance is the model. Choose it to match what "close" means in your problem.
-->

---
glowSeed: 778
clicks: 1
---

# Example 3: Where Are California's Cities?

<CalMetro :stage="$clicks" />

<!--
Third example, and a callback to the k-means deck: the locations of California's 20,640 census block groups. Block groups hold roughly similar numbers of people, so the points are a map of where people live.

Last time we asked k-means to place 8 depots so everyone is close to one. That is the picture now: 8 regions with straight borders, and every block group, including empty desert, belongs to one. That is the right answer for the depot question: everyone must be served.

[click] Different question: where are the cities? That is a density question. HDBSCAN with min_cluster_size = 300 and min_samples = 30 finds 8 metropolitan areas: Los Angeles, the biggest by far with 7,527 block groups, the Peninsula and San Jose, the East Bay, San Diego, Sacramento, Fresno, Stockton and Modesto, and the Inland Empire. Their shapes follow the actual urban areas, like Los Angeles sprawling along the coast and inland. About a quarter of block groups, 5,058, are noise: rural areas and small towns that are not part of a large dense region.

Same data, two methods, two different questions. k-means answers "how do I divide everything into K service areas?". HDBSCAN answers "where are the dense concentrations, whatever their size and shape?".
-->

---
layout: center
class: text-center
glowSeed: 779
---

# Part 4 · Comparing and Choosing

<div class="text-lg opacity-80 mt-3">How do we know a clustering is any good?</div>

<!--
Part four. We have used the adjusted Rand index all lecture. Time to say exactly what it is, when it is legitimate to use, and what to do when there are no labels at all.
-->

---
glowSeed: 780
clicks: 3
---

# Comparing Clusterings: ARI on Benchmarks

<div class="text-sm opacity-85 -mt-2 mb-3 text-left">

**ARI**: the fraction of point pairs that two clusterings treat the same way (same cluster in both, or different in both), adjusted so random labels score 0. **1** = identical, **0** = chance. Each method at its best settings; noise counts as singletons.

</div>

<CompareTable />

<!--
The adjusted Rand index compares two clusterings by looking at every pair of points: are they in the same cluster in both, or in different clusters in both? Then the score is adjusted for chance, so random labels score about 0 and identical clusterings score 1. Cluster ids don't matter, only who is grouped with whom. NMI, normalized mutual information, is a common alternative with the same use.

The table: five methods on five synthetic datasets, each method given its best-case settings: the true K for k-means, Ward and single linkage, and the ε, min_samples and min_cluster_size that score best for the density methods. So these are upper bounds. Hover over any cell to see its clustering; the panel follows the clicks otherwise.

Start: k-means on the moons, 0.23. [click] Single linkage on the moons: 1.00. [click] Single linkage on the blobs: 0.00, chaining. [click] HDBSCAN on the two-density data: 0.97, the only method that gets it.

The pattern: no column is teal all the way down. Every method wins somewhere and fails somewhere.

Important caveat: ARI needs true labels. That is fine for benchmarking a method on data where we know the answer, as here. On real problems, you don't have labels, and if you did, you would not tune your clustering against them; you would use a classifier. So ARI is for testing methods, not for choosing settings on your own data.
-->

---
glowSeed: 781
clicks: 1
---

# Stability: Does the Answer Survive Resampling?

<div class="text-sm opacity-85 -mt-2 mb-2 text-left">No labels needed: refit on 30 random 80% subsamples and compare each with the full-data clustering on the shared points.</div>

<StabilityStrip :truth="$clicks >= 1" />

<div class="text-sm text-center mt-2" border="2 solid white/5" bg="white/5" rounded-lg px-4 py-1 style="min-height: 2.4em">
<span v-if="$clicks < 1">Unstable = untrustworthy: single linkage and HDBSCAN on the blobs change their answer with the sample.</span>
<span v-else><span class="text-amber-300">◆ ARI vs. truth.</span> Stable is not the same as right: k-means is stable on the moons, and wrong.</span>
</div>

<!--
Without labels, one of the best checks is stability. If the structure is real, a clustering of a slightly different sample should give nearly the same answer. Procedure: take 30 random subsamples of 80% of the points, cluster each with the same settings, and compute the ARI between the subsample's labels and the full-data labels on the points they share. Each dot is one subsample; the bar is the median.

Three blobs: k-means is extremely stable, median 0.99. Ward 0.94. Single linkage is all over the place, from 0 to 1, because whether the bridge between blobs survives the subsample decides the whole answer. HDBSCAN is also unstable here: on touching blobs, its choice of branches flips.

On the moons, single linkage, DBSCAN and HDBSCAN are all very stable.

[click] Now the diamonds: ARI against the truth. On the moons, k-means is very stable, median 0.97, and wrong, 0.23. It confidently cuts the moons the same wrong way every time. Instability is a warning sign; stability is necessary but not sufficient. It tells you the method is not just fitting noise, not that its assumptions match the data.

So the toolkit without labels: stability, the elbow and silhouette from the k-means deck (for compact clusters), the dendrogram gaps, the k-distance knee, and above all, looking at the clusters and asking whether they make sense for the problem.
-->

---
glowSeed: 782
---

# Choosing a Method

<table class="choose">
<thead><tr><th /><th>Cluster shape</th><th>Needs</th><th>Noise?</th><th>Scales to</th><th>Reach for it when</th></tr></thead>
<tbody>
<tr><td class="text-blue-300">k-means</td><td>round, similar size</td><td>K</td><td>no</td><td>millions</td><td>you need K prototypes or a partition of everything</td></tr>
<tr><td class="text-teal-300">Hierarchical</td><td>depends on linkage</td><td>linkage, cut</td><td>no</td><td>~10⁴</td><td>the tree is the answer, or you have a custom distance</td></tr>
<tr><td class="text-amber-300">DBSCAN</td><td>any shape</td><td>ε, minPts</td><td>yes</td><td>millions</td><td>arbitrary shapes, similar density, outliers to flag</td></tr>
<tr><td class="text-violet-300">HDBSCAN</td><td>any shape</td><td>min_cluster_size</td><td>yes</td><td>~10⁶</td><td>shapes <b>and</b> varying density; a good default for exploration</td></tr>
<tr class="opacity-60"><td>GMM (next)</td><td>ellipses</td><td>K, covariance</td><td>soft</td><td>large</td><td>overlapping clusters, probabilities of membership</td></tr>
</tbody>
</table>

<style>
.choose { width: 100%; border-collapse: separate; border-spacing: 0 4px; font-size: 0.85rem; margin-top: 0.5rem; }
.choose th { font-size: 0.72rem; text-transform: uppercase; letter-spacing: 0.05em; opacity: 0.6; text-align: left; padding: 2px 8px; }
.choose td { background: rgba(255, 255, 255, 0.05); padding: 8px; text-align: left; }
.choose td:first-child { font-weight: 700; border-radius: 6px 0 0 6px; }
.choose td:last-child { border-radius: 0 6px 6px 0; }
</style>

<!--
Pulling it together.

k-means: compact, round, similar-size clusters; you choose K; every point is assigned; scales to millions of points. Use it when you want prototypes or a partition of everything, like the depot problem or color quantization.

Hierarchical: the shape depends on the linkage; you choose a linkage and where to cut; no noise label; quadratic memory, so up to roughly ten thousand points. Use it when the tree is what you want to show, or when you have a custom distance between items.

DBSCAN: any shape, flags noise, scales well with a spatial index, but one ε means it assumes all clusters have about the same density. Earthquakes are a good fit.

HDBSCAN: any shape and varying density, with one intuitive parameter. Slower than DBSCAN but fine up to around a million points in low dimensions. For exploring a new dataset it is a very good default.

All of these give hard labels: each point is in one cluster or noise. The last row is next time: Gaussian mixture models, which describe clusters as overlapping ellipses and give each point a probability of belonging to each cluster.

One caveat for all of them: in high dimensions, distances become less informative, the curse of dimensionality from the k-NN lecture, and density estimates suffer most. Reducing dimension first, Decks 4 and 5 of this unit, often helps.
-->

---
glowSeed: 783
clicks: 6
---

# Summary

<div class="grid grid-cols-3 gap-4 mt-6 text-left">
<div class="reveal" :class="{ shown: $clicks >= 1 }" border="2 solid teal-800" bg="teal-800/20" rounded-lg px-4 py-3>
<div class="font-bold text-teal-300">Hierarchical</div>
<div class="text-sm opacity-85 mt-1">Merge the closest clusters until one is left. A dendrogram holds every K; cut at a big gap.</div>
</div>
<div class="reveal" :class="{ shown: $clicks >= 2 }" border="2 solid blue-800" bg="blue-800/20" rounded-lg px-4 py-3>
<div class="font-bold text-blue-300">Linkage</div>
<div class="text-sm opacity-85 mt-1">Single follows chains (and chains through bridges); complete and Ward want compact blobs.</div>
</div>
<div class="reveal" :class="{ shown: $clicks >= 3 }" border="2 solid amber-800" bg="amber-800/20" rounded-lg px-4 py-3>
<div class="font-bold text-amber-300">DBSCAN</div>
<div class="text-sm opacity-85 mt-1">Core, border, noise from ε and minPts. Any shape, flags outliers. Pick ε just past the k-distance bend.</div>
</div>
<div class="reveal" :class="{ shown: $clicks >= 4 }" border="2 solid violet-800" bg="violet-800/20" rounded-lg px-4 py-3>
<div class="font-bold text-violet-300">HDBSCAN</div>
<div class="text-sm opacity-85 mt-1">Every ε at once; keeps the branches that last. Handles varying density with min_cluster_size.</div>
</div>
<div class="reveal" :class="{ shown: $clicks >= 5 }" border="2 solid orange-800" bg="orange-800/20" rounded-lg px-4 py-3>
<div class="font-bold text-orange-300">Distance is still the model</div>
<div class="text-sm opacity-85 mt-1">Scale features; use the metric that fits the data (Manhattan on traits, haversine on the globe).</div>
</div>
<div class="reveal" :class="{ shown: $clicks >= 6 }" border="2 solid red-800" bg="red-800/20" rounded-lg px-4 py-3>
<div class="font-bold text-red-300">Evaluate honestly</div>
<div class="text-sm opacity-85 mt-1">ARI only for benchmarks with known labels. Stability without labels, but stable ≠ right.</div>
</div>
</div>

<!--
Six takeaways.

[click] Hierarchical clustering builds a tree of merges. The dendrogram contains every number of clusters; look for long branches, a big gap in merge heights, to choose where to cut.
[click] The linkage is the shape assumption. Single linkage follows connected shapes but chains through bridges and outliers; complete, average and Ward prefer compact groups.
[click] DBSCAN defines clusters by density: core points have minPts neighbors within ε, clusters grow through core points, the rest is noise. Any shape, outliers flagged, ε from the k-distance knee.
[click] HDBSCAN removes the single ε: it builds the hierarchy over all density levels and keeps the most persistent clusters, so clusters of different densities are found together.
[click] As in the k-means deck, distance is the model: we used Manhattan distance on animal traits and great-circle distance on the globe.
[click] And evaluate honestly: ARI against labels only for benchmarking methods; on your own data, check stability, while remembering that a stable answer can still be wrong.
-->

---
glowSeed: 784
clicks: 1
---

# Next: Gaussian Mixture Models

<div class="grid grid-cols-[1.2fr_1fr] gap-8 items-center mt-2">
<div>
<SoftTeaser :soft="$clicks >= 1" />
</div>
<div class="text-left space-y-4">
<div border="2 solid white/5" bg="white/5" rounded-lg px-4 py-3 class="text-sm">
<b class="text-red-300">So far: hard labels.</b> Every point is in exactly one cluster, or noise, even at a fuzzy boundary.
</div>
<div class="reveal text-sm" :class="{ shown: $clicks >= 1 }" border="2 solid teal-800" bg="teal-800/20" rounded-lg px-4 py-3>
<b class="text-teal-300">Next deck:</b> each cluster is a <b>Gaussian</b>, an ellipse with its own shape and tilt, and each point gets a <b>probability</b> of belonging to each cluster. Overlapping, stretched clusters become workable.
</div>
</div>
</div>

<!--
Everything today produced hard labels: each point gets one cluster id, or −1. Here is the HDBSCAN result on the two-density data with every member drawn at full strength.

[click] Now shade each point by HDBSCAN's probabilities_, its strength of membership: points at the fringe of a cluster fade. That is a hint of a richer kind of answer, but HDBSCAN's score is a heuristic, not a probability model.

Next deck: Gaussian mixture models. Each cluster is a Gaussian, an ellipse with its own center, spread and orientation, and the model gives every point a genuine probability of belonging to each cluster. That handles the stretched, overlapping clusters that tripped up k-means, and it gives a density model of the data that we will use again for anomaly detection at the end of the unit. What it will not do is follow the moons: a Gaussian is still a convex blob, so the methods from today keep their place.
-->
