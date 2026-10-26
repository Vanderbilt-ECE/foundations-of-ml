<script setup lang="ts">
// Decision borders on the running example. Left: k-means' Voronoi cells (straight bisectors).
// Right: where each GMM component has the largest responsibility (converged fit); the borders are conics,
// curving around the small component and bending with the tilted one.
import d from '../data/em.json'

const F = d.frames[d.frames.length - 1]
</script>

<template>
  <div class="grid grid-cols-2 gap-5">
    <div>
      <ClusterPlot :pts="d.pts" :lab="d.km" :centroids="d.kmC" cells frame :w="420" :h="300" :r="2.2" label="k-means regions: straight borders" />
      <div class="text-center text-sm font-mono mt-1">k-means · ARI {{ d.kmAri.toFixed(2) }}</div>
    </div>
    <div>
      <GmmPlot :pts="d.pts" :mix="F" mode="hard" field="argmax" :levels="[1]" frame :w="420" :h="300" :r="2.2" :field-res="84" label="GMM regions: curved borders" />
      <div class="text-center text-sm font-mono mt-1 text-teal-300">GMM · ARI {{ d.gmmAri.toFixed(2) }}</div>
    </div>
  </div>
</template>
