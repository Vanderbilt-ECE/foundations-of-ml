<script setup lang="ts">
// k-means (best of 10 starts) on four datasets that break its assumptions (data/fails.json).
// Shaded cells are the Voronoi regions of the final centroids: every k-means
// boundary is a straight line, so every cluster is a convex region.
// `show` = number of panels visible; `truth` colors points by their true group instead.
import d from '../data/fails.json'

withDefaults(defineProps<{ show?: number, truth?: boolean }>(), { show: 4, truth: false })
const panels = [
  { key: 'moons', title: 'Curved shapes', why: 'Clusters are not round blobs around a center' },
  { key: 'unequal', title: 'Unequal spread', why: 'Splits the wide cluster, merges the two tight ones' },
  { key: 'aniso', title: 'Stretched', why: 'Distance is not equally meaningful in every direction' },
  { key: 'outliers', title: 'Outliers', why: 'A few far points pull a centroid or take one over' },
] as const
</script>

<template>
  <div class="grid grid-cols-4 gap-4">
    <div v-for="(p, n) in panels" :key="p.key" class="panel" :class="{ off: n >= show }">
      <div class="flex justify-between items-baseline">
        <span class="font-bold">{{ p.title }}</span>
        <span class="text-xs font-mono text-red-300">ARI {{ (d as any)[p.key].ari.toFixed(2) }}</span>
      </div>
      <ClusterPlot
        :pts="(d as any)[p.key].pts"
        :lab="truth ? (d as any)[p.key].truth : (d as any)[p.key].frames[0].lab"
        :centroids="truth ? null : (d as any)[p.key].frames[0].c"
        :w="230" :h="210" :r="2.3" :c-r="6" :cells="!truth" frame
        :label="`k-means on ${p.title.toLowerCase()}`"
      />
      <div class="text-xs opacity-75 mt-1 leading-snug">{{ p.why }}</div>
    </div>
  </div>
</template>

<style scoped>
.panel { transition: opacity 0.5s ease, transform 0.5s ease; }
.off { opacity: 0; transform: translateY(12px); }
</style>
